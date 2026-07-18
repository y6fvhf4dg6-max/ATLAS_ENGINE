# ATLAS_ENGINE — 2.5D RÖLYEF MOTORU ANA GELİŞTİRME PLANI

## Belge statüsü

- **Durum:** KİLİTLİ ANA PLAN
- **Başlangıç commit’i:** `19d97a3`
- **Başlangıç regresyonu:** `423 passed`
- **Başlangıç çalışma ağacı:** temiz
- **Tatil paketleri:** yalnız arşiv ve referans; doğrudan uygulanmayacak
- **Değişiklik politikası:** Plan yalnız zorunlu teknik gerekçeyle değiştirilir. Her değişiklik gerekçesi, etkisi, riski ve geri dönüş yöntemiyle belgelenir; plan değişikliği ayrı commit olur.

## 1. Ana hedef

```text
Müşteri görüntüsü
→ görüntü uygunluk analizi
→ kontrollü ön işleme
→ normalize height-map
→ isteğe bağlı maskeleme
→ bölgesel derinlik profili
→ baskı optimizasyonu
→ kapalı ve manifold 2.5D mesh
→ kalite ve risk raporu
→ fiziksel ürün ölçülendirmesi
→ STL
→ üretim manifestosu
```

İlk teknik hedef:

> Tek bir görüntüyü, aynı parametrelerle her çalıştırmada aynı sonucu veren, ölçülendirilmiş, manifold ve fiziksel olarak basılabilir bir 2.5D rölyefe dönüştüren genel çekirdek motor.

## 2. İlk çekirdek kapsamı

- Standart görüntü girdisi ve doğrulama
- Normalize height-map üretimi
- Kontrast, gamma, invert, yeniden örnekleme ve kontrollü smoothing
- Fiziksel boyut çözümleme
- Taban kalınlığı ile rölyef yüksekliğinin ayrılması
- Kapalı manifold mesh
- Topoloji, ölçüm ve baskı riski raporu
- Deterministik fixture ve regresyon altyapısı
- STL üretimine uygun veri sözleşmesi

### İlk aşamada kapsam dışı

- Çerçeve mesh sistemi
- Press-fit entegrasyonu
- Otomatik yüz tanıma veya AI segmentasyonu
- Yapay derinlik tahmini
- Web, sipariş ve ödeme sistemleri
- Otomatik fiyatlandırma
- Ambalaj otomasyonu
- Metal plaka ve 3D sertifika
- Paint-by-number
- Hazır ticari preset ve Heritage kataloğu

Bunlar iptal edilmemiştir; çekirdek doğrulanana kadar ertelenmiştir.

## 3. Tatil paketlerinin statüsü

15 paketlik rölyef ve 18 paketlik çerçeve paketleri:

```text
ARŞİV
REFERANS
FİKİR KATALOĞU
TEST SENARYOSU KAYNAĞI
SINIF / VERİ MODELİ ÖNERİSİ
```

Kurallar:

1. Hiçbir paket dosyası mevcut proje dosyasının üzerine körlemesine kopyalanmaz.
2. Paket kodu proje gerçeği kabul edilmez.
3. Her fikir mevcut ATLAS API’leriyle yeniden değerlendirilir.
4. Gerekli özellik mevcut mimariye göre yeniden yazılır.
5. Test edilmeden commit edilmez.

## 4. Değişmez mühendislik kuralları

1. Deneysel geliştirme doğrulanmış ana durum üzerinde toplu yapılmaz.
2. Her özellik küçük ve geri alınabilir commit ile eklenir.
3. Bir commit yalnız tek mantıksal değişiklik taşır.
4. Çalışan davranış sessizce değiştirilmez.
5. Yeni parametreler mümkün olduğunca geriye uyumludur.
6. Public API değişikliği belgelenir.
7. Görüntü işleme, height-map, geometri, kalite politikası ve ürün katmanı ayrıdır.
8. Ticari kurallar matematik çekirdeğine hard-code edilmez.
9. Fiziksel baskıyla doğrulanmamış sınırlar kesin değer sayılmaz.
10. Aynı girdi + aynı parametre = aynı çıktı.
11. Girdi dizileri yerinde değiştirilmez.
12. Birimler alan adlarında açıkça yazılır.
13. Her yeni CORE yeteneğinin hedefli testi olur.
14. Tam regresyon geçmeden sonraki aşamaya geçilmez.
15. Tek görüntüye veya tek ürün ölçüsüne özel hard-code yapılmaz.

