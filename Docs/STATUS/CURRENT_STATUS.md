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
