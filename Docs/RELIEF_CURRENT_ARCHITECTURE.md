# ATLAS Relief Engine — Mevcut Mimari Envanteri

## 1. Amaç

Bu belge, ATLAS_ENGINE içindeki mevcut Relief Engine mimarisinin doğrulanmış durumunu kaydeder.

Bu belge bir yeniden tasarım önerisi değildir. Mevcut kodu, test kapsamını, güçlü yönleri ve açık kalan teknik noktaları özetler.

İncelenen dosyalar:

- `CORE/atlas_height_map_engine.py`
- `CORE/atlas_relief_mesh_builder.py`
- `CORE/atlas_relief_quality_report.py`
- `CORE/atlas_relief_pipeline.py`
- `Test/test_height_map_engine.py`
- `Test/test_relief_mesh_builder.py`
- `Test/test_relief_quality_report.py`
- `Test/test_relief_pipeline.py`

---

## 2. Mevcut Uçtan Uca Akış

Mevcut Relief Pipeline şu sırayla çalışır:

```text
iki boyutlu sayısal girdi
→ normalizasyon
→ kontrast yeniden eşleme
→ isteğe bağlı bilinear yeniden örnekleme
→ isteğe bağlı Gaussian yumuşatma
→ kapalı 2.5D relief mesh
→ topoloji ve yüzey kalite raporu
```

Sistem şu anda sayısal dizi benzeri girdileri kabul eder.

Henüz üretim seviyesinde şu katmanlar bulunmaz:

- gerçek görüntü dosyası yükleme,
- görüntü doğrulama,
- maskeleme,
- semantik bölge işleme,
- depth profile politikası,
- baskı optimizasyonu,
- STL dışa aktarma,
- manifest üretimi.

---

## 3. Height Map Engine

Dosya:

- `CORE/atlas_height_map_engine.py`

Sınıf:

- `AtlasHeightMapEngine`

Public metotlar:

- `normalize`
- `remap_contrast`
- `resample_bilinear`
- `smooth_gaussian`

Internal yardımcılar:

- `_validate_target_size`
- `_as_valid_array`
- `_convolve_axis`

### 3.1 Girdi Sözleşmesi

Ortak doğrulama şu koşulları ister:

- iki boyutlu dizi,
- boş olmayan dizi,
- yalnızca sonlu sayısal değerler,
- deterministik `float64` dönüşümü.

### 3.2 Normalizasyon

`normalize`, girdi minimumunu `0.0`, maksimumunu `1.0` değerine eşler.

Sabit girdi tamamen sıfır olan bir height map üretir.

İsteğe bağlı ters çevirme, normalizasyondan sonra uygulanır.

### 3.3 Kontrast Yeniden Eşleme

`remap_contrast`, `0.0..1.0` aralığında normalize edilmiş girdi ister.

İşlem sırası:

1. black point ve white point kırpma,
2. yeniden `0.0..1.0` aralığına eşleme,
3. gamma şekillendirme,
4. son aralık kırpması.

### 3.4 Bilinear Yeniden Örnekleme

`resample_bilinear`, açık Python döngüleriyle deterministik interpolasyon yapar.

Hedef satır ve sütun değerleri:

- tam sayı olmalı,
- en az iki olmalı.

Kaynak ve hedef boyut aynıysa yeni bir kopya döndürülür.

### 3.5 Gaussian Yumuşatma

`smooth_gaussian`, ayrılabilir Gaussian kernel kullanır.

Mevcut özellikler:

- varsayılan radius: `ceil(3 × sigma)`,
- minimum radius: `1`,
- kenarlarda reflected padding,
- X ve Y eksenlerinde ayrı convolution,
- deterministik `float64` çıktı.

### 3.6 Mevcut Height Map Test Kapsamı

Testler şu davranışları kapsar:

- normalizasyon aralığı,
- şekil korunumu,
- ters çevirme,
- sabit girdi,
- geçersiz boyut,
- sonlu olmayan değerler,
- determinizm,
- Gaussian şekil korunumu,
- sabit harita korunumu,
- impulse yumuşatma,
- simetri,
- impulse kütlesi korunumu,
- geçersiz sigma ve radius,
- bilinear köşe korunumu,
- merkez interpolasyonu,
- sabit harita yeniden örnekleme,
- downsampling,
- aynı boyutta kopya,
- geçersiz hedef boyutları,
- kontrast uç noktaları,
- black point ve white point,
- gamma davranışı,
- kontrast determinizmi,
- geçersiz kontrast parametreleri,
- normalize olmayan kontrast girdisinin reddi.

### 3.7 Açık Kalan Height Map Noktaları

Henüz açıkça güvence altına alınmamış alanlar:

- tüm public metotlarda input mutation testleri,
- çok küçük grid ile büyük Gaussian radius,
- `2×N` ve `N×2` reflected-padding sınır durumları,
- çok küçük dinamik aralıkta normalizasyon hassasiyeti,
- smoothing sonrası aralık korunumu,
- resampling sonrası aralık korunumu,
- üretim boyutundaki gridler için performans ölçümü,
- aşırı büyük sigma veya radius politikası.

---

## 4. Relief Mesh Builder

Dosya:

- `CORE/atlas_relief_mesh_builder.py`

Sınıf:

- `AtlasReliefMeshBuilder`

Public metot:

- `build`

Internal yardımcılar:

- `_validate`
- `_add_top_surface`
- `_add_bottom_surface`
- `_add_perimeter_walls`
- `_add_wall_quad`

### 4.1 Geometri Sözleşmesi

Builder şu girdiyi ister:

- normalize edilmiş height map,
- en az iki satır,
- en az iki sütun.

Üretilen geometri:

- örneklenmiş üst yüzey,
- düz alt yüzey,
- segmentli çevre duvarları.

Z hesabı:

```text
bottom_z = origin_z

relief_base_z =
    origin_z + base_thickness_mm

top_z =
    relief_base_z
    + normalized_height × relief_height_mm
```

### 4.2 Mesh Sonucu

Dönen sözlük şunları içerir:

- triangle geometrisi,
- bottom grid,
- top grid,
- kopyalanmış height map,
- satır ve sütun sayısı,
- fiziksel ölçüler,
- taban ve relief yüksekliği,
- origin,
- minimum ve maksimum Z.

### 4.3 Triangle Sayısı

`rows` ve `columns` için:

```text
top =
    2 × (rows - 1) × (columns - 1)

bottom =
    2 × (rows - 1) × (columns - 1)

walls =
    4 × (rows + columns - 2)

total =
    4 × (rows - 1) × (columns - 1)
    + 4 × (rows + columns - 2)
```

### 4.4 Mevcut Mesh Builder Test Kapsamı

Testler şunları kapsar:

- grid boyutları,
- height map değerlerinin Z’ye çevrilmesi,
- kapalı ve manifold mesh,
- triangle sayısı formülü,
- origin offsetleri,
- sıfır relief yüksekliği,
- determinizm,
- geçersiz map şekli,
- geçersiz normalize değerler,
- geçersiz fiziksel ölçüler.

### 4.5 Açık Kalan Mesh Builder Noktaları

Henüz açıkça güvence altına alınmamış alanlar:

- `origin_x`, `origin_y`, `origin_z` için sonlu değer kontrolü,
- input mutation testi,
- dönen height map kopyasının bağımsızlığı,
- sıfır relief yüksekliğinde topoloji doğrulaması,
- triangle winding yönlerinin doğrudan testi,
- büyük grid performans ve bellek davranışı,
- indexed vertex depolama,
- private validator API bağımlılığı.

---

## 5. Relief Quality Report

Dosya:

- `CORE/atlas_relief_quality_report.py`

Sınıf:

- `AtlasReliefQualityReport`

Public metot:

- `build`

Internal yardımcılar:

- `_classify_print_risk`
- `_analyze_top_surface`
- `_add_slope`

### 5.1 Yapısal Analiz

Quality report şu değerleri üretir:

- triangle sayısı,
- vertex referans sayısı,
- koordinat sınırları,
- genişlik,
- derinlik,
- toplam yükseklik,
- açık kenar sayısı,
- non-manifold kenar sayısı,
- closed/manifold bayrakları,
- printable topology bayrağı.

Fiziksel ölçüler metadata’dan değil, triangle koordinatlarından hesaplanır.

### 5.2 Yüzey Analizi

`top_grid` mevcutsa şu metrikler hesaplanır:

- ortalama X örnekleme aralığı,
- ortalama Y örnekleme aralığı,
- incelenen yüzey kenarı sayısı,
- maksimum komşu yükselme,
- maksimum komşu eğim,
- ortalama komşu eğim.

Eğim şu anda yalnız yatay ve düşey komşular arasında ölçülür.

Diyagonal hücre eğimleri analiz edilmez.

### 5.3 Baskı Riski Sınıflandırması

Mevcut durumlar:

- `PASS`
- `WARN`
- `FAIL`

Varsayılan eşikler:

- uyarı eğimi: `55°`
- kritik eğim: `75°`

Kurallar:

- açık mesh → `FAIL`,
- non-manifold mesh → `FAIL`,
- yüzey analizi yok → `WARN`,
- maksimum eğim kritik eşik veya üzerindeyse → `FAIL`,
- maksimum eğim uyarı eşik veya üzerindeyse → `WARN`,
- aksi halde → `PASS`.