### Yasak işlemler

```text
Paketleri topluca proje içine açmak
CORE dosyalarını körlemesine tamamen değiştirmek
Birden fazla mimari değişikliği tek commit’e koymak
Testsiz CORE sınıfı eklemek
Gerçek baskı olmadan “print-safe” ilan etmek
Tek portreye özel algoritma yazmak
Çerçeve ile rölyef çekirdeğini erken birleştirmek
Ölçüm ile risk politikasını karıştırmak
Belirsiz birim adları kullanmak
Başarısız regresyonu görmezden gelmek
```

## 5. Mimari katmanlar

### Katman A — Girdi ve görüntü doğrulama

Görevler:

- Dosyayı okumak ve formatı doğrulamak
- Boyut ve kanal sayısını belirlemek
- Bozuk/boş dosyayı reddetmek
- EXIF yönünü uygulamak
- Alfa kanalını yönetmek
- Kaynak hash ve metadata üretmek

Önerilen sözleşme:

```text
AtlasReliefImage
- pixels
- width_px
- height_px
- channel_count
- has_alpha
- orientation_applied
- source_hash
- metadata
```

Bu katman mesh üretmez.

### Katman B — Görüntü ön işleme

- Gri ton dönüşümü
- Kontrast remap
- Gamma
- Invert
- Gölge/parlaklık sıkıştırması
- Gürültü azaltma
- Kontrollü smoothing
- Yeniden örnekleme

Bu katman milimetre bilmez.

Invariants:

- Sonlu değerler
- NaN/Infinity yok
- Girdi değişmez
- Deterministik çıktı
- Açık tanımlı değer aralığı

### Katman C — Maske ve bölgeler

- Global, subject, background ve named mask
- Feathering
- Çakışma analizi
- Ada/boşluk analizi
- Deterministik öncelik

Maske kuralları:

```text
değer aralığı: [0,1]
boyut: görüntüyle aynı
NaN/Infinity: yasak
çakışma politikası: açık
öncelik: deterministik
```

### Katman D — Height-map çekirdeği

- Normalize `[0,1]`
- Gamma ve kontrast eğrileri
- Bölgesel ağırlık
- Clamp
- Transform geçmişi

Önerilen sözleşme:

```text
AtlasHeightMap
- values
- rows
- columns
- min_value
- max_value
- source_metadata
- transform_history
```

Invariants:

```text
Tüm değerler sonlu
Normalize değerler [0,1]
rows > 0
columns > 0
Girdi değişmez
Deterministik çıktı
```

### Katman E — Baskı optimizasyonu

- Yerel gradyan sınırlandırma
- Spike suppression
- Küçük çukur/gürültü kontrolü
- Clamp
- Kontrollü smoothing
- Detay kaybı ölçümü

Orijinal height-map yerinde değişmez.

Rapor:

```text
changed_sample_count
changed_sample_ratio
maximum_absolute_change
mean_absolute_change
maximum_slope_before
maximum_slope_after
p95_slope_before
p95_slope_after
detail_loss_estimate
iterations
converged
```

### Katman F — Mesh üretimi

- Üst grid triangulation
- Taban
- Dört yan duvar
- Doğru winding ve normal
- Deterministik vertex/triangle sırası
- Kapalı manifold geometri

Mesh builder ürün, fiyat, çerçeve veya ticari kalite kararı bilmez.

### Katman G — Kalite ve risk

#### Geometrik ölçüm

- Vertex/triangle sayısı
- Open ve non-manifold edge
- Degenerate ve duplicate triangle
- Ters normal
- Bounds
- Fiziksel genişlik/yükseklik
- Taban, rölyef ve toplam kalınlık
- Sample spacing
- Eğim ölçümleri ve yüzdelikler
- Sınır sürekliliği

#### Risk politikası

- Warning/critical slope
- Minimum base thickness
- Minimum feature width
- Maximum relief ratio
- Sample spacing sınırı
- Yazıcı/nozzle/filament profili

Risk seviyeleri:

```text
PASS
WARN
FAIL
```

Ölçüm profile bağlı değildir; risk değerlendirmesi profile bağlıdır.

### Katman H — Ürün orkestrasyonu

- S/M/L presetleri
- Çerçeveli/çerçevesiz seçenek
- Kalite profili
- STL çıktısı
- Üretim manifestosu
- Daha sonra çerçeve adaptörü

