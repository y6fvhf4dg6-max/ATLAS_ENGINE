# ATLAS_ENGINE — CURRENT STATUS

## Belgenin görevi

Bu dosya, ATLAS_ENGINE geliştirmesinin kesin güncel durumunu ve sıradaki tek işlemi tanımlar.

Yeni bir çalışma oturumunda önce:

- Docs/START_HERE.md
- Docs/STATUS/CURRENT_STATUS.md

okunmalıdır.

---

## Güncelleme tarihi

2026-08-04

---

## Aktif ticari ürün

ATLAS My Life Map Wall Collection

Temel fikir:

Every important memory has a location.

---

## Aktif referans ürün

Köln — Pädagogische Fakultät

Kurallar:

- İlk referans ürün Köln'dür.
- Köln tamamlanmadan Bonn'a geçilmez.
- Köln gerçek baskı ile doğrulanmadan standart kilitlenmez.

Sonraki ürün:

Bonn

---

## Onaylanmış ürün standardı

- Dış ölçü: 150 × 150 mm
- Şehir açıklığı: 134 × 134 mm
- Çerçeve: 8 mm
- Çerçeve derinliği: 6 mm
- Referans ölçek: 1:5500

Etiket plakası:

- 118 × 11 × 1.2 mm
- Alt çerçeve bandına gömme: 5 mm

Yazı:

- Font: DejaVu Sans Bold
- Primary: 4.2 mm
- Secondary: 2.8 mm
- Yazı derinliği: 0.6 mm
- Maksimum genişlik: 108 mm

---

## Fiziksel renk standardı

Hedef yazıcı:

Bambu Lab P2S Combo

Toplam fiziksel renk:

En fazla 5

Köln Premium V1 kilitli paleti:

1. Beyaz
   - frame
   - terrain
   - roads
   - building walls
   - label text
2. Kırmızı
   - building roofs
   - ileride seçili vurgu binası
3. Yeşil
   - parks
   - trees
4. Siyah
   - label plate
   - ileride plaka simgesi
5. Mavi
   - water

Köln PBF sahnesinde su mesh'i bulunmadığı için mevcut gerçek paket dört STL üretmektedir:

- white
- red
- green
- black

Su bulunan ürünlerde blue STL otomatik olarak eklenir.


---

## Mevcut üretim zinciri

OSM / SRTM
→ terrain
→ roads
→ parks
→ trees
→ buildings
→ semantic wall / roof separation
→ frame
→ hidden keyhole hanger
→ label plate
→ label text
→ combined STL
→ aligned multicolor STL package

Üretim çıktıları:

1. Birleşik referans STL
2. Aynı koordinat sisteminde renk bazlı ayrı STL dosyaları

Köln gerçek çok renkli paket çıktıları:

- `koeln_paedagogische_fakultaet_150mm__white.stl`
- `koeln_paedagogische_fakultaet_150mm__red.stl`
- `koeln_paedagogische_fakultaet_150mm__green.stl`

Son gerçek topoloji üretimi etiket parametreleri olmadan çalıştırıldığı için bu doğrulamada siyah plaka STL'si üretilmedi. Etiket plakası etkinleştirildiğinde `black` STL aynı multicolor exporter tarafından oluşturulur.

Çıktı klasörü:

`OUTPUT/STL/koeln_paedagogische_fakultaet_multicolor/`

---

## Dijital preview durumu

Preview katmanları:

- frame
- terrain
- building walls
- building roofs
- roads
- parks
- trees
- water
- label plate
- label text

Desteklenen çıktılar:

- PNG renk karşılaştırma preview
- OBJ interaktif geometri preview
- MTL material tanımları

Etiket preview zinciri tamamlandı ve ilgili regresyon paketi `49 passed` sonucu verdi.

---

## Kilitlenen etiket tasarımı

Wall Collection v1 etiket geometrisi dijital olarak kilitlenmiştir:

- Şehir geometrisi küçültülmez veya yukarı taşınmaz.
- Etiket plakası alt çerçeve bandına gömülür.
- Plaka ölçüsü: 118 × 11 × 1.2 mm
- Çerçeve gömme miktarı: 5 mm
- Yazı kabartması: 0.6 mm
- Primary yazı yüksekliği: 4.2 mm
- Secondary yazı yüksekliği: 2.8 mm
- Ekran görüntüsüne dayanarak daha fazla mikro ayar yapılmaz.
- Sonraki revizyon yalnız fiziksel baskı veya Bambu Studio doğrulamasına dayanır.

Bu kilit yalnız etiket tasarımını kapsar. Köln fiziksel baskıyla doğrulanmadan genel Wall Collection standardı nihai olarak kilitlenmiş sayılmaz.

---

## Fiziksel Köln baskısı ve askı revizyonu

İlk gerçek beyaz Köln baskısı incelendi.

Fiziksel gözlemler:

- filament liflenmesi/stringing mevcut
- tek renk ürün yeterli premium ayrışmayı sağlamıyor
- siyah plaka ve beyaz yazı gerekli
- kırmızı çatılar gerekli
- yeşil alan katmanı gerekli
- Pädagogische Fakultät binası özel olarak ayrıştırılmalı
- plakaya mezuniyet kepi veya alternatif simge eklenmeli

Askı kararı:

- Mevcut revize keyhole askı kabul edildi.
- Çivi başı girişi: 5.0 mm
- Kilit kanalı: 3.0 mm
- Kilitleme hareketi: 1.0 mm
- Kapalı üst taşıyıcı duvar: 1.75 mm
- 150, 200 ve 260 mm ürünlere genel motor standardı olarak uygulanır.
- Commit: `404c0d2 Improve wall hanger nail retention`
- Push tamamlandı.
- Wall Collection ilgili regresyon: 28 passed

## Çok renkli Köln üretim durumu

Tamamlanan:

- `KOELN_PREMIUM_V1` malzeme profili
- semantik bina duvarı / çatı ayrımı
- beş renkli STL paket exporter'ı
- aynı RGB sınıfındaki mesh gruplarını tek STL içinde birleştirme
- aynı renk grubundaki birebir yinelenen üçgenleri exporter seviyesinde tekilleştirme
- aynı yükseklikte tamamen örtülen gereksiz `building:part` meshlerini renderer seviyesinde eleme
- `leisure:park` tarafından tamamen örtülen `landuse:grass` meshlerini eleme
- aynı renkli komşu parkların ortak iç sınır duvarlarını kaldırma
- yalnız tek noktada temas eden park katılarını baskı toleransının altında ayrıştırma
- farklı yükseklikteki komşu bina renk katılarını silmeden ayrıştırma
- semantik bina üçgenleri, `bottom`, `top` ve çatı metadata geometrisini birlikte taşıma
- genel `roof:shape=pyramidal` bina çatı üreticisi:
  - düz üst kapak kaldırılır
  - footprint merkezli tepe noktası oluşturulur
  - `roof:height` ürün ölçeğine çevrilir
  - Bonner Münster ve Kreuzkirche gibi kule parçaları artık düz kolon yerine piramidal siluet alır
- focused çatı doğrulaması: `55 passed`
- gerçek Köln white, red ve green STL üretimi
- renderer ve multicolor exporter paketi: `20 passed`
- commit: `9436dea Fix multicolor wall collection topology`
- push: `origin/main`

Topoloji temizliğinden önceki non-manifold değerleri:

- white: `95`
- red: `88`
- green: `26`

Son gerçek Köln multicolor STL doğrulaması:

- white: `20356` triangle, `0 open edge`, `0 non-manifold edge`
- red: `9188` triangle, `0 open edge`, `0 non-manifold edge`
- green: `32588` triangle, `0 open edge`, `0 non-manifold edge`

Tamamlanan son Köln adımları:

- Pädagogische Fakultät hedef binası tamamen kırmızı katmana ayrıldı.
- Etikete siyah mezuniyet kepi simgesi eklendi.
- Dört STL tek assembly olarak Bambu Studio'da açıldı ve hizalama doğrulandı.
- Semantik STL filament atamaları yapıldı.
- Bambu Studio dilimlemesi başarıyla tamamlandı.
- Dilimleme sonucu:
  - yaklaşık `5 saat 4 dakika`
  - `96.36 g`
  - `60` filament değişimi
- Prime tower plaka içine taşındı ve sınır hatası giderildi.
- AMS eşlemesi doğrulandı:
  - kırmızı proje filamenti → AMS A2
  - gri test filamenti → AMS A3
  - siyah proje filamenti → AMS A4
- Kod commit'i:
  - `40cdf17 Add Köln graduation label and building highlight`
- Bambu Studio projesi kalıcı olarak kaydedildi:
  - `/Users/Kubi/Documents/koeln_paedagogische_fakultaet_150mm_FINAL.3mf`
- Proje ayrıca ATLAS_ENGINE üretim çıktısına kopyalandı:
  - `OUTPUT/3MF/koeln_paedagogische_fakultaet_150mm_FINAL.3mf`
  - doğrulanan dosya boyutu: `810 KB`

Açık işler:

- sipariş edilen nihai filamentler geldikten sonra dört renkli referans baskıyı almak
- gerçek baskıda renk, yazı, çerçeve, çatı ve küçük detay kalitesini değerlendirmek
- stringing sorununu baskı profili ve filament kalibrasyonu seviyesinde doğrulamak
- baskı sonucu uygunsa Köln ürün standardını nihai olarak kilitlemek

## İlk gerçek çok renkli üretim eşiği

2026-07-29 tarihinde Köln Pädagogische Fakultät ürünüyle ATLAS_ENGINE ilk kez:

- gerçek semantik çok renkli STL paketi,
- Bambu Studio assembly doğrulaması,
- fiziksel filament ataması,
- başarılı çok renkli dilimleme,
- AMS slot eşlemesi

aşamalarını uçtan uca tamamladı.

Bu, ATLAS_ENGINE'in geometri geliştirme aşamasından gerçek çok renkli fiziksel ürün üretim aşamasına geçtiği kalıcı bir proje kilometre taşıdır.

## Köln tamamlanma kriterleri

Köln referans ürünü tamamlanmış sayılması için:

- Geometri doğrulanacak.
- Preview kontrol edilecek.
- Final STL üretilecek.
- STL Bambu Studio'da açılacak.
- 5 renk atanacak.
- Baskı süresi kontrol edilecek.
- Filament tüketimi incelenecek.
- Test baskısı yapılacak.
- Gerekli revizyonlar tamamlanacak.
- Standart kilitlenecek.

---

## Aktif teknik rölyef hattı — Dalyan kaya mezarları

Köln Pädagogische Fakultät ticari referans ürün önceliği değişmemiştir.

Buna paralel olarak 2.5B rölyef motorunda Dalyan kaya mezarları profilinden çıkan genel preprocessing ihtiyacı motor seviyesinde çözülmüştür.

Tamamlanan mimari çalışmalar:

- `CORE/atlas_relief_preprocessor_chain.py` eklendi.
- Preprocessor zinciri sıralı callable bileşenleri uygular.
- `AtlasReliefPipeline.build_from_image()` yeni `preprocessors=()` parametresini kabul eder.
- Pipeline preprocess edilmiş luminance verisini `preprocessed_luminance` alanında döndürür.
- `image_settings["preprocessor_count"]` metadata kaydı eklendi.
- Zincir ve pipeline entegrasyonu test-first geliştirildi.
- İlgili test sonucu: `70 passed`.
- Commit: `7c1782b Add relief preprocessor chain`
- Push: `origin/main`

Dalyan entegrasyonu:

- `Test/preview_dalyan_rock_tombs_relief_profile.py` artık illumination-normalized varyant için geçici normalize edilmiş kaynak görüntü kullanmaz.
- Her iki varyant aynı özgün `SOURCE_PATH` üzerinden çalışır.
- Normalizasyon doğrudan pipeline'ın `preprocessors` parametresinden uygulanır.
- Kullanılan mevcut normalizer:
  - `AtlasRockReliefIlluminationNormalizer`
  - `illumination_sigma=14.0`
  - `detail_strength=0.80`
- Original ve illumination-normalized preview varyantları başarıyla yeniden üretildi.
- Commit: `bbddbdd Route Dalyan relief normalization through preprocessors`
- Push: `origin/main`

Mimari sonuç:

- Görüntü preprocessing artık ürün preview scriptlerine dağılmış geçici dosya işlemleri değildir.
- Ürüne özgü preprocessing adımları ana rölyef pipeline'ına sıralı ve yeniden kullanılabilir biçimde bağlanabilir.
- Aynı yapı gelecekte portre, taş yüzey, düşük kontrastlı fotoğraf ve diğer rölyef kaynaklarında kullanılabilir.

Son tamamlanan Dalyan adımı:

- `CORE/atlas_rock_relief_production_preset.py` eklendi.
- `AtlasRockReliefProductionPreset` immutable bir üretim sözleşmesi olarak tanımlandı.
- `DALYAN_ROCK_TOMBS_PRODUCTION_PRESET` eklendi.
- Üretim preset'i şu bileşenleri tek nesnede birleştirir:
  - ürün profili: `ROCK_CARVED_LANDMARK`
  - preprocessing zinciri: `DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET`
- `AtlasRockReliefProductionPreset.build_from_image(...)` eklendi.
- Bu çağrı kilitli `product_profile` ve `preprocessors` değerlerini `AtlasReliefPipeline.build_from_image(...)` hattına otomatik aktarır.
- Dalyan preview içindeki kilitli production varyantı artık profil ve preprocessing argümanlarını elle açmaz.
- Normalize edilmiş kaynak preview çıktısı ve pipeline üretimi aynı Dalyan üretim preset'inden beslenir.
- Üretim preset'i, preprocessing preset'i, illumination normalizer ve preprocessor chain odaklı doğrulama:
  - `14 passed`

Tamamlanan Dalyan fiziksel STL üretimi:

- `CORE/atlas_relief_stl_exporter.py` eklendi.
- `AtlasReliefSTLExporter.export_pipeline_result(...)` genel rölyef pipeline sonucundan kapalı relief mesh'i çıkarır.
- Export işlemi mevcut `EXPORT.atlas_stl_writer.AtlasSTLWriter` üzerinden yapılır.
- Exporter focused test sonucu: `4 passed`.
- `Test/preview_dalyan_rock_tombs_relief_profile.py` seçilen production sonucunu STL'ye aktarır.
- Üretilen dosya:
  - `OUTPUT/RELIEF/dalyan_rock_tombs/dalyan_rock_tombs_relief_80x50mm.stl`
- Fiziksel ölçü:
  - `80 × 50 mm`
- Üçgen sayısı:
  - `95.036`
- Solid adı:
  - `DALYAN_ROCK_TOMBS_RELIEF`

Sıradaki tek teknik işlem:

Dalyan STL dosyasının topolojisini, minimum kalınlığını ve fiziksel baskı uygunluğunu doğrulamak.

Daha sonraki Dalyan işleri:

1. STL topolojisini ve manifold durumunu doğrulamak.
2. Minimum taban ve rölyef kalınlıklarını doğrulamak.
3. Bambu Studio'da açıp dilimleme sonucunu incelemek.
4. Gerekli fiziksel revizyonları uygulamak.
5. Nihai üretim STL'sini kalıcı final dosya adıyla kaydetmek.

## Dokümantasyon durumu

Tamamlanan:

- Docs/START_HERE.md
- Docs/STATUS/CURRENT_STATUS.md

Sıradaki belgeler:

- Docs/STANDARDS/ATLAS_WALL_COLLECTION_REFERENCE_STANDARD.md
- Docs/PRODUCTS/KOELN_PAEDAGOGISCHE_FAKULTAET_REFERENCE.md

---

## Çalışma kuralları

- Tüm işlemler terminalden yapılır.
- Aynı anda yalnızca bir işlem yapılır.
- Kullanıcı çıktısı görülmeden sonraki adıma geçilmez.
- Manuel editör talimatı verilmez.
- git add . kullanılmaz.
- Yalnız ilgili dosyalar stage edilir.
- Test-first geliştirme uygulanır.
- Doğrulanmış adımlar commit edilir.
- Uygun noktada origin main dalına push edilir.

---

## Sıradaki tek işlem

Dalyan kaya mezarları için üretilen `80 × 50 mm` fiziksel STL'nin topolojisini, minimum kalınlığını ve baskı uygunluğunu doğrulamak.

Köln için fiziksel bağımlılık değişmemiştir:

- nihai filamentler geldikten sonra `OUTPUT/3MF/koeln_paedagogische_fakultaet_150mm_FINAL.3mf` açılacak
- gerçek dört renk eşlemesi kontrol edilecek
- son fiziksel referans baskı alınacak


---

## Oturum kapatma kuralı

Her geliştirme oturumu tamamlanmadan önce bu belge güncellenmelidir.

En az aşağıdaki bilgiler güncel olmalıdır:

- Tamamlanan teknik çalışmalar
- Alınan mimari kararlar
- Güncellenen belgeler
- Varsa yeni standartlar
- Bilinen açık işler
- Sıradaki tek teknik işlem

Bu belge güncellenmeden geliştirme oturumu tamamlanmış kabul edilmez.

Bu kural, ATLAS_ENGINE geliştirme metodolojisinin zorunlu bir parçasıdır.

## Dalyan kaya mezarları görsel varyant kararı

Dört shaded preview karşılaştırıldı:

- Original / Standard
- Original / Detail
- Illumination normalized / Standard
- Illumination normalized / Detail

Nihai üretim seçimi:

`Illumination normalized / Standard`

Bu seçim mevcut `DALYAN_ROCK_TOMBS_PRODUCTION_PRESET` ile doğrudan temsil edilir:

- `ROCK_CARVED_LANDMARK`
- `DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET`

Detail varyantı, kaya yüzeyindeki yüksek frekanslı dokuyu ve baskı gürültüsü riskini
gereksiz artırdığı için nihai üretimden çıkarıldı.

Sıradaki teknik işlem:

Üretilen Dalyan fiziksel STL dosyasının topoloji, minimum kalınlık ve baskı uygunluğu doğrulamasını yapmak.

## Dalyan relief üretim paketi

Dalyan Kaya Mezarları 80 × 50 mm relief ürünü kalıcı üretim paketine bağlandı.

- STL: hazır
- Kalite raporu: hazır
- Üçgen: 95.036
- Açık kenar: 0
- Non-manifold kenar: 0
- Kapalı mesh: evet
- Baskıya uygun topoloji: evet
- Baskı riski: WARN
- Uyarı nedeni: az miktarda 55° üzeri yüzey eğimi
- Kritik eğim örneği: 0
- Nihai `.3mf`: henüz oluşturulmadı
- Çok renkli parça/renk ayrımı: sıradaki ürün aşaması

## Relief semantik malzeme haritası

Çok renkli Dalyan relief üretiminin ilk altyapı adımı tamamlandı.

- Yeni modül: `CORE/atlas_relief_semantic_material_map.py`
- Yeni test: `Test/test_relief_semantic_material_map.py`
- Focused test sonucu: 3 passed
- Varsayılan malzeme bölgesi destekleniyor.
- Adlandırılmış semantik maskeler malzeme kimliklerine dönüştürülüyor.
- Yanlış çözünürlüklü maskeler reddediliyor.
- Üst üste binen maskeler reddediliyor.
- Gri ton eşiklerine dayalı otomatik ayrım üretim yaklaşımı olarak reddedildi.
- Gerçek Dalyan semantik maskeleri: henüz oluşturulmadı.
- Çok renkli relief STL parçaları: henüz oluşturulmadı.
- Nihai Dalyan `.3mf`: henüz oluşturulmadı.

## Relief semantik maske girişi

Semantik malzeme maskelerinin dosyadan yüklenmesi tamamlandı.

- Yeni modül: `CORE/atlas_relief_semantic_mask_input.py`
- Yeni test: `Test/test_relief_semantic_mask_input.py`
- Focused test sonucu: 4 passed
- Gri ton maske desteği: tamamlandı
- RGB maske desteği: tamamlandı
- Eşik tabanlı boolean dönüşüm: tamamlandı
- Beklenen çözünürlük doğrulaması: tamamlandı
- Geçersiz eşik değerlerinin reddedilmesi: tamamlandı
- Gerçek Dalyan `vegetation` maskesi: henüz oluşturulmadı
- Gerçek Dalyan `tomb_facade` maskesi: henüz oluşturulmadı

## Relief semantik maske seti

Tamamlandı:

- `CORE/atlas_relief_semantic_mask_set.py`
- `Test/test_relief_semantic_mask_set.py`
- Adlandırılmış çoklu maske yükleme
- Ortak boyut doğrulaması
- Çakışma kontrolü
- Varsayılan malzeme desteği
- Tek `uint8` malzeme kimlik haritası üretimi

Doğrulama:

- Semantik maske paketi: `10 passed`

Dalyan için sıradaki işlem:

- `vegetation` maskesini üretmek
- `tomb_facade` maskesini üretmek
- Maskeleri 240 × 99 aktif relief girdisiyle eşlemek

## Dalyan relief semantik maske sözleşmesi

Tamamlandı:

- `CORE/atlas_dalyan_relief_semantic_masks.py`
- `Test/test_dalyan_relief_semantic_masks.py`
- Aktif relief boyutu: `240 × 99`
- Varsayılan malzeme: `rock`
- `vegetation` maske yolu tanımlandı
- `tomb_facade` maske yolu tanımlandı

Doğrulama:

- Dalyan sözleşme testi: `1 passed`
- Tüm semantik maske paketi: `11 passed`

Sıradaki işlem:

- Gerçek `vegetation_240x99.png` maskesini üretmek
- Gerçek `tomb_facade_240x99.png` maskesini üretmek
- Maskeleri `AtlasReliefSemanticMaskSet` ile yüklemek

## 31 Temmuz 2026 — Çalışma ağacı temizliği ve kalıcılaştırma

Tamamlananlar:

- Eski ve izlenmeyen çekirdek geliştirmeler test edilerek iş paketlerine ayrıldı.
- Toplu ilk doğrulamada `382 passed` sonucu alındı.
- Başarısız kalan eski Galata `end_taper` prototipi incelendi.
- Bunun yerine kullanılan genel `road_approaches` hattı `29 passed` ile doğrulandı.
- Eski `end_taper` mesher ve testi silindi.
- Kalan izlenmeyen test paketi yeniden çalıştırıldı:
  - `382 passed in 1.26s`

Kalıcılaştırılan commitler:

- `7585a68 Add MediaPipe relief landmark adapter`
- `056ab94 Add terrain contour generation system`
- `8952793 Add terrain-following landcover builder`
- `798542e Add green area sampling and WorldCover aggregation`
- `4ff45f1 Add relief normal processing pipeline`
- `0253fb2 Add relief face semantic calibration layers`
- `bff4629 Add relief semantic height adjustment`
- `17f4f10 Improve ancient theatre and building relation handling`
- `34265d1 Refine Wall Collection label and material standards`

Focused doğrulamalar:

- MediaPipe adapter: `17 passed`
- Terrain contour: `41 passed`
- Terrain-following landcover: `9 passed`
- Green area + WorldCover: `20 passed`
- Relief normal pipeline: `101 passed`
- Relief face semantic calibration: `191 passed`
- Relief semantic height adjustment: `2 passed`
- Ancient theatre + OSM relation: `16 passed`
- Wall Collection standardları: `52 passed`

Ortam kararı:

- Ana ortam: `.venv`, Python `3.14.6`
- MediaPipe ortamı: `.venv-landmarks`, Python `3.12.13`
- MediaPipe ortamı çalışır durumda ve korunuyor.
- Yeniden kurulum listesi:
  `Docs/ENVIRONMENTS/requirements-landmarks-python312.txt`

Wall Collection güncel standart sinyali:

- Bonn referans ürünü: `170 × 170 mm`
- Harita açıklığı: `150 × 150 mm`
- Ölçek: `1:3000`
- Çerçeve bandı: `10 mm`
- Etiket:
  - birinci satır `BONN`
  - ikinci satır `GEBURTSORT`
  - sağda doğum günü pastası simgesi
- Etiketli ve etiketsiz STL paketleri ayrı korunuyor.

Bilinen açık işler:

- Untracked preview dosyalarının sınıflandırılması
- Eski devir/status belgelerinin arşiv veya commit kararı
- `CORE/__init__.py` ve `CORE/atlas_tower_geometry.py` değerlendirmesi
- `Test/test_galata_real_bridge_base_topology.py` değerlendirmesi
- `Data/`, `Tools/`, `Test/atakule/` ve yardımcı preview girdilerinin kontrollü incelemesi
- Gereksiz preview/yardımcı dosyaların silinmesi veya kalıcı paketlere alınması

Sıradaki tek teknik işlem:

Kalan untracked preview, yardımcı test, belge ve veri klasörlerini sınıflandırmak; yalnız üretim veya regresyon değeri olanları ayrı commitlerle korumak.

## Yapılacaklar Listesi

### AtlasPhysicalDetailResolver v0.1

### Church Landmark Profile v0.1 Pilot

# 1 Ağustos 2026 — Güncel kesin çalışma noktası

## Aktif geliştirme

Bonn Münsterplatz — Church Landmark Profile v0.1 pilotu.

Köln fiziksel referans ürünü ticari ana referans olarak korunmaktadır; ancak güncel teknik geliştirme Bonn Bonner Münster kilise geometrisi üzerindedir.

## Bonn ürün standardı

- Dış ürün: `170 × 170 mm`
- Harita açıklığı: `150 × 150 mm`
- Ölçek: `1:3000`
- Çerçeve genişliği: `10 mm`
- Çerçeve derinliği: `6 mm`
- Etiket:
  - `BONN`
  - `GEBURTSORT`
  - doğum günü pastası simgesi

## Tamamlanan Church Landmark yapısal paketleri

- Gerçek footprint yönelimi ve ekstrüzyonu
- Kademeli kilise gövde seviyeleri
- Mimari çatı profil sistemi
- Mimari çatı mesheri
- Kule profil sistemi
- Kule mesheri
- Polygon crossing/outer tower geometrileri
- Box batı kuleleri
- Polygon spire çatıları
- Dış kulelerin gerçek footprint içine taşınması
- Merkez kule iki kademeli sekizgen çatı geçişi
- Merkez kule külah yüksekliğinin fiziksel üst halka açıklığından ve 30° eğimden türetilmesi

Son ilgili doğrulama:

- Church tower/profile/landmark/Bonn gerçek fixture paketi: `56 passed`

## Kule penceresi durumu

- Standalone pencere mesheri ve testleri korunuyor.
- Üretim entegrasyonu geometrik çakışma ve küçük kama artefaktları nedeniyle geri alındı.
- Revert:
  - `d5df3a7 Revert "Integrate church tower windows"`
- Yeniden entegrasyon yapılmadan önce recessed/inlay geometri sözleşmesi geliştirilmelidir.

## Son commit zinciri

- `919f857 Refine crossing tower roof transition`
- `6ecdc41 Derive crossing tower spire height from roof span`
- `006aa15 Center cathedral crossing tower on transept`
- `c5f1266 Align crossing tower with resolved octagonal tower center`

Son push:

- `006aa15..c5f1266 main -> main`

## Son Bonn üretimi

- `OUTPUT/STL/bonn_muensterplatz_city_150mm.stl`
  - `57.056` triangle
- `OUTPUT/STL/bonn_muensterplatz_wall_collection_170mm.stl`
  - `57.204` triangle
- white:
  - `20.338`
- red:
  - `9.982`
- green:
  - `33.868`
- black:
  - `148`

## Kritik açık sorun — merkez kule yerleşimi

Uzun külahlı `crossing_tower`, Bambu Studio görsel doğrulamasında büyük sekizgen yapının tam merkezine oturmuş görünmemektedir.

Son yapılanlar:

