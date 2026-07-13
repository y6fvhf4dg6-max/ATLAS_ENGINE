# ATLAS_ENGINE DURUM RAPORU

**Tarih:** 13 Temmuz 2026  
**Proje:** ATLAS_ENGINE  
**Durum:** Kale motorunun veri kalite ve regresyon altyapısı güçlendirildi. Görsel model geliştirme aşamasına dönülüyor.

---

## 1. Projenin Ana Hedefi

ATLAS_ENGINE; gerçek coğrafi, arazi ve mimari verileri kullanarak fiziksel olarak basılabilir 3D şehir, anıt, kale, arazi ve kişisel hatıra modelleri üretmek için geliştirilen genel amaçlı bir modelleme motorudur.

Temel ürün ilkesi:

> Every important memory has a location.  
> Her önemli hatıranın bir konumu vardır.

Planlanan ürün aileleri:

- My Life Map
- Our Love Map
- Family Heritage
- Şehir ve mahalle modelleri
- Tarihi yapı ve kale modelleri
- Anıt ve simge yapı modelleri
- Kişiselleştirilmiş 2.5D fotoğraf kabartma ürünleri

ATLAS’ın amacı yalnızca ekranda görünen modeller üretmek değildir. Hedef; temiz, manifold, fiziksel baskıya uygun ve ticari ürüne dönüştürülebilir STL dosyaları oluşturmaktır.

---

## 2. Bugün Tamamlanan Çalışmalar

### 2.1 Semantik Sorun Kayıtları

Aşağıdaki üç gerçek kale önizleme dosyasına ayrıntılı semantik sorun kayıtları eklendi:

- `Test/test_rumeli_full_scene_preview.py`
- `Test/test_burghausen_castle_preview.py`
- `Test/test_hohenzollern_castle_preview.py`

Raporlar artık yalnızca sorun sayılarını değil, sorunlu kaydın ayrıntılarını da gösteriyor:

- sorun adı
- kayıt tipi
- OSM kimliği
- ilgili alan
- mevcut değer

Örnek çıktı:

    complex_roof_shape (5)
      type=building id=122098764 field=roof:shape value=many

Burghausen verisinde `roof:shape=many` taşıyan beş bina tespit edildi:

- 122098764
- 122098773
- 122155613
- 122507266
- 123098479

Bu kayıtlar üretimi engelleyen veri hataları değildir. Karmaşık çatı biçimlerini ifade eden bilgilendirici kayıtlardır.

---

### 2.2 INFO / WARN / FAIL Sınıflandırması

`CORE/atlas_input_quality_report.py` dosyasına semantik önem seviyesi sistemi eklendi.

#### INFO

Üretimi engellemeyen, yalnızca bilgi veren durumlar:

- `complex_roof_shape`

#### WARN

Veri kalitesini düşüren fakat kontrollü üretime izin veren durumlar:

- `invalid_height`
- `non_positive_height`
- `invalid_levels`
- `non_positive_levels`
- `unknown_roof_shape`
- `conflicting_height_values`
- `conflicting_roof_shapes`
- `missing_castle_tag`

#### FAIL

Kale geometrisinin güvenilir şekilde üretilemeyeceğini gösteren yapısal sorunlar:

- `relation_missing_outer_geometry`
- `way_has_inner_geometry`
- `unsupported_castle_geometry_type`

Rapor yapısına şu alanlar eklendi:

    severity_counts
    severity_issues

Gerçek saha sonuçları:

#### Burghausen

    INFO : 5
    WARN : 0
    FAIL : 0

#### Hohenzollern

    INFO : 0
    WARN : 0
    FAIL : 0

#### Rumeli Hisarı

    INFO : 0
    WARN : 0
    FAIL : 0

Hohenzollern ve Rumeli Hisarı’nın genel kalite sonucu `MEDIUM / WARN` olsa da bunun nedeni semantik kusur değildir. OSM yükseklik ve çatı verisi kapsamının düşük olmasıdır.

---

### 2.3 Input Quality Regresyon Testi

`Test/test_input_quality_report.py` dosyasına yeni bir regresyon testi eklendi.

Test şu davranışı sabitledi:

- `roof:shape=many` → INFO
- geçersiz yükseklik → WARN
- outer geometrisi olmayan kale relation kaydı → FAIL

İlgili test sonucu:

    23 passed

Genel aktif test paketi sonucu:

    67 passed in 0.29s

---

### 2.4 Kale Regresyon Çalıştırıcısının İncelenmesi