### 5.4 Mevcut Quality Report Test Kapsamı

Testler şunları kapsar:

- topoloji çıktısı,
- ölçüler,
- koordinat sınırları,
- triangle sayısı,
- geometry type,
- geçersiz mesh girdisi,
- sonlu olmayan vertex,
- örnekleme aralıkları,
- eğim metrikleri,
- düz relief davranışı,
- `top_grid` yokluğu,
- determinizm,
- düzensiz `top_grid`,
- PASS/WARN/FAIL sınıflandırması,
- geçersiz eşik değerleri.

### 5.5 Açık Kalan Quality Report Noktaları

Henüz açıkça güvence altına alınmamış alanlar:

- her triangle’ın tam üç vertex içerdiğinin doğrulanması,
- malformed triangle girdilerinde tutarlı `ValueError`,
- bozuk `top_grid` noktaları için daha geniş negatif testler,
- diyagonal eğim analizi,
- riskli alan yüzdesi,
- dik eğim dağılımı,
- tekil ve geniş alanlı risk ayrımı,
- doğrudan açık mesh risk testi,
- doğrudan non-manifold risk testi,
- private `_topology_report` bağımlılığı.

---

## 6. Relief Pipeline

Dosya:

- `CORE/atlas_relief_pipeline.py`

Sınıf:

- `AtlasReliefPipeline`

Public metot:

- `build`

### 6.1 İşlem Sırası

Mevcut sıra:

1. normalize,
2. contrast remap,
3. isteğe bağlı resample,
4. isteğe bağlı smooth,
5. mesh üretimi,
6. quality report üretimi.

### 6.2 Parametre Bağımlılıkları

Mevcut kurallar:

- `target_rows` ve `target_columns` birlikte verilmelidir,
- `smoothing_radius`, `smoothing_sigma` olmadan kullanılamaz.

### 6.3 Pipeline Sonucu

Sonuç şu verileri korur:

- normalized height map,
- contrast height map,
- resampled height map,
- processed height map,
- relief mesh,
- quality report,
- işlem ve fiziksel ayarlar.

Kaydedilen target satır ve sütun değerleri, sonuçta oluşan processed array boyutudur.

### 6.4 Mevcut Pipeline Test Kapsamı

Testler şunları kapsar:

- tam sonuç yapısı,
- normalizasyon,
- resampling,
- smoothing,
- inversion,
- fiziksel ölçüler,
- processed map determinizmi,
- triangle determinizmi,
- quality report determinizmi,
- target size birlikteliği,
- smoothing radius bağımlılığı,
- contrast remap,
- gamma etkisi,
- contrast ayarlarının kaydı,
- geçersiz contrast ayarları.

### 6.5 Açık Kalan Pipeline Noktaları

Henüz açıkça güvence altına alınmamış alanlar:

- input mutation testi,
- ara dizilerin birbirinden bağımsızlığı,
- origin değerlerinin sonluluğu,
- quality-report eşiklerinin pipeline üzerinden ayarlanması,
- pipeline seviyesinde doğrudan print-risk testleri,
- istenen ve oluşan boyutların ayrı kaydı,
- gerçek görüntü yükleme,
- maskeleme,
- depth profile politikası,
- baskı optimizasyonu,
- STL export,
- manifest üretimi,
- üretim fixture sistemi.

---

## 7. Mevcut Güçlü Yönler

Mevcut temel şu yetenekleri zaten sağlar:

- deterministik sayısal işleme,
- merkezi height map doğrulaması,
- normalize ve fiziksel ölçekli relief geometrisi,
- kapalı ve manifold mesh üretimi,
- ara pipeline çıktılarının açık biçimde korunması,
- topoloji raporu,
- yüzey eğim metrikleri,
- deterministik baskı riski sınıflandırması,
- mevcut alt sistemler için odaklı unit testler.

---

## 8. Yakın Dönem Teknik Öncelikler

Yeni üretim yeteneklerinden önce şu sıra izlenmelidir:

1. deterministik fixture ve regression altyapısı,
2. input immutability ve output isolation testleri,
3. origin sonluluk doğrulaması,
4. malformed triangle ve top-grid doğrulamasının güçlendirilmesi,
5. üretim boyutu performans baseline’ı,
6. pipeline üzerinden ayarlanabilir kalite eşikleri,
7. ardından image input ve preprocessing katmanları.

---

## 9. Phase 0 Sonucu

Mevcut Relief Engine, çalışan ve deterministik bir numeric-to-mesh prototipidir.

Henüz üretim seviyesinde image-to-print motoru değildir.

Sonraki aşama; mevcut normalizasyon, determinizm, topoloji ve regression güvencelerini bozmadan bu temeli genişletmelidir.