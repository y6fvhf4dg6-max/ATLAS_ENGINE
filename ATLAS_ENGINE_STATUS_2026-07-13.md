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

---

## 12. 14 Temmuz 2026 — Foundation-First ve Anıtkabir Çalışmaları

Castle Engine çalışmaları dondurulduktan sonra ana odak, genel şehir ve anıtsal yapı motorunun Foundation-First mimarisi üzerinde geliştirilmesine çevrildi.

Bu çalışmanın temel amacı yalnızca Anıtkabir’i düzeltmek değil; eğimli arazide bulunan bütün bina, platform, merdiven, anıt, heykel ve tarihî yapı bileşenlerinin dünya genelinde kullanılabilecek genel kurallarla üretilmesini sağlamaktır.

Castle Engine kodu bu süreçte değiştirilmedi.

---

## 13. Foundation Placement Sisteminin Düzeltilmesi

Binaların yalnızca tek bir terrain noktasına göre yerleştirilmesi, özellikle geniş veya U biçimli footprint’lerde bazı yapıların arazi içine gömülmesine neden oluyordu.

Bu sorun için footprint-aware terrain örnekleme sistemi geliştirildi.

Yapılan değişiklikler:

- `CORE/atlas_foundation_sampler.py` genişletildi
- poligon içinden terrain örneği alınması sağlandı
- poligon sınırındaki noktalar hesaba katıldı
- tek nokta yerine footprint genelini temsil eden terrain değerleri kullanılmaya başlandı
- aşırı yüksek veya düşük tekil örneklerin etkisini azaltmak için robust referans politikası eklendi
- placement metadata kayıtları geliştirildi

Yeni metadata alanları:

- `reference_z`
- `placement_percentile`
- `sample_mode`

Foundation surface builder gerçek footprint noktalarını kullanacak şekilde güncellendi.

Bu değişiklik sonucunda Anıtkabir çevresindeki U biçimli ve geniş yapıların terrain içine gömülme sorunu giderildi.

---

## 14. Elevated Pedestrian Area Okuma Sistemi

Anıtkabir’de merdiven, platform ve terasların önemli bir bölümü OSM verisinde bina olarak değil şu biçimde tutuluyordu:

    highway=pedestrian
    area=yes
    height=<pozitif değer>

Bu kayıtlar daha önce normal pedestrian path olarak okunuyor ve üç boyutlu yapı hâline getirilmiyordu.

`CORE/atlas_local_osm_reader.py` içinde yeni elevated-area okuma sistemi geliştirildi.

Eklenen davranışlar:

- kapalı `highway=pedestrian` alanları tespit edildi
- `area=yes` şartı eklendi
- yalnızca pozitif ve sayısal `height` değerleri kabul edildi
- bu kayıtlar normal pedestrian path listesinden ayrıldı
- yeni `elevated_areas` veri grubu oluşturuldu
- engine sonuç raporuna `reader_elevated_areas` alanı eklendi

Anıtkabir fixture’ında:

    elevated area sayısı : 57
    pedestrian path sayısı: 32

olarak doğrulandı.

Bu ayrım sayesinde merdiven ve platform kayıtları, yol yüzeyi yerine gerçek hacimli geometriler olarak işlenebilir hâle geldi.

---

## 15. Elevated Area Foundation Builder

Yeni dosya oluşturuldu:

    CORE/atlas_elevated_area_foundation_builder.py

Builder’ın temel görevleri:

- elevated-area poligonlarını terrain üzerine yerleştirmek
- düz üst yüzey üretmek
- kapalı ve manifold hacim oluşturmak
- iç içe elevated-area kayıtlarında parent/child ilişkisi kurmak
- ardışık basamakların gerçek yükseklik farkını korumak

Parent seçimi şu genel kurallarla yapılıyor:

- parent poligonu child’dan daha büyük olmalı
- parent yüksekliği child yüksekliğinden düşük olmalı
- child merkez noktası parent poligonu içinde bulunmalı
- birden fazla aday varsa en küçük kapsayıcı parent seçilmeli

Child alanların terrain’den yeniden başlaması engellendi.

Yeni davranış:

    child bottom Z = parent top Z
    child top Z    = parent top Z + ölçeklenmiş yükseklik farkı

Bu sayede iç içe OSM platformları bağımsız dev bloklar yerine birbirine bağlı kademeler olarak üretildi.

---

## 16. Basamak Yüksekliği Hatasının Düzeltilmesi

İlk elevated-area sürümünde her child basamağa minimum yazdırılabilir kalınlık uygulanıyordu.

Bu davranış gerçek ölçekte 0,25 metre olan bir basamağı yaklaşık:

    gerçek ölçeklenmiş değer : 0,045 mm
    önceki zorunlu değer     : 0,180 mm

yüksekliğe çıkarıyordu.

Sonuç olarak merdivenler yaklaşık dört kat fazla yükseliyor ve yapı silueti bozuluyordu.

Bu hata giderildi.

Child alanlarda artık:

    height_increment_mm =
        child_height_mm - parent_height_mm

değeri korunuyor.

Minimum yazdırılabilir kalınlık yalnızca terrain üzerine doğrudan oturan bağımsız kök alanlarda kullanılıyor.

Bu değişiklikten sonra:

- Aslanlı Yol giriş basamakları oluştu
- tören alanına çıkan basamaklar okunabilir hâle geldi
- mozole giriş merdivenleri gerçek kademelerine yaklaştı
- platformlar ayrı hacimler olarak görünmeye başladı

---

## 17. Root Elevated Area Terrain Referansı

Terrain üzerine doğrudan oturan büyük elevated-area poligonlarında ilk politika şuydu:

    top_z = highest_terrain_z + printable_height

Bu yöntem poligon içindeki tek bir yüksek terrain köşesinin bütün platformu yukarı taşımasına neden oluyordu.

Örnek sorunlu kayıt:

    OSM ID       : 396671950
    height       : 1.25 m
    footprint    : yaklaşık 16.660 × 17.197 mm
    terrain farkı: yaklaşık 1.350 mm
    maksimum duvar yüksekliği: yaklaşık 1.577 mm

Bu nedenle bazı platformlarda gereksiz yüksek istinat duvarları oluşuyordu.

MAX, P90, median ve merkez terrain referansları karşılaştırıldı.

Karar:

- kök elevated-area üst kotu median terrain değerinden hesaplanacak
- üst yüzeyin üzerinde kalan terrain noktaları sınırlandırılacak
- minimum fiziksel kalınlık korunacak
- platform terrain içine kontrollü biçimde gömülebilecek

Yeni metadata:

- `terrain_reference_mode`
- `terrain_reference_z`
- `highest_terrain_z`

Yeni root politikası:

    terrain_reference_mode = median

Bu değişiklik sonucunda büyük platformların terrain tabanına kadar uzanan gereksiz duvarları önemli ölçüde azaldı.

---

## 18. Artwork ve Heykel Okuma Sistemi

Anıtkabir’deki Aslanlı Yol heykellerinin bina veya alan geometrisi olmadığı tespit edildi.

OSM kayıt biçimleri:

    tourism=artwork
    artwork_type=statue
    statue=animal

Anıtkabir fixture’ında:

    hayvan heykeli : 24
    diğer artwork  : 2
    toplam artwork : 26

olarak bulundu.

`CORE/atlas_local_osm_reader.py` içine artwork node desteği eklendi.

Her artwork kaydında şu bilgiler korunuyor:

- OSM ID
- latitude
- longitude
- geometry type
- bütün OSM tag’leri
- artwork type
- statue type
- name

Reader sonucu içine yeni grup eklendi:

    artworks

Artwork kayıtları bina alan filtresinden bağımsız çalışıyor.