Projede bulunan ortak regresyon çalıştırıcısı incelendi:

`Test/run_regression_suite.py`

Bu dosya testleri kategori bazında otomatik keşfediyor.

Mevcut gruplar:

- castles
- diagnostics
- bridges
- dams
- districts
- water
- terrain
- buildings
- roads
- nature

`castles` grubu toplam 16 dosya buldu.

Bunların arasında:

- Rumeli Hisarı testleri
- Burghausen önizlemesi
- Hohenzollern önizlemesi
- Hohenneuffen önizlemesi
- kale geometrisi sınıflandırma testleri
- çatı regresyonları
- crenellation testleri
- gerçek kale veri kalite regresyonları

bulunmaktadır.

---

### 2.5 Kritik Regresyon Sorununun Bulunması

Eski çalıştırıcı bütün dosyaları doğrudan şu yöntemle çalıştırıyordu:

    python Test/test_xxx.py

Bu yöntem, yalnızca `def test_...` fonksiyonlarından oluşan pytest dosyalarında testleri gerçekten yürütmeyebiliyordu.

Dosya Python tarafından açılıyor, fakat pytest fonksiyonları çağrılmadan program başarılı çıkış koduyla kapanabiliyordu.

Böylece bazı dosyalar geçti olarak raporlanırken test fonksiyonları gerçekte çalışmamış olabilirdi.

Bu sessiz güvenilirlik açığı bugün tespit edildi.

---

### 2.6 Regresyon Çalıştırıcısının Düzeltilmesi

`Test/run_regression_suite.py` güncellendi.

Yeni davranış:

#### Pytest dosyaları

Dosya içerisinde `def test_` bulunuyorsa:

    python -m pytest -q Test/test_xxx.py

komutuyla çalıştırılıyor.

#### Önizleme ve çalıştırılabilir betikler

Pytest fonksiyonu içermeyen dosyalar:

    python Test/test_xxx.py

komutuyla çalıştırılıyor.

Raporlara kullanılan çalıştırıcı da eklendi:

    RUNNER : pytest

veya:

    RUNNER : python

Böylece her dosyanın gerçekten hangi yöntemle çalıştırıldığı açıkça görülebiliyor.

---

### 2.7 Kale Regresyon Paketinin Doğrulanması

Güncellenen çalıştırıcı şu komutla çalıştırıldı:

    PYTHONPATH=. python Test/run_regression_suite.py castles

Sonuç:

    ATLAS REGRESSION SUITE PASSED
    Passed test files : 16
    Total runtime     : 3.65 seconds

Bu sonuçla:

- pytest dosyaları gerçekten çalıştırıldı
- önizleme betikleri gerçek üretim akışını çalıştırdı
- Rumeli Hisarı geçti
- Burghausen geçti
- Hohenzollern geçti
- Hohenneuffen geçti
- kale çatı regresyonları geçti
- kale geometrisi sınıflandırma testleri geçti
- crenellation testleri geçti
- gerçek saha veri kalite testleri geçti

---

## 3. Bugünkü Commitler

### Semantik sorun kayıtları

    Show semantic issue records in castle reports

Üç gerçek kale önizlemesine ayrıntılı sorun kayıtları eklendi.

### Semantik önem seviyeleri

    Classify semantic input issues by severity

INFO, WARN ve FAIL sınıflandırması eklendi.

### Regresyon çalıştırıcısı

    bb3ae0c Run pytest tests correctly in regression suite

Değişiklik özeti:

    1 file changed
    24 insertions
    4 deletions

Commit sonrasında çalışma alanı temizdi.

---

## 4. Gün Sonu Teknik Durum

    Input Quality tests : 23 passed
    Genel pytest paketi : 67 passed
    Castle suite        : 16 test files passed
    Warnings            : 0
    Working tree        : clean

---

## 5. Gerçek Kale Durumları

### Rumeli Hisarı

- Relation outer ve inner geometrileri düzeltilmiş durumda.
- Delikli kale kabuğu manifold üretiliyor.
- Üç ana kule otomatik tespit ediliyor.
- Kule kapakları local-Z sistemiyle çalışıyor.
- Castle shell ve kule yükseklikleri uyumlu.
- Crenellation sistemi mevcut.
- Arazi ve su katmanı mevcut.
- Yol topolojisi temiz.
- Açık kenar yok.
- Non-manifold kenar yok.
- Yapısal semantik sorun yok.

### Burghausen