1. Katedral profilindeki `0.02` boyuna kayma kaldırıldı.
2. Kule nef–transept kesişim merkezine taşındı.
3. Bunun yanlış hedef olduğu görüldü.
4. Büyük sekizgen yapı `outer_polygon_tower` olarak tanımlandı.
5. `crossing_tower`, footprint-safe resolver tarafından çözümlenen `outer_polygon_tower` merkezine bağlandı.
6. Otomatik testte iki yerel merkez eşit doğrulandı.
7. Buna rağmen Bambu Studio görseli, kullanıcının kastettiği sekizgen yapı ile uzun kulenin hâlâ merkezlenmediğini gösterdi.

Teknik sonuç:

- Otomatik test yanlış veya eksik geometrik nesneyi karşılaştırıyor olabilir.
- `outer_polygon_tower` olarak adlandırılan nesne, görselde hedeflenen büyük sekizgen gövde olmayabilir.
- Yeni oran veya manuel ofset uygulanmamalıdır.
- Z yerleşimi tartışmasına geçilmemelidir.
- Önce doğru hedef gövde kesin olarak tanımlanmalıdır.

## Sıradaki tek teknik işlem

Gerçek Bonn mesh çıktısında:

1. Görseldeki büyük sekizgen yapıyı oluşturan kesin mesh bileşenini belirlemek.
2. Bu bileşenin gerçek alt ve üst halka merkezlerini hesaplamak.
3. Uzun külahlı kulenin taban halkası merkezini hesaplamak.
4. İki merkezi dünya ve yerel koordinatlarda karşılaştırmak.
5. Hedef bileşen kesinleşmeden kod değişikliği yapmamak.

## Çalışma ağacı notu

Son kontrolde çalışma ağacında izlenmeyen bir dosya görülmüştür:

- `main`

Bu dosya incelenmeden silinmemeli veya commit edilmemelidir.

## Dokümantasyon kararı

Bu bölüm, eski Dalyan merkezli “sıradaki tek işlem” kayıtlarının yerine güncel aktif teknik çalışma noktasını tanımlar.

Çelişki halinde bu `1 Ağustos 2026 — Güncel kesin çalışma noktası` bölümü esas alınmalıdır.

# 4 Ağustos 2026 — Master Landmark Catalog V1 tamamlandı

## Güncel kesin çalışma noktası

Son temiz ve push edilmiş commit:

- `afbf46f Drive bridge foundation components from catalog flags`

Git durumu:

- `HEAD == origin/main`
- tracked çalışma ağacı temiz
- yalnız aşağıdaki devir belgeleri untracked:
  - `Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-08-01.md`
  - `Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-08-04.md`

Son tam regresyon:

- `2162 passed in 9.27s`

## Tamamlanan Master Landmark Catalog V1

Yeni merkezi landmark kataloğu:

- `CORE/atlas_master_landmark_catalog.py`
- `Test/test_master_landmark_catalog.py`

İlk katalog kayıtları:

- Bonn Münster
- Kreuzkirche Bonn
- Galata Tower
- Galata Bridge

Katalog tarafından yönetilen karar alanları:

- `landmark_family`
- `grammar_name`
- `profile_name`
- `component_flags`
- `geometry_overrides`

Üretim kodunda kataloğa bağlanan sistemler:

- Church grammar resolver
- Church geometry override resolver
- Tower profile resolver
- Bridge profile resolver
- Bridge foundation support/parapet component activation

Kimlik çözümleme:

- Wikidata kimlikleri normalize edilir.
- OSM kimlikleri güvenli biçimde normalize edilir.
- Wikidata eşleşmesi varsa OSM kimliğine göre önceliklidir.
- Bilinmeyen veya geçersiz kimlik güvenli biçimde `None` döndürür.

## Teknik sonuç

`CORE/` altında Bonn Münster, Kreuzkirche, Galata Tower veya
Galata Bridge için doğrudan sabit `Q...` Wikidata kararı kalmamıştır.

Test ve preview dosyalarındaki sabit kimlikler fixture, assertion veya
sahne tanımıdır; üretim karar mantığı değildir.

Bridge foundation hattında:

- `supports`
- `parapets`

artık birbirinden bağımsız olarak, katalogdaki ilgili
`component_flags` değerleriyle etkinleştirilir.

Galata Bridge yol yaklaşımı ve profil davranışı korunmuştur.

## Sıradaki tek teknik işlem

Master Landmark Catalog V1 için yeni soyutlama eklenmeyecektir.

Aktif geliştirme tekrar ürün doğrulama önceliğine döner:

1. Köln Premium V1 nihai filamentlerle fiziksel olarak basılır.
2. Renk dengesi, yazı okunabilirliği, çerçeve, çatılar, vurgu binası,
   stringing ve askı sistemi değerlendirilir.
3. Yalnız fiziksel baskı veya Bambu Studio doğrulamasından çıkan somut
   probleme göre revizyon yapılır.
4. Köln kabul edilmeden Bonn yeni premium standart olarak kilitlenmez.

Bu bölüm, daha eski Bonn merkez-kule veya Dalyan merkezli
“sıradaki tek işlem” kayıtlarına göre önceliklidir.

# 5 Ağustos 2026 — Karaköy gerçek ibadethane doğrulaması

## Güncel güvenli nokta

Son temiz ve push edilmiş commit:

- `aef280d Catalog Kılıç Ali Paşa Mosque grammar`

Git durumu:

- `HEAD == origin/main`
- tracked çalışma ağacı temiz
- yalnız aşağıdaki devir belgeleri untracked:
  - `Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-08-01.md`
  - `Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-08-04.md`

Son tam regresyon:

- `2267 passed in 9.88s`

## Tamamlanan teknik çalışma

Building-part hiyerarşisinden otomatik ibadethane grammar çıkarımı
tamamlandı ve push edildi:

- commit: `5dbbffa Infer worship and church grammars from components`

Cami çıkarımı:

- bir minare:
  - `single_dome_single_minaret`
- iki veya daha fazla minare ve iki veya daha fazla kubbe:
  - `multi_dome_multi_minaret`
- iki veya daha fazla minare fakat yeterli kubbe kanıtı yok:
  - `footprint_fallback`
- component sayıları üretim profilinin güvenli üst sınırında tutulur.

Kilise çıkarımı:

- bir `tower:type=bell_tower`:
  - `single_west_tower`
- iki `tower:type=bell_tower`:
  - `twin_west_towers`
- katalog grammar kararı component çıkarımından önce gelir.

## Karaköy gerçek PBF doğrulaması

Kaynak:

- `Data/OSM/turkey-latest.osm.pbf`

Yerel doğrulama fixture’ı:

- `Data/OSM/karakoy-kilic-ali-pasa-surp-krikor-test.osm.pbf`
- `.gitignore` kapsamındadır ve repoya dahil edilmemiştir.

Seçilen gerçek landmark’lar:

- Kılıç Ali Paşa Camii
  - OSM way: `165574748`
  - Wikidata: `Q862848`
- Surp Krikor Lusavoriç Ermeni Kilisesi
  - OSM way: `165575977`
  - Wikidata: `Q20472836`

İlk üretim sonucunda:

- Kılıç Ali Paşa Camii yalnız `footprint_fallback` gövdesi aldı.
- Mesh kapalı ve manifold idi fakat cami olarak görsel okunabilirliği
  yetersizdi.
- Surp Krikor kilisesi nef, transept, apsis, çatı ve tek batı kulesiyle
  okunabilir üretildi.

## Master Landmark Catalog genişletmesi

Kılıç Ali Paşa Camii Master Landmark Catalog’a eklendi:

- key:
  - `kilic-ali-pasha-mosque`
- family:
  - `mosque`
- Wikidata:
  - `Q862848`
- OSM:
  - `165574748`
- grammar:
  - `single_dome_single_minaret`

Commit:

- `aef280d Catalog Kılıç Ali Paşa Mosque grammar`

## Görsel doğrulama

Katalog bağlantısından sonra production foundation hattı yeniden
çalıştırıldı.

Kılıç Ali Paşa Camii:

- ana kubbe üretildi
- kasnak üretildi
- tek minare üretildi
- şerefe üretildi
- minare külahı üretildi
- yapı artık cami olarak görsel biçimde okunabiliyor

Surp Krikor Kilisesi:

- mevcut kilise geometrisi korundu
- kule, nef ve çatı sistemi bozulmadı

Birleşik yerel preview:

- `OUTPUT/STL/karakoy_kilic_ali_pasa_surp_krikor_catalog_preview_1_3000.stl`

Bu STL `.gitignore` kapsamındaki yerel görsel doğrulama çıktısıdır ve
repoya dahil edilmemiştir.

## Teknik sınır

Kılıç Ali Paşa çıktısı grammar doğrulaması açısından başarılıdır fakat
tarihî rekonstrüksiyon değildir.

Mevcut sınırlamalar:

- minare oranı kısa ve gövdeye yakındır
- ana kubbe oranları geneldir
- alt yapı gerçek footprint tabanlı ağır bir kütle olarak kalır
- landmark’a özgü tarihî oranlar modellenmemiştir

Bu sınırlamalar için landmark’a özel mesher yazılmayacaktır.
İleri iyileştirmeler genel Semantic Architecture, facade/detail ve LoD
sistemleri üzerinden yapılmalıdır.

## Sonuç

Bu paket tamamlandı:

- gerçek PBF landmark tespiti
- catalog grammar routing
- cami kubbe/minare üretimi
- kilise regresyon güvenliği
- manifold üretim
- görsel doğrulama
- commit ve push

Sıradaki geliştirme yeni bir Karaköy özel durumu değil, mevcut roadmap
ve ürün önceliklerine göre seçilmelidir.

## 6 Ağustos 2026 — Resmî LoD Sistemi V1

Resmî Level of Detail sistemi test-first geliştirilmiş ve gerçek landmark
verisiyle doğrulanmıştır.

LoD seviyeleri:

- LoD 0: footprint ve temel kütle
- LoD 1: ana gövde ve temel çatı
- LoD 2: kule, kubbe, apsis ve ana mimari bileşenler
- LoD 3: cephe açıklıkları ve yapısal detaylar
- LoD 4: ornament ve architectural relief

Tamamlanan paketler:

- resmî LoD seviye kataloğu
- ürün ve baskı girdilerine dayalı deterministik LoD resolver
- semantic architecture component görünürlük politikası
- semantic component → mesh group eşleme sözleşmesi
- opt-in ve non-mutating LoD mesh filtresi
- church synthetic fixture doğrulaması
- mosque synthetic fixture doğrulaması
- mevcut production davranışının korunması
- gerçek Bonner Münster LoD doğrulaması

LoD resolver şu girdileri sözleşmeye bağlar:

- ürün ölçüsü
- ölçek oranı
- nozzle çapı
- katman yüksekliği
- minimum duvar kalınlığı
- landmark önemi
- bakış mesafesi
- kullanılabilir renk sayısı

Önemli üretim sınırı:

- LoD filtresi otomatik uygulanmaz.
- Mevcut üretim yolları değişmeden korunur.
- Filtre yalnız açıkça istendiğinde çalışır.
- Kaynak production mesh mutasyona uğratılmaz.
- Premium Worship Engine V1 davranışı değiştirilmemiştir.

Gerçek landmark doğrulaması:

- fixture: `Data/OSM/bonn-muensterplatz-test.osm.pbf`
- landmark: Bonner Münster
- Wikidata: `Q686664`
- LoD 1: ana gövde ve çatı korunur
- LoD 2: katalogdaki dört kule korunur
- LoD 3: cephe ve kule pencere detayları korunur

Doğrulama sonuçları:

- LoD + Bonn gerçek fixture regresyonu: `158 passed in 1.89s`
- mevcut production-routing regresyonu: `110 passed in 0.47s`
- tam regresyon: `2685 passed in 12.58s`

LoD roadmap durumu:

- 6.1–6.9 tamamlandı
- 6.10 tam regresyon ve dokümantasyon tamamlandı
- Resmî LoD Sistemi V1 kilitlenmeye hazırdır

LoD V1 sonrasında roadmap sırasındaki aktif ana paket:

- Automatic Print Optimization and Reporting


# 7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.1

## Güncel kesin çalışma noktası

Automatic Print Optimization and Reporting ana roadmap paketinin ilk alt paketi
olan **7.1 `AtlasPrintOptimizationReport` contract** test-first tamamlandı.

Başlangıç güvenli checkpoint:

- `51f3fa0 Add August 7 development handoff`
- `HEAD == origin/main == 51f3fa0d807592cc25ac794b84fb4fcb61f9b727`

7.1 başlamadan önce doğrulandı:

- `Test/test_print_optimization_report.py` mevcut değildi.
- `CORE/atlas_print_optimization_report.py` mevcut değildi.
- İlk focused test RED sonucu:
  - `ModuleNotFoundError: No module named 'CORE.atlas_print_optimization_report'`

## Tamamlanan 7.1 contract

Yeni production modülü:

- `CORE/atlas_print_optimization_report.py`

Yeni contract testi:

- `Test/test_print_optimization_report.py`

Genel status / decision değerleri:

- `printable`
- `warning`
- `must_simplify`
- `must_thicken`
- `support_required`

İlk issue code değerleri:

- `detail_below_nozzle`
- `fragile_component`
- `excessive_color_change`
- `excessive_triangle_count`

Immutable veri sözleşmeleri:

- `AtlasPrintOptimizationIssue`
  - `code`
  - `severity`
  - `message`
  - `component`
- `AtlasPrintOptimizationReport`
  - `status`
  - `issues`

Contract davranışları:

- identifier string değerleri trim edilir ve lowercase normalize edilir.
- message trim edilir.
- boş zorunlu string değerleri reddedilir.
- report status yalnız tanımlı decision değerlerinden biri olabilir.
- issue koleksiyonu immutable tuple'a dönüştürülür.
- yanlış issue tipi reddedilir.
- `has_issue(...)` desteklenir.
- `issues_for_component(...)` desteklenir.
- `is_printable` desteklenir.
- `has_warnings` desteklenir.

## 7.1 kapsam sınırı

7.1 yalnız ortak veri modeli ve raporlama sözleşmesidir.

Bu pakette özellikle başlanmamıştır:

- minimum wall / thickness analizi
- overhang / support analizi
- fragile connection analizi
- nozzle-based detail analizi
- color-change analizi
- triangle/file-count analizi
- aggregate optimizer

Bu analizler roadmap 7.2–7.8 içinde ayrı test-first paketlerdir.

## Doğrulama

Focused 7.1 test:

- `15 passed in 0.02s`

Print / quality related regression:

- `81 passed in 0.32s`

Tam regresyon:

- `2700 passed in 12.55s`

Mevcut production davranışında otomatik optimizer entegrasyonu yapılmamıştır.
LoD production routing değiştirilmemiştir.
Landmark-specific hack eklenmemiştir.

## Automatic Print Optimization roadmap durumu

- [x] 7.1 `AtlasPrintOptimizationReport` contract
- [ ] 7.2 Minimum wall/thickness analysis
- [ ] 7.3 Overhang/support analysis
- [ ] 7.4 Fragile connection analysis
- [ ] 7.5 Nozzle-based detail analysis
- [ ] 7.6 Color-change analysis
- [ ] 7.7 Triangle/file-count analysis
- [ ] 7.8 Aggregate optimizer/report builder
- [ ] 7.9 Real production validation
- [ ] 7.10 Full regression + documentation + final lock

## Sıradaki tek teknik işlem

**7.2 Minimum wall/thickness analysis** paketine test-first başlamak.

Önce mevcut mesh / physical-detail altyapısı incelenmeli ve minimum wall/thickness
analizinin genel, landmark-bağımsız contract'ı kırmızı test ile tanımlanmalıdır.

Bu 7 Ağustos 2026 bölümü, daha eski belgelerdeki “sıradaki tek işlem”
kayıtlarına göre güncel teknik önceliği tanımlar.


# 7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.2

## Minimum wall/thickness analysis tamamlandı

7.2 paketi test-first tamamlandı.

Yeni production modülü:

- `CORE/atlas_minimum_thickness_analyzer.py`

Yeni test:

- `Test/test_minimum_thickness_analyzer.py`

Yeni immutable sözleşmeler:

- `AtlasThicknessMeasurement`
  - `component`
  - `thickness_mm`
- `AtlasMinimumThicknessAnalysis`
  - `minimum_thickness_mm`
  - `measurements`
  - `minimum_observed_thickness_mm`
  - `violating_components`
  - `is_safe`

Yeni analyzer:

- `AtlasMinimumThicknessAnalyzer.analyze(...)`

Davranış:

- component adları trim edilir ve lowercase normalize edilir.
- thickness değerleri pozitif ve finite olmak zorundadır.
- minimum thickness eşiği pozitif ve finite olmak zorundadır.
- eşik değerine eşit thickness güvenli kabul edilir.
- eşik altındaki component'ler sıralı biçimde raporlanır.
- aynı component birden fazla ihlal üretse bile `violating_components` içinde tek kez yer alır.
- measurement koleksiyonu immutable tuple olarak korunur.
- input koleksiyonu mutate edilmez.

## Mimari sınır

7.2 yalnız ölçülmüş fiziksel thickness değerlerinin genel,
landmark-bağımsız değerlendirilmesini sağlar.

Bu pakette yapılmamıştır:

- triangle mesh üzerinden otomatik thickness reconstruction
- landmark-specific thickness kuralları
- 7.1 `AtlasPrintOptimizationReport` aggregation
- otomatik production optimizer entegrasyonu
- overhang/support analizi

Bu ayrım mevcut `AtlasPhysicalDetailResolver` davranışını korur:
resolver üretim öncesi detay boyutlandırması yaparken,
7.2 üretilmiş/ölçülmüş fiziksel thickness değerlerini değerlendirir.

## Doğrulama

Focused:

- `20 passed in 0.02s`

İlgili physical-detail / quality / mesh regression:

- `51 passed in 0.09s`

Tam regresyon:

- `2720 passed in 12.31s`

## Automatic Print Optimization roadmap durumu

- [x] 7.1 `AtlasPrintOptimizationReport` contract
- [x] 7.2 Minimum wall/thickness analysis
- [ ] 7.3 Overhang/support analysis
- [ ] 7.4 Fragile connection analysis
- [ ] 7.5 Nozzle-based detail analysis
- [ ] 7.6 Color-change analysis
- [ ] 7.7 Triangle/file-count analysis
- [ ] 7.8 Aggregate optimizer/report builder
- [ ] 7.9 Real production validation
- [ ] 7.10 Full regression + documentation + final lock

## Sıradaki tek teknik işlem

**7.3 Overhang/support analysis** paketine test-first başlamak.

Bu bölüm, daha eski "sıradaki tek işlem" kayıtlarına göre güncel teknik
önceliği tanımlar.


# 7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.3

## Overhang/support analysis tamamlandı

7.3 paketi test-first tamamlandı.

Yeni production modülü:

- `CORE/atlas_overhang_support_analyzer.py`

Yeni test:

- `Test/test_overhang_support_analyzer.py`

Yeni immutable sözleşmeler:

- `AtlasOverhangMeasurement`
  - `component`
  - `overhang_degrees`
- `AtlasOverhangSupportAnalysis`
  - `support_threshold_degrees`
  - `measurements`
  - `maximum_overhang_degrees`
  - `support_required_components`
  - `support_required`

Yeni analyzer:

- `AtlasOverhangSupportAnalyzer.analyze(...)`

Açı semantiği:

- `0°`: dikey / support-free referans
- `90°`: yatay çıkıntı
- threshold altı: support-free
- threshold'a eşit veya üzeri: support required

Davranış:

- component adları trim edilir ve lowercase normalize edilir.
- overhang ölçümleri finite ve `0..90°` aralığında olmak zorundadır.
- support threshold finite, `> 0°` ve `<= 90°` olmak zorundadır.
- maksimum overhang değeri raporlanır.
- support gerektiren component'ler giriş sırasıyla raporlanır.
- aynı component birden fazla ihlal üretse bile yalnız bir kez listelenir.
- measurement koleksiyonu immutable tuple olarak korunur.
- input koleksiyonu mutate edilmez.

## Mimari sınır

7.3 genel ve landmark-bağımsız overhang/support değerlendirme sözleşmesidir.

Bu pakette yapılmamıştır:

- triangle normal'larından otomatik overhang ölçümü
- slicer-specific support üretimi
- landmark-specific support kuralları
- 7.1 `AtlasPrintOptimizationReport` aggregation
- relief slope sisteminin değiştirilmesi

Mevcut `AtlasReliefQualityReport` kendi relief yüzey eğimi/risk semantiğiyle
korunmuştur. Genel FDM overhang/support kararı ayrı analyzer olarak tutulur.

## Doğrulama

Focused:

- `22 passed in 0.02s`

İlgili overhang / relief / print regression:

- `77 passed in 0.12s`

Tam regresyon:

- `2742 passed in 12.31s`

## Automatic Print Optimization roadmap durumu

- [x] 7.1 `AtlasPrintOptimizationReport` contract
- [x] 7.2 Minimum wall/thickness analysis
- [x] 7.3 Overhang/support analysis
- [ ] 7.4 Fragile connection analysis
- [ ] 7.5 Nozzle-based detail analysis
- [ ] 7.6 Color-change analysis
- [ ] 7.7 Triangle/file-count analysis
- [ ] 7.8 Aggregate optimizer/report builder
- [ ] 7.9 Real production validation
- [ ] 7.10 Full regression + documentation + final lock

## Sıradaki tek teknik işlem

**7.4 Fragile connection analysis** paketine test-first başlamak.

Bu bölüm, daha eski "sıradaki tek işlem" kayıtlarına göre güncel teknik
önceliği tanımlar.


# 7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.4

## Fragile connection analysis tamamlandı

7.4 paketi test-first tamamlandı.

Yeni production modülü:

- `CORE/atlas_fragile_connection_analyzer.py`

Yeni test:

- `Test/test_fragile_connection_analyzer.py`

Yeni immutable sözleşmeler:

- `AtlasConnectionMeasurement`
  - `component`
  - `connection_width_mm`
  - `component_span_mm`
  - türetilmiş `connection_ratio`
- `AtlasFragileConnectionAnalysis`
  - `minimum_connection_ratio`
  - `measurements`
  - `minimum_observed_ratio`
  - `fragile_components`
  - `has_fragile_connections`

Yeni analyzer:

- `AtlasFragileConnectionAnalyzer.analyze(...)`

## Fragility semantiği

7.4 mutlak duvar/kalınlık kontrolünü tekrar etmez.

Bağlantı kırılganlığı şu oran üzerinden değerlendirilir:

- `connection_ratio = connection_width_mm / component_span_mm`

Karar:

- oran minimum threshold'un altındaysa: fragile
- threshold'a eşit veya üzerindeyse: safe

Bu nedenle 7.2 ile görev ayrımı şöyledir:

- 7.2: mutlak fiziksel thickness
- 7.4: bağlı bileşenin kendi açıklığına göre bağlantı/boğaz oranı

## Contract davranışı

- component adları trim edilir ve lowercase normalize edilir.
- bağlantı genişliği ve component açıklığı finite ve pozitif olmak zorundadır.
- `connection_width_mm > component_span_mm` geçersizdir.
- `connection_ratio` constructor girdisi değildir; immutable türetilmiş alandır.
- minimum connection ratio finite, `> 0` ve `<= 1` olmak zorundadır.
- minimum gözlenen oran raporlanır.
- fragile component'ler giriş sırasıyla korunur.
- duplicate component yalnız bir kez raporlanır.
- measurement koleksiyonu immutable tuple olarak korunur.
- input koleksiyonu mutate edilmez.

## Mimari sınır

Bu pakette yapılmamıştır:

- finite-element / structural load analysis
- otomatik mesh bağlantı kesiti çıkarımı
- landmark-specific kırılganlık kuralları
- mevcut minare/kule printable minimumlarının değiştirilmesi
- 7.1 `AtlasPrintOptimizationReport` aggregation
- otomatik geometry thickening veya redesign

Mevcut mesher printable-minimum davranışları korunmuştur.

## Doğrulama

İlk focused GREEN:

- `27 passed in 0.02s`

Derived-field contract düzeltmesi sonrası focused:

- `28 passed in 0.03s`

İlgili fragile / thickness / physical-detail / mosque regression:

- `86 passed in 0.22s`

Tam regresyon:

- `2770 passed in 12.33s`

## Automatic Print Optimization roadmap durumu

- [x] 7.1 `AtlasPrintOptimizationReport` contract
- [x] 7.2 Minimum wall/thickness analysis
- [x] 7.3 Overhang/support analysis
- [x] 7.4 Fragile connection analysis
- [ ] 7.5 Nozzle-based detail analysis
- [ ] 7.6 Color-change analysis
- [ ] 7.7 Triangle/file-count analysis
- [ ] 7.8 Aggregate optimizer/report builder
- [ ] 7.9 Real production validation
- [ ] 7.10 Full regression + documentation + final lock

## Sıradaki tek teknik işlem

**7.5 Nozzle-based detail analysis** paketine test-first başlamak.

Bu bölüm, daha eski "sıradaki tek işlem" kayıtlarına göre güncel teknik
önceliği tanımlar.


# 7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.5

## Nozzle-based detail analysis tamamlandı

7.5 paketi test-first tamamlandı.

Yeni production modülü:

- `CORE/atlas_nozzle_detail_analyzer.py`

Yeni test:

- `Test/test_nozzle_detail_analyzer.py`

Yeni immutable sözleşmeler:

- `AtlasNozzleDetailMeasurement`
  - `component`
  - `detail_size_mm`
  - `nozzle_diameter_mm`
  - türetilmiş `nozzle_ratio`
- `AtlasNozzleDetailAnalysis`
  - `nozzle_diameter_mm`
  - `measurements`
  - `minimum_observed_detail_mm`
  - `below_nozzle_components`
  - `has_below_nozzle_details`

Yeni analyzer:

- `AtlasNozzleDetailAnalyzer.analyze(...)`

## Nozzle/detail semantiği

7.5 üretim öncesi detail-resolution kararını tekrar etmez.

Mevcut `AtlasPhysicalDetailResolver`:

- gerçek ölçü
- model scale
- nozzle diameter

üzerinden `preserve / enlarge / omit` kararı vermeye devam eder.

7.5 ise üretilmiş veya çözülmüş fiziksel detail ölçülerini audit eder.

Temel ölçüt:

- `nozzle_ratio = detail_size_mm / nozzle_diameter_mm`

Karar:

- `detail_size_mm < nozzle_diameter_mm`: below nozzle
- `detail_size_mm >= nozzle_diameter_mm`: safe

## Contract davranışı

- component adları trim edilir ve lowercase normalize edilir.
- detail ölçüsü finite ve pozitif olmak zorundadır.
- nozzle çapı finite ve pozitif olmak zorundadır.
- `nozzle_ratio` constructor girdisi değildir; immutable türetilmiş alandır.
- analyzer içindeki bütün measurement'ların nozzle çapı analysis nozzle çapıyla eşleşmek zorundadır.
- minimum gözlenen detail ölçüsü raporlanır.
- nozzle altındaki component'ler giriş sırasıyla korunur.
- duplicate component yalnız bir kez raporlanır.
- measurement koleksiyonu immutable tuple olarak korunur.
- input koleksiyonu mutate edilmez.

## Mimari sınır

Bu pakette yapılmamıştır:

- detail resize
- detail enlarge
- detail omit
- geometry mutation
- `AtlasPhysicalDetailResolver` değişikliği
- LoD policy değişikliği
- landmark-specific nozzle kuralı
- 7.1 `AtlasPrintOptimizationReport` aggregation

`DETAIL_BELOW_NOZZLE` issue code'u 7.1 contract'ında mevcut kalır;
7.5 sonucunun aggregate report'a bağlanması 7.8 kapsamındadır.

## Doğrulama

Focused:

- `25 passed in 0.02s`

İlgili nozzle / physical-detail / LoD / print regression:

- `103 passed in 0.15s`

Tam regresyon:

- `2795 passed in 12.37s`

## Automatic Print Optimization roadmap durumu

- [x] 7.1 `AtlasPrintOptimizationReport` contract
- [x] 7.2 Minimum wall/thickness analysis
- [x] 7.3 Overhang/support analysis
- [x] 7.4 Fragile connection analysis
- [x] 7.5 Nozzle-based detail analysis
- [ ] 7.6 Color-change analysis
- [ ] 7.7 Triangle/file-count analysis
- [ ] 7.8 Aggregate optimizer/report builder
- [ ] 7.9 Real production validation
- [ ] 7.10 Full regression + documentation + final lock

## Sıradaki tek teknik işlem

**7.6 Color-change analysis** paketine test-first başlamak.

Bu bölüm, daha eski "sıradaki tek işlem" kayıtlarına göre güncel teknik
önceliği tanımlar.


# 7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.6

## Color-change analysis tamamlandı

7.6 paketi test-first tamamlandı.

Yeni production modülü:

- `CORE/atlas_color_change_analyzer.py`

Yeni test:

- `Test/test_color_change_analyzer.py`

Yeni immutable sözleşme:

- `AtlasColorChangeAnalysis`
  - `color_change_count`
  - `maximum_color_changes`
  - `excess_color_changes`
  - `is_excessive`

Yeni analyzer:

- `AtlasColorChangeAnalyzer.analyze(...)`

## Color-change semantiği

7.6 renk sayısı ile gerçek filament/color change sayısını birbirinden ayırır.

Mevcut multicolor exporter:

- `color_count`
- `part_count`

bilgisini üretmeye devam eder.

Bunlar gerçek slicer color-change sayısı değildir.

7.6 yalnız ölçülmüş veya slicer tarafından raporlanmış gerçek
`color_change_count` değerini audit eder.

Karar:

- `color_change_count <= maximum_color_changes`: safe
- `color_change_count > maximum_color_changes`: excessive

Türetilmiş sonuç:

- `excess_color_changes = max(0, color_change_count - maximum_color_changes)`

## Contract davranışı

- `color_change_count` non-negative integer olmak zorundadır.
- `maximum_color_changes` non-negative integer olmak zorundadır.
- `bool`, float ve string sayaç olarak kabul edilmez.
- `0` color change geçerlidir.
- `0` maximum threshold geçerlidir.
- threshold'a eşit change count safe kabul edilir.
- analysis immutable'dır.

## Mimari sınır

Bu pakette yapılmamıştır:

- color count üzerinden change-count tahmini
- `color_count - 1` türetimi
- slicer çağrısı
- Bambu Studio entegrasyonu
- multicolor exporter değişikliği
- LoD policy değişikliği
- filament assignment değişikliği
- 7.1 `AtlasPrintOptimizationReport` aggregation

`EXCESSIVE_COLOR_CHANGE` issue code'u 7.1 contract'ında mevcut kalır;
7.6 sonucunun aggregate report'a bağlanması 7.8 kapsamındadır.

## Doğrulama

Focused:

- `20 passed in 0.02s`

İlgili color / multicolor / LoD / print regression:

- `91 passed in 0.11s`

Tam regresyon:

- `2815 passed in 12.52s`

## Automatic Print Optimization roadmap durumu

- [x] 7.1 `AtlasPrintOptimizationReport` contract
- [x] 7.2 Minimum wall/thickness analysis
- [x] 7.3 Overhang/support analysis
- [x] 7.4 Fragile connection analysis
- [x] 7.5 Nozzle-based detail analysis
- [x] 7.6 Color-change analysis
- [ ] 7.7 Triangle/file-count analysis
- [ ] 7.8 Aggregate optimizer/report builder
- [ ] 7.9 Real production validation
- [ ] 7.10 Full regression + documentation + final lock

## Sıradaki tek teknik işlem

**7.7 Triangle/file-count analysis** paketine test-first başlamak.

Bu bölüm, daha eski "sıradaki tek işlem" kayıtlarına göre güncel teknik
önceliği tanımlar.


# 7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.7

## Triangle/file-count analysis tamamlandı

7.7 paketi test-first tamamlandı.

Yeni production modülü:

- `CORE/atlas_triangle_file_count_analyzer.py`

Yeni test:

- `Test/test_triangle_file_count_analyzer.py`

Yeni immutable sözleşme:

- `AtlasTriangleFileCountAnalysis`
  - `triangle_count`
  - `maximum_triangle_count`
  - `file_count`
  - `maximum_file_count`
  - `excess_triangle_count`
  - `excess_file_count`
  - `is_triangle_count_excessive`
  - `is_file_count_excessive`
  - `has_excessive_counts`

Yeni analyzer:

- `AtlasTriangleFileCountAnalyzer.analyze(...)`

## Analiz semantiği

Triangle count ve file count birbirinden bağımsız iki üretim karmaşıklığı sinyali olarak ele alınır.

Kararlar:

- `triangle_count <= maximum_triangle_count`: safe
- `triangle_count > maximum_triangle_count`: excessive
- `file_count <= maximum_file_count`: safe
- `file_count > maximum_file_count`: excessive

Türetilmiş sonuçlar:

- `excess_triangle_count = max(0, triangle_count - maximum_triangle_count)`
- `excess_file_count = max(0, file_count - maximum_file_count)`

## Contract davranışı

- Tüm count ve threshold alanları non-negative integer olmak zorundadır.
- `bool`, float ve string sayaç olarak kabul edilmez.
- `0` değerleri geçerlidir.
- threshold'a eşit değerler safe kabul edilir.
- analysis immutable'dır.

## Mevcut sistemle sınır

Repo içinde triangle count zaten farklı üretim noktalarında ölçülmektedir.

Mevcut multicolor exporter:

- `part_count`
- `color_count`
- renk bazlı STL parçaları

bilgisini üretmeye devam eder.

7.7 bunları yeniden üretmez veya exporter'a bağlanmaz.

Bu pakette yapılmamıştır:

- STL writer değişikliği
- multicolor exporter değişikliği
- LoD policy değişikliği
- mesh simplification
- otomatik dosya birleştirme
- otomatik triangle reduction
- yeni report issue aggregation

`EXCESSIVE_TRIANGLE_COUNT` issue code'u 7.1 contract'ında mevcut kalır.
7.7 analiz sonucunun `AtlasPrintOptimizationReport` içine bağlanması 7.8 kapsamındadır.

File-count için 7.7 aşamasında yeni issue code eklenmemiştir;
aggregate karar 7.8'de genel report builder tasarımıyla birlikte verilecektir.

## Doğrulama

Focused:

- `31 passed in 0.02s`

İlgili STL / exporter / LoD / print regression:

- `88 passed in 0.20s`

Tam regresyon:

- `2846 passed in 12.33s`

## Automatic Print Optimization roadmap durumu

- [x] 7.1 `AtlasPrintOptimizationReport` contract
- [x] 7.2 Minimum wall/thickness analysis
- [x] 7.3 Overhang/support analysis
- [x] 7.4 Fragile connection analysis
- [x] 7.5 Nozzle-based detail analysis
- [x] 7.6 Color-change analysis
- [x] 7.7 Triangle/file-count analysis
- [ ] 7.8 Aggregate optimizer/report builder
- [ ] 7.9 Real production validation
- [ ] 7.10 Full regression + documentation + final lock

## Sıradaki tek teknik işlem

**7.8 Aggregate optimizer/report builder** paketine test-first başlamak.

Bu bölüm, daha eski "sıradaki tek işlem" kayıtlarına göre güncel teknik
önceliği tanımlar.


# 7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.8

## Aggregate optimizer/report builder tamamlandı

7.8 paketi test-first tamamlandı.

Yeni production modülü:

- `CORE/atlas_print_optimization_report_builder.py`

Yeni test:

- `Test/test_print_optimization_report_builder.py`

Güncellenen report contract:

- `CORE/atlas_print_optimization_report.py`

Eklenen issue code'ları:

- `THICKNESS_BELOW_MINIMUM = "thickness_below_minimum"`
- `SUPPORT_REQUIRED_ISSUE = "support_required"`
- `EXCESSIVE_FILE_COUNT = "excessive_file_count"`

## Aggregate builder kapsamı

`AtlasPrintOptimizationReportBuilder.build(...)` şu analiz sonuçlarını
tek `AtlasPrintOptimizationReport` içinde birleştirir:

- `AtlasMinimumThicknessAnalysis`
- `AtlasOverhangSupportAnalysis`
- `AtlasFragileConnectionAnalysis`
- `AtlasNozzleDetailAnalysis`
- `AtlasColorChangeAnalysis`
- `AtlasTriangleFileCountAnalysis`

Builder yalnız mevcut analiz sonuçlarını report issue'larına çevirir.

## Status önceliği

Final status precedence kilitlendi:

1. `MUST_THICKEN`
2. `SUPPORT_REQUIRED`
3. `MUST_SIMPLIFY`
4. `WARNING`
5. `PRINTABLE`

Bu sayede birden fazla bulgu birlikte bulunduğunda daha yüksek üretim riski
final status'u belirler.

## Issue mapping

- minimum thickness violation
  - code: `THICKNESS_BELOW_MINIMUM`
  - severity: `MUST_THICKEN`

- fragile connection
  - code: `FRAGILE_COMPONENT`
  - severity: `MUST_THICKEN`

- support-required overhang
  - code: `SUPPORT_REQUIRED_ISSUE`
  - severity: `SUPPORT_REQUIRED`

- detail below nozzle
  - code: `DETAIL_BELOW_NOZZLE`
  - severity: `WARNING`

- excessive color changes
  - code: `EXCESSIVE_COLOR_CHANGE`
  - severity: `WARNING`

- excessive triangle count
  - code: `EXCESSIVE_TRIANGLE_COUNT`
  - severity: `MUST_SIMPLIFY`

- excessive file count
  - code: `EXCESSIVE_FILE_COUNT`
  - severity: `WARNING`

## Deterministik issue sırası

Builder issue'ları şu sırayla üretir:

1. thickness
2. support
3. fragile connection
4. nozzle detail
5. color change
6. triangle count
7. file count

Bu sıra test ile kilitlenmiştir.

## Mimari sınır

7.8 bir mutation/optimization engine değildir.

Bu pakette yapılmamıştır:

- mesh thickening
- mesh simplification
- automatic support generation
- automatic file merging
- automatic color reduction
- slicer çağrısı
- Bambu Studio entegrasyonu
- LoD policy değişikliği
- landmark-specific rule
- exporter behavior değişikliği

7.8'in görevi yalnız 7.1–7.7 analizlerini tek genel production report içinde
toplamaktır.

## Doğrulama

Focused builder:

- `19 passed in 0.03s`

7.1–7.8 odaklı regression:

- `180 passed in 0.13s`

Geniş print / exporter / LoD regression:

- `239 passed in 0.31s`

Tam regresyon:

- `2865 passed in 12.31s`

## Automatic Print Optimization roadmap durumu

- [x] 7.1 `AtlasPrintOptimizationReport` contract
- [x] 7.2 Minimum wall/thickness analysis
- [x] 7.3 Overhang/support analysis
- [x] 7.4 Fragile connection analysis
- [x] 7.5 Nozzle-based detail analysis
- [x] 7.6 Color-change analysis
- [x] 7.7 Triangle/file-count analysis
- [x] 7.8 Aggregate optimizer/report builder
- [ ] 7.9 Real production validation
- [ ] 7.10 Full regression + documentation + final lock

## Sıradaki tek teknik işlem

**7.9 Real production validation** paketine kontrollü biçimde başlamak.

Önce mevcut gerçek ürün üretim çıktılarından hangi ölçümlerin güvenilir biçimde
elde edilebildiği okunmalı; yeni production entegrasyonu varsayılmamalıdır.

Bu bölüm, daha eski "sıradaki tek işlem" kayıtlarına göre güncel teknik
önceliği tanımlar.


# 7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.9

## Real production validation tamamlandı

7.9 paketi gerçek Köln production artifact'ı üzerinden doğrulandı.

Yeni genel validator:

- `CORE/atlas_bambu_3mf_production_validator.py`

Yeni test:

- `Test/test_bambu_3mf_production_validator.py`

## Genel Bambu 3MF validation contract

`AtlasBambu3MFProductionValidator.validate(...)` Bambu Studio `.3mf`
artifact'ını read-only olarak doğrular.

Okunan metadata kaynakları:

- `Metadata/model_settings.config`
- `Metadata/project_settings.config`
- `Metadata/plate_1.json`

Validator şu production bilgilerini raporlar:

- object face count
- toplam part face count
- part count
- object/part face-count eşleşmesi
- Bambu mesh repair sayaçları
- printer model
- nozzle diameter
- layer height
- support enabled/disabled
- bed type
- structural validity

## Structural validity kuralı

`is_structurally_valid` yalnız şu iki koşul birlikte sağlanırsa `True` olur:

1. object face count == toplam part face count
2. Bambu mesh repair toplamı == 0

Validator geometriyi değiştirmez ve Bambu Studio'yu çalıştırmaz.

## Gerçek Köln production artifact doğrulaması

Doğrulanan artifact:

- `OUTPUT/3MF/koeln_paedagogische_fakultaet_150mm_FINAL.3mf`

Artifact Git tarafından tracked değildir ve 7.9 test fixture'ı olarak repoya
eklenmemiştir.

Gerçek Köln sonucu:

- object face count: `64776`
- part face count: `64776`
- part count: `4`
- face counts match: `True`
- mesh repair count: `0`
- has mesh repairs: `False`
- printer model: `Bambu Lab P2S`
- nozzle diameter: yaklaşık `0.4 mm`
- layer height: `0.2 mm`
- support enabled: `False`
- bed type: `textured_plate`
- structurally valid: `True`

Kaynak dört multicolor STL triangle sayıları da bire bir doğrulandı:

- black: `2904`
- green: `32588`
- red: `9188`
- white: `20096`
- toplam: `64776`

Bu toplam `.3mf` içindeki object face count ile tam eşleşmektedir.

## Bilinçli kapsam dışı production metrikleri

Mevcut Köln `.3mf` metadata'sında güvenilir biçimde bulunmayan değerler
validator tarafından tahmin edilmez:

- toplam color-change count
- toplam print time
- toplam filament gramı

`filament_sequence.json` mevcut artifact'ta gerçek toplam filament-change
ölçümü sağlamamaktadır.

Bu nedenle 7.6'daki `AtlasColorChangeAnalyzer` gerçek slicer ölçümü
gerektirmeye devam eder; multicolor `part_count` veya `color_count`
color-change sayısı yerine kullanılmaz.

## Mimari sınır

7.9 kapsamında yapılmamıştır:

- Bambu Studio otomasyonu
- slicer çağrısı
- `.3mf` mutation
- G-code üretimi veya parsing
- filament tüketimi tahmini
- print time tahmini
- color-change tahmini
- mesh repair
- LoD değişikliği
- exporter değişikliği
- landmark-specific validation

## Doğrulama

Focused validator:

- `8 passed in 0.04s`

İlgili production / print regression:

- `192 passed in 0.18s`

Tam regresyon:

- `2873 passed in 12.34s`

## Automatic Print Optimization roadmap durumu

- [x] 7.1 `AtlasPrintOptimizationReport` contract
- [x] 7.2 Minimum wall/thickness analysis
- [x] 7.3 Overhang/support analysis
- [x] 7.4 Fragile connection analysis
- [x] 7.5 Nozzle-based detail analysis
- [x] 7.6 Color-change analysis
- [x] 7.7 Triangle/file-count analysis
- [x] 7.8 Aggregate optimizer/report builder
- [x] 7.9 Real production validation
- [ ] 7.10 Full regression + documentation + final lock

## Sıradaki tek teknik işlem

**7.10 Full regression + documentation + final lock**

Bu aşamada yeni analyzer veya production davranışı eklenmemeli; mevcut
7.1–7.9 paketinin final kapsamı ve güvenli checkpoint'i kilitlenmelidir.

Bu bölüm, daha eski "sıradaki tek işlem" kayıtlarına göre güncel teknik
önceliği tanımlar.


# 7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.10 FINAL LOCK

## Roadmap paketi tamamlandı

Automatic Print Optimization and Reporting 7.1–7.10 paketi tamamlandı ve
final lock aşamasına ulaştı.

Bu milestone yeni production davranışı eklemez. 7.1–7.9 boyunca geliştirilen
sözleşmeler, analizler, aggregate report builder ve gerçek Bambu 3MF
validation zincirinin final regression ve dokümantasyon kilididir.

## Kilitlenen production-analysis zinciri

Final genel zincir:

1. `AtlasPrintOptimizationReport`
2. `AtlasMinimumThicknessAnalyzer`
3. `AtlasOverhangSupportAnalyzer`
4. `AtlasFragileConnectionAnalyzer`
5. `AtlasNozzleDetailAnalyzer`
6. `AtlasColorChangeAnalyzer`
7. `AtlasTriangleFileCountAnalyzer`
8. `AtlasPrintOptimizationReportBuilder`
9. `AtlasBambu3MFProductionValidator`

## Kilitlenen analiz kapsamı

### Minimum thickness

- absolute physical thickness measurement
- threshold altı violation
- equality safe
- component-level result

### Overhang / support

- 0° vertical / print-safe
- 90° horizontal overhang
- configured threshold ve üzeri support-required

### Fragile connection

- connection neck ratio:
  `connection_width_mm / component_span_mm`
- threshold altı fragile
- equality safe

### Nozzle detail

- resolved physical detail size nozzle çapına karşı audit edilir
- nozzle çapından küçük detail warning üretir
- equality safe
- geometri otomatik değiştirilmez

### Color changes

- yalnız gerçek slicer/production `color_change_count` kabul edilir
- multicolor `part_count` veya `color_count` color-change sayısı değildir
- tahmin yapılmaz

### Triangle / file count

- triangle count ve file count bağımsız sinyallerdir
- configured threshold üstü excess olarak raporlanır

## Aggregate report builder final contract

`AtlasPrintOptimizationReportBuilder` 7.2–7.7 analiz sonuçlarını tek
`AtlasPrintOptimizationReport` içinde toplar.

Final status precedence:

1. `MUST_THICKEN`
2. `SUPPORT_REQUIRED`
3. `MUST_SIMPLIFY`
4. `WARNING`
5. `PRINTABLE`

Deterministik issue sırası:

1. thickness
2. support
3. fragile connection
4. nozzle detail
5. color change
6. triangle count
7. file count

Job-level color/triangle/file bulguları `component="print_job"` kullanır.

## Gerçek production validation final contract

`AtlasBambu3MFProductionValidator` Bambu Studio `.3mf` artifact'ını read-only
olarak doğrular.

Okunan metadata:

- `Metadata/model_settings.config`
- `Metadata/project_settings.config`
- `Metadata/plate_1.json`

Structural validity:

- object face count == toplam part face count
- toplam Bambu mesh repair count == 0

Validator ayrıca şu metadata'yı raporlar:

- part count
- printer model
- nozzle diameter
- layer height
- support enabled/disabled
- bed type

## Gerçek Köln production kanıtı

Doğrulanan gerçek artifact:

- `OUTPUT/3MF/koeln_paedagogische_fakultaet_150mm_FINAL.3mf`

Final doğrulama sonucu:

- object face count: `64776`
- part face count: `64776`
- part count: `4`
- face counts match: `True`
- mesh repair count: `0`
- printer model: `Bambu Lab P2S`
- nozzle diameter: yaklaşık `0.4 mm`
- layer height: `0.2 mm`
- support enabled: `False`
- bed type: `textured_plate`
- structurally valid: `True`

Kaynak multicolor STL triangle toplamı da `64776` olup `.3mf` object face count
ile bire bir eşleşmiştir.

Gerçek `.3mf` Git tarafından tracked değildir ve test fixture olarak repoya
eklenmemiştir.

## Bilinçli final kapsam dışı alanlar

Bu roadmap paketi aşağıdakileri otomatikleştirmez:

- mesh thickening
- mesh simplification
- automatic support generation
- automatic file merging
- automatic color reduction
- automatic LoD selection
- Bambu Studio automation
- slicer invocation
- G-code generation/parsing
- filament consumption estimation
- print-time estimation
- color-change estimation
- mesh repair
- landmark-specific print rules

Mevcut `.3mf` içinde güvenilir olmayan print time, filament gramı ve gerçek
color-change count değerleri tahmin edilmez.

## Final doğrulama

7.1–7.9 final package regression:

- `188 passed in 0.15s`

Final full regression:

- `2873 passed in 12.30s`

## Automatic Print Optimization roadmap FINAL

- [x] 7.1 `AtlasPrintOptimizationReport` contract
- [x] 7.2 Minimum wall/thickness analysis
- [x] 7.3 Overhang/support analysis
- [x] 7.4 Fragile connection analysis
- [x] 7.5 Nozzle-based detail analysis
- [x] 7.6 Color-change analysis
- [x] 7.7 Triangle/file-count analysis
- [x] 7.8 Aggregate optimizer/report builder
- [x] 7.9 Real production validation
- [x] 7.10 Full regression + documentation + final lock

## Final lock kararı

**Automatic Print Optimization and Reporting V1 kilitlendi.**

Bu noktadan sonra bu roadmap paketinde yeni davranış eklenmemelidir.
Gelecekte değişiklik gerekirse ayrı, gerekçelendirilmiş ve test-first bir
roadmap paketi olarak açılmalıdır.

Bu bölüm, 7.1–7.9 içindeki tarihsel ara roadmap kayıtlarına göre güncel ve
nihai durumu tanımlar.

## 7 Ağustos 2026 — Urban Fabric & Product Composition V1 ACTIVE

Automatic Print Optimization and Reporting V1 final kilidinden sonra yeni aktif
roadmap paketi:

`Docs/Roadmap/URBAN_FABRIC_PRODUCT_COMPOSITION_V1.md`

Baseline güvenli commit:

`50daf58a00e31dd99f403af5eb8a6ac2edef3bba`

Yeni paket amacı:

- ATLAS landmark ve architectural-semantic üstünlüğünü korumak
- generic şehir dokusunu ürün ölçeğinde daha bütünlüklü hale getirmek
- road hierarchy, urban blocks, parks, vegetation, rail, water ve terrain
  bileşenlerini ortak ürün kompozisyonuna bağlamak
- fiziksel okunabilirliği strict map scale'den ayrı ve kontrollü biçimde ele almak
- farklı şehir morfolojilerine göre composition policy geliştirmek

Lichtbild karşılaştırmasından çıkan ana teknik sonuç:

Lichtbild'in görünür güçlü tarafı tekil bina detayından çok coherent urban,
landscape ve infrastructure composition'dır.

ATLAS hedefi:

`Lichtbild-level urban coherence + ATLAS landmark intelligence + ATLAS LoD/print infrastructure`

İlk kontrollü benchmark:

- Bonn
- center: `50.733270, 7.100440`
- Lichtbild product size: `14 × 14 cm`
- displayed coverage: `0.44 km²`
- ATLAS equivalent scale: yaklaşık `1:4738`
- exact benchmark output:
  `OUTPUT/STL/bonn_lichtbild_14cm_exact_0_44km2.stl`
- meshes: `922`
- triangles: `70798`

Aktif roadmap:

- 8.0 Bonn Urban Fabric Ground-Truth Audit
- 8.1 Urban Fabric Scene Contract
- 8.2 Road Hierarchy Engine
- 8.3 Linear Infrastructure Engine
- 8.4 Urban Block Resolver
- 8.5 Park & Plaza Semantic Surface Engine
- 8.6 Vegetation Composition Engine
- 8.7 Avenue Tree Row Engine
- 8.8 Semantic Surface Texture Engine
- 8.9 Morphology-Aware Terrain Product Resolver
- 8.10 Water & Shoreline Composition Engine
- 8.11 Bridge / Infrastructure Urban Integration
- 8.12 Building Height Product Normalizer
- 8.13 Physical Cartographic Exaggeration Resolver
- 8.14 City Composition LoD
- 8.15 Scene Morphology Classifier
- 8.16 Morphology Composition Policy
- 8.17 Semantic Color / Material Hierarchy
- 8.18 Customer Preview Parity
- 8.19 Urban Fabric Quality Report
- 8.20 Multi-Morphology Acceptance Benchmarks

### 8.0 Bonn Urban Fabric Ground-Truth Audit — TAMAMLANDI

8.0 read-only audit olarak tamamlandı. Production davranışı değiştirilmedi.

Kesinleşen ana bulgular:

- Railway source exact bbox içinde mevcut fakat `AtlasLocalOSMReader`
  normal railway collection üretmiyor. Surface-aday tram/platform verisi
  production geometry'ye girmiyor.
- `353` highway-line girdisinin yalnız `62` tanesi road builder tarafından
  kabul ediliyor; `291` pedestrian/path sınıfı mevcut production road
  geometry'sinde temsil edilmiyor.
- Münsterplatz ve benzeri önemli meydanların önemli kısmı line-based
  `highway=pedestrian` source olarak mevcut; source eksikliği değil,
  semantic/product expression eksikliği var.
- Hofgarten source→reader→final park mesh zincirinde mevcut; sorun missing
  source değil, zayıf park semantic composition.
- Vegetation clutter'ın ana nedeni WorldCover tree-cover örneklerinin
  context-free isolated tree objelerine dönüştürülmesi.
- `tree_rows` contract mevcut fakat producer ve production consumer yok.
- Building-part vertical interval bug bulunmadı.
- Generic height parser'da belirgin hata bulunmadı.
- Universitätshauptgebäude yüksekliği source-valid historic/castle semantics
  ile product-scale castle exaggeration birleşiminden geliyor; morphology /
  product composition policy konusu.
- Water `4 → 3` dönüşümü mevcut policy ile deterministik; fakat water source
  identity/name metadata downstream'de korunmuyor.
- Bonn terrain benchmarkı local SRTM eksikliği nedeniyle OpenTopography
  COP30 fallback ile üretildi. Belirgin terrain scaling bug bulunmadı; gerçek
  provider/fallback provenance final result metadata'da taşınmıyor.
- Exact Bonn'da `435` main building polygon var. Proximity sonucu:
  `43` cluster @2 m, `39` @4 m, `24` @6 m, `6` @10 m.
- `1:4738` product scale'de çok sayıda footprint fiziksel olarak küçülüyor:
  `59 <1 mm²`, `201 <4 mm²`, `340 <9 mm²`.
- Mevcut minimum-size filtering zaten bilinçli:
  `48` area minimum, `47` width minimum, `6` depth minimum,
  `1` triangulation failure.
- Dolayısıyla 8.4 yeni kaba size filter veya uncontrolled merge olmamalı;
  block-aware composition / LoD katmanı olmalı.

Ana sonuç:

`Bonn'daki temel boşluk source truth eksikliği değil; mevcut urban öğeleri
ürün ölçeğinde ortak semantic composition altında birleştiren stabil bir
scene contract ve morphology-aware policy eksikliğidir.`

### 8.1 Urban Fabric Scene Contract — TAMAMLANDI

8.1 test-first tamamlandı.

Yeni dosyalar:

- `CORE/atlas_urban_fabric_scene_contract.py`
- `Test/test_urban_fabric_scene_contract.py`

Kilitlenen immutable contract'lar:

- `AtlasUrbanFabricElement`
- `AtlasUrbanFabricRelationship`
- `AtlasUrbanFabricScene`

Contract artık şu bilgileri taşıyor:

- source identity
- semantic class
- product priority
- LoD eligibility
- geometry reference
- element relationships
- typed relationships
- scene-level referential integrity

Minimum Urban Fabric V1 semantic kapsamı:

- road
- railway
- pedestrian_path
- urban_block
- generic_building
- park
- plaza
- vegetation
- water
- infrastructure_corridor
- terrain

Bu liste kapalı enum değildir; semantic class sistemi extensible kalır.

