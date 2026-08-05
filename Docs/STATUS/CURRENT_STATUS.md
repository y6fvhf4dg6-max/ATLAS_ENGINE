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

