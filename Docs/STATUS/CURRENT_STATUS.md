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

### Phase 2 ilerleme — Provider-independent Geometry Source Result

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%14`
- Phase 2 status: `IMPLEMENTATION_ACTIVE`
- Yeni contract: `CORE/atlas_geometry_source_result.py`
- Yeni test paketi: `Test/test_geometry_source_result.py`
- `AtlasGeometrySourceResult`; normalized geometry, local bounds, normalized anchors, confidence, provenance ve supported projection modes sözleşmesini provider-independent ve immutable result sınırı olarak kurar.
- Caller mutable geometry/anchor girdileri result sonradan değişmeyecek şekilde izole edilir.
- Reversed/non-finite bounds, duplicate normalized anchor names, invalid confidence/provenance ve invalid projection-mode sets reddedilir.
- Unsupported projection mode `require_projection_mode()` ile erken ve açık hata verir.
- Focused: `21 passed in 0.02s`.
- Related semantic regression: `113 passed in 0.27s`.
- Full regression: `3873 passed in 16.79s`, `1 failed`.
- Tek full-regression kırığı Phase 2 dışındaki untracked Premium Gift Box connector calibration paketidir: spec `0.20/0.25/0.30`, eski test `0.05/0.10/0.15` beklemektedir.
- `git diff --check`: temiz.
- Korunan unrelated Erkelenz/Jamaica/Gift Box/OSM çalışmalarına dokunulmadı.
- Sıradaki kesin iş: provider ve CORE sorumluluklarını ayıracak Phase 2 adapter interface contractının ilk RED testi.

### Phase 2 ilerleme — Geometry Source Adapter responsibility boundary

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%15`
- Phase 2 status: `IMPLEMENTATION_ACTIVE`
- Yeni contract: `CORE/atlas_geometry_source_adapter.py`
- Yeni test paketi: `Test/test_geometry_source_adapter.py`
- `AtlasGeometrySourceAdapter` abstract provider/CORE boundary olarak kilitlendi.
- Concrete adapter `adapt(source)` uygular ve CORE'a yalnız `AtlasGeometrySourceResult` döndürür.
- Non-canonical adapter output `validate_result()` ile reddedilir.
- Requested projection mode yalnız canonical result capability setine karşı doğrulanır; unsupported mode erken hata verir.
- Focused Phase 2: `27 passed in 0.04s`.
- Related semantic regression: `113 passed in 0.25s`.
- Full regression: `3879 passed in 16.74s`, `1 failed`.
- Tek failure daha önce doğrulanan unrelated untracked Premium Gift Box connector calibration spec/test tutarsızlığıdır.
- `git diff --check`: temiz.
- Phase 2 kaynaklı yeni regression yoktur.
- Korunan unrelated Erkelenz/Jamaica/Gift Box/OSM çalışmalarına dokunulmadı.
- Sıradaki kesin iş: Phase 2 roadmap sırasındaki ilk concrete adapter olan height-map relief source contractı için ilk RED test.

### Phase 2 ilerleme — Height-map Geometry Source Adapter

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%17`
- Phase 2 status: `IMPLEMENTATION_ACTIVE`
- Yeni adapter: `CORE/atlas_height_map_geometry_source_adapter.py`
- Yeni test paketi: `Test/test_height_map_geometry_source_adapter.py`
- `AtlasHeightMapGeometrySourceAdapter`; existing normalized relief height-map verisini provider-independent canonical geometry-source result sınırına taşır.
- Canonical geometry snapshot: `geometry_kind=height_map_relief`, immutable height field snapshot, row/column count, width, depth ve relief height.
- Local bounds `(0,0,0)` ile `(width,depth,relief_height)` arasında deterministic kurulur.
- Adapter mesh/STL üretmez.
- Supported projection modes yalnız `flat_plane`; Phase 5 projection capability’leri erken ilan edilmez.
- Input isolation, malformed map rejection, normalized range, finite değerler, minimum 2x2 shape ve fiziksel ölçü validation kapıları tamamlandı.
- Focused Phase 2: `44 passed in 0.08s`.
- Related semantic/architectural relief regression: `126 passed in 0.28s`.
- Full regression: `3896 passed in 16.73s`, `1 failed`.
- Tek failure daha önce doğrulanan unrelated untracked Premium Gift Box connector calibration spec/test tutarsızlığıdır.
- `git diff --check`: temiz.
- Phase 2 kaynaklı yeni regression yoktur.
- Korunan unrelated Erkelenz/Jamaica/Gift Box/OSM çalışmalarına dokunulmadı.
- Sıradaki kesin iş: Phase 2 roadmap sırasındaki `existing triangle mesh source` adapter contractı için ilk RED test.

### Phase 2 ilerleme — Existing Triangle Mesh Source Adapter

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%19`
- Phase 2 status: `IMPLEMENTATION_ACTIVE`
- Yeni adapter: `CORE/atlas_triangle_mesh_geometry_source_adapter.py`
- Yeni test paketi: `Test/test_triangle_mesh_geometry_source_adapter.py`
- `AtlasTriangleMeshGeometrySourceAdapter`, ATLAS'ın yaygın direct triangle-soup mesh formatını canonical geometry-source result sınırına taşır.
- Indexed `vertices/faces` formatı zorlanmaz; mevcut motor formatı korunur.
- Canonical result isolated triangles, triangle count, deterministic local bounds, anchors, confidence, provenance ve supported projection modes taşır.
- Adapter mesh üretmez ve topology/manifold doğrulamasını kendi sorumluluğuna almaz.
- Malformed/non-finite/non-numeric triangle source validation kapıları tamamlandı.
- Focused Phase 2: `55 passed in 0.09s`.
- Related semantic/relief regression: `143 passed in 0.27s`.
- Önceden full regressionı kirleten Premium Gift Box stale calibration test güncel production kontratı olan `0.20/0.25/0.30`, engagement `1.6`, recess `1.8` değerlerine hizalandı; production spec değiştirilmedi.
- Full regression: `3908 passed in 16.80s`.
- `git diff --check`: temiz.
- Sıradaki kesin iş: Phase 2 roadmap sırasındaki `parametric primitive source` adapter contractı için ilk RED test.

### Phase 2 ilerleme — Parametric Primitive Source Adapter

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%21`
- Phase 2 status: `IMPLEMENTATION_ACTIVE`
- Yeni adapter: `CORE/atlas_parametric_primitive_geometry_source_adapter.py`
- Yeni test paketi: `Test/test_parametric_primitive_geometry_source_adapter.py`
- İlk primitive contract `closed_cylinder`.
- Existing ATLAS cylinder descriptor provider-independent canonical geometry-source result sınırına taşınır.
- Normalized geometry; primitive type ve center/base/radius/height/segments parametrelerini içerir.
- Deterministic local bounds ve `base_center` / `top_center` anchors üretilir.
- Adapter herhangi bir mesh/STL/triangle üretmez.
- Primitive normalization ile geometry production sorumluluğu ayrılmıştır.
- Unsupported primitive, malformed source ve invalid numeric/segment validation kapıları tamamlandı.
- Focused Phase 2: `74 passed in 0.11s`.
- Related semantic/geometry regression: `152 passed in 0.29s`.
- Full regression: `3927 passed in 16.52s`.
- `git diff --check`: temiz.
- Sıradaki kesin iş: Phase 2 roadmap sırasındaki `facade grammar source` adapter contractı için ilk RED test.

### Phase 2 ilerleme — Facade Grammar Source Adapter

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%23`
- Phase 2 status: `IMPLEMENTATION_ACTIVE`
- Yeni adapter: `CORE/atlas_facade_grammar_geometry_source_adapter.py`
- Yeni test paketi: `Test/test_facade_grammar_geometry_source_adapter.py`
- İlk grammar contract: `uniform_openings`.
- Existing facade grammar tanımı canonical geometry-source result sınırına normalize edilir.
- Geometry snapshot; facade dimensions, level/bay counts, opening semantics, margin ratios ve opening count taşır.
- Deterministic local bounds ve facade anchors üretilir.
- Facade grammar normalization ile facade geometry meshing sorumlulukları ayrılmıştır.
- Adapter triangle/mesh/STL üretmez.
- Unsupported grammar ve malformed source validation kapıları tamamlandı.
- Focused Phase 2: `102 passed in 0.13s`.
- Related semantic/facade regression: `188 passed in 0.37s`.
- Full regression: `3955 passed in 16.66s`.
- `git diff --check`: temiz.
- Sıradaki kesin iş: Phase 2 roadmap sırasındaki `catalog component source` adapter contractı için ilk RED test.

### Phase 2 ilerleme — Catalog Component Source Adapter

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%25`
- Phase 2 status: `IMPLEMENTATION_ACTIVE`
- Yeni adapter: `CORE/atlas_catalog_component_geometry_source_adapter.py`
- Yeni test paketi: `Test/test_catalog_component_geometry_source_adapter.py`
- Mevcut Master Landmark Catalog metadata'sı semantic component reference ile canonical geometry-source result sınırında bağlandı.
- Wikidata ve OSM identity resolution desteklenir.
- Catalog identity/grammar/profile/component metadata'sı geometry bounds/anchor metadata'sından ayrı tutulur.
- Component flags bulunan catalog entry'lerde role compatibility doğrulanır.
- Adapter geometry üretmez; mesh/STL/triangle üretimi başka katmanlarda kalır.
- Focused Phase 2: `116 passed in 0.16s`.
- Related catalog/semantic regression: `137 passed in 0.25s`.
- Full regression: `3969 passed in 16.77s`.
- `git diff --check`: temiz.
- Sıradaki kesin iş: Phase 2 roadmap sırasındaki `future canonical face/head source` contractı için mevcut portrait/face/head kaynaklarını audit etmek.

### Phase 2 ilerleme — Face/Head Geometry Source Adapter

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%27`
- Phase 2 status: `IMPLEMENTATION_ACTIVE`
- Yeni adapter: `CORE/atlas_face_head_geometry_source_adapter.py`
- Yeni test paketi: `Test/test_face_head_geometry_source_adapter.py`
- Mevcut portrait landmark result canonical geometry-source descriptorına normalize edilir.
- Geometry kind `face_head_landmarks`, coordinate space `normalized_image_2d`.
- Landmark identity canonical snake_case biçimindedir.
- Deterministic bounds ve semantic anchors üretilir.
- Provider confidence ve provider provenance korunur.
- Adapter 3D head mesh veya fiziksel geometry üretmez.
- Bu contract yalnız Phase 2 source-adapter sınırıdır; canonical 3D head kararı Phase 8'e bırakılmıştır.
- Focused Phase 2: `124 passed in 0.18s`.
- Related portrait/face regression: `176 passed in 0.22s`.
- Full regression: `3977 passed in 16.92s`.
- `git diff --check`: temiz.
- Sıradaki kesin iş: Phase 2 roadmap sırasındaki `future body/pose/prop source` adapter contractı için mevcut figurative/body/pose/prop kaynaklarını audit etmek.

### Phase 2 — Geometry Source Adapter Contracts LOCKED

Status: `LOCKED`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%30`
- Phase 2 tamamlandı.
- Canonical geometry-source result ve adapter boundary kilitlendi.
- Yedi adapter ailesi tamamlandı: height-map, triangle mesh, parametric primitive, facade grammar, catalog component, face/head boundary, body/pose/prop boundary.
- Provider ve CORE sorumlulukları ayrıldı.
- Aynı semantic scene farklı adapter implementasyonlarıyla çalışabiliyor.
- Adapter resultları deterministic ve input-isolated.
- Unsupported projection mode erken fail ediyor.
- Face/head ve body/pose/prop future contracts mevcut gerçek veri sınırlarını aşmadan tanımlandı.
- Final focused: `137 passed in 0.21s`.
- Full regression: `3990 passed in 16.55s`.
- `git diff --check`: temiz.
- Acceptance gate: `PASS`.
- Sıradaki kesin iş: Phase 3 `Semantic Depth & Occlusion` için mevcut depth/layer/occlusion altyapısının audit edilmesi ve ilk RED contract.

### Phase 3 — Semantic Depth & Occlusion Composer LOCKED

Status: `LOCKED`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%36`
- `AtlasSemanticDepthOcclusionComposer` tamamlandı.
- Semantic scene → deterministic depth/occlusion composition plan contractı kilitlendi.
- Semantic depth-band ranges, layer ordering, parent-child depth inheritance ve explicit occlusion conflict reporting tamamlandı.
- `contact/embed/recess/raised` semantic depth relation contractı tamamlandı.
- Impossible embed reddediliyor.
- Semantic depth relation ile mesher-level physical depth ve Phase 4 printability policy birbirinden ayrı tutuluyor.
- Material boundary ile geometry boundary ayrı identities olarak korunuyor.
- Deterministic `depth_band` operator override ve audit record desteği tamamlandı.
- Existing scene parent-cycle validation yeniden kullanılmaktadır.
- Composer mesh/triangle/STL üretmez.
- Acceptance gate: `PASS`.
- Focused: `30 passed in 0.04s`.
- Related regression: `124 passed in 0.18s`.
- Full regression: `4020 passed in 16.68s`.
- `git diff --check`: temiz.
- Sıradaki kesin iş: Phase 4 `Physical Feature Resolver` mevcut altyapı audit ve ilk RED contract.

### Phase 4 — Physical Feature Resolver LOCKED

Status: `LOCKED`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%42`
- `AtlasPhysicalFeatureResolver` ve `AtlasPhysicalFeatureProfile` tamamlandı.
- Resolver geometry üretmez; semantic feature → deterministic physical decision dönüşümü yapar.
- Kilitlenen action set:
  - `preserve`
  - `enlarge`
  - `merge`
  - `simplify`
  - `convert_to_engraving`
  - `omit`
  - `require_operator_review`
- Raised width/height ve groove width/depth için profile-driven minimumlar tamamlandı.
- Adjacent spacing → merge, repeated density → simplify contractları tamamlandı.
- Unsupported projection/slope ve fragile connection riskleri operator review'e bağlandı.
- Semantic importance ve readability priority fiziksel karar akışında korunuyor.
- Silent feature loss yok; enlargement ve omission açık adjustment/reason kaydı taşır.
- Aynı feature farklı product size değerlerinde açıklanabilir farklı karar alabilir.
- Acceptance gate: `PASS`.
- Focused: `17 passed in 0.04s`.
- Related regression: `104 passed in 0.14s`.
- Full regression: `4037 passed in 17.01s`.
- `git diff --check`: temiz.
- Sıradaki kesin iş: Phase 5 `Surface Target & Projection V1` audit ve ilk RED contract.

### Semantic Relief Phase 5 — Surface Target & Projection V1 LOCKED

Status: `LOCKED`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%48`
- Phase 5 acceptance gate tamamlandı.
- Canonical target contract: `AtlasSurfaceTarget`.
- Canonical projection engine: `AtlasSurfaceProjectionEngine`.
- Kilitlenen target surface aileleri:
  - `flat_plane`
  - `oriented_planar`
  - `bilinear_surface`
  - `cylindrical_surface`
  - `dome_surface`
  - `vault_surface`
  - `indexed_mesh_surface`
- Her target surface canonical olarak şu fiziksel/geometrik contractları taşır:
  - stable local UV/frame identity
  - outward normal convention
  - clipping boundary
  - relief polarity
  - allowable depth envelope
  - attachment policy
  - intersection policy
  - source component identity
  - target component identity
- `indexed_mesh_surface` için explicit per-vertex `vertex_uvs` contractı zorunludur.
- Indexed mesh projection UV-space face selection ve barycentric interpolation ile deterministic world-space geometry üretir.
- Projection davranışları:
  - target dışı geometri deterministic reject edilir
  - depth-envelope ihlali reject edilir
  - `must_attach` relief target yüzeye temas etmek zorundadır
  - duplicate overlapping triangles reject edilir
  - `outward` / `inward` relief polarity bütün projection modlarında fiziksel depth yönüne uygulanır
- Orientation/winding audit artık placeholder değildir.
- Gerçek winding audit şu target ailelerinde aktif:
  - flat plane
  - oriented planar
  - bilinear surface
  - cylindrical surface
  - vault surface
  - dome surface
  - indexed mesh surface
- Existing architectural relief hattı korunmuştur; projection sistemi mevcut relief producer davranışını yeniden yazmaz.
- Existing architectural relief regression: `70 passed in 0.16s`.
- Acceptance:
  - projection sonrası orientation / winding audit: PASS
  - deterministic target boundary reject: PASS
  - physical attachment enforcement: PASS
  - depth-envelope enforcement: PASS
  - duplicate overlap detection: PASS
  - inward / outward polarity: PASS
  - arbitrary indexed mesh UV projection: PASS
  - flat projection existing relief compatibility: PASS
- Phase 5 focused validation: `31 passed in 0.06s`.
- Related regression: `157 passed in 0.26s`.
- Full regression: `4068 passed in 16.89s`.
- `git diff --check`: temiz.
- Korunan unrelated working-tree çalışmalarına reset/restore/clean uygulanmadı.
- Sıradaki kesin tek iş: Master Execution Compass Phase 6 `Architectural Ornament Library V1` audit ve ilk RED contract.

### Semantic Relief Phase 6 — Architectural Ornament Library V1 LOCKED

Status: `LOCKED`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%54`
- Phase 6 `Architectural Ornament Library V1` tamamlandı ve kilitlendi.
- Canonical catalog modelleri:
  - `AtlasArchitecturalOrnamentCatalogEntry`
  - `AtlasArchitecturalOrnamentInstance`
  - `AtlasArchitecturalOrnamentCatalog`
- Her canonical catalog entry şu contract alanlarını taşır:
  - component ID ve version
  - semantic class ve style tags
  - parametric dimensions
  - anchors
  - supported projection modes
  - minimum printable profile
  - material role
  - repetition mode ve symmetry
  - assembled / relief / kit output eligibility
  - license ve provenance
  - geometry producer identity
- Bound catalog instances deterministic ve immutable parametre contractı taşır.
- Fiziksel minimum profile ihlalleri binding aşamasında deterministic reject edilir.
- Repeated instances canonical component identity'yi korurken ayrı occurrence identity taşıyabilir.
- Phase 5 projection mode contractları catalog seviyesinde korunur.
- Mevcut geometry producer'ları mümkün olan yerlerde yeniden kullanıldı; duplicate topology/primitive altyapısı oluşturulmadı.
- Phase 6 sonunda canonical reusable aileler:
  - `arch.round_v1`
  - `archivolt.round_v1`
  - `opening.recessed_rect_v1`
  - `tracery.mullion_transom_v1`
  - `portal.surround_rect_v1`
  - `tympanum.triangular_v1`
  - `pilaster.rect_v1`
  - `column.classical_round_v1`
  - `column_base.classical_round_v1`
  - `column_capital.classical_round_v1`
  - `cornice.band_v1`
  - `frieze.band_v1`
  - `molding.rectangular_band_v1`
  - `medallion.circular_v1`
  - `rosette.circular_v1`
  - `panel.inscription_rect_v1`
  - `ornament.geometric_polygon_v1`
  - `ornament.floral_radial_v1`
  - `plaque.figurative_rect_v1`
  - `niche.recessed_arch_v1`
  - `surface_unit.brick_v1`
  - `surface_unit.stone_block_v1`
  - `surface_unit.roof_tile_v1`
- Phase 6 kapsamında eklenen reusable geometry producer'ları:
  - `AtlasFacadePortalSurroundMesher`
  - `AtlasFacadePilasterMesher`
  - `AtlasClassicalColumnDetailMesher`
  - `AtlasGeometricOrnamentMesher`
  - `AtlasFloralOrnamentMesher`
  - `AtlasRecessedArchNicheMesher`
  - `AtlasFacadeTraceryMesher`
  - `AtlasTympanumMesher`
  - `AtlasFacadeMoldingMesher`
  - `AtlasFigurativePlaqueMesher`
  - `AtlasRepeatableSurfaceUnitMesher`
- `AtlasFacadeArchMesher`, `AtlasFacadeOpeningMesher`, `AtlasFacadePanelBuilder`, `AtlasFacadeCircularPanelBuilder`, `AtlasClassicalColonnadeBuilder` ve `AtlasClosedCylinderBuilder` uygun family contractlarında yeniden kullanıldı.
- Archivolt mevcut arch producer üzerinden ayrı semantic catalog identity olarak doğrulandı.
- Tracery canonical mullion + transom kapalı component sistemiyle doğrulandı.
- Tympanum triangular pediment panel olarak reusable closed prism üretir.
- Figurative plaque Phase 6 sınırında yalnız figurative-content carrier contractıdır; insan/portre geometrisi sonraki figurative fazlara bırakılmıştır.
- Brick / stone block / roof tile aynı reusable physical surface-unit primitive'ini paylaşır; semantic identity catalog seviyesinde ayrıdır.
- Aynı canonical part farklı geçerli boyutlarda deterministic binding üretir.
- Minimum printable profile altındaki fiziksel olarak okunamaz varyantlar deterministic reject edilir.
- Catalog producer entegrasyonlarında mevcut `AtlasMeshValidator` topology gate yeniden kullanıldı.
- Phase 6 focused acceptance: `61 passed in 0.21s`.
- Phase 6 related regression: `135 passed in 0.34s`.
- Full regression: `4129 passed in 17.09s`.
- `git diff --check`: temiz.
- Korunan unrelated working-tree çalışmalarına reset/restore/clean uygulanmadı.
- Phase 6 `LOCKED`.
- Sıradaki kesin tek iş: Master Execution Compass Phase 7 `Architectural Semantic Relief Product` contractını audit etmek ve ilk RED contractı açmak.

### Semantic Relief Phase 7 — Architectural Semantic Relief Product V1 IMPLEMENTATION_ACTIVE

Status: `IMPLEMENTATION_ACTIVE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%58`
- Phase 7 `Architectural Semantic Relief Product V1` gerçek ürün doğrulama hattında aktif.
- İlk gerçek Phase 7 referansı kilitlendi:
  - `Cathédrale Notre-Dame de Strasbourg`
  - west facade / central portal
  - reference ID: `strasbourg_cathedral_central_portal_phase7_v1`
- Gerçek reference asset:
  - `Data/RELIEF/strasbourg_cathedral_phase7/strasbourg_cathedral_central_portal_reference.jpg`
  - JPEG RGB
  - `1333 × 2000`
  - `1219504 bytes`
  - SHA-256: `e9315eca500ef296c33016ad4c576a5e65dde1828d04885bd5a01ab24abcaeef`
  - license: `CC-BY-2.0`
  - provenance: `Wikimedia Commons / jeffowenphotos`
- Canonical Strasbourg reference contract:
  - `CORE/atlas_strasbourg_cathedral_phase7_reference.py`
  - `Test/test_strasbourg_cathedral_phase7_reference.py`
- Strasbourg reference mevcut `AtlasArchitecturalReliefInput` hattına bağlandı.
- Yeni image-to-relief profile identity:
  - `ARCHITECTURAL_STONE_FACADE`
  - mevcut güvenli architectural relief sayısal davranışı korunuyor
  - `ROCK_CARVED_LANDMARK` kimliği Strasbourg'a zorla uygulanmıyor.
- Phase 7 product contractı:
  - `AtlasArchitecturalSemanticReliefProduct`
  - zorunlu semantic içerik denetimleri
  - real `AtlasSurfaceTarget` binding
  - canonical `AtlasSurfaceProjectionEngine` delegation
  - operator visual acceptance
  - physical coupon acceptance
- Phase 7 baseline/semantic comparison:
  - `AtlasArchitecturalSemanticReliefComparisonReport`
  - generic score comparison
  - `AtlasPhysicalFeatureDecision` tabanlı feature-retention comparison
  - semantic readability görsel operatör kabulünden ayrı tutuluyor.
- Phase 7 mandatory semantic içerik contractı:
  - recessed opening
  - raised ornament
  - figurative or emblematic feature
  - inscription or panel
  - minimum three semantic depth bands
  - real target-surface projection
- Strasbourg real component geometry milestone tamamlandı:
  - `build_strasbourg_cathedral_phase7_component_meshes()`
  - dört canonical catalog instance mevcut Phase 6 geometry producer'larına doğrudan bağlandı
  - recessed opening -> `AtlasFacadeOpeningMesher`
  - archivolt -> `AtlasFacadeArchMesher`
  - figurative tympanum carrier -> `AtlasFigurativePlaqueMesher`
  - panel carrier -> `AtlasFacadePanelBuilder`
  - occurrence identity ve canonical semantic class mesh metadata üzerinde korunuyor
  - dört component mesh ayrı ayrı closed/manifold topology gate geçiyor
  - mevcut V1 panel yalnız semantic panel carrier'dır; gerçek inscription varlığı iddia edilmez.
- Strasbourg projection milestone tamamlandı:
  - dört gerçek component mesh canonical `oriented_planar` `AtlasSurfaceTarget` üzerine `AtlasSurfaceProjectionEngine` ile project ediliyor
  - facade-space `(X, Y, Z)` producer geometrisi projection-local `(U, V, depth)` contractına deterministic dönüştürülüyor
  - attachment ve `0.0 .. 1.8 mm` depth-envelope gate geçiliyor
  - closed-solid tangent side faces winding audit tarafından artık yanlış violation sayılmıyor
  - `opening.recessed_rect_v1` inward polarity ile project ediliyor
  - archivolt, figurative tympanum carrier ve panel carrier outward polarity ile project ediliyor
  - projection sonucu occurrence identity ve canonical semantic class metadata'sını koruyor
  - recessed opening'in inward davranışı target outward normal boyunca signed-depth contractıyla doğrulandı.
- Strasbourg semantic depth / occlusion composition milestone tamamlandı:
  - mevcut Phase 3 `AtlasSemanticDepthOcclusionComposer` Phase 7 Strasbourg referansına bağlandı
  - canonical facade surface scene graph içinde gerçek target component olarak temsil ediliyor
  - semantic sıra deterministic: `recessed -> primary -> raised_primary -> raised_secondary`
  - composer depth-band aralıkları canonical normalize `0.0 .. 1.0` contractını koruyor
  - projected gerçek geometry üzerinde recessed opening ile üç ayrı raised fiziksel seviye ayrışıyor
  - figurative tympanum ve archivolt için gereksiz yükseklik zorlaması yapılmadı; mevcut gerçek producer geometrisi korundu
  - composition plan `conflicts == ()`
- Phase 7 focused validation: `34 passed in 0.05s`.
- Phase 7 related regression: `124 passed in 0.16s`.
- Full regression: `4149 passed in 16.44s`.
- `git diff --check`: temiz (`EXIT=0`).
- Korunan unrelated working-tree çalışmalarına reset/restore/clean uygulanmadı.
- Phase 7 henüz `LOCKED` değildir.
- Sıradaki kesin tek iş: Strasbourg semantic ve generic height-map baseline çıktısını aynı fiziksel ürün contractında karşılaştıran gerçek comparison path'i test-first bağlamak.


## 18 Aug 2026 — Phase 7 Portrait Semantic Diagnostic Checkpoint

Status:
- Semantic Relief, Figurative & Kit System V1 remains active.
- Phase 7 — Architectural Semantic Relief Product V1 remains `IMPLEMENTATION_ACTIVE`.
- This portrait work is a controlled Phase 7 diagnostic experiment; Phase 8 / Phase 9 have NOT started.
- ATLAS overall progress remains 68%.
- Active program progress remains 58%.

Portrait diagnostic findings:
- Real two-person portrait source was processed through the existing image-relief pipeline.
- Illumination normalization and aspect-correct crop were validated.
- MediaPipe 0.10.35 runtime was isolated in a dedicated Python 3.12 environment.
- The front face produced a valid 478-point XYZ landmark set.
- MediaPipe Z is anatomically coherent enough to act as relative coarse-form evidence, but it is provider-estimated relative depth, not scanned 3D geometry.
- Full-face landmark-Z replacement / hybrid was visually rejected because it softened identity-bearing facial detail too aggressively.
- The existing linear `AtlasReliefFaceDepthCalibrator` passes synthetic tests but did not materially restore the real shadow-compressed face volume; it is NOT locked as a production capability and remains experimental.
- A root cause was found for the persistent flat plateaus around the nose and lips:
  `ROCK_CARVED_LANDMARK.depth_upper_percentile=97.0` clips valid portrait facial peaks in `AtlasReliefDepthCompressor`.
- Measured 97.0 percentile behavior:
  - nose AT_ONE = 16.671%
  - mouth AT_ONE = 10.597%
  - nose gradient-near-zero = 22.454%
- Diagnostic `depth_upper_percentile=99.5` result:
  - nose AT_ONE = 0.249%
  - mouth AT_ONE = 0.438%
  - nose gradient-near-zero = 6.210%
- 100.0 removes clipping completely but compresses the useful visual range more than desired.
- Therefore 99.5 is the accepted current PORTRAIT DIAGNOSTIC baseline; it has NOT yet been added as a canonical production profile.
- Canonical diagnostic STL:
  `OUTPUT/RELIEF/portrait_semantic_experiment_v1/two_person_portrait_PORTRAIT_BASELINE_99_5_PREVIEW.stl`
  - 4,037,596 triangles
  - approx. 80.0 x 84.0816 x 2.6 mm
- Bambu Studio visual inspection confirms the severe 97-percentile nose plateau is substantially reduced and face volume is more continuous.
- Remaining limitation: facial relief is still too luminance/texture-driven around eyes, nose-understructure, mouth and skin texture.

Validation at this checkpoint:
- focused portrait/profile: 26 passed in 0.08s
- Strasbourg Phase 7 reference: 9 passed in 0.04s
- full regression: 4152 passed in 16.96s
- git diff --check: EXIT=0

Phase 7 architectural status remains unchanged:
- Strasbourg real-photo generic relief baseline is valid.
- Semantic-only primitive replacement was visually rejected.
- Image relief remains the main form carrier.
- Semantic systems should operate as local structural/depth corrections, not wholesale replacement of source identity.

Exact next single task:
- Build a non-destructive diagnostic using MediaPipe XYZ only as LOW-FREQUENCY LOCAL structural support for the front-face nose and upper/lower-lip regions on top of the accepted 99.5 portrait baseline.
- Do not modify the rest of the face.
- Do not return to full-face landmark hybrid.
- Do not start Phase 8 or Phase 9.
- Do not create a canonical portrait product profile until this local correction is visually validated.


## 18 Aug 2026 — Phase 7 Local Semantic Depth Diagnostic Accepted

Status:
- Phase 7 remains `IMPLEMENTATION_ACTIVE`.
- Portrait work remains a controlled Phase 7 diagnostic; Phase 8 / Phase 9 have NOT started.
- No canonical portrait product profile has been created.

Accepted diagnostic result:
- The accepted portrait image baseline remains the real-photo relief pipeline with diagnostic
  `depth_upper_percentile=99.5`.
- Full-face MediaPipe XYZ replacement/hybrid remains REJECTED because it softens identity-bearing detail.
- Strict-local MediaPipe XYZ correction for the foreground face nose + mouth region is DIAGNOSTIC ACCEPTED.
- MediaPipe XYZ is used only as low-frequency relative structural support; it is not treated as scanned 3D geometry.
- The original photo-derived height map remains the primary form/identity carrier.
- Correction is spatially restricted to the selected local anatomical masks.
- Verified outside-mask preservation:
  `OUTSIDE_MAX_DELTA=0.000000000000`.
- Local correction metrics:
  - touched pixels: 54,077
  - local mean absolute normalized depth delta: 0.037910
  - local max absolute normalized depth delta: 0.120165
- Corrected physical diagnostic STL:
  `OUTPUT/RELIEF/portrait_semantic_experiment_v1/two_person_portrait_PORTRAIT_99_5_LOCAL_NOSE_MOUTH_Z_PREVIEW.stl`
  - triangles: 4,037,596
  - approx. 80.0 x 84.0816 x 2.6 mm
- Bambu Studio oblique-angle inspection showed a small but real improvement in nose / nose-understructure continuity without visible whole-face identity loss or mask-boundary artifact.
- Lip improvement is more limited and does not justify further parameter sweeping at this stage.

Architectural implication for Phase 7:
- Image-derived relief should remain the main form carrier.
- Semantic/provider-derived geometry should be applied as bounded local structural correction at identity-critical regions.
- Semantic geometry should NOT wholesale replace real image form.
- This diagnostic question is considered answered; further portrait tuning is parked.

Validation immediately before this diagnostic sequence:
- focused portrait/profile: 26 passed in 0.08s
- Strasbourg Phase 7 reference: 9 passed in 0.04s
- full regression: 4152 passed in 16.96s
- git diff --check: EXIT=0

Exact next task:
- Return to the official Phase 7 Strasbourg path.
- Build the real semantic-vs-generic comparison from actual generated outputs / measurable retained semantic evidence.
- Do NOT recreate hard-coded comparison decisions.
- Do NOT continue portrait parameter tuning.

## Phase 7 Strasbourg Semantic Structural Depth Checkpoint — 18 August 2026

**Program:** Semantic Relief, Figurative & Kit System V1
**Phase:** Phase 7 — Architectural Semantic Relief Product V1
**Status:** `IMPLEMENTATION_ACTIVE`
**ATLAS overall completion:** 68%
**Active program completion:** 58%

Phase 7 remains focused on the real Strasbourg Cathedral central-portal reference. The real photo-derived relief remains the primary identity/form carrier; semantic geometry is a bounded structural enhancement layer and must not replace the photographic architecture.

### Checkpoint capability completed

The Strasbourg comparison path now has the missing measurable structural-depth bridge:

- `AtlasArchitecturalSemanticReliefFeatureMeasurement`
  - reports active pixels, retained pixels, and retained-active-pixel ratio from the existing physical detail filter;
  - connected-component retention ratio is no longer treated as the primary readability metric because component fragmentation can distort that score.
- `AtlasProjectedSemanticMeshDepthRasterizer`
  - rasterizes projected triangle meshes into deterministic depth maps;
  - supports world-space projected meshes through `AtlasSurfaceTarget`;
  - converts world coordinates back to target-local `U/V + signed normal depth`;
  - respects relief polarity during overlap resolution:
    - outward -> greatest signed depth;
    - inward -> most recessed signed depth.
- `AtlasFacadeArchBandMesher`
  - adds the minimum closed/manifold arch-band geometry required for the Strasbourg archivolt;
  - replaces the previous solid arch behavior only in the Strasbourg Phase 7 reference path.
- Strasbourg projected semantic depths are now physically coherent:
  - recessed opening: `-0.800 mm`;
  - archivolt: `+0.900 mm`;
  - figurative tympanum: `+0.700 mm`;
  - panel: `+0.500 mm`.
- The previous archivolt solid-overlap defect was corrected with the arch-band geometry.
- Strasbourg opening, archivolt, figurative tympanum, and panel placement has been re-registered against the previously accepted real image-space registration instead of the earlier generic canonical placements.
- The rejected strict-local detail-gain experiment remains rejected as a Phase 7 superiority proof. It was perfectly local but produced only a very small pixel-retention gain and did not provide sufficient visual/semantic superiority evidence.
- No hard-coded preserve/omit comparison decisions were reintroduced.
- Portrait diagnostic work remains parked; Phase 8/9 has not started.

### Validation at this checkpoint

- Focused Phase 7 geometry/raster/Strasbourg tests: `17 passed in 0.19s`
- Related regression: `68 passed in 0.27s`
- Full regression: `4163 passed in 16.82s`
- `git diff --check`: `EXIT=0`

### Exact next task after the pause

Run one post-registration Strasbourg overlap + signed-depth audit using the newly registered component geometry. Verify that the opening, archivolt, figurative tympanum, and panel occupy physically coherent regions with no unintended destructive overlap.

If that audit is clean, build the combined semantic structural-depth reference from the real projected component outputs and apply it only as a bounded/local structural enhancement to the real photo-derived generic Strasbourg relief. Then produce the next measurable generic-vs-semantic A/B comparison.

Do not start another parameter sweep, portrait work, Phase 8/9, unrelated refactor, or horizontal scope expansion before this exact Phase 7 task is completed.

## Phase 7 Strasbourg Physical Production Checkpoint — 18 August 2026

**Program:** Semantic Relief, Figurative & Kit System V1
**Phase:** Phase 7 — Architectural Semantic Relief Product V1
**Status:** `IMPLEMENTATION_ACTIVE`

The official Phase 7 Strasbourg path has now reached the physical-coupon gate. The real photo-derived relief remains the primary identity/form carrier; semantic geometry remains a bounded local structural enhancement and does not replace the photographic architecture.

### Digital product path completed

- Post-registration overlap + signed-depth audit is clean.
- The real projected semantic component outputs are combined into a structural-depth reference.
- Bounded/local semantic enhancement is applied only on top of the real photo-derived baseline.
- Generic-vs-semantic A/B comparison is now measurable from generated evidence:
  - generic retained semantic evidence score: `0.75`
  - semantic retained evidence score: `1.00`
  - semantic readability delta: `+0.25`
  - comparison report: `PASS`
- Operator visual review of the semantic A/B remains accepted for the architectural comparison path.
- Image relief remains the main identity/form carrier.
- Semantic-only primitive replacement remains rejected.

### Physical production conditioning completed

The initial photo-derived physical coupon exposed excessive high-frequency surface activity in Bambu Studio. The solution was kept product-facing and did not alter source truth.

Locked production conditioning sequence:

1. bounded/local semantic enhancement
2. architectural physical detail-scale conditioning
3. polarity-aware positive/negative micro-detail filtering
4. triangle-safe slope conditioning
5. closed/manifold physical mesh production
6. official physical quality report

Locked physical detail-scale contract:

- `minimum_feature_mm = 0.8`
- `activity_threshold = 0.02`
- `minimum_density = 0.25`

The previous absolute-value connected-component interpretation produced a percolation defect: one component contained `91,787` pixels and `92.3587%` of active micro-detail. Positive and negative relief polarities are now filtered independently before recomposition.

Polarity-aware result:

- original active micro-detail pixels: `99,381`
- retained active pixels: `62,232`
- culled active pixels: `37,149`
- culled active micro-detail: `37.380385%`
- positive components: `6,937`
- negative components: `5,352`

Semantic structural protection remains exact during this product-facing detail conditioning.

### Triangle-safe physical slope gate

The physical slope conditioner is derived from the locked architectural risk profile and the real triangular mesh topology.

- warning slope limit: `55.0 deg`
- critical slope limit: `75.0 deg`
- final maximum physical slope: `54.929772603 deg`
- warning slope samples: `0%`
- critical slope samples: `0%`
- warning slope surface area: `0%`
- critical slope surface area: `0%`
- official physical quality status: `PASS`
- `is_print_ready = True`

Final physical topology:

- dimensions: `80 x 120 x 2.6 mm`
- triangles: `617,600`
- open edges: `0`
- non-manifold edges: `0`

Canonical current coupon:

`OUTPUT/RELIEF/strasbourg_cathedral_phase7/strasbourg_cathedral_phase7_polarity_conditioned_physical_coupon_80x120mm.stl`

Canonical current shaded preview:

`OUTPUT/RELIEF/strasbourg_cathedral_phase7/strasbourg_cathedral_phase7_polarity_conditioned_shaded_preview.png`

### Bambu Studio validation

Current slicer validation used:

- Bambu Lab P2S
- `0.4 mm` nozzle
- `0.20 mm` layer height
- total model height: `2.60 mm`
- 13 layers
- 0 filament changes
- approx. `15.94 g`
- approx. `1 h 14 min`

The polarity-aware coupon has passed the slicer readability gate:

`ACCEPTED_FOR_PHYSICAL_COUPON`

This is NOT physical-object acceptance.

### Validation at this checkpoint

- Strasbourg focused: `18 passed in 69.65s`
- related regression: `89 passed in 69.13s`
- full regression: `4180 passed in 86.78s`
- `git diff --check`: clean

### Remaining Phase 7 gate

Physical coupon printing is currently pending because the printer is occupied.

Therefore:

- `physical_coupon_accepted = False / PENDING`
- Phase 7 remains `IMPLEMENTATION_ACTIVE`
- Phase 7 is NOT yet `LOCKED`
- Phase 8 has NOT started

Exact next physical task when the printer becomes available:

Print the canonical polarity-conditioned Strasbourg coupon, inspect architectural readability and physical feature survival on the real object, and record explicit operator acceptance or rejection.

Do not perform another parameter sweep, unrelated relief tuning, portrait work, or Phase 8/9 production work before that physical gate is resolved.

## ATLAS Five-Pillar Product & Production Backend Master Plan — 18 August 2026

**Status:** `STRATEGIC_DIRECTION_LOCKED / EXECUTION_NOT_STARTED`
**Current execution authority:** existing `Semantic Relief, Figurative & Kit System V1` roadmap
**Current active phase:** Phase 7 — `Architectural Semantic Relief Product V1`

### Purpose

This master plan defines the post-current-program technical/product direction required to make ATLAS capable of supporting five commercial product pillars from one shared backend and production architecture.

The five product pillars are:

1. **Places**
   - personalized location, city, terrain, home, university, island, destination and related geospatial products.

2. **People & Memories**
   - personalized photo, person, family, couple, pet and memory-based relief / figurative products.

3. **Stories**
   - compositions combining place, person, landmark, date, text, symbol and personal meaning.

4. **Architecture & Collections**
   - pre-engineered non-personalized landmark, architectural, cultural-heritage and collectible products.
   - strategic intent: maintain a reusable global digital catalog so an order triggers production rather than redesign from zero.

5. **Model Kits**
   - pre-engineered multipart architectural/model-building products.
   - may include hundreds or thousands of numbered parts.
   - may be pre-colored or paint-ready.
   - production package may include grouped/bagged parts, assembly instructions, paint specification, adhesive specification and related kit contents.

### Ten-step backend/product master plan

1. **Close Phase 7 — Architectural Semantic Relief Product V1**
   - complete the existing official Phase 7 physical coupon gate and LOCK Phase 7 only after its official acceptance criteria are satisfied.

2. **Face / Portrait Engine**
   - execute official Phase 8 `Canonical Face/Head Decision Gate`.
   - execute official Phase 9 `Identity-Preserving Portrait Relief V1`.
   - establishes the core backend capability for `People & Memories`.

3. **Figurative Engine**
   - execute official Phase 10 `Figurative Body, Pose & Prop Grammar V1`.

4. **Personalized Story Engine**
   - execute official Phase 11 `Personalized Story Composer V1`.
   - establishes composition across place, person, landmark, date, text, symbol and meaning.

5. **Shared Component & Kit Engine**
   - execute official Phase 12 `Shared Component Catalog & Kit Contract V1`.
   - establishes reusable components, part identity and assembly/kit contracts.

6. **Modular Model Kit Engine**
   - execute official Phase 13 `Modular Architectural Kit Prototype V1`.
   - establishes decomposition of architectural products into manufacturable assembly kits and validates the `Model Kits` pillar.

7. **Unified Product Orchestration**
   - execute official Phase 14 `Unified Product Orchestration`.
   - one backend must orchestrate the five product pillars without duplicating independent product engines.

8. **Commercial Production Gate**
   - execute official Phase 15 `Commercial Production Gate`.
   - production readiness must cover geometry, physical printability, topology, material/color identity, QA and production-package requirements.

9. **Global Architecture & Product Catalog**
   - expand reusable pre-engineered digital inventory after the relevant official engine gates are complete.
   - intended coverage includes landmarks, cathedrals, churches, mosques, towers, stadiums, castles, bridges, universities, heritage structures, terrain/island products and other validated product families.
   - catalog growth must reuse canonical engines/components and must not become uncontrolled one-off hard-coding.

10. **Production & Fulfillment Backend**
    - build the non-customer-facing production infrastructure needed to turn validated product definitions into repeatable manufacturing packages.
    - intended scope includes job generation/routing, material/color package, kit batching, part grouping/numbering, assembly-document generation, QA records, packaging specification and shipping-ready production output.

### Completion meaning

When all ten steps are completed and accepted, ATLAS should have the technical/product backend required to support all five commercial pillars from one shared production architecture:

- Places
- People & Memories
- Stories
- Architecture & Collections
- Model Kits

This completion statement explicitly excludes the customer-facing commercial platform.

### Hard execution boundaries — DO NOT VIOLATE

1. **This plan does NOT replace, renumber, shorten, expand or bypass the official `Semantic Relief, Figurative & Kit System V1` roadmap.**
2. **Official Phase 7–15 order remains authoritative.**
3. **No later official phase may production-start before the current phase satisfies its documented gate.**
4. **Phase 8 must not start before Phase 7 is physically accepted and LOCKED.**
5. **Phase 9–11 remain subject to the official Phase 8 decision gate.**
6. **Steps 9 and 10 of this master plan are strategic continuation work; they do not authorize premature implementation while official dependency gates remain open.**
7. **The five commercial pillars are product/business classifications, not permission to create parallel engines or duplicate existing CORE systems.**
8. **Shared infrastructure must be reused wherever technically valid; horizontal duplication is prohibited without explicit architectural justification.**
9. **No product-specific hard-code may be promoted into general engine behavior without verified catalog/provenance and an explicit reusable contract.**
10. **Source truth, semantic identity, physical material identity and commercial output role remain separate concepts.**
11. **Preview output alone is never physical production proof. Existing topology, printability, slicer and physical validation gates remain mandatory where applicable.**
12. **Physical parts must satisfy the applicable closed/manifold and production-quality contracts before product-ready status.**
13. **Customer-facing configurator, storefront, account system, checkout, pricing UI, order UX and marketing platform are explicitly OUT OF SCOPE for this ten-step backend/product master plan.**
14. **Customer-platform work is a later separate program and must not destabilize or prematurely reshape the production engine.**
15. **Global catalog expansion must follow validated reusable engines; do not attempt to model the world manually before the corresponding product engine is locked.**
16. **Model Kit catalog expansion must not begin at scale before Phase 12 and Phase 13 contracts are accepted.**
17. **Production/Fulfillment automation must consume canonical product outputs; it must not become a second geometry engine.**
18. **Protected unrelated working-tree work must not be reset, cleaned, restored, deleted or staged as a side effect of this plan.**
19. **No `git add .`; stage only explicitly reviewed files.**
20. **At every meaningful milestone: focused tests -> related regression -> `git diff --check` -> full regression -> documentation -> explicit staging -> commit -> push -> HEAD/origin verification.**

### Immediate execution state

This strategic plan is recorded for continuity only.

It does NOT change the current exact task:

- Phase 7 — Architectural Semantic Relief Product V1 is `LOCKED`.
- Strasbourg digital, slicer and physical coupon gates are complete.
- Strasbourg V4 physical coupon is `ACCEPTED`.
- `physical_coupon_accepted = True / ACCEPTED`.
- Phase 8 has NOT started.
- Phase 8 — Canonical Face/Head Decision Gate is the next official roadmap phase.

Until that gate is resolved, this new master plan must not trigger additional implementation work.

## 19 Aug 2026 — Phase 7 Strasbourg Physical Coupon V4 Checkpoint

**Phase:** Phase 7 — Architectural Semantic Relief Product V1
**Status:** `IMPLEMENTATION_ACTIVE`

Strasbourg physical-ground-truth refinement reached V4 while preserving the locked Phase 7 architecture: the real photo-derived relief remains the primary identity/form carrier and bounded semantic correction is still reapplied only after physical photo-carrier conditioning.

### V4 refinement

- Previous V3 physical smoothing: `sigma=0.60`, `radius=2`.
- V4 physical smoothing: `sigma=1.00`, `radius=3`.
- Smoothing is applied only to the photo-conditioned carrier before bounded semantic correction.
- Semantic correction itself is not blurred.
- Numerical carrier audit showed mean absolute Laplacian decreasing from `0.08180509` at V3 to `0.04744589` at V4, approximately a 42% reduction in high-frequency surface activity.
- A stronger `sigma=1.20`, `radius=4` candidate was measured but deliberately not adopted because of increased risk of eroding meaningful architectural relief.

### V4 digital / slicer assessment

- The previous worm-like / cable-like micro-ridge appearance is substantially reduced.
- The surface is visibly calmer without losing the principal Gothic portal hierarchy.
- Opening, archivolt, central vertical structure, figurative tympanum region and architectural bands remain readable.
- V4 is therefore the current physical-coupon candidate; no V5 refinement is authorized before physical ground-truth evaluation.

### Validation

- Strasbourg focused V4 contract: `1 passed`.
- Full Strasbourg reference suite: `20 passed in 105.72s`.
- Related Phase 7 regression: `94 passed in 103.87s`.
- Full regression: `4191 passed in 119.98s`.
- V4 STL: `OUTPUT/RELIEF/strasbourg_cathedral_phase7/strasbourg_cathedral_phase7_physical_coupon_v4_smoothed_80x120mm.stl`.
- Triangle count: `617600`.
- Open edges: `0`.
- Non-manifold edges: `0`.
- Printable topology: `True`.
- Quality status: `PASS`.

### Remaining Phase 7 gate

- Physical V4 coupon printing is still `PENDING` because the printer is occupied by the current Dalyan production job.
- Phase 7 remains `IMPLEMENTATION_ACTIVE` and is NOT `LOCKED`.
- When the printer becomes available, print V4 and explicitly evaluate:
  1. survival/removal of the former worm-like micro-ridges on the real object;
  2. portal readability at normal viewing distance;
  3. preservation of small architectural/stone detail without muddying;
  4. overall physical product acceptance or rejection.
- Phase 8 must not start before this physical acceptance gate is completed.

## 20 Aug 2026 — Phase 7 Strasbourg Physical ACCEPT / LOCK

**Phase:** Phase 7 — Architectural Semantic Relief Product V1
**Status:** `LOCKED`

The canonical Strasbourg V4 physical coupon was printed and physically inspected after the completed digital, topology and slicer gates.

### Physical acceptance

- V4 physical coupon: `ACCEPTED`.
- The former worm-like / cable-like high-frequency ridge character is materially reduced on the real print.
- Main portal hierarchy remains physically readable: opening, archivolt, central vertical structure, tympanum region and architectural bands survive.
- Small architectural/stone detail remains present without unacceptable muddying.
- No collapsed major region, destructive smoothing failure or print defect invalidating the Phase 7 product contract was observed.
- V4 therefore satisfies the mandatory Phase 7 physical-ground-truth gate.
- No V5 refinement is required or authorized for Phase 7 closure.

### Locked V4 production reference

- Physical smoothing: `sigma=1.00`, `radius=3`.
- Photo-derived relief remains the primary identity/form carrier.
- Bounded semantic correction remains a local structural enhancement and is applied after physical photo-carrier conditioning.
- STL: `OUTPUT/RELIEF/strasbourg_cathedral_phase7/strasbourg_cathedral_phase7_physical_coupon_v4_smoothed_80x120mm.stl`.
- Triangle count: `617600`.
- Open edges: `0`.
- Non-manifold edges: `0`.
- Printable topology: `True`.
- Quality status: `PASS`.
- Physical coupon acceptance: `True`.

### Roadmap transition

- Phase 7 is now formally `LOCKED`.
- Phase 8 has NOT started.
- The next official roadmap phase is Phase 8 — Canonical Face/Head Decision Gate.
- Planned packaging production and the already-open physical-product Defect #4 cleanup may be completed as an operational interlude; they do not renumber, bypass or start Phase 8.

## 20 Aug 2026 — ATLAS Full Continuity & Execution Authority

### Continuity purpose
This record is the handover authority for the next engineer/model. Historical records remain valid; this section binds the current mission, roadmap state, physical evidence, open operational work and exact forward execution so the user does not need to reconstruct project context manually.

### ATLAS mission
ATLAS is one shared generative physical-product engine spanning location, terrain, architecture, semantic relief, human identity, personalized stories and modular kits. The five commercial pillars remain: Places; People & Memories; Stories; Architecture & Collections; Model Kits. Shared CORE infrastructure must be reused; independent one-off product engines and premature horizontal duplication are prohibited.

Canonical backend direction remains: source evidence -> semantic interpretation -> canonical geometry -> physical feature resolution -> composition -> manufacturing validation -> production package -> commercial production gate. Customer-facing storefront/configurator/account/checkout work remains outside the current engine program.

### Official roadmap state
Semantic Relief, Figurative & Kit System V1 contains 16 phases, 0 through 15. Phases 0-7 are LOCKED. Phase 8 Canonical Face/Head Decision Gate is the next active phase after this documentation checkpoint. Phases 9-15 are NOT STARTED. Phase 9 may not production-start before Phase 8 reaches explicit GO + LOCK.

Roadmap meaning: 0-7 establish semantic/physical world and architectural product generation; 8-11 add human identity and personalized storytelling; 12-15 establish reusable catalog/kit architecture, unified orchestration and commercial production gating.

### Phase 7 and physical defect state
Strasbourg Cathedral V4 is the locked Phase 7 physical reference. Real-photo relief remains the primary identity/form carrier; bounded semantic correction remains local structural enhancement after physical carrier conditioning. V4 sigma=1.00 radius=3 was physically ACCEPTED; topology is closed/manifold with 0 open and 0 non-manifold edges. No V5 is authorized for Phase 7 closure.

Physical Defects #1 and #2 have permanent software fixes. Defect #3 root-cause software corrections are complete with later physical validation separate. Defect #4 software hardening is complete: final scaled tree trunk minimum 1.50 mm, TREE_SEGMENTS 18, classical round column minimum 1.2 mm, tracery mullion/transom minimum 1.2 mm; related regression 84 passed, full regression 4220 passed; code commit bbe59fa, documentation commit d292f9a. Future full-scene physical acceptance does not reopen Phase 7.

### Existing portrait evidence
Pre-Phase-8 portrait work is diagnostic evidence, not production portrait capability. Image/luminance depth alone is insufficient as canonical identity geometry. Full-face MediaPipe XYZ replacement was rejected because it softened identity-bearing detail. MediaPipe XYZ may provide bounded low-frequency structural evidence but is not scanned 3D geometry. Diagnostic depth_upper_percentile=99.5 reduced facial peak clipping; strict-local nose/mouth structural correction was diagnostically accepted. AtlasReliefFaceDepthCalibrator remains experimental. No canonical portrait production profile has been locked.

### Phase 8 mission — ATLAS Human Identity Architecture Gate
Phase 8 must define the canonical identity representation shared by Phase 9 portrait relief, Phase 10 figurative systems, Phase 11 personalized stories and later kit/orchestration work. It is not a single-face demo task.

Current benchmark direction: full-3D rather than 2.5D canonical representation; stable/fixed topology; separate identity, pose, expression, asymmetry and person-specific detail; portrait relief as an output adapter rather than canonical geometry; symmetry only as prior/regularizer; hair as a separate semantic component; explicit insufficient-evidence BLOCKED behavior; commercial license/privacy/runtime evidence before any external model becomes a production dependency.

Preferred architecture candidate for benchmark is hybrid: stable parametric/fixed-topology canonical head plus person-specific detail. This is a preferred candidate, not yet a final dependency decision.

### Phase 8 internal plan
8.0 Input Evidence Contract — define frontal, 3/4, profile, multi-view, video and single-image fallback evidence classes plus BLOCKED conditions.
8.1 Canonical Topology Contract — define full-3D stable topology, correspondence and semantic-region boundaries without prematurely binding to one provider.
8.2 Identity Shape Contract — separate identity-bearing geometry from pose, expression and residual detail.
8.3 Landmark & Dense Correspondence Contract — define their roles; landmark error alone is not proof of likeness.
8.4 Camera / Pose Normalization — separate focal/perspective effects, camera pose and head pose from identity geometry.
8.5 Expression Separation — keep smile, jaw, eyelid and other expression state out of canonical identity shape.
8.6 Asymmetry Preservation — symmetry may regularize, but meaningful real asymmetry must survive.
8.7 Head Semantic Boundary — define face, ears, jaw, neck and eyes ownership; hair separate; beard/moustache may be separate detail layers.
8.8 Identity Confidence Gate — define evidence quality, confidence and failure reasons; architecture decision GO/HOLD/REJECT and production BLOCKED_INSUFFICIENT_IDENTITY_EVIDENCE behavior.
8.9 Physical Representation Gate — prove one canonical identity can survive conversion to relief, bust, figurine head and story/kit component including physical minimums and LoD.
8.10 Canonical Benchmark & LOCK — compare parametric/fixed-topology, direct neural dense reconstruction and hybrid canonical+detail approaches. Mandatory evidence includes identity preservation, multi-view consistency, silhouette/profile, head ratios, jaw/chin, nose projection, orbital/cheek volume, expression/pose separation, topology, physical suitability, Apple Silicon/runtime, reproducibility, privacy/data retention, commercial license/model-weight/dataset restrictions and processing cost/time. Close only with explicit GO/HOLD/REJECT; Phase 9 requires GO + LOCK.

### FLAME and external-model status
The 21 Jul 2026 FLAME 2023 Open selection remains historical/provisional evidence and a strong benchmark candidate, but no longer authorizes production dependency by itself. Phase 8 must re-audit commercial licensing, attribution, model/data/weight restrictions, privacy, runtime, identity preservation and downstream physical suitability. DECA, MICA, EMOCA and similar systems remain research/benchmark references unless a separately verified commercial-use path exists.

### Packaging operational state
Packaging is an operational interlude and does not alter roadmap numbering. Physically validated gift-box connector contract: male engagement 4.0 mm; female recess depth 4.2 mm; clearance 0.05 mm per side; 28.1 mm female against 28.0 mm male accepted; 28.2/28.3 too loose. Architecture: BASE top male -> MIDDLE bottom female/top male -> LID bottom female.

Tiered support V2 work uses a 28 mm module with shelf levels 7/14/21/28 mm, 2.0 mm wall, 2.0 mm shelf and 8 mm corner engagement while preserving legacy 25/50 behavior. Current gift contains seven scenes, not the earlier eight-scene assumption. Do not lock final MIDDLE height until seven-scene distribution and support stack are recalculated. Do not print final LID until raised personalization is finalized. Full-size BASE has been sent to physical printing using the validated connector contract. Packaging/support changes remain separate from Phase 8 work.

### Working-tree and execution discipline
Intentional modified/untracked product, packaging, portrait-diagnostic, calibration, preview and source-data work may exist. Never reset/clean/restore/delete unrelated work. Never use git add . Stage only reviewed files. Preserve Data/OSM and other intentional source data.

Meaningful milestones follow: RED contract -> minimal implementation -> focused tests -> related regression -> git diff --check -> full regression -> documentation -> explicit staging -> commit -> push -> HEAD==origin/main verification. Preview quality alone is never production proof; physical outputs require applicable topology, slicer and physical gates.

### Exact forward execution
1. Commit and push this continuity synchronization without staging unrelated work.
2. Activate Phase 8 Canonical Face/Head Decision Gate.
3. Start only Phase 8.0 Input Evidence Contract.
4. Audit existing face/head source-adapter and portrait diagnostic contracts before creating new CORE abstractions.
5. Write the first RED evidence-classification and BLOCKED-semantics contract.
6. Do not begin Phase 9 production portrait implementation.

## 20 Aug 2026 — Phase 8.0 Input Evidence Contract LOCK

**Program:** Semantic Relief, Figurative & Kit System V1
**Phase:** 8 — Canonical Face/Head Decision Gate
**Sub-phase:** 8.0 — Input Evidence Contract
**Status:** `LOCKED`

Phase 8 implementation formally started with a provider-independent identity-input evidence boundary. This milestone deliberately does NOT create canonical head geometry or identity confidence.

### Locked architectural separations

- raw portrait input evidence != landmark-provider result;
- landmark-provider confidence != identity evidence confidence;
- input usability != identity likeness/confidence;
- provider-defined landmark Z != canonical metric head depth;
- evidence coverage != canonical 3D reconstruction;
- no 8.0 contract claims vertices, faces, head mesh or production portrait geometry.

### New contracts

- `CORE/atlas_portrait_input_evidence.py`
  - immutable raw evidence identity;
  - media kind: image/video;
  - canonical view classes: front, left/right three-quarter, left/right profile, unknown;
  - dimensions and metadata are normalized without embedding landmark or geometry responsibilities.

- `CORE/atlas_portrait_input_evidence_set.py`
  - immutable multi-evidence collection;
  - unique evidence IDs;
  - deterministic coverage classes:
    - `high_confidence_multiview`: front + three-quarter + profile;
    - `multiview_partial`: front + three-quarter;
    - `single_view_fallback`: front only;
    - `insufficient`: evidence without adequate frontal identity coverage;
  - insufficient coverage returns `BLOCKED_INSUFFICIENT_IDENTITY_EVIDENCE`.
  - coverage-class wording does not constitute final identity confidence.

- `CORE/atlas_portrait_input_quality_observation.py`
  - immutable provider-independent observations for face detection, face coverage, occlusion, blur and perspective distortion;
  - observations do not claim identity confidence or geometry.

- `CORE/atlas_portrait_input_usability_gate.py`
  - combines evidence coverage with matching quality observations;
  - returns deterministic `ACCEPTED` or `BLOCKED` usability result;
  - explicit blocked reasons cover missing face, insufficient face coverage, excessive occlusion, excessive blur, excessive perspective distortion and insufficient identity-view evidence;
  - requires exactly one quality observation for every evidence item.

### Initial usability policy

Current explicit policy constants are:

- minimum face coverage ratio: `0.18`;
- maximum occlusion ratio: `0.35`;
- minimum blur score: `0.40`;
- maximum perspective-distortion score: `0.55`.

These are initial input-usability policy thresholds, not identity-confidence or likeness thresholds. They remain eligible for evidence-based revision during later Phase 8 benchmark work without collapsing the contract boundaries.

### Validation

- new focused contracts:
  - portrait input evidence: 11 passed;
  - portrait input evidence set: 12 passed;
  - portrait quality observation: 21 passed;
  - portrait usability gate: 10 passed.
- related portrait / face-head regression: `147 passed in 0.22s`.
- full regression: `4274 passed in 121.37s`.
- `git diff --check`: `EXIT=0`.

### Gate decision

Phase 8.0 is `LOCKED`.

The next exact sub-phase is **8.1 — Canonical Topology Contract**. Before choosing or integrating FLAME or any other provider, 8.1 must define the provider-independent full-3D topology/correspondence/semantic-region contract and preserve the Phase 8 license/runtime decision gate.

## 20 Aug 2026 — Phase 8.1 Canonical Topology Contract LOCK

**Program:** Semantic Relief, Figurative & Kit System V1
**Phase:** 8 — Canonical Face/Head Decision Gate
**Sub-phase:** 8.1 — Canonical Topology Contract
**Status:** `LOCKED`

Phase 8.1 establishes the provider-independent canonical full-3D head topology boundary. It deliberately does not select FLAME or another external provider and does not yet define identity parameters, expression, pose, likeness confidence or commercial dependency approval.

### Locked contracts

- `CORE/atlas_canonical_head_topology.py`
  - immutable provider-independent topology descriptor;
  - normalized topology identity;
  - explicit fixed vertex count;
  - indexed triangular connectivity;
  - semantic vertex regions;
  - deterministic SHA-256 connectivity signature derived from vertex count and face connectivity;
  - connectivity identity is independent of provider naming and future per-person vertex coordinates.

- `CORE/atlas_canonical_head_geometry.py`
  - immutable full-3D vertex geometry bound to an `AtlasCanonicalHeadTopology`;
  - vertex array shape must be `(topology.vertex_count, 3)`;
  - finite coordinates required;
  - different person-specific geometries may use different vertex coordinates while preserving one canonical topology/connectivity signature;
  - semantic region vertices can be retrieved without mutating topology;
  - contract does not claim pose, expression, identity parameters, provider identity or confidence.

- `CORE/atlas_canonical_head_topology_compatibility_gate.py`
  - provider-independent topology compatibility gate;
  - minimum canonical semantic regions currently required:
    - `face`
    - `nose`
    - `left_eye`
    - `right_eye`
  - missing required regions produce `BLOCKED_MISSING_CANONICAL_SEMANTIC_REGION`;
  - ear/hair/neck ownership is intentionally deferred to Phase 8.7 rather than prematurely hard-coded here.

### Architectural meaning

Canonical topology and canonical instance geometry are now separate concepts.

Two identities may have different 3D vertex coordinates while remaining topologically compatible when their indexed connectivity signature is identical. This is the foundation required for later identity-shape fitting, expression separation, correspondence and downstream relief/bust/figurine adapters.

The general `AtlasTriangleMeshGeometrySourceAdapter` remains the generic triangle-mesh source boundary and is not duplicated. Phase 8.1 adds human-head topology semantics that generic triangle soup cannot express safely.

### Explicit non-decisions

Phase 8.1 does NOT:

- bind ATLAS to FLAME or another provider;
- hard-code the historical FLAME vertex/triangle counts;
- define identity coefficients;
- define expression or pose parameters;
- define likeness or identity confidence;
- approve any external model license, weights or dataset;
- create portrait relief production geometry.

Those decisions remain assigned to later Phase 8 gates.

### Validation

- canonical topology descriptor: `15 passed in 0.03s`;
- canonical head geometry: `9 passed in 0.05s`;
- topology compatibility gate: `8 passed in 0.02s`;
- related Phase 8 / geometry-source regression: `108 passed in 0.21s`;
- full regression: `4306 passed in 119.70s`;
- `git diff --check`: `EXIT=0`.

### Gate decision

Phase 8.1 is `LOCKED`.

The next exact sub-phase is **8.2 — Identity Shape Contract**. It must define identity-bearing canonical geometry separately from expression, pose and residual detail while preserving the fixed topology contract established here.

## 20 Aug 2026 — Phase 8.2 Identity Shape Contract LOCK

**Program:** Semantic Relief, Figurative & Kit System V1
**Phase:** 8 — Canonical Face/Head Decision Gate
**Sub-phase:** 8.2 — Identity Shape Contract
**Status:** `LOCKED`

Phase 8.2 establishes the provider-independent identity-bearing shape layer on top of the fixed canonical head topology locked in Phase 8.1.

### Locked contracts

- `CORE/atlas_canonical_head_identity_shape.py`
  - immutable identity-shape descriptor;
  - normalized `identity_shape_id`;
  - references an immutable `AtlasCanonicalHeadGeometry`;
  - stores person-specific `identity_displacement` as a finite immutable `(N, 3)` array;
  - resolved geometry is deterministically computed as canonical reference geometry plus identity displacement;
  - resolved geometry preserves the exact canonical topology and connectivity signature from Phase 8.1.

- `CORE/atlas_canonical_head_identity_shape_compatibility_gate.py`
  - evaluates a collection of `AtlasCanonicalHeadIdentityShape` instances;
  - empty collections are rejected;
  - non-identity-shape members are rejected;
  - identity shapes sharing one canonical connectivity signature are `ACCEPTED`;
  - mixed canonical connectivity produces `BLOCKED_MIXED_CANONICAL_HEAD_CONNECTIVITY`;
  - result exposes compatibility status, blocked reasons, shared connectivity signature and identity-shape count.

### Architectural meaning

Identity shape is now a dedicated layer separate from canonical topology and separate from later transient deformations.

The contract represents identity-bearing 3D shape as a displacement over a canonical reference geometry while preserving fixed vertex correspondence. This allows different individuals to occupy different canonical 3D geometries without changing connectivity.

Different canonical reference geometry instances may still be compatible when their indexed connectivity signature is identical. Phase 8.2 therefore does not require byte-identical reference vertex coordinates; it requires canonical topological compatibility.

### Explicit non-decisions

Phase 8.2 does NOT:

- define expression parameters or expression displacement;
- define head/body pose;
- define residual/high-frequency detail;
- define likeness or identity confidence;
- bind ATLAS to FLAME, DECA, MICA, EMOCA or another provider;
- expose provider-specific coefficients;
- approve external model licenses, weights or datasets;
- create final portrait relief, bust or figurine production geometry.

Expression separation remains assigned to Phase 8.5. Provider and commercial dependency decisions remain later Phase 8 gate work.

### Validation

- identity-shape contract: `10 passed in 0.05s`;
- identity-shape compatibility gate: `6 passed in 0.05s`;
- related Phase 8 / geometry-source regression: `124 passed in 0.29s`;
- full regression: `4323 passed in 120.98s`;
- `git diff --check`: `EXIT=0`.

### Gate decision

Phase 8.2 is `LOCKED`.

The next exact sub-phase is **8.3 — Landmark & Dense Correspondence Contract**. It must define stable semantic/index correspondence between observed portrait evidence and the canonical head without coupling ATLAS to a specific provider implementation.

## 20 Aug 2026 — Phase 8.3 Landmark & Dense Correspondence Contract LOCK

**Program:** Semantic Relief, Figurative & Kit System V1
**Phase:** 8 — Canonical Face/Head Decision Gate
**Sub-phase:** 8.3 — Landmark & Dense Correspondence Contract
**Status:** `LOCKED`

Phase 8.3 establishes provider-independent correspondence contracts between observed portrait evidence and the canonical head topology locked in Phase 8.1.

### Locked contracts

- `CORE/atlas_canonical_head_landmark_correspondence.py`
  - immutable sparse correspondence contract;
  - maps observed landmark IDs to canonical head vertex indices;
  - bound to an `AtlasCanonicalHeadTopology`;
  - canonical targets must be unique;
  - canonical vertex indices must remain inside topology vertex bounds;
  - exposes deterministic observed landmark ordering, canonical targets, correspondence count and connectivity signature;
  - does not claim provider identity, confidence, camera fit, identity shape or fit quality.

- `CORE/atlas_canonical_head_dense_correspondence.py`
  - immutable dense correspondence contract;
  - maps observed sample indices to canonical head vertex indices;
  - bound to an `AtlasCanonicalHeadTopology`;
  - canonical targets must be unique and in range;
  - exposes correspondence count and canonical coverage ratio;
  - full canonical coverage reports `1.0`;
  - preserves the canonical connectivity signature.

### Architectural meaning

Observed portrait indexing and canonical head indexing are now explicitly separated.

`AtlasPortraitIndexedLandmarkResult` remains the provider-independent observation container and intentionally performs no correspondence. Phase 8.3 adds the missing bridge from observed IDs/samples to canonical head vertex identity without embedding provider-specific topology into the canonical head contract.

Sparse and dense correspondence are separate layers:

- sparse correspondence represents semantically selected observed landmark IDs;
- dense correspondence represents broader indexed sample-to-canonical-vertex coverage.

Both preserve fixed canonical topology and therefore remain compatible with the identity-shape layer from Phase 8.2.

### Explicit non-decisions

Phase 8.3 does NOT:

- perform camera fitting or perspective normalization;
- define pose normalization;
- define expression fitting;
- calculate correspondence fit error or likeness confidence;
- bind ATLAS to MediaPipe, FLAME or another provider;
- approve external model licenses, datasets or weights;
- infer identity shape from correspondence alone.

Camera and pose normalization remain assigned to Phase 8.4.

### Validation

- sparse canonical landmark correspondence: `14 passed in 0.03s`;
- dense canonical correspondence: `15 passed in 0.03s`;
- related Phase 8 / portrait regression: `107 passed in 0.20s`;
- full regression: `4352 passed in 120.93s`;
- `git diff --check`: `EXIT=0`.

### Gate decision

Phase 8.3 is `LOCKED`.

The next exact sub-phase is **8.4 — Camera / Pose Normalization**. It must normalize observation camera and head pose independently from identity shape and expression while preserving the canonical topology/correspondence contracts established in Phase 8.1–8.3.

## 20 Aug 2026 — Phase 8.4 Camera / Pose Normalization LOCK

**Program:** Semantic Relief, Figurative & Kit System V1
**Phase:** 8 — Canonical Face/Head Decision Gate
**Sub-phase:** 8.4 — Camera / Pose Normalization
**Status:** `LOCKED`

Phase 8.4 establishes provider-independent observation and normalization contracts for head pose and portrait camera state while keeping identity shape and expression separate.

### Locked contracts

- `CORE/atlas_canonical_head_pose_observation.py`
  - immutable observed head-pose contract;
  - normalized `pose_id`;
  - finite yaw, pitch and roll angles in degrees;
  - canonical neutral pose is explicitly `0 / 0 / 0`;
  - does not claim camera state, identity shape, expression, provider or confidence.

- `CORE/atlas_canonical_head_camera_observation.py`
  - immutable provider-independent portrait camera observation;
  - perspective projection contract;
  - positive image dimensions;
  - positive finite focal length in pixels;
  - finite principal point constrained to image bounds;
  - exposes normalized principal point coordinates;
  - camera state remains independent from head pose and identity state.

- `CORE/atlas_canonical_head_pose_normalization.py`
  - immutable canonical pose-normalization descriptor;
  - references an observed head pose and camera observation;
  - exposes inverse yaw / pitch / roll needed to return the observed head orientation to canonical neutral orientation;
  - target orientation is explicitly `0 / 0 / 0`;
  - preserves observation contracts without mutating identity geometry or expression state.

### Architectural meaning

Phase 8.4 separates three concerns that must not be conflated:

1. observed head orientation;
2. observed portrait camera state;
3. canonical pose normalization.

This establishes the boundary needed to remove observation pose/camera effects before later identity and expression evaluation. Camera normalization is not treated as identity deformation, and head-pose normalization is not allowed to modify identity shape.

The existing `AtlasPortraitInputQualityObservation.perspective_distortion_score` remains an input-quality signal only and is not a camera model. Existing surface-projection and body-pose adapters remain separate product/figurative systems and are not reused as canonical portrait-camera contracts.

### Explicit non-decisions

Phase 8.4 does NOT:

- change canonical identity shape;
- define or remove facial expression;
- calculate likeness or identity confidence;
- bind ATLAS to a provider-specific camera estimator;
- perform FLAME, DECA, MICA or EMOCA fitting;
- approve external model licenses, datasets or weights;
- create final portrait relief, bust or figurine geometry.

Expression separation remains assigned to Phase 8.5.

### Validation

- head-pose observation: `10 passed in 0.02s`;
- camera observation: `14 passed in 0.02s`;
- canonical pose normalization: `8 passed in 0.02s`;
- related Phase 8 regression: `132 passed in 0.23s`;
- full regression: `4384 passed in 119.85s`;
- `git diff --check`: `EXIT=0`.

### Gate decision

Phase 8.4 is `LOCKED`.

The next exact sub-phase is **8.5 — Expression Separation**. Work must resume there after the planned pause.

## Premium Gift Box — 180.8 mm Physical Compatibility System — 21 Aug 2026

Operational gift-box work remains separate from the paused Phase 8 portrait program.

A physical 170 mm Wall Collection box chain is now locked around the already-printed / in-production 180.8 mm BASE geometry. This physical compatibility chain must not be confused with the newer 181.5 mm nominal production-box spec.

### Physical reference BASE
- outer XY: 180.8 x 180.8 mm
- inner XY: 176.0 x 176.0 mm
- total height: 35.4 mm
- top male connector outer XY: 178.8 x 178.8 mm
- male engagement: 4.0 mm
- connector inset: 1.0 mm / side
- physical fit calibration: 0.05 mm clearance / side
- mating female opening: 178.9 x 178.9 mm
- female recess depth: 4.2 mm
- BASE is currently being physically printed.

### Physical MIDDLE
- outer XY: 180.8 x 180.8 mm
- inner XY: 176.0 x 176.0 mm
- total part height: 50.0 mm
- bottom connector: female
- bottom female opening: 178.9 x 178.9 mm
- female recess depth: 4.2 mm
- top connector: male
- top male outer XY: 178.8 x 178.8 mm
- male engagement: 4.0 mm
- mesh: 80 triangles
- open edges: 0
- non-manifold edges: 0
- STL:
  OUTPUT/STL/PREMIUM_GIFT_BOX_170MM_PHYSICAL_180_8/PREMIUM_GIFT_BOX_170MM_MIDDLE_180_8x180_8x50_0.stl
- Bambu Studio dimensional inspection: accepted.
- physical print pending.

### Physical tall LID with pull-tab
- main lid body XY: 180.8 x 180.8 mm
- total height: 35.0 mm
- bottom connector: female
- female opening: 178.9 x 178.9 mm
- female recess depth: 4.2 mm
- top thickness: 2.0 mm
- usable internal height above connector transition: 28.8 mm
- finger notch concept was rejected.
- final opening aid is an outward pull-tab / small visor-like lip:
  - width: 30.0 mm
  - projection: 4.0 mm
  - thickness: 3.0 mm
- pull-tab-inclusive bounding XY: 180.8 x 184.8 mm
- final mesh: 72 triangles
- connected components: 1
- watertight: True
- open edges: 0
- non-manifold edges: 0
- STL:
  OUTPUT/STL/PREMIUM_GIFT_BOX_170MM_PHYSICAL_180_8/PREMIUM_GIFT_BOX_170MM_LID_PULL_TAB_180_8x184_8x35_0.stl
- Bambu Studio visual inspection: accepted.
- physical print pending.

### Modular fit contract
- BASE male -> MIDDLE female
- MIDDLE male -> LID female
- LID may also mount directly on BASE without MIDDLE.
- main outside body remains flush at 180.8 x 180.8 mm through BASE / MIDDLE / LID.
- 184.8 mm shown for the LID is only the local total bounding dimension caused by the 4.0 mm outward pull-tab.
- female clearance remains the physically calibrated 0.05 mm / side.

Do not regenerate these physical-fit parts from the 181.5 mm nominal production factory unless explicitly migrating the physical system. The 180.8 mm chain exists to match the actual BASE currently being printed.

## Phase 8.5 — Expression Separation — LOCK candidate

Phase 8.5 establishes a strict separation between persistent identity shape and temporary facial expression deformation on canonical head topology.

Implemented contracts:
- CORE/atlas_canonical_head_expression_displacement.py
- CORE/atlas_canonical_head_expression_compatibility_gate.py
- CORE/atlas_canonical_head_expression_composition.py

Tests:
- Test/test_canonical_head_expression_displacement.py
- Test/test_canonical_head_expression_compatibility_gate.py
- Test/test_canonical_head_expression_composition.py

Locked behavior:
- expression is represented as an immutable canonical (N,3) displacement layer;
- zero displacement is the neutral expression;
- expression state does not carry identity, pose, camera, provider, confidence, or likeness state;
- identity and expression may compose only when canonical connectivity signatures match;
- connectivity mismatch is explicitly blocked with BLOCKED_IDENTITY_EXPRESSION_CONNECTIVITY_MISMATCH;
- resolved expression geometry is identity resolved geometry plus expression displacement;
- identity and expression contracts remain immutable and are not mutated during composition.

Validation:
- focused Phase 8.5: 23 passed in 0.08s
- related canonical-head regression: 132 passed in 0.26s
- Phase 8.5 scoped git diff --check: clean
- full regression: 4409 passed in 121.49s

Phase 8.4 remains LOCKED.
Phase 8.5 is ready for final commit/push lock.
Next planned subphase after lock: Phase 8.6 — Asymmetry Preservation.

## Phase 8.6 — Asymmetry Preservation — LOCK candidate

Phase 8.6 preserves meaningful person-specific asymmetry instead of forcing canonical identity geometry into bilateral symmetry. Symmetry remains a possible prior or regularizer, not a destructive final-shape requirement.

Implemented contracts:
- CORE/atlas_canonical_head_asymmetry_displacement.py
- CORE/atlas_canonical_head_asymmetry_compatibility_gate.py
- CORE/atlas_canonical_head_asymmetry_composition.py

Tests:
- Test/test_canonical_head_asymmetry_displacement.py
- Test/test_canonical_head_asymmetry_compatibility_gate.py
- Test/test_canonical_head_asymmetry_composition.py

Locked behavior:
- asymmetry is represented as an immutable canonical (N,3) displacement layer;
- zero displacement represents no preserved asymmetry;
- nonzero displacement may preserve meaningful real identity asymmetry;
- asymmetry state does not carry expression, pose, camera, provider, confidence, or likeness state;
- identity and asymmetry may compose only when canonical connectivity signatures match;
- connectivity mismatch is explicitly blocked with BLOCKED_IDENTITY_ASYMMETRY_CONNECTIVITY_MISMATCH;
- resolved asymmetric geometry is identity resolved geometry plus asymmetry displacement;
- identity and asymmetry contracts remain immutable and are not mutated during composition;
- symmetry is not encoded as a mandatory final geometry constraint.

Validation:
- focused Phase 8.6: 23 passed in 0.08s
- related canonical-head regression: 155 passed in 0.32s
- Phase 8.6 scoped git diff --check: clean
- full regression: 4432 passed in 120.47s

Phase 8.5 remains LOCKED.
Phase 8.6 is ready for final commit/push lock.
Next planned subphase after lock: Phase 8.7 — Head Semantic Boundary.

## Phase 8.7 — Head Semantic Boundary — LOCK candidate

Phase 8.7 defines provider-independent ownership boundaries between canonical head surface regions, separate semantic components and optional facial-detail layers.

Implemented contracts:
- CORE/atlas_canonical_head_semantic_boundary.py
- CORE/atlas_canonical_head_semantic_boundary_compatibility_gate.py
- CORE/atlas_canonical_head_semantic_region_resolver.py

Tests:
- Test/test_canonical_head_semantic_boundary.py
- Test/test_canonical_head_semantic_boundary_compatibility_gate.py
- Test/test_canonical_head_semantic_region_resolver.py

Locked ownership policy:
- canonical head surface owns face, left/right ears, jaw, chin, neck and left/right eye regions;
- hair is a separate semantic component;
- left/right eyeballs are separate semantic components rather than canonical head-surface regions;
- beard and moustache are optional detail layers;
- separate components and optional detail layers are not required canonical topology semantic regions;
- canonical topology must expose all required canonical-head semantic regions;
- missing required regions are explicitly blocked with BLOCKED_MISSING_CANONICAL_HEAD_SEMANTIC_REGION;
- semantic region resolution is deterministic and provider-independent;
- non-canonical ownership classes cannot be resolved as canonical-head topology vertex regions;
- these contracts do not claim geometry generation, provider identity, likeness or confidence.

Validation:
- focused Phase 8.7: 35 passed in 0.07s
- related canonical-head regression: 190 passed in 0.39s
- Phase 8.7 scoped git diff --check: clean
- full regression: 4467 passed in 120.93s

Phase 8.6 remains LOCKED.
Phase 8.7 is ready for final commit/push lock.
Next planned subphase after lock: Phase 8.8 — Identity Confidence Gate.

## Phase 8.8 — Identity Confidence Gate — LOCK candidate

Phase 8.8 establishes a provider-independent identity-confidence decision boundary. Input usability, landmark support and successful geometry generation are not treated as proof that a reconstructed head reliably preserves a specific person identity.

Implemented contracts:
- CORE/atlas_canonical_head_identity_confidence_observation.py
- CORE/atlas_canonical_head_identity_confidence_gate.py

Tests:
- Test/test_canonical_head_identity_confidence_observation.py
- Test/test_canonical_head_identity_confidence_gate.py

Locked observation channels:
- view coverage support;
- multi-view consistency;
- silhouette support;
- profile support;
- identity-shape support;
- landmark support;
- asymmetry support.

Locked decision behavior:
- identity evidence is not collapsed into one opaque confidence scalar;
- landmark support is recorded separately and cannot override weak identity-shape, profile or multi-view evidence;
- GO means production identity evidence is accepted;
- HOLD means evidence is limited and production remains BLOCKED;
- REJECT means critical identity evidence is insufficient and production remains BLOCKED;
- every non-GO result carries BLOCKED_INSUFFICIENT_IDENTITY_EVIDENCE;
- deterministic channel-specific failure reasons explain HOLD/REJECT results;
- critical-channel values below 0.35 produce REJECT;
- critical-channel values from 0.35 up to but not including 0.70 produce HOLD;
- required decision channels at or above 0.70 produce GO;
- asymmetry weakness alone may force HOLD but does not by itself force REJECT;
- confidence contracts do not claim geometry, provider identity or likeness score.

Validation:
- focused Phase 8.8: 45 passed in 0.05s
- related canonical-head regression: 235 passed in 0.44s
- Phase 8.8 scoped git diff --check: clean
- full regression: 4512 passed in 120.26s

Phase 8.7 remains LOCKED.
Phase 8.8 is ready for final commit/push lock.
Next planned subphase after lock: Phase 8.9 — Physical Representation Gate.

## Phase 8.9 — Physical Representation Gate — LOCK candidate

Phase 8.9 establishes the provider-independent physical representation gate for carrying one canonical identity into relief, bust, figurine-head and story/kit-component outputs without treating printability alone as proof of identity preservation.

Implemented contracts:
- CORE/atlas_canonical_head_physical_representation_observation.py
- CORE/atlas_canonical_head_physical_representation_gate.py

Tests:
- Test/test_canonical_head_physical_representation_observation.py
- Test/test_canonical_head_physical_representation_gate.py

Locked representation classes:
- relief;
- bust;
- figurine_head;
- story_kit_component.

Locked observation channels:
- target head height in mm;
- minimum physical feature in mm;
- LoD level;
- identity-preservation support;
- silhouette-preservation support;
- profile-preservation support.

Locked gate behavior:
- physical printability and identity preservation are separate requirements;
- minimum head height is 18.0 mm;
- minimum physical feature is 0.40 mm;
- identity-preservation support below 0.50 produces REJECT;
- identity-preservation support from 0.50 up to but not including 0.70 produces HOLD;
- required preservation channels at or above 0.70 may produce GO;
- LoD levels through 4 may pass; LoD 5+ produces HOLD;
- limited silhouette or profile preservation produces HOLD;
- GO means the physical identity representation is accepted;
- HOLD and REJECT remain production BLOCKED;
- every non-GO result carries BLOCKED_PHYSICAL_IDENTITY_REPRESENTATION;
- deterministic failure reasons identify physical-size, feature-size, identity, silhouette, profile or LoD limitations;
- these contracts do not claim geometry generation, provider identity or likeness score.

Validation:
- focused Phase 8.9: 37 passed in 0.05s
- related canonical-head regression: 272 passed in 0.45s
- Phase 8.9 scoped git diff --check: clean
- full regression: 4549 passed in 121.23s

Phase 8.8 remains LOCKED.
Phase 8.9 is ready for final commit/push lock.
Next planned subphase after lock: Phase 8.10 — Canonical Benchmark & LOCK.

## Phase 8.10 — Canonical Benchmark & LOCK — LOCK candidate

Phase 8.10 establishes the final provider-independent canonical-head benchmark decision architecture for Phase 8. It compares parametric/fixed-topology, direct neural dense reconstruction and hybrid canonical+detail approaches under one evidence contract and prevents Phase 9 authorization unless a complete benchmark produces an explicit GO result.

Implemented contracts:
- CORE/atlas_canonical_head_benchmark_candidate_observation.py
- CORE/atlas_canonical_head_benchmark_candidate_gate.py
- CORE/atlas_canonical_head_benchmark_decision_gate.py

Tests:
- Test/test_canonical_head_benchmark_candidate_observation.py
- Test/test_canonical_head_benchmark_candidate_gate.py
- Test/test_canonical_head_benchmark_decision_gate.py

Locked benchmark architecture classes:
- parametric_fixed_topology;
- direct_neural_dense;
- hybrid_canonical_detail.

Locked benchmark evidence:
- identity preservation;
- multi-view consistency;
- silhouette/profile support;
- head-ratio support;
- jaw/chin support;
- nose-projection support;
- orbital/cheek-volume support;
- expression separation;
- pose separation;
- topology suitability;
- physical suitability;
- Apple Silicon/runtime support;
- reproducibility;
- commercial-license acceptability;
- privacy/data-retention acceptability;
- model-weight restriction acceptability;
- dataset restriction acceptability;
- processing time and processing cost.

Locked candidate behavior:
- policy failures for commercial license, privacy/data retention, model weights or dataset restrictions are hard REJECT conditions;
- benchmark quality below 0.50 produces REJECT;
- benchmark quality from 0.50 up to but not including 0.70 produces HOLD;
- required quality channels at or above 0.70 may produce GO;
- strong geometric evidence cannot override topology, policy, physical-suitability, runtime or reproducibility failure;
- processing time/cost do not outrank identity quality and are used only as late tie-break evidence.

Locked final benchmark behavior:
- all three architecture classes are required for a complete canonical benchmark;
- duplicate architecture classes are rejected;
- only candidate-level GO observations are eligible for final selection;
- no candidate-level GO means Phase 8 remains HOLD/BLOCKED;
- final selection is deterministic and prioritizes identity preservation, physical suitability, topology suitability, reproducibility and Apple Silicon/runtime before processing time/cost;
- final GO returns LOCK_READY and authorizes Phase 9;
- incomplete benchmark or absence of a GO candidate cannot authorize Phase 9;
- provider implementation and real external-model dependency selection remain separate from this provider-independent decision contract.

Validation:
- focused Phase 8.10: 66 passed in 0.07s
- related canonical-head regression: 338 passed in 0.52s
- Phase 8.10 scoped git diff --check: clean
- full regression: 4615 passed in 120.45s

Phase 8.9 remains LOCKED.
Phase 8.10 is ready for final commit/push lock.

Important closure condition:
Phase 8 contract architecture is ready to LOCK, but this contract milestone alone does not fabricate real benchmark evidence for FLAME, DECA, MICA, EMOCA or another external implementation. Any production dependency still requires the documented commercial-license, privacy, runtime, reproducibility and physical-identity evidence audit. Phase 9 authorization requires a real complete benchmark result with explicit GO.

## Phase 8.10 — FLAME 2023 Open Real Raw Benchmark Evidence — ACTIVE EVIDENCE

The first real Phase 8.10 benchmark evidence has now been established for the `parametric_fixed_topology` architecture using FLAME 2023 Open. This evidence does not yet constitute a candidate GO decision and does not authorize Phase 9.

New provider-independent raw-evidence contracts:
- CORE/atlas_canonical_head_focal_identifiability_observation.py
- CORE/atlas_canonical_head_benchmark_measurement_observation.py
- CORE/atlas_canonical_head_flame_benchmark_evidence.py

Tests:
- Test/test_canonical_head_focal_identifiability_observation.py
- Test/test_canonical_head_benchmark_measurement_observation.py
- Test/test_canonical_head_flame_benchmark_evidence.py

Verified FLAME model evidence:
- model: FLAME 2023 Open;
- architecture class: `parametric_fixed_topology`;
- canonical topology: 5023 vertices / 9976 triangles;
- identity model capacity: 300 components;
- selected active benchmark identity capacity: 90 components;
- expression capacity: 100 components, held neutral for this benchmark;
- benchmark input: two real subjects, each with front + two opposing head-turn views;
- MediaPipe detection: 6/6 views successful;
- dense correspondence count: 105 MediaPipe-to-FLAME barycentric correspondences.

Identity-capacity audit:
- historical 20-component baseline was insufficient;
- 20 -> 90 produced substantial reprojection improvement;
- 90 -> 300 produced only marginal additional reprojection improvement while runtime increased by approximately 7x;
- 90 active identity components are therefore the selected fair FLAME benchmark capacity for the current Phase 8.10 evidence protocol.

Perspective-camera identifiability audit:
- benchmark source photos contain no usable focal-length EXIF data;
- optimized focal length was tested under 5000, 10000 and 20000 px upper bounds;
- in both subjects and all views the fitted focal length tracked the active upper bound exactly;
- focal length is therefore not identifiable from the current image evidence;
- bound-dependent optimized focal values are not accepted as canonical camera evidence.

Verified raw subject measurements:

Subject 01:
- view count: 3;
- landmarks per view: 105;
- mean reprojection IOD-NME: 0.027984;
- mean reprojection bbox-NME: 0.007818;
- independent-view canonical identity-shape NME: 0.059630;
- focal identifiable: false;
- 3D ground truth available: false;
- volumetric identity proven: false;
- primary 90D shared-identity processing time: 1.407287 s.

Subject 02:
- view count: 3;
- landmarks per view: 105;
- mean reprojection IOD-NME: 0.023456;
- mean reprojection bbox-NME: 0.007082;
- independent-view canonical identity-shape NME: 0.064978;
- focal identifiable: false;
- 3D ground truth available: false;
- volumetric identity proven: false;
- primary 90D shared-identity processing time: 1.457528 s.

Verified aggregate raw measurements:
- mean reprojection IOD-NME: 0.025720;
- mean cross-view canonical identity-shape NME: 0.062304;
- all focal lengths identifiable: false;
- any volumetric identity proven: false.

Cross-view protocol note:
- independent-view identity consistency was rerun with the historical staged FLAME fitting chain from the pre-removal implementation snapshot;
- root pose was resolved first from the 17-point semantic correspondence set;
- root pose was then held fixed during 90-component dense identity fitting using the 105-point embedding;
- this replaced an invalid exploratory spike that jointly optimized pose and identity and drove pose/identity variables to bounds;
- invalid exploratory values 0.175878 and 0.186543 are not benchmark evidence and must not be reused.

Evidence-boundary rule:
- raw measurement != normalized support != candidate decision;
- no [0,1] benchmark support values have been assigned from these measurements;
- no FLAME candidate GO/HOLD/REJECT decision has yet been issued from this evidence;
- no volumetric identity claim is allowed without appropriate 3D ground-truth evidence;
- Phase 9 remains NOT AUTHORIZED.

Validation for this raw-evidence milestone:
- focal-identifiability focused tests: 14 passed;
- raw measurement focused tests: 26 passed;
- deterministic FLAME evidence catalog tests: 8 passed;
- related Phase 8.10 benchmark regression: 114 passed in 0.13s;
- canonical-head related regression before evidence catalog: 378 passed in 0.60s;
- scoped git diff --check: clean;
- full regression: 4663 passed in 120.58s.

Next Phase 8.10 requirement:
- continue the real benchmark evidence program without fabricating support values;
- establish the remaining evidence required to calibrate raw measurements into benchmark support channels;
- benchmark all three required architecture classes before any final Phase 8 GO / LOCK_READY decision;
- Phase 9 remains blocked until the complete benchmark explicitly returns GO.

## Phase 8.10 — Benchmark Evidence Coverage Boundary

The raw-measurement-to-support boundary is now explicit. Phase 8.10 does not treat an available measurement, structural property or runtime observation as an automatic `[0,1]` benchmark support score.

New provider-independent contract:
- `CORE/atlas_canonical_head_benchmark_evidence_coverage.py`

New test:
- `Test/test_canonical_head_benchmark_evidence_coverage.py`

Evidence coverage states:
- `MEASURED` — a directly relevant benchmark measurement exists;
- `PARTIAL` — relevant evidence exists but is insufficient for a complete support claim;
- `DIRECT` — structural/runtime/reproducibility evidence is directly verified but has not been converted into a support score;
- `MISSING` — required evidence has not yet been established.

The coverage contract:
- covers all 13 Phase 8.10 quality channels;
- exposes missing channels deterministically;
- carries no normalized support score;
- carries no GO/HOLD/REJECT decision;
- carries no Phase 9 authorization.

FLAME 2023 Open conservative coverage:
- identity preservation: `PARTIAL`;
- multi-view consistency: `MEASURED`;
- silhouette/profile: `MISSING`;
- head ratio: `MISSING`;
- jaw/chin: `MISSING`;
- nose projection: `MISSING`;
- orbital/cheek volume: `MISSING`;
- expression separation: `MISSING`;
- pose separation: `PARTIAL`;
- topology suitability: `DIRECT`;
- physical suitability: `MISSING`;
- Apple Silicon runtime: `DIRECT`;
- reproducibility: `DIRECT`.

Interpretation boundary:
- `DIRECT` does not mean support `1.0`;
- `MEASURED` does not by itself define a support calibration;
- 2D reprojection and cross-view consistency do not prove volumetric identity;
- missing 3D ground truth prevents unsupported jaw/chin, nose-projection and orbital/cheek-volume claims;
- current evidence therefore cannot yet instantiate a complete FLAME candidate observation for the Phase 8.10 decision gate.

Validation:
- evidence coverage focused tests: `16 passed in 0.03s`;
- coverage + FLAME focused integration: `26 passed in 0.05s`;
- related Phase 8.10 regression: `132 passed in 0.15s`;
- full regression: `4681 passed in 120.85s`;
- scoped tracked diff check: clean;
- staged diff check remains required because the new coverage contract/test are currently untracked.

Next Phase 8.10 requirement:
- close the remaining evidence gaps before assigning calibrated support values;
- do not fabricate volumetric, physical or expression evidence from the current two-subject photo benchmark;
- retain the required three-architecture benchmark boundary;
- Phase 9 remains NOT AUTHORIZED.


## Phase 8.10 — FLAME Leave-One-View-Out Benchmark C — RAW EVIDENCE COMPLETE

The FLAME 2023 Open `parametric_fixed_topology` candidate now has a
completed leave-one-view-out multi-view generalization benchmark over
the current two-subject / three-view real-photo evidence set.

New provider-independent observation contracts:
- `CORE/atlas_canonical_head_shared_identity_fit_observation.py`
- `CORE/atlas_canonical_head_held_out_view_observation.py`

Tests:
- `Test/test_canonical_head_shared_identity_fit_observation.py`
- `Test/test_canonical_head_held_out_view_observation.py`

FLAME deterministic evidence catalog integration:
- `CORE/atlas_canonical_head_flame_benchmark_evidence.py`
- `Test/test_canonical_head_flame_benchmark_evidence.py`

Benchmark C protocol:
- each subject has `front`, `side_a` and `side_b`;
- exactly two views train one shared 90-component FLAME identity;
- expression remains fixed neutral;
- the third view is completely excluded from identity training;
- held-out identity is then locked;
- only held-out root pose and weak-perspective camera are resolved;
- the same 105 MediaPipe-to-FLAME barycentric correspondences are used;
- reprojection is normalized independently by outer-eye IOD and by the
  full 478-landmark MediaPipe 2D bounding-box diagonal;
- perspective focal fitting is not used because focal length is not
  identifiable from the current source photographs.

Verified held-out raw measurements:

Subject 01:
- held-out `front`, training `side_a + side_b`:
  - IOD-NME `0.025737053`;
  - bbox-NME `0.009386448`;
  - identity bound hits `0`;
  - held-out pose bound hits `0`;
  - processing time `10.257207 s`.
- held-out `side_a`, training `front + side_b`:
  - IOD-NME `0.042736096`;
  - bbox-NME `0.010860442`;
  - identity bound hits `1`;
  - held-out pose bound hits `0`;
  - processing time `10.775558 s`.
- held-out `side_b`, training `front + side_a`:
  - IOD-NME `0.038976068`;
  - bbox-NME `0.010278185`;
  - identity bound hits `0`;
  - held-out pose bound hits `0`;
  - processing time `10.701019 s`.

Subject 02:
- held-out `front`, training `side_a + side_b`:
  - IOD-NME `0.038987713`;
  - bbox-NME `0.014025643`;
  - identity bound hits `0`;
  - held-out pose bound hits `0`;
  - processing time `16.549599 s`.
- held-out `side_a`, training `front + side_b`:
  - IOD-NME `0.037416831`;
  - bbox-NME `0.011151774`;
  - identity bound hits `4`;
  - held-out pose bound hits `0`;
  - processing time `13.301181 s`.
- held-out `side_b`, training `front + side_a`:
  - IOD-NME `0.031452767`;
  - bbox-NME `0.008749089`;
  - identity bound hits `4`;
  - held-out pose bound hits `0`;
  - processing time `11.974395 s`.

Verified subject aggregates:
- Subject 01 mean held-out IOD-NME: `0.035816406`;
- Subject 01 mean held-out bbox-NME: `0.010175025`;
- Subject 02 mean held-out IOD-NME: `0.035952437`;
- Subject 02 mean held-out bbox-NME: `0.011308835`.

Verified six-case aggregate:
- leave-one-view-out combinations completed: `6/6`;
- optimizer success: `6/6`;
- held-out pose bound hits: `0/6`;
- mean held-out IOD-NME: `0.035884421`;
- mean held-out bbox-NME: `0.010741930`.

Interpretation boundary:
- Benchmark C establishes real unseen-view reprojection/generalization
  evidence for a shared FLAME identity under the current protocol;
- successful 2D held-out reprojection is not metric 3D identity proof;
- the current source photographs have no 3D ground-truth scan;
- shared-identity training must not be interpreted as an independent
  cross-view identity-shape success metric;
- no normalized `[0,1]` support score is assigned by this milestone;
- no FLAME candidate GO/HOLD/REJECT decision is issued by this milestone;
- no missing silhouette/profile, metric facial-volume, expression or
  physical-print evidence is fabricated from these results;
- the required three-architecture Phase 8.10 benchmark boundary remains
  unchanged;
- Phase 9 remains `NOT AUTHORIZED`.

Validation:
- held-out contract + FLAME evidence focused validation:
  `37 passed in 0.05s`;
- Phase 8.10 evidence/observation related regression:
  `94 passed in 0.11s`;
- scoped `git diff --check`: clean;
- full regression:
  `4723 passed in 121.14s`.

Next Phase 8.10 requirement:
- preserve these measurements as raw evidence;
- continue closing the explicitly missing benchmark evidence channels
  without converting incomplete evidence into fabricated support values;
- complete the required `direct_neural_dense` and
  `hybrid_canonical_detail` architecture-class evidence before any final
  Phase 8 GO / `LOCK_READY` decision;
- Phase 9 remains blocked until the complete canonical benchmark
  explicitly returns GO.

## Phase 8.10 — PRNet Direct-Neural-Dense Silhouette/Profile Evidence Checkpoint

The PRNet `direct_neural_dense` candidate now has deterministic raw
silhouette/lateral-view benchmark evidence over the current two-subject /
three-view real-photo evidence set.

New provider-specific evidence catalog:
- `CORE/atlas_canonical_head_prnet_benchmark_evidence.py`

New test:
- `Test/test_canonical_head_prnet_benchmark_evidence.py`

External persistent PRNet evidence:
- `/Users/Kubi/ATLAS_PRNET_SPIKE/EVIDENCE/phase8_10_prnet_2026-08-22/`
- persistent evidence file count: `29`;
- manifest entry count: `28`;
- manifest verification: `VERIFY_EXIT=0`;
- manifest SHA256:
  `b9c6c1dcf955cda612e975455e9887c90f4b1eb99a5c6600840ba9951f0286bd`.

Verified PRNet topology:
- canonical vertex count: `43867`;
- triangle count: `86906`;
- all six exported OBJ cases preserve the same topology.

Silhouette/lateral-view raw measurement protocol:
- the reference contour is the existing Atlas MediaPipe `face_oval`
  landmark chain;
- reference landmarks are transformed with the exact PRNet
  256 × 256 crop similarity transform;
- PRNet reconstructed silhouettes are rasterized from the preserved
  `43867`-vertex / `86906`-triangle topology;
- this reference is a MediaPipe face-oval projection, not 3D ground truth
  and not manual silhouette segmentation;
- `side_a` / `side_b` names are not treated as canonical profile
  classifications;
- lateral-view geometry is measured independently from file naming using
  bilateral landmark asymmetry.

Verified aggregate measurements:
- front case count: `2`;
- lateral case count: `4`;
- front mean silhouette IoU: `0.8580595773782285`;
- lateral mean silhouette IoU: `0.7694332569672948`;
- lateral minimum silhouette IoU: `0.7140243158622372`;
- lateral mean absolute normalized nose offset:
  `0.5696098447867725`.

Conservative Phase 8.10 PRNet evidence coverage:
- identity preservation: `MISSING`;
- multi-view consistency: `MISSING`;
- silhouette/profile: `PARTIAL`;
- head ratio: `MISSING`;
- jaw/chin: `MISSING`;
- nose projection: `MISSING`;
- orbital/cheek volume: `MISSING`;
- expression separation: `MISSING`;
- pose separation: `MISSING`;
- topology suitability: `DIRECT`;
- physical suitability: `MISSING`;
- Apple Silicon runtime: `DIRECT`;
- reproducibility: `DIRECT`.

Interpretation boundary:
- silhouette measurement is directly established;
- the combined silhouette/profile channel remains `PARTIAL` because
  canonical `profile_left` / `profile_right` classification has not yet
  been established for the lateral benchmark cases;
- raw IoU or lateral-offset values are not normalized support scores;
- no metric 3D identity, facial-volume, expression or physical-print
  evidence is inferred from this checkpoint;
- no PRNet candidate observation with calibrated support values is created;
- no PRNet GO/HOLD/REJECT decision is issued;
- the required three-architecture Phase 8.10 benchmark boundary remains
  unchanged;
- Phase 9 remains `NOT AUTHORIZED`.

Validation:
- PRNet evidence focused validation:
  `7 passed in 0.02s`;
- PRNet + coverage + FLAME related regression:
  `43 passed in 0.07s`;
- broad Phase 8.10 regression:
  `152 passed in 0.17s`;
- scoped PRNet `git diff --check`: clean;
- scoped documentation `git diff --check`: clean.

Next Phase 8.10 requirement:
- continue closing the remaining PRNet evidence gaps without converting
  incomplete raw evidence into fabricated support values;
- preserve the `silhouette/profile = PARTIAL` boundary until canonical
  profile classification or equivalent direct profile evidence exists;
- continue required `direct_neural_dense` evidence closure, then complete
  the `hybrid_canonical_detail` architecture-class evidence;
- Phase 9 remains blocked until the complete Phase 8 benchmark explicitly
  returns GO and is locked.

## Phase 8.10 — PRNet Direct-Neural-Dense Multi-View Consistency Checkpoint

The PRNet `direct_neural_dense` candidate now has deterministic raw
multi-view geometric consistency evidence over the current two-subject /
three-view real-photo evidence set.

Persistent external PRNet evidence:
- `/Users/Kubi/ATLAS_PRNET_SPIKE/EVIDENCE/phase8_10_prnet_2026-08-22/`
- multi-view measurement script:
  `prnet_phase8_10_multiview_consistency_measurement.py`;
- multi-view measurement artifact:
  `prnet_phase8_10_multiview_consistency_measurement.json`;
- manifest verification: `VERIFY_EXIT=0`;
- manifest SHA256:
  `6970201f05dfe43e2bf27b3193b09bfa2dfc7944b5353456fc6a6adb84759404`.

Measurement protocol:
- each subject contributes `front`, `side_a` and `side_b` PRNet
  reconstructions;
- all reconstructions preserve the same PRNet canonical UV topology with
  `43867` corresponded vertices;
- each view pair is aligned in 3D with deterministic similarity alignment;
- translation, rotation and uniform scale are removed;
- reflection is not allowed;
- residual error is computed vertex-to-corresponding-vertex over the shared
  canonical topology;
- residual RMS is normalized by the target mesh RMS radius.

Verified measurements:
- subject count: `2`;
- view count per subject: `3`;
- pair count: `6`;
- Subject 01 mean pairwise normalized residual:
  `0.036128559369067476`;
- Subject 02 mean pairwise normalized residual:
  `0.03721806460958436`;
- aggregate mean pairwise normalized residual:
  `0.03667331198932592`;
- aggregate maximum pairwise normalized residual:
  `0.04595704484272138`.

Interpretation boundary:
- this is direct PRNet multi-view geometric consistency evidence;
- this is not the FLAME `cross_view_identity_shape_nme` metric;
- this is not identity-preservation proof;
- this is not 3D ground-truth error;
- these raw residuals are not normalized support scores;
- no PRNet candidate GO/HOLD/REJECT decision is issued by this milestone;
- Phase 9 remains `NOT AUTHORIZED`.

Updated conservative PRNet Phase 8.10 evidence coverage:
- identity preservation: `MISSING`;
- multi-view consistency: `MEASURED`;
- silhouette/profile: `PARTIAL`;
- head ratio: `MISSING`;
- jaw/chin: `MISSING`;
- nose projection: `MISSING`;
- orbital/cheek volume: `MISSING`;
- expression separation: `MISSING`;
- pose separation: `MISSING`;
- topology suitability: `DIRECT`;
- physical suitability: `MISSING`;
- Apple Silicon runtime: `DIRECT`;
- reproducibility: `DIRECT`.

Validation:
- PRNet focused evidence validation:
  `8 passed in 0.03s`;
- PRNet + coverage + FLAME related regression:
  `44 passed in 0.07s`;
- broad Phase 8.10 regression:
  `153 passed in 0.18s`;
- scoped `git diff --check`: clean.

Next Phase 8.10 requirement:
- continue closing the remaining PRNet evidence gaps without converting
  multi-view consistency into unsupported identity claims;
- preserve `silhouette/profile = PARTIAL` until direct profile evidence
  exists;
- continue required `direct_neural_dense` evidence closure;
- then complete the `hybrid_canonical_detail` architecture-class evidence;
- Phase 9 remains blocked until the complete Phase 8 benchmark explicitly
  returns GO and is locked.

## Phase 8.10 — Hybrid Canonical Detail Residual-Detail Contract — IMPLEMENTED

The required `hybrid_canonical_detail` architecture class now has a
provider-independent canonical residual-detail composition layer.

New contracts:
- `CORE/atlas_canonical_head_residual_detail_displacement.py`
- `CORE/atlas_canonical_head_residual_detail_compatibility_gate.py`
- `CORE/atlas_canonical_head_residual_detail_composition.py`

Tests:
- `Test/test_canonical_head_residual_detail_displacement.py`
- `Test/test_canonical_head_residual_detail_compatibility_gate.py`
- `Test/test_canonical_head_residual_detail_composition.py`

Architectural behavior:
- residual detail is represented as an immutable finite `(N, 3)`
  displacement bound to canonical head topology;
- residual detail remains separate from identity shape, expression,
  asymmetry, pose, camera, provider state, confidence and likeness;
- compatibility is determined by canonical connectivity signature rather
  than topology object identity;
- mixed identity/detail connectivity is explicitly blocked with
  `BLOCKED_IDENTITY_RESIDUAL_DETAIL_CONNECTIVITY_MISMATCH`;
- composition resolves canonical identity geometry plus residual-detail
  displacement without mutating either source contract;
- canonical topology and connectivity signature are preserved.

Verified validation:
- residual-detail focused validation: `21 passed in 0.08s`;
- related canonical displacement regression: `83 passed in 0.24s`;
- broad canonical-head regression: `475 passed in 0.73s`;
- scoped `git diff --check`: clean.

Hybrid evidence boundary:
- six Phase 8.10 benchmark photographs now have real DSINE float32 normal
  evidence generated on Apple Silicon MPS in the external hybrid evidence
  workspace;
- DSINE normals are restricted to the role
  `bounded_low_amplitude_residual_detail_source_only`;
- DSINE normals are not canonical identity geometry;
- DSINE normals are not 3D ground truth;
- DSINE normals are not identity-preservation or pose-separation proof;
- the DSINE-to-canonical residual-detail projection/correspondence bridge
  is not yet implemented;
- the `hybrid_canonical_detail` benchmark candidate is therefore not yet
  complete;
- no normalized support score or GO/HOLD/REJECT decision is issued by
  this milestone;
- Phase 9 remains `NOT AUTHORIZED`.

External hybrid evidence provenance:
- evidence directory:
  `/Users/Kubi/ATLAS_HYBRID_SPIKE/EVIDENCE/phase8_10_hybrid_dsine_2026-08-23/`;
- DSINE repo commit:
  `ef0c2afa32b4dd19cb8ca4567c652802cd92591c`;
- DSINE architecture: `v02`;
- runtime: Python `3.12.13`, Torch `2.13.0`, Apple Silicon MPS;
- benchmark cases completed: `6/6`;
- all normal fields: shape `1152 x 1536 x 3`, dtype `float32`, finite,
  mean normal length `1.0`;
- evidence manifest verification: `VERIFY_EXIT=0`;
- manifest SHA256:
  `cd6dbf999899fd50fe8c222070cf465ac55120092756138d0437ea277756eceb`.

Next Phase 8.10 requirement:
- define and validate the deterministic bridge from bounded image-space
  residual-detail observations to canonical-head vertex displacement;
- preserve canonical topology and prevent appearance-to-geometry leakage;
- then evaluate hybrid candidate evidence under the same Phase 8.10
  benchmark channels;
- Phase 9 remains blocked until the complete canonical benchmark
  explicitly returns GO.

## Phase 8.10 — Canonical Normal-Directed Residual Detail Primitive — IMPLEMENTED

The hybrid canonical-detail path now has provider-independent geometry
primitives for restricting residual detail to canonical surface-normal
motion.

New contracts:
- `CORE/atlas_canonical_head_vertex_normal_evaluator.py`
- `CORE/atlas_canonical_head_normal_residual_detail_projector.py`

Tests:
- `Test/test_canonical_head_vertex_normal_evaluator.py`
- `Test/test_canonical_head_normal_residual_detail_projector.py`

Architectural behavior:
- canonical vertex normals are deterministically derived from canonical
  geometry and topology face winding;
- face cross-products are accumulated at incident vertices and normalized;
- degenerate faces or unresolved degenerate vertex normals are rejected;
- returned normal and displacement arrays are immutable float64 snapshots;
- residual-detail amplitudes are scalar values with one value per canonical
  vertex;
- scalar amplitudes are converted to `(N, 3)` displacement only along the
  canonical vertex-normal direction;
- this primitive does not permit arbitrary tangential residual-detail
  displacement;
- the primitive carries no provider, camera, pose, confidence, likeness or
  Phase 9 authorization state.

Validation:
- focused vertex-normal/projector validation: `15 passed in 0.06s`;
- related geometry/residual-detail regression: `60 passed in 0.16s`;
- broad canonical-head regression: `490 passed in 0.77s`;
- scoped `git diff --check`: clean.

Interpretation boundary:
- this does not yet map DSINE image-space observations to canonical vertices;
- this does not define image sampling, visibility, camera projection or
  multi-view fusion;
- this does not establish a residual-detail amplitude bound or confidence
  policy;
- DSINE remains only a bounded low-amplitude residual-detail evidence source;
- the `hybrid_canonical_detail` benchmark candidate remains incomplete;
- Phase 9 remains `NOT AUTHORIZED`.

Next exact Phase 8.10 task:
- define the provider-independent observation/correspondence boundary that
  maps bounded image-space residual-detail evidence onto canonical vertex
  scalar amplitudes before normal-directed projection.

## Phase 8.10 — Residual Detail Observation / Correspondence Boundary — IMPLEMENTED

The hybrid canonical-detail path now has a provider-independent image-space
residual-detail observation contract and a separate compatibility boundary to
canonical dense correspondence.

New contracts:
- `CORE/atlas_canonical_head_residual_detail_observation.py`
- `CORE/atlas_canonical_head_residual_detail_correspondence_gate.py`

Tests:
- `Test/test_canonical_head_residual_detail_observation.py`
- `Test/test_canonical_head_residual_detail_correspondence_gate.py`

Architectural behavior:
- residual-detail evidence is represented as indexed image-space samples;
- each observation stores normalized image coordinates, scalar residual-detail
  values and per-sample confidence;
- image coordinates are independent from canonical vertex identity;
- canonical vertex mapping remains owned by the existing
  `AtlasCanonicalHeadDenseCorrespondence` contract;
- the compatibility gate accepts only correspondence sample IDs that exist in
  the observation;
- observations may contain additional unmapped samples;
- unknown correspondence sample IDs are explicitly blocked with
  `BLOCKED_RESIDUAL_DETAIL_OBSERVATION_SAMPLE_MISMATCH`;
- the compatibility result exposes matched observation sample IDs, canonical
  vertex IDs and the canonical connectivity signature.

Validation:
- focused observation/correspondence validation: `23 passed in 0.07s`;
- related residual-detail contracts: `67 passed in 0.16s`;
- broad canonical-head regression: `513 passed in 0.79s`;
- scoped `git diff --check`: clean.

Interpretation boundary:
- no provider identity is embedded in the canonical observation contract;
- no DSINE-specific logic is present;
- no camera projection, visibility or occlusion decision is performed;
- no confidence weighting is applied to scalar detail;
- no amplitude bound is applied;
- no canonical `(N,)` amplitude vector is generated yet;
- no residual displacement is produced by this boundary;
- the `hybrid_canonical_detail` benchmark candidate remains incomplete;
- Phase 9 remains `NOT AUTHORIZED`.

Next exact Phase 8.10 task:
- define the canonical scalar-amplitude resolver that consumes a compatible
  residual-detail observation plus dense correspondence and produces a
  canonical per-vertex scalar detail vector while preserving explicit
  confidence and amplitude-policy boundaries.

## Phase 8.10 — Canonical Residual-Detail Scalar-Amplitude Resolver — IMPLEMENTED

The hybrid canonical-detail path now has a provider-independent resolver that
moves compatible indexed residual-detail observations into canonical vertex
space while preserving raw scalar detail and confidence as separate channels.

New contract:
- `CORE/atlas_canonical_head_residual_detail_amplitude_resolver.py`

Test:
- `Test/test_canonical_head_residual_detail_amplitude_resolver.py`

Architectural behavior:
- consumes `AtlasCanonicalHeadResidualDetailObservation` plus
  `AtlasCanonicalHeadDenseCorrespondence`;
- reuses the existing residual-detail correspondence compatibility gate;
- produces canonical-length raw scalar-detail and confidence arrays;
- unmapped canonical vertices remain zero;
- raw scalar detail is not multiplied by confidence;
- canonical connectivity signature is preserved;
- result arrays are immutable snapshots.

Validation:
- focused amplitude resolver: `8 passed in 0.05s`;
- related residual-detail regression: `82 passed in 0.20s`;
- broad canonical-head regression: `521 passed in 0.82s`;
- scoped `git diff --check`: clean.

Interpretation boundary:
- no confidence weighting policy is applied;
- no maximum-amplitude policy or clipping is applied;
- no visibility or occlusion decision is performed;
- no camera or pose projection is performed;
- no residual displacement or geometry is produced;
- no provider identity is embedded;
- the `hybrid_canonical_detail` benchmark candidate remains incomplete;
- Phase 9 remains `NOT AUTHORIZED`.

Next exact Phase 8.10 task:
- define the residual-detail amplitude policy layer that can apply explicit
  confidence weighting and bounded amplitude limits without mixing those
  policy decisions into observation, correspondence, or canonical mapping.

## Phase 8.10 — Residual-Detail Amplitude Policy Layer — IMPLEMENTED

The hybrid canonical-detail path now has a separate policy layer that applies
confidence weighting and a bounded symmetric amplitude limit after canonical
scalar-detail mapping.

New contract:
- `CORE/atlas_canonical_head_residual_detail_amplitude_policy.py`

Test:
- `Test/test_canonical_head_residual_detail_amplitude_policy.py`

Architectural behavior:
- consumes `AtlasCanonicalHeadResidualDetailAmplitudeResult`;
- computes weighted amplitude as raw canonical scalar detail multiplied by
  canonical confidence;
- zero confidence removes residual-detail contribution;
- applies a symmetric `±maximum_absolute_amplitude` bound;
- preserves canonical connectivity signature and mapped vertex count;
- does not mutate the upstream amplitude-resolver result;
- weighted and bounded amplitude arrays are immutable snapshots.

Validation:
- focused amplitude-policy validation: `14 passed in 0.05s`;
- related amplitude/residual-detail regression: `81 passed in 0.21s`;
- broad canonical-head regression: `535 passed in 0.84s`;
- scoped `git diff --check`: clean.

Interpretation boundary:
- this layer owns confidence weighting and amplitude bounding only;
- no visibility or occlusion decision is performed;
- no camera or pose projection is performed;
- no normal-space direction is selected;
- no canonical residual displacement is produced here;
- no geometry is generated;
- no provider identity is embedded;
- the `hybrid_canonical_detail` benchmark candidate remains incomplete;
- Phase 9 remains `NOT AUTHORIZED`.

Next exact Phase 8.10 task:
- define the view-to-canonical residual-detail bridge that combines real
  observation evidence, dense correspondence and the existing amplitude
  resolver/policy chain while preserving explicit projection/visibility
  boundaries.

## Phase 8.10 — View-to-Canonical Residual-Detail Bridge — IMPLEMENTED

The hybrid canonical-detail path now has a provider-independent orchestration
bridge that connects one residual-detail view observation to canonical vertex
space through the already separated correspondence, amplitude-resolver and
amplitude-policy layers.

New contract:
- `CORE/atlas_canonical_head_view_residual_detail_bridge.py`

Test:
- `Test/test_canonical_head_view_residual_detail_bridge.py`

Architectural behavior:
- consumes `AtlasCanonicalHeadResidualDetailObservation`;
- consumes `AtlasCanonicalHeadDenseCorrespondence`;
- delegates canonical scalar/confidence mapping to the existing amplitude
  resolver;
- delegates confidence weighting and symmetric amplitude bounding to the
  existing amplitude-policy layer;
- preserves observation identity, source-view identity, canonical connectivity
  signature and mapped vertex count;
- returns immutable snapshots of raw scalar detail, confidence, weighted
  amplitude and bounded amplitude;
- does not mutate the source observation.

Validation:
- focused view-to-canonical bridge: `9 passed in 0.05s`;
- related hybrid-detail regression: `90 passed in 0.22s`;
- broad canonical-head regression: `544 passed in 0.86s`;
- scoped `git diff --check`: clean.

Interpretation boundary:
- this bridge performs orchestration only;
- no camera projection is performed;
- no pose normalization is performed;
- no visibility or occlusion decision is performed;
- no normal direction is selected;
- no canonical residual displacement is generated;
- no geometry is generated;
- no provider identity is embedded;
- this does not yet constitute real DSINE-to-canonical benchmark evidence;
- the `hybrid_canonical_detail` benchmark candidate remains incomplete;
- Phase 9 remains `NOT AUTHORIZED`.

Next exact Phase 8.10 task:
- connect real held benchmark-view residual-detail evidence into this bridge
  through an explicit image/view sampling boundary, while keeping camera,
  visibility and projection assumptions separately auditable.

## Phase 8.10 — Residual-Detail Image/View Sampling Boundary — IMPLEMENTED

The hybrid canonical-detail path now has a provider-independent image/view
sampling boundary that converts two-dimensional scalar-detail and confidence
fields into `AtlasCanonicalHeadResidualDetailObservation` samples.

New contract:
- `CORE/atlas_canonical_head_residual_detail_image_sampler.py`

Test:
- `Test/test_canonical_head_residual_detail_image_sampler.py`

Architectural behavior:
- consumes one 2D scalar-detail field;
- consumes one shape-matched 2D confidence field;
- consumes normalized image-space sample coordinates;
- performs deterministic bilinear sampling;
- preserves scalar detail and confidence as separate channels;
- returns the existing immutable residual-detail observation contract;
- derives image width and height from the sampled fields;
- does not apply confidence weighting to scalar detail.

Validation:
- focused image/view sampler: `10 passed in 0.05s`;
- related view/detail contracts: `64 passed in 0.14s`;
- broad canonical-head regression: `554 passed in 0.88s`;
- scoped `git diff --check`: clean.

Interpretation boundary:
- no DSINE file loading is performed;
- no provider-specific normal decoding is performed;
- no camera or pose projection is performed;
- no visibility or occlusion decision is performed;
- no dense canonical correspondence is performed;
- no amplitude weighting or clipping is performed;
- no canonical displacement or geometry is generated;
- this is not yet real held-view hybrid benchmark evidence;
- the `hybrid_canonical_detail` benchmark candidate remains incomplete;
- Phase 9 remains `NOT AUTHORIZED`.

Next exact Phase 8.10 task:
- connect the real held benchmark-view DSINE normal evidence to an explicit
  residual-detail scalar/confidence field source and feed those fields through
  this sampling boundary without collapsing provider provenance, projection or
  visibility assumptions into the generic sampler.

## Phase 8.10 — DSINE Residual-Detail Field Source — IMPLEMENTED

The hybrid canonical-detail path now has a bounded interpretation source that
converts a DSINE-style normal field into a residual scalar-detail field while
preserving confidence as a separate channel.

New contract:
- `CORE/atlas_canonical_head_dsine_residual_detail_field_source.py`

Test:
- `Test/test_canonical_head_dsine_residual_detail_field_source.py`

Architectural behavior:
- consumes a finite `(H, W, 3)` normal field;
- consumes an explicit shape-matched confidence field;
- reuses `AtlasReliefNormalStructureDetailDecomposer` to isolate residual
  detail normals;
- reuses `AtlasReliefNormalHeightIntegrator` with
  `normalize_output=False`;
- zero-centers the resulting residual scalar-detail field;
- preserves confidence unchanged as a separate immutable channel;
- does not confidence-weight the scalar-detail field at this stage.

Validation:
- focused DSINE residual-detail field source: `13 passed in 0.05s`;
- related normal/detail regression: `99 passed in 0.18s`;
- broad canonical-head regression: `567 passed in 0.90s`;
- scoped `git diff --check`: clean.

Interpretation boundary:
- DSINE normals are not canonical identity geometry;
- DSINE normals are not 3D ground truth;
- confidence is not inferred from DSINE normals;
- confidence weighting is intentionally deferred to the existing canonical
  amplitude-policy layer to avoid double weighting;
- no image sampling is performed here;
- no camera, pose, visibility or occlusion reasoning is performed;
- no dense canonical correspondence is performed;
- no canonical displacement or geometry is generated;
- the `hybrid_canonical_detail` benchmark candidate remains incomplete;
- Phase 9 remains `NOT AUTHORIZED`.

Next exact Phase 8.10 task:
- run the real six-view DSINE benchmark evidence through this field source and
  the existing image-sampling boundary, producing auditable real residual-detail
  observations before canonical correspondence and bounded bridge evaluation.

## Phase 8.10 — DSINE Residual-Detail Explicit Face-Support Mask Boundary — IMPLEMENTED

The DSINE residual-detail field source now accepts an explicit face-support mask.

Purpose:
- keep residual-detail decomposition and integration constrained to explicit face support;
- prevent background normal regions from contributing to the residual scalar field;
- preserve the confidence channel independently from the support mask.

Implementation:
- `AtlasCanonicalHeadDsineResidualDetailFieldSource.build(...)` now accepts
  optional `mask=`;
- mask shape must match the DSINE normal field;
- mask values must be finite;
- mask values are clipped to `0.0..1.0`;
- the mask must contain at least one active pixel;
- the mask is forwarded to
  `AtlasReliefNormalStructureDetailDecomposer.decompose(...)`;
- the same mask is forwarded to
  `AtlasReliefNormalHeightIntegrator.integrate(...)`;
- zero-centering is computed only over active mask pixels;
- scalar residual detail outside the mask is forced to `0.0`;
- explicit confidence is not altered by the mask.

Validation:
- focused DSINE field-source: `17 passed in 0.05s`;
- related normal/detail regression: `103 passed in 0.18s`;
- broad canonical-head regression: `571 passed in 0.90s`;
- scoped `git diff --check`: clean.

Evidence interpretation:
- the current six-view benchmark does not contain independent subject-mask evidence;
- therefore no full-image `np.ones()` mask may be silently substituted;
- the next real six-view run will derive explicit face support from the existing
  MediaPipe landmark `face_oval -> face_interior` path;
- that support must be recorded as `landmark-derived face support`, not as an
  independently observed segmentation mask;
- DSINE normals remain bounded residual-detail evidence only;
- Phase 9 remains `NOT AUTHORIZED`.

## Phase 8.10 — Real Six-View DSINE Residual-Detail Observation Run — VERIFIED

The real six-view benchmark evidence has now been run through the
landmark-derived support/confidence path, DSINE residual-detail field source and
image-sampling boundary without creating canonical correspondence or canonical
geometry.

Verified pipeline:
- existing MediaPipe 478-point landmark JSON is converted to absolute image-space
  coordinates;
- `AtlasReliefMediaPipeLandmarkAdapter` produces the semantic landmark groups;
- `AtlasReliefFaceLandmarkRegions` derives `face_oval -> face_interior`;
- `face_interior` is used as explicit landmark-derived face support;
- `AtlasReliefFaceStructureConfidenceMap` produces the separate semantic
  confidence field;
- real DSINE normals are processed by
  `AtlasCanonicalHeadDsineResidualDetailFieldSource`;
- resulting scalar-detail and confidence fields are sampled by
  `AtlasCanonicalHeadResidualDetailImageSampler`;
- each view produces 478 real residual-detail samples.

Verified real six-view measurements:
- `subject_01_front`: support `77019`, confidence mean `0.798674`,
  detail range `-1.357800 .. 3.942569`;
- `subject_01_side_a`: support `39351`, confidence mean `0.863371`,
  detail range `-3.354918 .. 3.404447`;
- `subject_01_side_b`: support `27231`, confidence mean `0.873235`,
  detail range `-2.572433 .. 5.402657`;
- `subject_02_front`: support `178146`, confidence mean `0.832813`,
  detail range `-2.293613 .. 3.930144`;
- `subject_02_side_a`: support `29739`, confidence mean `0.846852`,
  detail range `-3.183855 .. 3.890012`;
- `subject_02_side_b`: support `27691`, confidence mean `0.856909`,
  detail range `-2.626679 .. 5.148389`.

Validation facts:
- all six DSINE normal fields match `(1152, 1536, 3)`;
- all generated support/confidence/detail outputs are finite;
- residual detail outside explicit face support is exactly `0.0` for all six
  views;
- all six observations contain `478` samples;
- confidence remains a separate channel and is not multiplied into scalar detail
  at field-source or sampling stage.

Interpretation boundary:
- the support is landmark-derived face support, not an independently observed
  segmentation mask;
- the MediaPipe top-level provider confidence is not treated as identity evidence
  confidence;
- the 478 sampled points are image-space residual-detail observations, not dense
  canonical correspondence;
- DSINE normals remain bounded residual-detail evidence only;
- no canonical vertex displacement has been produced;
- no hybrid candidate GO/HOLD/REJECT decision has been issued;
- Phase 9 remains `NOT AUTHORIZED`.

Next exact Phase 8.10 task:
- resolve the correct canonical correspondence boundary for the real residual
  observations;
- do not reinterpret the existing 105 MediaPipe-to-FLAME barycentric face
  correspondences as direct canonical-vertex mappings;
- once correspondence semantics are explicit, run the canonical amplitude
  resolver, bounded amplitude policy and view-to-canonical bridge and record
  quantitative hybrid evidence.


## Phase 8.10 — Canonical Surface/Barycentric Correspondence Boundary — IMPLEMENTED

The canonical-head correspondence boundary now explicitly supports observed
samples whose canonical targets lie on triangle surfaces rather than directly on
canonical vertices.

Why this boundary was required:
- the existing `AtlasCanonicalHeadDenseCorrespondence` and
  `AtlasCanonicalHeadLandmarkCorrespondence` contracts represent direct
  observed-sample/landmark -> canonical-vertex mappings;
- the real FLAME MediaPipe embedding instead provides
  observed landmark -> FLAME face index + barycentric weights;
- reinterpreting those 105 FLAME correspondences as direct canonical vertices
  would therefore be semantically and geometrically incorrect;
- the existing `AtlasSurfaceProjectionEngine` contains internal barycentric
  projection mathematics, but it is not a canonical-head correspondence
  contract.

Implementation:
- added `AtlasCanonicalHeadSurfaceCorrespondence`;
- each observed sample maps to:
  - one canonical triangle/face index;
  - exactly three barycentric weights;
- the contract is bound directly to `AtlasCanonicalHeadTopology`;
- canonical face indices must be inside the topology face range;
- barycentric weights must be finite and inside `0.0..1.0`;
- barycentric weights must sum to `1.0` within numerical tolerance;
- multiple observed samples may validly target the same canonical face;
- the canonical topology connectivity signature is preserved;
- the contract does not claim provider, camera, pose, visibility, identity
  confidence, scalar detail, displacement, geometry or Phase 9 authorization.

Files:
- `CORE/atlas_canonical_head_surface_correspondence.py`
- `Test/test_canonical_head_surface_correspondence.py`

Validation:
- focused surface-correspondence contract: `9 passed in 0.03s`;
- related canonical correspondence/residual-detail regression:
  `75 passed in 0.16s`;
- broad canonical-head regression: `580 passed in 0.91s`;
- full ATLAS regression: `4857 passed in 125.44s`;
- scoped `git diff --check`: clean.

Architecture boundary:
- existing direct-vertex correspondence contracts remain unchanged;
- existing residual-detail amplitude resolver and view bridge remain
  direct-vertex based and have not yet been modified;
- this milestone only establishes the missing provider-independent canonical
  surface correspondence semantics;
- no FLAME barycentric embedding has yet been coerced into a vertex mapping;
- no canonical residual displacement has yet been produced from the real
  six-view DSINE observations;
- no hybrid candidate `GO / HOLD / REJECT` has been issued;
- Phase 9 remains `NOT AUTHORIZED`.

Next exact Phase 8.10 task:
- define the smallest explicit bridge from canonical surface correspondence to
  canonical residual-detail amplitude representation;
- preserve the existing confidence-weighting and bounded-amplitude policy
  boundaries;
- then run the real 105 MediaPipe-to-FLAME barycentric correspondences through
  the six-view residual-detail evidence path;
- record quantitative hybrid canonical-detail evidence before any architecture
  decision.


## Phase 8.10 — Canonical Surface-to-Vertex Residual-Detail Amplitude Resolver — IMPLEMENTED

The canonical residual-detail path now has an explicit bridge from barycentric
canonical-surface observations to the existing per-canonical-vertex amplitude
representation.

Why this bridge is required:
- `AtlasCanonicalHeadSurfaceCorrespondence` correctly represents an observed
  sample as canonical face index + barycentric weights;
- downstream residual-detail policy, normal projection and displacement
  contracts operate on one scalar amplitude per canonical vertex;
- a barycentric surface observation therefore must not be coerced into one
  arbitrary canonical vertex;
- the bridge must solve the surface constraints explicitly before the existing
  amplitude-policy layer is entered.

Implementation:
- added `AtlasCanonicalHeadSurfaceResidualDetailAmplitudeResolver`;
- reuses the existing
  `AtlasCanonicalHeadResidualDetailAmplitudeResult` output contract;
- builds the barycentric linear system only over canonical vertices supported by
  the supplied surface correspondences;
- resolves raw canonical vertex scalar detail with deterministic
  `numpy.linalg.lstsq`;
- unmapped canonical vertices remain exactly zero;
- canonical confidence remains a separate channel;
- confidence is transferred to supported vertices by barycentric support-weighted
  averaging and is not multiplied into raw scalar detail;
- confidence weighting of amplitude remains owned exclusively by
  `AtlasCanonicalHeadResidualDetailAmplitudePolicy`;
- topology connectivity signature is preserved;
- unknown observation sample references are blocked.

Files:
- `CORE/atlas_canonical_head_surface_residual_detail_amplitude_resolver.py`
- `Test/test_canonical_head_surface_residual_detail_amplitude_resolver.py`

Validation:
- focused surface-amplitude resolver: `7 passed in 0.05s`;
- related surface/residual-detail regression: `91 passed in 0.22s`;
- broad canonical-head regression: `587 passed in 0.94s`;
- full ATLAS regression: `4864 passed in 126.95s`;
- scoped `git diff --check`: clean.

Architecture boundary:
- the existing direct-vertex amplitude resolver remains unchanged;
- the existing bounded-amplitude policy remains unchanged;
- the existing normal residual-detail projector remains unchanged;
- the existing residual-detail displacement/composition contracts remain
  unchanged;
- no provider-specific FLAME logic is embedded in this resolver;
- no camera, pose, visibility or identity claim is introduced;
- no real six-view FLAME/DSINE canonical amplitude evidence has yet been
  produced by this new bridge;
- no hybrid candidate `GO / HOLD / REJECT` has been issued;
- Phase 9 remains `NOT AUTHORIZED`.

Next exact Phase 8.10 task:
- connect the real 105 MediaPipe-to-FLAME face+barycentric embedding to the
  canonical surface correspondence contract;
- run the six real DSINE residual-detail observations through the new
  surface-to-vertex amplitude resolver;
- apply the existing bounded-amplitude policy and canonical normal projection
  boundaries;
- record quantitative hybrid canonical-detail evidence;
- only after that evidence is audited may the remaining benchmark gaps and final
  three-architecture comparison proceed.


## Phase 8.10 — FLAME Barycentric Floating-Point Boundary Tolerance — IMPLEMENTED

The canonical surface-correspondence contract now safely accepts the tiny
floating-point boundary noise present in the real FLAME MediaPipe embedding
without weakening the barycentric validity rules.

Observed real FLAME evidence:
- `lmk_face_idx`: 105 entries;
- `lmk_b_coords`: shape `(105, 3)`;
- `landmark_indices`: 105 unique MediaPipe landmark IDs;
- barycentric weight sums range from
  `0.9999999999999999` to `1.0000000000000002`;
- minimum observed weight is
  `-1.3322676295501878e-15`;
- this negative value is floating-point roundoff around mathematical zero, not
  a meaningful negative barycentric coordinate.

Implementation:
- `AtlasCanonicalHeadSurfaceCorrespondence` now permits only tiny barycentric
  boundary excursions within `1e-12`;
- values below `0.0` or above `1.0` within that tolerance are clamped to the
  valid interval;
- the clamped triplet is deterministically renormalized so the final weights
  sum to exactly the canonical barycentric unit total within numerical
  precision;
- materially invalid barycentric weights outside the tolerance remain rejected;
- the existing provider-independent surface-correspondence semantics remain
  unchanged.

Validation:
- focused surface-correspondence tests: `10 passed in 0.03s`;
- related surface correspondence/amplitude regression:
  `69 passed in 0.17s`;
- broad canonical-head regression: `588 passed in 0.95s`;
- full ATLAS regression: `4865 passed in 119.64s`.

Evidence interpretation:
- this change is required by the actual FLAME embedding data;
- it does not approximate or reinterpret the 105 correspondences as canonical
  vertices;
- it does not change the surface-to-vertex least-squares amplitude resolver;
- it does not alter confidence weighting;
- it does not introduce provider, camera, pose, visibility or identity claims;
- no real six-view canonical hybrid-detail amplitude evidence has yet been
  produced;
- no hybrid candidate `GO / HOLD / REJECT` has been issued;
- Phase 9 remains `NOT AUTHORIZED`.

Next exact Phase 8.10 task:
- construct the real canonical FLAME topology from the verified
  `flame2023_Open.pkl` face connectivity;
- bind the real 105 MediaPipe landmark IDs to their verified FLAME face indices
  and barycentric weights through
  `AtlasCanonicalHeadSurfaceCorrespondence`;
- verify all six real landmark observations contain the required 105 landmark
  IDs;
- only then run the six DSINE residual-detail observations through the
  surface-to-vertex amplitude resolver and existing bounded-amplitude policy.


## Phase 8.10 — Residual-Detail Scale Normalization Boundary — IMPLEMENTED

The hybrid canonical-detail path now has an explicit provider-independent
normalization boundary between image-space residual-detail measurements and
canonical model-space amplitude.

Problem resolved:
- DSINE residual scalar-detail is produced by integrating image-space normal
  gradients over pixel steps;
- therefore the raw scalar-detail magnitude is resolution- and image-scale
  dependent;
- FLAME canonical geometry exists in a separate canonical model-space scale;
- raw DSINE scalar-detail must not be interpreted directly as canonical vertex
  displacement amplitude.

Normalization rule:
- `scale_factor = canonical_reference_span / image_reference_span_px`;
- normalized canonical residual detail is
  `image_space_scalar_detail * scale_factor`;
- the image reference span and canonical reference span are explicit caller
  inputs;
- scaling both the image-space residual magnitude and the image reference span
  by the same resolution factor leaves the normalized canonical residual detail
  unchanged.

Implementation:
- added
  `CORE/atlas_canonical_head_residual_detail_scale_normalizer.py`;
- added
  `AtlasCanonicalHeadResidualDetailScaleNormalizer`;
- added immutable
  `AtlasCanonicalHeadResidualDetailScaleNormalizationResult`;
- observation identity, source-view identity, sample indices, normalized sample
  coordinates and confidence are preserved;
- confidence remains a separate channel and is not modified by scale
  normalization;
- source observations are not mutated;
- invalid, non-finite or non-positive reference spans are rejected.

Test:
- `Test/test_canonical_head_residual_detail_scale_normalizer.py`

Validation:
- focused scale-normalizer tests: `13 passed in 0.05s`;
- related residual-detail regression: `79 passed in 0.17s`;
- broad canonical-head regression: `601 passed in 0.99s`;
- full ATLAS regression: `4878 passed in 120.83s`.

Architecture boundary:
- this contract defines scale normalization only;
- it does not select a physical millimeter amplitude limit;
- it does not apply confidence weighting;
- it does not perform barycentric surface-to-vertex resolution;
- it does not perform normal projection or geometry composition;
- no provider-specific FLAME or DSINE behavior is embedded;
- no hybrid `GO / HOLD / REJECT` decision is issued;
- Phase 9 remains `NOT AUTHORIZED`.

Next exact Phase 8.10 task:
- produce the six real residual-detail observations from the existing DSINE
  normal evidence and MediaPipe landmark data;
- select the verified 105 MediaPipe landmark samples required by the FLAME
  barycentric embedding;
- apply this scale-normalization boundary using an explicit per-view image
  reference span and the corresponding canonical FLAME reference span;
- then run the normalized observations through the existing canonical
  surface-to-vertex amplitude resolver.

## Phase 8.10 — Checklist Item 5 Real FLAME Surface Correspondence — VERIFIED

The original Phase 8.10 `Exact next Phase 8.10 work` checklist item 5,
`connect those observations through dense correspondence`, is now satisfied
through the corrected provider-independent canonical surface correspondence
boundary.

Important architecture clarification:
- the real FLAME MediaPipe embedding is not a direct canonical-vertex map;
- the verified path is:
  `MediaPipe sample -> FLAME face index + barycentric weights -> canonical surface`;
- `AtlasCanonicalHeadSurfaceCorrespondence` remains the authoritative boundary;
- no 105 MediaPipe landmark is reinterpreted as a canonical FLAME vertex.

Real evidence verified:
- six benchmark views;
- 478 real MediaPipe samples per view;
- all six views contain the required FLAME embedding landmark set:
  `105 / 105`;
- real FLAME MediaPipe embedding:
  - 105 landmark IDs;
  - 105 FLAME face indices;
  - 105 barycentric triplets;
- real FLAME topology:
  - 5023 canonical vertices;
  - 9976 triangular faces;
- six real DSINE normal artifacts are available from the persistent hybrid
  evidence directory;
- DSINE artifact integrity audit:
  - 6 / 6 files present;
  - shape `(1152, 1536, 3)`;
  - dtype `float32`;
  - all finite;
  - SHA-256 values match the persistent `SHA256SUMS.txt` manifest;
- each real DSINE observation contains 478 finite scalar-detail/confidence
  samples;
- the required 105 samples from every real observation bind successfully to
  the verified FLAME face+barycentric canonical surface correspondence;
- confidence remains a separate channel.

New real-data integration test:
- `Test/test_phase8_10_real_flame_surface_correspondence.py`

Validation:
- focused real correspondence integration:
  `3 passed, 3 warnings in 2.89s`;
- related correspondence/residual-detail regression:
  `64 passed, 3 warnings in 2.98s`;
- broad canonical-head regression:
  `604 passed, 3 warnings in 3.83s`;
- full ATLAS regression:
  `4881 passed, 3 warnings in 123.16s`;
- scoped `git diff --check`:
  clean.

Warning note:
- the three warnings are NumPy deprecation warnings emitted while loading the
  historical FLAME pickle (`numpy.core.numeric`);
- they do not change the verified correspondence behavior and are not a Phase
  8.10 blocker.

Original Phase 8.10 checklist status:
1. run six real DSINE normal fields through field source — DONE;
2. preserve explicit confidence separately — DONE;
3. scalar-detail + confidence through image sampler — DONE;
4. create real residual-detail observations — DONE;
5. connect observations through correspondence — DONE;
6. run canonical amplitude resolver — NEXT;
7. apply bounded amplitude policy — PENDING;
8. run view-to-canonical bridge — PENDING;
9. record quantitative real hybrid-detail evidence — PENDING;
10. close remaining benchmark evidence gaps — PENDING;
11. perform architecture-class comparison — PENDING;
12. issue final Phase 8 GO / HOLD / REJECT — PENDING;
13. only explicit GO may authorize Phase 9 — PENDING.

Exact next Phase 8.10 task:
- checklist item 6;
- run the six real, 105-sample FLAME-surface-bound residual-detail observations
  through the existing
  `AtlasCanonicalHeadSurfaceResidualDetailAmplitudeResolver`;
- preserve confidence as a separate channel;
- do not yet apply the bounded-amplitude policy or issue any hybrid
  GO / HOLD / REJECT decision.

Phase 8.10 remains `ACTIVE`.
Phase 9 remains `NOT AUTHORIZED`.

## Phase 8.10 — Checklist Item 6 Real Canonical Surface Amplitude — VERIFIED

The original Phase 8.10 `Exact next Phase 8.10 work` checklist item 6,
`run the canonical amplitude resolver`, is now verified with the six real
DSINE benchmark views through the FLAME barycentric canonical-surface path.

Scale-reference boundary:
- raw DSINE scalar-detail is not interpreted directly as canonical model-space
  displacement;
- no undocumented historical IOD formula is reused;
- a provider-independent correspondence reference-span boundary was added;
- image reference span is the 2D bounding-box diagonal of the corresponded
  observation samples in pixels;
- canonical reference span is the 3D bounding-box diagonal of the same
  barycentric canonical-surface samples;
- the resulting spans are passed through the existing
  `AtlasCanonicalHeadResidualDetailScaleNormalizer`.

Implementation:
- `CORE/atlas_canonical_head_correspondence_reference_span_resolver.py`;
- immutable `AtlasCanonicalHeadCorrespondenceReferenceSpanResult`;
- `AtlasCanonicalHeadCorrespondenceReferenceSpanResolver`;
- topology compatibility is required;
- missing observation samples are blocked;
- only correspondence-owned samples affect the reference spans.

Real six-view amplitude path verified:
- six real DSINE normal fields;
- 478 real residual-detail samples per view;
- 105 verified MediaPipe samples required by the FLAME embedding;
- FLAME face+barycentric canonical-surface correspondence;
- per-view correspondence-derived scale normalization;
- canonical surface-to-vertex amplitude resolution;
- canonical scalar detail and confidence remain separate;
- outputs are finite;
- unmapped canonical vertices remain exactly zero;
- connectivity signature is preserved.

Real FLAME support audit:
- 105 referenced FLAME faces contain 265 distinct face-member vertices;
- normalized strictly-positive barycentric support covers 264 vertices;
- vertex `1224` is excluded because sample `387`, face `276`, has raw weight
  `-1.3322676295501878e-15`;
- this previously verified floating-point boundary noise is correctly clamped
  to `0.0`;
- real resolver result therefore uses `mapped_vertex_count = 264`.

Tests:
- `Test/test_canonical_head_correspondence_reference_span_resolver.py`;
- extended:
  `Test/test_phase8_10_real_flame_surface_correspondence.py`.

Validation:
- focused reference-span resolver: `4 passed in 0.05s`;
- real six-view normalized amplitude integration:
  `4 passed, 5 warnings in 5.64s`;
- related regression:
  `82 passed, 5 warnings in 5.79s`;
- broad canonical-head regression:
  `609 passed, 5 warnings in 6.64s`;
- full ATLAS regression:
  `4886 passed, 5 warnings in 126.14s`;
- scoped `git diff --check`: clean.

Warning note:
- warnings are NumPy deprecation warnings while loading the historical FLAME
  pickle through `numpy.core.numeric`;
- they do not alter the verified amplitude behavior and are not a Phase 8.10
  blocker.

Original Phase 8.10 checklist status:
1. run six real DSINE normal fields through field source — DONE;
2. preserve explicit confidence separately — DONE;
3. scalar-detail + confidence through image sampler — DONE;
4. create real residual-detail observations — DONE;
5. connect observations through correspondence — DONE;
6. run canonical amplitude resolver — DONE;
7. apply bounded amplitude policy — NEXT;
8. run view-to-canonical bridge — PENDING;
9. record quantitative real hybrid-detail evidence — PENDING;
10. close remaining benchmark evidence gaps — PENDING;
11. perform architecture-class comparison — PENDING;
12. issue final Phase 8 GO / HOLD / REJECT — PENDING;
13. only explicit GO may authorize Phase 9 — PENDING.

Architecture boundary:
- bounded physical amplitude policy is not applied yet;
- canonical normal displacement is not applied yet;
- final geometry is not composed;
- no hybrid GO / HOLD / REJECT decision is issued;
- Phase 9 remains NOT AUTHORIZED.

Exact next Phase 8.10 task:
- checklist item 7;
- apply the existing bounded amplitude policy to the six real canonical
  scalar-detail/confidence results;
- preserve confidence-separation semantics;
- quantify clipping/bounding behavior before checklist item 8.

Phase 8.10 remains `ACTIVE`.
Phase 9 remains `NOT AUTHORIZED`.

## Phase 8.10 — Checklist Item 7 Real Bounded Amplitude Policy — VERIFIED

The original Phase 8.10 `Exact next Phase 8.10 work` checklist item 7,
`apply the bounded amplitude policy`, is now verified against the six real
DSINE benchmark views after canonical surface correspondence, reference-span
normalization and surface-to-vertex amplitude resolution.

Real limit-selection evidence:
- no fixture amplitude such as `0.15` or `1.0` is reused as a real benchmark
  limit;
- no undocumented physical-millimeter interpretation is introduced;
- the real six-view weighted-amplitude distribution was measured before
  selecting the bound;
- aggregate active weighted-amplitude count: `1268`;
- aggregate absolute maximum:
  `0.0034050619741867834`;
- aggregate percentiles:
  - P50 `4.487979690317351e-05`;
  - P90 `0.0003373176398647061`;
  - P95 `0.0005265063861895659`;
  - P99 `0.0009101237261288755`;
  - P99.5 `0.001220223767185876`.

Sensitivity audit:
- `0.5%` canonical reference span:
  `20 / 1268` clipped, `1.5773%`;
- `1.0%` canonical reference span:
  `1 / 1268` clipped, `0.0789%`;
- `1.5%` canonical reference span:
  `1 / 1268` clipped, `0.0789%`;
- `2.0%` canonical reference span:
  `1 / 1268` clipped, `0.0789%`.

Selected Phase 8.10 hybrid bounded-detail rule:
- `maximum_absolute_amplitude =
  canonical_reference_span * 0.01`;
- the `1.0%` rule is the lowest tested non-aggressive bound that preserves all
  but the single measured extreme tail vertex;
- increasing the tested limit to `1.5%` or `2.0%` preserves no additional
  active vertex;
- the rule remains canonical model-space relative and is not claimed as a
  physical-millimeter production limit.

Real six-view policy result:
- `subject_01_front`: `0` clipped;
- `subject_01_side_a`: `0` clipped;
- `subject_01_side_b`: `0` clipped;
- `subject_02_front`: `0` clipped;
- `subject_02_side_a`: `1` clipped;
- `subject_02_side_b`: `0` clipped;
- aggregate active weighted amplitudes: `1268`;
- aggregate clipped amplitudes: `1`;
- aggregate clipping ratio:
  `0.07886435331230283%`.

Policy semantics preserved:
- confidence weighting occurs only in
  `AtlasCanonicalHeadResidualDetailAmplitudePolicy`;
- weighted amplitude equals raw canonical scalar detail multiplied by canonical
  confidence;
- zero confidence removes residual-detail contribution;
- symmetric bounding is applied after confidence weighting;
- bounded amplitudes do not exceed the selected maximum;
- upstream canonical amplitude results are not mutated;
- mapped vertex count is preserved;
- connectivity signature is preserved.

Real integration coverage:
- extended
  `Test/test_phase8_10_real_flame_surface_correspondence.py`;
- real chain:
  DSINE normal evidence
  -> residual-detail observation
  -> 105 FLAME barycentric surface correspondences
  -> correspondence-derived reference spans
  -> canonical scale normalization
  -> surface-to-vertex amplitude resolution
  -> confidence weighting
  -> bounded amplitude policy.

Validation:
- real six-view bounded-policy integration:
  `5 passed, 7 warnings in 8.42s`;
- related residual-detail/policy regression:
  `53 passed, 7 warnings in 8.52s`;
- broad canonical-head regression:
  `610 passed, 7 warnings in 9.42s`;
- full ATLAS regression:
  `4887 passed, 7 warnings in 128.98s`;
- scoped `git diff --check`:
  clean.

Warning note:
- warnings are NumPy deprecation warnings emitted while loading the historical
  FLAME pickle through `numpy.core.numeric`;
- they do not alter the verified bounded-amplitude behavior and are not a
  Phase 8.10 blocker.

Original Phase 8.10 checklist status:
1. run six real DSINE normal fields through field source — DONE;
2. preserve explicit confidence separately — DONE;
3. scalar-detail + confidence through image sampler — DONE;
4. create real residual-detail observations — DONE;
5. connect observations through correspondence — DONE;
6. run canonical amplitude resolver — DONE;
7. apply bounded amplitude policy — DONE;
8. run view-to-canonical bridge — NEXT;
9. record quantitative real hybrid-detail evidence — PENDING;
10. close remaining benchmark evidence gaps — PENDING;
11. perform architecture-class comparison — PENDING;
12. issue final Phase 8 GO / HOLD / REJECT — PENDING;
13. only explicit GO may authorize Phase 9 — PENDING.

Architecture boundary:
- this milestone selects a Phase 8.10 benchmark-relative bounded-detail rule;
- it does not define a final physical-millimeter production displacement limit;
- canonical normal projection is not yet run in this checklist milestone;
- final geometry is not composed;
- no hybrid GO / HOLD / REJECT decision is issued;
- Phase 9 remains NOT AUTHORIZED.

Exact next Phase 8.10 task:
- checklist item 8;
- run the existing view-to-canonical residual-detail bridge against the six
  real normalized/corresponded observations using the verified `1.0%`
  canonical-reference-span amplitude bound;
- preserve visibility/projection boundaries;
- then record the quantitative real hybrid-detail evidence required by
  checklist item 9.

Phase 8.10 remains `ACTIVE`.
Phase 9 remains `NOT AUTHORIZED`.

## Phase 8.10 — Checklist Item 8 Real Surface View-to-Canonical Bridge — VERIFIED

The original Phase 8.10 `Exact next Phase 8.10 work` checklist item 8,
`run the view-to-canonical bridge`, is now verified for the real FLAME
barycentric surface-correspondence path.

Architecture decision:
- the existing `AtlasCanonicalHeadViewResidualDetailBridge` remains unchanged;
- that bridge intentionally accepts
  `AtlasCanonicalHeadDenseCorrespondence`;
- the real Phase 8.10 FLAME embedding is face+barycentric surface
  correspondence and is not reinterpreted as direct canonical-vertex mapping;
- a parallel provider-independent surface-aware orchestration boundary was
  therefore added.

Implementation:
- added
  `CORE/atlas_canonical_head_surface_view_residual_detail_bridge.py`;
- added
  `AtlasCanonicalHeadSurfaceViewResidualDetailBridge`;
- the bridge consumes:
  - `AtlasCanonicalHeadResidualDetailObservation`;
  - `AtlasCanonicalHeadSurfaceCorrespondence`;
  - explicit `maximum_absolute_amplitude`;
- it reuses:
  - `AtlasCanonicalHeadSurfaceResidualDetailAmplitudeResolver`;
  - `AtlasCanonicalHeadResidualDetailAmplitudePolicy`;
  - existing `AtlasCanonicalHeadViewResidualDetailBridgeResult`.

Behavior:
- surface/barycentric mapping is resolved to canonical scalar detail and
  canonical confidence;
- confidence weighting remains owned by the amplitude-policy layer;
- symmetric bounded amplitude remains owned by the amplitude-policy layer;
- observation identity and source-view identity are preserved;
- mapped vertex count and connectivity signature are preserved;
- no dense-vertex correspondence is fabricated;
- upstream observations and correspondence contracts are not mutated.

Real six-view verification:
- six real normalized DSINE residual-detail observations were passed through
  the new surface-aware bridge;
- the verified Phase 8.10 bound remains
  `1.0%` of canonical correspondence reference span;
- for every view, bridge outputs match the already verified direct
  surface-amplitude-resolver plus bounded-policy chain;
- canonical scalar detail matches;
- canonical confidence matches;
- weighted amplitude matches;
- bounded amplitude matches;
- all six real runs preserve `mapped_vertex_count = 264`;
- bounded amplitudes remain inside the explicit per-view maximum;
- FLAME connectivity signature is preserved.

Tests:
- `Test/test_canonical_head_surface_view_residual_detail_bridge.py`;
- extended real integration coverage in
  `Test/test_phase8_10_real_flame_surface_correspondence.py`.

Validation:
- focused surface-aware bridge:
  `4 passed in 0.05s`;
- focused + real six-view bridge integration:
  `10 passed, 9 warnings in 11.21s`;
- related bridge/residual-detail regression:
  `57 passed, 9 warnings in 11.34s`;
- broad canonical-head regression:
  `615 passed, 9 warnings in 12.21s`;
- full ATLAS regression:
  `4892 passed, 9 warnings in 132.88s`;
- scoped `git diff --check`:
  clean.

Warning note:
- warnings are NumPy deprecation warnings emitted while loading the historical
  FLAME pickle through `numpy.core.numeric`;
- they do not alter the verified bridge behavior and are not a Phase 8.10
  blocker.

Original Phase 8.10 checklist status:
1. run six real DSINE normal fields through field source — DONE;
2. preserve explicit confidence separately — DONE;
3. scalar-detail + confidence through image sampler — DONE;
4. create real residual-detail observations — DONE;
5. connect observations through correspondence — DONE;
6. run canonical amplitude resolver — DONE;
7. apply bounded amplitude policy — DONE;
8. run view-to-canonical bridge — DONE;
9. record quantitative real hybrid-detail evidence — NEXT;
10. close remaining benchmark evidence gaps — PENDING;
11. perform architecture-class comparison — PENDING;
12. issue final Phase 8 GO / HOLD / REJECT — PENDING;
13. only explicit GO may authorize Phase 9 — PENDING.

Architecture boundary:
- the bridge does not claim camera, pose, visibility or occlusion resolution;
- it does not select normal direction;
- it does not create canonical displacement geometry;
- it does not compose final identity geometry;
- no hybrid GO / HOLD / REJECT decision is issued;
- Phase 9 remains NOT AUTHORIZED.

Exact next Phase 8.10 task:
- checklist item 9;
- record quantitative real hybrid-detail evidence from the verified six-view
  surface-aware bridge outputs;
- preserve raw, weighted and bounded amplitude statistics separately;
- only after that evidence is audited proceed to remaining benchmark gaps.

Phase 8.10 remains `ACTIVE`.
Phase 9 remains `NOT AUTHORIZED`.

## Phase 8.10 — Checklist Item 9 Quantitative Real Hybrid-Detail Evidence — VERIFIED

The original Phase 8.10 checklist item 9,
`record quantitative real hybrid-detail evidence`, is now verified.

New raw evidence contracts:
- `CORE/atlas_canonical_head_hybrid_detail_measurement_observation.py`;
- `AtlasCanonicalHeadHybridDetailMeasurementObservation`;
- `CORE/atlas_canonical_head_hybrid_detail_benchmark_evidence.py`;
- `AtlasCanonicalHeadHybridDetailBenchmarkEvidence`.

Evidence boundary:
- records raw quantitative hybrid-detail measurements only;
- does not convert measurements into benchmark support scores;
- does not create `AtlasCanonicalHeadBenchmarkCandidateObservation`;
- does not perform architecture comparison;
- does not issue GO / HOLD / REJECT;
- does not authorize Phase 9.

Real six-view quantitative evidence:
- architecture kind: `hybrid_canonical_detail`;
- view count: `6`;
- mapped vertex count per view: `264`;
- aggregate active vertex count: `1268`;
- aggregate clipped vertex count: `1`;
- aggregate clipped fraction:
  `0.0007886435331230284`
  (`0.07886435331230284%`);
- connectivity signature count: `1`;
- canonical reference span:
  `0.16373484421605985`;
- selected maximum absolute amplitude:
  `0.0016373484421605986`
  (`1.0%` of canonical reference span).

Per-view active / clipped counts:
- `subject_01_front`: `264 / 0`;
- `subject_01_side_a`: `135 / 0`;
- `subject_01_side_b`: `167 / 0`;
- `subject_02_front`: `264 / 0`;
- `subject_02_side_a`: `227 / 1`;
- `subject_02_side_b`: `211 / 0`.

The only clipped real measurement:
- `subject_02_side_a`;
- weighted absolute max:
  `0.0034050619741867834`;
- bounded absolute max:
  `0.0016373484421605986`.

Reproducibility:
- the evidence catalog is cross-checked against a recomputed real six-view
  chain:
  DSINE residual detail
  -> reference-span normalization
  -> FLAME barycentric surface correspondence
  -> surface-aware view-to-canonical bridge
  -> confidence weighting
  -> bounded amplitude policy;
- catalog values reproduce image span, canonical span, scale factor,
  mapped/active/clipped counts, raw max, weighted max, bounded max,
  weighted P95/P99 and connectivity signature.

Validation:
- measurement contract:
  `43 passed in 0.04s`;
- evidence catalog focused validation:
  `10 passed in 0.03s`;
- real catalog cross-check:
  `54 passed, 2 warnings in 2.90s`;
- related regression:
  `102 passed, 11 warnings in 14.11s`;
- broad canonical-head regression:
  `669 passed, 11 warnings in 15.03s`;
- full ATLAS regression:
  `4946 passed, 11 warnings in 134.93s`;
- scoped `git diff --check`:
  clean.

Original Phase 8.10 checklist status:
1. run six real DSINE normal fields through field source — DONE;
2. preserve explicit confidence separately — DONE;
3. scalar-detail + confidence through image sampler — DONE;
4. create real residual-detail observations — DONE;
5. connect observations through correspondence — DONE;
6. run canonical amplitude resolver — DONE;
7. apply bounded amplitude policy — DONE;
8. run view-to-canonical bridge — DONE;
9. record quantitative real hybrid-detail evidence — DONE;
10. close remaining benchmark evidence gaps — NEXT;
11. perform architecture-class comparison — PENDING;
12. issue final Phase 8 GO / HOLD / REJECT — PENDING;
13. only explicit GO may authorize Phase 9 — PENDING.

Exact next work after the planned pause:
- Phase 8.10 checklist item 10;
- audit and close remaining benchmark evidence gaps;
- do not start Phase 9.

Phase 8.10 remains `ACTIVE`.
Phase 8 remains not yet LOCKED.
Phase 9 remains `NOT AUTHORIZED`.

## Phase 8.10 — Checklist Item 10 Benchmark Evidence Gap Closure — VERIFIED

The original Phase 8.10 checklist item 10,
`close remaining benchmark evidence gaps`, is now verified as an
explicit evidence-gap closure boundary.

New provider-independent gap-closure contracts:
- `CORE/atlas_canonical_head_benchmark_gap_closure_observation.py`;
- `AtlasCanonicalHeadBenchmarkGapClosureObservation`;
- `CORE/atlas_canonical_head_benchmark_gap_closure_evidence.py`;
- `AtlasCanonicalHeadBenchmarkGapClosureEvidence`.

Boundary:
- missing or partial quality channels are preserved explicitly;
- verified policy blockers are preserved separately from unresolved policy;
- no unsupported numeric benchmark support score is fabricated;
- no `AtlasCanonicalHeadBenchmarkCandidateObservation` is created from
  incomplete evidence;
- no architecture-class comparison is performed here;
- no GO / HOLD / REJECT decision is issued here;
- Phase 9 is not authorized.

FLAME 2023 Open gap closure:
- candidate: `flame-2023-open`;
- architecture: `parametric_fixed_topology`;
- commercial model license state: `ACCEPTABLE`;
- remaining policy states for privacy/data retention, model-weight
  restrictions and dataset restrictions remain `UNRESOLVED`;
- current evidence still lacks metric 3D ground truth, expression-variation
  benchmark evidence and candidate-specific physical evidence;
- existing missing / partial quality channels remain explicit rather than
  being converted into unsupported numeric scores.

PRNet gap closure:
- candidate: `prnet`;
- architecture: `direct_neural_dense`;
- commercial license state: `BLOCKED`;
- model-weight restrictions state: `BLOCKED`;
- dataset restrictions state: `BLOCKED`;
- privacy/data-retention state remains `UNRESOLVED`;
- the current pretrained-model training-data provenance is not acceptable
  for a commercial candidate;
- current geometric limitations remain explicit.

Hybrid gap closure:
- architecture: `hybrid_canonical_detail`;
- no standalone hybrid candidate id is fabricated;
- no final candidate observation is created;
- real six-view bounded-detail evidence remains architecture-level evidence;
- the current DSINE dependency carries a verified non-commercial license
  blocker;
- hybrid evidence therefore remains non-authorizing.

Validation:
- focused gap-closure tests:
  `10 passed in 0.05s`;
- related benchmark regression:
  `120 passed in 0.17s`.

Original Phase 8.10 checklist status:
1. run six real DSINE normal fields through field source — DONE;
2. preserve explicit confidence separately — DONE;
3. scalar-detail + confidence through image sampler — DONE;
4. create real residual-detail observations — DONE;
5. connect observations through correspondence — DONE;
6. run canonical amplitude resolver — DONE;
7. apply bounded amplitude policy — DONE;
8. run view-to-canonical bridge — DONE;
9. record quantitative real hybrid-detail evidence — DONE;
10. close remaining benchmark evidence gaps — DONE;
11. perform architecture-class comparison — NEXT;
12. issue final Phase 8 GO / HOLD / REJECT — PENDING;
13. only explicit GO may authorize Phase 9 — PENDING.

Phase 8.10 remains `ACTIVE`.
Phase 8 remains not yet LOCKED.
Phase 9 remains `NOT AUTHORIZED`.

## Phase 8.10 — Checklist Item 11 Architecture-Class Comparison — VERIFIED

The original Phase 8.10 checklist item 11,
`perform architecture-class comparison`, is now verified.

New comparison contract:
- `CORE/atlas_canonical_head_benchmark_architecture_comparison.py`;
- `AtlasCanonicalHeadBenchmarkArchitectureComparison`.

Comparison boundary:
- compares exactly the three required architecture classes:
  `parametric_fixed_topology`,
  `direct_neural_dense`,
  `hybrid_canonical_detail`;
- reuses verified Item 10 evidence-gap closure records;
- does not fabricate numeric support scores;
- does not fabricate a standalone hybrid candidate id;
- does not create final candidate observations from incomplete evidence;
- does not select a winner while evidence remains incomplete;
- does not issue the final Phase 8 decision;
- does not authorize Phase 9.

Current comparison result:
- FLAME 2023 Open is represented at candidate level as
  `flame-2023-open / parametric_fixed_topology`;
- its commercial model-license state is `ACCEPTABLE`, while unresolved
  quality and policy evidence remains explicit;
- PRNet is represented at candidate level as
  `prnet / direct_neural_dense`;
- its verified commercial-license, model-weight and dataset policy blockers
  remain explicit;
- Hybrid remains architecture-level evidence only;
- no hybrid candidate id is fabricated;
- the current DSINE dependency retains its verified non-commercial
  policy blocker;
- `selected_architecture_kind()` therefore returns `None`;
- `comparison_complete_for_final_scoring()` is `False`.

Validation:
- focused architecture-comparison tests:
  `4 passed in 0.03s`;
- related benchmark regression:
  `108 passed in 0.16s`.

Original Phase 8.10 checklist status:
1. run six real DSINE normal fields through field source — DONE;
2. preserve explicit confidence separately — DONE;
3. scalar-detail + confidence through image sampler — DONE;
4. create real residual-detail observations — DONE;
5. connect observations through correspondence — DONE;
6. run canonical amplitude resolver — DONE;
7. apply bounded amplitude policy — DONE;
8. run view-to-canonical bridge — DONE;
9. record quantitative real hybrid-detail evidence — DONE;
10. close remaining benchmark evidence gaps — DONE;
11. perform architecture-class comparison — DONE;
12. issue final Phase 8 GO / HOLD / REJECT — NEXT;
13. only explicit GO may authorize Phase 9 — PENDING.

Phase 8.10 remains `ACTIVE`.
Phase 8 remains not yet LOCKED.
Phase 9 remains `NOT AUTHORIZED`.

## Phase 8.10 — Checklist Item 12 Final Phase 8 Decision — HOLD

The original Phase 8.10 checklist item 12,
`issue final Phase 8 GO / HOLD / REJECT`, is now evaluated.

Final current decision:
- decision: `HOLD`;
- status: `BLOCKED`;
- selected candidate: none;
- selected architecture: none;
- Phase 9 authorized: `False`.

Decision basis:
- final scoring evidence remains incomplete;
- FLAME 2023 Open still has unresolved quality / policy evidence;
- PRNet remains policy-blocked;
- Hybrid remains architecture-level evidence only;
- the current DSINE dependency remains non-commercial and therefore
  policy-blocked for the commercial candidate path;
- no unsupported candidate score was fabricated;
- no GO candidate exists from the currently verified evidence.

New final-decision boundary:
- `CORE/atlas_canonical_head_phase8_final_decision.py`;
- `AtlasCanonicalHeadPhase8FinalDecision`.

Verified blocked reasons:
- `INCOMPLETE_FINAL_SCORING_EVIDENCE`;
- `PRNET_POLICY_BLOCKED`;
- `HYBRID_DSINE_LICENSE_BLOCKED`.

Validation:
- focused final-decision tests:
  `3 passed in 0.03s`;
- related benchmark regression:
  `83 passed in 0.15s`.

Original Phase 8.10 checklist status:
1. run six real DSINE normal fields through field source — DONE;
2. preserve explicit confidence separately — DONE;
3. scalar-detail + confidence through image sampler — DONE;
4. create real residual-detail observations — DONE;
5. connect observations through correspondence — DONE;
6. run canonical amplitude resolver — DONE;
7. apply bounded amplitude policy — DONE;
8. run view-to-canonical bridge — DONE;
9. record quantitative real hybrid-detail evidence — DONE;
10. close remaining benchmark evidence gaps — DONE;
11. perform architecture-class comparison — DONE;
12. issue final Phase 8 GO / HOLD / REJECT — HOLD;
13. only explicit GO may authorize Phase 9 — NOT SATISFIED.

Phase 8.10 remains `ACTIVE`.
Phase 8 remains not yet LOCKED.
Phase 9 remains `NOT AUTHORIZED`.

## Phase 8.10 — Post-HOLD FLAME Policy Evidence Update

Post-HOLD blocker reduction work verified two additional FLAME policy
channels without changing the Phase 8 HOLD decision.

Current FLAME policy states:
- commercial license: `ACCEPTABLE`;
- privacy / data retention: `ACCEPTABLE`;
- model-weight restrictions: `ACCEPTABLE`;
- dataset restrictions: `UNRESOLVED`.

Privacy / data-retention evidence:
- the active FLAME benchmark/fitting path was audited for network, upload,
  cloud, telemetry, remote-service and subprocess behavior;
- no such runtime path was found;
- the verified benchmark path reads local model, embedding, landmark and
  residual-detail evidence files only;
- this acceptance applies to the local ATLAS runtime path and does not make
  broader claims about external FLAME web services.

Model-weight evidence:
- the FLAME 2023 Open model remains the verified model candidate;
- its model-license path permits commercial use subject to the applicable
  attribution requirements;
- the model-weight restriction state is therefore `ACCEPTABLE`.

Remaining dataset/provenance gap:
- `mediapipe_landmark_embedding.npz` remains an active benchmark dependency;
- local metadata and git history do not establish its source provenance;
- it is not a direct copy of `flame_static_embedding.pkl`;
- therefore dataset/provenance restrictions remain `UNRESOLVED`;
- no provenance or policy state is fabricated.

Validation:
- FLAME policy focused tests:
  `5 passed in 0.03s`;
- related gap/comparison/final-decision regression:
  `19 passed in 0.08s`.

Phase 8 final decision remains `HOLD / BLOCKED`.
Phase 9 remains `NOT AUTHORIZED`.

## Phase 8.10 — Post-HOLD FLAME Quality Blocker Audit

Post-HOLD audit verified the remaining FLAME quality-evidence boundary
without fabricating support values and without adding a new blocker contract.

Existing blocker representation is sufficient:
- `AtlasCanonicalHeadBenchmarkGapClosureObservation.unresolved_quality_channels`
  already derives every `PARTIAL` / `MISSING` quality channel;
- `blocked_policy_channels` and `unresolved_policy_channels` separately
  preserve policy blockers;
- no additional CORE blocker field or contract is required.

Verified remaining FLAME quality boundaries:
- identity preservation: `PARTIAL`;
- multi-view consistency: `MEASURED`;
- silhouette / profile: `MISSING`;
- head ratio: `MISSING`;
- jaw / chin: `MISSING`;
- nose projection: `MISSING`;
- orbital / cheek volume: `MISSING`;
- expression separation: `MISSING`;
- pose separation: `PARTIAL`;
- topology suitability: `DIRECT`;
- physical suitability: `MISSING`;
- Apple Silicon / runtime: `DIRECT`;
- reproducibility: `DIRECT`.

Audit conclusions:
- silhouette/profile cannot be promoted from current evidence: the historical
  FLAME fitting/projection/visible-boundary implementation exists in git
  history, but no committed six-view fitted-mesh/camera artifact or benchmark
  runner remains; the historical visibility stage was front-facing winding
  only and did not provide occlusion-aware ground-truth silhouette evidence;
- head-ratio evidence has no independent calibrated benchmark measurement in
  the active Phase 8.10 evidence path; a simple landmark width/height ratio is
  not treated as sufficient evidence;
- jaw/chin, nose projection and orbital/cheek volume remain blocked by the
  absence of appropriate metric 3D ground truth;
- expression separation remains missing because all six held-out FLAME
  observations use `expression_fixed_neutral=True`; there is no expression-
  variation benchmark;
- pose separation remains intentionally `PARTIAL`: held-out identity is locked
  and only root pose plus weak-perspective camera are solved, but this is not
  promoted beyond the verified evidence boundary;
- physical suitability remains missing because no candidate-specific physical
  representation observation exists; the Phase 8.9 gate requires calibrated
  identity, silhouette and profile preservation supports rather than
  printability alone;
- `mediapipe_landmark_embedding.npz` provenance remains unresolved, so FLAME
  dataset restrictions remain `UNRESOLVED`.

No CORE change is justified by this audit.
Phase 8 final decision remains `HOLD / BLOCKED`.
Phase 9 remains `NOT AUTHORIZED`.
## Phase 8.10 — Post-HOLD Metric 3D Ground-Truth Evaluation Boundary

Post-HOLD blocker reduction opened the provider-independent metric 3D
ground-truth evaluation boundary required by the remaining FLAME quality gaps.

New contract:
- `AtlasCanonicalHeadMetricGroundTruthObservation`;
- carries metric ground-truth mesh and reconstruction mesh separately;
- requires physical units to be `mm`;
- rejects non-finite vertex data and invalid triangle indices;
- keeps benchmark source identity explicit through `source_id`;
- distinguishes benchmark-only evaluation use from production dependency use
  through `evaluation_use_only`;
- records benchmark-source provenance separately through
  `source_provenance_state = VERIFIED | UNRESOLVED`;
- records benchmark evaluation-license state separately through
  `evaluation_license_state = ACCEPTABLE | BLOCKED | UNRESOLVED`.

Important boundary:
- benchmark/evaluation dataset provenance and license state are not treated as
  the candidate model's production/commercial dependency policy;
- no external metric 3D dataset has yet been accepted or integrated;
- no scan-to-mesh, alignment, regional error or support-score calculation is
  claimed by this milestone;
- no `[0,1]` benchmark support values are fabricated.

Validation:
- focused metric-GT observation tests:
  `8 passed in 0.04s`;
- related benchmark/evidence regression:
  `62 passed in 0.13s`.

Phase 8 final decision remains `HOLD / BLOCKED`.
Phase 8.10 remains `ACTIVE`.
Phase 9 remains `NOT AUTHORIZED`.

## Phase 8.10 — Post-HOLD Metric Mesh Unit Normalization Boundary

A provider-independent metric mesh unit-normalization boundary was added for
metric 3D ground-truth evaluation.

New contract:
- `AtlasCanonicalHeadMetricMeshUnitNormalizer`;
- accepts only explicit metric source units: `mm`, `cm`, `m`;
- normalizes vertices into millimetres;
- exposes the applied `scale_factor`;
- preserves the source vertex array without mutation;
- rejects unsupported units and non-finite geometry.

Important boundary:
- the normalizer never infers source units from geometry dimensions;
- HSRD-100 `HSR0015-Body-035` has been inspected as a candidate metric-GT
  spike sample, but its OBJ file contains no explicit unit declaration;
- therefore HSRD source units are not yet promoted to verified evidence;
- no silent `x1000` conversion is authorized;
- no scan-to-mesh or support-score evidence is claimed by this milestone.

Validation:
- focused metric mesh unit-normalizer tests:
  `7 passed in 0.05s`;
- related metric-GT/evidence regression:
  `69 passed in 0.14s`.

Phase 8 final decision remains `HOLD / BLOCKED`.
Phase 8.10 remains `ACTIVE`.
Phase 9 remains `NOT AUTHORIZED`.

## Phase 8.10 — Post-HOLD Metric Rigid Alignment Boundary

A provider-independent rigid 3D alignment boundary was added for the
metric ground-truth evaluator.

New contract:
- `AtlasCanonicalHeadMetricRigidAlignment`;
- solves rotation and translation from matched 3D point correspondences;
- requires at least three correspondences;
- preserves scale exactly at `1.0`;
- rejects mismatched or non-finite point sets;
- corrects improper reflection solutions;
- does not mutate source or target point arrays.

Important boundary:
- this milestone does not estimate scale;
- it does not perform ICP or nearest-surface correspondence;
- it has not yet been applied to the HSRD-100 spike sample;
- no scan-to-mesh distance or benchmark support score is claimed.

Validation:
- focused rigid-alignment tests:
  `4 passed in 0.05s`;
- related metric/evidence regression:
  `73 passed in 0.16s`.

Phase 8 final decision remains `HOLD / BLOCKED`.
Phase 8.10 remains `ACTIVE`.
Phase 9 remains `NOT AUTHORIZED`.

## Phase 8.10 — Post-HOLD Point-to-Surface Metric Boundary

A provider-independent exact point-to-triangle surface-distance boundary was
added for the metric 3D ground-truth evaluator.

New contract:
- `AtlasCanonicalHeadMetricPointToSurfaceDistance`;
- measures source-point distance to target triangle surfaces;
- handles triangle interiors, edges and vertices;
- returns per-point distances in millimetres;
- reports global mean and maximum raw geometric error;
- rejects non-finite source geometry and invalid target triangle indices.

Important boundary:
- this milestone is a raw geometric measurement layer only;
- it does not perform rigid alignment internally;
- it does not perform ICP or semantic correspondence;
- it has not yet been applied to the real HSRD-100 spike sample;
- no regional jaw/chin, nose or orbital/cheek metric is claimed yet;
- no `[0,1]` benchmark support score is claimed;
- the current exact implementation prioritizes correctness; real-mesh
  performance/scalability remains a separate validation boundary.

Validation:
- focused point-to-surface tests:
  `4 passed in 0.05s`;
- related metric/evidence regression:
  `77 passed in 0.18s`.

Phase 8 final decision remains `HOLD / BLOCKED`.
Phase 8.10 remains `ACTIVE`.
Phase 9 remains `NOT AUTHORIZED`.

## Phase 8.10 — Post-HOLD Global Raw Distance Metric Boundary

A provider-independent raw metric aggregation boundary was added on top of
point-to-surface distance evidence.

New contract:
- `AtlasCanonicalHeadMetricDistanceAggregate`;
- consumes nonnegative per-point distances in millimetres;
- reports sample count;
- reports mean distance;
- reports median distance;
- reports RMSE distance;
- reports p95 distance;
- reports maximum distance;
- rejects empty, non-finite, negative or non-1D distance arrays;
- does not mutate the source distance array.

Important boundary:
- this milestone aggregates raw geometric evidence only;
- it does not perform alignment or surface correspondence itself;
- it does not create semantic regional metrics yet;
- it has not yet been applied to the real HSRD-100 spike sample;
- it does not convert raw metric values into `[0,1]` benchmark support.

Validation:
- focused raw-distance aggregate tests:
  `7 passed in 0.05s`;
- related metric/evidence regression:
  `84 passed in 0.21s`.

Phase 8 final decision remains `HOLD / BLOCKED`.
Phase 8.10 remains `ACTIVE`.
Phase 9 remains `NOT AUTHORIZED`.

## Phase 8.10 — Post-HOLD Region-Wise Raw Distance Metric Boundary

A semantic region-wise raw metric aggregation boundary was added on top of
the global point-to-surface distance metric.

New contract:
- `AtlasCanonicalHeadMetricRegionDistanceAggregate`;
- consumes global per-sample distances in millimetres;
- consumes explicit semantic region -> sample-index mappings;
- normalizes semantic region names;
- computes an independent `AtlasCanonicalHeadMetricDistanceAggregate`
  for each named region;
- rejects empty region maps, empty sample sets, non-integer indices and
  out-of-bounds indices;
- keeps region aggregates immutable through a read-only mapping.

Important boundary:
- semantic region membership must be supplied explicitly;
- the contract does not infer facial regions from geometry;
- it does not create correspondence or alignment;
- it does not yet apply the metric to real HSRD-100 geometry;
- it does not convert regional raw errors into `[0,1]` benchmark support.

Validation:
- focused region-wise metric tests:
  `5 passed in 0.05s`;
- related metric/evidence regression:
  `89 passed in 0.22s`.

Phase 8 final decision remains `HOLD / BLOCKED`.
Phase 8.10 remains `ACTIVE`.
Phase 9 remains `NOT AUTHORIZED`.

## Phase 8.10 — Post-HOLD FLAME Evaluation-Only Embedding Policy Boundary

The FLAME candidate policy boundary was corrected so that the
`mediapipe_landmark_embedding.npz` benchmark artifact is not treated as a
production/runtime dataset dependency.

Verified boundary:
- the embedding remains a Phase 8.10 benchmark/evaluation artifact;
- its exact source-license provenance remains unresolved;
- that unresolved provenance is preserved explicitly as
  `BENCHMARK_MEDIAPIPE_EMBEDDING_PROVENANCE_UNRESOLVED`;
- it is not promoted into a production dependency;
- therefore FLAME candidate `dataset_restrictions_state` is now `ACCEPTABLE`;
- `dataset_restrictions_state` is no longer present in FLAME
  `unresolved_policy_channels`;
- the general candidate policy gate was not weakened or changed;
- PRNet and Hybrid policy states were not changed.

This supersedes the earlier interpretation that unresolved provenance of the
evaluation-only MediaPipe-to-FLAME embedding must itself keep the FLAME
candidate production dataset-policy state `UNRESOLVED`.

Validation:
- focused FLAME gap-closure evidence: `6 passed in 0.03s`;
- related Phase 8.10 policy/gap regression: `83 passed in 0.13s`;
- scoped `git diff --check`: clean;
- full regression: `5001 passed, 11 warnings in 133.82s`.

Important decision boundary:
- this removes one FLAME policy blocker only;
- it does not fabricate missing quality support values;
- remaining quality evidence gaps still prevent a candidate-level GO;
- Phase 8 final decision therefore remains `HOLD / BLOCKED`;
- Phase 8.10 remains `ACTIVE`;
- Phase 9 remains `NOT AUTHORIZED`.

## Phase 8.10 — 25 Aug 2026 HSRD Metric-GT HOLD Closure

The real HSRD-100 A03 metric ground-truth investigation was completed through
the full 3/4 investigation branch and 4/4 HOLD-closure decision audit.

Final scientific disposition:
- A03 metric-GT branch:
  `CLOSED_AS_INADMISSIBLE_ALIGNMENT`;
- Step 3/4:
  `COMPLETE_WITH_NEGATIVE_EVIDENCE`;
- camera path:
  `UNRESOLVED_GLOBAL_CONVENTION`;
- metric admissibility firewall:
  `INADMISSIBLE_ALIGNMENT`;
- A03 evidence class:
  `DIAGNOSTIC_NEGATIVE_EVIDENCE`;
- A03 metric-GT claim:
  `NOT_ADMISSIBLE`;
- no strict-face millimetre error value was computed or claimed.

Verified positive boundaries:
- native metric units were explicitly normalized to millimetres;
- the real HSRD GT scan and FLAME reconstruction were both available;
- the official FLAME semantic `strict_face` evaluation support was fixed;
- registration and evaluation supports were kept disjoint;
- scale remained fixed at exactly `1.0`;
- similarity alignment remained forbidden;
- nonrigid alignment remained forbidden;
- independent registration-stability methods agreed that the current rigid
  transform was not admissible.

Verified negative evidence:
- no single globally validated HSRD camera convention was established;
- region-balanced leave-one-region-out rigid registration was unstable:
  maximum rotation delta `75.187773 deg`,
  maximum translation delta `79.058976 mm`;
- ICP-free closed-form translation anchors were also unstable:
  pairwise median disagreement `48.761583 mm`,
  pairwise maximum disagreement `125.909685 mm`;
- therefore a unique, defensible scale-fixed rigid transform was not
  established;
- strict-face metric execution remained unauthorized.

Important interpretation:
- this HOLD does not prove that FLAME geometry is poor;
- it proves that the current A03 evidence cannot support a defensible
  FLAME-vs-GT strict-face millimetre error claim;
- the metric firewall correctly prevented a false precision claim.

Final decision:
- Phase 8 final decision: `HOLD / BLOCKED`;
- current HSRD HOLD evidence branch:
  `EVIDENCE_COMPLETE_FOR_CURRENT_HOLD_BRANCH`;
- Phase 9: `NOT AUTHORIZED / NOT STARTED`;
- a new independently admissible metric-GT evidence route is required before
  the Phase 8 GO gate can be reconsidered.

Persistent evidence:
- directory:
  `/Users/Kubi/ATLAS_HSRD_SPIKE/EVIDENCE/phase8_10_hsrd_hold_2026-08-25/`;
- verified evidence files: `110`;
- manifest:
  `SHA256SUMS.txt`;
- manifest SHA256:
  `fd652d4392fccbcc5f9c0b8cb84393f8ce8b43462aaddb8b443846ec2dfa2f51`;
- A03 final disposition SHA256:
  `b6924f00b8a9040cde3599a86ea3845ffae0908922b2704362151bc745e07d86`;
- Phase 8 HOLD closure SHA256:
  `57974f47c79ee79c8a625ab57d01ab326730f677b95f927893e6b2c6b79fc56a`.

Repository boundary at closure:
- safe pushed checkpoint before this documentation update:
  `c9c40fa5b40829001733f44d8f7dde9254ccca7d`;
- unrelated dirty working-tree files were not modified, staged or cleaned by
  the HSRD HOLD investigation.

## Phase 8.10 — 26 Aug 2026 Personal Multiview Silhouette / Recovery Update

This section records the previously unpersisted personal-multiview FLAME
silhouette/profile investigation and the Step61AF recovery boundary.

Phase state remains unchanged:

- Phase 8 / Phase 8.10: `ACTIVE`;
- Phase 8 final decision: `HOLD / BLOCKED`;
- Phase 9: `NOT AUTHORIZED / NOT STARTED`;
- none of the results below constitute a Phase 8 GO decision.

### 1. Corrected image-coordinate contract

The personal-multiview audit established that target normalized coordinates
must be converted to pixels with `[W-1, H-1]`.

The earlier `[W,H]` target scaling introduced an approximately `0.866 px`
systematic mean delta across the 63 jaw observations.

### 2. Static105 / silhouette correspondence boundary

The 105 static MediaPipe-to-FLAME barycentric correspondences do not contain
the 21 lower-jaw MediaPipe IDs used by the silhouette experiment.

The static105 set also has zero overlap with the complete 36-point MediaPipe
face oval.

Therefore static105 does not directly constrain the jaw / visible silhouette
contour.

### 3. Corrected cross-side transferred-target evidence

With the corrected pixel contract and transferred target-curve
parameterization:

- `turn_right` visible pointwise error:
  `14.8749502083 px -> 5.74889830225 px`,
  approximately `61.35%` reduction;
- `turn_left` visible pointwise error:
  `21.1256531544 px -> 8.10962204034 px`,
  approximately `61.61%` reduction.

This is silhouette/profile evidence only and is not identity proof.

### 4. Normalized silhouette scale

Diagonal-normalized transferred-target mean error:

- `turn_right`: approximately `0.0029964`;
- `turn_left`: approximately `0.00422684`.

Static shared-identity coordinate RMSE was approximately `0.00260971`.

### 5. Objective-energy audit

Static105 objective:

- coordinate count: `630`;
- SSE: `0.004290672838`.

Visible side-silhouette objective:

- coordinate count: `50`;
- unweighted SSE: `0.001081767111`;
- unweighted silhouette/static energy ratio: `0.25212`.

Derived silhouette residual weights:

- 2.4% -> `0.0951925299576`;
- 2.5% -> `0.0991588853725`;
- 2.6% -> `0.1031255207874`;
- 2.7% -> `0.1070915962023`;
- 2.8% -> `0.1110579516172`;
- 3.0% -> `0.1189906624470`;
- 3.5% -> `0.1388224395215`;
- 4.0% -> `0.1586542165960`;
- 5.0% -> `0.198317770745`;
- 10.0% -> `0.396635541491`.

### 6. Silhouette-weight candidate sweep

| Energy | Identity L2 | Bound hits | Front px | Right px | Left px | Right transfer | Left transfer | 3-view dynamic |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0% | 12.660953 | - | 10.081836 | 14.874950 | 21.125653 | 5.748898 | 8.109622 | 44.657495 |
| 2.4% | 13.494390 | 6 | 10.159214 | 11.853075 | 17.132544 | 4.467208 | 7.609798 | 35.305151 |
| 2.5% | 13.546543 | 6 | 10.240553 | 11.796885 | 17.028959 | 4.460669 | 7.601278 | 35.088429 |
| 2.6% | 13.598742 | 6 | 10.322652 | 11.742466 | 16.928821 | 4.454447 | 7.593379 | 34.878950 |
| 2.7% | 13.649544 | 7 | 10.403375 | 11.689790 | 16.833018 | 4.448618 | 7.586214 | 34.677250 |
| 2.8% | 13.699676 | 7 | 10.483471 | 11.638790 | 16.740851 | 4.443130 | 7.579623 | 34.482500 |
| 3.0% | 13.797590 | 8 | 10.656342 | 11.550107 | 16.574997 | 4.433134 | 7.567609 | 34.135362 |
| 3.5% | 14.024314 | 7 | 11.157368 | 11.397306 | 16.263528 | 4.414511 | 7.545906 | 33.493117 |
| 4.0% | 14.196729 | 9 | 11.332241 | 11.306038 | 16.016323 | 4.389005 | 7.507306 | 33.065063 |
| 5.0% | 14.510363 | 10 | 11.597580 | 11.173570 | 15.616450 | 4.367959 | 7.449340 | 32.355438 |
| 10.0% | 15.928964 | 12 | 12.247499 | 10.994083 | 14.718174 | 4.618289 | 7.438853 | 30.020194 |

Observed trade-off:

- side-profile and raw 3-view dynamic error improve as silhouette energy rises;
- identity L2 and front-view error degrade;
- no scalar mathematical optimum was established;
- 3.5% and above are increasingly profile-biased.

### 7. Preferred local candidate

The preferred local conservative silhouette-energy candidate is `2.5%`.

This selection is only the preferred candidate for the next
identity-preservation audit.

It is explicitly:

- not a Phase 8 GO;
- not identity-preservation proof;
- not a mathematically unique knee.

The 2.4% candidate has slightly better identity/front metrics and slightly
weaker profile correction.

### 8. Silhouette-objective architecture

The verified candidate architecture uses:

- static105 reprojection residuals;
- visible side-silhouette residuals only for `turn_right` and `turn_left`;
- identity regularization;
- front silhouette excluded from the optimization objective;
- weak-perspective camera analytically re-solved from static105 only;
- silhouette residual does not influence the camera solve;
- per-view root poses fixed from Step22;
- neutral expression;
- active identity component count `90`;
- identity bounds `±3`;
- regularization weight `1e-5`.

### 9. Step21 / Step22 state boundary

Step21 and Step22 shared identity parameter vectors were exactly equal.

Their per-view root poses differed.

A previous Step61J7/J8 audit caught an early candidate using Step21 poses.
Subsequent clean silhouette experiments used Step22 poses.

### 10. Step22 baseline evidence

Recorded Step22 baseline metrics:

- identity L2: `12.6609528884`;
- front visible: `10.0818356599 px`;
- turn_right visible: `14.8749502083 px`;
- turn_left visible: `21.1256531544 px`;
- turn_right transferred-target: `5.74889830225 px`;
- turn_left transferred-target: `8.10962204034 px`;
- 3-view dynamic raw: `44.65749537595`.

### 11. Step61AF temporary-state loss

During the identity-preservation pre-audit it was discovered that critical
historical experiment state previously held only in `/tmp` was no longer
present.

Missing temporary state includes the expected:

- Step22 pose-convergence NPZ;
- 2.5% candidate NPZ / JSON;
- Step11 initializer NPZ;
- temporary personal-multiview landmark working directory;
- several ad-hoc experiment scripts.

This is a reproducibility/evidence loss, not a loss of the ATLAS repository.

### 12. Python bytecode recovery

Persistent Python cache remnants were recovered for the 2.4% and 2.6%
candidate scripts.

Python 3.9.6 disassembly of the 2.4% bytecode recovered the experiment
orchestration, including:

- Step22 NPZ as the direct starting state;
- active identity count `90`;
- identity parameter limit `±3.0`;
- regularization weight `1e-5`;
- `scipy.optimize.least_squares`, method `trf`;
- maximum function evaluations `60`;
- `ftol = xtol = gtol = 1e-10`;
- fixed Step22 root poses;
- neutral expression;
- static105-only analytic camera solve;
- side-only silhouette residual;
- `[image_width-1, image_height-1]` pixel scaling;
- 21 MediaPipe lower-jaw source IDs;
- expected FLAME dynamic-contour count `17`;
- exact 2.4% residual weight `0.0951925299576`.

Recovered view IDs:

- front: `0B54D8DA-6E72-4E5F-9850-DC6250CAE81F`;
- turn_right: `4E2C4BF5-6BB5-456A-8B98-C79B46CA0EC3`;
- turn_left: `7995EE35-F4AA-48DD-85B0-E83985291297`.

The cached scripts also confirmed that historical output/banner names could
remain `5%-ENERGY` even when the actual candidate weight differed. Candidate
identity state and unique output provenance therefore take precedence over the
legacy banner text.

### 13. Recovery searches completed

No exact Step22 numerical state was recovered from the searched:

- current `/tmp`;
- Git history / committed FLAME orchestration source;
- `.zsh_history`;
- `.zsh_sessions`;
- Spotlight filename search;
- available local Time Machine snapshots;
- ordinary readable `/Users/Kubi/Library` content;
- broader Python-cache reference search;
- persistent filesystem search for the recovered three view IDs.

These searches do not prove that the original portrait photographs are lost.
They establish that the searched locations did not expose the required
temporary Step22 / landmark experiment state.

### 14. No-guess recovery rule

The historical Step22 identity vector and per-view pose state must not be
approximated or fabricated.

If exact state cannot be recovered, the valid path is a new, explicitly
labelled reproducibility run from verified source inputs.

Only the personal-multiview Step22-to-silhouette-candidate chain would need
reconstruction; Phase 8 and the ATLAS project are not restarted from scratch.

### 15. Persistent experiment-state rule

Effective 26 Aug 2026:

A critical experiment artefact or intermediate state that becomes an input to
a later experiment must never have its only copy in `/tmp`.

For meaningful validated state:

- critical NPZ / JSON / equivalent state must be persisted;
- provenance / manifest information must accompany it;
- hashes must be recorded;
- `/tmp` is scratch / diagnostic storage only;
- repository and persistent-project writes remain controlled and deliberate.

Exact next scientific task after persistence closure:

`identity-preservation audit of the preferred 2.5% candidate versus the
Step22 baseline and held-out evidence`, using recovered exact state if found,
otherwise an explicitly labelled reproducibility run.

Repository checkpoint at this documentation update:

- branch: `main`;
- HEAD before update:
  `60948bb43a4e6ccfb7fd1957aadce272c4b8b347`;
- origin/main before update:
  `60948bb43a4e6ccfb7fd1957aadce272c4b8b347`;
- unrelated dirty working-tree files were not modified, staged or cleaned by
  this documentation operation.

Persistent evidence for this update:

- directory:
  `/Users/Kubi/ATLAS_PERSONAL_MULTIVIEW_SPIKE/EVIDENCE/phase8_10_personal_multiview_2026-08-26/`;
- evidence file:
  `PHASE8_10_PERSONAL_MULTIVIEW_SILHOUETTE_RECOVERY_EVIDENCE.md`;
- evidence SHA256:
  `b51a5b3796a58703d50078990faaa97043672512be7adeac94d889a96fceae57`;
- manifest:
  `SHA256SUMS.txt`.


---

## Phase 8.10 — Personal Multiview Held-Out Runner Checkpoint — 26 Aug 2026
<!-- PHASE8_10_G1D6_RUNNER_BUILD_2026_08_26 -->

- Main checklist: **8 — Pose / Expression Separation**
- Phase 8 / 8.10: **ACTIVE**
- Phase 8 final decision: **HOLD / BLOCKED**
- Phase 9: **NOT AUTHORIZED / NOT STARTED**
- [x] G-1d.5 fixed-identity held-out pose fitter complete; structural audit `RESULT=OK`.
- [x] G-1d.6 metrics + persistence runner build complete.
- Added and structurally verified: `compute_held_out_metrics`, `persist_held_out_results`, `run_leave_one_out_case`, `build_case_persistence_payload`, `run_reproducibility_held_out`.
- Final entrypoint structural audit: `AST_PARSE=OK`, `RUN_REPRODUCIBILITY_HELD_OUT_COUNT=1`, `MAIN_GUARD_COUNT=1`, `RESULT=OK`.
- Persistent runner: `/Users/Kubi/ATLAS_PERSONAL_MULTIVIEW_SPIKE/EVIDENCE/phase8_10_personal_multiview_2026-08-26/reproducibility_held_out/REPRODUCIBILITY_HELD_OUT_runner.py`
- Runner line count after build: **1912**.
- Runner has **NOT** been executed; held-out experiment has **NOT** started; JSON/NPZ held-out results have **NOT** yet been produced.
- **NEXT:** G-2 full runner audit before execution.


---

## Phase 8.10 — G-2 Full Runner Audit — 26 Aug 2026
<!-- PHASE8_10_G2_FULL_RUNNER_AUDIT_2026_08_26 -->

- Main checklist: **8 — Pose / Expression Separation**
- [x] G-2 full runner static audit completed before execution.
- Audit result: **RESULT=OK**.
- Verified: AST parse, protocol label, 3 leave-one-out cases, ±60° pose limit, pose optimizer tolerances/max_nfev, identity bounds/reg/max_nfev, exact five-start set, required functions, single main guard, JSON/NPZ stems, no duplicate required functions.
- Function count observed: **24**.
- Runner execution state: **NOT EXECUTED**.
- Phase 8 / 8.10: **ACTIVE**; final decision **HOLD / BLOCKED**.
- Phase 9: **NOT AUTHORIZED / NOT STARTED**.
- **NEXT:** G-3 persistent output target preparation.


---

## Phase 8.10 — G-3 Persistent Output Target Ready — 26 Aug 2026
<!-- PHASE8_10_G3_OUTPUT_TARGET_READY_2026_08_26 -->

- Main checklist: **8 — Pose / Expression Separation**
- [x] G-3 persistent held-out output target verified clean and ready.
- Persistent directory contains only `REPRODUCIBILITY_HELD_OUT_runner.py` before execution.
- `REPRODUCIBILITY_HELD_OUT.json`: **ABSENT**.
- `REPRODUCIBILITY_HELD_OUT.npz`: **ABSENT**.
- `PROVENANCE.md`: **ABSENT**.
- `SHA256SUMS.txt`: **ABSENT**.
- No stale held-out result artifact will be mistaken for a new run.
- Runner execution state remains **NOT EXECUTED**.
- Phase 8 / 8.10: **ACTIVE**; final decision **HOLD / BLOCKED**.
- Phase 9: **NOT AUTHORIZED / NOT STARTED**.
- **NEXT:** G-4 three two-view baseline identity fits, as part of the audited `REPRODUCIBILITY_HELD_OUT` run.


---

## Phase 8.10 — G-4..G-14 Held-Out Generalization Evidence — 26 Aug 2026
<!-- PHASE8_10_G4_G14_HELD_OUT_EVIDENCE_2026_08_26 -->

- Main checklist: **8 — Pose / Expression Separation**
- Protocol: **REPRODUCIBILITY_HELD_OUT**; not an exact historical Benchmark C rerun.
- [x] G-4 three two-view baseline identity fits complete.
- [x] G-5 three silhouette candidate identity fits complete.
- [x] G-6 held-out view exclusion enforced by leave-one-view-out protocol.
- [x] G-7 identity locked during held-out evaluation.
- [x] G-8 held-out optimization used root pose + analytically re-solved weak-perspective camera only; expression remained neutral/fixed.
- [x] G-9 all three leave-one-out cases complete.
- [x] G-10 IOD-NME complete.
- [x] G-11 bbox-NME complete.
- [x] G-12 pose bound-hit audit complete: all baseline/candidate held-out fits had **0 pose bound hits**.
- [x] G-13 identity bound-hit metrics recorded.
- [x] G-14 generalization interpretation complete.
- Held-out FRONT: IOD-NME delta **-0.0013668933674423553**; bbox-NME delta **-0.0005582593502745682**.
- Held-out RIGHT: IOD-NME delta **-0.0004531578048686466**; bbox-NME delta **-0.0001474750349296887**.
- Held-out LEFT: IOD-NME delta **-0.000607133121751792**; bbox-NME delta **-0.00018343768571488575**.
- Aggregate mean delta: IOD-NME **-0.0008090614313542646**; bbox-NME **-0.0002963906903063809**.
- **3/3 held-out views improved on both NME metrics.** This is positive generalization evidence only; it is not a Phase 8 GO/LOCK decision.
- Metric completeness audit: **RESULT=OK**; all required scalar metrics finite and all held-out pose optimizers successful.
- Persistent artifacts currently present: `REPRODUCIBILITY_HELD_OUT.json` and `REPRODUCIBILITY_HELD_OUT.npz`.
- Phase 8 / 8.10 remains **ACTIVE**; final decision remains **HOLD / BLOCKED**.
- Phase 9 remains **NOT AUTHORIZED / NOT STARTED**.
- **NEXT:** G-15 persistent outputs completion.


---

## Phase 8.10 — G-15 Persistent Outputs Complete — 26 Aug 2026
<!-- PHASE8_10_G15_PERSISTENT_OUTPUTS_COMPLETE_2026_08_26 -->

- Main checklist: **8 — Pose / Expression Separation**
- [x] G-15 persistent held-out outputs complete.
- Persistent result artifacts:
  - `reproducibility_held_out/REPRODUCIBILITY_HELD_OUT_runner.py`
  - `reproducibility_held_out/REPRODUCIBILITY_HELD_OUT.json`
  - `reproducibility_held_out/REPRODUCIBILITY_HELD_OUT.npz`
  - `reproducibility_held_out/PROVENANCE.md`
  - `PHASE8_10_REPRODUCIBILITY_HELD_OUT_EVIDENCE.md`
- `PROVENANCE.md` SHA256 at creation: `7a16107f1d77f0d449cf1d03a877bc8c39043d0ca666b9e9f38ed20ea47f9d0a`.
- Held-out evidence summary SHA256 at creation: `f43f48c3917c1bdc95ea8db057e449cc1cb9981de2d2ba94263ca60437647bb8`.
- Evidence summary records 3/3 held-out improvement on both IOD-NME and bbox-NME, while preserving explicit claim boundaries around identity preservation and Phase decisions.
- Phase 8 / 8.10 remains **ACTIVE**; final decision remains **HOLD / BLOCKED**.
- Phase 9 remains **NOT AUTHORIZED / NOT STARTED**.
- **NEXT:** G-16 SHA256 manifest.


---

## Phase 8.10 — G-16 SHA256 Manifest Complete — 26 Aug 2026
<!-- PHASE8_10_G16_SHA256_MANIFEST_COMPLETE_2026_08_26 -->

- Main checklist: **8 — Pose / Expression Separation**
- [x] G-16 SHA256 manifest complete and verified.
- Manifest: `reproducibility_held_out/SHA256SUMS.txt`.
- Manifested artifacts: held-out runner, JSON, NPZ, `PROVENANCE.md`, and held-out evidence summary.
- Verification result: all five files `OK`; `VERIFY_EXIT=0`.
- Manifest SHA256: `7f6439bd6202ff8a0cf2859ebed78c7d922719fc6d1fb95d4a017f9845fef598`.
- Phase 8 / 8.10 remains **ACTIVE**; final decision remains **HOLD / BLOCKED**.
- Phase 9 remains **NOT AUTHORIZED / NOT STARTED**.
- **NEXT:** G-17 evidence evaluation.


---

## Phase 8.10 — G-17 Evidence Evaluation Complete — 26 Aug 2026
<!-- PHASE8_10_G17_EVIDENCE_EVALUATION_COMPLETE_2026_08_26 -->

- Main checklist: **8 — Pose / Expression Separation**
- [x] G-17 held-out evidence evaluation complete.
- All 3/3 leave-one-out cases improved on both IOD-NME and bbox-NME.
- All six baseline/candidate held-out pose fits had **0 pose-bound hits**.
- Identity-bound pressure remained present: baseline/candidate hit counts by case were `(2,4)`, `(4,5)`, `(5,5)`.
- Baseline-to-candidate held-out pose shift L2: mean **0.5024247735942852 deg**, max **1.120613331392075 deg**.
- Baseline-to-candidate weak-perspective camera parameter shift L2: mean **0.03946311398967011**, max **0.04611478198293965**.
- Interpretation: **positive held-out generalization with identity-bound pressure**.
- Critical boundary: these metrics alone **do not prove identity↔pose/camera leakage closure**.
- No normalized support score or acceptance threshold was inferred.
- Phase 8 / 8.10 remains **ACTIVE**; final decision remains **HOLD / BLOCKED**.
- Phase 9 remains **NOT AUTHORIZED / NOT STARTED**.
- **NEXT:** G-18 confirm no support-score fabrication.


---

## Phase 8.10 — G-18 No Support-Score Fabrication — 26 Aug 2026
<!-- PHASE8_10_G18_NO_SUPPORT_SCORE_FABRICATION_2026_08_26 -->

- Main checklist: **8 — Pose / Expression Separation**
- [x] G-18 claim-boundary audit complete.
- Persistent held-out artifacts contain **no assigned or fabricated normalized Phase 8 support score**.
- Persistent held-out artifacts contain **no Phase 8 GO claim**, **no Phase 8 LOCK claim**, and **no Phase 9 authorization claim**.
- Claim boundaries are explicitly present in the runner, result JSON, `PROVENANCE.md`, and held-out evidence summary.
- Phase 8 / 8.10 remains **ACTIVE**; final decision remains **HOLD / BLOCKED**.
- Phase 9 remains **NOT AUTHORIZED / NOT STARTED**.
- **NEXT:** G-19 confirm no Phase 8 GO.


---

## Phase 8.10 — G-19 / G-20 and G-Chain Closure — 26 Aug 2026
<!-- PHASE8_10_G19_G20_G_CHAIN_COMPLETE_2026_08_26 -->

- Main checklist: **8 — Pose / Expression Separation**.
- [x] G-19 verified: no Phase 8 GO or LOCK decision was made.
- [x] G-20 verified: Phase 9 remains **NOT AUTHORIZED / NOT STARTED**.
- The three continuity documents and the persistent held-out evidence all retain the same Phase boundary.
- [x] G-4 through G-20 held-out execution/evidence chain is complete.
- `REPRODUCIBILITY_HELD_OUT` produced persistent runner, JSON, NPZ, provenance, evidence summary, and verified SHA256 manifest.
- Held-out result remains **positive generalization evidence with identity-bound pressure**; identity↔pose/camera leakage closure was explicitly **NOT proven by these metrics alone**.
- Phase 8 / Phase 8.10 remains **ACTIVE** and final decision remains **HOLD / BLOCKED**.
- Phase 9 remains **NOT AUTHORIZED / NOT STARTED**.
- Main checklist Item 8 is **not complete**: remaining work includes identity↔pose leakage closure, remaining camera separation audit, expression separation, region-wise evidence, and reproducibility closure.
- **NEXT active subitem:** 8.6 Identity↔Pose leakage closure; do not begin Phase 9.


---

## Phase 8.10 — Item 8.6 Identity↔Pose Leakage Evaluation — 26 Aug 2026
<!-- PHASE8_10_ITEM8_6_IDENTITY_POSE_EVALUATION_COMPLETE_2026_08_26 -->

- Main checklist: **8 — Pose / Expression Separation**.
- [x] 8.6 identity↔pose leakage evaluation complete under the approved 3-case interpretation rule.
- Result: **3/3 positive held-out evidence**.
- All three leave-one-view-out cases improved on both IOD-NME and bbox-NME.
- All baseline/candidate held-out pose optimizers succeeded and all pose-bound hit counts were `0`.
- Baseline→candidate identity delta L2 by case: front `5.900646418352201`; turn_left `2.9760018850601666`; turn_right `4.112008577690931`.
- Identity-bound pressure remained present: baseline/candidate hit counts `(2,4)`, `(4,5)`, `(5,5)`.
- Held-out baseline→candidate pose shift L2: front `1.120613331392075 deg`; turn_left `0.08418652100036113 deg`; turn_right `0.3024744683904195 deg`.
- Interpretation: positive evidence against a simple training-view-only silhouette-overfit / identity↔pose leakage explanation.
- Boundary: this is **not** proof that all identity↔pose leakage is absent, does not remove identity-bound pressure, and does not constitute a Phase 8 GO/LOCK decision.
- No new numerical acceptance threshold or normalized support score was invented.
- Phase 8 / 8.10 remains **ACTIVE / HOLD-BLOCKED**.
- Phase 9 remains **NOT AUTHORIZED / NOT STARTED**.
- **NEXT:** 8.7 identity↔camera separation audit.


---

## Phase 8.10 — Item 8.7 Identity↔Camera Separation — 26 Aug 2026
<!-- PHASE8_10_ITEM8_7_IDENTITY_CAMERA_COMPLETE_2026_08_26 -->

- Main checklist: **8 — Pose / Expression Separation**.
- [x] 8.7 identity↔camera separation audit complete.
- Weak-perspective camera is **not an identity optimizer parameter**; it is analytically re-solved for each pose/geometry candidate.
- Held-out baseline↔candidate camera drift was measured in all 3 leave-one-out cases and all values were finite.
- Maximum absolute camera deltas: scale `0.045572643138570346`; tx `0.006315134745830009`; ty `0.0038789005409067823`.
- Maximum relative scale change: `0.01947504438447153` (~1.95%).
- All three candidate held-out evaluations simultaneously retained improved IOD-NME and bbox-NME.
- Interpretation boundary: architecture prevents camera from being a free identity optimization variable, but these measurements do **not** prove that analytic camera re-solving performs zero compensatory adjustment for geometry differences.
- No numerical acceptance threshold or normalized support score was invented.
- Phase 8 / 8.10 remains **ACTIVE / HOLD-BLOCKED**.
- Phase 9 remains **NOT AUTHORIZED / NOT STARTED**.
- **NEXT:** 8.8 identity↔expression separation.


---

## Phase 8.10 — Item 8.8 Expression Source Evidence Blocker — 26 Aug 2026
<!-- PHASE8_10_ITEM8_8_EXPRESSION_SOURCE_BLOCKER_2026_08_26 -->

- Main checklist: **8 — Pose / Expression Separation**.
- [~] 8.8 identity↔expression separation remains incomplete.
- Canonical expression infrastructure exists and FLAME runtime exposes 100 expression components.
- Existing personal-multiview and six-view benchmark evidence keeps expression neutral/fixed; existing status records explicitly classify expression-separation evidence as `MISSING`.
- A read-only portrait/evidence asset inventory found the existing six benchmark portrait views and landmarks, but no separately identified same-identity neutral + mild controlled-expression source pair.
- Therefore no empirical variable-expression fitting, identity↔expression leakage, or expression-region displacement claim will be fabricated from the current neutral-only evidence.
- **BLOCKER:** a verified same-identity pair containing at least neutral and mild controlled expression states is required before empirical 8.8 closure can proceed.
- Phase 8 / 8.10 remains **ACTIVE / HOLD-BLOCKED**.
- Phase 9 remains **NOT AUTHORIZED / NOT STARTED**.
- **NEXT:** resolve the 8.8 source-evidence blocker before expression fitting.


---

## Phase 8.10 — Item 8.8 Expression Sources + Landmarks Ready — 27 Aug 2026
<!-- PHASE8_10_ITEM8_8_EXPRESSION_SOURCES_LANDMARKS_READY_2026_08_27 -->

- Main checklist: **8 — Pose / Expression Separation**.
- [~] 8.8 identity↔expression separation remains ACTIVE; empirical fitting/evaluation is not complete.
- Previous blocker `BLOCKED_MISSING_EXPRESSION_VARIATION_SOURCE` is resolved at the source-input level.
- Persistent source pair:
  - `expression_separation_8_8/source_neutral.PNG` — SHA256 `b8915ab2f6ed6b7535b3cdb3ca4c53b0bb85f1e9eca153e58db9747d533c309d`;
  - `expression_separation_8_8/source_mild_smile.PNG` — SHA256 `a408df491326ef3a9524941a23be306631d5bbcdbaf61230c1e4ccb8a373757b`.
- Persistent source provenance: `expression_separation_8_8/PROVENANCE.md`.
- MediaPipe landmark outputs generated for both images:
  - `landmarks_neutral.json`;
  - `landmarks_smile.json`.
- Both landmark JSON files verify: schema `atlas-mediapipe-face-landmarks-v1`; provider `mediapipe-face-landmarker-tasks`; MediaPipe `0.10.35`; `478` landmarks; image `1536x1152`; `view_type=front`; `synthetic=false`.
- Landmark metadata `source_image_sha256` values exactly match the persistent source PNG hashes.
- No identity↔expression separation conclusion is claimed yet.
- Phase 8 / 8.10 remains **ACTIVE / HOLD-BLOCKED**.
- Phase 9 remains **NOT AUTHORIZED / NOT STARTED**.
- **NEXT:** audit the existing FLAME expression-fitting path before fixed-identity / variable-expression execution.


---

## Phase 8.10 — Item 8.8 Fixed-Identity / Variable-Expression Protocol V1 — 27 Aug 2026
<!-- PHASE8_10_ITEM8_8_EXPRESSION_FIT_PROTOCOL_V1_2026_08_27 -->

- Main checklist: **8 — Pose / Expression Separation**.
- [~] 8.8 identity↔expression separation remains ACTIVE.
- Source blocker is resolved; neutral and mild-smile portraits and their 478-point MediaPipe landmark JSONs are persistent and verified.
- Existing ATLAS/recovered runtime contains FLAME expression basis/evaluation support but no expression-parameter fitter.
- User authorized a new evidence-only fixed-identity / variable-expression fitting implementation for 8.8.
- FLAME basis audit: 300 identity components, 100 expression components; median identity basis norm `0.0038575450527278577`; median expression basis norm `0.002364258115208621`; expression/identity median norm ratio `0.612891899612874`; all finite.
- New reproducibility protocol V1 is persisted in `expression_separation_8_8/PROVENANCE.md` under marker `ITEM8_8_EXPRESSION_FIT_PROTOCOL_V1`.
- Protocol: neutral-source identity fitted once with expression zero; identity then locked; neutral and smile pose/camera controls evaluated; smile candidate optimizes expression + root pose only with analytic camera re-solve; 100 expression components; bounds ±3; regularization `1e-5`; scipy least_squares TRF; ftol/xtol/gtol `1e-10`; max_nfev `200`; identity must not mutate; candidate must not increase reprojection error.
- Expression bounds/regularization are explicitly a new ATLAS 8.8 reproducibility protocol choice, not a claimed historical FLAME/ATLAS default.
- No numerical PASS threshold, normalized support score, Phase 8 GO/LOCK, or Phase 9 authorization is implied.
- Phase 8 / 8.10 remains **ACTIVE / HOLD-BLOCKED**.
- Phase 9 remains **NOT AUTHORIZED / NOT STARTED**.
- **NEXT:** implement the persistent 8.8 evidence runner/fitter under this locked protocol.


---

## Phase 8.10 — Item 8.8 Fixed-Identity Expression/Pose Solver Verified — 27 Aug 2026
<!-- PHASE8_10_ITEM8_8_FIXED_EXPRESSION_POSE_SOLVER_VERIFIED_2026_08_27 -->

- Main checklist: **8 — Pose / Expression Separation**.
- [~] 8.8 identity↔expression separation remains ACTIVE.
- Persistent runner: `expression_separation_8_8/REPRODUCIBILITY_EXPRESSION_runner.py`.
- Implemented: model/static-embedding/expression-landmark loaders; neutral identity fit helper; fixed-identity variable-expression/root-pose geometry evaluator; fixed-identity/fixed-expression root-pose solver.
- Pose solver is adapted from the previously verified held-out G-chain solver: ±60 degree root-pose bounds; exact five starts; scipy least_squares TRF; ftol/xtol/gtol `1e-12`; max_nfev `300`; minimum-SSE solution selection; analytic weak-perspective camera re-solve.
- Structural audit result: `AST_PARSE=OK`, solver count `1`, pose constants verified, `RESULT=OK`.
- No expression optimization has been executed yet.
- No identity↔expression separation conclusion is claimed yet.
- Phase 8 / 8.10 remains **ACTIVE / HOLD-BLOCKED**.
- Phase 9 remains **NOT AUTHORIZED / NOT STARTED**.
- **NEXT:** implement smile neutral-expression baseline using locked neutral identity.


---

## Phase 8.10 — Item 8.8 Expression Optimizer Structurally Verified — 27 Aug 2026
<!-- PHASE8_10_ITEM8_8_EXPRESSION_OPTIMIZER_STRUCTURALLY_VERIFIED_2026_08_27 -->

- Main checklist: **8 — Pose / Expression Separation**.
- [~] 8.8 identity↔expression separation remains ACTIVE.
- Persistent runner: `expression_separation_8_8/REPRODUCIBILITY_EXPRESSION_runner.py`.
- Smile neutral-expression baseline helper is implemented with identity locked, expression fixed to zero, root pose optimized, and analytic weak-perspective camera re-solve.
- Smile expression candidate helper is implemented with optimization variables restricted to **100 expression coefficients + 3 root-pose parameters**; identity is copied/locked and guarded against mutation.
- Protocol constants verified structurally: expression bounds ±3; regularization `1e-5`; scipy `least_squares` TRF; ftol/xtol/gtol `1e-10`; max_nfev `200`.
- Candidate contains a non-degradation guard against the neutral-expression smile baseline.
- Structural audit: `AST_PARSE=OK`, required guards/constants verified, total function count `10`, `RESULT=OK`.
- No end-to-end expression fitting experiment has been executed yet.
- No identity↔expression separation conclusion is claimed yet.
- Phase 8 / 8.10 remains **ACTIVE / HOLD-BLOCKED**.
- Phase 9 remains **NOT AUTHORIZED / NOT STARTED**.
- **NEXT:** add the narrow end-to-end runner orchestration without executing it.


---

## Phase 8.10 — Item 8.8 Expression Runner Pre-Execution Complete — 27 Aug 2026
<!-- PHASE8_10_ITEM8_8_EXPRESSION_RUNNER_PREEXEC_COMPLETE_2026_08_27 -->

- Main checklist: **8 — Pose / Expression Separation**.
- [~] 8.8 identity↔expression separation remains ACTIVE.
- Persistent runner: `expression_separation_8_8/REPRODUCIBILITY_EXPRESSION_runner.py`.
- Execution-preparation chain is now implemented and structurally audited: input/model loaders; neutral identity fit; fixed-identity expression/root-pose geometry evaluation; fixed-expression pose solver; smile neutral-expression baseline; smile expression+pose candidate; end-to-end in-memory orchestration; JSON/NPZ persistence.
- Persistence audit verified one persistence function and one camera serializer; JSON target `REPRODUCIBILITY_EXPRESSION.json`; NPZ target `REPRODUCIBILITY_EXPRESSION.npz`; locked identity, baseline/candidate pose, candidate expression parameters, and claim boundary are represented; `RESULT=OK`.
- No end-to-end expression experiment has been executed yet.
- Therefore no measured identity↔expression result, leakage conclusion, region displacement conclusion, Phase 8 GO/LOCK, or Phase 9 authorization is claimed.
- Phase 8 / 8.10 remains **ACTIVE / HOLD-BLOCKED**.
- Phase 9 remains **NOT AUTHORIZED / NOT STARTED**.
- **NEXT:** execute the expression reproducibility runner once and persist its JSON/NPZ outputs, then inspect the actual result before any interpretation.


---

## Phase 8.10 — Item 8.8 Expression Execution Verified — 27 Aug 2026
<!-- PHASE8_10_ITEM8_8_EXPRESSION_EXECUTION_VERIFIED_2026_08_27 -->

- Main checklist: **8 — Pose / Expression Separation**.
- [~] 8.8 identity↔expression separation remains ACTIVE; no final 8.8 decision yet.
- Evidence directory: `/Users/Kubi/ATLAS_PERSONAL_MULTIVIEW_SPIKE/EVIDENCE/phase8_10_personal_multiview_2026-08-26/expression_separation_8_8/`.
- End-to-end `REPRODUCIBILITY_EXPRESSION` execution completed successfully.
- Locked neutral identity remained identical across neutral-control, smile-baseline, and smile-candidate stages: `True`.
- Neutral identity final weighted RMSE: `0.0017046114719840692`.
- Neutral control weighted RMSE: `0.0016562939971430865`.
- Smile neutral-expression baseline weighted RMSE: `0.003244844202129136`.
- Smile expression+pose candidate weighted RMSE: `0.0017492051014259343`.
- Absolute smile reprojection improvement: `0.0014956391007032019`.
- Expression coefficient L2: `3.11474187411104`; maximum absolute coefficient: `1.5184330400773487`; expression bound hits: `0`.
- Candidate pose bound hits: `0`; optimizer success: `True`.
- Persistent JSON verified: `REPRODUCIBILITY_EXPRESSION.json`, SHA256 `4913e4564b950c041c337b824c7b8acd185578d5e180834ef2ac59203f8d5da5`.
- Persistent NPZ verified: `REPRODUCIBILITY_EXPRESSION.npz`, SHA256 `7397903d9df50dfc459623e42e49417516a42fa367260ddcc73c400821685a74`.
- NPZ contains locked identity `(300,)` and smile candidate expression `(100,)` plus neutral/baseline/candidate root poses.
- These results establish successful execution and strict identity locking only; they do **not yet establish the final identity↔expression leakage conclusion or region-wise expression geometry quality**.
- Phase 8 / 8.10 remains **ACTIVE / HOLD-BLOCKED**.
- Phase 9 remains **NOT AUTHORIZED / NOT STARTED**.
- **NEXT:** evaluate identity↔expression leakage from the persisted evidence before region-wise interpretation.


---

## Phase 8.10 — Item 8.8 Identity↔Expression Leakage Audit — 27 Aug 2026
<!-- PHASE8_10_ITEM8_8_IDENTITY_EXPRESSION_LEAKAGE_POSITIVE_EVIDENCE_2026_08_27 -->

- Main checklist: **8 — Pose / Expression Separation**.
- [~] 8.8 identity↔expression separation remains ACTIVE; final 8.8 decision is not yet made.
- Persisted `REPRODUCIBILITY_EXPRESSION` evidence was audited for identity/expression leakage.
- Locked identity remained unchanged across expression stages: `True`; direct identity-parameter leakage is therefore **BLOCKED_BY_CONSTRUCTION** for this experiment.
- Smile neutral-expression baseline weighted RMSE: `0.003244844202129136`.
- Smile expression+pose candidate weighted RMSE: `0.0017492051014259343`.
- Absolute RMSE improvement: `0.0014956391007032019`; relative improvement: `0.46092786202857555` (~46.09%).
- Baseline→candidate root-pose shift: `0.021695098363393176` rad L2 = `1.2430375723436085` deg L2; components `[-1.2324791684955405, 0.14853940049759803, 0.0638243839159214]` deg.
- Camera compensation remained finite but nonzero: delta scale `0.020698729014841488`; relative scale change `0.0161588846252`; delta tx `-0.0002854984451964304`; delta ty `0.0037528664005536116`.
- Expression coefficient L2 `3.11474187411104`; max absolute coefficient `1.5184330400773487`; expression bound hits `0`; pose bound hits `0`; optimizer success `True`.
- Audit classification: **POSITIVE_EVIDENCE** against direct identity↔expression parameter leakage in this locked-identity experiment.
- Boundary: pose and analytic camera changed during candidate fitting, so this does **not** prove that all observed expression signal is exclusively explained by the expression basis or that all possible identity/expression leakage is absent.
- Phase 8 / 8.10 remains **ACTIVE / HOLD-BLOCKED**.
- Phase 9 remains **NOT AUTHORIZED / NOT STARTED**.
- **NEXT:** measure global and facial-region expression displacement before making the 8.8 decision.


---

## Phase 8.10 — Item 8.8 Global Expression Displacement + Region Mapping Boundary — 27 Aug 2026
<!-- PHASE8_10_ITEM8_8_GLOBAL_EXPRESSION_DISPLACEMENT_AND_REGION_BLOCKER_2026_08_27 -->

- Main checklist: **8 — Pose / Expression Separation**.
- [~] 8.8 identity↔expression separation remains ACTIVE pending final evaluation.
- Global canonical expression displacement was measured on the same locked identity, comparing zero expression against the fitted mild-smile expression with pose and camera excluded from the measurement.
- FLAME vertex count: `5023`; displacement finite: `True`.
- Neutral canonical bbox diagonal: `0.4486333063594445`.
- Mean displacement: `0.0009632637131319599` = `0.0021471070013696085` of bbox diagonal (~0.2147%).
- RMS displacement: `0.0019937861778385134` = `0.0044441332143117665` of bbox diagonal (~0.4444%).
- P95 displacement: `0.005499748573523398` = `0.012258894949535925` of bbox diagonal (~1.2259%).
- Maximum displacement: `0.009147708844819628` = `0.020390168797433186` of bbox diagonal (~2.0390%).
- Existing canonical semantic ownership includes face/jaw/chin/eye-region names, but the verified real FLAME Phase 8.10 topology currently maps only `face` to all 5023 vertices.
- FLAME model asset inventory contains no segmentation/region/mask/vertex-part asset. Therefore jaw/chin/eye/etc. region-wise displacement cannot currently be measured without introducing an unverified vertex segmentation.
- No fabricated region indices or region metrics are permitted; region-wise expression displacement is therefore explicitly **BLOCKED_BY_MISSING_VERIFIED_FLAME_SUBREGION_MAPPING**.
- This does not invalidate the verified global displacement or locked-identity leakage evidence.
- No Phase 8 GO/LOCK or Phase 9 authorization is implied.
- Phase 8 / 8.10 remains **ACTIVE / HOLD-BLOCKED**; Phase 9 remains **NOT AUTHORIZED / NOT STARTED**.
- **NEXT:** perform the bounded final evaluation for Item 8.8 using only verified evidence and this explicit region-mapping limitation.


---

## Phase 8.10 — Item 8.8 Bounded Final Evaluation — 27 Aug 2026
<!-- PHASE8_10_ITEM8_8_BOUNDED_FINAL_EVALUATION_2026_08_27 -->

- Main checklist: **8 — Pose / Expression Separation**.
- [x] 8.8 identity↔expression separation bounded evaluation completed.
- Evidence classification: **POSITIVE_EVIDENCE_WITH_REGION_MAPPING_LIMITATION**.
- Identity remained locked across expression stages: `True`.
- Smile neutral-expression baseline weighted RMSE: `0.003244844202129136`.
- Smile expression+pose candidate weighted RMSE: `0.0017492051014259343`.
- Relative RMSE improvement: `0.46092786202857555` (~46.09%).
- Optimizer success: `True`; expression finite: `True`; expression bound hits: `0`; pose bound hits: `0`.
- Direct identity-parameter leakage is **BLOCKED_BY_CONSTRUCTION** for this experiment because identity is not an optimized smile-stage variable and was verified unchanged.
- Global canonical expression displacement was independently verified on the same locked identity with pose/camera excluded.
- Region-wise expression displacement remains **BLOCKED_BY_MISSING_VERIFIED_FLAME_SUBREGION_MAPPING** because the verified real FLAME topology currently exposes only the all-vertex `face` region and no trusted segmentation asset was found.
- No PASS threshold was applied. This result does not prove absence of all possible identity/expression leakage and does not prove region-wise expression quality.
- No Phase 8 GO/LOCK is claimed.
- Phase 8 / 8.10 remains **ACTIVE / HOLD-BLOCKED**.
- Phase 9 remains **NOT AUTHORIZED / NOT STARTED**.
- **NEXT CHECKLIST ITEM:** 8.9 — Pose/Expression Region-wise, beginning from the verified missing-subregion-mapping boundary; do not invent FLAME region indices.

## PHASE8_10_ITEM8_9_WIDE_REGION_PROTOCOL_V1_2026_08_27

- Main Checklist Item 8.9 `Pose / Expression Region-wise`: wide protocol approved.
- Region evidence will cover fully supported static105 groups and explicitly labelled partial-overlap groups, plus the existing jaw/silhouette channel.
- Pose, expression, and cross-region compensation will be evaluated separately.
- Real FLAME vertex-level 3D subregion metrics remain blocked pending a verified FLAME semantic vertex mapping.
- No acceptance threshold was invented.
- Phase 8 remains ACTIVE / HOLD-BLOCKED.
- Phase 9 remains NOT AUTHORIZED / NOT STARTED.

## PHASE8_10_ITEM8_9_EXPRESSION_REGION_WISE_EVIDENCE_2026_08_27

- Item 8.9 expression region-wise audit executed under the approved wide protocol.
- Locked-identity baseline vs expression candidate: all 7 measured regions improved; 0 degraded.
- Fully supported static105 regions improved: right_eye, left_eye, nose_bridge, upper_lip.
- Verified-overlap partial regions also improved: nose_body, nose_base, lower_lip.
- Largest relative improvement: lower_lip ~79.93%; smallest: nose_bridge ~12.49%.
- Evidence is 2D observation-space only; verified real-FLAME 3D subregion mapping remains unavailable.
- Next Item 8.9 task: held-out pose region-wise audit.
- Phase 8 remains ACTIVE / HOLD-BLOCKED; Phase 9 remains NOT AUTHORIZED / NOT STARTED.

## PHASE8_10_ITEM8_9_HELD_OUT_POSE_REGION_WISE_EVIDENCE_2026_08_27

- Item 8.9 held-out pose region-wise audit executed under the approved wide protocol.
- Across 21 region-view comparisons: 12 improved, 9 degraded.
- Fully supported static105 regions: 8 improved / 4 degraded.
- Partial-overlap regions: 4 improved / 5 degraded.
- `nose_body` degraded in all 3 held-out views.
- Therefore the previously positive global held-out metrics do not establish uniform regional improvement; cross-region compensation is measurable.
- Classification is not yet final; jaw/silhouette integration and combined cross-region evaluation remain.
- No threshold was invented.
- Phase 8 remains ACTIVE / HOLD-BLOCKED; Phase 9 remains NOT AUTHORIZED / NOT STARTED.

## PHASE8_10_ITEM8_9_JAW_SILHOUETTE_CHANNEL_INTEGRATED_2026_08_27

- Item 8.9 jaw / silhouette contour-region channel integrated into the approved wide protocol.
- static105 has zero overlap with the 21 lower-jaw IDs and the full 36-point face oval, so this channel remains separate from interior-face region metrics.
- Corrected silhouette evidence: turn_right ~61.35% reduction; turn_left ~61.61% reduction.
- Preferred candidate remains the 2.5% silhouette-energy candidate.
- This is silhouette/profile evidence only, not identity proof or 3D FLAME jaw-region evidence.
- Next Item 8.9 task: combined cross-region audit.
- Phase 8 remains ACTIVE / HOLD-BLOCKED; Phase 9 remains NOT AUTHORIZED / NOT STARTED.

## PHASE8_10_ITEM8_9_COMBINED_CROSS_REGION_AUDIT_2026_08_27

- Item 8.9 combined cross-region audit completed from the three verified evidence channels.
- Expression: 7/7 measured regions improved, 0 degraded.
- Held-out pose: 12/21 region-view comparisons improved, 9 degraded; cross-region compensation is measurable.
- `nose_body` degraded in all 3 held-out pose views.
- Jaw/silhouette contour evidence remains positive (~61.35% right, ~61.61% left reduction) and separate from static105 interior-region metrics.
- Positive global held-out metrics do not establish uniform regional improvement.
- No new formal classification code or acceptance threshold was invented.
- 3D real-FLAME semantic-subregion evaluation remains blocked by missing verified vertex mapping.
- Next: Item 8.9 bounded final evaluation.
- Phase 8 remains ACTIVE / HOLD-BLOCKED; Phase 9 remains NOT AUTHORIZED / NOT STARTED.

## PHASE8_10_ITEM8_9_BOUNDED_FINAL_EVALUATION_2026_08_27

- [x] Main Checklist Item 8.9 Pose / Expression Region-wise bounded evaluation completed under the approved wide protocol.
- Expression region evidence: 7/7 measured regions improved; 0 degraded.
- Held-out pose region evidence: 12/21 improved; 9/21 degraded; measurable cross-region compensation remains.
- `nose_body` degraded in all 3 held-out pose views.
- Jaw/silhouette contour evidence remains positive (~61.35% right, ~61.61% left reduction).
- Therefore uniform region-wise preservation is NOT established despite positive global held-out metrics.
- No acceptance/failure threshold or new formal classification code was invented.
- Real-FLAME vertex-level 3D subregion evaluation remains blocked by missing verified semantic vertex mapping.
- Phase 8 remains ACTIVE / HOLD-BLOCKED.
- Phase 9 remains NOT AUTHORIZED / NOT STARTED.

## PHASE8_10_ITEM8_REPRODUCIBILITY_CLOSURE_2026_08_27

- [x] Main Checklist Item 8 reproducibility closure completed for the held-out and expression/8.9 evidence chains.
- New machine-readable regional evidence: `REPRODUCIBILITY_ITEM8_9_REGION_WISE.json`, SHA256 `f5a5cc438d003c1a4186d8782aa3ad008105a8a9800325ca56415b9247eaa7ca`.
- Expression/8.9 `SHA256SUMS.txt` manifests 9 persistent artifacts.
- Manifest verification: 9/9 `OK`; `VERIFY_EXIT=0`.
- Manifest SHA256: `a6402ef2ae8d729cbf69ba68adb1ab9e3c432b5240bde9b38a680e17db96294e`.
- Critical Item 8 experiment state required for continued interpretation is no longer dependent on `/tmp`.
- This closure does not alter the bounded scientific result: held-out pose region behavior remains mixed and real-FLAME 3D subregion mapping remains blocked.
- No Phase 8 GO/LOCK is claimed.
- Phase 9 remains NOT AUTHORIZED / NOT STARTED.
- Next: audit Main Checklist Item 8 as a whole before any closure claim.

## PHASE8_10_ITEM8_REPRODUCIBILITY_CLOSURE_FINAL_VERIFIED_2026_08_27

- [x] Main Checklist Item 8 reproducibility closure final verification completed.
- Expression / Item 8.9 manifest verification: 9/9 artifacts `OK`.
- `VERIFY_EXIT=0`.
- Final verified `SHA256SUMS.txt` SHA256:
  `a6402ef2ae8d729cbf69ba68adb1ab9e3c432b5240bde9b38a680e17db96294e`.
- Previous pre-refresh manifest SHA256 `43cecf6f539690c7b30edf83d4d4fafaf0abbab6076841309cdf7ae208f28a0f` is superseded because
  `PROVENANCE.md` was updated after the initial manifest creation.
- Persistent expression and Item 8.9 evidence no longer depends on `/tmp`.
- This reproducibility closure does not change the bounded scientific result:
  held-out pose region behavior remains mixed and verified real-FLAME 3D
  semantic-subregion mapping remains unavailable.
- No Phase 8 GO / LOCK is claimed.
- Phase 9 remains NOT AUTHORIZED / NOT STARTED.
- Next: whole-item audit of Main Checklist Item 8 before any closure claim.

## PHASE8_10_ITEM8_HEALTH_CLOSURE_PLAN_LOCKED_2026_08_27

### Main Checklist Item 8 — Pose / Expression Separation
**Revised Health Closure Plan — USER APPROVED / LOCKED**

Reason for revision:
- the previously used internal 8.1–8.5 working labels were not recovered as an authoritative numbered plan and must not be retroactively represented as such;
- the underlying verified work remains valid and is preserved;
- Item 8.9 established mixed held-out regional pose behavior: `12/21` region-view comparisons improved and `9/21` degraded;
- `nose_body` degraded in `3/3` held-out pose views;
- uniform region-wise preservation is therefore not established;
- verified real-FLAME semantic vertex-level facial-subregion mapping is still unavailable.

Already verified foundation — DO NOT REPEAT:
- fixed-identity held-out pose fitting;
- analytic weak-perspective camera separation;
- leave-one-view-out generalization evidence;
- identity↔pose leakage evaluation;
- identity↔camera separation audit;
- fixed-identity identity↔expression evaluation;
- observation-space region-wise pose/expression audit;
- jaw/silhouette contour integration;
- reproducibility closure and verified persistent manifests.

### LOCKED remaining Item 8 Health Closure sequence

#### H1 — Pose Regional Regression Diagnosis
- diagnose the source of the measured held-out regional regressions;
- `nose_body` degradation in `3/3` held-out views is a mandatory diagnostic target;
- distinguish identity, root-pose, analytic-camera and correspondence/observation compensation effects;
- diagnosis precedes optimization;
- no blind parameter tuning and no invented acceptance threshold.

#### H2 — Verified 3D Facial-Region Mapping
- establish a verified semantic facial-region mapping on the real FLAME topology for the regions required by Item 8 evaluation;
- prefer an authoritative/provider-supported mapping asset when provenance is acceptable;
- if no trustworthy mapping exists, design a separately verifiable mapping contract before using vertex-level region claims;
- fabricated or guessed FLAME vertex indices are prohibited;
- absence of verified mapping must remain explicitly BLOCKED rather than being silently inferred.

#### H3 — Counterfactual Separation Stress
- hold canonical identity fixed while independently perturbing/evaluating pose, expression and camera conditions;
- measure canonical identity drift and region-wise behavior under those controlled changes;
- preserve separation between identity geometry, temporary expression deformation, root pose and observation camera;
- use this as a validation channel, not as biometric identification or face-recognition functionality.

#### H4 — Commercial-Health Acceptance Gate
- evaluate whether remaining regressions materially threaten premium personalized-product likeness, consistency or automation reliability;
- final Item 8 result may be `PASS`, `BOUNDED_PASS`, or `HOLD`, based only on verified evidence;
- `21/21` regional improvement is not pre-declared as a mandatory academic target;
- no arbitrary numerical threshold, normalized support score or success criterion may be invented without explicit approval;
- unresolved customer-visible identity degradation remains a blocker.

### Scope boundary
- Cross-session long-term identity stability, exhaustive adversarial search, biometric fingerprinting and face-recognition functionality are NOT mandatory Item 8 requirements.
- They remain optional future Advanced Validation work and require separate authorization.
- This plan revision does not discard or invalidate prior Item 8 evidence.
- Main Checklist Item 8 remains ACTIVE until H1→H4 are completed/evaluated.
- Phase 8 / Phase 8.10 remains ACTIVE / HOLD-BLOCKED.
- No Phase 8 GO / LOCK decision is made by this plan revision.
- Phase 9 remains NOT AUTHORIZED / NOT STARTED.

### Exact next step
**H1 — Pose Regional Regression Diagnosis.**
Do not start H2, H3, H4 or Phase 9 before H1 is completed or explicitly re-planned by the user.

## PHASE8_10_ITEM8_H1_NOSE_BODY_PER_LANDMARK_DIAGNOSIS_2026_08_27

- [x] H1 `nose_body` per-landmark regression decomposition persisted as machine-readable evidence.
- Artifact: `ITEM8_H1_NOSE_BODY_PER_LANDMARK_DIAGNOSIS.json`.
- SHA256: `840d2ff568d2616ba2b76a70b285c7d6e3fb0947c34e42b8b9221557b88e06d0`.
- Existing Item 8.9 regional means were independently reproduced in `3/3` held-out cases.
- Front: `2` degraded / `3` improved nose-body landmarks.
- Turn-right: `4` degraded / `1` improved.
- Turn-left: `3` degraded / `2` improved.
- No single landmark explains all three regional regressions.
- Current bounded hypothesis: **view-dependent regional compensation**.
- Causal attribution is NOT yet established.
- No new fit, threshold, Phase 8 GO/LOCK, or Phase 9 authorization is claimed.
- Next: refresh and verify the persistent expression/H1 SHA256 manifest before using this artifact in further H1 diagnosis.

## PHASE8_10_ITEM8_H1_MANIFEST_VERIFIED_2026_08_27

- [x] H1 persistent evidence manifest refreshed and verified.
- Manifested artifacts: `10`.
- Verification: `10/10 OK`.
- `VERIFY_EXIT=0`.
- Current `SHA256SUMS.txt` SHA256:
  `e375bd030d4e6c8bab94e35f21bd38a2714d871568bf4bc9a8300a280bda2ecf`.
- `ITEM8_H1_NOSE_BODY_PER_LANDMARK_DIAGNOSIS.json` is included with SHA256
  `840d2ff568d2616ba2b76a70b285c7d6e3fb0947c34e42b8b9221557b88e06d0`.
- The H1 per-landmark diagnostic is now persistent and manifest-verified and may be used as input to subsequent H1 diagnosis.
- No causal attribution has yet been established.
- Next: H1 source/causal diagnosis; do not begin H2.

## PHASE8_10_ITEM8_H1_IDENTITY_POSE_CAMERA_FACTORIAL_ATTRIBUTION_2026_08_27

- [x] H1 identity / pose / camera factorial attribution persisted as machine-readable evidence.
- Artifact SHA256: `613c909793580f80b7d8e30c6cb4292097175a5e04e0322722816fbcf5ca722d`.
- No new fit was executed.
- Front identity-only nose-body delta: `+7.011260688409 px`; candidate-geometry camera effect: `-12.121822264794 px`; interaction remainder: `-18.727062751493 px`.
- Turn-right identity-only delta: `+1.797765024214 px`; candidate-geometry camera effect: `-1.835768571616 px`; interaction remainder: `-1.575516500993 px`.
- Turn-left identity-only delta: `+9.448225974679 px`; candidate-geometry camera effect: `-9.066358967544 px`; interaction remainder: `-12.280936264086 px`.
- Current bounded diagnostic: nose-body degradation is **not pose-only**; strong view-dependent, non-additive identity/analytic-camera compensation is observed.
- This is not yet a causal closure.
- Next: refresh and verify the evidence manifest before further H1 use.

## PHASE8_10_ITEM8_H1_FACTORIAL_MANIFEST_VERIFIED_2026_08_27

- [x] H1 identity/pose/camera factorial attribution evidence is persistent and manifest-verified.
- Manifested artifacts: `11`.
- Verification: `11/11 OK`.
- `VERIFY_EXIT=0`.
- Current `SHA256SUMS.txt` SHA256:
  `25a1b3cdc3596e581021dceacef3d21e52527da823612b3f23c10800204a7ac7`.
- Factorial attribution artifact:
  `ITEM8_H1_IDENTITY_POSE_CAMERA_FACTORIAL_ATTRIBUTION.json`.
- Artifact SHA256:
  `613c909793580f80b7d8e30c6cb4292097175a5e04e0322722816fbcf5ca722d`.
- Current bounded diagnostic remains: `nose_body` regression is not pose-only; strong view-dependent, non-additive identity / analytic-camera compensation is observed.
- This is not yet final causal attribution.
- Next locked step: continue H1 source/causal diagnosis; do not begin H2.

## PHASE8_10_ITEM8_H1_ANALYTIC_CAMERA_COMPENSATION_ISOLATED_2026_08_27

- [x] H1 analytic-camera compensation isolation completed and persisted.
- Artifact: `ITEM8_H1_ANALYTIC_CAMERA_COMPENSATION_ISOLATION.json`.
- SHA256: `5c54a26f45b34d1486ad99661452abbcad0a08879c535ab93adcf9d998c15878`.
- Identity-conditioned camera compensation on nose-body:
  - front `-6.353380705389 px`;
  - turn-right `-1.601042624041 px`;
  - turn-left `-9.229767619759 px`.
- Joint identity+pose camera compensation:
  - front `-12.121822264794 px`;
  - turn-right `-1.835768571616 px`;
  - turn-left `-9.066358967544 px`.
- Verified conclusion: analytic camera re-solving materially masks/compensates geometry-conditioned regional reprojection changes in all `3/3` held-out views.
- Pose-only change does not explain the complete nose-body regression pattern.
- Ultimate causal source of the candidate identity-geometry change is NOT yet established.
- Next: refresh and verify the H1 evidence manifest before further diagnosis.

## PHASE8_10_ITEM8_H1_CAMERA_COMPENSATION_MANIFEST_VERIFIED_2026_08_27

- [x] H1 analytic-camera compensation evidence is persistent and manifest-verified.
- Manifested artifacts: `12`.
- Verification: `12/12 OK`.
- `VERIFY_EXIT=0`.
- Current `SHA256SUMS.txt` SHA256:
  `13fee252e6de140e16ad75772d7699427bf25a72e10bf0b2c3772a26a6749c6e`.
- Analytic-camera compensation artifact:
  `ITEM8_H1_ANALYTIC_CAMERA_COMPENSATION_ISOLATION.json`.
- Artifact SHA256:
  `5c54a26f45b34d1486ad99661452abbcad0a08879c535ab93adcf9d998c15878`.
- Verified bounded result: analytic weak-perspective camera re-solving materially compensates geometry-conditioned nose-body reprojection change in all `3/3` held-out views.
- Pose-only change is insufficient to explain the observed three-view nose-body regression pattern.
- Ultimate causal source of the candidate identity-geometry change remains unresolved.
- Next locked step: continue H1 source/causal diagnosis; do not begin H2.

## PHASE8_10_ITEM8_H1_SILHOUETTE_INITIALIZATION_CONTROL_2026_08_27

- [x] H1 silhouette initialization sensitivity control completed and persisted.
- Artifact SHA256:
  `ecb5849f4405e8c075e28dbb61e9b3a21be4c23caee9ce35b938af04e6f33d54`.
- Zero-init silhouette fits converge extremely close to persisted baseline-initialized candidate fits:
  - front identity L2 `0.000148252162`;
  - turn-right `0.000164822372`;
  - turn-left `0.000144593254`.
- Held-out nose-body output differences are approximately `±0.00001 px`.
- Bounded conclusion: initialization choice is not supported as a material explanation for the candidate identity shift.
- Verified meaningful objective-level protocol difference remains silhouette inclusion.
- This is not yet the final H1 causal conclusion.
- Next: refresh and verify H1 evidence manifest.

## PHASE8_10_ITEM8_H1_INITIALIZATION_CONTROL_MANIFEST_VERIFIED_2026_08_27

- [x] H1 silhouette-initialization control evidence is persistent and manifest-verified.
- Manifested artifacts: `13`.
- Verification: `13/13 OK`.
- `VERIFY_EXIT=0`.
- Current `SHA256SUMS.txt` SHA256:
  `18e6bb538ae01ce7080fc72d436f97aba18337829d069eb7963ddcb18b6ba4f6`.
- Initialization-control artifact:
  `ITEM8_H1_SILHOUETTE_INITIALIZATION_CONTROL.json`.
- Artifact SHA256:
  `ecb5849f4405e8c075e28dbb61e9b3a21be4c23caee9ce35b938af04e6f33d54`.
- Verified bounded result:
  zero-initialized silhouette fits converge essentially to the same candidate identities as baseline-initialized silhouette fits in all three held-out cases.
- Initialization/basin choice is therefore not supported as a material explanation for the candidate identity shift in this control.
- The meaningful verified objective-level protocol difference remains silhouette-residual inclusion.
- Combined H1 evidence now supports preparation of the bounded H1 diagnostic conclusion; no H2 work has started.

## PHASE8_10_ITEM8_H1_POSE_REGIONAL_REGRESSION_DIAGNOSIS_COMPLETE_2026_08_27

- [x] **H1 — Pose Regional Regression Diagnosis: BOUNDED_DIAGNOSIS_COMPLETE.**
- Persistent conclusion:
  `ITEM8_H1_POSE_REGIONAL_REGRESSION_DIAGNOSIS.json`.
- SHA256:
  `c28a2b416e55b77a1cfcc0cad0c09eecd3ed366fb6f09e3735036bd0f364167d`.
- Classification:
  `VIEW_DEPENDENT_NONADDITIVE_OBSERVATION_CONDITIONED_IDENTITY_CAMERA_COMPENSATION`.
- Verified:
  - nose-body regression `3/3` held-out views;
  - root pose alone insufficient;
  - fixed-camera candidate identity worsens nose-body `3/3`;
  - analytic camera materially compensates the geometry-conditioned change `3/3`;
  - initialization/basin effect materially unsupported by zero-init control;
  - meaningful objective-level difference is silhouette-residual inclusion;
  - silhouette constraint is transferred 2D observation/correspondence evidence, not independent metric 3D facial-region GT.
- Not proven:
  - true metric 3D nose deformation;
  - verified semantic FLAME nose-region vertex mapping;
  - commercial acceptability;
  - Phase 8 GO/LOCK.
- H2 has not started.
- Next locked step after H1 manifest closure:
  `H2 — Verified 3D Facial-Region Mapping`.

## PHASE8_10_ITEM8_H1_OFFICIALLY_CLOSED_2026_08_27

- [x] **H1 — Pose Regional Regression Diagnosis officially closed.**
- Final diagnosis status: `BOUNDED_DIAGNOSIS_COMPLETE`.
- Final diagnosis artifact:
  `ITEM8_H1_POSE_REGIONAL_REGRESSION_DIAGNOSIS.json`.
- Diagnosis artifact SHA256:
  `c28a2b416e55b77a1cfcc0cad0c09eecd3ed366fb6f09e3735036bd0f364167d`.
- Final evidence manifest verification:
  - artifacts: `14`;
  - verification: `14/14 OK`;
  - `VERIFY_EXIT=0`;
  - manifest SHA256:
    `d7905a154725868baa44b60a3cf4da59be533dca12f0d7c66f3ac26450cbb91f`.
- H1 bounded classification:
  `VIEW_DEPENDENT_NONADDITIVE_OBSERVATION_CONDITIONED_IDENTITY_CAMERA_COMPENSATION`.
- H1 verified:
  - nose-body regression occurs in `3/3` held-out views;
  - no single static105 nose landmark explains all three;
  - root pose alone does not explain the pattern;
  - fixed-camera candidate identity change worsens nose-body reprojection in all `3/3`;
  - analytic weak-perspective camera materially compensates the geometry-conditioned error in all `3/3`;
  - initialization/basin sensitivity is not materially supported by the zero-init silhouette control;
  - silhouette inclusion is the meaningful verified objective-level protocol difference;
  - silhouette evidence remains transferred 2D observation/correspondence evidence, not independent metric 3D semantic-region ground truth.
- H1 does NOT establish:
  - true metric 3D nose deformation;
  - verified semantic FLAME nose-region vertex mapping;
  - commercial acceptability;
  - Phase 8 GO/LOCK.
- H2 has not started.
- Next locked step:
  `H2 — Verified 3D Facial-Region Mapping`.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H2_PROVIDER_ANCHOR_MAPPING_BOUNDARY_2026_08_27

- [~] **H2 — Verified 3D Facial-Region Mapping remains ACTIVE.**
- Persistent evidence:
  `ITEM8_H2_OBSERVATION_PROVIDER_REGION_ANCHOR_AUDIT.json`
- Evidence SHA256:
  `83e59b0cd05b73794462b8e72ecb5914d246a9ed46ee77eac7d028f99e04e51d`.
- Verified FLAME provider mask source contains:
  - `nose`: 379 unique vertices;
  - `lips`: 250 unique vertices after deduplication;
  - `left_eye_region`: 287 unique vertices;
  - `right_eye_region`: 287 unique vertices.
- Existing MediaPipe-to-FLAME barycentric anchors were compared against those provider masks without creating a new dense vertex mapping.
- Verified anchor support:
  - `left_eye -> left_eye_region`: 6/6 triangles fully inside; barycentric support 1.0;
  - `right_eye -> right_eye_region`: 6/6 fully inside; support 1.0;
  - `upper_lip -> lips`: 8/8 fully inside; support 1.0;
  - `lower_lip -> lips`: 7/7 fully inside; support 1.0;
  - `nose_bridge -> nose`: 3/4 fully inside, 4/4 partially/fully inside; mean barycentric support 0.880330790;
  - `nose_body -> nose`: 0/5 fully inside, only 2/5 have any inside vertex; mean barycentric support 0.016339805;
  - `nose_base -> nose`: 0/2 have any inside vertex; barycentric support 0.0.
- Therefore the provider `nose` mask MUST NOT be relabelled or assumed to represent Item-8 `nose_body` or `nose_base`.
- Current evidence supports verified broad 3D mapping for eye and lip regions and substantial support for `nose_bridge`, but NOT verified dense 3D mapping for `nose_body` / `nose_base`.
- No fabricated/guessed FLAME vertex indices are permitted.
- H2 remains open pending diagnosis of the nose semantic mismatch or a separately verifiable mapping route.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H2_NOSE_SEMANTIC_MISMATCH_DIAGNOSIS_2026_08_27

- [~] **H2 — Verified 3D Facial-Region Mapping remains ACTIVE.**
- Persistent evidence:
  `ITEM8_H2_NOSE_SEMANTIC_MISMATCH_CLASSIFICATION.json`
- Evidence SHA256:
  `89fb1ad05ead4c9236ab93f35b350c1c12dcb4ea256e4961922fa3aa0af4c7c2`.
- Existing MediaPipe-to-FLAME barycentric embedding was used only as an observation-anchor diagnostic; no new dense mapping or segmentation was created.
- `nose_body`:
  - all 5 Item-8 landmarks have valid FLAME surface embeddings;
  - all 5 embedded triangles are fully inside the broad FLAME `face` provider mask;
  - only landmarks 129 and 358 touch a `nose`-mask vertex, each with barycentric support `0.040849512`;
  - the remaining 3/5 have zero provider-`nose` support.
- `nose_base`:
  - both Item-8 landmarks have valid FLAME surface embeddings;
  - both embedded triangles are fully inside the broad FLAME `face` provider mask;
  - both have zero provider-`nose` support.
- Canonical embedded-point coordinates are geometrically structured and approximately bilateral for the nose-body anchors, with landmark 2 centered and forward; current evidence therefore does not support a claim that these anchors were mapped to an unrelated part of the FLAME surface.
- Bounded diagnosis:
  `PROVIDER_NOSE_MASK_AND_ITEM8_MEDIAPIPE_NOSE_BODY_BASE_ARE_NOT_SEMANTICALLY_EQUIVALENT`.
- This diagnosis does NOT yet prove whether the difference originates from provider-mask design intent, landmark semantic definition, or another correspondence convention.
- The FLAME provider `nose` mask MUST NOT be relabelled as Item-8 `nose_body` or `nose_base`.
- No fabricated/guessed FLAME vertex indices are permitted.
- Verified finer 3D `nose_body` / `nose_base` mapping remains unresolved.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H2_NOSE_SPATIAL_ENVELOPE_DIAGNOSIS_2026_08_27

- [~] **H2 — Verified 3D Facial-Region Mapping remains ACTIVE.**
- Persistent evidence:
  `ITEM8_H2_PROVIDER_NOSE_SPATIAL_ENVELOPE_AUDIT.json`
- Evidence SHA256:
  `58206d521ade744820c00b35c442dd91d5f90bdcdefe08240e2b5bc1ca753bf6`.
- FLAME provider `nose` mask:
  - 379 unique vertices;
  - bbox min = `(-0.024391672, -0.022403485, 0.039551163)`;
  - bbox max = `(0.024238879, 0.022048222, 0.075088655)`;
  - centroid = `(0.000120103, -0.008946480, 0.058531186)`.
- Item-8 `nose_bridge`:
  - 3/4 embedded points lie inside the provider nose bbox;
  - landmark 168 lies only `0.001430251` above the provider Y maximum;
  - nearest provider-nose vertex distances remain small (`0.000262924` to `0.002220987`, except the same order for the remaining points).
- Item-8 `nose_body`:
  - landmarks 129 and 358 lie inside the provider nose bbox;
  - landmarks 98, 2 and 327 are outside only on the inferior Y axis by approximately `0.000139425`, `0.001169578`, and `0.000226845`;
  - their X and Z coordinates remain inside the provider nose bbox.
- Item-8 `nose_base`:
  - landmarks 2 and 326 are outside only on the inferior Y axis by approximately `0.001169578` and `0.001091537`;
  - both remain inside the provider nose bbox on X and Z.
- The current spatial evidence does NOT support a claim that the problematic nose-body/base anchors map to an unrelated FLAME surface area.
- Bounded interpretation:
  `ITEM8_NOSE_BODY_BASE_ANCHORS_LIE_AT_OR_JUST_BELOW_PROVIDER_NOSE_INFERIOR_BOUNDARY`.
- This strengthens, but does not prove, the hypothesis that the FLAME provider `nose` mask uses a narrower inferior/base semantic boundary than the Item-8 MediaPipe nose grouping.
- Spatial proximity/envelope membership is NOT semantic ground truth and MUST NOT be used to invent new vertex indices.
- No new mapping or segmentation was created.
- Verified dense `nose_body` / `nose_base` mapping remains unresolved.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H2_NOSE_TOPOLOGICAL_BOUNDARY_DIAGNOSIS_2026_08_27

- [~] **H2 — Verified 3D Facial-Region Mapping remains ACTIVE.**
- Persistent evidence:
  `ITEM8_H2_PROVIDER_NOSE_TOPOLOGICAL_BOUNDARY_AUDIT.json`
- Evidence SHA256:
  `579e8736db8c8eb50654b809dc31aa9aca6f13d05282b165dbc72cae6ae65816`.
- FLAME provider `nose` mask contains 379 unique vertices and 38 topological boundary vertices.
- Item-8 `nose_bridge` anchors:
  - all 4 embedded triangles have minimum graph distance `0` to the provider nose mask;
  - 3/4 triangles are fully inside the mask;
  - landmark 168 straddles the mask boundary with barycentric nose support `0.521323160`.
- Item-8 `nose_body` anchors:
  - landmarks 129 and 358 directly straddle the provider nose-mask boundary (`min graph distance = 0`);
  - landmarks 98, 2 and 327 are immediately adjacent to the provider nose mask (`min graph distance = 1`);
  - no evaluated nose-body anchor is topologically remote from the provider nose region.
- Item-8 `nose_base` anchors:
  - landmarks 2 and 326 are both immediately adjacent to the provider nose mask (`min graph distance = 1`);
  - neither is topologically remote from the provider nose region.
- Combined with the spatial-envelope audit, current evidence is consistent with a narrow provider-mask inferior boundary rather than a gross MediaPipe-to-FLAME correspondence failure.
- Bounded diagnosis:
  `ITEM8_NOSE_BODY_BASE_ANCHORS_ARE_ON_OR_IMMEDIATELY_ADJACENT_TO_PROVIDER_NOSE_BOUNDARY`.
- This remains a proximity/topology diagnosis only; graph distance does NOT establish semantic ground truth.
- One-hop neighboring vertices MUST NOT be automatically promoted into `nose_body` or `nose_base`.
- No new mapping or segmentation was created.
- Verified dense `nose_body` / `nose_base` semantic mapping remains unresolved.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H2_FINER_NOSE_MAPPING_SOURCE_AUDIT_2026_08_27

- [~] **H2 — Verified 3D Facial-Region Mapping remains ACTIVE.**
- Persistent evidence: `ITEM8_H2_FINER_NOSE_MAPPING_SOURCE_AUDIT.json`.
- Evidence SHA256: `146389cfefdd278210a84b56ceefa5aa2e1d6c892a237095f5b7b6f43dab573a`.
- Audited ATLAS repo, private FLAME spike assets, persistent Phase 8.10 evidence and bounded public references.
- The verified provider asset exposes broad `nose`, but no separate authoritative `nose_body` or `nose_base` dense vertex mask was found in the audited sources.
- Public reference implementations corroborate `FLAME_masks.pkl` as a FLAME vertex-mask asset used with FLAME 2023, but the reviewed material does not provide the Item-8 finer `nose_body` / `nose_base` partition.
- This is bounded negative evidence; it does NOT prove that no such mapping exists anywhere.
- Provider `nose` MUST NOT be relabelled as `nose_body` or `nose_base`.
- Spatial/topological proximity MUST NOT be used to promote neighboring vertices into those semantic classes.
- No new mapping or segmentation was created.
- Next permitted H2 route under the locked plan:
  `SEPARATELY_VERIFIABLE_ATLAS_MAPPING_CONTRACT`.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H2_MAPPING_CONTRACT_STANDARD_LOCKED_2026_08_27

- [x] User approved the final H2 separately-verifiable mapping-contract standard.
- Persistent evidence:
  `ITEM8_H2_SEPARATELY_VERIFIABLE_MAPPING_CONTRACT_STANDARD.json`
- Evidence SHA256:
  `7b971f0eedc808b67e6818e6fe85cbe4fc8fbe36c7c5c5ac53d329cbaf144904`.
- LOCKED criteria:
  1. frozen verified Item-8 source anchors;
  2. existing verified MediaPipe-to-FLAME barycentric embedding only;
  3. deterministic derivation with all parameters predeclared before output inspection;
  4. provider masks preserved as independent reference evidence;
  5. explicit semantic-leakage measurement against distinct provider regions;
  6. anatomical/bilateral sanity checks are post-hoc validation only;
  7. predeclared sensitivity/stability audit is mandatory;
  8. restricted claim: `ATLAS-derived, separately verified finer FLAME-topology semantic mapping`;
  9. evidence-first persistent reproducibility before production integration;
  10. FLAME licensing/redistribution remains separate and unresolved until Item 13 audit.
- LOCKED anti-circularity gate:
  the H2 mapping MUST NOT be designed, selected, tuned or modified to improve,
  hide or eliminate the existing H1 `nose_body` 3/3 held-out degradation.
  Mapping rule and parameters must be frozen independently before H1 outcome evaluation.
- No vertex mapping or segmentation has yet been created under this contract.
- H2 remains ACTIVE.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H2_DERIVATION_RULE_FROZEN_2026_08_27

- [x] H2 separately-verifiable finer-mapping derivation rule frozen BEFORE mapping output generation.
- Persistent rule artifact:
  `ITEM8_H2_FINER_MAPPING_DERIVATION_RULE_FROZEN.json`
- Rule SHA256:
  `25b76337c25661de0c7c1734b1037bb82af01f700c3b6c5e2c4b79abb33b2ce0`.
- Frozen derivation:
  `BARYCENTRIC_ANCHOR_SUPPORT_TRIANGLE_UNION`.
- Only existing frozen Item-8 semantic anchors and their existing verified MediaPipe-to-FLAME barycentric embeddings may be used.
- For each anchor, exactly its existing FLAME support triangle is retained.
- For each semantic group, the topology footprint is the sorted unique union of those support-triangle vertices.
- Prohibited:
  radius expansion, graph-hop expansion, nearest-neighbor expansion, bbox expansion,
  provider-mask expansion, guessed vertices, manual vertex addition/removal and tunable thresholds.
- Provider masks remain independent post-derivation reference evidence only.
- Permitted claim is restricted to:
  `ATLAS-derived barycentric-anchor-supported FLAME topology footprint`.
- This mapping MUST NOT be called a dense anatomical region, provider-authored region or anatomical ground truth.
- The rule has no free numeric hyperparameter.
- Stability validation remains mandatory after output generation.
- Anti-circularity remains locked: existing H1 `nose_body` 3/3 outcome may not select or tune mapping membership.
- No mapping output was generated in this freeze step.
- FLAME-derived index redistribution remains unresolved; generated mapping must remain in controlled private evidence pending Item 13.
- H2 remains ACTIVE.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H2_EXACT_ANCHOR_TOPOLOGY_FOOTPRINT_GENERATED_2026_08_27

- [~] **H2 — Verified 3D Facial-Region Mapping remains ACTIVE.**
- Frozen-rule mapping artifact:
  `ITEM8_H2_EXACT_BARYCENTRIC_ANCHOR_TOPOLOGY_FOOTPRINT.json`
- Evidence SHA256:
  `e3d1744b85c34167100f0f8b87c3cf6f4528da7789c8e2a616438cc8baec7580`.
- Mapping was generated exactly from the previously frozen
  `BARYCENTRIC_ANCHOR_SUPPORT_TRIANGLE_UNION` rule.
- No tunable threshold, graph-hop expansion, radius expansion, nearest-neighbor expansion,
  provider-mask expansion or manual vertex editing was used.
- H1 outcome was not evaluated or used during membership generation.
- Exact generated footprints:
  - `nose_bridge`: 4 frozen anchors -> 12 unique FLAME support vertices;
    provider `nose` overlap = `10/12`;
  - `nose_body`: 5 frozen anchors -> 13 unique FLAME support vertices;
    provider `nose` overlap = `2/13`;
  - `nose_base`: 2 frozen anchors -> 6 unique FLAME support vertices;
    provider `nose` overlap = `0/6`.
- Semantic leakage audit at generation time:
  - `lips`: 0 overlap for all three footprints;
  - `left_eye_region`: 0;
  - `right_eye_region`: 0;
  - `left_ear`: 0;
  - `right_ear`: 0;
  - `neck`: 0.
- Therefore no overlap with the audited clearly distinct provider semantic regions was observed.
- Permitted claim remains strictly:
  `ATLAS-derived barycentric-anchor-supported FLAME topology footprint`.
- These footprints are NOT claimed to be dense anatomical regions,
  provider-authored finer regions or anatomical ground truth.
- Post-generation tuning remains prohibited.
- Production integration remains unauthorized pending later validation and licensing review.
- Next H2 validation:
  deterministic rerun reproducibility and same-triangle barycentric perturbation stability.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H2_DETERMINISTIC_RERUN_REPRODUCIBILITY_VERIFIED_2026_08_27

- [x] H2 frozen finer-mapping rule deterministic rerun reproducibility VERIFIED.
- Persistent evidence:
  `ITEM8_H2_DETERMINISTIC_RERUN_REPRODUCIBILITY.json`
- Evidence SHA256:
  `ef70a7001b25a804bf97caab16e47dba5465931cb6e2fa0582f255d984953ee5`.
- Reference mapping:
  `ITEM8_H2_EXACT_BARYCENTRIC_ANCHOR_TOPOLOGY_FOOTPRINT.json`
  SHA256 `e3d1744b85c34167100f0f8b87c3cf6f4528da7789c8e2a616438cc8baec7580`.
- A second derivation was independently reconstructed from the frozen Item-8 anchor IDs,
  existing MediaPipe-to-FLAME barycentric embedding, real FLAME topology and provider masks.
- Exact equality was verified for all three target regions:
  `nose_bridge`, `nose_body`, `nose_base`.
- Exact verified dimensions:
  frozen anchor IDs, embedding face indices, barycentric weights, support triangles,
  sorted unique footprint vertices, provider-nose overlap vertices and all audited
  distinct-provider overlap vertices.
- No H1 metric was evaluated and no mapping tuning was performed.
- Deterministic rerun reproducibility is therefore established for the frozen derivation.
- This does NOT establish anatomical ground truth or provider-authored finer segmentation.
- Same-triangle barycentric perturbation stability remains the next H2 validation.
- Post-generation tuning remains prohibited.
- H2 remains ACTIVE.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H2_BARYCENTRIC_PERTURBATION_PROTOCOL_FROZEN_2026_08_27

- [x] H2 same-triangle barycentric perturbation stability protocol frozen BEFORE execution.
- Persistent protocol:
  `ITEM8_H2_BARYCENTRIC_PERTURBATION_STABILITY_PROTOCOL_FROZEN.json`
- Protocol SHA256:
  `817967cf01c653d9862f26136dc8d6b69f8f7c57ad5e18316e0b79ba5b140bda`.
- Frozen perturbation:
  `w' = (1-alpha) w + alpha (1/3,1/3,1/3)`.
- Frozen alpha levels:
  `0.01`, `0.05`, `0.10`.
- Perturbations remain inside the same source triangle by construction;
  face-index reassignment is prohibited.
- Anchor sets, source faces and mapping membership may not be changed or tuned.
- Required result:
  every anchor preserves its source face/triangle and every target region preserves
  exactly the same topology footprint and provider-overlap sets at all three alpha levels.
- Floating-point sum-to-one tolerance `1e-12` is validation-only and cannot affect membership.
- H1 metrics are prohibited from this stability test.
- This test will establish only same-triangle barycentric-coordinate stability;
  it cannot establish dense anatomical ground truth or stability under face reassignment.
- Perturbation execution has NOT occurred in this step.
- H2 remains ACTIVE.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H2_BARYCENTRIC_PERTURBATION_STABILITY_VERIFIED_2026_08_27

- [x] H2 frozen same-triangle barycentric perturbation stability VERIFIED.
- Persistent evidence:
  `ITEM8_H2_BARYCENTRIC_PERTURBATION_STABILITY_RESULT.json`
- Evidence SHA256:
  `f027318ded10fd0e210fd7b9bcaa91f37480c039a2871002fc8f436284f5f8c8`.
- Frozen perturbation protocol was executed unchanged at alpha values
  `0.01`, `0.05`, `0.10`.
- All perturbed barycentric weights remained finite, non-negative and summed to one
  within the predeclared numerical tolerance.
- All source face indices and support triangles remained unchanged.
- For `nose_bridge`, `nose_body`, and `nose_base`, the sorted topology footprint,
  provider-nose overlap and all audited distinct-provider overlap sets remained
  exactly identical at every frozen alpha level.
- Therefore same-triangle barycentric-coordinate stability of the frozen
  anchor-supported topology footprint is VERIFIED.
- This does NOT test stability under face-index reassignment and does NOT establish
  dense anatomical ground truth or provider-authored finer segmentation.
- H1 metrics were not evaluated and mapping membership was not tuned.
- H2 remains ACTIVE.
- Next H2 stage: apply the verified anchor-supported 3D footprints to the already
  existing canonical identity/expression/pose evidence without changing membership.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H2_CANONICAL_3D_REGION_MEASUREMENT_PROTOCOL_FROZEN_2026_08_27

- [x] H2 canonical 3D region measurement protocol frozen before measurement.
- Persistent protocol:
  `ITEM8_H2_CANONICAL_3D_REGION_MEASUREMENT_PROTOCOL_FROZEN.json`
- Protocol SHA256:
  `4a9fd55b0f3e47a7ce3a3498e83d752e5a313595994f8fef97656537a4aee285`.
- Frozen regions:
  `nose_bridge`, `nose_body`, `nose_base`.
- Region membership comes only from the already frozen barycentric-anchor topology footprint.
- Canonical geometry is evaluated in unposed FLAME vertex space using
  `AtlasPortraitFlameBlendshapeEvaluator.evaluate`.
- No root pose, camera, kinematic transform, LBS, or image normalization is allowed.
- Held-out identity comparison:
  baseline vs candidate identity, neutral expression, zero pose.
- Expression comparison:
  locked identity, neutral expression vs persisted smile expression, zero pose.
- Raw FLAME coordinate displacement is primary.
- Bbox-diagonal normalization is secondary.
- No millimetre claim is permitted.
- Mapping membership may not be changed after seeing measurements.
- No acceptance threshold is introduced.
- Measurement has NOT executed in this step.
- H2 remains ACTIVE.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H2_CANONICAL_3D_REGION_MEASUREMENT_COMPLETE_2026_08_27

- [x] Frozen H2 canonical 3D region measurement executed successfully.
- Persistent evidence:
  `ITEM8_H2_CANONICAL_3D_REGION_MEASUREMENT_RESULT.json`
- Evidence SHA256:
  `c246ab54ddf7ecd965b8801d868f815f3014b04f7e3440f0ad22c193f9f655c9`.
- Coordinate space:
  FLAME canonical unposed vertex space.
- No root pose, camera, kinematic transform, LBS or image-coordinate normalization was applied.
- Frozen mapping membership was not modified.
- Held-out identity-only geometry was measured for:
  `held_out_front`, `held_out_turn_left`, `held_out_turn_right`.
- Expression-only geometry was measured with the persisted identity held exactly fixed.
- Raw FLAME canonical-coordinate measurements:
  - `held_out_front` / `nose_bridge`: mean `0.00110464382359`, RMS `0.00113633337273`, max `0.00154811355775`.
  - `held_out_front` / `nose_body`: mean `0.00203260142855`, RMS `0.00205797307108`, max `0.00273015888716`.
  - `held_out_front` / `nose_base`: mean `0.00186030002716`, RMS `0.00186138621504`, max `0.00196177231558`.
  - `held_out_turn_left` / `nose_bridge`: mean `0.00192002630073`, RMS `0.00193124913931`, max `0.00228990050264`.
  - `held_out_turn_left` / `nose_body`: mean `0.00248787114811`, RMS `0.00249267333356`, max `0.00272107993733`.
  - `held_out_turn_left` / `nose_base`: mean `0.00265751899861`, RMS `0.00265820821102`, max `0.00272107993733`.
  - `held_out_turn_right` / `nose_bridge`: mean `0.00121404750445`, RMS `0.00122606148586`, max `0.00158354651723`.
  - `held_out_turn_right` / `nose_body`: mean `0.00179900763291`, RMS `0.0018030673079`, max `0.00200174547587`.
  - `held_out_turn_right` / `nose_base`: mean `0.00190733524233`, RMS `0.00190828439557`, max `0.00200174547587`.
  - `expression_locked_identity` / `nose_bridge`: mean `0.0002314670621`, RMS `0.000250315150677`, max `0.000417232203628`.
  - `expression_locked_identity` / `nose_body`: mean `0.00208669086366`, RMS `0.00216703273231`, max `0.00289951861026`.
  - `expression_locked_identity` / `nose_base`: mean `0.00118981823044`, RMS `0.00119979588446`, max `0.00143380447343`.
- Bbox-diagonal-normalized measurements are preserved in the machine-readable evidence.
- No millimetre/metric-ground-truth claim is made.
- No acceptance threshold was applied.
- H1 2D outcomes were not used to tune mapping or measurement.
- This step records measurement only; interpretation and H2 closure remain pending.
- H2 remains ACTIVE.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H2_BOUNDED_3D_MAPPING_INTERPRETATION_2026_08_27

- [x] H2 bounded canonical-3D mapping interpretation completed.
- Persistent evidence:
  `ITEM8_H2_BOUNDED_3D_MAPPING_INTERPRETATION.json`
- Evidence SHA256:
  `1595a2e26e81fbe8390d3513f5c73234511a62a09e1eeb890222102dbea11377`.
- Verified on the frozen `nose_body` anchor-supported FLAME topology footprint:
  candidate-vs-baseline identity produces non-zero canonical model-space displacement
  in all three held-out cases.
- Mean/BBox displacement:
  - `held_out_front`: `0.00472730861366`;
  - `held_out_turn_left`: `0.00552368544455`;
  - `held_out_turn_right`: `0.00420085836729`.
- Therefore the H1 `nose_body 3/3` observation-space effect cannot be explained
  by analytic camera/reprojection variation alone; canonical identity-geometry change exists.
- This does NOT prove true metric/anatomical 3D degradation because there is no independent
  metric 3D ground truth or directional correctness target for the fine footprint.
- With identity held fixed, expression also changes the same `nose_body` footprint:
  mean/BBox `0.00465121700525`.
- That expression responsiveness is NOT by itself an identity-expression leakage claim;
  controlled separation stress belongs to H3.
- H2 mapping claim remains restricted to:
  `ATLAS-derived barycentric-anchor-supported FLAME topology footprint`.
- H2 is not officially closed yet.
- Next locked step:
  H2 evidence manifest / integrity closure.
- H3 has NOT started.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H2_EVIDENCE_MANIFEST_INTEGRITY_CLOSED_2026_08_27

- [x] H2 evidence manifest / integrity closure VERIFIED.
- Existing `SHA256SUMS.txt` pre-H2 state was verified before mutation:
  `14/14` existing entries matched their files.
- Added `16` successful H2 evidence artifacts:
  - `H2_FLAME_MASK_STRUCTURE_AUDIT_V2.txt`;
  - `H2_FLAME_MASK_GEOMETRY_SANITY_AUDIT.txt`;
  - all `14` successful `ITEM8_H2_*` artifacts through
    `ITEM8_H2_BOUNDED_3D_MAPPING_INTERPRETATION.json`.
- The failed first FLAME mask structure audit was NOT manifested as successful evidence.
- Post-update manifest:
  `30/30` entries hash-verified.
- `SHA256SUMS.txt` SHA256:
  `9dad1831387b3ba42fb048ca71c8bbeaa1b3a2761087c8af93c121a38a4983aa`.
- H2 evidence integrity chain is complete for the currently successful H2 evidence set.
- H2 is NOT officially closed by this integrity step alone.
- Next locked step:
  `H2 official closure`.
- H3 has NOT started.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H2_OFFICIALLY_CLOSED_2026_08_27

- [x] **H2 — Verified 3D Facial-Region Mapping OFFICIALLY CLOSED.**
- Closure classification:
  `BOUNDED_VERIFIED_COMPLETE`.
- Closure evidence:
  `ITEM8_H2_OFFICIAL_CLOSURE.json`
- Closure SHA256:
  `f5ef03ba51c1c2713ab98f4d667e2546bc06bd7613a292ed59e2a96327a29cf6`.
- Verified mapping claim is restricted to:
  `ATLAS-derived barycentric-anchor-supported FLAME topology footprint`.
- Verified target footprints:
  `nose_bridge`, `nose_body`, `nose_base`.
- Mapping membership was frozen before downstream measurement.
- Deterministic rerun reproducibility verified exactly.
- Same-triangle barycentric perturbation stability verified at the frozen
  `0.01`, `0.05`, `0.10` levels.
- No overlap was observed with the audited distinct provider semantic masks
  `lips`, eye regions, ears, or neck.
- Canonical unposed FLAME model-space measurement confirms non-zero
  candidate-vs-baseline identity geometry change on `nose_body`
  in all three held-out cases.
- Therefore H1's `nose_body 3/3` observation-space effect cannot be attributed
  to analytic camera/reprojection variation alone.
- This H2 closure does NOT establish:
  dense anatomical fine-region ground truth,
  provider-authored finer mapping,
  metric 3D anatomical degradation,
  commercial acceptability,
  complete identity/expression separation,
  Phase 8 GO/LOCK,
  or Phase 9 authorization.
- Evidence manifest after closure:
  `31/31` hash-verified.
- `SHA256SUMS.txt` SHA256:
  `caa8d243e0e9afd47b9f17c1c2829483506c6dc93c218dc900a81c09246b006b`.
- **NEXT LOCKED STEP: H3 — Counterfactual Separation Stress.**
- H3 has NOT started.
- H4 has NOT started.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H3_COUNTERFACTUAL_SEPARATION_PROTOCOL_FROZEN_2026_08_27

- [~] **H3 — Counterfactual Separation Stress ACTIVE.**
- H3 source/state audit completed before protocol definition.
- Counterfactual protocol is now frozen before experiment execution.
- Persistent protocol:
  `ITEM8_H3_COUNTERFACTUAL_SEPARATION_PROTOCOL_FROZEN.json`
- Protocol SHA256:
  `02cbe7847941a5ca83a7ed805dcaa3588d717dd0ac5d49a0c7ad9fb5883f5dad`.
- No new nuisance state was invented:
  persisted baseline/candidate pose, expression and camera states are reused.
- Pose-only branch:
  identity fixed within each control, expression neutral, camera excluded.
- Expression-only branch:
  locked identity fixed; neutral vs persisted smile expression is evaluated
  independently at both persisted smile baseline and candidate pose controls.
- Camera-only branch:
  each held-out baseline/candidate geometry control is held fixed while only
  the persisted baseline/candidate weak-perspective camera state changes.
- Canonical identity parameter mutation is prohibited.
- Identity-only canonical geometry must remain exactly unchanged under
  nuisance counterfactuals.
- No numeric drift tolerance or commercial acceptance threshold was invented.
- H1 `nose_body 3/3` results were not used to tune H3 states or protocol.
- H2 frozen semantic-region membership remains unchanged.
- Evidence manifest after protocol freeze:
  `32/32` hash-verified.
- `SHA256SUMS.txt` SHA256:
  `854decf9fb8b71cb90b780cdd129811bf66365bb36530ba20aaf15077a8bedd3`.
- Next locked execution:
  `H3 pose-only counterfactual stress`.
- H4 has NOT started.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H3_POSE_ONLY_COUNTERFACTUAL_STRESS_COMPLETE_2026_08_27

- [x] H3 pose-only counterfactual stress completed successfully.
- Persistent evidence:
  `ITEM8_H3_POSE_ONLY_COUNTERFACTUAL_STRESS_RESULT.json`
- Evidence SHA256:
  `ecff81fdaed378c50ebb2f9c7ba8f54bc56e28fd033223b5836187bd7b4c65ca`.
- Frozen H3 protocol was unchanged.
- Existing persisted baseline/candidate root-pose states only were used.
- Baseline and candidate identities were tested separately as fixed controls.
- Expression remained neutral; camera was excluded.
- Identity parameter vectors remained exactly unchanged.
- Identity-only canonical FLAME geometry remained exactly unchanged.
- Pose changed posed geometry as expected; frozen H2 region motion was measured.
- Regional posed motion is not classified as identity drift.
- No metric-mm or commercial-acceptability claim is made.
- Evidence manifest:
  `33/33` hash-verified.
- `SHA256SUMS.txt` SHA256:
  `1cf24a41cfb9682527610a967dab70ff988df6ea84c818f53ecad8b8ee2cbf7e`.
- Next locked step:
  `H3 expression-only counterfactual stress`.
- H3 remains active.
- H4 has NOT started.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H3_EXPRESSION_ONLY_COUNTERFACTUAL_STRESS_COMPLETE_2026_08_27

- [x] H3 expression-only counterfactual stress completed successfully.
- Persistent evidence:
  `ITEM8_H3_EXPRESSION_ONLY_COUNTERFACTUAL_STRESS_RESULT.json`
- Evidence SHA256:
  `c19a765af6c36faeb4518861c7cd9fadc5e592d2cfd8283563d8d20131661cff`.
- Frozen H3 protocol was not modified.
- Locked identity remained exactly unchanged.
- Neutral vs persisted smile expression was evaluated independently at
  `smile_baseline_pose` and `smile_candidate_pose`.
- Pose remained fixed within each expression pair.
- Existing FLAME geometry chain was reused only through image-coordinate
  normalization; landmark evaluation, camera solving and projection were excluded.
- No new expression or pose state was generated.
- Identity-only canonical FLAME geometry remained exactly unchanged.
- Frozen H2 `nose_bridge`, `nose_body`, and `nose_base` region motion was measured.
- Non-zero expression-region motion is not classified as identity drift.
- No identity-expression leakage, metric-mm, or commercial-acceptability claim
  is made from this branch alone.
- Evidence manifest:
  `34/34` hash-verified.
- `SHA256SUMS.txt` SHA256:
  `03bc1b2a3fe91a278a868a9335021775c1f6672a0acd9223eb6bb88cd9cb01c4`.
- Next locked step:
  `H3 camera-only counterfactual stress`.
- H3 remains active.
- H4 has NOT started.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H3_CAMERA_ONLY_COUNTERFACTUAL_STRESS_COMPLETE_2026_08_27

- [x] H3 camera-only counterfactual stress completed successfully.
- Persistent evidence:
  `ITEM8_H3_CAMERA_ONLY_COUNTERFACTUAL_STRESS_RESULT.json`
- Evidence SHA256:
  `f78a9ed291956c0dc6fa827797d087a345877bd2c6ffc748eb7291c50236c02d`.
- Frozen H3 protocol was not modified.
- Three held-out persisted baseline/candidate weak-perspective camera pairs
  were reused; no new camera state was generated or optimized.
- For each held-out case, baseline geometry and candidate geometry were
  evaluated separately as fixed controls.
- Within each camera pair identity, root pose, neutral expression, and
  3D geometry remained fixed.
- Existing ATLAS weak-perspective projection contract was used:
  `u = scale*x + tx`, `v = scale*y + ty`.
- Identity parameter vectors remained exactly unchanged.
- Three-dimensional geometry remained exactly unchanged.
- Camera state changed only projected 2D coordinates as expected.
- Frozen H2 `nose_bridge`, `nose_body`, and `nose_base` projection shifts
  were measured in normalized image-coordinate units.
- Projection shift is not classified as canonical identity drift.
- No pixel, metric-mm, degradation, or commercial-acceptability claim is made.
- Evidence manifest:
  `35/35` hash-verified.
- `SHA256SUMS.txt` SHA256:
  `b4eaa3187e555a6cde489d5362586cdb876f2225f00fa191757c439275885677`.
- Next locked step:
  `H3 bounded interpretation`.
- H3 remains active and is not yet officially closed.
- H4 has NOT started.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H3_BOUNDED_COUNTERFACTUAL_SEPARATION_INTERPRETATION_COMPLETE_2026_08_27

- [x] H3 bounded counterfactual interpretation completed.
- Classification:
  `STRUCTURAL_COUNTERFACTUAL_SEPARATION_SUPPORTED_WITH_BOUNDED_CLAIMS`.
- Persistent evidence:
  `ITEM8_H3_BOUNDED_COUNTERFACTUAL_SEPARATION_INTERPRETATION.json`
- Evidence SHA256:
  `f10b07b5addd0e3dbdd6e1df9254e91dafa7029a03189480348be8d8a6bf6fcb`.
- Pose-only:
  identity parameters and identity-only canonical geometry remained exact
  invariants while posed geometry changed.
- Expression-only:
  locked identity and identity-only canonical geometry remained exact
  invariants while expression-dependent geometry changed.
- Camera-only:
  identity and fixed 3D geometry remained exact invariants while only
  weak-perspective 2D projection changed.
- Non-zero pose/expression regional movement is not classified as identity drift.
- Expression response was measured at both persisted pose controls; similarity
  is descriptive only and no acceptance threshold was invented.
- H3 supports bounded structural nuisance separation under frozen-identity
  counterfactuals.
- H3 does NOT globally prove absence of leakage under arbitrary future or
  unconstrained identity-refitting optimizers.
- No biometric, metric-mm, dense-anatomy, or commercial-acceptability claim.
- Phase 8 GO/LOCK is NOT established.
- Phase 9 remains NOT AUTHORIZED.
- Evidence manifest:
  `36/36` hash-verified.
- `SHA256SUMS.txt` SHA256:
  `307e313b9641c162078207970cbf1421b4ab458306be94cfc234485a697c8bd7`.
- Next locked step:
  `H3 evidence integrity and official closure`.
- H4 has NOT started.

## PHASE8_10_ITEM8_H3_OFFICIALLY_CLOSED_2026_08_27

- [x] **H3 — Counterfactual Separation Stress OFFICIALLY CLOSED.**
- Closure classification:
  `BOUNDED_VERIFIED_COMPLETE`.
- Persistent closure evidence:
  `ITEM8_H3_OFFICIAL_CLOSURE.json`
- Closure SHA256:
  `8e90de785f500ee3a5d0d3be0a4275b7e6787be2ce92d766f276ae6498abeeab`.
- Pose-only, expression-only, and camera-only branches are complete.
- Canonical identity parameters remained exact invariants across all H3
  counterfactual nuisance branches.
- Identity-only canonical geometry remained exact under pose and expression.
- Fixed 3D geometry remained exact under camera-only counterfactuals.
- H3 supports bounded structural nuisance separation for the tested
  ATLAS/FLAME forward-model paths.
- H3 does NOT globally prove absence of leakage under arbitrary future or
  unconstrained identity-refitting optimizers.
- No biometric, metric-mm, dense-anatomy, or commercial-acceptability claim.
- Evidence manifest:
  `37/37` hash-verified.
- `SHA256SUMS.txt` SHA256:
  `0e4b601528fe8682a3356deee7303f11390c4c89b47d56d0d0bd03f87a0998ea`.
- Next locked step:
  `H4 — Commercial-Health Acceptance Gate`.
- H4 has NOT started.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 8 GO/LOCK is NOT established.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H4_COMMERCIAL_HEALTH_ACCEPTANCE_PROTOCOL_FROZEN_2026_08_27

- [~] **H4 — Commercial-Health Acceptance Gate STARTED.**
- Decision protocol frozen before commercial-health classification.
- Persistent protocol:
  `ITEM8_H4_COMMERCIAL_HEALTH_ACCEPTANCE_PROTOCOL_FROZEN.json`
- Protocol SHA256:
  `f3cdb1a1001910f485e6d3a59881dce3ae85c250e01cb65058bdb97e072e8c6a`.
- Allowed final H4 / Item-8 decision classes:
  `PASS`, `BOUNDED_PASS`, `HOLD`.
- Commercial-health dimensions:
  likeness, cross-condition consistency, automation reliability.
- Locked blocker:
  unresolved customer-visible identity degradation prevents `PASS`.
- `21/21` regional improvement is NOT required.
- No numeric acceptance threshold, support score, or post-hoc success criterion
  has been introduced.
- Positive global metrics may NOT be treated as uniform regional proof.
- Non-zero FLAME model-space displacement may NOT automatically be called
  anatomical degradation.
- H3 structural separation may NOT be generalized to global absence of future
  optimizer leakage.
- Evidence manifest:
  `38/38` hash-verified.
- `SHA256SUMS.txt` SHA256:
  `da05c002f8d4d82485191241ce8b64caaa1f15f1f897c94c47c59b5548ae9d2f`.
- Next locked step:
  evaluate H1-H3 verified evidence against this frozen H4 gate.
- H4 decision has NOT yet been made.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 8 GO/LOCK remains undecided.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H4_COMMERCIAL_HEALTH_EVALUATION_BOUNDED_PASS_2026_08_27

- [x] H4 commercial-health evaluation completed against the frozen gate.
- H4 decision:
  `BOUNDED_PASS`.
- Persistent evidence:
  `ITEM8_H4_COMMERCIAL_HEALTH_EVALUATION.json`
- Evidence SHA256:
  `a8ccd5af2a8ffd44615f4b9faf35a740a04bbd1622b153871d8f50a28bd0506f`.
- `PASS` was not selected because verified residual regional pose regressions
  remain, including `nose_body` degradation in `3/3` held-out observation-space
  views.
- `HOLD` was not selected because current evidence does NOT establish verified
  customer-visible identity degradation, metric anatomical degradation, or a
  material Item-8 automation failure.
- H3 bounded structural pose/expression/camera separation remains verified.
- Likeness classification:
  `BOUNDED_RESIDUAL_RISK`.
- Cross-condition consistency:
  `BOUNDED_SUPPORTED`.
- Automation reliability:
  `BOUNDED_SUPPORTED`.
- `21/21` regional improvement is not required and uniform regional
  improvement remains NOT established.
- No numeric acceptance threshold or normalized support score was introduced.
- No dense-anatomy, metric-mm, biometric, or global optimizer-leakage claim.
- Evidence manifest:
  `39/39` hash-verified.
- `SHA256SUMS.txt` SHA256:
  `0349d986d3195ca30ed1e1159449a44e77f1fdb4717024e4cb7011a28c873707`.
- Next locked step:
  `H4 evidence integrity and official closure`.
- H4 is not yet officially closed.
- Item 8 is not yet officially closed.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 8 GO/LOCK remains undecided.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_ITEM8_H4_OFFICIALLY_CLOSED_BOUNDED_PASS_2026_08_27

- [x] **H4 — Commercial-Health Acceptance Gate OFFICIALLY CLOSED.**
- Closure classification:
  `BOUNDED_PASS`.
- Persistent closure evidence:
  `ITEM8_H4_OFFICIAL_CLOSURE.json`
- Closure SHA256:
  `3b98d3f9ea9612da9c32a77bac32cb1ab6a072ca113557635c2a323e0f5640be`.
- Likeness:
  `BOUNDED_RESIDUAL_RISK`.
- Cross-condition consistency:
  `BOUNDED_SUPPORTED`.
- Automation reliability:
  `BOUNDED_SUPPORTED`.
- Verified residual risk remains:
  `nose_body` observation-space degradation in `3/3` held-out views and
  non-uniform regional improvement.
- Unqualified `PASS` is therefore not supported.
- `HOLD` is also not supported because current evidence does NOT establish
  customer-visible identity degradation, metric anatomical degradation, or
  a material Item-8 consistency/automation blocker.
- H4 is therefore officially closed as `BOUNDED_PASS`.
- No numerical acceptance threshold or normalized support score was invented.
- No global optimizer-leakage, dense-anatomy, metric-mm, or biometric claim.
- Evidence manifest:
  `40/40` hash-verified.
- `SHA256SUMS.txt` SHA256:
  `659e47dd3388accba614aed72cb28f2904c88e12bfa550cc8969da42b6893038`.
- Next locked step:
  `Main Checklist Item 8 — official closure`.
- Item 8 is NOT yet officially closed by this H4 record.
- Phase 8 remains `ACTIVE / HOLD-BLOCKED`.
- Phase 8 GO/LOCK remains undecided.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_10_MAIN_CHECKLIST_ITEM8_OFFICIALLY_CLOSED_BOUNDED_PASS_2026_08_27

- [x] **Main Checklist Item 8 — Pose / Expression Separation OFFICIALLY CLOSED.**
- Final Item 8 classification:
  `BOUNDED_PASS`.
- Persistent closure evidence:
  `ITEM8_OFFICIAL_CLOSURE.json`
- Closure SHA256:
  `4c47666fab2920a65968b6c60594410b3f23f62f4981466ca5efc028035c4b69`.
- H1:
  `BOUNDED_DIAGNOSIS_COMPLETE`.
- H2:
  `BOUNDED_VERIFIED_COMPLETE`.
- H3:
  `BOUNDED_VERIFIED_COMPLETE`.
- H4:
  `BOUNDED_PASS`.
- Verified residual limitation:
  held-out regional pose quality is not uniform and `nose_body` degrades in
  `3/3` measured held-out observation-space views.
- Current evidence does NOT establish verified customer-visible identity
  degradation or metric anatomical degradation.
- Structural pose/expression/camera separation is supported under the tested
  frozen counterfactual conditions.
- An unqualified `PASS` would overstate the evidence; `HOLD` is not supported.
- Item 8 is therefore officially closed as `BOUNDED_PASS`.
- No `21/21` requirement, numeric acceptance threshold, normalized support
  score, dense-anatomy claim, metric-mm claim, biometric claim, or global
  optimizer-leakage claim was introduced.
- Evidence manifest:
  `41/41` hash-verified.
- `SHA256SUMS.txt` SHA256:
  `6e5a45b02652769739348c33108fc2e248568c248b909a92a6eff87ba54dcabf`.
- There is no remaining H1-H4 Item-8 health-closure work.
- Phase 8 itself is NOT closed by this record.
- Phase 8 GO/LOCK is NOT established.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.
- Before continuing, return to the authoritative Main Checklist and identify
  the exact next Item 9 subitem.



---

## PHASE8_REMAINING_ITEM9_15_MASTER_ACTION_PLAN_LOCKED_2026_08_27

### Status

**Main Checklist Items 9–15 — MASTER ACTION PLAN — USER APPROVED / LOCKED**

This plan is the authoritative remaining Phase 8 execution structure after the
official closure of Main Checklist Item 8 as `BOUNDED_PASS`.

The required execution order is:

`Item 9 regional geometry`
→ `Item 10 metric ground truth`
→ `Item 11 physical survival`
→ `Item 12 runtime / reproducibility`
→ `Item 13 commercial / legal / privacy`
→ `Item 14 three-class architecture comparison`
→ `Item 15 Phase 8 final GO / HOLD / REJECT + LOCK gate`

This plan does NOT authorize Phase 9.

Phase 9 may start only after explicit:

`PHASE 8 = GO + LOCK`

No later item may be silently skipped, merged away, or declared complete from
evidence belonging to another evaluation space.

---

# 9 — FACIAL REGION GEOMETRY QUALITY

## Purpose

Prevent positive global reprojection or aggregate scores from concealing
material local facial-geometry or likeness failures.

Evaluation spaces remain explicitly separate:

- 2D observation space;
- canonical model space;
- metric 3D ground-truth space;
- physical-output space.

A result in one space MUST NOT automatically be promoted into another.

Landmark error is not volumetric geometry accuracy.
Reprojection improvement is not likeness proof.

## 9.1 — Evaluation-Space & Claim Boundary

Establish and preserve explicit distinctions between:

- 2D observation-space evidence;
- canonical model-space evidence;
- metric 3D ground-truth evidence;
- physical-output evidence.

Required boundary rules:

- landmark fit != surface accuracy;
- 2D reprojection != metric 3D accuracy;
- canonical model-space displacement != anatomical millimetres;
- printability != identity preservation;
- aggregate improvement != uniform regional improvement.

## 9.2 — Semantic Region Mapping Audit

Every evaluated facial region must have an explicit mapping state:

- provider-verified;
- independently verified ATLAS-derived;
- anchor-supported only;
- unresolved / BLOCKED.

Required regions:

- jaw;
- chin;
- nose bridge;
- nose body;
- nose base / tip;
- left orbital region;
- right orbital region;
- left cheek / zygomatic region;
- right cheek / zygomatic region;
- upper lip;
- lower lip;
- perioral region;
- forehead;
- cranial / head envelope.

Existing Item 8 H2 mappings remain bounded exactly as previously verified.

An `ATLAS-derived barycentric-anchor-supported FLAME topology footprint`
MUST NOT be relabelled as:

- dense anatomical segmentation;
- provider-authored region;
- anatomical ground truth.

No fabricated or guessed FLAME vertex indices are permitted.

## 9.3 — Jaw / Chin Quality

Evaluate where evidence permits:

- mandibular width;
- jaw angle;
- chin width;
- chin projection;
- chin vertical position;
- left/right contour;
- frontal consistency;
- profile consistency;
- cross-view stability.

## 9.4 — Nose Quality

Evaluate where evidence permits:

- bridge;
- dorsum / body;
- base;
- tip projection;
- alar width;
- nasolabial relation;
- profile projection;
- bilateral consistency;
- cross-view consistency.

The verified Item 8 residual limitation:

`nose_body observation-space degradation in 3/3 held-out pose views`

must remain explicitly traceable and may not disappear behind a global metric.

## 9.5 — Orbital / Eye-Socket Quality

Evaluate where evidence permits:

- inter-orbital relation;
- orbital rim;
- eye-socket form/depth;
- upper orbital contour;
- lower orbital contour;
- left/right asymmetry;
- eye-region to nose-bridge spatial relationship.

## 9.6 — Cheek / Midface Quality

Evaluate where evidence permits:

- zygomatic width;
- cheek prominence;
- anterior projection;
- midface fullness;
- cheek-to-nose transition;
- cheek-to-jaw transition;
- bilateral asymmetry.

## 9.7 — Mouth / Perioral Quality

Evaluate where evidence permits:

- mouth width;
- upper/lower lip relation;
- philtrum region;
- lip projection;
- commissures;
- neutral geometry versus expression deformation;
- nasolabial/perioral contamination.

Expression-dependent deformation MUST remain separate from canonical identity.

## 9.8 — Forehead / Cranial Quality

Evaluate where evidence permits:

- forehead height;
- forehead slope;
- frontal curvature;
- temple transition;
- cranial width;
- cranial depth;
- overall skull/head envelope.

## 9.9 — Head Ratios / Anthropometric Proportions

Evaluate appropriate subject-specific proportions such as:

- facial width / height;
- bizygomatic relation;
- bigonial relation;
- interocular relation;
- nose width / height;
- mouth width;
- upper/lower facial proportions;
- cranial-to-facial relationship.

Population anthropometric statistics may be used only as contextual/reference
evidence.

Population averages MUST NOT become identity targets.

## 9.10 — Cross-View Regional Consistency

For front / right / left and any later verified views:

- evaluate the same semantic region;
- preserve the same canonical identity;
- measure view-conditioned residuals;
- identify improvement/degradation consistency;
- isolate profile-sensitive regions.

## 9.11 — Cross-Region Compensation Audit

Explicitly test for:

- global improvement with local degradation;
- camera compensation;
- pose compensation;
- one facial region compensating for another;
- alignment concealing local failure.

Positive global held-out metrics MUST NOT establish uniform regional success.

## 9.12 — Regional Surface Error

When valid metric ground truth exists, evaluate appropriate raw metrics such as:

- point-to-surface distance;
- bidirectional/symmetric surface error where methodologically valid;
- mean;
- median;
- RMS;
- P95;
- maximum/outlier characterization;
- surface-normal discrepancy where meaningful.

No millimetre claim may be made without verified metric ground truth and units.

## 9.13 — Landmark-vs-Surface Agreement Audit

Explicitly identify:

- landmark success with surface failure;
- surface success with landmark failure;
- local landmark localization uncertainty;
- regional measurement-confidence limitations.

## 9.14 — Customer-Visible Likeness Risk

Separately evaluate whether mathematically bounded error is potentially
customer-visible or identity-bearing.

Critical attention includes:

- nose;
- jaw/chin;
- orbital region;
- cheek/midface;
- head silhouette/profile.

Academic geometric error MUST NOT automatically be equated with commercial
likeness acceptance.

## 9.15 — Item 9 Closure

Permitted final classifications:

- `PASS`;
- `BOUNDED_PASS`;
- `HOLD`;
- `REVISION_REQUIRED`.

No new arbitrary numerical threshold may be invented merely to close Item 9.

---

# 10 — METRIC GROUND-TRUTH LAYER

## Purpose

Establish a traceable physical/metric truth layer so anatomical or millimetre
accuracy claims cannot be inferred from photographs, normalized model space,
landmarks, or uncalibrated meshes.

## 10.1 — Ground-Truth Source Qualification

Every GT asset must record where available:

- acquisition technology;
- acquisition system / manufacturer;
- source;
- subject;
- units;
- resolution;
- calibration state;
- version/date;
- provenance;
- license/restrictions.

## 10.2 — Unit Certainty

Permitted unit states must be explicit.

Examples:

- mm;
- cm;
- m;
- unresolved.

Rules:

- no inferred units;
- no silent `×1000`;
- no scale assumption from typical head size;
- every unit transformation traceable.

## 10.3 — Scale Calibration

Where needed, establish:

- physical calibration object;
- known physical dimension;
- scanner calibration evidence;
- reconstruction scale factor;
- scale uncertainty.

## 10.4 — Coordinate-System Contract

Record explicitly:

- handedness;
- axis definitions;
- origin;
- orientation;
- canonical pose;
- reflection state.

No silent reflection or axis swap.

## 10.5 — Rigid Alignment

Separate:

- translation;
- rotation;
- scale.

Rigid and similarity alignment MUST NOT be silently conflated.

## 10.6 — Alignment Landmark Independence

Audit whether landmarks/features used for alignment also drive reported
evaluation results in a way that artificially reduces apparent error.

## 10.7 — Surface Correspondence

Explicitly document:

- closest-point assumptions;
- barycentric surface projection;
- correspondence direction;
- bidirectional evaluation where appropriate;
- topology-independent evaluation where required.

## 10.8 — Global Metric Error

Where GT supports it, measure appropriate global raw errors:

- mean;
- median;
- RMS;
- P95;
- maximum/outliers;
- surface coverage.

## 10.9 — Region-Wise Metric Error

Apply Item 9 verified semantic regions to metric GT only when correspondence and
region mapping are legitimately established.

## 10.10 — Measurement Uncertainty

Keep separate where evidence permits:

- GT acquisition/scanner uncertainty;
- landmark localization uncertainty;
- alignment uncertainty;
- prediction/reconstruction error.

## 10.11 — Repeat Capture / Repeatability

Where datasets permit:

- repeat acquisition;
- repeat reconstruction;
- intra-run repeatability;
- inter-run repeatability.

## 10.12 — Trueness vs Precision

These concepts MUST remain separate:

- trueness: closeness to reference truth;
- precision: consistency among repeated measurements.

Repeatability MUST NOT be reported as accuracy.

## 10.13 — Ground-Truth Leakage Audit

Explicitly record whether GT was:

- evaluation-only;
- used during fitting;
- used during tuning;
- used during model selection.

Evaluation GT must not silently become training/tuning evidence.

## 10.14 — Dataset Coverage

Record:

- subject count;
- views;
- expressions;
- capture conditions;
- demographic/phenotypic coverage where legitimately available and appropriate;
- missing regions;
- missing GT states.

Do not infer demographic attributes from images.

## 10.15 — Item 10 Closure

For every intended metric claim classify evidence as appropriate:

- supported;
- partial;
- missing;
- blocked.

Unresolved units or unqualified GT remain explicit blockers to millimetre claims.

---

# 11 — PHYSICAL REPRESENTATION GATE

## Purpose

Verify that canonical identity survives conversion into manufacturable ATLAS
outputs.

Digital geometry correctness and physical fabrication correctness are separate.

Required representation families remain:

- relief;
- bust;
- figurine head;
- story / kit component.

## 11.1 — Canonical-to-Physical Adapter Isolation

Conversion to physical representation must not silently modify the canonical
identity source.

Adapter-side transformations must be traceable.

## 11.2 — Scale Classes

Record actual physical head/output dimensions for each representation class.

## 11.3 — Minimum Feature Survival

Evaluate critical identity-bearing features where applicable:

- nose edges/profile;
- nose base;
- lips;
- eyelid/orbital boundaries;
- jaw edge;
- chin;
- ear structures where included.

## 11.4 — Relief Depth Transfer

Audit:

- canonical depth to relief-depth mapping;
- compression;
- clipping;
- flattening;
- exaggerated depth;
- local loss of identity-bearing shape.

## 11.5 — LoD Identity Preservation

Across LoD reduction evaluate preservation of:

- silhouette;
- profile;
- nose;
- jaw/chin;
- orbital/cheek;
- mouth.

Printability alone does not establish identity preservation.

## 11.6 — Topology / Manufacturability

Evaluate applicable production requirements:

- closed/manifold behavior;
- self-intersection;
- degenerate geometry;
- wall/feature thickness;
- unsupported structures;
- disconnected unintended geometry.

## 11.7 — Slicer Gate

A valid digital mesh MUST NOT automatically be considered slicer-valid.

## 11.8 — Printed Dimensional Fidelity

Where measurable, compare printed output against intended digital geometry.

## 11.9 — Physical Regional Preservation

Re-evaluate Item 9 critical facial regions after physical conversion where
practically observable/measurable.

## 11.10 — Orientation Sensitivity

Determine whether production orientation materially changes identity-bearing
geometry.

## 11.11 — Layer / Nozzle Sensitivity

Evaluate relevant manufacturing-profile changes where required.

## 11.12 — Material Sensitivity

Evaluate material/profile effects where they materially affect physical
identity-bearing features.

## 11.13 — Human Visual Inspection Protocol

Where subjective visual inspection is used, control as much as practical:

- front;
- 3/4;
- profile;
- viewing distance;
- illumination;
- camera/view comparison conditions.

Subjective inspection MUST remain identified as subjective evidence.

## 11.14 — Digital-vs-Physical Failure Classification

Failures must be attributed where evidence permits to:

- reconstruction;
- canonical-to-physical adapter;
- LoD;
- slicer;
- printer;
- material;
- post-processing.

## 11.15 — Item 11 Closure

Determine whether the selected canonical identity is sufficiently preserved
through the required physical-representation paths.

---

# 12 — RUNTIME / REPRODUCIBILITY

## Purpose

Prove that benchmark and production-relevant behavior can be recreated,
audited, and automated without hidden historical state.

## 12.1 — Exact Environment Capture

Record as applicable:

- OS;
- machine architecture;
- Python;
- package versions;
- frameworks;
- model version;
- model weights/checkpoints.

## 12.2 — Apple Silicon Native Path

Audit explicitly:

- CPU;
- MPS;
- fallback behavior;
- unsupported operations;
- platform-specific deviations.

## 12.3 — Cold-Start Runtime

Measure relevant end-to-end startup cost including model initialization/loading
where required.

## 12.4 — Warm Runtime

Measure repeat processing cost per image/subject/job where relevant.

## 12.5 — Stage-Wise Timing

Where applicable:

- preprocessing;
- landmarks/correspondence;
- fitting;
- detail reconstruction;
- evaluation;
- conversion/export.

## 12.6 — Memory

Record where relevant:

- peak RAM;
- model/checkpoint footprint;
- intermediate artifact footprint.

## 12.7 — Determinism

Same input + same declared environment/protocol should reproduce deterministic
stages exactly where mathematically intended.

## 12.8 — Seed Control

All stochastic components must expose and persist relevant seeds/state.

## 12.9 — Cross-Run Reproducibility

Repeat independent executions and compare outputs/results.

## 12.10 — Hardware Reproducibility

Where technically and commercially justified, evaluate cross-hardware
differences without weakening the Apple Silicon requirement.

## 12.11 — Dependency Reproducibility

Persist:

- package versions;
- model versions;
- model hashes;
- checkpoint hashes;
- critical auxiliary-asset hashes.

## 12.12 — Input Provenance

Benchmark and acceptance inputs require traceable identity and hashes where
permitted.

## 12.13 — Persistent Outputs

Critical evidence must include as appropriate:

- runner;
- machine-readable JSON;
- NPZ or equivalent numerical state;
- `PROVENANCE.md`;
- `SHA256SUMS.txt`;
- manifest verification.

Critical continuation state MUST NOT exist only under `/tmp`.

## 12.14 — Historical-vs-Reconstructed Run Boundary

These labels remain semantically distinct:

- exact historical result;
- exact historical rerun;
- reproducibility adaptation;
- reconstructed/recovered run.

A reconstructed run MUST NOT be relabelled as historical evidence.

## 12.15 — Failure Recovery

Interrupted or failed execution must not leave stale output that can be mistaken
for a successful fresh run.

Use explicit status/atomicity semantics where necessary.

## 12.16 — Automation Reliability

Evaluate multiple valid subjects/inputs without hidden manual repair steps.

Manual intervention must be recorded rather than hidden.

## 12.17 — Processing Cost

Measure relevant compute/time/resource cost.

Processing cost is subordinate to identity quality, physical suitability,
policy acceptability and reproducibility.

## 12.18 — Item 12 Closure

Close only after the required runtime and reproducibility chain for the selected
candidate(s) is persistent and auditable.

---

# 13 — COMMERCIAL / LEGAL / PRIVACY

## Purpose

Determine whether the selected technical architecture and its dependencies can
legitimately support commercial personalized-product processing.

This item is not a legal opinion.
It is the ATLAS engineering/policy evidence gate.

Reconstruction/personalization MUST NOT automatically be described as facial
recognition or biometric identification.

At the same time, face geometry, derived templates, coefficients, meshes and
associated metadata require explicit privacy/legal classification.

## 13.1 — Processing-Purpose Classification

Explicitly distinguish:

- personalized reconstruction/manufacturing;
- authentication;
- verification;
- identification;
- recognition.

ATLAS must not silently acquire identification/recognition functionality.

## 13.2 — Data-Class Inventory

Inventory applicable data classes:

- source photographs;
- video where used;
- landmarks;
- correspondence;
- canonical mesh;
- identity coefficients;
- expression coefficients;
- detail fields;
- embeddings/templates;
- derived measurements;
- customer/order metadata.

## 13.3 — Jurisdiction Matrix

At minimum evaluate requirements relevant to:

- European Union / Germany;
- France / CNIL guidance;
- United States federal + relevant state law;
- Japan / APPI-PPC framework;
- China / PIPL and applicable facial-information rules.

## 13.4 — Consent / Lawful-Basis Audit

Processing basis must be explicit for each relevant data class and purpose.

## 13.5 — Purpose Limitation

Order fulfilment/personalization and unrelated secondary uses remain separate.

## 13.6 — Data Minimization

Retain/process only what the legitimate workflow requires.

## 13.7 — Retention / Deletion

Raw source images and derived artifacts may require different retention rules.

Retention must be explicit rather than indefinite by default.

## 13.8 — Local vs Cloud Processing

Record where every relevant processing stage occurs.

## 13.9 — Cross-Border Transfer

Identify cross-border processing/storage dependencies where applicable.

## 13.10 — Encryption / Access Control

Establish appropriate controls for retained sensitive/personal data.

## 13.11 — User Rights / Deletion Propagation

Define deletion consequences across:

- raw images;
- landmarks;
- coefficients;
- canonical meshes;
- derived assets;
- caches;
- backups where applicable.

## 13.12 — Minor / Third-Person Images

Require separately defined handling rather than silently treating all submitted
faces identically.

## 13.13 — Training Reuse Prohibition / Consent Boundary

Customer content used for product fulfilment MUST NOT automatically be reused
for:

- model training;
- fine-tuning;
- dataset creation;
- unrelated product improvement.

Any secondary use requires its own legitimate basis/authorization.

## 13.14 — Biometric Identification Boundary

Identity-preserving geometry generation must remain technically and
semantically distinct from biometric recognition/identification functionality
unless a later separately authorized program explicitly addresses it.

## 13.15 — Model License

Audit the exact model/version license.

## 13.16 — Weight License

Model-code permission MUST NOT be assumed to cover model weights/checkpoints.

## 13.17 — Dataset License

Audit benchmark/training/evaluation dataset restrictions separately.

## 13.18 — Derived Asset / Redistribution

Audit restrictions relevant to:

- masks;
- embeddings;
- vertex mappings;
- derived provider assets;
- benchmark artifacts;
- redistributed indices/data.

## 13.19 — Attribution Requirements

Record and implement mandatory attribution obligations.

## 13.20 — Commercial-Use Compatibility

Every external dependency must have an explicit commercial-use state.

Historical/provisional selection does not equal commercial clearance.

For FLAME specifically, version-specific licensing must remain explicit.

## 13.21 — Third-Party Service Terms

Audit externally hosted APIs/services where relevant.

## 13.22 — Security / Breach Exposure

Evaluate retained data and external service attack/exposure surface.

## 13.23 — Accuracy & Marketing Claim Audit

Commercial statements MUST NOT exceed evidence.

Examples requiring evidence discipline:

- exact likeness;
- scan accuracy;
- metric accuracy;
- biometric;
- identity guaranteed.

## 13.24 — Documentation / Audit Trail

All critical commercial/legal/privacy conclusions must be persistent and
traceable to their source/version/date.

## 13.25 — Item 13 Closure

Each critical dependency/data path receives an evidence-grounded state such as:

- `ACCEPTABLE`;
- `CONDITIONAL`;
- `UNRESOLVED`;
- `BLOCKED`.

A prohibited or unresolved hard policy dependency cannot be overridden by strong
geometric performance.

---

# 14 — THREE-CLASS ARCHITECTURE COMPARISON

## Purpose

Perform the final fair comparison of all three mandatory Phase 8 architecture
classes without allowing a single aggregate score to conceal local,
physical, reproducibility, or policy failures.

Required architecture classes:

- `parametric_fixed_topology`;
- `direct_neural_dense`;
- `hybrid_canonical_detail`.

## 14.1 — Candidate Freeze

Freeze exact evaluated candidate implementations/versions before final
comparison.

## 14.2 — Same Input Evidence

Use equivalent input evidence wherever the architecture permits a fair
comparison.

Any architecture-specific evidence advantage/disadvantage must be explicit.

## 14.3 — Same Evaluation Protocol

Use common evaluation semantics wherever technically valid.

## 14.4 — Same Ground Truth

Use common GT for comparable measurements.

## 14.5 — Identity Preservation

Compare verified identity-preservation evidence.

## 14.6 — Multi-View Consistency

Compare cross-view consistency/generalization.

## 14.7 — Silhouette / Profile

Compare silhouette and profile evidence separately from interior-face fit.

## 14.8 — Facial Region Geometry

Consume Item 9 results.

## 14.9 — Metric Ground Truth

Consume Item 10 results.

## 14.10 — Expression Separation

Compare identity/expression separation.

## 14.11 — Pose / Camera Separation

Compare nuisance separation and compensation behavior.

## 14.12 — Topology Stability

Evaluate topology consistency and suitability.

## 14.13 — Correspondence Stability

Evaluate whether semantic/canonical correspondence remains stable enough for
downstream ATLAS use.

## 14.14 — Detail Preservation

Compare person-specific detail preservation without allowing detail to overwrite
canonical identity ownership.

## 14.15 — Physical Suitability

Consume Item 11 results.

## 14.16 — Runtime

Consume Item 12 timing evidence.

## 14.17 — Reproducibility

Consume Item 12 reproducibility evidence.

## 14.18 — Automation Reliability

Compare unattended/production-relevant behavior.

## 14.19 — Apple Silicon Viability

Compare current target-platform feasibility.

## 14.20 — License / Policy

Consume Item 13 license/policy evidence.

## 14.21 — Privacy / Data Processing

Consume Item 13 privacy-processing evidence.

## 14.22 — Processing Cost

Compare cost only after critical quality/policy/physical requirements.

## 14.23 — Failure Mode Matrix

For every architecture explicitly document:

- where it succeeds;
- where it degrades;
- where evidence is missing;
- known failure modes;
- failure detectability;
- recoverability where relevant.

## 14.24 — Evidence Coverage Matrix

Every required evaluation channel receives an explicit evidence state.

Existing Phase 8 semantics such as:

- `DIRECT`;
- `MEASURED`;
- `PARTIAL`;
- `MISSING`;

remain usable where applicable.

`BLOCKED` remains explicit where evidence/policy forbids progression.

## 14.25 — No Score Fabrication

Raw measurements MUST NOT be converted into invented `[0,1]` support values.

Any calibrated support policy requires independent justification and approval.

## 14.26 — Pareto Evaluation

Do not prematurely collapse:

- identity quality;
- regional geometry;
- physical suitability;
- topology;
- reproducibility;
- runtime;
- legal/policy;
- processing cost

into one opaque scalar.

## 14.27 — Candidate Eligibility

A candidate with a material unresolved critical blocker must not win merely
because its global geometric score is strongest.

## 14.28 — Architecture Recommendation

Final recommendation must be traceable to verified evidence and unresolved
limitations.

## 14.29 — Item 14 Closure

The three mandatory architecture classes must be compared sufficiently for the
Phase 8 final gate.

---

# 15 — PHASE 8 FINAL DECISION / PHASE 9 GATE

## Purpose

Produce the final Phase 8 decision without hiding blockers, fabricating support
or allowing premature Phase 9 implementation.

## 15.1 — Checklist Completeness

Audit Main Checklist Items 1–14.

## 15.2 — Evidence Manifest Integrity

Verify all critical final evidence and manifests.

## 15.3 — Outstanding Blocker Inventory

Every unresolved blocker remains visible.

No blocker may disappear merely because a later aggregate result is positive.

## 15.4 — Identity Quality Gate

Audit final evidence for:

- identity preservation;
- multi-view consistency;
- silhouette/profile;
- facial-region geometry;
- metric evidence where required.

## 15.5 — Separation Gate

Audit:

- identity ↔ pose;
- identity ↔ camera;
- identity ↔ expression;
- canonical identity ↔ person-specific detail.

## 15.6 — Physical Gate

Consume Item 11 closure evidence.

## 15.7 — Runtime / Reproducibility Gate

Consume Item 12 closure evidence.

## 15.8 — Commercial / Legal / Privacy Gate

Consume Item 13 closure evidence.

## 15.9 — Architecture Comparison Gate

Consume Item 14 closure evidence.

## 15.10 — Residual-Risk Classification

Every unresolved issue must be classified as one of:

- material blocker;
- bounded limitation;
- future validation;
- irrelevant to Phase 9 authorization.

## 15.11 — No Unsupported Claim Audit

Explicitly verify:

- no fabricated metric 3D claim;
- no fabricated dense-anatomy claim;
- no fabricated likeness score;
- no fabricated commercial/license clearance;
- no fabricated biometric validation;
- no unsupported normalization/support score.

## 15.12 — Candidate Decision

Each architecture candidate receives only an evidence-supported result:

- `GO`;
- `HOLD`;
- `REJECT`.

## 15.13 — Phase 8 Global Decision

Final Phase 8 result:

- `GO`;
- `HOLD`;
- `REJECT / REVISION_REQUIRED`.

## 15.14 — LOCK Readiness

A GO result alone is not sufficient to claim safe continuation unless the
selected architecture and evidence are persistent and operationally defined.

Before LOCK:

- critical evidence persistent;
- continuity docs current;
- reproducibility closed;
- selected dependency explicit;
- unresolved restrictions explicit.

## 15.15 — Phase 9 Authorization

Phase 9 may start only when:

`PHASE 8 = GO + LOCK`

Only then may ATLAS begin official:

`Phase 9 — Identity-Preserving Portrait Relief V1`

No implicit authorization is allowed.

## 15.16 — Phase 9 Handoff Contract

The handoff must explicitly define what Phase 9 receives:

- selected canonical representation;
- topology;
- correspondence semantics;
- identity model;
- detail model;
- semantic mapping;
- quality limitations;
- physical representation contract;
- runtime/reproducibility requirements;
- privacy/license restrictions.

## 15.17 — Final Documentation / Persistence

Persist final:

- decision evidence;
- manifests;
- provenance;
- architecture selection;
- blockers/limitations;
- continuity state;
- exact next authorized action.

## 15.18 — Item 15 / Phase 8 Closure

Item 15 closes only when the Phase 8 decision and LOCK state are explicit,
persistent and verified.

---

# LOCKED CROSS-ITEM HARD RULES

The following rules apply across Main Checklist Items 9–15.

1. Global error is never the sole facial-quality criterion. Region-wise
   evaluation is mandatory.

2. Landmark fit and surface fit remain separate evidence families.

3. 2D reprojection and metric 3D accuracy remain separate.

4. Trueness, precision and repeatability remain separate measurement concepts.

5. Alignment is part of the evaluation protocol and must be recorded; alignment
   choices may materially affect measured error.

6. Metric units MUST NOT be inferred.

7. Facial-region evaluation requires verified mapping appropriate to the exact
   claim.

8. Population anthropometry MUST NOT become an identity template or fitting
   target merely because population statistics exist.

9. Pose, expression and camera behavior MUST NOT be misreported as identity
   quality.

10. Physical print quality and canonical identity quality remain separate gates.

11. Printed physical fidelity must be separately verified where required.

12. Runtime or processing cost cannot rescue a candidate that fails material
    identity, physical, policy or reproducibility requirements.

13. A reproducibility adaptation MUST NOT be relabelled as an exact historical
    rerun.

14. Model license, weight/checkpoint license and dataset restrictions are
    separate evidence channels.

15. Customer photographs/content MUST NOT automatically be reused for model
    training, fine-tuning or unrelated dataset construction.

16. Personalized face reconstruction and biometric identification/recognition
    remain separate functionality and policy categories.

17. No normalized support-score fabrication.

18. No arbitrary acceptance threshold may be invented merely to force closure.

19. No candidate may win solely on global score while a verified material
    customer-visible facial-region identity blocker remains unresolved.

20. Phase 9 begins only after explicit Phase 8 `GO + LOCK`.

21. Existing verified evidence and claim boundaries from Items 1–8 remain valid
    unless new evidence explicitly supersedes them.

22. Item 8 `BOUNDED_PASS` does not become an unqualified PASS retroactively.

23. The Item 8 residual limitation involving mixed held-out regional behavior
    and `nose_body` degradation in `3/3` measured held-out observation-space
    views remains traceable into Items 9, 14 and 15.

24. H2 `ATLAS-derived barycentric-anchor-supported FLAME topology footprints`
    remain bounded mappings and MUST NOT be promoted to dense anatomical ground
    truth.

25. No millimetre anatomical claim without verified metric GT.

26. Critical evidence feeding later decisions must be persistent; `/tmp` alone
    is insufficient.

27. No Phase 9 production portrait implementation before the Phase 8 final
    decision and LOCK.

---

# RESEARCH-DERIVED DESIGN BASIS

The Item 9–15 structure was formed after cross-checking available academic,
published technical, regulatory and practitioner material associated with the
United States, Japan, China, Germany and France.

The research synthesis supports the following engineering principles:

- regional facial evaluation is necessary because global aggregate errors may
  conceal region-specific degradation;
- surface and landmark accuracy must not be conflated;
- rigid/similarity alignment methodology materially affects evaluation and must
  be explicit;
- scanner/measurement validation requires separation of trueness, precision
  and repeatability;
- calibrated physical reference is required before metric-anatomical claims;
- facial regions such as nose, orbital structures, jaw/chin and cheek/midface
  need explicit region-aware evaluation;
- multi-view and held-out-view evidence is important for separating identity
  quality from training-view fit;
- physical manufacturing introduces an additional error domain beyond digital
  reconstruction;
- exact environment, model/checkpoint provenance, hashes and repeatable
  execution are required for production-grade reproducibility;
- face reconstruction/personalization, biometric identification and facial
  recognition must not be treated as synonymous processing purposes;
- data protection, retention, model/weight/dataset licensing and commercial-use
  compatibility are independent production-dependency gates;
- architecture comparison must cover quality, local geometry, physical
  suitability, topology, reproducibility, runtime and policy rather than only
  one aggregate accuracy score.

Country-specific research contribution was interpreted conservatively:

### United States
Relevant material reinforces measurement/benchmark discipline, repeatability,
demographic/performance considerations, biometric/privacy risk analysis and the
need for substantiated accuracy/privacy claims.

### Japan
Relevant material reinforces standardized facial anthropometry, controlled
orientation/capture, calibrated measurement, trueness/precision/repeatability
separation and explicit treatment of identifying facial-feature data.

### China
Relevant material reinforces region-wise 3D facial measurement, standardized
multi-view evaluation, metric scanner comparison and strict purpose/minimization
considerations for facial-information processing.

### Germany
Relevant work around FLAME-family reconstruction, canonical topology,
multi-view fitting, detail/expression separation and neural/hybrid head
reconstruction strongly informs the canonical-head benchmark architecture.

### France
Relevant privacy/regulatory guidance reinforces privacy-by-design, biometric
template/data distinctions, purpose limitation and conservative treatment of
facial processing.

Low-signal forum material must not be elevated above controlled academic,
published technical, official provider or regulatory evidence merely to satisfy
a geographic quota.

---

# AUTHORITATIVE EXECUTION CONSEQUENCE

After this plan is recorded:

- Main Checklist Item 8 remains officially closed as `BOUNDED_PASS`;
- Main Checklist Item 9 becomes the next planned technical item;
- Item 9 implementation does NOT automatically begin merely because the plan is
  recorded;
- no new protocol, threshold, evidence file, CORE contract or experiment is
  authorized by this documentation step alone;
- before executing Item 9, the exact first Item 9 substep must be selected
  explicitly under this locked plan;
- Items 9–15 must proceed in order unless the user explicitly authorizes a plan
  revision;
- Phase 8 final decision remains undecided;
- Phase 8 GO/LOCK is not established;
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.



---

## PHASE8_ITEM9_15_RESEARCH_AUGMENTATION_LOCKED_2026_08_27

### Status

**Research-derived augmentation to the already locked Main Checklist Item 9–15 master action plan.**

This augmentation was added after cross-checking current openly available work from
the ATLAS first-ring research institutions, including relevant work associated with:

- Carnegie Mellon University;
- MIT;
- Stanford University;
- ETH Zürich;
- UC Berkeley;
- University of Cambridge;
- University of Oxford.

The previously locked Item 9–15 master plan remains authoritative.

This augmentation does NOT replace or renumber the existing plan.
It adds four explicit evaluation channels that were found to be materially useful
for ATLAS's canonical-identity, multi-view, hybrid-detail and evidence-quality goals.

No Item 9 implementation is authorized merely by recording this augmentation.

---

# A — EVIDENCE ORIGIN / HALLUCINATION AUDIT

## Placement

Primary placement:

- Item 9.2 — Semantic Region Mapping Audit;
- Item 9.10 — Cross-View Regional Consistency;
- Item 14 — Three-Class Architecture Comparison.

## Purpose

ATLAS must not treat all reconstructed facial geometry as equally observed.

For each evaluated facial region, record the strongest justified evidence-origin state.

Permitted evidence-origin states:

- `DIRECTLY_OBSERVED`;
- `MULTIVIEW_CONSTRAINED`;
- `MODEL_PRIOR_INFERRED`;
- `GENERATED_COMPLETION`;
- `UNRESOLVED`.

These states describe evidence origin, not geometric quality.

## Required rules

1. `DIRECTLY_OBSERVED` means the relevant region has direct source-view support.

2. `MULTIVIEW_CONSTRAINED` means geometry is supported by multiple compatible
   observations/views but is not necessarily directly visible in every target view.

3. `MODEL_PRIOR_INFERRED` means the geometry is substantially determined by a
   learned/statistical/canonical prior rather than direct subject observation.

4. `GENERATED_COMPLETION` means missing or occluded geometry is synthesized/completed
   by a generative or predictive mechanism.

5. `UNRESOLVED` means the evidence origin cannot be established strongly enough.

6. Reconstructed geometry MUST NOT be described as directly observed merely because
   a model produced a confident-looking surface.

7. Unseen regions such as contralateral profile, posterior cranial surface, hidden ear
   structures or other occluded facial/head areas require explicit evidence-origin labeling.

8. Evidence origin MUST remain separate from:
   - metric accuracy;
   - likeness;
   - topology quality;
   - physical printability.

9. A generated or prior-inferred region may still be useful, but its provenance must
   remain explicit in Items 9, 14 and 15.

---

# B — VIEW-SPECIFIC INCONSISTENCY / EXPLAIN-AWAY CHANNEL

## Placement

Primary placement:

- Item 9.11 — Cross-Region Compensation Audit;
- Item 14.23 — Failure Mode Matrix;
- Item 15.5 — Separation Gate.

## Purpose

Prevent a view-specific observation error or inconsistency from being absorbed into
canonical identity geometry.

Before assigning a cross-view mismatch to identity, ATLAS must test whether the mismatch
can be explained by another bounded source.

Candidate explain-away causes include:

- landmark localization uncertainty;
- occlusion;
- partial visibility;
- illumination asymmetry;
- motion;
- expression;
- root-pose error;
- camera error;
- scale/translation compensation;
- correspondence mismatch;
- view-specific reconstruction inconsistency;
- generated/synthesized-view inconsistency;
- missing information.

## Required rules

1. A single-view mismatch MUST NOT automatically mutate canonical identity.

2. Canonical identity changes require evidence that the discrepancy is not better
   explained by nuisance or observation-specific factors.

3. The audit must preserve distinction between:
   - canonical-consistent component;
   - view-specific inconsistent component.

4. Global reprojection improvement MUST NOT be accepted if it is achieved by absorbing
   view-specific error into identity.

5. The existing Item 8 H1 finding of view-dependent non-additive
   observation-conditioned identity-camera compensation remains directly relevant.

6. Where possible, measure whether exclusion/down-weighting of a suspect observation
   changes canonical identity materially.

7. This channel is an evaluation safeguard, not authorization for arbitrary robust-loss
   tuning.

8. New thresholds, outlier rules or weights require explicit evidence and approval.

---

# C — INDEPENDENT GEOMETRY / CAMERA CROSS-CHECK

## Placement

Primary placement:

- Item 9 — Facial Region Geometry Quality;
- Item 10 — Metric Ground-Truth Layer;
- Item 14 — Three-Class Architecture Comparison.

## Purpose

Reduce the risk that one reconstruction stack validates its own assumptions.

Where technically and legally viable, ATLAS should compare its primary fitting/reconstruction
result against an independent geometry/camera evidence source.

Possible roles for an independent source include:

- camera estimation;
- relative depth;
- multi-view point structure;
- correspondence;
- coarse geometry;
- view-consistency diagnostics.

The independent system MUST NOT automatically become canonical identity ownership.

## Required rules

1. Primary and independent systems should not share the same hidden assumptions whenever
   independence is being claimed.

2. Agreement between two systems is supporting evidence, not metric ground truth.

3. Disagreement must be preserved and investigated rather than silently averaged away.

4. Independent camera evidence is particularly relevant when analytic camera re-solving
   materially compensates geometry changes.

5. Independent geometry evidence may support:
   - region consistency;
   - silhouette/profile interpretation;
   - camera sanity;
   - multi-view coherence;
   - failure localization.

6. Independent geometry evidence MUST NOT create millimetre claims without verified metric GT.

7. Research systems with non-commercial licensing may be used only as research/benchmark
   evidence where permitted; they must not silently become production dependencies.

8. Commercial-use compatibility must be evaluated separately under Item 13 before any
   such system enters a production path.

9. Current research direction identifies VGGT-class systems as potentially useful
   independent geometry/camera evidence providers, subject to exact version, checkpoint,
   license, runtime and platform verification.

10. VGGT or any similar system is NOT automatically selected as an ATLAS dependency by
    this plan augmentation.

---

# D — CANONICAL-vs-RESIDUAL OWNERSHIP AUDIT

## Placement

Primary placement:

- Item 14.14 — Detail Preservation;
- Item 14.23 — Failure Mode Matrix;
- Item 15.5 — Separation Gate.

Secondary relevance:

- hybrid `canonical + detail` architecture throughout Items 9–15.

## Purpose

Ensure that the hybrid architecture preserves clean ownership between canonical identity
geometry and bounded person-specific detail.

Required semantic separation:

`identity shape`
!=
`person-specific residual detail`
!=
`expression/transient deformation`
!=
`appearance/texture`
!=
`camera/view artifact`

## Required tests

Where the hybrid candidate permits:

1. Evaluate canonical geometry with residual/detail disabled.

2. Evaluate canonical geometry with approved residual/detail enabled.

3. Measure whether the detail layer introduces low-frequency identity-shape drift.

4. Measure whether residual/detail improves one view while degrading cross-view consistency.

5. Determine whether residual energy remains within its declared semantic role.

6. Determine whether expression/transient structure leaks into persistent identity detail.

7. Determine whether appearance/illumination artifacts leak into geometry.

8. Determine whether the residual layer materially changes:
   - silhouette;
   - nose projection;
   - jaw/chin;
   - orbital/cheek volume;
   - cranial/head ratio.

9. Preserve the existing ATLAS principle:
   canonical identity geometry owns identity;
   residual detail may refine but must not silently become a second identity model.

10. DSINE or any similar normal/detail provider remains bounded according to its verified
    role unless new evidence explicitly expands that role.

## Required outcomes

The audit must be able to classify the hybrid candidate as:

- ownership separation supported;
- bounded leakage present;
- material ownership violation;
- evidence insufficient.

A material ownership violation blocks an unqualified architecture PASS.

---

# RESEARCH-DRIVEN FAILURE-CONDITION STRATIFICATION

The following conditions should be represented explicitly in Item 14.23 Failure Mode Matrix
when evidence is available:

- frontal;
- moderate yaw;
- strong yaw / profile;
- partial occlusion;
- low-resolution input;
- illumination asymmetry;
- weak texture;
- missing semantic region;
- generated/completed unseen region;
- view-specific inconsistent observation.

Average benchmark performance MUST NOT conceal condition-specific failure.

---

# UPDATED ITEM RELATIONSHIPS

The locked Item 9–15 execution dependency chain remains:

`Item 9 regional geometry`
→ `Item 10 metric ground truth`
→ `Item 11 physical survival`
→ `Item 12 runtime / reproducibility`
→ `Item 13 commercial / legal / privacy`
→ `Item 14 three-class architecture comparison`
→ `Item 15 Phase 8 final gate`

The research augmentation adds the following cross-links:

- Item 9.2 now includes evidence-origin classification.
- Item 9.10 now includes direct-vs-constrained-vs-inferred regional consistency.
- Item 9.11 now includes view-specific inconsistency / explain-away analysis.
- Item 10 may use independent geometry/camera evidence only as supporting evidence,
  never as fake metric GT.
- Item 14.14 now includes canonical-vs-residual ownership.
- Item 14.23 now includes condition-stratified and view-specific failure modes.
- Item 14 must preserve research-only versus production-eligible dependency status.
- Item 15 must verify that no model-prior/generated completion or residual-detail ownership
  violation is hidden inside a final GO claim.

---

# ADDITIONAL LOCKED HARD RULES

These rules augment, but do not replace, the existing locked Item 9–15 hard rules.

28. Reconstructed geometry must carry an evidence-origin state when the region was not
    directly observed.

29. Generated completion MUST NOT be silently described as subject-observed identity truth.

30. A view-specific observation inconsistency MUST NOT automatically be absorbed into
    canonical identity.

31. Independent geometry/camera estimation may provide supporting evidence but is not
    metric ground truth by itself.

32. Agreement among multiple learned models does not constitute physical ground truth.

33. Hybrid residual/detail layers must not silently own low-frequency canonical identity shape.

34. Appearance, illumination and expression detail must not leak into persistent identity
    geometry without explicit evidence.

35. Research-only or non-commercial systems may not enter the ATLAS commercial dependency
    path merely because they improve benchmark evidence.

36. Condition-specific failures must remain visible even when aggregate metrics are positive.

37. Any future auxiliary system such as VGGT-class reconstruction must undergo exact:
    - version verification;
    - checkpoint verification;
    - license verification;
    - model-weight restriction audit;
    - runtime/platform verification;
    - reproducibility audit;
    before production eligibility can even be considered.

---

# AUTHORITATIVE CONSEQUENCE

After this augmentation is recorded:

- the original Item 9–15 plan remains locked;
- this augmentation becomes part of the authoritative remaining Phase 8 plan;
- Main Checklist Item 9 remains the next technical item;
- Item 9 implementation has not yet started;
- no new CORE contract, test, evidence artifact, threshold or external dependency is created
  by this documentation update alone;
- Phase 8 final decision remains undecided;
- Phase 8 GO + LOCK remains false;
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.



---

## PHASE8_ITEM9_1_EVALUATION_SPACE_CLAIM_BOUNDARY_COMPLETE_2026_08_27

### Main Checklist Item 9.1 — Evaluation-Space & Claim Boundary

Status: **COMPLETE**

Item 9.1 establishes an executable provider-independent claim boundary between
different ATLAS facial-geometry evidence spaces.

Implemented:

- `CORE/atlas_canonical_head_evaluation_space_claim_boundary.py`
- `Test/test_canonical_head_evaluation_space_claim_boundary.py`

Explicit evaluation spaces:

- `2d_observation`
- `canonical_model`
- `metric_3d_ground_truth`
- `physical_output`

The contract blocks unsupported evidence-to-claim promotion, including:

- `landmark_fit -> surface_accuracy`
- `2d_reprojection -> metric_3d_accuracy`
- `canonical_model_displacement -> anatomical_millimetres`
- `printability -> identity_preservation`
- `aggregate_improvement -> uniform_regional_improvement`

Same-scope claims remain representable without promoting their evidentiary meaning.

The contract deliberately does NOT:

- calculate geometric measurements;
- create a likeness score;
- create a normalized support score;
- introduce a new acceptance threshold;
- claim metric accuracy;
- claim anatomical millimetres;
- produce GO / HOLD / REJECT;
- authorize Phase 9.

Existing metric, reprojection and physical-representation contracts remain separate
and unchanged.

Validation:

- RED test first: expected `ModuleNotFoundError` before implementation.
- Focused: `14 passed in 0.03s`.
- Related canonical-head regression: `732 passed, 2 warnings in 4.16s`.
- Full regression: `5015 passed, 11 warnings in 135.61s`.
- `git diff --check`: `EXIT=0`.

The warnings observed are existing NumPy `numpy.core.numeric` deprecation warnings
from the Phase 8.10 FLAME surface-correspondence path; no Item 9.1 test failure occurred.

Item 9.1 conclusion:

`EVALUATION_SPACE_AND_CLAIM_BOUNDARY = ESTABLISHED`

This conclusion means only that ATLAS now has an executable epistemic boundary for
the five locked Item 9.1 claim rules. It does not establish facial-region accuracy,
metric anatomical accuracy, physical identity fidelity, or Phase 8 GO.

Next planned Main Checklist subitem:

`9.2 — Semantic Region Mapping Audit`

Current global state remains:

- Phase 8 final decision: NOT MADE;
- Phase 8 GO + LOCK: FALSE;
- Phase 9: NOT AUTHORIZED / NOT STARTED.

### PHASE8_ITEM9_2_SEMANTIC_REGION_MAPPING_EVIDENCE_CONTRACT_COMPLETE_2026_08_27

- Main Checklist Item 9.2 — Semantic Region Mapping Audit executable evidence contract added.
- New contract:
  `CORE/atlas_canonical_head_semantic_region_mapping_evidence.py`
- New focused test:
  `Test/test_canonical_head_semantic_region_mapping_evidence.py`
- Exact required Item 9.2 regions:
  `jaw`, `chin`, `nose_bridge`, `nose_body`, `nose_base_tip`,
  `left_orbital`, `right_orbital`, `left_cheek`, `right_cheek`,
  `upper_lip`, `lower_lip`, `perioral`, `forehead`,
  `cranial_head_envelope`.
- Exact mapping states:
  `provider_verified`,
  `independently_verified_atlas_derived`,
  `anchor_supported_only`,
  `unresolved_blocked`.
- Exact evidence-origin states:
  `directly_observed`,
  `multiview_constrained`,
  `model_prior_inferred`,
  `generated_completion`,
  `unresolved`.
- Contract carries explicit `mapping_scope`, source reference,
  permitted claim and prohibited claims.
- Contract does NOT derive vertex mappings, create semantic aliases,
  claim dense anatomical ground truth, claim metric 3D/mm accuracy,
  assign confidence/threshold scores, or make Phase decisions.
- Existing H2 nose mappings remain bounded to the exact
  ATLAS-derived barycentric-anchor-supported FLAME topology footprint;
  they are not provider-authored dense anatomy.
- Existing provider `left_eye_region` / `right_eye_region` evidence is
  not silently relabelled as orbital anatomy.
- Existing provider `lips` evidence is not silently split into dense
  upper/lower/perioral topology regions.
- `nose_base` evidence is not silently promoted to `nose_base_tip`.
- Verification:
  focused `23 passed in 0.03s`;
  related canonical-head regression `755 passed, 2 warnings in 4.13s`;
  full regression `5038 passed, 11 warnings in 134.90s`.
- Phase 8 final decision unchanged.
- Official Phase 9 remains NOT AUTHORIZED / NOT STARTED.

### PHASE8_ITEM9_3_JAW_CHIN_QUALITY_EVIDENCE_CONTRACT_COMPLETE_2026_08_27

- Main Checklist Item 9.3 — Jaw / Chin Quality bounded evidence contract added.
- New contract:
  `CORE/atlas_canonical_head_jaw_chin_quality_evidence.py`
- New focused test:
  `Test/test_canonical_head_jaw_chin_quality_evidence.py`
- Exact Item 9.3 criteria represented:
  `mandibular_width`, `jaw_angle`, `chin_width`, `chin_projection`,
  `chin_vertical_position`, `left_right_contour`, `frontal_consistency`,
  `profile_consistency`, `cross_view_stability`.
- Evaluation-space boundary retained:
  `2d_observation`, `canonical_model`, `metric_3d_ground_truth`,
  `physical_output`.
- Evidence statuses:
  `bounded_positive`, `bounded_negative_not_established`,
  `bounded_aggregate_only`, `blocked`.
- Evidence-origin states:
  `directly_observed`, `multiview_constrained`, `model_prior_inferred`,
  `generated_completion`, `unresolved`.
- Verified machine-readable jaw/silhouette source:
  `/Users/Kubi/ATLAS_PERSONAL_MULTIVIEW_SPIKE/EVIDENCE/phase8_10_personal_multiview_2026-08-26/expression_separation_8_8/REPRODUCIBILITY_ITEM8_9_REGION_WISE.json`
- Verified source SHA256:
  `f5a5cc438d003c1a4186d8782aa3ad008105a8a9800325ca56415b9247eaa7ca`.
- Item 9.3 bounded classification:
  - mandibular width: `BLOCKED`;
  - jaw angle: `BLOCKED`;
  - chin width: `BLOCKED`;
  - chin projection: `BLOCKED`;
  - chin vertical position: `BLOCKED`;
  - left/right contour: bounded positive 2D silhouette/profile evidence;
  - frontal consistency: bounded negative / not established;
  - profile consistency: bounded positive 2D evidence;
  - cross-view stability: bounded aggregate-only; feature-specific stability
    is not established.
- Verified side-contour evidence:
  `turn_right` approximately 61.35% reduction;
  `turn_left` approximately 61.61% reduction.
- Preferred 2.5% silhouette-energy candidate improves side-profile evidence
  but increases front-view contour error relative to baseline; the trade-off
  remains explicit.
- `static105` has zero overlap with the 21 lower-jaw IDs and the full
  36-point face oval.
- Verified FLAME jaw/chin vertex-level semantic mapping remains unavailable.
- Therefore no guessed FLAME vertex indices, dense jaw/chin anatomy,
  metric 3D/mm accuracy, identity-preservation proof, or feature-specific
  cross-view stability claim is permitted.
- No acceptance threshold, confidence score, Phase 8 decision, or Phase 9
  authorization is introduced by this contract.
- Verification:
  focused `18 passed in 0.03s`;
  related canonical-head regression `773 passed, 2 warnings in 4.35s`;
  full regression `5056 passed, 11 warnings in 134.52s`.
- Phase 8 final decision unchanged.
- Official Phase 9 remains NOT AUTHORIZED / NOT STARTED.

### PHASE8_ITEM9_4_NOSE_QUALITY_EVIDENCE_CONTRACT_COMPLETE_2026_08_27

- Main Checklist Item 9.4 — Nose Quality bounded evidence contract added.
- New contract:
  `CORE/atlas_canonical_head_nose_quality_evidence.py`
- New focused test:
  `Test/test_canonical_head_nose_quality_evidence.py`
- Exact Item 9.4 criteria represented:
  `bridge`, `dorsum_body`, `base`, `tip_projection`, `alar_width`,
  `nasolabial_relation`, `profile_projection`, `bilateral_consistency`,
  `cross_view_consistency`.
- Evaluation-space boundary retained:
  `2d_observation`, `canonical_model`, `metric_3d_ground_truth`,
  `physical_output`.
- Evidence statuses:
  `bounded_model_space`, `bounded_negative_not_established`, `blocked`.
- Evidence-origin states:
  `directly_observed`, `multiview_constrained`, `model_prior_inferred`,
  `generated_completion`, `unresolved`.
- Verified Item 8 H2 mapping scope retained:
  - `nose_bridge`: frozen 12-vertex ATLAS-derived barycentric-anchor-supported
    FLAME topology footprint;
  - `nose_body`: frozen 13-vertex ATLAS-derived barycentric-anchor-supported
    FLAME topology footprint;
  - `nose_base`: frozen 6-vertex ATLAS-derived barycentric-anchor-supported
    FLAME topology footprint.
- These footprints are not dense anatomical segmentations and are not
  provider-authored finer nose regions.
- Item 9.4 bounded classification:
  - bridge: `BOUNDED_MODEL_SPACE`;
  - dorsum/body: `BOUNDED_NEGATIVE_NOT_ESTABLISHED`;
  - base: `BOUNDED_MODEL_SPACE`;
  - tip projection: `BLOCKED`;
  - alar width: `BLOCKED`;
  - nasolabial relation: `BLOCKED`;
  - profile projection: `BLOCKED`;
  - bilateral consistency: `BLOCKED`;
  - cross-view consistency: `BOUNDED_NEGATIVE_NOT_ESTABLISHED`.
- Mandatory retained failure evidence:
  `nose_body` observation-space degradation occurs in `3/3` held-out pose views.
- H2 further establishes that non-zero candidate-vs-baseline canonical-model
  geometry change is present on the frozen `nose_body` footprint in all three
  held-out cases; the H1 effect therefore cannot be reduced to analytic-camera
  / reprojection variation alone.
- This does NOT establish true metric 3D anatomical nose degradation because
  no independent metric 3D ground-truth correctness target exists for the
  finer nose footprint.
- Historical FLAME and PRNet benchmark coverage records
  `nose_projection_support=MISSING`; synthetic candidate-gate fixture scores
  are not treated as nose-quality evidence.
- `nose_base` is not silently promoted to `nose_base_tip`.
- Signed canonical-axis displacement is not relabelled as tip projection,
  profile projection, alar width, bilateral consistency or anatomical
  correctness.
- No millimetre claim is made.
- No global nose-quality PASS is claimed.
- No acceptance threshold, confidence score, Phase 8 decision or Phase 9
  authorization is introduced by this contract.
- Verification:
  focused `19 passed in 0.03s`;
  related canonical-head regression `792 passed, 2 warnings in 4.17s`;
  full regression `5075 passed, 11 warnings in 135.29s`.
- Phase 8 final decision unchanged.
- Official Phase 9 remains NOT AUTHORIZED / NOT STARTED.

### PHASE8_ITEM9_5_ORBITAL_EYE_SOCKET_QUALITY_EVIDENCE_CONTRACT_COMPLETE_2026_08_27

- Main Checklist Item 9.5 — Orbital / Eye-Socket Quality bounded evidence contract added.
- New contract:
  `CORE/atlas_canonical_head_orbital_quality_evidence.py`
- New focused test:
  `Test/test_canonical_head_orbital_quality_evidence.py`
- Exact Item 9.5 criteria represented:
  `inter_orbital_relation`, `orbital_rim`, `eye_socket_form_depth`,
  `upper_orbital_contour`, `lower_orbital_contour`,
  `left_right_asymmetry`, `eye_region_nose_bridge_relation`.
- Evaluation-space boundary retained:
  `2d_observation`, `canonical_model`, `metric_3d_ground_truth`,
  `physical_output`.
- Evidence statuses:
  `bounded_not_established`, `blocked`.
- Evidence-origin states:
  `directly_observed`, `multiview_constrained`, `model_prior_inferred`,
  `generated_completion`, `unresolved`.
- Verified provider FLAME masks:
  - `left_eye_region`: 287 unique vertices;
  - `right_eye_region`: 287 unique vertices.
- Verified observation-to-provider anchor support:
  - left eye: 6/6 embedded anchors fully supported by `left_eye_region`;
  - right eye: 6/6 embedded anchors fully supported by `right_eye_region`.
- Provider `eye_region` evidence is NOT promoted to orbital anatomy.
- Item 9.5 bounded classification:
  - inter-orbital relation: `BOUNDED_NOT_ESTABLISHED`;
  - orbital rim: `BLOCKED`;
  - eye-socket form/depth: `BLOCKED`;
  - upper orbital contour: `BLOCKED`;
  - lower orbital contour: `BLOCKED`;
  - left/right asymmetry: `BOUNDED_NOT_ESTABLISHED`;
  - eye-region to nose-bridge relation: `BOUNDED_NOT_ESTABLISHED`.
- Real held-out 2D eye-region evidence remains view-dependent:
  - held_out_front:
    right_eye delta `+0.062302674623 px`,
    left_eye delta `+0.179408183345 px`;
  - held_out_turn_left:
    right_eye delta `-0.053835099557 px`,
    left_eye delta `-0.058580004479 px`;
  - held_out_turn_right:
    right_eye delta `+0.005074152054 px`,
    left_eye delta `-0.041701365010 px`.
- Therefore uniform orbital/eye-region stability is NOT established.
- Parametric `EYE_SOCKET_*` constants are model-prior/generated geometry and
  are not treated as subject-observed orbital quality evidence.
- Historical FLAME and PRNet benchmark coverage remains
  `orbital_cheek_volume_support=MISSING`.
- No orbital-rim mapping, socket-depth ground truth, upper/lower orbital
  contour mapping, subject-specific anatomical asymmetry metric, or explicit
  eye-region to nose-bridge spatial-relation metric is claimed.
- No metric millimetre claim is made.
- No global orbital-quality PASS is claimed.
- No acceptance threshold, confidence score, Phase 8 decision, or Phase 9
  authorization is introduced by this contract.
- Verification:
  focused `17 passed in 0.03s`;
  related canonical-head regression `809 passed, 2 warnings in 4.51s`;
  full regression `5092 passed, 11 warnings in 135.24s`.
- Phase 8 final decision unchanged.
- Official Phase 9 remains NOT AUTHORIZED / NOT STARTED.

### PHASE8_ITEM9_6_CHEEK_MIDFACE_QUALITY_EVIDENCE_CONTRACT_COMPLETE_2026_08_27

- Main Checklist Item 9.6 — Cheek / Midface Quality evidence contract added.
- New contract:
  `CORE/atlas_canonical_head_cheek_midface_quality_evidence.py`
- New focused test:
  `Test/test_canonical_head_cheek_midface_quality_evidence.py`
- Exact Item 9.6 criteria represented:
  `zygomatic_width`, `cheek_prominence`, `anterior_projection`,
  `midface_fullness`, `cheek_to_nose_transition`,
  `cheek_to_jaw_transition`, `bilateral_asymmetry`.
- Evaluation-space boundary retained:
  `2d_observation`, `canonical_model`, `metric_3d_ground_truth`,
  `physical_output`.
- Current evidence status for all seven criteria is `blocked`.
- Evidence-origin states retained:
  `directly_observed`, `multiview_constrained`, `model_prior_inferred`,
  `generated_completion`, `unresolved`.
- Item 9.2 cheek mapping evidence remains unresolved:
  `left_cheek` / `right_cheek` are required semantic regions but no verified
  subject-specific canonical cheek mapping was found.
- Persistent Item 8 H2 evidence contains no cheek/midface-specific mapping
  or regional quality measurement.
- `REPRODUCIBILITY_ITEM8_9_REGION_WISE.json` contains no cheek/midface
  region-wise held-out keys.
- FLAME and PRNet benchmark coverage remains
  `orbital_cheek_volume_support=MISSING`.
- Existing parametric `CHEEK_*` constants and `cheek_projection` values are
  model-prior/generated geometry and are NOT treated as subject-observed
  cheek/midface quality evidence.
- Existing 2.5D relief `left_cheek` / `right_cheek` masks are NOT promoted
  to canonical 3D cheek/midface ground truth.
- No verified subject-specific evidence currently establishes:
  - zygomatic width;
  - cheek prominence;
  - anterior projection;
  - midface fullness;
  - cheek-to-nose transition;
  - cheek-to-jaw transition;
  - bilateral cheek/midface asymmetry.
- `zygomatic_width` remains Item 9.6 regional geometry scope.
- `bizygomatic_relation` remains separately reserved for Item 9.9
  anthropometric/proportional evaluation and is not promoted into Item 9.6.
- No regional surface-accuracy, anatomical-ground-truth, metric-millimetre,
  threshold, confidence-score, Phase 8 decision, or Phase 9 authorization
  claim is introduced.
- Verification:
  focused `18 passed in 0.03s`;
  related canonical-head regression `827 passed, 2 warnings in 4.23s`;
  full regression `5110 passed, 11 warnings in 134.36s`.
- Phase 8 final decision unchanged.
- Official Phase 9 remains NOT AUTHORIZED / NOT STARTED.

### PHASE8_ITEM9_7_MOUTH_PERIORAL_QUALITY_EVIDENCE_CONTRACT_COMPLETE_2026_08_27

- Main Checklist Item 9.7 — Mouth / Perioral Quality evidence contract added.
- New contract:
  `CORE/atlas_canonical_head_mouth_perioral_quality_evidence.py`
- New focused test:
  `Test/test_canonical_head_mouth_perioral_quality_evidence.py`
- Exact Item 9.7 criteria represented:
  `mouth_width`, `upper_lower_lip_relation`, `philtrum_region`,
  `lip_projection`, `commissures`,
  `neutral_geometry_vs_expression_deformation`,
  `nasolabial_perioral_contamination`.
- Evaluation-space boundary retained:
  `2d_observation`, `canonical_model`, `metric_3d_ground_truth`,
  `physical_output`.
- Evidence-status states retained:
  `bounded_not_established`, `bounded_structural`, `blocked`.
- Evidence-origin states retained:
  `directly_observed`, `multiview_constrained`, `model_prior_inferred`,
  `generated_completion`, `unresolved`.
- Provider FLAME semantic coverage contains one broad `lips` mask with
  250 unique vertices; provider evidence does NOT split this mask into
  upper lip, lower lip, philtrum, commissures, or dense perioral anatomy.
- H2 observation/provider anchor audit:
  upper_lip has 8/8 embedded anchors fully supported by the provider
  `lips` mask; lower_lip has 7 embedded anchors fully supported by the
  provider `lips` mask while historical region-wise coverage remains
  `partial_static105_overlap` because the requested lower-lip set is 7/8.
- Held-out 2D observation evidence:
  upper_lip improves in all three held-out pose views:
  front `-0.596790245425 px`,
  turn-left `-0.195223703135 px`,
  turn-right `-0.293216107193 px`.
- Held-out lower_lip also improves in all three held-out pose views:
  front `-0.418135292306 px`,
  turn-left `-0.124998030645 px`,
  turn-right `-0.076177947174 px`,
  with partial static105 overlap.
- These lip results are bounded 2D landmark/reprojection evidence only;
  they do NOT establish explicit upper-to-lower lip geometry relation,
  lip surface accuracy, lip projection, commissure accuracy, or metric
  3D anatomy.
- Item 9.7 criterion classification:
  - mouth_width: `BLOCKED`;
  - upper_lower_lip_relation: `BOUNDED_NOT_ESTABLISHED`;
  - philtrum_region: `BLOCKED`;
  - lip_projection: `BLOCKED`;
  - commissures: `BLOCKED`;
  - neutral_geometry_vs_expression_deformation: `BOUNDED_STRUCTURAL`;
  - nasolabial_perioral_contamination: `BLOCKED`.
- `mouth_width` measurement/deformation machinery and
  `mouth_left`/`mouth_right` landmarks exist, but no persisted
  subject-specific validated mouth-width quality measurement was found.
- Parametric `upper_lip_projection`, `lower_lip_projection`, and
  `philtrum_depth` values are model-prior/generated geometry and are NOT
  treated as subject-observed quality evidence.
- Relief philtrum/lip masks and suppression/confidence maps remain
  2.5D relief semantics and are NOT promoted to canonical 3D ground truth.
- H3 counterfactual evidence supports bounded structural separation:
  expression-dependent geometry changes while locked identity parameter
  state and identity-only canonical geometry remain invariant.
- H3 does NOT provide mouth-specific regional accuracy, dense perioral
  anatomy, or proof of leakage absence in every future optimizer.
- No dedicated commissure-quality, philtrum-surface,
  nasolabial/perioral-contamination, or metric lip-projection measurement
  is currently established.
- No millimetre claim, regional surface-accuracy claim, acceptance
  threshold, confidence score, global mouth-quality pass, Phase 8 decision,
  or Phase 9 authorization is introduced.
- Verification:
  focused `17 passed in 0.03s`;
  related canonical-head regression `850 passed, 11 warnings in 15.47s`;
  full regression `5127 passed, 11 warnings in 134.26s`.
- Phase 8 final decision unchanged.
- Official Phase 9 remains NOT AUTHORIZED / NOT STARTED.

### PHASE8_ITEM9_8_FOREHEAD_CRANIAL_QUALITY_EVIDENCE_CONTRACT_COMPLETE_2026_08_27

- Main Checklist Item 9.8 — Forehead / Cranial Quality evidence contract added.
- New contract:
  `CORE/atlas_canonical_head_forehead_cranial_quality_evidence.py`
- New focused test:
  `Test/test_canonical_head_forehead_cranial_quality_evidence.py`
- Exact Item 9.8 criteria represented:
  `forehead_height`, `forehead_slope`, `frontal_curvature`,
  `temple_transition`, `cranial_width`, `cranial_depth`,
  `overall_skull_head_envelope`.
- Evaluation-space boundary retained:
  `2d_observation`, `canonical_model`, `metric_3d_ground_truth`,
  `physical_output`.
- Current evidence status for all seven criteria is `blocked`.
- Evidence-origin states retained:
  `directly_observed`, `multiview_constrained`, `model_prior_inferred`,
  `generated_completion`, `unresolved`.
- Provider FLAME semantic coverage includes:
  `forehead` with 133 unique vertices and
  `scalp` with 489 unique vertices.
- Provider semantic masks are region descriptors only and are NOT treated
  as criterion-specific quality measurements.
- H2 FLAME mask geometry sanity measurements remain model-space geometry
  descriptions and are NOT promoted to subject-specific anatomical truth.
- Item 8 region-wise / held-out evidence contains no dedicated forehead or
  cranial quality channel.
- Existing personal-multiview silhouette/profile evidence uses the
  lower-jaw visible contour channel with 21 MediaPipe lower-jaw source IDs.
  It is therefore NOT promoted to forehead, cranial-width, cranial-depth,
  or global skull/head-envelope quality evidence.
- Existing `forehead_height` measurement / parameter / reference-profile
  machinery exists, but no persisted subject-specific validated
  forehead-height quality measurement was found.
- No criterion-specific subject evidence was found for:
  - forehead slope;
  - frontal curvature;
  - temple transition;
  - cranial width;
  - cranial depth;
  - overall skull/head envelope.
- `cranial_head_envelope` remains a required semantic region in the Item 9.2
  contract, but this audit does not establish a verified criterion-specific
  mapping or quality measurement for Item 9.8.
- Item 9.8 criterion classification:
  - forehead_height: `BLOCKED`;
  - forehead_slope: `BLOCKED`;
  - frontal_curvature: `BLOCKED`;
  - temple_transition: `BLOCKED`;
  - cranial_width: `BLOCKED`;
  - cranial_depth: `BLOCKED`;
  - overall_skull_head_envelope: `BLOCKED`.
- No millimetre claim, subject-anatomical-truth claim, regional
  surface-accuracy claim, acceptance threshold, confidence score,
  global forehead/cranial pass, Phase 8 decision, or Phase 9 authorization
  is introduced.
- Verification:
  focused `17 passed in 0.03s`;
  related canonical-head regression `867 passed, 11 warnings in 15.36s`;
  full regression `5144 passed, 11 warnings in 135.88s`.
- Phase 8 final decision unchanged.
- Official Phase 9 remains NOT AUTHORIZED / NOT STARTED.

## PHASE8_ITEM9_9_HEAD_RATIO_ANTHROPOMETRIC_QUALITY_EVIDENCE_CONTRACT_COMPLETE_2026_08_27

Phase 8 / Main Checklist Item 9.9 — Head Ratios / Anthropometric Proportions
evidence contract is implemented and verified.

Contract:
- CORE/atlas_canonical_head_head_ratio_anthropometric_quality_evidence.py
- Test/test_canonical_head_head_ratio_anthropometric_quality_evidence.py

Exact Item 9.9 criteria:
- facial_width_height
- bizygomatic_relation
- bigonial_relation
- interocular_relation
- nose_width_height
- mouth_width
- upper_lower_facial_proportions
- cranial_to_facial_relationship

Evidence classification:
- facial_width_height: BOUNDED_2D_OBSERVATION_ONLY
- bizygomatic_relation: BLOCKED
- bigonial_relation: BOUNDED_2D_OBSERVATION_ONLY
- interocular_relation: BOUNDED_2D_OBSERVATION_ONLY
- nose_width_height: BOUNDED_2D_OBSERVATION_ONLY; exact denominator semantics remain unresolved
- mouth_width: BOUNDED_2D_OBSERVATION_ONLY
- upper_lower_facial_proportions: BLOCKED
- cranial_to_facial_relationship: BLOCKED

Verified source boundary:
- AtlasFrontalFaceMeasurer provides deterministic subject-specific normalized
  two-dimensional frontal-landmark measurements for face width, face height,
  eye spacing, nose width, nose length, mouth width, jaw width and forehead height.
- These measurements support bounded 2D observation-space proportions/surrogates only.
- They do not establish metric 3D anthropometric truth, canonical surface accuracy,
  subject anatomical ground truth or physical-output accuracy.
- Existing SYNTHETIC_NEUTRAL frontal reference ratios are calibration/reference priors only.
- Population/reference averages MUST NOT be promoted to identity targets.
- Existing jaw-width landmark measurement is only a 2D surrogate and MUST NOT be
  promoted to anatomical gonion-to-gonion ground truth.
- Existing eye-spacing measurement is 2D landmark evidence and MUST NOT be promoted
  to orbital or metric 3D anatomy.
- No verified subject-specific bizygomatic, upper/lower facial decomposition or
  cranial-to-facial measurement evidence exists in the audited evidence.
- FLAME benchmark head_ratio_support remains MISSING.
- PRNet benchmark head_ratio_support remains MISSING.
- No millimetre accuracy, population threshold, confidence score, benchmark score,
  global anthropometric PASS, Phase 8 final decision or Phase 9 authorization is claimed.

Evaluation spaces remain explicitly separated:
- 2d_observation
- canonical_model
- metric_3d_ground_truth
- physical_output

Evidence-origin states:
- directly_observed
- multiview_constrained
- model_prior_inferred
- generated_completion
- unresolved

Verification:
- focused: 19 passed
- related canonical-head: 886 passed, 11 warnings
- full regression: 5163 passed, 11 warnings
- warnings are existing NumPy pickle/deprecation warnings in the FLAME test path.

Phase 8 final decision remains unchanged.
Official Phase 9 remains NOT AUTHORIZED / NOT STARTED.

## PHASE8_ITEM9_10_CROSS_VIEW_REGIONAL_CONSISTENCY_EVIDENCE_CONTRACT_COMPLETE_2026_08_27

Phase 8 / Main Checklist Item 9.10 — Cross-View Regional Consistency
evidence contract is implemented and verified.

Contract:
- CORE/atlas_canonical_head_cross_view_regional_consistency_evidence.py
- Test/test_canonical_head_cross_view_regional_consistency_evidence.py

Locked Item 9.10 criteria:
- same_region_across_views
- view_conditioned_residual_behavior
- consistent_regional_improvement
- consistent_regional_degradation
- mixed_view_conditioned_behavior
- profile_sensitive_region_behavior
- coverage_consistency
- uniform_regional_success

Primary persistent evidence:
- REPRODUCIBILITY_ITEM8_9_REGION_WISE.json
- ITEM8_H1_NOSE_BODY_PER_LANDMARK_DIAGNOSIS.json
- ITEM8_H2_CANONICAL_3D_REGION_MEASUREMENT_RESULT.json
- ITEM8_H2_BOUNDED_3D_MAPPING_INTERPRETATION.json

Held-out protocol boundary:
- views: front, turn_left, turn_right
- measured regional comparisons: 21
- improved comparisons: 12
- degraded comparisons: 9
- unchanged comparisons: 0
- these are two-dimensional landmark/reprojection observation-space comparisons;
  they are NOT metric 3D anatomical measurements or regional surface-error measurements.

Coverage boundary:
- full coverage: 12/21 comparisons
  - left_eye: 3/3 full
  - right_eye: 3/3 full
  - nose_bridge: 3/3 full
  - upper_lip: 3/3 full
  - aggregate: 8 improved, 4 degraded
- partial_static105_overlap: 9/21 comparisons
  - lower_lip: 3/3 partial
  - nose_base: 3/3 partial
  - nose_body: 3/3 partial
  - aggregate: 4 improved, 5 degraded
- partial overlap MUST NOT be promoted to full semantic-region support or dense
  anatomical regional coverage.

Exact cross-view regional behavior:
- upper_lip:
  - CONSISTENT_IMPROVEMENT, full coverage, 3/3 views
  - front delta_px = -0.596790245425
  - turn_left delta_px = -0.195223703135
  - turn_right delta_px = -0.293216107193
- lower_lip:
  - CONSISTENT_IMPROVEMENT, partial_static105_overlap, 3/3 views
  - front delta_px = -0.418135292306
  - turn_left delta_px = -0.124998030645
  - turn_right delta_px = -0.076177947174
- nose_body:
  - CONSISTENT_DEGRADATION, partial_static105_overlap, 3/3 views
  - front delta_px = +0.529442151973
  - turn_left delta_px = +0.213729300156
  - turn_right delta_px = +0.313909213145
  - the Item 8 H1 nose_body 3/3 negative evidence therefore remains explicitly visible
- left_eye:
  - MIXED_VIEW_CONDITIONED, full coverage
  - 2 improved / 1 degraded
- right_eye:
  - MIXED_VIEW_CONDITIONED, full coverage
  - 1 improved / 2 degraded
- nose_bridge:
  - MIXED_VIEW_CONDITIONED, full coverage
  - 2 improved / 1 degraded
- nose_base:
  - MIXED_VIEW_CONDITIONED, partial_static105_overlap
  - 1 improved / 2 degraded

Claim boundary:
- aggregate multi-view consistency does NOT establish uniform regional consistency.
- 12/21 improving regional comparisons do NOT establish a global facial-region PASS.
- eye-region landmark evidence MUST NOT be promoted to orbital anatomical accuracy.
- nose_body partial-static105 evidence MUST NOT be promoted to dense anatomical
  nose-body segmentation.
- the repeated nose_body regression is bounded observation-space evidence; without
  independent metric 3D ground truth it MUST NOT be called true anatomical degradation.
- H2 canonical nose footprints remain barycentric-anchor-supported bounded mappings,
  not dense anatomical ground truth.
- jaw silhouette evidence remains a separate contour channel and is not promoted
  to canonical regional consistency.
- no millimetre accuracy, metric 3D regional consistency, regional surface accuracy,
  arbitrary threshold, global facial-quality PASS, Phase 8 final decision or
  Phase 9 authorization is claimed.
- profile-sensitive behavior remains bounded/partial; view-conditioned behavior alone
  is not promoted to verified anatomical profile correctness.

Evidence statuses:
- bounded_positive
- bounded_negative
- bounded_mixed
- bounded_partial
- not_established

Evaluation spaces remain explicitly separated:
- 2d_observation
- canonical_model
- metric_3d_ground_truth
- physical_output

Evidence-origin states:
- directly_observed
- multiview_constrained
- model_prior_inferred
- generated_completion
- unresolved

Verification:
- focused: 22 passed
- related canonical-head: 902 passed, 2 warnings
- full regression: 5185 passed, 11 warnings
- warnings are existing NumPy/FLAME pickle deprecation warnings and are not introduced
  by the Item 9.10 contract.

Phase 8 final decision remains unchanged.
Official Phase 9 remains NOT AUTHORIZED / NOT STARTED.

## Phase 8 / Main Checklist Item 9.11 — Cross-Region Compensation Audit

Marker: `PHASE8_ITEM9_11_CROSS_REGION_COMPENSATION_AUDIT_COMPLETE_2026_08_27`

Status: COMPLETE — bounded evidence/claim-boundary contract implemented and verified.

Implemented:
- `CORE/atlas_canonical_head_cross_region_compensation_evidence.py`
- `Test/test_canonical_head_cross_region_compensation_evidence.py`

Verified Item 9.11 classifications:
- `global_improvement_with_local_degradation` → `bounded_positive`
  - held-out global IOD-NME and bbox-NME improve in 3/3 views;
  - regional observation-space audit remains mixed: 12/21 improved, 9/21 degraded;
  - `nose_body` degraded in 3/3 held-out views;
  - global improvement does not establish uniform regional success.
- `camera_compensation` → `bounded_positive`
  - persisted H1 factorial/isolation evidence verifies material analytic weak-perspective camera compensation in all three held-out views;
  - this is observation-space compensation, not physical 3D correction and not proof of structural identity-camera leakage.
- `pose_compensation` → `not_established_as_primary_explanation`
  - pose-only effects do not reproduce the complete three-view `nose_body` regression pattern;
  - H3 pose-only counterfactuals preserve canonical identity state and identity-only canonical geometry exactly.
- `cross_region_compensation` → `bounded_mixed`
  - simultaneous regional improvements/degradations establish measurable cross-region performance trade-off;
  - no causal claim that one facial region compensates for another is established.
- `alignment_concealing_local_failure` → `bounded_positive`
  - the tested held-out root-pose + analytic weak-perspective camera-resolved evaluation path can reduce aggregate reprojection error while local `nose_body` failure remains visible;
  - this is not a universal claim about all alignment methods.

H3 boundary retained:
- pose may alter posed geometry without mutating canonical identity;
- expression may alter expression-dependent geometry without mutating canonical identity;
- weak-perspective camera changes projection while fixed 3D geometry and identity remain invariant;
- unconstrained identity refitting under nuisance stress was not tested;
- therefore global absence of optimizer leakage is not established.

Claim boundaries retained:
- 2D reprojection/landmark evidence is not metric 3D anatomical truth;
- no millimetre claim;
- no metric surface-accuracy claim;
- no arbitrary threshold or fabricated score;
- H2 anchor-supported nose footprints remain bounded and are not dense anatomy;
- Item 9.11 does not make a Phase 8 GO/HOLD decision;
- Official Phase 9 remains NOT AUTHORIZED / NOT STARTED.

Verification:
- focused: 21 passed;
- related canonical-head regression: 923 passed, 2 warnings;
- full regression: 5206 passed, 11 warnings;
- target diff check: exit 0.

## Phase 8 / Main Checklist Item 9.12 — Regional Surface Error

Marker: `PHASE8_ITEM9_12_REGIONAL_SURFACE_ERROR_EVIDENCE_CONTRACT_COMPLETE_2026_08_27`

Status: COMPLETE — `CAPABILITY_PRESENT_METRIC_RESULT_BLOCKED`.

Implemented:
- `CORE/atlas_canonical_head_regional_surface_error_evidence.py`
- `Test/test_canonical_head_regional_surface_error_evidence.py`

Verified capability:
- provider-independent point-to-surface distance implementation exists;
- raw metric aggregation supports mean, median, RMS, P95 and maximum;
- semantic region-wise raw aggregation capability exists when explicit
  region-to-sample mappings are legitimately supplied.

Current real metric-result boundary:
- no admissible real subject-specific regional surface-error result is available;
- HSRD-100 A03 branch is `CLOSED_AS_INADMISSIBLE_ALIGNMENT`;
- A03 metric-GT claim is `NOT_ADMISSIBLE`;
- strict-face millimetre execution remained unauthorized;
- no unique defensible scale-fixed rigid transform was established;
- Item 9 semantic regions have not been legitimately mapped to metric-GT
  scan samples with verified correspondence.

Item 9.12 classifications:
- `point_to_surface_distance` → `capability_present`;
- `mean_distance` → `capability_present`;
- `median_distance` → `capability_present`;
- `rms_distance` → `capability_present`;
- `p95_distance` → `capability_present`;
- `maximum_outlier_characterization` → `capability_present`;
- `bidirectional_symmetric_surface_error` → `not_established`;
- `surface_normal_discrepancy` → `not_established`;
- `real_metric_regional_result` →
  `capability_present_metric_result_blocked`.

Primary blocker states:
- `alignment_inadmissible`;
- `regional_correspondence_unverified`;
- `region_mapping_unverified`.

Claim boundaries retained:
- capability presence is not real-GT execution;
- synthetic/unit-test millimetre values are not subject-specific accuracy evidence;
- no jaw, chin, nose, orbital, cheek or other facial-region millimetre error
  may be claimed from current evidence;
- HSRD HOLD does not establish that FLAME geometry is poor;
- anchor-supported FLAME mappings are not scan-GT regional mappings;
- no metric surface-accuracy acceptance claim;
- no arbitrary threshold or fabricated confidence score;
- no Phase 8 GO/HOLD decision is made by Item 9.12;
- Official Phase 9 remains NOT AUTHORIZED / NOT STARTED.

Verification:
- focused: 24 passed;
- related canonical-head regression: 947 passed, 2 warnings;
- full regression: 5230 passed, 11 warnings;
- target diff check: exit 0.

## Phase 8 / Main Checklist Item 9.13 — Landmark-vs-Surface Agreement Audit

Marker: `PHASE8_ITEM9_13_LANDMARK_SURFACE_AGREEMENT_EVIDENCE_CONTRACT_COMPLETE_2026_08_27`

Status: COMPLETE — bounded agreement/disagreement evidence contract implemented and verified.

Implemented:
- `CORE/atlas_canonical_head_landmark_surface_agreement_evidence.py`
- `Test/test_canonical_head_landmark_surface_agreement_evidence.py`

Verified Item 9.13 classifications:
- `landmark_success_with_surface_failure` → `not_established`
  - landmark/reprojection success exists in bounded 2D observation-space channels;
  - no same-region independent admissible metric surface failure is currently available;
  - canonical-model displacement alone is not surface failure.
- `surface_success_with_landmark_failure` → `not_established`
  - no admissible real subject-specific metric regional surface-success result exists;
  - synthetic point-to-surface tests are not subject-specific surface-success evidence.
- `local_landmark_localization_uncertainty` → `unresolved`
  - current held-out and correspondence contracts do not expose verified per-landmark
    sigma, variance, covariance or equivalent localization-uncertainty evidence;
  - MediaPipe top-level provider confidence is not per-landmark uncertainty;
  - DSINE confidence is a separate residual-detail confidence channel.
- `regional_measurement_confidence_limitations` → `bounded_negative`
  - 9/21 held-out regional comparisons use `partial_static105_overlap`;
  - static105 has zero overlap with the 21 lower-jaw IDs and full 36-point face oval;
  - eye-region landmark evidence is not orbital anatomical surface evidence;
  - H2 nose footprints remain barycentric-anchor-supported bounded mappings;
  - real regional metric surface GT remains blocked.

Claim boundaries retained:
- `landmark_fit -> surface_accuracy` remains forbidden;
- `2d_reprojection -> metric_3d_accuracy` remains forbidden;
- landmark success is not surface success;
- canonical model-space geometry change is not metric anatomical failure;
- regional surface success/failure is not claimed without admissible metric GT;
- partial landmark coverage is not promoted to full semantic-region coverage;
- unknown landmark uncertainty is not treated as zero uncertainty;
- no surface-error millimetre result, landmark uncertainty number, arbitrary threshold,
  confidence score, Phase 8 final decision or Phase 9 authorization is introduced.

Verification:
- focused: 19 passed;
- related canonical-head regression: 966 passed, 2 warnings;
- full regression: 5249 passed, 11 warnings;
- target diff check: exit 0.

Official Phase 9 remains NOT AUTHORIZED / NOT STARTED.

## PHASE8_ITEM9_14_CUSTOMER_VISIBLE_LIKENESS_RISK_EVIDENCE_CONTRACT_COMPLETE_2026_08_27

- Main Checklist Item 9.14 — Customer-Visible Likeness Risk evidence contract added.
- New contract:
  `CORE/atlas_canonical_head_customer_visible_likeness_risk_evidence.py`
- New focused test:
  `Test/test_canonical_head_customer_visible_likeness_risk_evidence.py`
- Exact critical regions represented:
  `nose`, `jaw_chin`, `orbital_region`, `cheek_midface`,
  `head_silhouette_profile`.
- Region risk classifications:
  - nose: `BOUNDED_POTENTIAL_LIKENESS_RISK`;
  - jaw/chin: `BOUNDED_MIXED_LIKENESS_RISK`;
  - orbital region: `UNRESOLVED_LIKENESS_RISK`;
  - cheek/midface: `UNRESOLVED_LIKENESS_RISK`;
  - head silhouette/profile: `BOUNDED_MIXED_LIKENESS_RISK`.
- Overall Item 9.14 interpretation:
  `POTENTIAL_CUSTOMER_VISIBLE_RISK_NOT_VERIFIED`.
- Retained negative signal:
  `nose_body` degrades in `3/3` held-out observation-space views.
- Retained silhouette/profile trade-off:
  side-profile contour evidence improves while front-view contour error
  increases relative to baseline for the preferred bounded candidate.
- Current evidence does NOT establish verified customer-visible identity
  degradation, commercial likeness rejection, or metric anatomical failure.
- Pre-Phase-8 portrait visual rejection remains historical diagnostic evidence
  and is NOT promoted to rejection of the current canonical-head candidate.
- Academic geometric/landmark error is NOT equated automatically with
  commercial likeness acceptance or rejection.
- No customer-visible score, likeness score, acceptance threshold, commercial
  acceptance flag, Phase 8 decision, or Phase 9 authorization is introduced.
- Verification:
  focused `21 passed in 0.03s`;
  related canonical-head regression `987 passed, 2 warnings in 4.52s`;
  full regression `5270 passed, 11 warnings in 134.96s`;
  scoped `git diff --check`: `EXIT=0`.
- Phase 8 final decision remains unchanged.
- Official Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.