Bu katman en son eklenir.

## 6. Fiziksel ölçülendirme modeli

```text
product_width_mm
product_height_mm
base_thickness_mm
relief_height_mm
total_height_mm
sample_spacing_x_mm
sample_spacing_y_mm
```

Kurallar:

1. En-boy oranı varsayılan korunur.
2. Açık crop isteği yoksa görüntü gerilmez.
3. Yalnız genişlik veya yalnız yükseklikten diğer boyut hesaplanır.
4. İki boyut birlikte verilirse fit/crop/stretch açıkça seçilir.
5. Stretch varsayılan değildir.
6. Taban kalınlığı ve rölyef yüksekliği ayrıdır.
7. Toplam kalınlık açık hesaplanır.
8. Düşük örnekleme çözünürlüğü uyarı üretir.

## 7. Geliştirme aşamaları

### Aşama 0 — Mevcut sistem envanteri

İncelenecek CORE dosyaları:

```text
CORE/atlas_height_map_engine.py
CORE/atlas_relief_mesh_builder.py
CORE/atlas_relief_quality_report.py
CORE/atlas_relief_pipeline.py
```

İlgili tüm testler bulunur.

Çıkarılacak bilgiler:

- Public API
- Parametreler ve varsayılanlar
- Veri tipleri
- Hata davranışları
- Bağımlılıklar
- Mesh ve kalite sözleşmesi
- Tüketici noktaları
- Geriye uyumluluk riskleri
- Performans özellikleri

Çıkış:

```text
Docs/RELIEF_CURRENT_ARCHITECTURE.md
```

Geçiş şartı:

- Kod değişikliği yok
- Tam regresyon geçer
- Mimari belge tamam
- Riskler sınıflandırılmış

### Aşama 1 — Deterministik fixture sistemi

Fixture ailesi:

1. Düz sabit yüzey
2. Yatay gradyan
3. Dikey gradyan
4. Keskin basamak
5. Merkezi tepe
6. Merkezi çukur
7. Gürültülü yüzey
8. Çok küçük grid
9. Dikdörtgen grid
10. Alfa kanallı sentetik görüntü
11. Tam siyah
12. Tam beyaz
13. NaN
14. Infinity
15. Portre benzeri sentetik yüzey
16. Maskelenmiş konu
17. Düşük kontrast
18. Aşırı kontrast
19. Tek satır/tek sütun geçersiz örnek
20. Sabit seed rastgele yüzey

Kurallar:

- Harici internet/dosya bağımlılığı yok
- NumPy ile üretim
- Seed açık
- Deterministik
- Girdi değişmez

### Aşama 2 — Veri sözleşmeleri

Aday sınıflar:

```text
AtlasHeightMap
AtlasReliefMeshResult
AtlasReliefMeasurements
AtlasReliefRiskAssessment
AtlasReliefPipelineResult
```

Kurallar:

- Birimler isimlerde açık
- Merkezi validation
- Mümkün olduğunca immutable
- `to_dict()` yalnız raporlama için
- Eski API adaptörle korunur

### Aşama 3 — Height-map matematik doğrulaması

- Normalize
- Sabit görüntü
- Gamma
- Contrast remap
- Invert
- Clamp
- Resample
- Smoothing
- Sınır davranışı
- Float hassasiyeti
- NaN/Infinity
- Girdi değişmezliği

Her dönüşümün hedefli testi ve tam regresyonu olur.

### Aşama 4 — Fiziksel boyut çözümleyici

Testler:

- Kare/yatay/dikey görüntü
- Yalnız genişlik
- Yalnız yükseklik
- İki boyut
- Fit/crop/stretch
- Negatif/sıfır ölçü
- S/M/L ölçüleri

### Aşama 5 — Mesh topolojisi

Kontroller:

- Grid triangulation
- Diagonal seçimi
- Üst/taban/yan winding
- Köşe birleşimleri
- Manifold kapanış
- Degenerate/duplicate triangle
- Vertex tekrarları
- Deterministik indeks
- Origin offset

Zorunlu testler:

```text
2×2
3×3
düz
eğimli
tek tepe
tek çukur
dikdörtgen
çok düşük rölyef
yüksek rölyef
pozitif/negatif origin
ince taban
geçersiz sıfır taban
```

Hedef:

```text
open_edges = 0
non_manifold_edges = 0
degenerate_triangles = 0
duplicate_triangles = 0
```