Bu özellikle küçük heykel, anıt, sütun ve benzeri noktasal tarihî öğeler için genel bir altyapı oluşturdu.

---

## 19. Artwork Foundation Builder

Yeni dosya oluşturuldu:

    CORE/atlas_artwork_foundation_builder.py

İlk sürümün görevi artwork node’larını terrain üzerine kapalı ve yazdırılabilir küçük hacimler olarak yerleştirmekti.

İlk profiller:

    animal_statue:
        width  = 0.90 mm
        depth  = 1.40 mm
        height = 1.00 mm

    generic_statue:
        width  = 0.90 mm
        depth  = 0.90 mm
        height = 1.40 mm

Üretilen her artwork mesh’i:

- terrain Z değerine oturuyor
- kapalı hacim oluşturuyor
- 12 üçgen içeriyor
- open edge üretmiyor
- non-manifold edge üretmiyor
- bina alan filtresinden etkilenmiyor

Builder ana Foundation-First engine’e bağlandı.

Yeni engine rapor alanları:

- `reader_artworks`
- `artwork_meshes`

Yeni mesh grubu:

    mesh_groups["artworks"]

---

## 20. Hayvan Heykeli Yönlendirmesi

İlk artwork meshleri doğru koordinatlarda fakat dünya X/Y eksenlerine paralel dikdörtgen bloklar olarak görünüyordu.

Aslanlı Yol heykelleri analiz edildi.

Sonuç:

    toplam heykel : 24
    sıra sayısı   : 2
    yol doğrultusu: yaklaşık -52.478 derece
    sıra uzaklığı : yaklaşık ±2.1 mm

Genel ve Anıtkabir’e özel olmayan bir yönlendirme politikası geliştirildi.

Her `animal_statue` için:

- en yakın aynı profilli artwork bulunuyor
- iki nokta arasındaki eksen hesaplanıyor
- açı `-90° ile +90°` aralığında normalize ediliyor
- footprint bu eksene göre döndürülüyor

Bu sayede Aslanlı Yol’daki iki heykel sırası yol doğrultusuna paralel hâle geldi.

Aslanlar henüz ayrıntılı hayvan geometrisi değil, ölçeklenmiş ve yönlendirilmiş düşük detaylı hacimlerdir.

Ayrıntılı heykel profili daha sonraki bir geliştirme aşamasına bırakıldı.

---

## 21. Anıtkabir Elevated-Area Geometri Teşhisi

Anıtkabir ana merdivenlerinde yelpaze veya ışın biçiminde çizgiler görüldü.

İlk olası nedenler ayrı ayrı araştırıldı:

- terrain çakışması
- bina çakışması
- eş düzlemli yüzeyler
- STL görüntüleyici z-fighting
- parent/child taban çakışması
- yanlış parent ilişkisi
- aşırı yüksek root platformlar

Yalnızca elevated-area meshlerinden oluşan ayrı STL üretildi:

    OUTPUT/STL/anitkabir_elevated_areas_only.stl

İzole STL sonucu:

    elevated mesh : 55
    triangles     : 6208

Yelpaze biçimlerinin bu izole STL’de de bulunduğu doğrulandı.

Böylece sorunların:

- terrain’den
- binalardan
- artwork meshlerinden
- genel STL katman çakışmasından

kaynaklanmadığı kesinleşti.

---

## 22. İç İçe Basamak Poligonlarının Yapısı

Basamak zincirindeki parent ve child poligonlar ayrıntılı biçimde karşılaştırıldı.

Ana zincir:

    1.25 m
    1.50 m
    1.75 m
    2.00 m
    ...
    11.50 m

seviyelerine kadar ilerliyor.

Zincirin büyük bölümünde child poligonlar parent poligonun:

    yüzde 80–94

oranında aynı sınırlarını tekrar kullanıyor.

Birçok seviyede:

- 50’den fazla child kenarı bulunuyor
- bunların yalnızca 2–7 tanesi yeni kenar
- kalan kenarlar parent sınırıyla ortak
- her yeni seviyede genellikle yalnızca birkaç köşe geri çekiliyor

Örnek:

    height       : 1.50 m
    child edges  : 67
    shared edges : 63
    new edges    : 4
    shared ratio : %94.0

Başka bir örnek:

    height       : 7.25 m
    child edges  : 28
    shared edges : 26
    new edges    : 2
    shared ratio : %92.9

Bu sonuç, OSM kayıtlarının ayrı basamak şeritleri değil, birikimli üst platform poligonları olduğunu gösterdi.

Ham OSM poligonları her seviyede birkaç köşe kaybederek küçülüyor.

Builder bu ham sınırları aynen hacme dönüştürdüğü için bazı seviyelerde düz basamak cephesi yerine tek noktaya yönelen yelpaze biçimleri oluşuyor.

---

## 23. Ortak Parent Kenarı Metadata Sistemi

Child poligon kenarlarının parent sınırında bulunup bulunmadığını belirleyen genel geometri fonksiyonları eklendi.

Yeni yardımcı fonksiyonlar:

- `_edge_lies_on_polygon_boundary`
- `_point_lies_on_segment`

Bu sistem yalnızca uç noktaları birebir aynı olan kenarları değil, daha uzun bir parent kenarının üzerinde kısmen bulunan child kenarlarını da ortak sınır olarak kabul ediyor.

Yeni mesh metadata alanları:

- `shared_parent_edge_count`
- `new_step_edge_count`
- `shared_parent_edge_indices`
- `new_step_edge_indices`

Bu metadata şu aşamada geometriyi değiştirmiyor.

Ama bir sonraki geliştirmede:

- gerçek yeni basamak cephesini
- parent ile ortak dış sınırı
- yapısal geçiş seviyelerini

birbirinden ayırmak için kullanılacak.

---

## 24. Parent Embed Deneyi ve Geri Alınması

Yelpaze çizgilerinin eş düzlemli parent ve child yüzeylerinden kaynaklanabileceği ihtimali test edildi.

Geçici olarak şu sabit eklendi:

    PARENT_EMBED_MM = 0.01

Child mesh alt yüzeyi parent üst yüzeyinden 0,01 mm aşağı gömüldü.

Bu deney:

- basamak üst kotunu değiştirmedi
- child yükseklik farkını korudu
- regresyon testlerinden geçti

Ancak görsel sonuçta yelpaze biçimleri devam etti.

Daha sonra şüpheli üst yüzeylerde dihredral açı analizi yapıldı.

Sonuç:

    non_coplanar = 0
    max_angle    = 0.000000°

Bu, yelpaze veya ışın biçiminde görünen çizgilerin gerçek yüzey kırıkları olmadığını; tamamen düz üst yüzeylerin triangülasyon kenarları olduğunu doğruladı.

Bu nedenle:

- `PARENT_EMBED_MM` çözüm olarak kabul edilmedi
- gereksiz parent/child örtüşmesi oluşturduğu için geri alındı
- child tabanı tekrar doğrudan parent üst kotundan başlatıldı
- ilgili regresyon testi eski doğru davranışa döndürüldü

Güncel durumda kodda `PARENT_EMBED_MM` bulunmamaktadır.

---

## 25. Building Part ve Anıtsal Yapı İstisnası

Anıtkabir fixture’ında 53 adet `building:part` way bulundu.

Bunların önemli bir bölümü:

- kolon
- pilaster
- yatay yapı parçası
- küçük anıtsal mimari öğe

niteliğindedir.

Mevcut reader yalnızca doğrudan `building=*` etiketi bulunan kayıtları normal bina olarak kabul ediyor.

Ayrıca genel şehir politikası:

    MIN_BUILDING_AREA_M2 = 20.0

olarak korunuyor.

Karar:

- normal binalar için 20 m² filtresi değişmeyecek
- tarihî ve anıtsal kompleks parçaları için genel bir istisna sistemi geliştirilecek
- istisna OSM ID hard-code’u kullanmayacak
- fiziksel minimum genişlik, derinlik ve yükseklik kontrolü uygulanacak
- geçerli küçük mimari parçalar ana bina motoruna dahil edilecek

Anıtkabir’de görülen havada kalan yatay `building:part` ve eksik kolonlar bu aşamada henüz çözülmedi.

Bu çalışma elevated-area ve artwork sistemleri tamamlandıktan sonra ele alınacak.

---

## 26. Test Durumu

Bu çalışma sırasında yeni regresyon testleri eklendi.

Başlıca test dosyaları:

- `Test/test_foundation_surface_builder.py`
- `Test/test_local_osm_reader_elevated_areas.py`
- `Test/test_elevated_area_foundation_builder.py`
- `Test/test_local_osm_reader_artworks.py`
- `Test/test_artwork_foundation_builder.py`

Doğrulanan davranışlar:

- footprint-aware foundation placement
- elevated-area reader ayrımı
- parent/child platform ilişkisi
- gerçek ölçeklenmiş basamak farkı
- median terrain referansı
- yüksek terrain noktalarının sınırlandırılması
- artwork node okuma
- kapalı artwork mesh üretimi
- animal statue yönlendirmesi
- ortak parent sınırlarının tespiti
- child tabanının doğrudan parent üst kotundan başlaması
- düz elevated-area üst yüzeylerinin coplanar olması

Şüpheli üst yüzeylerde yapılan dihredral açı analizinde:

    non_coplanar = 0
    max_angle    = 0.000000°

sonucu alındı.

Son tam regresyon sonucu:

    130 passed in 0.48s

Bu aşamada test paketi temizdir.

---


## 27. Henüz Commit Edilmemiş Çalışmalar

Foundation-First, elevated-area ve artwork geliştirmeleri çalışma ağacında bulunmaktadır.

Bu bölüm için henüz nihai commit oluşturulmadı.

Elevated-area yelpaze çizgileri üzerindeki teknik inceleme tamamlandı:

- izole elevated-area STL üretildi
- sorunlu seviyelerin yeni kenarları ölçüldü
- üst yüzeylerde dihredral açı analizi yapıldı
- bütün şüpheli üst yüzeylerin coplanar olduğu doğrulandı
- `PARENT_EMBED_MM` deneyi geri alındı
- elevated-area geometrisini yalnızca triangülasyon çizgileri nedeniyle değiştirmeme kararı alındı

Commit öncesinde yapılması gerekenler:

1. durum dosyasındaki son teknik sonuçları doğrulamak
2. küçük anıtsal `building:part` çalışmalarını tamamlamak
3. Anıtkabir görsel sonucunu yeniden doğrulamak
4. tam pytest paketini çalıştırmak
5. eski şehir ve kale fixture’larını doğrulamak
6. `git diff --check` çalıştırmak
7. değişiklikleri mantıksal commit gruplarına ayırmak
8. kontrollü commit oluşturmak

Castle Engine mantığı bu süreçte değiştirilmedi.

---


## 28. Mevcut Kesin Teşhis

Anıtkabir ana merdivenlerinde görülen yelpaze veya ışın biçimli çizgiler ayrıntılı olarak incelendi.

Yalnızca elevated-area meshlerinden oluşan ayrı STL üretildi:

    OUTPUT/STL/anitkabir_elevated_areas_only.stl

Bu STL:

    elevated mesh : 55
    triangles     : 6208

içermektedir.

Şüpheli seviyelerdeki üst yüzey üçgenlerinin komşu yüzey normalleri karşılaştırıldı.

Sonuç:

    non_coplanar = 0
    max_angle    = 0.000000°

Kesin teşhis:

> Yelpaze veya ışın biçiminde görünen çizgiler gerçek yüzey kırıkları, oluklar ya da basamak cepheleri değildir. Tamamen düz ve coplanar üst yüzeylerin STL triangülasyon kenarlarıdır.

Bu çizgiler STL görüntüleyicinin üçgen sınırlarını göstermesi nedeniyle görünür.

Fiziksel baskıda:

- ek basamak oluşturmaz
- oluk oluşturmaz
- kabartı oluşturmaz
- yüzey eğimi oluşturmaz

Bu nedenle elevated-area poligonlarını yalnızca bu çizgileri kaldırmak amacıyla değiştirmemek kararı alındı.

Sorun değildir:

- terrain örnekleme
- root platform yüksekliği
- parent seçimi
- child yükseklik farkı
- bina çakışması
- artwork çakışması
- STL writer
- z-fighting
- parent/child alt yüzey eş düzlemliliği
- gerçek non-coplanar yüzey kırığı

---


## 29. Son Kalınan Nokta

Sorunlu elevated-area seviyelerindeki yeni kenarların uzunluk ve açı analizi tamamlandı.

İncelenen seviyeler:

    1.50 m
    4.25 m
    7.00 m
    8.50 m
    9.25 m
    9.50 m

Bu seviyelerde parent sınırında bulunmayan child kenarları çıkarıldı ve ölçüldü.

Ölçülen bilgiler:

- edge index
- başlangıç koordinatı
- bitiş koordinatı
- uzunluk
- normalize edilmiş açı

Analiz, bazı poligonların birkaç uzun kenarı ortak bir noktada birleştirdiğini gösterdi. Ancak daha sonra yapılan yüzey normali analizi, görüntüleyicideki yelpaze çizgilerinin bu sınırların oluşturduğu gerçek kırıklar olmadığını kesinleştirdi.

`PARENT_EMBED_MM = 0.01` deneyi geri alındı.

Güncel doğru davranış:

    child bottom Z = parent top Z

Elevated-area sistemi şu anda:

- parent/child zincirini doğru kuruyor
- gerçek ölçeklenmiş yükseklik farkını koruyor
- root alanlarda median terrain referansı kullanıyor
- kapalı ve manifold mesh üretiyor
- düz üst yüzeyleri coplanar üretiyor

Son tam regresyon:

    130 passed in 0.48s

---


## 30. Güncel Çalışma Önceliği

Elevated-area yelpaze çizgileri artık motor hatası olarak değerlendirilmemektedir.

Bir sonraki çalışma noktası:

> Anıtkabir’de eksik kalan küçük anıtsal `building:part` kayıtlarını genel bina motoruna dahil edecek, normal şehir binalarındaki 20 m² alan filtresini bozmayan semantik ve fiziksel istisna sistemini geliştirmek.

Öncelik sırası:

1. `building:part` kayıtlarının reader karar akışını incelemek
2. küçük anıtsal parçalar için genel kabul kriterlerini tanımlamak
3. normal binalar için `MIN_BUILDING_AREA_M2 = 20.0` politikasını korumak
4. minimum fiziksel genişlik, derinlik ve yükseklik kontrollerini eklemek
5. kolon ve pilaster niteliğindeki parçaları sınıflandırmak
6. havada kalan yatay yapı parçasının parent/body bağlantısını çözmek
7. Anıtkabir görsel doğrulamasını tekrarlamak
8. artwork/aslan profilinin fiziksel baskı değerlendirmesini yapmak
9. tam regresyonu çalıştırmak
10. eski şehir ve kale fixture’larını yeniden doğrulamak
11. `git diff --check` çalıştırmak
12. değişiklikleri kontrollü biçimde commit etmek

Temel ilke korunmaktadır:

> Anıtkabir’de bulunan hiçbir sorun yalnızca Anıtkabir’e özel biçimde çözülmeyecektir. Her çözüm ana motora genellenecek, regresyon testine dönüştürülecek ve önceki gerçek sahnelerde yeniden doğrulanacaktır.