Scene contract davranışları:

- deterministic element lookup
- semantic-class filtering
- duplicate element-ID rejection
- duplicate relationship-ID rejection
- relationship endpoint validation
- related-element referential integrity
- present semantic class reporting
- missing required semantic class reporting

Doğrulama:

- focused: `40 passed`
- related regression: `120 passed in 0.53s`
- full regression: `2913 passed in 12.75s`

8.1 sırasında final production geometry davranışı değiştirilmedi.

### 8.2 Road Hierarchy Engine — TAMAMLANDI

8.2 test-first tamamlandı.

Yeni ana sözleşmeler:

- `AtlasUrbanRoadProfile`
- `AtlasUrbanRoadHierarchyResolver`

Source highway sınıfları product-semantic hierarchy'ye çözülüyor:

- motorway / trunk / primary / secondary / tertiary -> `major_road`
- residential / living_street / unclassified / road -> `local_road`
- service -> `service_road`
- footway / path / pedestrian / steps -> `pedestrian_path`
- cycleway -> `cycleway`
- bridleway -> `bridleway`

`cycleway` ve `bridleway` fiziksel corridor davranışı bilinçli olarak
8.3 Linear Infrastructure Engine'e bırakıldı.

Road profile contract şu alanları taşıyor:

- semantic priority
- physical width
- minimum printable width
- vertical treatment
- LoD eligibility
- simplification priority

Fiziksel genişlik çözümü:

- geçerli OSM `width=*` source truth olarak kullanılır
- vehicle sınıflarında source width yok/geçersizse mevcut ATLAS default
  genişlikleri korunur
- gerçek genişlik product scale'e çevrilir
- açıkça verilen printable minimum uygulanır
- pedestrian path için source width yok/geçersizse gerçek-metre fallback
  uydurulmaz; doğrudan explicit printable minimum kullanılır

Relative hierarchy:

`major_road > local_road > service_road > pedestrian_path`

Bu sıra semantic priority, physical width ve simplification priority
açısından doğrulanabilir.

Production entegrasyonu geriye dönük uyumludur:

- `AtlasRoadFoundationBuilder.build_roads(...)`
  `minimum_printable_width_mm=None` kabul eder
- `None` iken legacy vehicle-road davranışı korunur
- değer verildiğinde semantic hierarchy ve pedestrian yollar etkinleşebilir
- `AtlasFoundationFirstEngine.generate_city_stl(...)`
  `road_minimum_printable_width_mm=None` kabul eder
- mevcut ürünlere gizli minimum genişlik uygulanmaz

Bonn-specific width, koordinat veya landmark hack eklenmedi.

Doğrulama:

- focused + integration: `69 passed`
- related regression: `82 passed in 1.25s`
- full regression: `2982 passed in 12.70s`

### 8.3 Linear Infrastructure Engine — TAMAMLANDI / LOCKED

8.3 test-first tamamlandı ve final regression ile doğrulandı.

Yeni ana modüller:

- `CORE/atlas_linear_infrastructure_resolver.py`
- `CORE/atlas_linear_infrastructure_geometry_builder.py`
- `CORE/atlas_linear_infrastructure_solid_builder.py`

Reader entegrasyonu:

- `CORE/atlas_local_osm_reader.py`
- public `read()` sonucu artık `linear_infrastructure` koleksiyonunu taşır
- cycleway source artık legacy pedestrian-path bucket'ında tutulmaz;
  `cycle_corridor` olarak sınıflanır

Kilitlenen semantic kapsam:

- railway
- light rail
- tram
- cycle corridor
- bridleway corridor
- pedestrian path
- embankment
- infrastructure corridor

Kilitlenen davranışlar:

- active / proposed / disused operational state
- surface visibility
- product-surface eligibility
- surface / bridge-elevated / subsurface vertical treatment
- visual priority
- source-driven physical width
- explicit printable minimum width
- gauge-aware parallel-line readability
- LoD eligibility
- `linear_strip` / `area_strip` geometry kind
- product-space footprint generation
- terrain-following closed infrastructure solid generation

Linear infrastructure için source width yoksa gerçek-metre genişliği
uydurulmaz; explicit printable minimum kullanılır.

`AtlasUrbanRoadHierarchyResolver.resolve_physical_width_mm(...)` yeniden
kullanıldığı için scale matematiği ikinci kez yazılmadı.

Bonn exact benchmark doğrulaması:

- reader linear infrastructure: `26`
- product-surface eligible: `4`
- `3` active surface tram
- `1` closed `landuse=railway` infrastructure corridor
- tunnel/proposed/disused rail records surface product geometry'sine alınmaz

Anıtkabir regression güncellemesi:

- source way `883691085`
- `highway=cycleway`
- artık `cycle_corridor`
- pedestrian-path sayısı `32 -> 31`
- source kaybolmaz; `linear_infrastructure` sonucu içinde korunur

Doğrulama:

- focused 8.3 package: `102 passed in 0.09s`
- related regression: `105 passed in 0.35s`
- full regression: `3085 passed in 12.59s`

8.3 içinde Bonn-specific koordinat, landmark veya görsel taklit hack'i
eklenmedi.

8.3 commit henüz oluşturulmadığı için bu kayıtta yeni commit hash
uydurulmamıştır. Son güvenli/push edilmiş 8.2 commit:

`e75cb10d64d8e2ab3f52fd88a7c9df12ce1bea3c`

### Sıradaki tek adım

**8.4 Urban Block Resolver**

8.4 test-first yürütülecek.

Amaç generic building gruplarını source footprint, gerçek courtyard,
semantic landmark ve mevcut LoD davranışını bozmadan block-aware product
composition altında çözmektir.

8.4 tamamlanmadan 8.5 veya sonraki behavior başlamayacak.

Uzun-form teknik sözleşme ve acceptance kriterleri için:

`Docs/Roadmap/URBAN_FABRIC_PRODUCT_COMPOSITION_V1.md`

esas alınmalıdır.

## 8 Ağustos 2026 — Urban Fabric 8.4 Urban Block Resolver

8.4 test-first geliştirildi ve full regression aşamasına ulaştı.

Yeni ana dosyalar:

- `CORE/atlas_urban_block_resolver.py`
- `Test/test_urban_block_resolver.py`

Kilitlenen çekirdek davranışlar:

- road-defined urban block polygonization
- generic-building block membership
- deterministic exclusive multi-block assignment
- source-footprint preservation
- courtyard / inner-void preservation
- block density reporting
- shared-boundary / street-wall continuity metric

Ek block-level metadata:

- local `median_height_m` reporting
- nearest-landmark distance reporting
- existing `AtlasLoDLevel` pass-through as composition metadata
- courtyard count
- `urban_block` scene element integration
- deterministic `contains_building` relationships

Doğrulama:

- focused 8.4: `39 passed in 0.06s`
- related regression: `379 passed in 0.35s`
- full regression: `3124 passed in 12.86s`

8.4 sınırları:

- source building footprint'leri mutate edilmez
- courtyard geometrileri kapatılmaz
- landmark binalar generic block membership'e alınmaz
- bina yükseklikleri değiştirilmez; yalnız block-level istatistik raporlanır
- yeni bir LoD resolver oluşturulmaz; mevcut LoD contract kullanılır
- Bonn-specific koordinat veya competitor-specific implementation kuralı yoktur

### Sıradaki tek adım

**8.5 Park & Plaza Semantic Surface Engine**

8.5 de test-first yürütülecek. 8.4 yeni davranış eklenmeden önce dokümantasyon,
scoped commit, push ve `HEAD == origin/main` doğrulamasıyla kilitlenecektir.

## 8 Ağustos 2026 — Urban Fabric 8.5 Park & Plaza Semantic Surface Engine

8.5 test-first geliştirildi ve full regression aşamasına ulaştı.

Yeni ana dosyalar:

- `CORE/atlas_park_plaza_semantic_resolver.py`
- `Test/test_park_plaza_semantic_resolver.py`

Kilitlenen semantic sınıflar:

- park
- garden
- plaza
- pedestrian_square
- courtyard
- grass_area
- cemetery
- sports_field

Kilitlenen profile/composition davranışları:

- immutable semantic profile contract
- semantic sınıfa göre distinct ground surface role
- profile-aware composition capability resolution
- deterministic `composition_layers`
- source record enrichment without source mutation
- internal paths / tree rows / vegetation clusters / clearings / borders / edges metadata preservation
- plaza ve pedestrian-square yüzeylerinin park-only composition katmanlarını almaması
- geometry-derived courtyard semantics

Reader entegrasyonu:

- mevcut `AtlasLocalOSMReader` park record yapısı korunur
- mevcut `pedestrian_paths` koleksiyonu kullanılır
- tamamen park poligonu içinde kalan pedestrian path'ler `internal_paths` olarak çözülür
- park sınırını kesip dışarı çıkan path'ler internal path sayılmaz
- internal path'ler ID üzerinden deduplicate edilir
- internal path sırası input sırasından bağımsız deterministiktir

8.5 sınırları:

- yeni tree-row producer eklenmedi; 8.7 kapsamına bırakıldı
- yeni vegetation-cluster producer eklenmedi; 8.6 kapsamına bırakıldı
- park source geometry'si mutate edilmez
- Bonn/Hofgarten-specific kural eklenmez

Doğrulama:

- focused 8.5: `35 passed in 0.05s`
- related regression: `206 passed in 0.24s`
- full regression: `3159 passed in 12.98s`

### Sıradaki tek adım

**8.6 Vegetation Composition Engine**

8.6 test-first yürütülecek. 8.5 yeni davranış eklenmeden önce dokümantasyon,
scoped commit, push ve `HEAD == origin/main` doğrulamasıyla kilitlenecektir.

## 8 Ağustos 2026 — Urban Fabric 8.6 Vegetation Composition Engine

8.6 test-first geliştirildi ve production vegetation hattına entegre edildi.

Yeni ana dosyalar:

- `CORE/atlas_vegetation_composition_resolver.py`
- `CORE/atlas_forest_canopy_foundation_builder.py`
- `Test/test_vegetation_composition_resolver.py`

Kilitlenen semantic roller:

- `isolated_tree`
- `tree_row`
- `tree_cluster`
- `forest_canopy`

Kilitlenen composition davranışları:

- immutable vegetation composition profile
- source-context-aware semantic role resolution
- gerçek OSM tree kayıtlarının `isolated_tree` olarak korunması
- WorldCover sampled tree kayıtlarının tekil ağaç olarak yorumlanmaması
- `osm_green_area_fill` kayıtlarının `tree_cluster` olarak çözülmesi
- deterministic collection grouping and ordering
- source mutation yapılmaması
- park fill cluster'larının `park_id` bazında ayrılması
- WorldCover forest hücrelerinin source resolution'a göre spatial connectivity ile canopy gruplarına ayrılması
- raw WorldCover provider record formatının desteklenmesi
- `resolution_m` değerinin canopy connectivity kararına taşınması
- WorldCover sampled tree + raw forest double representation'ın engellenmesi

Forest canopy fiziksel temsili:

- mevcut `AtlasWorldCoverSurfaceAggregator.dissolve()` yeniden kullanılır
- bağlı forest hücreleri birleşik polygon yüzeylere dönüştürülür
- açık terrain-following visual surface final STL'ye doğrudan sokulmaz
- `AtlasForestCanopyFoundationBuilder`, mevcut kapalı terrain-following foundation geometrisini reuse eder
- canopy mesh semantic type: `forest_canopy_foundation`
- topology doğrulaması: `0 open edge`, `0 non-manifold edge`

Production entegrasyonu:

- `AtlasFoundationFirstEngine` artık vegetation composition resolver üzerinden çalışır
- WorldCover sampled tree kayıtları doğrudan `tree_meshes` hattına eklenmez
- gerçek isolated tree'ler mevcut `AtlasTreeFoundationBuilder` hattında kalır
- forest canopy meshleri final scene'e ayrı vegetation grubu olarak eklenir
- yeni scene group: `mesh_groups["forest_canopies"]`
- result metadata: `forest_canopy_meshes`
- `castle_only=True` durumunda tree ve canopy vegetation çıktısı bastırılır
- mevcut water/tree filtering davranışı korunur

Preview / multicolor product entegrasyonu:

- `forest_canopies` → mevcut `trees` material batch
- canopy mevcut green vegetation material rengini kullanır
- multicolor exporter canopy geometrisini green STL içine taşır
- yeni ayrı renk/material sistemi oluşturulmaz

8.6 sınırları:

- yeni tree-row detector veya producer eklenmedi; 8.7 kapsamındadır
- avenue / boulevard / promenade alignment çözümü 8.7 kapsamındadır
- dormant `AtlasGreenAreaTreeSampler` production'a bağlanmadı
- Bonn/Hofgarten-specific koordinat veya görsel taklit kuralı eklenmedi
- yeni genel spatial-cluster motoru oluşturulmadı
- mevcut landmark, LoD, road, park ve water davranışları değiştirilmedi

Doğrulama:

- focused vegetation resolver: `51 passed in 0.07s`
- vegetation + engine integration: `57 passed in 0.16s`
- related regression: `154 passed in 0.36s`
- full regression: `3217 passed in 12.60s`

### Sıradaki tek adım

**8.7 Avenue Tree Row Engine**

8.7 test-first yürütülecek. 8.6 yeni davranış eklenmeden önce roadmap ve
START_HERE güncellemesi, scoped commit, push ve `HEAD == origin/main`
doğrulamasıyla kilitlenecektir.

## 8 Ağustos 2026 — Urban Fabric 8.7 Avenue Tree Row Engine

8.7 test-first geliştirildi, gerçek OSM verisi üzerinde doğrulandı ve
production vegetation hattına entegre edildi.

Yeni ana modüller:

- `CORE/atlas_tree_row_resolver.py`
- `CORE/atlas_tree_row_spacing_resolver.py`
- `CORE/atlas_tree_row_layout_resolver.py`
- `CORE/atlas_tree_row_member_producer.py`
- `CORE/atlas_tree_row_context_resolver.py`

Reader / evidence entegrasyonu:

- `AtlasLocalOSMReader` artık `natural=tree_row` way kayıtlarını okur
- `read()` sonucu `tree_rows` koleksiyonunu expose eder
- reader tree rows ile nature-provider tree rows composition hattında birleşir
- source geometry ve source tags korunur

Tree-row resolution:

- semantic role: `tree_row`
- representation mode: `ordered_row`
- source direction ve toplam uzunluk çözülür
- segment istatistikleri diagnostic olarak korunur
- OSM way vertex aralıkları gerçek ağaç spacing'i kabul edilmez
- açık `tree_spacing_m` evidence varsa kullanılır
- explicit spacing yoksa product-readability fallback kullanılır
- fallback, fiziksel tree symbol maksimum çapı + nozzle clearance üzerinden çözülür
- iki noktalı explicit OSM tree-row kayıtları geçerli direction evidence ile strong kabul edilir

Physical representation:

- row members mevcut `AtlasTreeFoundationBuilder` üzerinden üretilir
- controlled symbol: `park_tree_symbol`
- physical contract:
  - diameter: `0.60–1.10 mm`
  - height: `1.0–1.4 mm`
- tree-kind explicit override desteklenir
- deterministic member ids ve ordering korunur
- production parametresi:
  - `tree_row_nozzle_diameter_mm=0.4`
- gerçek resolved XY scale spacing kararına propagate edilir

Urban / landscape context:

- nearby roads ve pedestrian paths değerlendirilir
- yalnız `<= 20 m` ve direction cosine `>= 0.95` adaylar kabul edilir
- yakın fakat crossing / non-parallel feature context olarak kabul edilmez
- deterministic nearest-candidate selection uygulanır
- context metadata row member tags içine taşınır:
  - `adjacent_feature_type`
  - `adjacent_feature_id`
  - `tree_row_relationship`

Source continuity / gaps:

- segment median değerinin `2.5x` üstündeki büyük segmentler source-gap adayıdır
- gap metadata resolver sonucunda korunur
- gap-aware layout büyük source boşluklarının üzerinden yapay tree member üretmez
- gap olmayan mevcut row davranışı değiştirilmez

Gerçek OSM doğrulaması:

Köln Regierungsbezirk:

- `7408` gerçek `natural=tree_row` way
- filtered source supporting nodes: `28127`
- current-model naive members: `88639`
- gap-aware members: `83250`
- bastırılan yapay member: `5389`
- gerçek üretim davranışında etkilenen row: `363`

Köln Pädagogische Fakultät:

- `6` gerçek tree row
- `6/6` strong
- `58` controlled member
- `0` detected source gap
- `5/6` geçerli parallel road/path context
- yeni tree-row rhythm gerçek STL / Bambu Studio görünümünde belirgin biçimde doğrulandı
- formal landscape / avenue okunabilirliğinde görünür premium iyileşme gözlendi

8.7 sınırları:

- source olmayan arbitrary tree row icat edilmez
- way vertexleri gerçek ağaç pozisyonu veya gerçek spacing sayılmaz
- crossing path/road context olarak zorlanmaz
- Bonn/Hofgarten veya Köln'e özel koordinat kuralı eklenmez
- landmark, LoD, terrain, bridge veya mevcut park geometrisi yeniden yazılmaz

Doğrulama:

- focused tree-row regression: `70 passed in 0.36s`
- related vegetation / park / nature / engine regression: `156 passed in 0.35s`
- full regression: `3267 passed in 12.78s`

### Sıradaki tek adım

**8.8 Semantic Surface Texture Engine**

8.8 test-first yürütülecek. 8.7 yeni davranış eklenmeden önce scoped commit,
push ve `HEAD == origin/main` doğrulamasıyla kilitlenecektir.



## 9 Ağustos 2026 — Urban Fabric 8.8 + 8.9 Güncel Durum

Son güvenli commit:

- `1607154 Add semantic surfaces and morphology-aware terrain`
- push başarılı
- `HEAD == origin/main`

### 8.8 Semantic Surface Texture Engine

Durum:

- teknik implementation: tamamlandı
- production integration: tamamlandı
- topology blocker: çözüldü
- long-interior-edge blocker: çözüldü
- automated regression: yeşil
- final visual acceptance: açık
- LOCK: henüz değil

Ana production davranışı:

- semantic surface resolver
- deterministic physical pattern
- shallow printable relief
- terrain-following meshing
- Foundation First integration
- source semantic preservation
- constrained dense-boundary triangulation
- shared-edge-safe interior refinement

Gerçek Köln son teknik doğrulama:

- city triangles: `43122`
- color preview triangles: `49856`
- textured park open edges: `0`
- `> 2 × feature_pitch_mm` interior edges: `0`
- `> 4 × feature_pitch_mm` interior edges: `0`

Son preview:

`OUTPUT/PREVIEW/koeln_paedagogische_fakultaet_competitor_comparison_v1.png`

Kalan acceptance:

- yeni preview'da park / grass yüzeylerinin premium,
  okunabilir ve fan/radial artefact içermeyen fiziksel dilinin
  görsel doğrulanması

### 8.9 Morphology-Aware Terrain Product Resolver

Durum:

- resolver contract: tamamlandı
- deterministic morphology policy: tamamlandı
- printability resolution: tamamlandı
- terrain pipeline integration: tamamlandı
- terrain truth preservation: doğrulandı
- automated regression: yeşil

Yeni dosyalar:

- `CORE/atlas_morphology_aware_terrain_product_resolver.py`
- `Test/test_morphology_aware_terrain_product_resolver.py`
- `Test/test_terrain_pipeline_morphology_product_resolver.py`

Morphology sınıfları:

- dense urban
- historic core
- suburban
- rural
- mountain
- landscape / nature

8.9 source elevation data'yı değiştirmez.

Product-facing kararlar metadata profili olarak taşınır:

- terrain emphasis
- vertical compression policy
- source elevation range
- product size
- urban density pressure
- landmark / semantic protection
- physical relief range
- printable relief resolution
- relative product relief

Pipeline truth contract:

- terrain grid değişmez
- `delta_height_m` değişmez
- `z_scale` değişmez

Doğrulama:

- focused resolver: `13 passed in 0.02s`
- resolver + pipeline: `16 passed in 0.06s`
- related 8.8 + 8.9: `102 passed in 2.11s`
- full regression: `3338 passed in 15.03s`

### Sıradaki tek adım

8.8'in son `49856` triangle Köln preview görsel acceptance'ını tamamla.

Ardından:

**8.10 Water & Shoreline Composition Engine**


## 9 Ağustos 2026 — 8.9 Terrain Sampling / Presentation Current Status

8.9 durumu:

- morphology-aware resolver: yeşil
- terrain pipeline resolver integration: yeşil
- provider sampling audit: tamamlandı
- OpenTopography/COP30 bilinear sampling: yeşil
- configurable production terrain grid: yeşil
- Köln 97 x 97 full-city integration: doğrulandı
- presentation-surface regularization: AÇIK
- 8.9 LOCK: HAYIR

Köln terrain truth:

- local SRTM tile `N50E006.hgt` mevcut değil
- gerçek production source:
  OpenTopography COP30 fallback
- cache:
  `CACHE/DEM/COP30_50_930972_6_914474_50_937593_6_924979.asc`

Provider-level bulgular:

- SRTM nearest-neighbor sampling test-first bilinear hale getirildi
- focused SRTM test: `2 passed`
- OpenTopography nearest-neighbor sampling test-first bilinear hale getirildi
- focused OpenTopography test: `1 passed`

Terrain grid integration:

- yeni production parametresi:
  `terrain_grid_size`
- default:
  `25`
- Köln integration reference:
  `97`
- FoundationFirst → TerrainPipeline propagation doğrulandı
- focused integration:
  `4 passed`

Köln full-city 97 x 97 sonuç:

- city triangles: `74762`
- preview triangles: `81404`
- buildings / roads / parks / vegetation / foundations terrain ile birlikte
  başarılı üretildi
- Bambu Studio görsel incelemesinde coarse terrain stepping belirgin biçimde
  azaldı

Kalan problem:

- single-color / shallow-light görünümünde source DEM raster karakterinden kalan
  yüzey banding/faceting

Sıradaki tek adım:

**canonical truth'u değiştirmeyen deterministic presentation-surface
regularization paketini test-first geliştirmek.**

Bu tamamlanmadan 8.10'a geçilmez.

## 9 Ağustos 2026 — 8.9 FINAL LOCK

**8.9 Morphology-Aware Terrain Product Resolver: LOCK**

Tamamlanan final terrain sözleşmesi:

- morphology-aware terrain resolver tamamlandı
- canonical source elevation truth korunuyor
- SRTM provider bilinear interpolation kullanıyor
- OpenTopography/COP30 provider bilinear interpolation kullanıyor
- `terrain_grid_size` production FoundationFirst zincirinde configurable
- legacy default `25`
- Köln production integration reference `97 x 97`
- visible terrain için deterministic presentation-surface regularization eklendi
- canonical `grid` değişmiyor
- canonical `top_points` değişmiyor
- FoundationSampler terrain truth değişmiyor
- visible surface ayrı `presentation_top_points` üzerinden üretiliyor
- presentation regularization default olarak kapalıdır
- Köln GRID97 A/B Bambu Studio görsel acceptance tamamlandı
- full regression: `3348 passed in 13.42s`

8.9 kapsamında açık teknik iş kalmadı.

**DURMA NOKTASI:** 8.10 Water & Shoreline Composition Engine henüz
başlatılmayacak. Kullanıcının sonraki talimatı beklenecek.

## 9 Ağustos 2026 — 8.10 FINAL LOCK

**8.10 Water & Shoreline Composition Engine: LOCK**

8.10 genel, source-preserving ve product-facing water / shoreline
composition katmanı olarak tamamlandı.

### Tamamlanan genel semantic kapsam

Desteklenen temel sınıflar:

- river
- canal
- lake
- coastline
- island
- embankment
- quay
- waterfront_pier
- marina

Water surface ve shoreline structure birbirinden semantic olarak ayrılır.

Ek composition rolleri:

- `water_surface`
- `shoreline_structure`
- `land_within_water`

### First-class scene contract

Water / shoreline kayıtları artık şu ortak product contract bilgilerini taşır:

- `semantic_class`
- `composition_role`
- `first_class_scene_layer`
- `lod_eligible`
- `preserves_source_geometry`
- `physical_separation_role`
- `product_scale_simplification`
- `shoreline_treatment`

Temel kurallar:

- source geometry korunur
- artificial shoreline detail üretilmez
- unknown semantics için yapay class üretilmez
- water surface continuity açık contract olarak taşınır
- shoreline readability açık contract olarak taşınır
- water fiziksel olarak raised / separated product solid olarak temsil edilebilir
- shoreline structures ayrı structural-edge semantiği taşır
- islands land-within-water morphology olarak ayrılır

### Waterfront reader extraction

`AtlasLocalOSMReader` artık ayrı:

`waterfront_structures`

output katmanı üretir.

Test-first desteklenen source tipleri:

- `man_made=quay` → `quay`
- `man_made=pier` → `waterfront_pier`
- `leisure=marina` → `marina`

Bridge pier metadata ile gerçek waterfront pier birbirine karıştırılmaz.

Source:

- id
- geometry
- tags
- geometry type

korunur.

### Scene-level composition

Reader'dan gelen:

- waters
- coastlines
- waterfront structures
- embankments

ortak `water_shoreline_composition` kayıtlarına resolve edilir.

FoundationFirst final result artık:

- `reader_waterfront_structures`
- `water_shoreline_composition`
- `water_shoreline_composition_records`

alanlarını taşır.

Mevcut inland-water ve coastline foundation geometry hattı yeniden
yazılmamıştır.

### Bridge / road / rail interaction

Water / shoreline source geometry ile gerçek scene context arasındaki
intersection deterministic olarak resolve edilir.

Taşınan interaction flag'leri:

- `bridge_interaction`
- `road_interaction`
- `rail_interaction`

Kurallar:

- yalnız gerçek geometry intersection kullanılır
- proximity buffer kullanılmaz
- tahmini ilişki icat edilmez
- invalid / eksik geometry interaction üretmez
- source geometry mutate edilmez

FoundationFirst scene context'i gerçek:

- bridge landmark
- bridge road
- road
- railway / light rail / tram

kaynaklarından oluşturulur.

### Embankment ve island tamamlaması

8.10 final closure öncesinde iki açık contract da kapatıldı:

- `place=island` → `island`
- linear `embankment` source → shoreline composition

Böylece roadmap'in water / shoreline morphology kapsamındaki zorunlu
sınıfları semantic contract düzeyinde tamamlandı.

### Galata gerçek sahne acceptance

Gerçek benchmark:

`Data/OSM/galata-bridge-test.osm.pbf`

Galata Köprüsü — Eminönü / Karaköy sahnesi:

- ürün alanı: `220 × 220 mm`
- ölçek: `1:5500`
- final scene: `1459` mesh
- final scene triangles: `65832`
- Galata prototype: `7` mesh / `100` triangle
- retained road meshes: `193`
- water meshes: `1`
- water triangles: `15886`

Renkli acceptance preview:

`OUTPUT/PREVIEW/galata_bridge_8_10_color_acceptance.png`

Renkli interactive OBJ / MTL:

- `OUTPUT/PREVIEW/galata_bridge_8_10_color_acceptance.obj`
- `OUTPUT/PREVIEW/galata_bridge_8_10_color_acceptance.mtl`

OBJ / MTL acceptance scene:

`65832` triangle

Final STL ile birebir triangle parity doğrulandı.

Görsel acceptance sonucunda:

- water first-class morphology layer olarak açık okunuyor
- iki kıyı water body tarafından net ayrılıyor
- Galata Köprüsü water üzerinde doğru urban connector olarak okunuyor
- bridge / road / waterfront ilişkisi korunuyor
- water surface texture bilinçli dalga presentation'ıdır
- worship / church fallback landmark blokları 8.10 kapsamı değildir

### Doğrulama