- Castle-focus sahnesi çalışıyor.
- Defensive tower çatı problemi düzeltildi.
- Büchsenmacherturm kapalı manifold üretiliyor.
- Beş karmaşık çatı kaydı INFO olarak raporlanıyor.
- Üretimi durduracak veri sorunu yok.
- Gerçek fixture regresyon testiyle korunuyor.

### Hohenzollern

- Kale doğru tepe üzerinde konumlanıyor.
- SRTM arazi verisi kullanılıyor.
- Kule profilleri çalışıyor.
- Pyramidal ve hipped kule çatıları mevcut.
- Yapısal semantik sorun yok.
- OSM yükseklik ve çatı kapsamı düşük.
- Bir sonraki görsel geliştirme şapel ve uzun kanat çatılarında yapılacak.

---

## 6. Terminal Üzerinden Güvenli Çalışma Yöntemi

Bugünkü çalışmalarda terminal tabanlı kontrollü düzenleme yöntemi kullanıldı.

Standart süreç:

1. Hedef dosya ve ilgili kod bölümü incelenir.
2. Değiştirilecek nokta kesin olarak belirlenir.
3. Kontrollü hedefli değişiklik uygulanır.
4. `py_compile` ile sözdizimi kontrol edilir.
5. İlgili regresyon testleri çalıştırılır.
6. Genel test paketi çalıştırılır.
7. `git diff --check` uygulanır.
8. `git diff` incelenir.
9. Yalnızca ilgili dosyalar stage edilir.
10. Commit yapılır.
11. `git status --short` ile çalışma alanı doğrulanır.

Terminal üzerinden güvenli biçimde yapılabilen işlemler:

- yeni dosya oluşturma
- dosya silme
- dosya taşıma
- kod bloğu ekleme
- kod bloğu kaldırma
- hedefli kod değiştirme
- dosyanın tamamını kontrollü yeniden yazma
- sözdizimi kontrolü
- test çalıştırma
- Git fark kontrolü
- commit oluşturma

Bu yöntem elle yapılan uzun kopyalama işlemlerini azaltmış, zaman kazandırmış ve hata riskini düşürmüştür.

ATLAS_ENGINE’de küçük ve orta ölçekli değişiklikler için varsayılan yöntem olacaktır.

---

## 7. Sıradaki Ana Hedef

Kalite güvence altyapısı tamamlandı. Şimdi yeniden görsel model geliştirme aşamasına geçiliyor.

İlk hedef:

> Hohenzollern Kalesi’nde şapel ve uzun kanat binalarına gerçekçi eğimli ve gable çatılar eklemek.

İncelenecek dosyalar:

- `Test/test_hohenzollern_castle_preview.py`
- `CORE/atlas_castle_roof_builder.py`
- `CORE/atlas_castle_gable_roof_builder.py`

Henüz bu görsel geliştirme için dosya değişikliği yapılmadı.

---

## 8. Hohenzollern Çatı Geliştirme Planı

### Aşama 1 — Mevcut Karar Akışını İnceleme

İncelenecek konular:

- roof dispatch
- `roof_type` seçimi
- bina profile sınıflandırması
- defensive tower
- gate tower
- chapel
- castle wing
- gable
- hipped
- pyramidal
- çatı yüksekliği
- footprint oranları
- OSM çatı verisi bulunmadığında fallback davranışı

### Aşama 2 — Yapı Profillerini Ayırma

Hedef profiller:

- `defensive_tower`
- `gate_tower`
- `chapel`
- `castle_wing`
- `main_building`
- `service_building`

Bu sınıflandırma OSM kimliklerine hard-code edilmeyecek.

Kararlar şu verilerden türetilecek:

- footprint alanı
- uzunluk / genişlik oranı
- geometri
- yapı etiketi
- kale içindeki bağlam
- tahmini gövde yüksekliği

### Aşama 3 — Şapel Çatısı

Şapel için hedef:

- belirgin gable çatı
- uzun eksene paralel mahya
- gövdeyle uyumlu çatı yüksekliği
- fiziksel baskıda görülebilir siluet
- kapalı manifold mesh
- bina gövdesiyle boşluksuz birleşim

### Aşama 4 — Uzun Kale Kanatları

Uzun kanatlar için hedef:

- flat roof yerine eğimli çatı
- footprint uzun eksenine uygun mahya
- kuleleri bastırmayan daha düşük çatı oranı
- komşu binalarla çakışmama
- kalenin genel siluetini güçlendirme

### Aşama 5 — Hibrit Çatı Yüksekliği

