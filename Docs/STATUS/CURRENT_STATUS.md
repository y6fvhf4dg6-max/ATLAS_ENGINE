# ATLAS_ENGINE — CURRENT STATUS

## Belgenin görevi

Bu dosya, ATLAS_ENGINE geliştirmesinin kesin güncel durumunu ve sıradaki tek işlemi tanımlar.

Yeni bir çalışma oturumunda önce:

- Docs/START_HERE.md
- Docs/STATUS/CURRENT_STATUS.md

okunmalıdır.

---

## Güncelleme tarihi

2026-07-30

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