Final 8.10 focused regression:

`49 passed in 0.23s`

Full regression:

`3387 passed in 13.53s`

### Mimari sınır

8.10:

- bridge engine'i yeniden yazmaz
- terrain truth'u değiştirmez
- source shoreline detail icat etmez
- worship / church landmark geometry kalitesini çözmeye çalışmaz
- yalnız water / shoreline semantic composition ve scene interaction
  contract'ını sağlar

### Sonuç

**8.10 Water & Shoreline Composition Engine tamamlandı ve LOCK edildi.**

8.10 kapsamında açık teknik iş kalmadı.

Sıradaki roadmap paketi:

**8.11 — Bridge / Infrastructure Urban Integration**

8.11 henüz başlatılmamıştır.

## 9 Ağustos 2026 — 8.11 FINAL LOCK

**8.11 Bridge / Infrastructure Urban Integration: LOCK**

8.11 mevcut ATLAS bridge engine yeniden yazılmadan tamamlandı.

Yeni genel Urban Fabric entegrasyon katmanı:

- `CORE/atlas_bridge_urban_integration_resolver.py`
- `Test/test_bridge_urban_integration_resolver.py`
- `Test/test_foundation_first_bridge_urban_integration.py`

Production entegrasyonu:

- `CORE/atlas_foundation_first_engine.py`

### Kilitlenen 8.11 sözleşmesi

Bridge artık Urban Fabric composition içinde bağımsız landmark geometry olarak
değil, surrounding transport / water / terrain sistemiyle ilişkili semantic
element olarak temsil edilebilir.

Desteklenen context family'leri:

- road hierarchy
- railway / tram / light rail
- water
- shoreline / quay / waterfront pier / marina
- embankment
- surrounding urban block
- terrain

### Geometry-based context

Bridge context source ilişkileri gerçek source geometry intersection üzerinden
resolve edilir.

Kurallar:

- artificial proximity ilişkisi üretilmez
- source geometry değiştirilmez
- yanlış semantic family source-id eşleşmesi ilişki üretmez
- bridge source identity korunur
- general solution kullanılır
- Bonn, Galata veya başka tek landmark için özel integration kuralı eklenmez

Geometry context zinciri:

`bridge source geometry`
→ `intersecting context source ids`
→ `Urban Fabric target elements`
→ `typed bridge relationships`

Typed relationships:

- `connects_road`
- `connects_railway`
- `crosses_water`
- `meets_shoreline`
- `meets_embankment`
- `adjacent_to_block`
- `placed_on_terrain`

### Approach-road continuity

Mevcut ATLAS bridge road-approach sistemi yeniden yazılmadı.

Korunan mevcut capability:

- `AtlasBridgeRoadApproachResolver`
- `AtlasBridgeRoadApproachTargetResolver`
- `AtlasBridgeRoadApproachProfile`
- `AtlasBridgeRoadApproachMesher`

8.11 yalnız mevcut bridge mesh içindeki `road_approaches` bilgisini integration
contract'a bağlar.

Integration record şu bilgileri taşıyabilir:

- approach-road continuity mevcut / değil
- approach count
- bağlı road mesh index'leri
- maksimum source distance
- toplam approach length

`road_mesh_index`, Urban Fabric source identity olarak yeniden yorumlanmaz.

### Bridge topology / landmark preservation

8.11 bridge geometry üretimini yeniden yazmaz.

Final integration contract açıkça:

- `existing_bridge_topology_preserved=True`
- `bridge_geometry_rewritten=False`

taşır.

Mevcut landmark davranışı ve bridge topology hattı korunur.

### Visual priority

Bridge Urban Fabric element:

- `semantic_class=bridge`
- `product_priority=1.0`
- `lod_eligible=True`

olarak composition sistemine katılır.

Bridge'in ilişkili road / rail / water / infrastructure context içindeki
relative visual priority'si deterministic olarak resolve edilir.

### LoD coordination

Yeni paralel LoD sistemi oluşturulmadı.

8.11 mevcut:

- `AtlasLoDResolver`
- `AtlasLoDMeshFilter`
- Urban Fabric `lod_eligible`
- infrastructure / road semantic priority

sözleşmeleriyle birlikte çalışır.

LoD-ineligible surrounding element zorla LoD sistemine dahil edilmez.

### FoundationFirst production integration

`AtlasFoundationFirstEngine.generate_city_stl()` final result zinciri artık
bridge integration attachment çağrısını içerir.

Final result şu alanları expose eder:

- `bridge_urban_integration`
- `bridge_urban_integration_records`

Attachment, product-bounds filtering sonrasındaki gerçek retained landmark
mesh'leriyle çalışır.

Foundation placement bilgisi integration record'a taşınabilir:

- `foundation_z`

Bu entegrasyon bridge mesh üretimini değiştirmez.

### Doğrulama

Yeni 8.11 resolver + FoundationFirst production tests:

- `24 passed`

Bridge / approach / water-shoreline / LoD focused regression:

- `90 passed in 0.90s`

Full regression:

- `3411 passed in 13.56s`

### 8.11 acceptance sonucu

Roadmap acceptance maddeleri karşılandı:

- road hierarchy integration
- railway integration where applicable
- water relationship
- shoreline relationship
- embankment relationship
- urban-block context
- terrain placement
- approach-road continuity
- existing bridge topology preservation
- landmark behavior preservation
- city-scene visual priority
- surrounding infrastructure LoD coordination
- general / landmark-independent integration

Primary acceptance principle karşılandı:

> Bridges should read as part of the complete transport and water system,
> not as isolated standalone geometry.

8.11 kapsamında açık teknik iş kalmadı.

**Sıradaki roadmap paketi: 8.12 — Building Height Product Normalizer.**

## 9 Ağustos 2026 — 8.12 FINAL LOCK

**8.12 Building Height Product Normalizer: LOCK**

8.12, 8.0 Bonn Urban Fabric Ground-Truth Audit sonucuna uygun olarak
tamamlandı.

8.0'da generic building height parser hattında genel bir source/parser bug
bulunmadığı doğrulanmıştı.

Bu nedenle 8.12:

- source height parser'ını yeniden yazmaz
- `height`
- `building:levels`
- fallback height
- building-part hierarchy
- landmark-specific architecture
- terrain / foundation placement

source truth katmanlarını değiştirmez.

Bunun yerine generic building geometry için ayrı bir product-facing height
policy oluşturur.

### Eklenen ana modüller

- `CORE/atlas_building_height_product_normalizer.py`
- `CORE/atlas_building_height_product_context_resolver.py`

Yeni test paketleri:

- `Test/test_building_height_product_normalizer.py`
- `Test/test_building_height_product_context_resolver.py`
- `Test/test_foundation_first_building_height_product_context.py`
- `Test/test_foundation_first_building_height_product_wiring.py`
- `Test/test_foundation_first_pipeline_product_height.py`
- `Test/test_foundation_mesh_extruder_product_height.py`
- `Test/test_foundation_scene_builder_building_height_product.py`

Production entegrasyonu:

- `CORE/atlas_foundation_first_engine.py`
- `CORE/atlas_foundation_scene_builder.py`
- `CORE/atlas_foundation_first_pipeline.py`
- `CORE/atlas_foundation_mesh_extruder.py`
- `CORE/atlas_urban_block_resolver.py`

### Source truth / product height ayrımı

8.12'nin temel mimari kuralı:

> Source building height truth korunur; product readability için ayrı ve
> deterministic bir product height üretilebilir.

`AtlasBuilding.estimated_height` değiştirilmez.

Generic extrusion hattına ayrı:

- `product_height_m`

override'ı aktarılabilir.

Final building mesh aynı anda:

- `estimated_height_m`
- `product_height_m`
- `height_product_normalization_reason`
- `height_product_normalization_changed`

bilgilerini taşıyabilir.

Bu nedenle normalization source veriyi overwrite etmez.

### Generic building height normalization

`AtlasBuildingHeightProductNormalizer` aşağıdaki context'i birlikte
değerlendirir:

- generic source building height
- local block median height
- product scale
- physical minimum readable height
- excessive background height
- statistical height outlier
- landmark proximity
- semantic building importance

Normal variation keyfi biçimde flatten edilmez.

Aşırı generic background outlier'ları local block context'e göre
deterministic olarak sınırlandırılabilir.

Fiziksel ölçekte okunamayacak kadar düşük generic building height ise
minimum readable product height'a yükseltilebilir.

### Local block context

8.12, mevcut 8.4 Urban Block Resolver altyapısını yeniden kullanır.

Yeni context resolver:

- source buildings
- road-defined blocks
- block membership
- local median building height
- landmark proximity

bilgisinden product-height context üretir.

Block relationships source footprint'i değiştirmez ve building merge
yapmaz.

### Gerçek metre uzayı

Urban block / landmark proximity height policy için gerçek metre uzayında
çözülür.

Lat/lon degree değerleri doğrudan metre gibi yorumlanmaz.

`AtlasCoordinateEngine.latlon_to_local_meters(...)` kullanılarak context
production-scale fiziksel uzaya taşınır.

### Semantic importance

Normalizer yeni ve yapay bir building priority uydurmaz.

Mevcut context varsa:

1. `semantic_importance`
2. `product_priority`
3. aksi halde `0.0`

sırasıyla kullanılır.

Yüksek semantic importance taşıyan generic building'lerde moderate gerçek
height variation korunabilir.

### Landmark proximity

Landmark yakınındaki generic urban fabric'in tamamı kör biçimde aynı yüksekliğe
çekilmez.

Moderate contextual height variation korunabilir.

Ancak extreme generic background outlier, landmark yakınında olsa dahi
kontrolsüz biçimde korunmaz.

Bu sayede landmark çevresi düzleştirilmeden semantic landmark dominance
korunabilir.

### Semantic architecture koruması

Generic product-height normalizer:

- castle architecture
- building parts
- semantic landmark architecture

üzerinde generic height policy zorlamaz.

Castle-specific height multipliers / minimums korunur.

Building-part vertical interval contract korunur.

Semantic landmark geometry kendi architecture ve height policy'sini
kullanmaya devam eder.

### FoundationFirst production wiring

`AtlasFoundationFirstEngine.generate_city_stl()` artık generic building
product-height context'ini production öncesinde çözebilir.

Context:

`raw buildings + roads + landmarks`
→ `road-defined urban blocks`
→ `local block height context`
→ `building product-height normalization`
→ `FoundationFirstPipeline`
→ `FoundationMeshExtruder`

zinciri üzerinden gerçek mesh üretimine ulaşır.

Public production parameter:

- `building_minimum_readable_height_mm`

ile fiziksel minimum product readability kontrol edilebilir.

Normalizasyon context'i olmayan building'lerde legacy extrusion davranışı
korunur.

### Existing behavior compatibility

8.12 entegrasyonu sırasında iki compatibility sınırı ayrıca doğrulandı:

- tek road segment içeren unrelated scenes Urban Block resolution nedeniyle
  hata vermez
- legacy FoundationFirst extruder test doubles, product override yokken eski
  çağrı contract'ıyla çalışmaya devam eder

Böylece yeni product-height davranışı opt-in / context-driven kalır.

### Roadmap acceptance sonucu

8.12 roadmap maddeleri karşılandı:

- generic building height reasoning
- local block context
- product scale
- physical minimum readable height
- excessive background height control
- statistical height outlier handling
- landmark proximity
- semantic building importance
- semantic landmark architecture preservation
- source height truth preservation
- non-destructive city-height normalization

Primary acceptance principle karşılandı:

> Generic buildings should form a coherent background height field while
> meaningful landmarks remain visually dominant.

### Doğrulama

8.12 focused / production integration regression:

- `114 passed in 0.29s`

Full ATLAS regression:

- `3446 passed in 14.60s`

8.12 kapsamında açık teknik iş kalmadı.

**Sıradaki roadmap paketi: 8.13 — Physical Cartographic Exaggeration Resolver.**



## 9 Ağustos 2026 — 8.13 FINAL LOCK

**8.13 Physical Cartographic Exaggeration Resolver: LOCK**

8.13, strict real-world scale altında fiziksel olarak kaybolabilecek önemli
cartographic feature'ları kontrollü biçimde okunabilir tutan genel product
resolution katmanı olarak tamamlandı.

Yeni ana resolver:

- `CORE/atlas_physical_cartographic_exaggeration_resolver.py`

Ana contract:

- `AtlasPhysicalCartographicExaggeration`
- `AtlasPhysicalCartographicExaggerationResolver`

### Temel 8.13 ilkesi

Sistem source truth'u değiştirmez.

Her desteklenen feature için iki değer ayrı tutulabilir:

- strict-scale physical width
- product geometry physical width

Strict-scale değer fiziksel olarak okunabiliyorsa aynen korunur.

Okunamıyorsa product geometry yalnız deterministic physical minimum seviyesine
çıkarılır.

Bu nedenle davranış arbitrary enlargement değildir.

Resolution mantığı:

`source width`
→ `strict scale width`
→ `printable / nozzle minimum`
→ `controlled physical exaggeration`

### Resolver context

8.13 resolver şu bilgileri birlikte kullanabilir:

- semantic feature class
- source width
- product scale
- physical product size
- nozzle diameter
- explicit minimum printable width
- semantic priority
- LoD level

Resolver sonucu ayrıca:

- strict-scale width
- final physical width
- effective physical minimum
- exaggeration applied / not applied
- resolution reason

bilgisini taşır.

### Desteklenen semantic kapsam

8.13 genel resolver contract'ı şu feature family'lerini destekler:

- major road
- local road
- service road
- pedestrian path
- cycleway
- railway
- light rail
- tram
- narrow waterway
- shoreline edge
- vegetation element

### Road integration

Mevcut `AtlasRoadFoundationBuilder` yeniden yazılmadı.

8.13 mevcut road hierarchy / source-width davranışına optional cartographic
context bağlar.

Road source width strict scale altında yeterince okunabiliyorsa gerçek ölçek
korunur.

Fiziksel minimumun altındaysa:

- nozzle diameter
- explicit printable minimum

birlikte değerlendirilerek deterministic product width uygulanabilir.

Mevcut road hierarchy korunur:

`major road > local road > service road > pedestrian path`

Legacy behavior korunur; cartographic context yoksa mevcut road üretimi
sessizce değiştirilmez.

### Linear infrastructure integration

Mevcut:

- `AtlasLinearInfrastructureResolver`
- `AtlasLinearInfrastructureGeometryBuilder`
- `AtlasLinearInfrastructureSolidBuilder`

mimarisi korunur.

8.13 physical exaggeration desteği:

- railway
- light rail
- tram
- diğer uygun linear infrastructure width kaynakları

için mevcut source-width çözümüne bağlandı.

Rail / tram geometry veya vertical-treatment sistemi yeniden yazılmadı.

Strict-scale width okunabilir olduğunda aynen korunur.

### Water / shoreline integration

`AtlasWaterShorelineCompositionResolver` artık gerektiğinde 8.13 general
cartographic exaggeration resolver'ını kullanabilir.

Desteklenen fiziksel resolution semantics:

- `narrow_waterway`
- `shoreline_edge`

Water source truth ve shoreline composition contract korunur.

### Narrow waterway production

Açık line-based:

- `waterway=river`
- `waterway=stream`
- `waterway=canal`

source geometry artık reader tarafından korunabilir.

`AtlasLocalOSMReader` bu feature'lar için iki veya daha fazla noktalı açık
geometry'yi `waters` koleksiyonuna taşıyabilir.

Surface-water polygon davranışı ayrıca korunur.

Yeni narrow-waterway production hattı:

`OSM open waterway`
→ `reader waters`
→ `physical cartographic exaggeration`
→ `terrain contour band`
→ `terrain-following closed solid`

şeklindedir.

Yeni geometry-specific landmark hack eklenmedi.

Mevcut genel builder'lar yeniden kullanılır:

- `AtlasTerrainContourBandBuilder`
- `AtlasLinearInfrastructureSolidBuilder`

### Vegetation integration

`park_tree_symbol` için source crown diameter mevcutsa:

- `diameter_crown`

gerçek-metre source truth olarak kullanılabilir.

Bu değer product scale'e çevrilir ve 8.13 physical exaggeration resolver
üzerinden fiziksel tree-symbol diameter'a dönüştürülebilir.

Zincir:

`FoundationFirst vegetation`
→ `AtlasTreeFoundationBuilder.build_trees`
→ `_build_tree_mesh`
→ `_build_park_tree_symbol`
→ `_park_tree_symbol_dimensions`
→ `AtlasPhysicalCartographicExaggerationResolver`

Source crown diameter yoksa mevcut legacy randomized symbol-dimension davranışı
korunur.

### FoundationFirst production integration

`AtlasFoundationFirstEngine.generate_city_stl()` 8.13 cartographic context'i
production zincirine taşıyabilir.

Public optional context:

- `cartographic_nozzle_diameter_mm`
- `cartographic_lod_level`

Product size mevcut `target_size_mm` değerinden,
scale ise gerçek resolved `xy_scale` değerinden alınır.

Bu context gerektiğinde:

- roads
- narrow waterways
- vegetation

production yollarına aktarılır.

Cartographic LoD değeri mevcut `AtlasLoDLevelCatalog` üzerinden resolve edilir;
yeni paralel LoD sistemi oluşturulmaz.

8.13 davranışı context-driven / backward-compatible kalır.

### Source truth ve hierarchy koruması

8.13 şu prensipleri LOCK eder:

- source geometry değiştirilmez
- strict scale değeri kaybedilmez
- okunabilir feature gereksiz yere büyütülmez
- semantic hierarchy korunur
- physical minimum deterministic uygulanır
- landmark-specific hack eklenmez
- mevcut LoD architecture yeniden yazılmaz
- existing road / rail / water / vegetation systems yeniden yazılmaz

Primary acceptance principle karşılandı:

> Features that matter to city readability should remain physically visible
> without destroying their relative hierarchy or spatial relationships.

### Doğrulama

8.13 combined cartographic focused regression:

- `67 passed in 0.18s`

FoundationFirst / runtime integration regression:

- `53 passed in 0.26s`

Expanded related regression:

- `200 passed in 0.40s`

Full ATLAS regression:

- `3503 passed in 14.59s`

8.13 kapsamında açık teknik iş kalmadı.

**Sıradaki roadmap paketi: 8.14 — City Composition LoD.**


## 9 Ağustos 2026 — 8.14 FINAL LOCK

**8.14 City Composition LoD: LOCK**

8.14, mevcut ATLAS LoD mimarisini yeniden yazmadan LoD kararını tekil mesh
karmaşıklığından bütün şehir kompozisyonu ve narrative hierarchy seviyesine
genişletti.

Yeni ana bileşenler:

- `CORE/atlas_city_composition_lod_resolver.py`
- `CORE/atlas_city_composition_scene_adapter.py`
- `CORE/atlas_city_composition_mesh_filter.py`

### Temel 8.14 ilkesi

City Composition LoD, yalnız triangle count azaltmaya çalışan paralel bir LoD
sistemi değildir.

Mevcut:

- `AtlasLoDLevel`
- `AtlasLoDLevelCatalog`
- `AtlasLoDResolver`
- `AtlasLoDResolutionResult`
- component-level LoD / mesh-filter architecture

korunur.

8.14 bu sistemin resolved LoD level bilgisini şehir semantiğiyle birlikte
kullanır.

Primary acceptance principle:

> LoD must control the narrative hierarchy of the city, not only triangle
> count.

### City Composition LoD karar contract'ı

`AtlasCityCompositionLoDResolver` karar verirken şu girdileri birlikte
kullanabilir:

- semantic importance
- product priority
- physical product size
- scene morphology
- landmark proximity
- printability
- existing ATLAS LoD level

Her karar şu bilgileri taşıyabilir:

- retain
- simplify
- narrative priority
- representation mode
- decision reason
- resolved LoD level

### Semantic narrative hierarchy

8.14 deterministic city-level semantic priority sistemi oluşturur.

Yüksek narrative priority örnekleri:

- landmark
- major road
- railway
- light rail
- tram
- water
- park

Orta / background composition örnekleri:

- urban block
- generic building
- isolated building
- tree row
- vegetation

Düşük-priority detail örnekleri:

- service road
- pedestrian path
- minor path

Bu hierarchy sayesinde landmark / major infrastructure / park / water yapısı,
minor background detail ile aynı karar seviyesinde değerlendirilmez.

### Product-scale davranışı

Physical product size artık composition kararına aktif olarak katılır.

Örneğin küçük ürün ve düşük LoD kombinasyonunda çok minor pedestrian detail
suppress edilebilirken, daha büyük ürün aynı source detail'i koruyabilir.

Bu davranış source geometry'yi değiştirmez; yalnız product representation
kararını değiştirir.

### Scene morphology

Scene morphology composition kararına aktif olarak katılır.

Örneğin dense urban morphology içinde yoğun vegetation detail daha agresif
generalization adayı olabilirken suburban morphology aynı vegetation detail'i
koruyabilir.

### Landmark proximity

Landmark yakınlığı background context için ek narrative protection sağlar.

Bu sayede landmark çevresindeki generic urban context tamamen rastgele
silinmez; yakın çevre şehir anlatısının parçası olarak daha yüksek priority
alabilir.

### Representation modes

8.14 aşağıdaki semantic representation kararlarını tanımlar:

- `source_detail`
- `suppressed`
- `simplified_mass`
- `generalized_row`
- `canopy_or_cluster`

Bu contract'lar sonraki geometry-level generalization sistemleri tarafından
kullanılabilir.

8.14 kapsamında gerçek final-STL composition application doğrudan
`retain=False` suppression kararını uygular.

`generalized_row`, `canopy_or_cluster` ve `simplified_mass` şu aşamada
deterministic composition decision contract'larıdır; yeni geometry
reconstruction sistemi bu paket içinde icat edilmemiştir.

### Existing LoD architecture reuse

`resolve_from_lod_result(...)` adapter'ı mevcut
`AtlasLoDResolutionResult` değerini yeniden hesaplamadan kullanır.

Böylece:

`AtlasLoDResolver`
→ `AtlasLoDResolutionResult`
→ existing `AtlasLoDLevel`
→ `AtlasCityCompositionLoDResolver`

zinciri korunur.

Yeni paralel LoD level/catalog/filter architecture oluşturulmaz.

### Urban Fabric Scene integration

8.14 mevcut:

- `AtlasUrbanFabricElement`
- `AtlasUrbanFabricScene`

contract'larını reuse eder.

`AtlasCityCompositionSceneAdapter` FoundationFirst source koleksiyonlarını ince
bir semantic adapter üzerinden mevcut Urban Fabric Scene modeline taşır.

Desteklenen source family'ler:

- landmarks
- roads / pedestrian paths
- generic buildings
- parks
- waters
- linear infrastructure

Adapter:

- source identity'yi korur
- source geometry'yi değiştirmez
- semantic class atar
- narrative product priority atar

### Urban block integration

Mevcut `AtlasUrbanBlockProfile.composition_lod_level` contract'ı korunur.

`resolve_urban_block_profile(...)`:

- block density
- nearest landmark distance
- existing composition LoD level

bilgisini kullanarak urban block için city-composition kararı üretebilir.

Urban Block Resolver yeniden yazılmamıştır.

### Vegetation composition

Mevcut vegetation architecture korunur:

- isolated trees
- tree rows
- controlled clusters
- forest canopies

City Composition LoD:

- tree row için `generalized_row`
- dense urban vegetation için `canopy_or_cluster`
- uygun daha açık morphology için `source_detail`

representation kararları üretebilir.

Yeni vegetation geometry engine oluşturulmamıştır.

### Major city structure preservation

Scene-level acceptance testleri aynı sahnede:

- landmark
- railway
- park
- water

yapılarının korunabildiğini,

generic / isolated building background'un sadeleştirme adayı olduğunu ve minor
detail'in suppress edilebildiğini doğrular.

Narrative priority sırası major city structure lehine korunur.

### Road source provenance

8.14 final STL application için road mesh provenance eksikliği kapatıldı.

`AtlasRoadFoundationBuilder` artık road mesh'e:

- `source_id`

metadata'sını koruyarak aktarır.

Bu değişiklik geometry veya road hierarchy davranışını değiştirmez.

### Final mesh application

`AtlasCityCompositionMeshFilter` source identity üzerinden final mesh
gruplarına composition kararlarını uygular.

Şu gruplar source identity ile eşleştirilebilir:

- roads
- buildings
- parks
- waters
- landmarks

`retain=False` kararı verilen source mesh final product composition'dan
çıkarılabilir.

Unmapped veya unrelated mesh grupları korunur.

### FoundationFirst production wiring

`AtlasFoundationFirstEngine.generate_city_stl()` yeni optional context alır:

- `city_composition_lod_level`
- `scene_morphology`

City Composition LoD opt-in'dir.

`city_composition_lod_level=None` olduğunda legacy STL composition davranışı
korunur.

Context aktif olduğunda production zinciri:

`FoundationFirst source collections`
→ `AtlasCityCompositionSceneAdapter`
→ `AtlasUrbanFabricScene`
→ `AtlasCityCompositionLoDResolver`
→ `AtlasCityCompositionMeshFilter`
→ final mesh assembly
→ `AtlasSTLWriter`

şeklindedir.

Composition filter artık STL yazımından **önce** çalışır.

Runtime regression, düşük LoD / küçük dense-urban ürün context'inde minor
pedestrian source mesh'inin gerçek final STL mesh listesinden çıkarıldığını
doğrular.

Result metadata ayrıca:

- `city_composition_scene`
- `city_composition_lod`
- `city_composition_suppressed_meshes`

bilgilerini taşır.

### Roadmap acceptance sonucu

8.14 kapsamında doğrulanan davranışlar:

- landmarks retain higher narrative priority
- generic urban fabric can be marked for simplification
- minor paths can be suppressed at constrained product scale
- major road hierarchy receives higher narrative priority
- tree rows can receive generalized-row composition decisions
- excessive dense vegetation can receive canopy/cluster decisions
- isolated buildings can receive simplified-mass decisions
- important railway corridors remain protected
- major park and water structure remain protected
- product scale affects composition
- morphology affects composition
- landmark proximity affects composition
- printability affects composition
- existing ATLAS LoD architecture is reused
- final STL composition can be changed by City Composition LoD

### Doğrulama

8.14 focused / production wiring regression:

- `44 passed in 0.09s`

8.14 real FoundationFirst runtime suppression regression:

- `6 passed in 0.15s`

Expanded related regression:

- `193 passed in 0.34s`

Full ATLAS regression:

- `3549 passed in 14.66s`

8.14 kapsamında açık blocker kalmadı.

**Sıradaki roadmap paketi: 8.15.**


## 10 Ağustos 2026 — 8.15 FINAL LOCK

**8.15 Scene Morphology Classifier: LOCK**

8.15, product scene'in dominant urban / landscape karakterini deterministic ve
evidence-driven biçimde sınıflandıran genel morphology katmanı olarak
tamamlandı.

Yeni ana bileşenler:

- `CORE/atlas_scene_morphology_classifier.py`
- `CORE/atlas_scene_morphology_evidence_resolver.py`
- `CORE/atlas_scene_morphology_mesh_area_resolver.py`

### Temel 8.15 ilkesi

Classifier location identity kullanmaz.

Özellikle:

- şehir adı
- landmark adı
- lokasyon shortcut'ı
- hard-coded geographic identity

classification girdisi değildir.

Sistem scene morphology'yi kaynak evidence üzerinden çözer.

Primary acceptance principle:

> Two geographically different areas with similar morphology should resolve to
> similar composition behavior.

### Initial morphology classes

Desteklenen morphology sınıfları:

- `dense_urban`
- `historic_core`
- `suburban`
- `rural`
- `forest`
- `river_city`
- `coastal`
- `mountain`
- `mixed`

### Evidence contract

Classifier şu normalized evidence alanlarını kullanabilir:

- building density
- road density
- block compactness
- vegetation coverage
- forest coverage
- water coverage
- railway presence
- terrain relief
- landmark density

Evidence değerleri deterministic olarak normalize edilir.

### Scene Morphology Evidence Resolver

`AtlasSceneMorphologyEvidenceResolver` fiziksel/product scene ölçülerini
classifier contract'ına dönüştürür.

Desteklenen production ölçüleri:

- product area
- building projected footprint area
- road projected surface area
- vegetation projected area
- forest projected area
- water projected area
- railway count
- terrain relief
- terrain reference height
- landmark count
- building count
- existing urban block density profiles

Urban Block Resolver yeniden yazılmamıştır.

Mevcut `AtlasUrbanBlockProfile.density_ratio` değerleri block compactness
evidence olarak reuse edilebilir.

### Projected XY area resolver

Morphology coverage hesabında raw triangle-area toplamı kullanılmaz.

Yeni:

- `AtlasSceneMorphologyMeshAreaResolver`

mesh triangle'larının XY projection'ını polygon olarak çözer ve Shapely union
üzerinden gerçek projected footprint alanını hesaplar.

Bu sayede kapalı solid meshlerde aynı footprint'i temsil eden:

- top surface
- bottom surface

ayrı ayrı sayılmaz.

Overlapping XY projection deterministic olarak tek footprint alanına
dissolve edilir.

### Classification scoring

Classifier semantic/evidence scoring kullanır.

Örneğin:

- yüksek building + road + compact block → `dense_urban`
- yüksek forest coverage → `forest`
- güçlü water dominance + urban fabric → `river_city`
- düşük building / road ve açık vegetation → `rural`
- yüksek terrain relief → `mountain`

Water-dominance scoring gerçek normalized coverage evidence'ına dayanır;
location-specific waterbody veya city shortcut'ı kullanılmaz.

### Determinism

Aynı evidence girdisi tekrar verildiğinde aynı morphology sonucu üretilir.

Tie / weak-dominance durumlarında `mixed` kullanılabilir.

Result ayrıca:

- resolved morphology
- confidence
- per-class scores
- normalized evidence

bilgilerini taşır.

### FoundationFirst production integration

`AtlasFoundationFirstEngine.generate_city_stl()` artık final composition
öncesindeki scene mesh gruplarından morphology evidence üretir.

Production zinciri:

`FoundationFirst source data`
→ scene meshes
→ projected XY morphology measurements
→ normalized morphology evidence
→ `AtlasSceneMorphologyClassifier`
→ `resolved_scene_morphology`

şeklindedir.

Result metadata artık şunları taşır:

- `scene_morphology_evidence`
- `scene_morphology_classification`
- `resolved_scene_morphology`
- `effective_scene_morphology`

### Explicit morphology override

Mevcut public:

- `scene_morphology`

parametresi korunur.

Explicit morphology verilirse classifier sonucu metadata'da yine hesaplanır,
ancak composition için explicit değer kullanılır.

Helper:

- `_select_scene_morphology(...)`

şu davranışı kilitler:

`explicit morphology`
→ varsa preserve

aksi durumda:

`classified morphology`
→ effective morphology

### City Composition LoD integration

8.15, mevcut 8.14 City Composition LoD mimarisini yeniden yazmaz.

Doğru production sırası artık:

`mesh groups`
→ morphology evidence
→ morphology classifier
→ effective morphology
→ City Composition LoD
→ City Composition Mesh Filter
→ final STL

şeklindedir.

8.14'ten kalan eski:

`city_composition_lod_level provided`
→ `scene_morphology explicitly required`

guard'ı kaldırıldı.

Böylece:

`scene_morphology=None`
→ automatic classifier
→ effective morphology
→ existing City Composition LoD

zinciri production runtime'da çalışır.

Explicit `scene_morphology` verilmişse mevcut override behavior korunur.

### Compatibility cleanup

8.15 geliştirmesi sırasında 8.14'ten kalan geç City Composition metadata
recalculation bloğu tespit edildi ve kaldırıldı.

City Composition resolution artık yalnız doğru yerde:

- final mesh filtering öncesinde

çalışır.

### Roadmap acceptance sonucu

8.15 kapsamında doğrulanan davranışlar:

- deterministic morphology classification
- evidence-driven classification
- no location-name shortcuts
- building density evidence
- road density evidence
- block compactness evidence contract
- vegetation coverage evidence
- forest coverage evidence
- water coverage evidence
- railway presence evidence
- terrain relief evidence
- landmark density evidence
- projected-area double-count prevention
- explicit morphology override preservation
- automatic morphology resolution
- automatic 8.14 City Composition LoD integration

Primary acceptance principle karşılandı:

> Two geographically different areas with similar morphology should resolve to
> similar composition behavior.

### Doğrulama

8.15 morphology core + production integration:

- `27 passed in 0.21s`

Expanded related regression:

- `105 passed in 0.27s`

Full ATLAS regression:

- `3570 passed in 15.07s`

8.15 kapsamında açık blocker kalmadı.

**Sıradaki roadmap paketi: 8.16 — Morphology Composition Policy.**


## 10 Ağustos 2026 — 8.16 FINAL LOCK

**8.16 Morphology Composition Policy: LOCK**

8.16, 8.15 tarafından çözülen scene morphology bilgisini product-level
composition emphasis policy'ye dönüştüren deterministic ve profile-driven
katman olarak tamamlandı.

Yeni ana bileşen:

- `CORE/atlas_morphology_composition_policy.py`

### Temel 8.16 ilkesi

Morphology Composition Policy source truth'ü değiştirmez.

Policy:

- source geometry'yi yeniden yazmaz
- OSM semantic truth'ü değiştirmez
- landmark identity değiştirmez
- yeni paralel LoD sistemi oluşturmaz

Yalnız mevcut product composition zincirinde semantic katmanların relative
emphasis değerlerini çözer.

Primary acceptance principle:

> Scene composition should reflect the dominant physical character of the
> place instead of applying one universal visual recipe everywhere.

### Named morphology profiles

Deterministic named profiller:

- `dense_urban`
- `historic_core`
- `suburban`
- `forest`
- `rural`
- `river_city`
- `coastal`
- `mountain`
- `mixed`

Policy şu semantic emphasis alanlarını üretir:

- `terrain_emphasis`
- `road_emphasis`
- `urban_block_emphasis`
- `vegetation_emphasis`
- `water_emphasis`
- `infrastructure_emphasis`
- `landmark_emphasis`

### Morphology davranışı

`dense_urban`:
- terrain prominence düşürülür
- road hierarchy ve urban-block readability güçlendirilir
- vegetation clutter sınırlandırılır
- important infrastructure ve landmark dominance korunur

`historic_core`:
- street structure ve compact urban fabric güçlendirilir
- landmark emphasis maksimum tutulur
- generic vegetation ve terrain prominence sınırlandırılır

`suburban`:
- buildings, roads, vegetation ve moderate terrain dengelenir

`forest`:
- canopy / vegetation en yüksek emphasis'i alır
- terrain güçlü tutulur
- urban-block prominence azaltılır
- önemli paths / roads korunur

`rural`:
- terrain ve landcover structure öne çıkarılır
- gereksiz urban-style detail azaltılır
- settlement structure korunur

`river_city` / `coastal`:
- water emphasis maksimumdur
- shoreline / bridge / embankment / waterfront infrastructure için
  infrastructure emphasis yüksektir

`mountain`:
- terrain dominance maksimumdur
- secondary urban detail daha düşük emphasis alır

### Mixed morphology

`mixed` universal sabit recipe kullanmaz.

`scene_evidence` mevcutsa:

- building density
- road density
- block compactness
- vegetation coverage
- forest coverage
- water coverage
- railway presence
- terrain relief
- landmark density

üzerinden deterministic evidence blend üretilir.

Result:

- named morphology → `profile_source = named_profile`
- mixed evidence blend → `profile_source = evidence_blend`

Evidence yoksa safe named-profile fallback korunur.

### City Composition LoD integration

8.16 mevcut `AtlasCityCompositionLoDResolver` mimarisini reuse eder.

`composition_policy` opsiyonel olarak:

- `resolve(...)`
- `resolve_scene(...)`
- `resolve_urban_fabric_scene(...)`

zincirinden geçirilir.

`composition_policy=None` olduğunda legacy 8.14 behavior korunur.

Semantic mapping:

- terrain → terrain emphasis
- roads / paths → road emphasis
- urban block / generic building / isolated building → urban-block emphasis
- tree row / vegetation / park → vegetation emphasis
- water → water emphasis
- railway / light rail / tram / infrastructure corridor → infrastructure emphasis
- landmark → landmark emphasis

Existing semantic narrative priority korunur.

Morphology policy base narrative priority üzerinde relative emphasis uygular.

Decision metadata artık:

- `composition_emphasis`

alanını da taşır.

### FoundationFirst production wiring

Production zinciri:

`scene evidence`
→ `resolved_scene_morphology`
→ `effective_scene_morphology`
→ `AtlasMorphologyCompositionPolicy`
→ `morphology_composition_policy`
→ `AtlasCityCompositionLoDResolver`
→ narrative priority decisions
→ existing City Composition Mesh Filter
→ final STL

şeklindedir.

Result metadata ayrıca:

- `morphology_composition_policy`

bilgisini taşır.

### Source truth preservation

8.16 kapsamında:

- source feature existence değiştirilmez
- source geometry yeniden üretilmez
- OSM semantic classification değiştirilmez
- location-specific shortcut kullanılmaz
- morphology yalnız relative product emphasis üretir

### Doğrulama

8.16 policy + City Composition integration:

- `43 passed in 0.07s`

Expanded related regression:

- `82 passed in 0.35s`

Full ATLAS regression:

- `3590 passed in 15.09s`

8.16 kapsamında açık blocker kalmadı.

**Sıradaki roadmap paketi: 8.17 — Semantic Color / Material Hierarchy.**


## 10 Ağustos 2026 — 8.17 FINAL LOCK

**8.17 Semantic Color / Material Hierarchy: LOCK**

8.17, urban product scene içinde renk ve fiziksel material kullanımını yalnız
dekorasyon olarak değil, semantic scene hierarchy'nin üretim katmanı olarak
çözen sistem olarak tamamlandı.

Yeni ana bileşen:

- `CORE/atlas_semantic_material_hierarchy.py`

Güncellenen ana production bileşenleri:

- `CORE/atlas_product_color_preview_renderer.py`
- `CORE/atlas_wall_collection_multicolor_stl_exporter.py`

### Temel 8.17 ilkesi

Color / material hierarchy semantic role üzerinden tanımlanır.

Fiziksel filament rengi semantic identity değildir.

Örneğin aynı fiziksel beyaz material şu semantic rolleri aynı anda
taşıyabilir:

- generic building
- terrain
- roads / hardscape
- label plate

Bu roller aynı RGB / filament altında birleşse bile semantic kimliklerini
kaybetmez.

Primary acceptance principle:

> Materials should reinforce scene hierarchy while preserving ATLAS product
> identity and production constraints.

### Semantic material roles

İlk product-level hierarchy şu rolleri destekler:

- `generic_building`
- `generic_building_roof`
- `landmark_wall`
- `landmark_roof`
- `vegetation`
- `water`
- `roads_hardscape`
- `terrain`
- `frame`
- `label_plate`
- `label_text`

Generic building roof ile landmark roof semantic olarak ayrı rollerdir.

Aynı fiziksel roof material'ını paylaşmaları mümkündür.

### Existing material profiles preserved

8.17 mevcut:

- `AtlasProductPreviewMaterialProfile`

altyapısını yeniden yazmaz.

Mevcut product profile RGB değerleri reuse edilir.

Özellikle:

- `KOELN_PREMIUM_V1`
- `DALYAN_KAUNOS_PREMIUM_V1`
- existing comparison / preview profiles

korunur.

Lichtbild veya başka competitor palette'i production standardı olarak
hard-code edilmemiştir.

### Physical material grouping

Semantic role ile physical material birbirinden ayrılmıştır.

Her semantic role:

- semantic role
- RGB
- physical material
- surface treatment
- relief priority
- readability priority

metadata'sını taşıyabilir.

Aynı RGB kullanan semantic roller aynı physical material altında birleşebilir.

### Readability contract

Birden fazla semantic role aynı fiziksel filament rengini kullandığında
readability yalnız renk farkına bağlı değildir.

Hierarchy ayrıca:

- `surface_treatment`
- `relief_priority`
- `readability_priority`

contract'larını taşır.

Örneğin:

- terrain → terrain relief treatment
- roads → hardscape linear treatment
- generic building → building mass treatment
- landmark wall → landmark wall treatment
- landmark roof → landmark roof treatment
- vegetation → vegetation texture
- water → water surface

gibi semantic presentation davranışları ayrıdır.

Landmark wall / roof readability priority değerleri generic building
counterpart'larından daha yüksektir.

### Preview integration

`AtlasProductColorPreviewRenderer.build_scene()` artık semantic material
hierarchy üretir.

Preview result:

- `semantic_material_hierarchy`

metadata'sını taşır.

Material batches ayrıca:

- `semantic_role`
- `physical_material`
- `surface_treatment`
- `relief_priority`
- `readability_priority`

alanlarını taşır.

Preview renderer fiziksel AMS / filament limitini kendi başına zorlamaz.

Bu ayrım kasıtlıdır:

- digital preview semantic/material richness gösterebilir
- physical production limit ayrı production boundary'de uygulanır

### Preview batch semantic mapping

Mevcut preview batch contract şu semantic rollere bağlandı:

- `frame` → frame
- `terrain` → terrain
- `buildings` / `building_walls` → generic building
- `building_roofs` → generic building roof
- `landmarks` → landmark wall
- `roads` → roads / hardscape
- `parks` / `trees` → vegetation
- `water` → water
- `label_plate` → label plate
- `label_text` → label text

### Multicolor exporter semantic provenance

`AtlasWallCollectionMulticolorSTLExporter` artık fiziksel STL part metadata'sında:

- source batches
- semantic roles
- physical material
- RGB

bilgilerini korur.

Bu sayede fiziksel olarak aynı STL / filament altında birleştirilen semantic
roller production provenance içinde kaybolmaz.

### Profile-driven physical grouping

Exporter artık yalnız:

`batch name → hard-coded color name`

mantığına bağımlı değildir.

Bir material batch explicit:

- `physical_material`

taşıyorsa fiziksel grouping bu identity üzerinden yapılır.

Bu sayede farklı product family / production profile'ları kendi material
stratejilerini kullanabilir.

Legacy scene metadata'sında `physical_material` yoksa mevcut batch/color
behavior korunur.

### Köln Premium V1 compatibility

Mevcut Köln Premium V1 production hattı korunmuştur.

Legacy fiziksel renk stratejisi:

- white
- red
- green
- black
- blue

çalışmaya devam eder.

Mevcut multicolor STL filename / grouping behavior için backward compatibility
korunmuştur.

### Production physical color limit

Preview ve production color constraint ayrılmıştır.

`AtlasWallCollectionMulticolorSTLExporter.export_scene(...)` artık opsiyonel:

- `maximum_physical_color_count`

production constraint'ını destekler.

Limit verilirse physical STL part sayısı export başlamadan önce doğrulanır.

Limit aşılırsa export reddedilir.

Limit içindeki paketler:

- `physical_color_count`
- `maximum_physical_color_count`

metadata'sını taşır.

Legacy caller'lar için limit verilmezse mevcut behavior korunur.

### Source / semantic truth preservation

8.17:

- source geometry'yi değiştirmez
- OSM semantics'i değiştirmez
- morphology classification'ı değiştirmez
- City Composition LoD kararlarını değiştirmez

Yalnız bu semantic product hierarchy'nin preview ve physical material
representation katmanını tanımlar.

### Roadmap acceptance sonucu

8.17 kapsamında doğrulanan davranışlar:

- product-level semantic material roles
- generic building / landmark semantic distinction
- generic roof / landmark roof distinction
- configurable product material profiles
- no Lichtbild palette hard-code
- shared physical filament with preserved semantic identity
- surface-treatment readability contract
- relief-priority contract
- readability-priority contract
- preview semantic hierarchy metadata
- preview material-batch semantic metadata
- multicolor semantic provenance
- profile-driven physical material grouping
- legacy Köln Premium V1 compatibility
- configurable production physical color limit

Primary acceptance principle karşılandı:

> Materials should reinforce scene hierarchy while preserving ATLAS product
> identity and production constraints.

### Doğrulama

8.17 focused core / preview / exporter:

- `42 passed in 0.17s`

Expanded related regression:

- `84 passed in 0.24s`

Full ATLAS regression:

- `3603 passed in 15.30s`

8.17 kapsamında açık blocker kalmadı.

**Sıradaki roadmap paketi: 8.18 — Customer Preview Parity.**


## 10 Ağustos 2026 — 8.18 FINAL LOCK

**8.18 Customer Preview Parity: LOCK**

8.18, customer-facing preview ile physical production scene arasında semantic
composition parity sağlayan ve bu parity'yi read-only olarak doğrulayan katman
olarak tamamlandı.

Yeni ana bileşen:

- `CORE/atlas_customer_preview_parity.py`

Güncellenen preview bileşenleri:

- `CORE/atlas_product_color_preview_renderer.py`
- `CORE/atlas_product_color_preview_png_renderer.py`

### Temel 8.18 ilkesi

Customer preview ayrı bir scene composition sistemi kullanmaz.

Preview:

- production geometry'yi yeniden üretmez
- morphology'yi yeniden çözmez
- City Composition LoD kararlarını yeniden hesaplamaz
- suppressed geometry'yi geri getirmez
- production material hierarchy'den bağımsız yeni semantic hierarchy üretmez

Production tarafında çözülen scene hierarchy preview tarafından reuse edilir.

Primary acceptance principle:

> The customer should receive a physical product whose composition matches the
> scene hierarchy shown in the preview.

### Shared production scene

Mevcut Wall Collection akışında aynı:

- `city_result`

hem physical product export'una hem customer color preview renderer'a verilir.

Bu sayede preview temel geometry kaynağı production scene ile aynıdır.

Preview renderer doğrudan:

- `city_result["mesh_groups"]`

üzerinden çalışır.

City Composition Mesh Filter tarafından production için suppression uygulanmış
geometry preview tarafından yeniden eklenmez.

### Production composition metadata passthrough

Preview scene artık production result içindeki şu metadata'yı aynen taşır:

- `resolved_scene_morphology`
- `effective_scene_morphology`
- `morphology_composition_policy`
- `city_composition_lod`
- `city_composition_suppressed_meshes`

Bu alanlar preview tarafında yeniden hesaplanmaz.

### Production-filtered geometry parity

Davranış testiyle doğrulandı:

- retained production mesh preview'de bulunur
- suppressed production mesh preview'de bulunmaz
- City Composition LoD'da retain=false olan fakat final mesh_groups içinde
  bulunmayan geometry preview tarafından geri oluşturulmaz

Bu özellikle road / generic urban detail suppression parity'sini korur.

### Product-size awareness

Preview scene zaten:

- outer width
- outer height
- opening width
- opening height

bilgilerini taşır.

City Composition LoD içindeki:

- `product_size_mm`

ile preview opening size parity resolver tarafından karşılaştırılabilir.

### Consistent camera framing

Mevcut PNG preview camera davranışı değiştirilmeden contract haline getirildi.

Camera:

- elevation: `58.0°`
- azimuth: `-58.0°`

olarak deterministic kalır.

Framing doğrudan product outer dimensions üzerinden çözülür:

- x min/max
- y min/max
- outer width
- outer height

PNG result metadata artık:

- `camera`
- `framing`

alanlarını taşır.

Bu sayede aynı product geometry için framing davranışı test edilebilir ve
tekrarlanabilir hale geldi.

### Semantic material parity

8.17 Semantic Color / Material Hierarchy doğrudan reuse edilir.

Preview scene:

- `semantic_material_hierarchy`

metadata'sını taşımaya devam eder.

Customer Preview Parity resolver gerekli temel semantic rollerin preview
hierarchy içinde bulunduğunu doğrulayabilir:

- generic building
- landmark wall
- vegetation
- water
- roads / hardscape
- terrain

Yeni parallel material resolver oluşturulmamıştır.

### Landmark / building highlighting parity

Mevcut highlight sistemi korunmuştur.

Preview yalnız production-filtered mesh_groups içinde gerçekten bulunan:

- building
- building component
- landmark

geometry'sini highlight edebilir.

Requested fakat production scene içinde bulunmayan / suppressed edilmiş
landmark preview'ye eklenmez.

Preview result artık:

- requested building source IDs
- applied building source IDs
- requested landmark IDs
- applied landmark IDs

bilgilerini `highlighting` metadata'sında taşır.

Böylece customer preview'nin production scene'de olmayan bir landmark'ı
highlight ederek yanlış vaat vermesi engellenir.

### Customer Preview Parity resolver

Yeni:

- `AtlasCustomerPreviewParity`

read-only parity resolver olarak eklendi.

Resolver production result ile preview scene arasında şu kontrolleri yapar:

- scene morphology parity
- morphology composition policy parity
- City Composition LoD parity
- suppressed mesh count parity
- product-size parity
- required semantic material role coverage

Resolver geometry veya metadata değiştirmez.

Result:

- `matches`
- `checks`
- `mismatches`

alanlarını taşır.

### LoD parity

Preview, production:

- `city_composition_lod`

metadata'sını doğrudan taşır.

Parity resolver LoD kararlarının preview tarafında değiştirilip
değiştirilmediğini tespit eder.

Örneğin production'da:

- retain=true

olan road preview metadata'sında:

- retain=false

olarak değiştirilirse parity başarısız olur.

### Morphology composition parity

Production:

- `effective_scene_morphology`
- `morphology_composition_policy`

preview tarafından aynen taşınır.

Road emphasis, landmark emphasis, terrain emphasis, vegetation emphasis,
water emphasis ve diğer 8.16 policy değerlerinde preview-side sapma parity
failure olarak raporlanabilir.

### Rendering-specific freedom

8.18 rendering-specific visual teknikleri yasaklamaz.

Preview renderer:

- camera
- lighting
- background
- raster rendering

gibi presentation teknikleri kullanabilir.

Ancak bunlar production'da olmayan:

- geometry
- hierarchy
- semantic importance
- LoD detail
- material role

vaat edemez.

### Roadmap acceptance sonucu

8.18 kapsamında doğrulanan davranışlar:

- same production scene source
- production-filtered geometry reuse
- no suppressed-geometry reintroduction
- morphology metadata parity
- morphology composition policy parity
- City Composition LoD parity
- product-size awareness
- semantic material hierarchy parity
- landmark / building highlight provenance
- suppressed highlight protection
- deterministic camera
- product-aware framing
- read-only centralized parity validation
- real preview renderer output accepted by parity resolver

Primary acceptance principle karşılandı:

> The customer should receive a physical product whose composition matches the
> scene hierarchy shown in the preview.

### Doğrulama

8.18 focused customer preview parity:

- `51 passed in 0.29s`

Expanded related regression:

- `118 passed in 0.35s`

Full ATLAS regression:

- `3611 passed in 15.17s`

8.18 kapsamında açık blocker kalmadı.

## 8.19 — Urban Fabric Quality Report — LOCK

Urban Fabric kompozisyonunun yalnız görsel incelemeye bağlı kalmadan,
deterministik ve tekrar üretilebilir kalite metrikleriyle ölçülmesi için:

- `CORE/atlas_urban_fabric_quality_report.py`
- `Test/test_urban_fabric_quality_report.py`
- `Test/test_foundation_first_urban_fabric_quality_report_wiring.py`

eklendi.

### Read-only quality report contract

Yeni:

- `AtlasUrbanFabricQualityReport`

final production scene/result üzerinde read-only kalite raporu üretir.

Rapor:

- geometry değiştirmez
- feature suppress etmez
- building height normalize etmez
- LoD kararı değiştirmez
- material assignment değiştirmez

Aynı scene input için deterministik sonuç üretir.

### Morphology ve composition metrikleri

Mevcut production metadata reuse edilerek raporlanan temel metrikler:

- building density
- road density
- block compactness
- vegetation coverage
- forest coverage
- water coverage
- railway presence
- terrain relief
- landmark density

Bu değerler yeni paralel analiz sistemiyle yeniden hesaplanmaz;
mevcut scene morphology evidence source-of-truth olarak kullanılır.

### City Composition LoD istatistikleri

`city_composition_lod` kararlarından:

- decision count
- retained count / ratio
- suppressed count / ratio
- simplified count / ratio

ölçülür.

### Vegetation composition quality

Mevcut vegetation composition metadata üzerinden:

- isolated tree count
- tree-row count
- forest canopy count
- tree-row member count
- vegetation mode distribution
- isolated-tree clutter ratio

raporlanır.

### Building height quality

Mevcut building-height normalization metadata üzerinden:

- `building_height_outlier_count`

ölçülür.

Yeni height normalizer veya ikinci bir outlier sistemi oluşturulmamıştır.

### Terrain prominence

Mevcut morphology composition policy içindeki:

- `terrain_emphasis`

değeri:

- `terrain_prominence_ratio`

olarak quality report'a taşınır.

### Landmark-to-background prominence

City Composition LoD içindeki mevcut:

- semantic class
- narrative priority

metadata reuse edilerek:

- landmark narrative priority
- background narrative priority
- landmark-to-background prominence ratio

hesaplanır.

### Road continuity

Final production result'a attach edilen:

- `bridge_urban_integration`

kayıtlarından:

- bridge record count
- continuous bridge count
- major-road continuity ratio

ölçülür.

Approach-road continuity mevcut production geometry/integration
metadata'sından okunur; quality report geometry oluşturmaz.

### Water completeness ve continuity

Final production result içindeki:

- `water_shoreline_composition`

kayıtlarından:

- composition record count
- continuous surface record count
- water completeness ratio

ölçülür.

`supports_water_surface_continuity` mevcut shoreline composition
contract'ından doğrudan reuse edilir.

### Road hierarchy coverage

Final:

- `city_composition_scene`

içindeki gerçek semantic class kayıtlarından:

- major-road count
- local-road count
- service-road count
- pedestrian-path count
- represented hierarchy class count
- road hierarchy coverage ratio

ölçülür.

### Semantic surface coverage

Final park meshleri üzerinde mevcut:

- `semantic_surface_texture`

metadata'sı kullanılarak:

- eligible surface count
- textured surface count
- semantic surface coverage ratio

hesaplanır.

### Forest continuity signal

Final:

- `mesh_groups["forest_canopies"]`

üzerinden:

- forest canopy mesh count
- forest canopy presence

raporlanır.

Gerçek production contract henüz daha güçlü bir forest-continuity oranı
taşımadığı için sahte bir continuity ratio üretilmemiştir.

### Issue reporting

Quality report iki temel problem sınıfını ayırt eder:

- missing semantic content
- visually weak but technically present content

Doğrulanan issue örnekleri:

- missing park content
- missing water content
- missing railway content
- weak road presence
- weak vegetation presence
- weak major-road continuity
- weak water-surface continuity

### Production wiring

`AtlasFoundationFirstEngine.generate_city_stl()` final result zincirine
quality report bağlandı.

Sıra:

- production scene oluşturulur
- City Composition LoD uygulanır
- bridge urban integration metadata eklenir
- water / shoreline composition metadata eklenir
- castle semantic architecture tamamlanır
- `AtlasUrbanFabricQualityReport.build(scene_result=result)` çağrılır
- final result içinde `urban_fabric_quality_report` döner

Böylece report ara veya eksik scene'i değil, final production result'ı ölçer.

Mevcut water/shoreline FoundationFirst fixture'ı quality-report build
aşamasına kadar genişletildi ve gerçek final-result metadata akışı
davranışsal olarak doğrulandı.

### Bilinçli kapsam sınırı