Çatı yüksekliği yalnızca sabit bir katsayıyla belirlenmeyecek.

Hesapta kullanılacak faktörler:

- bina gövde yüksekliği
- footprint kısa kenarı
- footprint uzunluk / genişlik oranı
- yapı profili
- minimum basılabilir yükseklik
- maksimum siluet oranı

Yaklaşık hedefler:

    Ana kule    : gövdenin yüzde 45–50’si
    Küçük kule  : gövdenin yüzde 30–35’i
    Kapı kulesi : gövdenin yüzde 25–30’u
    Şapel       : footprint ve gövde oranına göre
    Uzun kanat  : daha düşük ve yatay siluet

### Aşama 6 — Topoloji

Her yeni çatı geliştirmesinde şu değerler zorunlu olacaktır:

    open_edge_count = 0
    non_manifold_edge_count = 0

Ayrıca:

- duplicate triangle olmayacak
- degenerate triangle olmayacak
- çatı ile bina gövdesi arasında boşluk olmayacak
- çatı kontrolsüz biçimde bina dışına taşmayacak
- kanat ve kule çatıları çakışmayacak

### Aşama 7 — Regresyon

Hohenzollern değişikliklerinden sonra:

    python -m pytest -q
    PYTHONPATH=. python Test/run_regression_suite.py castles

komutları çalıştırılacak.

Yeniden doğrulanacak gerçek kaleler:

- Rumeli Hisarı
- Burghausen
- Hohenzollern
- Hohenneuffen

---

## 9. Castle Engine İçin Orta Vadeli Plan

1. Hohenzollern şapel ve kanat çatılarını tamamlamak.
2. Hohenzollern siluetini yeniden değerlendirmek.
3. Gerekirse kule çatı oranlarını son kez ayarlamak.
4. Rumeli Hisarı görsel ayrıntılarını geliştirmek.
5. Crenellation dağılımını rafine etmek.
6. Plaka, border, isim, tarih ve ölçek sistemini tamamlamak.
7. Rumeli Hisarı’nın fiziksel baskı sürümünü hazırlamak.
8. Eski bütün kaleleri tek komutla doğrulamak.
9. Castle Engine’i yeni gerçek kalelerde test etmek.
10. Bulunan genel sorunları CORE motoruna ve regresyon testlerine eklemek.

Temel çalışma ilkesi:

> Her kale testi yalnızca o kaleyi düzeltmek için kullanılmayacaktır. Bulunan sorun ana motora genellenecek, regresyon testine dönüştürülecek ve önceki kaleler yeniden doğrulanacaktır.

---

## 10. Uzun Vadeli ATLAS Planı

Castle Engine tamamlandıktan sonra:

1. Anıtkabir premium model geliştirmesi
2. şehir modelleme motorunun ürün seviyesine getirilmesi
3. otomatik plaka ve yazı sistemi
4. seçilebilir ölçek
5. seçilebilir sahne kapsamı
6. ürün önizleme sistemi
7. çevrimiçi kişiselleştirme
8. My Life Map
9. Our Love Map
10. Family Heritage
11. Amazon ve diğer satış kanalları
12. 2.5D kişisel fotoğraf kabartma motoru
13. şehir ve hatıra ürünlerinin aynı ATLAS platformunda birleştirilmesi

İlk gerçek ATLAS STL modeli için korunacak özel hedef:

> Anıtkabir, ATLAS tarafından üretilen ilk gerçek model olarak küçük bir metadata imzası taşıyacaktır.

---

## 11. Sonuç

13 Temmuz 2026 itibarıyla ATLAS_ENGINE’in Castle Engine altyapısında önemli bir eşik geçildi.

Bugünün ana kazanımları:

- semantik sorun kayıtları ayrıntılı hâle getirildi
- INFO / WARN / FAIL sınıflandırması eklendi
- gerçek kale fixture’ları doğrulandı
- genel aktif paket 67 teste ulaştı
- kale regresyon paketi 16 dosyayı gerçekten çalıştırır hâle getirildi
- sessiz pytest atlama riski giderildi
- değişiklikler kontrollü biçimde commit edildi
- görsel geliştirmeye güvenli şekilde dönülebilecek altyapı oluşturuldu

Bir sonraki çalışma noktası:

> Hohenzollern şapel ve uzun kanat binalarının mevcut çatı karar akışını incelemek ve genel Castle Engine’i bozmadan eğimli/gable çatı sistemini geliştirmek.