### Aşama 6 — Ölçüm ile risk politikasını ayırma

```text
Mesh
→ AtlasReliefMeasurements
→ AtlasReliefRiskPolicy
→ AtlasReliefRiskAssessment
```

Aynı mesh farklı profil altında farklı risk alabilir; ham ölçümler değişmez.

### Aşama 7 — Baskı optimizasyonu

İlk sürüm:

- Gradyan sınırı
- Spike suppression
- Clamp
- Controlled smoothing
- Convergence

Yüz/göz/saç semantiği yoktur.

Geçiş şartı:

- Risk azalır
- Düz alanlar gereksiz değişmez
- Topoloji bozulmaz
- Detay kaybı ölçülür
- Deterministik
- Tam regresyon geçer

### Aşama 8 — Gerçek görüntü sağlayıcısı

İlk destek:

- JPEG
- PNG
- Grayscale
- RGB
- RGBA

Kontroller:

- Dosya yok
- Bozuk format
- Aşırı büyük görüntü
- EXIF orientation
- Alfa
- Kanal sayısı
- Kaynak hash

Çekirdek doğrudan Pillow nesnesine bağlanmaz; sağlayıcı standart ATLAS sözleşmesine dönüştürür.

### Aşama 9 — Maske sistemi

```text
global
subject
background
custom named masks
```

İşlemler:

- Normalize
- Invert
- Feather
- Priority
- Union/intersection/subtract
- Validity report

### Aşama 10 — Bölgesel derinlik profili

```text
region_name
height_scale
height_offset
contrast
gamma
feather_radius
priority
blend_mode
```

Amaç:

- Ana konuyu öne çıkarmak
- Arka planı bastırmak
- Bölge sınırlarında duvar oluşmasını engellemek
- Deterministik blending

### Aşama 11 — İlk fiziksel prototipler

Testler:

1. Gradyan plaka
2. Sentetik yüzey
3. Sentetik portre
4. Gerçek portre
5. Arka planlı portre
6. Yüksek kontrastlı çizim

Ölçümler:

- Baskı süresi
- Filament
- Yüzey okunabilirliği
- Gölge davranışı
- Katman izi
- Minimum detay
- Güvenli eğim
- Taban eğilmesi
- Destek ihtiyacı
- Nozzle/layer etkisi
- Slicer uyarıları

Fiziksel test olmadan nihai üretim eşiği kesinleştirilmez.

### Aşama 12 — Ürün presetleri

```text
S: 150 × 150 mm
M: 200 × 200 mm
L: 250 × 250 mm
```

Her preset veri taşır:

- Boyut
- Taban kalınlığı
- Rölyef yüksekliği
- Grid çözünürlüğü
- Sample spacing
- Kalite/yazıcı profili

Preset algoritmaya hard-code edilmez.

### Aşama 13 — Çerçeve entegrasyonu

Rölyef motoru çerçeveyi bilmez.

Standart insert sözleşmesi:

```text
insert_width_mm
insert_height_mm
insert_thickness_mm
retention_profile
clearance_mm
corner_radius_mm
```

İlk fiziksel işlem tam çerçeve değil tolerans kuponudur:

```text
0.15 mm
0.20 mm
0.25 mm
0.30 mm
0.35 mm
```

## 8. Test stratejisi

- Birim testleri
- Veri sözleşmesi testleri
- Geometri/topoloji testleri
- Regresyon testleri
- Altın fixture testleri
- Özellik tabanlı testler
- Performans ve bellek testleri
- Slicer ve fiziksel baskı doğrulaması

Altın fixture’larda tam vertex listesi yerine kararlı özetler tercih edilir:

- Shape
- Min/max
- Bounds
- Triangle count
- Topology counts
- Quantile/histogram
- Deterministik checksum

## 9. Her commit için zorunlu sıra

```text
1. py_compile
2. hedefli testler
3. ilgili alt sistem testleri
4. tam pytest
5. git diff --check
6. git status --short
7. diff incelemesi
8. commit
```

## 10. Commit politikası

Örnek sıra:

```text
Document current relief architecture
Add deterministic relief fixture factory
Define relief height-map data contract
Harden height-map normalization edge cases
Add physical relief dimension resolver
Harden relief mesh topology
Separate relief measurements from risk policy
Add controlled relief slope optimizer
Add image height-map provider
Add regional relief mask model
Add regional relief depth profiles
Add relief product size presets
Add relief insert interface
```