Roadmap'te candidate metric olarak bulunan:

- urban-block continuity

şu anda final FoundationFirst `city_composition_scene` içine gerçek
urban-block profile/relationship metadata'sı taşınmadığı için uydurma bir
metrikle raporlanmamıştır.

Aynı prensip daha güçlü forest continuity ölçümü için de uygulanmıştır:
source-of-truth production metadata yoksa heuristic kalite metriği
icat edilmemiştir.

### Roadmap acceptance sonucu

8.19 kapsamında doğrulanan temel davranış:

> Urban Fabric quality must become measurable enough that regressions can be
> detected before relying only on visual inspection.

Quality report artık final production scene üzerinde objektif,
deterministik ve read-only ölçümler üretmektedir.

### Doğrulama

Focused Urban Fabric Quality Report:

- `14 passed in 0.02s`

FoundationFirst behavior / wiring:

- `23 passed in 0.26s`

Expanded related regression:

- `103 passed in 0.30s`

Full ATLAS regression:

- `3629 passed in 15.25s`

8.19 kapsamında açık blocker kalmadı.

## 8.20 — Multi-Morphology Acceptance Benchmarks — LOCK

Urban Fabric & Product Composition V1'in son acceptance paketi
tamamlandı.

Amaç Bonn üzerinde çalışan sistemleri Bonn'a özel kabul etmek değil,
aynı genel production mimarisinin birbirinden belirgin biçimde farklı
şehir ve peyzaj morfolojilerinde doğru davranmasını kanıtlamaktı.

### Acceptance mimarisi

Fresh doğrulamalar eski STL çıktıları reuse edilmeden güncel:

`FoundationFirst → morphology evidence/classification → morphology
composition policy → City Composition LoD → quality report`

production zincirinden yeniden üretildi.

Lokasyon adı veya coordinate-specific exception classifier/policy
girdisi olarak kullanılmadı.

### Fresh production acceptance matrix

Beş zorunlu morfoloji ailesi gerçek source verisiyle yeniden üretildi:

| Scene | Accepted morphology | Confidence | Final building topology |
|---|---:|---:|---:|
| Galata Tower | `dense_urban` | 0.515931 | 0 invalid / 0 open / 0 non-manifold |
| Sultanahmet | `historic_core` | 0.492700 | 0 invalid / 0 open / 0 non-manifold |
| Galata Bridge | `river_city` | 0.795935 | 0 invalid / 0 open / 0 non-manifold |
| Real WorldCover forest fixture | `forest` | 0.794195 | 0 invalid / 0 open / 0 non-manifold |
| Erkelenz Reeser Straße | `rural` | 0.470798 | 0 invalid / 0 open / 0 non-manifold |

Sonuç:

**5/5 required morphology families passed.**

Fresh üretim triangle sonuçları:

- Galata Tower: `18,490`
- Sultanahmet: `65,996`
- Galata Bridge: `51,534`
- forest fixture: `12,364`
- Erkelenz: `21,052`

Bunlar audit kanıtıdır; exact triangle sayıları kalıcı regression
contract'ında kırılgan acceptance şartı yapılmamıştır.

### Steinbach kararı

WorldCover surface düzeltmesinden sonra Steinbach'ın gerçek vegetation /
forest evidence'i yükseldi ve sahne artık `rural` yerine `mixed`
çözülmektedir.

Classifier Steinbach'ı zorla `rural` yapmak için değiştirilmedi.

Bu, 8.20'nin overfit önleme ilkesine uygun olarak kabul edildi.
Gerçek production zincirinde kararlı biçimde `rural` kalan Erkelenz,
rural acceptance benchmark'ı olarak kullanıldı.

### 8.20 sırasında bulunan ve genel mimaride kapatılan production açıkları

1. **Geçersiz source building level değeri**

   `building:levels=0` daha önce `0.0 m` height üretip downstream product
   normalization'ı bozabiliyordu.

   Non-positive level değerleri artık geçerli kat yüksekliği olarak
   kullanılmıyor ve mevcut building-type/default height fallback zincirine
   düşüyor.

2. **Gerçek urban-block profile'larının morphology zincirinde kaybolması**

   Building-height context resolver gerçek road-defined block profile'larını
   zaten üretiyor fakat FoundationFirst morphology evidence'e taşımıyordu.

   Resolver backward-compatible biçimde profile-aware sonuç verecek şekilde
   genişletildi ve FoundationFirst gerçek block profile'larını morphology
   evidence resolver'a bağladı.

3. **Morphology classifier acceptance coverage açığı**

   `historic_core` ve `suburban` için canonical acceptance coverage eklendi
   ve scoring genel morphology sinyalleri üzerinden yeniden dengelendi.

   Lokasyon ismi veya coordinate-specific rule eklenmedi.

4. **WorldCover polygon-hole veri kaybı**

   `AtlasWorldCoverSurfaceAggregator.dissolve()` içinde interior ring taşıyan
   polygonların tamamı discard ediliyordu.

   Gerçek forest fixture'da 17,030 WorldCover tree-cover hücresinin yalnız
   37'si korunuyor, yaklaşık `%99.78` source evidence kayboluyordu.

   Hole içeren connected component'ler artık gerçek source cell merkezleri
   üzerinden deterministik, hole-free surface parçalarına ayrılıyor.

   Aynı fixture'da sonuç:

   - input cells: `17,030`
   - represented cells: `17,030`
   - retained ratio: `1.0`
   - forest morphology confidence: `0.794195`

5. **Post-processing sonrası final building topology gate eksikliği**

   Foundation extrusion topology validation yapmasına rağmen roof / minaret /
   dome / castle post-processing sonrasında mesh tekrar validate edilmeden
   final scene'e eklenebiliyordu.

   İki seviyeli güvenlik kuruldu:

   - invalid topology artık `AtlasFoundationMeshExtruder` sınırında reject edilir;
   - bütün architectural post-processing tamamlandıktan sonra
     `AtlasFoundationSceneBuilder` final building topology'yi yeniden validate
     eder ve invalid mesh'i scene'e kabul etmez.

   Gerçek Sultanahmet doğrulamasında daha önce final scene'de kalan iki invalid
   building mesh kaldırıldı:

   - önce: `2 invalid`, `16 open edges`
   - sonra: `0 invalid`, `0 open edges`, `0 non-manifold edges`

### Kalıcı acceptance regression contract

Yeni:

`Test/test_multi_morphology_acceptance_benchmarks.py`

fresh production audit'inde ölçülen evidence snapshot'larını kullanarak aynı
genel architecture üzerinde:

- deterministic morphology classification
- doğru required morphology family
- morphology composition policy
- distinct composition priorities
- read-only/deterministic Urban Fabric Quality Report parity

davranışlarını kalıcı olarak kilitler.

Required families:

- `dense_urban`
- `historic_core`
- `river_city`
- `forest`
- `rural`

Kalıcı acceptance contract:

- `7 passed in 0.03s`

### Regression doğrulaması

8.20 focused genel düzeltme paketi:

- `68 passed in 0.23s`

Expanded related regression:

- `138 passed in 0.38s`

Full ATLAS regression:

- `3645 passed in 15.23s`

### Roadmap acceptance sonucu

8.20 acceptance, Urban Fabric V1'in Bonn veya tek bir morphology üzerinde
overfit olmadığını gerçek üretim verileriyle doğruladı.

Temel ilke doğrulandı:

> Urban Fabric V1 is complete only when the same general architecture
> improves multiple fundamentally different city and landscape types.

8.20 kapsamında açık teknik blocker kalmadı.

**Urban Fabric & Product Composition V1 — 8.0–8.20 tamamlandı.**

Sonraki ürün/production roadmap paketi ayrı olarak kilitlenecektir.

---

## 8.20 Sonrası Güncel Production Checkpoint — 11 Ağustos 2026

Önceki `c7771ca` checkpoint kaydı artık tarihsel referanstır ve aşağıdaki
durum tarafından supersede edilmiştir.

### Son güvenli ve push edilmiş commit

- Commit: `768fa05c25017d2fa3bf644182f0018d736dc60d`
- Kısa hash: `768fa05`
- Commit mesajı: `Add canonical tree product geometry`
- Branch: `main`
- `HEAD == origin/main`
- Tracked çalışma ağacı temiz

Bilinen unrelated untracked dosyalar:

- `Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-08-01.md`
- `Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-08-04.md`
- `Test/preview_church_semantic_surfaces.py`

Bu dosyalara dokunulmamalı ve toplu stage edilmemelidir.

### 8.20 sonrası tamamlanan commit zinciri

1. `ae129c8` — `Clip roads to product bounds`
2. `9925553` — `Preserve elevated dome part height intervals`
3. `768fa05` — `Add canonical tree product geometry`

### Road boundary clipping

Ürün sınırını kesen gerçek source road geometrileri extrusion öncesinde
product bounds'a clip edilir.

Erkelenz gerçek production doğrulamasında crossing-road geometrileri
korunmuş, final road mesh'ler manifold kalmıştır.

### Elevated dome part height interval düzeltmesi

Elevated architectural dome/building-part geometrilerinde source
`min_height` / yükseklik interval bilgisinin product geometry zincirinde
kaybolması engellenmiştir.

Bu düzeltme genel architectural pipeline seviyesindedir; landmark veya
lokasyon özel kural içermez.

### Canonical Tree V1

Eski ayrı runtime ağaç formları:

- `round`
- `conifer`
- `park_tree_symbol`

ürün hattında tek bir canonical fiziksel ağaç geometrisine indirgenmiştir.

Canonical Tree V1 fiziksel sözleşmesi:

- total height: `2.15 mm`
- trunk height: `0.80 mm`
- trunk diameter: `0.45 mm`
- crown height: `1.35 mm`
- default crown diameter: `1.55 mm`
- minimum cartographic crown diameter: `0.60 mm`
- deterministic geometry
- visible trunk + crown
- terrain-following foundation placement

Explicit source `diameter_crown` mevcutsa Physical Cartographic
Exaggeration Resolver üzerinden fiziksel crown çapına taşınabilir.

### Terrain boundary güvenliği

Tree center'ın yalnız product içine düşmesi artık yeterli değildir.

Canonical crown'un tamamı gerçek terrain XY bounds içinde kalmak zorundadır.
Böylece ürün/terrain dışına taşan ağaç geometrileri final sahneye girmez.

Bonn gerçek sahne doğrulamasında bu clipping sonrası:

- trees: `158`
- forest canopies: `14`

### Canonical tree-row spacing

Tree-row member üretimi artık `tree_kind=canonical` kullanır.

Tree-row spacing fiziksel minimumu:

`canonical crown diameter + nozzle clearance`

olarak uygulanır.

Default `1.55 mm` crown ve `0.40 mm` nozzle için minimum spacing:

- `1.95 mm`

Bu nedenle strict-scale spacing fiziksel crown overlap üretecekse
`enlarge` kararı uygulanır.

### Building exclusion

Canonical tree crown, gerçek building footprint ile çakışıyorsa ağaç final
scene'den çıkarılır.

Building footprint kaynağı doğrudan final building mesh'in `bottom`
geometrisidir; convex-hull tahmini kullanılmaz.

Bonn gerçek scene etkisi:

- trees: `155 -> 153`
- triangles: `65,606 -> 65,126`

### Road exclusion

Canonical tree crown, gerçek road surface ile çakışıyorsa ağaç final
scene'den çıkarılır.

Road mesh `top` verisinin tek polygon olmadığı, her road mesh içinde ardışık
4 noktalı surface segmentlerinin tutulduğu gerçek Bonn probe ile
doğrulanmıştır.

İlk tek-polygon yaklaşımı gerçek sahnede etkisiz kalmıştır.

Düzeltilmiş V2 filtre:

- `top` verisini 4 noktalı road surface segmentlerine ayırır;
- her segmenti ayrı polygon olarak değerlendirir;
- canonical crown radius kadar exclusion uygular.

Bonn gerçek scene V2 etkisi:

- trees: `153 -> 150`
- tree-row members: `36`
- forest canopies: `14`
- triangles: `65,126 -> 64,406`

Görsel doğrulamada road ve building crown overlap problemleri kabul edilebilir
seviyede temizlenmiştir.

### Test doğrulaması

Canonical tree / tree-row / vegetation related regression:

- `71 passed in 0.37s`

Foundation tree-water/building/road filter regression:

- `23 passed in 0.17s`

Full ATLAS regression:

- `3645 passed in 16.20s`

`git diff --check` temizdir.

### Güncel açık vegetation konusu

Canonical Tree V1 ve building/road exclusion tamamlanmıştır.

Açık kalan vegetation konusu artık fiziksel collision değil, kompozisyon ve
forest-canopy temsilidir.

Özellikle:

- bazı tree-row dizilimleri görsel olarak fazla mekanik olabilir;
- mevcut forest-canopy hattı halen gerçek canopy hacmi yerine
  terrain-following semantic surface karakterindedir;
- park / canopy / canonical-tree ilişkisi premium fiziksel ürün görünümü
  açısından ayrı bir sonraki çalışma konusu olarak ele alınmalıdır.

Yeni çalışma bu checkpoint'ten başlatılmalıdır:

`768fa05c25017d2fa3bf644182f0018d736dc60d`

---

## 11 Ağustos 2026 — Rounded Label / Embedded Frame Milestone

### Güncel güvenli checkpoint

- Commit: `c882ab6` — `Embed rounded labels in wall frames`
- `HEAD == origin/main == c882ab6`
- Working tree temiz
- Full regression: `3656 passed in 16.20s`

### Wall Collection label fiziksel standardı

Label sistemi artık ortak Wall Collection çekirdeğinde fiziksel ürün
standardına taşınmıştır.

Global `AtlasLabelPlateSpec` varsayılanı:

- width: `118.0 mm`
- height: `9.0 mm`
- depth: `1.2 mm`
- corner radius: `2.0 mm`

`corner_radius_mm=0.0` açıkça verilerek eski dikdörtgen geometri halen
desteklenmektedir.

### Embedded label / frame recess

`AtlasWallCollectionProductBuilder` ve
`AtlasWallFrameHangerMesher` seviyesinde ortak front recess desteği
eklenmiştir.

Standart recess:

- recess depth: `1.0 mm`
- label plate başlangıç Z: `frame_depth - 1.0 mm`
- `6.0 mm` frame için label plate: `Z 5.0 -> 6.2 mm`
- text/icon yüzeyi: `Z 6.2 -> 6.8 mm`

Rounded label outline ile frame recess outline bire bir aynı geometriyi
kullanır.

Bu davranış lokasyon-özel değildir. Varsayılan `AtlasLabelPlateSpec()`
kullanan Bonn, Köln ve diğer Wall Collection ürünlerine ortak çekirdekten
sirayet eder.

### Doğrulama

Focused label/recess regression:

- `26 passed`

Wall Collection related regression:

- `58 passed`

Full ATLAS regression:

- `3656 passed in 16.20s`

### Recovery güvenliği

14 saatlik 9.0 topology/debug çalışma dalı çalışma ağacına geri
getirilmemiştir.

Safety stash korunmaktadır:

`stash@{0}: On main: SAFETY before rollback to c7771ca 2026-08-11`

Bu stash otomatik olarak apply/drop edilmemelidir.

### Sıradaki iş

Güncel `c882ab6` checkpoint'i üzerinden Bonn Münsterplatz hediye ürünü
yeniden üretilecek ve yeni ortak rounded/embedded label standardı fiziksel
ürün çıktısında doğrulanacaktır.

---

## 12 Ağustos 2026 — Wall Collection Physical Palette / Mola Checkpoint

### Güncel güvenli checkpoint

- Commit: `7f92013` — `Lock shared Wall Collection physical palette`
- `HEAD == origin/main == 7f92013`
- Working tree temiz
- Full regression: `3656 passed in 15.92s`

Önceki ortak rounded/embedded label milestone:

- `c882ab6` — `Embed rounded labels in wall frames`

### Ortak 5 renk fiziksel Wall Collection standardı

Kullanıcının mevcut Bambu Lab PLA Matte filament stoğuna göre ortak fiziksel
palet kilitlenmiştir.

#### BLACK

- outer frame
- roads / hardscape
- label text
- label icon

#### DESERT TAN

- terrain
- generic building walls
- landmark walls
- label plate

#### BRICK RED

- generic building roofs
- landmark roof semantic role

#### DARK GREEN

- parks
- trees
- vegetation
- forest vegetation

#### BLUE

- water

Palette fiziksel olarak en fazla 5 renk kullanır.

Preview RGB contract:

- Black: `(20, 20, 20)`
- Desert Tan: `(205, 190, 160)`
- Brick Red: `(156, 48, 42)`
- Dark Green: `(73, 105, 58)`
- Blue: `(70, 140, 180)`

### Multicolor STL isim standardı

Wall Collection multicolor export artık fiziksel filament isimlerini kullanır:

- `__black.stl`
- `__desert_tan.stl`
- `__brick_red.stl`
- `__dark_green.stl`
- `__blue.stl`

Eski `white / red / green` isimleri ortak fiziksel palette kullanılmaz.

### Bonn doğrulaması

Bonn Münsterplatz güncel ortak palette yeniden üretilmiştir.

Ürün:

- outer size: `170 × 170 mm`
- city opening: `150 × 150 mm`
- scale: `1:3000`
- label: `BONN / GEBURTSORT`
- birthday cake icon aktif

Güncel multicolor output triangle sayıları:

- black: `3412`
- desert_tan: `20102`
- brick_red: `10211`
- dark_green: `49804`
- blue: `156`

Yolların white batch'ten black batch'e taşındığı gerçek Bonn çıktısında
doğrulanmıştır.

Not: Bonner Münster içindeki landmark/component roof semantik dağılımının
son görsel kontrolü ayrı bir ürün doğrulama konusu olarak kalabilir; ortak
palette/geometri sözleşmesi bundan bağımsız olarak kilitlenmiştir.

### Label fiziksel standardı

Ortak label standardı korunmaktadır:

- plate width: `118.0 mm`
- plate height: `9.0 mm`
- plate depth: `1.2 mm`
- corner radius: `2.0 mm`
- frame recess depth: `1.0 mm`
- frame: Black
- label plate: Desert Tan
- label text/icon: Black

### Test doğrulaması

Palette focused regression:

- `24 passed`

Renderer/material related regression:

- `54 passed`

Semantic material hierarchy:

- `8 passed`

Full ATLAS regression:

- `3656 passed in 15.92s`

### Recovery güvenliği

Safety stash korunmaktadır:

`stash@{0}: On main: SAFETY before rollback to c7771ca 2026-08-11`

Bu stash otomatik olarak apply/drop edilmemelidir.

### Moladan sonraki kesin çalışma sırası

Yatay scope expansion yapılmayacak.

1. Jamaica Wall Collection sahnesi temizden oluşturulacak.
2. Seychelles Wall Collection sahnesi temizden oluşturulacak.
3. Kalan 8 sahne/plaka temizden, teker teker yeniden oluşturulacak.
4. Toplam 10 sahne/plaka tamamlandıktan sonra collector box geliştirilecek.
5. Ardından köşebentler / corner supports geliştirilecek.
6. Plakaların arka yüzlerine mıknatıs yuvaları / magnet recesses eklenecek.

Her sahne bağımsız olarak tamamlanıp doğrulanmadan sonraki sahneye
geçilmeyecek.

---

## 12 Ağustos 2026 — Scale-Aware WorldCover Vegetation / Jamaica Validation

### Durum

Jamaica / Mavis Bank / Blue Mountains sahnesi üzerinde WorldCover forest
temsili production seviyesinde yeniden kalibre edilmiştir.

Bu milestone Jamaica ürününün tamamlandığı anlamına gelmez.
Kilitlenen konu, WorldCover tree-cover verisinin fiziksel Wall Collection
ürününe genel ve scale-aware biçimde dönüştürülmesidir.

Jamaica çalışması başlangıcındaki checkpoint `98b5cbf` tarihsel referanstır.

Güncel güvenli ve push edilmiş WorldCover vegetation checkpoint:

- Commit: `65ce99d98867d1056b982a16d337800e212d5857`
- Kısa hash: `65ce99d`
- Commit mesajı: `Add scale-aware WorldCover tree sampling`
- `HEAD == origin/main == 65ce99d`
- Commit sonrası code/test çalışma ağacı temiz olarak doğrulanmıştır.

### Jamaica doğrulama sahnesi

- center: `18.0314032, -76.6583705`
- location: Mavis Bank / Blue Mountains, Jamaica
- city/map size: `150 × 150 mm`
- audit scale: `1:5000`
- ground coverage: yaklaşık `750 × 750 m`
- terrain source elevation delta: `264.70549808231567 m`

OSM production input:

- buildings: `249`
- roads: `6`

### Reddedilen forest canopy yaklaşımı

İlk WorldCover forest temsili continuous canopy/slab hattından üretildi.

Bu yaklaşım reddedildi çünkü büyük forest polygonları terrain üzerinde
uzun planar triangle/ramp yüzeyleri oluşturdu ve gerçek orman görünümünü
bozdu.

Hole-aware canopy ve `inner_rings` denemeleri production çözümü olarak
kabul edilmedi ve çalışma ağacından temizlendi.

### Kilitlenen WorldCover tree representation

Raw `tree_cover` verisi korunur ve ürün scale bilgisi çözüldükten sonra
Foundation/product context içinde yeniden örneklenir.

Genel fiziksel kontrat:

- minimum physical tree-center spacing: `4.0 mm`
- spacing scale-aware çözülür
- `1:5000` için source minimum spacing: `20.0 m`
- sampling deterministic minimum-distance / blue-noise-like davranır
- WorldCover raster satır/sütun görünümünü kırmak için source cell içinde
  deterministic jitter uygulanır
- jitter limiti source cell resolution değerinin `%40`ıdır
- OSM/non-WorldCover ağaçları korunur
- raw `tree_cover` yoksa mevcut WorldCover sampled trees korunur
- raw `tree_cover` varsa legacy WorldCover sample seti yeniden oluşturulur

Production hattında sampled WorldCover trees mevcutsa duplicate:

- `worldcover_forest_canopy_fill`
- continuous forest canopy slab

üretilmez.

### Gerçek production doğrulaması

Monkeypatch kullanılmadan gerçek `AtlasFoundationFirstEngine` hattından
üretilen Jamaica sonucu:

- physical spacing contract: `4.0 mm`
- source spacing at `1:5000`: `20.0 m`
- final WorldCover tree meshes: `623`
- forest canopy meshes: `0`
- tree sources: `worldcover`
- buildings: `249`
- roads: `6`
- terrain delta: `264.70549808231567 m`
- triangles: `158722`

Validation STL:

`OUTPUT/STL/jamaica_mavis_bank_blue_mountains_150mm_5000_PRODUCTION_WORLDCOVER_TREE_FIX.stl`

### Production STL topology doğrulaması

Mevcut `AtlasMeshValidator` edge-topology kurallarıyla gerçek ASCII STL
üzerinde doğrulama yapılmıştır:

- triangles: `158722`
- unique edges: `238083`
- open edges: `0`
- non-manifold edges: `0`

Bu production STL kapalı ve manifold olarak doğrulanmıştır.

### Test doğrulaması

İlgili vegetation regression:

- `106 passed in 0.40s`

Full ATLAS regression:

- `3661 passed in 16.22s`

`git diff --check` temizdir.

### Jamaica Wall Collection fiziksel üretim benchmarkı — 12 Ağustos 2026

WorldCover vegetation milestone sonrasında Jamaica / Mavis Bank /
Blue Mountains sahnesi gerçek Wall Collection ürününe dönüştürülmüştür.

Ürün kontratı:

- outer size: `170 × 170 mm`
- city/map area: `150 × 150 mm`
- scale: `1:5000`
- frame: Black
- label plate: Desert Tan
- label text/icon: Black
- roofs: Brick Red
- vegetation: Dark Green
- label:
  - `JAMAICA`
  - `MAVIS BANK / BLUE MOUNTAINS`
- kişisel ikon: interlocking wedding rings

Bambu Studio / AMS fiziksel renk eşlemesi:

- A1: Black — PLA Basic
- A2: Desert Tan — PLA Matte
- A3: Brick Red — PLA Matte
- A4: Dark Green — PLA Matte

Dört multicolor STL parçası hizalı multi-part object olarak yüklenmiş ve
doğru filamentlere atanmıştır.

Gerçek Bambu Studio slice benchmarkı:

- model / gerçek ürün: `210.53 g`
- purge: `142.04 g`
- prime tower: `44.18 g`
- toplam filament: `396.75 g`
- ürün dışı filament: `186.22 g`
- ürün dışı oran: yaklaşık `%47`
- filament changes: `616`
- estimated print time: `19 h 53 min`
- purge multiplier: `0.60`

Bu sonuç fiziksel baskı için kabul edilmemiştir.

### Kritik üretim dersi

Semantik olarak doğru ve manifold çok renkli STL üretmek tek başına
production-ready olmak için yeterli değildir.

Aynı Z katmanlarında terrain, roads, buildings, roofs, vegetation ve label
gibi farklı renkli geometrilerin tekrar tekrar bulunması AMS tarafında çok
yüksek filament-change sayısı üretmektedir.

Jamaica benchmarkında ana problem purge multiplier değildir:

- `616` filament değişimi vardır
- purge ve prime tower toplamı ürün kütlesine yaklaşmaktadır
- purge multiplier azaltmak yalnız ikincil optimizasyondur
- kalıcı çözüm ürünün color/layer architecture ve multicolor export
  stratejisinde aranmalıdır

Bundan sonraki fiziksel ürün değerlendirmelerinde şu metrikler birinci sınıf
production acceptance kriterleri olarak izlenecektir:

- filament-change count
- purge mass
- prime-tower mass
- product mass
- total filament mass
- estimated print time

### Jamaica ürün durumu

Mevcut Jamaica / Mavis Bank / Blue Mountains ürünü silinmeyecektir.

Bu çalışma:

- gerçek AMS maliyetini ortaya çıkaran ilk production benchmarkıdır
- multicolor optimizasyonu için regression/reference ürün olarak korunacaktır
- edinilen deneyim başarısızlık değil, fiziksel production mimarisi girdisidir

Fiziksel baskı şu anda `HOLD` durumundadır.

### Aktif sonraki adım

Mevcut Jamaica slice basılmayacaktır.

Devam sırası:

1. Bambu Studio layer preview üzerinden renk değişimlerinin yoğun olduğu
   Z aralıklarını ölç.
2. `616` filament değişiminin hangi semantic mesh kombinasyonlarından
   kaynaklandığını belirle.
3. Görsel kaliteyi koruyarak aynı katmandaki renk değişimlerini azaltacak
   production/color-layer stratejisi tasarla.
4. Yeni STL setini üret ve tekrar slice et.
5. Yeni sonucu mevcut `210.53 / 142.04 / 44.18 / 396.75 g`,
   `616 changes`, `19 h 53 min` benchmarkına karşılaştır.
6. Atık kabul edilebilir seviyeye inmeden ilk fiziksel baskıyı başlatma.

Jamaica işi kayıt altına alınmadan ve üretim dersi korunmadan Seychelles
veya başka lokasyona geçilmeyecektir.

---

## Eschersheim Production Geometry Checkpoint — 13 Ağustos 2026

Bu checkpoint, önceki 8.20 sonrası production checkpoint kayıtlarını
güncel güvenli repo durumu açısından supersede eder.

### Son güvenli ve push edilmiş commit

- Commit: `311ddbfb15798ac7f6f525c1bd213b7be8626763`
- Kısa hash: `311ddbf`
- Commit mesajı: `Clip rail and water infrastructure to product bounds`
- Branch: `main`
- `HEAD == origin/main`
- Full regression: `3674 passed in 16.69s`

### Eschersheim / Niedwiesenstraße production geometry

Aktif sipariş sahnesi:

- lokasyon: Eschersheim / Frankfurt am Main
- tarihî adres referansı: `Niedwiesenstraße 99`
- scene basis: current / modern OSM geometry
- highlighted current OSM way: `29054040`
- current OSM address: `Niedwiesenstraße 103`
- old 99 / current 103 eşleşmesi kesin tarihsel kanıt olarak kabul edilmez
- outer product: `220 × 220 mm`
- map opening: `200 × 200 mm`
- frame width: `10 mm`
- frame depth: `6 mm`
- scale: `1:3000`

### Rail ve water product-bound clipping

Gerçek Eschersheim doğrulamasında railway ve narrow-waterway geometrilerinin
ürün dışına taşabildiği tespit edildi.

Genel çözüm:

- surface railway footprint extrusion öncesinde product bounds'a clip edilir
- narrow-waterway footprint solid oluşturulmadan önce product bounds'a clip edilir
- clipping mevcut `AtlasRoadPolygonBuilder._clip_polygon_to_bounds`
  mekanizmasını yeniden kullanır
- lokasyona veya belirli OSM ID'sine özel geometri hack'i eklenmez
- clipping sonrası solid yeniden üretildiği için boundary sidewall'ları korunur

Gerçek Nidda doğrulaması:

- source way: `251248199`
- type: `narrow_waterway_foundation`
- clipped bounds:
  - X: `0.000000 .. 127.009576 mm`
  - Y: `80.899604 .. 200.000000 mm`
- triangles: `68`
- open edges: `0`
- non-manifold edges: `0`

Gerçek railway doğrulaması:

- dört surface railway mesh'i ürün sınırları içinde kalır
- her railway solid için:
  - open edges: `0`
  - non-manifold edges: `0`

Bambu Studio fiziksel ürün yerleşim doğrulamasında önce görülen
yaklaşık `853 × 773 mm` taşma ve `laid over boundary` problemi ortadan kalktı.
Final 5-color STL seti 220 × 220 mm ürün footprint'i içinde açılıyor.

### Geometri lock / label pending

Eschersheim şehir ve ürün geometrisi bu checkpoint'te kilitlenmiştir.

Label metni ayrı bir ürün-content kararıdır ve henüz kilitli değildir.
Sipariş sahibinden teyit beklenmektedir. Label daha sonra değiştirilirse
şehir geometrisi, road/rail/water sistemi, ölçek veya product footprint
yeniden tasarlanmayacaktır; yalnız label çıktıları ve ilgili final export'lar
yeniden üretilecektir.

### Korunması gereken aktif çalışma ağacı

`311ddbf` commit'i dışında bırakılan Jamaica / wedding-rings / label
çalışmaları bilinçli olarak korunmaktadır:

- `CORE/atlas_label_text_spec.py`
- `CORE/atlas_product_color_preview_renderer.py`
- `CORE/atlas_wall_collection_product_builder.py`
- `Test/test_label_text_spec.py`
- `Test/test_product_color_preview_renderer.py`
- `Test/test_wall_collection_product_builder.py`
- `CORE/atlas_label_wedding_rings_mesher.py`
- `Data/OSM/`
- `Test/preview_jamaica_mavis_bank_blue_mountains_wall_collection.py`
- `Test/test_label_wedding_rings_mesher.py`

Bu dosyalar toplu stage/reset/restore/clean işlemine dahil edilmemelidir.



---

## 14 Ağustos 2026 — Physical Production Checkpoint

### Jamaica Premium Island Relief V1 — PRODUCTION PACKAGE READY

Jamaica whole-island relief yaklaşımı gerçek multicolor production package
seviyesine ulaşmıştır.

Geometry:

- product: `170 × 170 mm`
- opening: `150 × 150 mm`
- frame: `10 mm`
- island: `140.000 × 55.189 mm`
- relief Z: `1.600 .. 9.788 mm`
- island triangles: `68,444`

Aligned color STLs:

1. black frame
2. blue sea
3. green island relief
4. white label plate
5. black label text + wedding rings

Label:

`JAMAICA`
`BLUE MOUNTAINS · MAVIS BANK`

Bambu Studio production validation:

- approximately `2 h 54 min`
- approximately `88.62 g` total filament
- `40` filament changes

Bu sonuç, önceki Mavis Bank city-based benchmarkındaki `616` change /
`396.75 g` / `19 h 53 min` sonucuna karşı yeni fiziksel color/layer
architecture'ın başarılı production-cost doğrulamasıdır.

Bambu Studio `.3mf` project kaydedildi.

### Niedwiesenstraße 99 — physical completion work

Tamamlanan fiziksel işler:

- ana sahne basıldı
- ayrı wide river insert basıldı
- river insert sahneye fiziksel olarak eklendi
- premium gift-box lid basıldı
- premium gift-box base baskıya gönderildi

Gift-box lid üst yüzeyinde premium kaliteyi bozan çizgisel / ipliksi yüzey
gözlendi.

Base için kullanılan son calibration:

- `0.24 mm` layer height
- `10%` sparse infill
- `6` top shell layers
- `No ironing`
- slice yaklaşık `2 h 52 min`
- yaklaşık `172.21 g`

Base baskısı tamamlandığında fiziksel top-surface sonucu kontrol edilecek.

### Next exact task

Niedwiesenstraße fiziksel sahnesi için ayrı basılabilir tree / vegetation
insert package hazırlanacak.

Bu çalışma:

- mevcut ATLAS canonical tree geometry'sini mümkün olduğunca yeniden kullanmalı
- sahneye sonradan yerleştirilebilir olmalı
- yeşil filamentle ayrı basılabilmeli
- küçük boy varyasyonları / doğal kümelenme desteklemeli
- mevcut Jamaica çalışmalarına zarar vermemeli

### Working-tree protection

Jamaica / wedding-rings aktif uncommitted çalışmalarına toplu
reset/restore/clean uygulanmayacaktır.


### Gift Box BASE physical validation — PASS

Niedwiesenstraße Premium Gift Box V1 BASE baskısı tamamlandı ve fiziksel olarak
incelendi.

Observed result:

- large flat internal surface: smooth / homogeneous
- previous lid'deki çapraz / ipliksi surface artifact: yok
- corner lifting: yok
- visible severe warping: yok
- right long edge: hafif, elle hissedilebilen inward bow
- inward bow acceptance: PASS, tolerance note olarak korunacak

Physical reference settings:

- `0.4 mm` nozzle
- `0.24 mm` layer height
- `10%` sparse infill
- `6` top shell layers
- `No ironing`

Decision:

- Gift Box BASE physical validation: `PASS`
- bu ayar kombinasyonu yeni flat-surface production reference'tır
- yeni lid baskısı aynı ayarlarla yapılmalıdır
- eski lid top-surface sonucu artık production standardı değildir


---

## 14 Ağustos 2026 — Physical Tree V1

Status: `PASS / ready for checkpoint commit`

Problem confirmed:

ATLAS had a functioning tree pipeline but the previous canonical tree contract
was not physically printable at product scale.

Old canonical dimensions:

- trunk diameter: `0.45 mm`
- crown diameter: `1.55 mm`
- total height: `2.15 mm`

Physical Tree V1:

- trunk diameter: `1.125 mm`
- crown diameter: `3.875 mm`
- total height: `5.375 mm`
- WorldCover spacing: `6.0 mm`
- deterministic WorldCover scale variants:
  `0.95× / 1.00× / 1.05×`

Niedwiesenstraße real validation:

- tree count after Physical V1 spacing: `349`
- variant distribution:
  - `0.95×`: `118`
  - `1.00×`: `112`
  - `1.05×`: `119`
- final tree-only candidate:
  - `83,760` triangles
  - `0` open edges
  - `0` non-manifold edges

Bambu Studio visual density / geometry validation: `PASS`

Regression:

- tree-focused combined package: `61 passed`
- full regression: `3689 passed in 16.37s`

Important:

Niedwiesenstraße-specific geometry hack was not added. The fix is generic and
applies through the shared ATLAS tree foundation / WorldCover composition path.


---

## 14 August 2026 — Bonn Birthplace Production V1 / PRINTING

### Product and palette

- location: Bonn Münsterplatz
- product/opening/scale: `170 × 170 mm` / `150 × 150 mm` / `1:3000`
- label: `BONN / GEBURTSORT`; symbol: baby stroller
- Black: frame, roads, label text, stroller
- White: terrain, label plate
- Desert Tan: buildings, generic roofs, landmark walls
- Brick Red: historic church/tower roof surfaces
- Dark Green: parks, trees
- water/Blue: not used

`BONN_BIRTHPLACE_V1` separates generic and landmark roof materials.

### Geometry/export corrections

- unsupported semantic splits preserve the closed original building;
- same-material generic walls/roofs remain one closed solid;
- landmark roofs use a separate `landmark_roofs` batch;
- projected landmark/building overlaps and park near-coverage/touching topology are filtered;
- known physical RGB values resolve to filament filenames instead of internal names such as `material_1`.

Package: `OUTPUT/STL/BONN_BIRTHPLACE_PRODUCTION_V1/`

Topology:

- black `4512`, white `2592`, desert_tan `19382`, brick_red `78`, dark_green `27428` triangles
- every file: `0` open / `0` non-manifold

### Physical completion and production lesson

Automatic landmark roof metadata did not cover every intended Münster roof surface. Incorrect red parts were reassigned to Desert Tan and the desired roofs were painted Brick Red in Bambu Studio. This is product-local physical completion; automatic roof classification is not fully solved.

Preview correctness alone is not a physical production gate. Require closed/manifold material solids or slicer-verified volumetric color, Bambu object/material inspection, plausible per-filament model mass, purge/prime-tower/change/time review, and AMS/external capacity review.

Slice:

- model `121.46 g`; purge `45.64 g`; tower `15.15 g`; total `182.25 g`
- changes `193`; time `9 h 31 min`; estimated finish approximately `08:07` on 15 August
- A1 Black; A2 White; A3 Desert Tan; A4 Dark Green; External Brick Red

Current project: `bonn_muensterplatz_170mm_BIRTHPLACE_PRODUCTION_V1.3mf`. Older erroneous Bonn projects must not be reused. External red requires manual intervention.

Regression: `109 passed`; full `3704 passed in 16.54s`.

---

## 15 August 2026 — Seychellen Premium Archipelago V1 / PRINT QUEUE

### Product contract

- outer/opening: `170 × 170 mm` / `150 × 150 mm`
- archipelago span: `140.000 × 99.808 mm`
- relief Z: `1.600 .. 10.683 mm`
- German label: `SEYCHELLEN / SILBERHOCHZEIT · 25 JAHRE`
- no label symbol
- Black: frame and label text
- White: label plate
- Dark Green: island relief
- Blue: sea slab

The physical package contains five aligned STL files but uses four physical
filaments because frame and label text are separate Black parts.

### Geometry and topology

The real disconnected archipelago components are preserved. Two independent
island components that touched at only one XY vertex were separated by
`0.0001 mm`. This removed two four-owner vertical edges without changing the
visible product dimensions or triangle count.

- sea: `12` triangles
- island relief: `7248` triangles
- frame: `248` triangles
- label plate: `96` triangles
- label text: `2344` triangles
- every physical STL: `0` open / `0` non-manifold

### Bambu physical gate

- model: `73.03 g`
- purge: `9.98 g`
- prime tower: `3.31 g`
- total: `86.32 g`
- filament changes: `40`
- total time: `2 h 32 min`

Per-material model mass is plausible: Black `22.21 g`, White `1.49 g`,
Dark Green `1.72 g`, Blue `47.61 g`.

Project: `seychelles_premium_archipelago_170mm_PRODUCTION_V1.3mf`.

Status: `PRINTING`.

---

## 15 August 2026 — Modular/Personalized Gift Box and Physical Tree V2

### Gift-box production system

The shared Premium Gift Box now supports:

- Mini `120 mm`, Original `170 mm`, Grande `220 mm`;
- `25 mm` and `50 mm` stackable middle capacities with `2 mm` usable clearance;
- base male, middle female/male and lid female connector architecture;
- removable centered personalization insert with a real lid recess;
- one or two centered DejaVu Sans Bold personalization lines;
- universal `25 mm` / `50 mm` tier corner supports, quantity four per level.

Personalization standards:

- Mini plate/recess: `80 × 24` / `80.4 × 24.4 mm`
- Original: `110 × 28` / `110.4 × 28.4 mm`
- Grande: `140 × 32` / `140.4 × 32.4 mm`
- plate thickness `1.2 mm`; recess depth `0.8 mm`;
  fit clearance `0.20 mm/side`; raised text `0.6 mm`

All generated modular box parts, personalization lids/inserts/text and
universal supports passed closed/manifold topology gates.

### Physical Tree V2

Physical printing showed that the accepted V1 tree appearance was good but its
`1.125 mm` trunk started directly at the terrain surface and could break under
light handling.

The generic canonical tree was strengthened without changing placement,
density, crown appearance or visible product height:

- trunk diameter `1.50 mm`
- smallest deterministic variant `1.425 mm`
- root collar `2.20 × 0.80 mm`
- terrain embed `0.60 mm`
- connected single closed surface; `0` open / `0` non-manifold

Validation:

- tree-related package: `76 passed`
- full regression: `3764 passed in 16.70s`

Seychellen production state: `PRINTING`; A1 Black, A2 White, A3 Blue,
A4 Dark Green.


---

## 15 August 2026 — Köln Graduation Production V2 / PRINT QUEUE

### Physical product

- current standard: `170 × 170 mm` outer, `150 × 150 mm` opening
- scale: `1:3000`
- label: `UNIVERSITÄT ZU KÖLN / PÄDAGOGISCHE FAKULTÄT`
- icon: graduation cap
- target building: Universität zu Köln Gebäude `216`,
  Gronewaldstraße 2; OSM source `125014714`
- Gebäude 216 scene bounds:
  X `70.084 .. 80.355 mm`, Y `51.402 .. 91.826 mm`
- current institutional name: Humanwissenschaftliche Fakultät;
  recipient context: former Pädagogische Fakultät

### Physical palette and geometry

- Black: frame, label text, graduation cap
- White: terrain, roads, generic buildings/roofs, label plate
- Brick Red: only the Bambu-painted roof of Gebäude 216
- Dark Green: parks and Physical Tree V2 vegetation
- Blue: real scene water (`148` triangles)

Generated material STL topology:

- black `2904`, white `9526`, generated Brick Red `46`,
  Dark Green `40900`, Blue `148` triangles
- every generated STL: `0` open / `0` non-manifold

The generated `46`-triangle Brick Red part was not visibly useful and was
removed from the Bambu project. Gebäude 216 was identified from source ID and
scene bounds, then only its roof was painted Brick Red. Its walls and all
neighbouring buildings remain White. Layer preview confirmed real volumetric
red toolpaths.

The Black STL floating-cantilever warning is a false positive caused by label
text/cap being separate components in the shared Black part. Layer inspection
confirmed continuous White label-plate material below the Black text; supports
must not be enabled.

### Bambu physical gate

Final slice after removing the redundant generated red part:

- model `100.77 g`
- purge `22.90 g`
- prime tower `6.67 g`
- total `130.33 g`
- filament changes `88`
- total time `6 h 19 min`

Removing the redundant part improved the earlier slice from `89` to `88`
changes, `23.09` to `22.90 g` purge and `6 h 20 min` to `6 h 19 min`.

Saved project:

`OUTPUT/STL/koeln_paedagogische_fakultaet_multicolor_170mm_PRODUCTION_V2/koeln_paedagogische_fakultaet_170mm_GRADUATION_PRODUCTION_V2.3mf`

Status: `PRINT QUEUE`, after the current Seychellen production.

Validation: focused `25 passed`; related `82 passed`; full `3767 passed in 16.96s`.

### Parked engine development: layer-aware color/change optimization

Add a generic production optimizer/report before future batch printing:

- report required physical materials for every Z layer;
- identify empty, occluded or visually redundant material parts;
- report which geometry causes every filament transition;
- estimate model, purge and prime-tower mass before Bambu completion;
- propose safe material-order/consolidation opportunities;
- never replace a visible semantic color automatically;
- retain Bambu object/material, layer-preview and gram-distribution checks as
  the final physical gate.

---

## 15 August 2026 — Meckenheim Home Production V2 / BAMBU PROJECT READY

### Verified product contract

- address: Jungholzweg 2/3, 53340 Meckenheim
- verified OSM buildings:
  - `220593156`: `2, 2 a, 2 b`, `building=apartments`
  - `389176145`: `3`, `building=house`
- Apple Maps Jungholzweg 2 pin:
  `50.619320, 7.032310`
- OSM `220593156` center is `7.64 m` from the Apple pin
- outer/opening/scale: `170 / 150 mm / 1:3000`
- label/icon: `JUNGHOLZWEG 2/3 / MECKENHEIM` / home

### Physical palette and selected-roof separation

The Bonn-style premium hierarchy is used:

- Black: frame, label text and home symbol
- White: terrain, roads and label plate
- Desert Tan: generic buildings and generic roofs
- Brick Red: only the verified Jungholzweg 2/3 target roofs
- Dark Green: parks and Physical Tree V2 vegetation
- Blue: available in the profile but absent from this real scene

A new opt-in renderer contract preserves same-material buildings as single
closed solids by default, but can force safe closed wall/roof separation for
verified highlighted buildings. Meckenheim uses roof-only highlighting and
routes the two target roofs to the Brick Red landmark-roof batch. All other
walls and roofs remain Desert Tan.

Physical STL topology:

- Black `1848` triangles
- White `5832`
- Brick Red `20`
- Desert Tan `10150`
- Dark Green `19952`
- every part: `0` open / `0` non-manifold

Saved Bambu project:

`OUTPUT/STL/meckenheim_jungholzweg_2_3_multicolor_170mm_PRODUCTION_V2/meckenheim_jungholzweg_2_3_170mm_HOME_PRODUCTION_V2.3mf`

Visual composition: `PASS`.
Physical topology gate: `PASS`.
Slice/mass/change/time gate: `PENDING`.

Validation: related package `71 passed`; full regression
`3772 passed in 16.90s`.

Production sequencing requirement: complete the current Köln print, then
update P2S firmware and Bambu Studio before slicing or starting Meckenheim.

---

## Semantic Relief, Figurative & Kit System V1 — ROADMAP WRITING

ATLAS 2.5D rölyef motorunun mevcut kodu incelendi. Sonuç: temel zayıflık height-map matematiği değil; kaynakları semantic component graph haline getirip depth, occlusion, fiziksel feature, surface projection ve product output kararlarıyla yönetecek üst omurganın eksikliğidir.

### Doğrulanan mevcut temel

Mevcut sistem image input, preprocessing, multiscale decomposition, depth composition ve compression, mask ve morphology, layer separation, semantic material, portrait landmark regions, physical profiles, closed relief mesh, topology ve print-risk raporları, STL export, facade component meshers ve production-package altyapısına sahiptir. Bu katmanlar korunacak ve yeni semantic program tarafından yeniden kullanılacaktır.

### Doğrulanan ana boşluklar

- `AtlasSemanticArchitectureComponent` henüz yalnız identity metadata taşır.
- Canonical component graph, transform, target surface, depth order, occlusion, physical policy, repetition, output eligibility ve assembly interface eksiktir.
- Architectural Relief V1 tek normalize height-map sonucunu düz plakaya çevirir; gerçek semantic architecture orchestration ve surface projection yapmaz.
- Production package Dalyan ve 80x50 mm sabitlerine bağlıdır.
- Figurative body, pose, gesture, prop, contact ve personalized story grammar mevcut değildir.
- Production seviyesinde canonical face/head fitting hattı tamamlanmamıştır.
- Portrait belgelerinde FLAME kararı ile multi-view reconstruction yönü arasında açık decision gate gerektiren çelişki vardır.

### Kilitlenen program kapsamı

Ana roadmap 15 fazdan oluşur:

- Phase 0: audit ve karar temizliği;
- Phase 1–5: semantic scene contract, geometry adapters, depth/occlusion, physical resolver ve surface projection;
- Phase 6–7: ornament library ve ilk architectural semantic relief product;
- Phase 8–11: face/head decision gate, portrait, figurative grammar ve personalized story composer;
- Phase 12–13: shared component catalog ve modular architectural kit;
- Phase 14–15: unified orchestration ve commercial production gate.

Detaylı kabul kapıları ve stop kriterleri aktif devir belgesindeki `Semantic Relief, Figurative & Kit System V1 — Master Execution Compass` bölümündedir.

### Güncel durum

Status: `RED_CONTRACT`

- Yeni CORE veya Test implementation başlatılmadı.
- Yeni RED contract yazılmadı.
- Phase 0 baseline tamamlandı: relief, architectural relief, semantic architecture ve portrait contract paketlerinde `1020 passed in 2.28s`, exit `0`.
- Phase 0 status: `LOCKED`; full regression: `3772 passed in 16.84s`, exit `0`.
- Yeni CORE veya Test implementation başlatılmadı; ilk RED contract henüz yazılmadı.
- `Data/OSM/` ve üç Jamaica preview scripti korunmuş unrelated untracked kapsamıdır.
- Broad stage, reset, restore veya clean uygulanmayacaktır.

### Sıradaki kesin tek iş

Üç roadmap belgesinin birlikte UTF-8, heading, duplicate, control-byte, diff ve status kontrolünü yapmak. Kontroller yeşilse mevcut relief ve semantic architecture baseline test paketlerini çalıştırmak ve sonucu Phase 0 audit kaydına eklemek. Phase 1 RED contract bundan önce başlatılmayacaktır.

### Phase 1 ilerleme — Canonical component foundation

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%7`
- Phase 1 status: `IMPLEMENTATION_ACTIVE`
- Yeni contract: `AtlasSemanticReliefComponent`
- Focused validation: `22 passed`
- Related semantic validation: `46 passed in 0.14s`
- Full regression: `3794 passed in 16.84s`
- Diff check: temiz

Canonical component artık identity, parent identity, source reference, target surface, projection mode, depth band, layer order, material role, physical feature policy, output eligibility, provenance ve confidence alanlarını immutable ve normalize edilmiş biçimde taşır. Eksik target/projection ilişkisi, geçersiz layer order, geçersiz output modes ve geçersiz confidence reddedilir.

Phase 1 henüz tamamlanmadı. Sıradaki paket transform, orientation ve physical dimensions contractıdır; ardından repetition ve `AtlasSemanticReliefScene` graph doğrulamaları gelecektir.

Yüzde kayıt kuralı: bundan sonraki her anlamlı milestone kaydında `ATLAS genel tamamlanma` ve `Aktif program tamamlanma` birlikte yazılacaktır. Yüzdeler test sayısına göre değil, kabul kapısı tamamlanan gerçek yeteneklere göre değiştirilecektir.

### Phase 1 ilerleme — Transform ve fiziksel yerleşim

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%8`
- Phase 1 status: `IMPLEMENTATION_ACTIVE`
- Yeni contract: `AtlasSemanticReliefTransform`
- Focused validation: `31 passed in 0.05s`
- Related semantic validation: `55 passed in 0.16s`
- Full regression: `3803 passed in 16.81s`
- Diff check: temiz

Transform contract translation, XYZ rotation, positive physical dimensions ve coordinate-space kimliğini immutable ve finite değerlerle taşır. Malformed triplets, non-finite değerler ve non-positive dimensions reddedilir. `AtlasSemanticReliefComponent` yalnız doğrulanmış transform nesnesi kabul eder.

Sıradaki Phase 1 paketi repetition ve interchangeable-instance contractıdır; ardından `AtlasSemanticReliefScene` graph doğrulamaları geliştirilecektir.

### Phase 1 ilerleme — Repetition ve interchangeable instances

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%9`
- Yeni immutable contract: `CORE/atlas_semantic_relief_repetition.py`
- Yeni test paketi: `Test/test_semantic_relief_repetition.py`
- `AtlasSemanticReliefRepetition`; canonical `repeat_group_id`, pozitif `quantity`, finite `spacing_mm` ve strict boolean `interchangeable` taşır.
- Çoklu instance için sıfır spacing reddedilir; tek instance için sıfır spacing kabul edilir.
- `AtlasSemanticReliefComponent`, yalnız doğrulanmış `AtlasSemanticReliefRepetition` veya `None` kabul eder.
- Focused validation: `41 passed in 0.04s`
- Related semantic validation: `72 passed in 0.17s`
- Full regression: `3820 passed in 16.81s`
- `git diff --check`: temiz.
- Korunan Jamaica/OSM untracked girdilerine dokunulmadı.

Sıradaki kesin iş: Phase 1 içinde canonical component, transform ve repetition contractlarını tek immutable semantic relief scene/model graph altında birleştiren ilk RED sözleşme.

### Phase 1 ilerleme — Immutable semantic relief scene graph

Status: `GREEN_MILESTONE`; Phase 1 henüz `LOCKED` değildir.

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%10`
- Yeni contract: `CORE/atlas_semantic_relief_scene.py`
- Yeni test: `Test/test_semantic_relief_scene.py`
- Scene identity, typed/non-empty components, unique IDs, parent/target referansları, self-parent ve cycle kapıları kilitlendi.
- Canonical component, direct-child, target-surface ve root-component sorguları eklendi.
- Focused: `12 passed in 0.02s`
- Related: `84 passed in 0.19s`
- Full regression: `3832 passed in 16.78s`
- `git diff --check`: temiz.

Phase 1 kalan kabul kapıları: `occlusion_policy`; architecture, portrait, figurative ve kit synthetic fixture; mevcut `AtlasSemanticArchitectureModel` geçiş ilişkisinin belgelenmesi. Sıradaki kesin iş: `occlusion_policy` için ilk RED contract.

### Phase 1 LOCKED — Semantic Relief Scene Contract V1

Status: `LOCKED`.

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%12`
- Immutable component, transform, repetition ve scene graph contractları tamamlandı.
- Duplicate ID, missing parent/target surface, self-parent ve parent-cycle doğrulamaları tamamlandı.
- Depth/layer, output mode, occlusion policy, material/physical policy, provenance ve confidence sözleşmeleri tamamlandı.
- Architecture, portrait, figurative ve modular-kit kullanımları synthetic fixture ile doğrulandı.
- Mevcut `AtlasSemanticArchitectureModel` ile tek yönlü geçiş ilişkisi belgelendi; gerçek adapter Phase 2 kapsamındadır.
- Focused use-case paketi: `41 passed in 0.06s`.
- Related semantic regression: `87 passed in 0.20s`.
- Full regression: `3835 passed in 16.74s`.
- `git diff --check`: temiz.

Phase 1 kabul kapısı eksiksiz kapanmıştır. Sıradaki kesin iş: Phase 2 Geometry Source Adapter Contracts için provider-independent normalize geometry result sözleşmesinin ilk RED testi.

### Wall Collection 25 mm corner support — GREEN_PROTOTYPE

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%12`
- Universal köşebent geometrisindeki harici alt female socket ile üst male pin/pad kaldırıldı.
- Üretim geometrisi yalnız 90 derece ana köşe gövdesi ve iç taşıyıcı raftan oluşur.
- Focused corner-support paketi: `26 passed in 0.08s`.
- Full regression: `3836 passed in 16.80s`.
- Yeniden üretilen `ATLAS_TIER_CORNER_SUPPORT_25MM.stl`: `64` triangle, yaklaşık `13 KB`, toplam yükseklik `33.4 mm`.
- Dört parçalık PLA fiziksel prototip basıldı; görsel kalite, tutuş ve dört-köşe sallanma kontrolleri geçti.
- Fiziksel kabul: `GREEN_PROTOTYPE`.
- Mevcut `50MM` STL yeniden üretilmedi; eski connector geometrisi taşıdığı için üretimde kullanılmayacaktır.
- Sıradaki fiziksel paket: beş sahnelik modüler kutu için küçük geçme toleransı kalibrasyon kuponu.