Refactor, yeni özellik, dosya yeniden adlandırma ve public API kırılması aynı committe birleştirilmez.

## 11. Geri dönüş mekanizması

```text
Doğrulanmış başlangıç commit’i
Temiz çalışma ağacı
Küçük commitler
Deterministik fixture’lar
Tam regresyon
Eski API adaptörleri
Arşiv ZIP’leri
Belgelenmiş kararlar
```

Sorunda yalnız ilgili commit geri alınır; tüm proje yeniden yazılmaz.

## 12. Dosya silme ve API kaldırma

1. Yeni yapı eklenir.
2. Adaptör yazılır.
3. Eski ve yeni sonuç karşılaştırılır.
4. Tüketiciler taşınır.
5. Deprecation belgelenir.
6. Tam regresyon geçer.
7. Eski kod ayrı committe kaldırılır.

## 13. Stop kriterleri

Şunlardan biri oluşursa geliştirme durur:

- Tam regresyon başarısız
- Open/non-manifold mesh
- Degenerate triangle
- Determinizm kaybı
- Birim belirsizliği
- Sessiz public API kırılması
- Tek görüntüye özel çözüm
- Kontrolsüz detay kaybı
- Kontrolsüz performans/bellek kötüleşmesi
- Fiziksel baskı ile yazılım raporu uyuşmazlığı
- Yeni özellik eski doğrulanmış davranışı bozuyor

## 14. Plan değişiklik politikası

Bu belge yaşayan fakat kilitli bir plandır.

Yalnız şu durumlarda değişir:

1. Mevcut ATLAS API’si planı teknik olarak imkânsız kılıyorsa
2. Test temel varsayımı çürütüyorsa
3. Fiziksel baskı varsayımı geçersiz kılıyorsa
4. Ciddi performans/bellek sorunu varsa
5. Veri bütünlüğü riski varsa
6. Daha basit ve açıkça daha güvenli mimari kanıtlanmışsa

Her değişiklik kaydı:

```text
Değişiklik tarihi
İlgili aşama
Eski karar
Yeni karar
Teknik gerekçe
Etkilenen modüller
Etkilenen testler
Geriye uyumluluk etkisi
Risk
Geri dönüş yöntemi
Onay durumu
İlgili commit
```

Plan değişikliği ile uygulama kodu mümkün olduğunca ayrı commitlerde tutulur.

## 15. İlk çalışma sırası

```text
1. Dört mevcut CORE dosyasını incele
2. İlgili tüm testleri listele
3. Public API haritasını çıkar
4. Veri akışını çıkar
5. Bağımlılık haritasını çıkar
6. Mevcut invariants ve varsayımları belirle
7. Riskli noktaları sınıflandır
8. Docs/RELIEF_CURRENT_ARCHITECTURE.md oluştur
9. Tam regresyonu doğrula
10. İlk kod değişikliğini bundan sonra seç
```

Beklenen ilk kod geliştirmesi:

> Deterministik fixture ve regresyon altyapısı.

## 16. Ana geliştirme ilkesi

```text
Önce ölç
→ mevcut sözleşmeyi belgeleyerek sabitle
→ fixture oluştur
→ matematiği doğrula
→ fiziksel ölçüleri kesinleştir
→ geometriyi doğrula
→ kaliteyi ölç
→ optimize et
→ gerçek görüntüyü bağla
→ maske ve bölgesel derinlik ekle
→ fiziksel baskıyla doğrula
→ en son ticari ürüne dönüştür
```

## 17. Kilit kararı

Aşağıdaki kararlar kilitlenmiştir:

- Tatil paketleri doğrudan uygulanmayacak.
- Mevcut doğrulanmış çekirdek korunacak.
- Önce mimari envanter çıkarılacak.
- Sonra deterministik fixture sistemi kurulacak.
- Her özellik genel CORE yeteneği olacak.
- Her özellik hedefli test ve tam regresyonla doğrulanacak.
- Fiziksel baskı yapılmadan nihai üretim eşikleri kesinleştirilmeyecek.
- Çerçeve sistemi rölyef çekirdeğinden ayrılacak.
- Plan yalnız ciddi teknik gerekçeyle ve belgelenerek değiştirilecek.
- Geri dönüşsüz, toplu veya körlemesine dosya değişiklikleri yapılmayacak.
