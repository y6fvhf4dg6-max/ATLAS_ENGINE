# ATLAS_ENGINE — START HERE

## Amaç

Bu belge, yeni bir ChatGPT sohbetinde ATLAS_ENGINE projesine kaldığı yerden devam etmek için ana giriş noktasıdır.

Yeni sohbette şu iki belge paylaşılmalıdır:

1. `Docs/START_HERE.md`
2. `Docs/STATUS/CURRENT_STATUS.md`

Yeni motor önce bu belgeyi, ardından `CURRENT_STATUS.md` dosyasını okumalı ve yalnızca belirtilen sıradaki adımdan devam etmelidir.

## Proje özeti

ATLAS_ENGINE iki ana ürün hattına sahiptir:

1. 3B şehir, terrain ve landmark ürünleri
2. 2.5B fotoğraf ve portre rölyef ürünleri

Aktif ticari öncelik:

`ATLAS My Life Map Wall Collection`

Temel fikir:

`Every important memory has a location.`

## Aktif ürün hattı

- Ürün ailesi: My Life Map Wall Collection
- İlk premium referans: Köln Pädagogische Fakultät
- Sonraki premium ürün: Bonn
- Köln fiziksel baskıyla doğrulanmadan nihai standart tamamen kilitlenmiş sayılmaz.

## Köln referans ürünü

- Merkez: `50.93428235, 6.91972655`
- Ölçek: `1:5500`
- PBF: `Data/OSM/koeln-paedagogische-fakultaet-test.osm.pbf`
- Ürün kaydı: `Docs/PRODUCTS/KOELN_PAEDAGOGISCHE_FAKULTAET_REFERENCE.md`

## Temel ürün ölçüleri

- Dış ölçü: `150 × 150 mm`
- Şehir açıklığı: `134 × 134 mm`
- Çerçeve genişliği: `8 mm`
- Çerçeve derinliği: `6 mm`
- Etiket plakası: `118 × 11 × 1.2 mm`
- Etiket alt çerçeve gömme miktarı: `5 mm`

## Yazı sistemi

- Font: DejaVu Sans Bold
- Primary nominal yükseklik: `4.2 mm`
- Secondary nominal yükseklik: `2.8 mm`
- Maksimum yazı genişliği: `108 mm`
- Yazı kabartma derinliği: `0.6 mm`
- Satır aralığı: `1.0 mm`
- Etiket ve yazı geometrisi şehir alanını küçültmeden veya taşımadan uygulanır.
- Bu etiket geometrisi Wall Collection v1 dijital standardı olarak kilitlenmiştir.
- Sonraki revizyon yalnız fiziksel baskı veya Bambu Studio doğrulamasından çıkan somut probleme göre yapılır.

## Fiziksel baskı standardı

- Hedef yazıcı: Bambu Lab P2S Combo
- Motor en fazla 5 fiziksel renk üretir.
- Köln Premium V1 renk paleti:

1. Beyaz:
   - terrain
   - yollar
   - normal bina duvarları
   - etiket plakası
2. Kırmızı:
   - bina çatıları
   - seçili Pädagogische Fakultät binasının tamamı
3. Yeşil:
   - parklar
   - yeşil alanlar
   - ağaçlar
4. Siyah:
   - çerçeve
   - etiket yazısı
   - mezuniyet kepi simgesi
5. Mavi:
   - deniz
   - nehir
   - göl
   - kanal

## Genel bina çatı geometrisi

- `roof:shape=pyramidal` olarak sınıflandırılan normal bina ve `building:part` kuleleri artık düz üst kapakla bırakılmaz.
- `AtlasBuildingPyramidalRoofBuilder`, mevcut düz üst yüzeyi kaldırır ve footprint sınırını merkez tepe noktasına bağlayan piramidal çatı üretir.
- Geçerli `roof:height` değeri ürün ölçeğine çevrilerek fiziksel çatı yüksekliği olarak korunur.
- Bu hat özellikle kilise, katedral ve bağımsız kule parçalarının gerçek siluetini korumak için kullanılır.
   - havuz

Köln sahnesinde mevcut su mesh'i bulunmadığı için ilk gerçek paket dört aktif renk üretmektedir: beyaz, kırmızı, yeşil ve siyah. Su içeren sahnelerde mavi STL otomatik olarak üretilir.

Motor semantik material gruplarını gerçek baskı renklerine birleştirerek aynı koordinat sisteminde ayrı STL dosyaları üretir.

## Fiziksel Köln baskısından aktarılan motor kazanımları

- İlk fiziksel Köln baskısında filament liflenmesi/stringing görüldü; bu konu baskı profili ve filament kalibrasyonu kapsamında çözülmelidir.
- Askı geometrisi ana motor seviyesinde revize edildi.
- Askı ölçüleri:
  - çivi başı girişi: 5.0 mm
  - kilit kanalı: 3.0 mm
  - kilitleme hareketi: 1.0 mm
  - üst kapalı taşıyıcı duvar: 1.75 mm
- Askı değişikliği 150, 200 ve 260 mm Wall Collection ürünlerinin tamamına uygulanır.
- Askı commit'i:
  - `404c0d2 Improve wall hanger nail retention`
- Wall Collection askı ve ürün regresyonu:
  - 28 passed
- Çok renkli üretim zinciri:
  - `AtlasProductColorPreviewRenderer`
  - `AtlasWallCollectionMulticolorSTLExporter`
  - `KOELN_PREMIUM_V1`
- Çok renkli zincir doğrulaması:
  - Renderer ve exporter odaklı paket: `20 passed`
- Köln gerçek multicolor STL topolojisi doğrulandı:
  - white: `0 open edge`, `0 non-manifold edge`
  - red: `0 open edge`, `0 non-manifold edge`
  - green: `0 open edge`, `0 non-manifold edge`
- Renderer seviyesinde uygulanan kalıcı topoloji kuralları:
  - aynı yükseklikte tamamen örtülen gereksiz `building:part` meshleri elenir
  - `leisure:park`, tamamen örttüğü `landuse:grass` yüzeyine öncelik verir
  - aynı renkli komşu parkların ortak iç sınır duvarları kaldırılır
  - yalnız tek noktada temas eden park katıları baskı toleransının altında ayrıştırılır
  - farklı yükseklikteki komşu bina renk katıları korunarak mikroskobik biçimde ayrıştırılır
- Aynı renk grubundaki birebir yinelenen üçgenler exporter seviyesinde tekilleştirilir.
- Kilit commit:
  - `9436dea Fix multicolor wall collection topology`

## İlk gerçek çok renkli üretim eşiği

Köln Pädagogische Fakultät ürünüyle ATLAS_ENGINE ilk kez gerçek çok renkli fiziksel üretime hazır uçtan uca ürün hattına ulaşmıştır.

Tamamlananlar:

- Dört hizalı semantik STL üretildi:
  - `white`
  - `red`
  - `green`
  - `black`
- Pädagogische Fakultät hedef binası tamamen kırmızı katmana ayrıldı.
- Siyah mezuniyet kepi simgesi etikete eklendi.
- Etiket metni:
  - `UNIVERSITÄT ZU KÖLN`
  - `PÄDAGOGISCHE FAKULTÄT`
- Bambu Studio assembly hizalaması doğrulandı.
- Filament atamaları yapıldı.
- Bambu Studio dilimlemesi başarıyla tamamlandı.
- Dilimleme sonucu:
  - yaklaşık `5 saat 4 dakika`
  - `96.36 g` filament
  - `60` filament değişimi
- Prime tower plaka sınırları içine taşındı ve G-code sınır hatası giderildi.
- AMS eşlemesi doğrulandı.
- Kilit kod commit'i:
  - `40cdf17 Add Köln graduation label and building highlight`

Nihai dört renkli referans baskı, sipariş edilen filamentler geldikten sonra alınacaktır.

Bambu Studio projesi ayrıca şu adla kaydedilmelidir:

`koeln_paedagogische_fakultaet_150mm_FINAL.3mf`

Bu eşik, ATLAS_ENGINE'in yalnız geometri üreten bir motor olmaktan çıkarak gerçek çok renkli baskı üretim hattına geçtiğini gösterir.

## Rölyef motoru preprocessing mimarisi

2.5B fotoğraf ve rölyef hattı artık genel, sıralı ve yeniden kullanılabilir bir preprocessing katmanına sahiptir.

Ana bileşenler:

- `AtlasReliefPreprocessorChain`
- `AtlasReliefPipeline.build_from_image(..., preprocessors=())`
- pipeline çıktısında `preprocessed_luminance`
- metadata içinde `preprocessor_count`

Bu mimariyle ürüne özgü görüntü düzeltmeleri geçici dosya üretmeden doğrudan ana rölyef pipeline'ına bağlanabilir.

İlk gerçek entegrasyon Dalyan kaya mezarları rölyef profilinde yapılmıştır. Kaya yüzeyindeki geniş ölçekli aydınlatma değişimi `AtlasRockReliefIlluminationNormalizer` üzerinden preprocessing zincirine alınmıştır.

Kilit commit'ler:

- `7c1782b Add relief preprocessor chain`
- `bbddbdd Route Dalyan relief normalization through preprocessors`

İlgili pipeline ve preprocessor doğrulaması:

- `70 passed`

Bu kazanım Dalyan'a özel bir geçici çözüm değil, tüm fotoğraf ve rölyef ürünlerinde kullanılabilecek genel motor mimarisidir.

İsimli kaya rölyefi preprocessing ve üretim preset sistemi:

- `AtlasRockReliefPreprocessingPreset` immutable ve callable preprocessing sözleşmesidir.
- İlk standart preprocessing preset'i:
  - `DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET`
- Preprocessing preset'i `illumination_sigma=14.0` ve `detail_strength=0.80` değerlerini kalıcı olarak taşır.
- `AtlasRockReliefProductionPreset` immutable üretim sözleşmesi eklendi.
- İlk standart üretim preset'i:
  - `DALYAN_ROCK_TOMBS_PRODUCTION_PRESET`
- Dalyan üretim preset'i şu bileşenleri tek nesnede birleştirir:
  - `ROCK_CARVED_LANDMARK`
  - `DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET`
- Preview scriptindeki anonim `lambda` ve dağınık profil/preprocessor bağlantıları kaldırıldı.
- Ürün profili ile preprocessing zinciri artık tek isimli üretim preset'i üzerinden kullanılır.
- `AtlasRockReliefProductionPreset.build_from_image(...)` kilitli ürün profili ve preprocessing zincirini ana rölyef pipeline'ına tek çağrıyla aktarır.
- Dalyan preview içindeki kilitli production varyantı artık `product_profile` ve `preprocessors` argümanlarını elle açmaz.
- Üretim preset'i, preprocessing preset'i, normalizer ve preprocessor chain odaklı doğrulama:
  - `14 passed`

## Ana belge yapısı

- `Docs/START_HERE.md`: yeni sohbet giriş belgesi
- `Docs/STATUS/CURRENT_STATUS.md`: kesin çalışma noktası
- `Docs/STANDARDS/`: genel ve kalıcı standartlar
- `Docs/PRODUCTS/`: ürünlere özgü teknik kayıtlar
- `Docs/STATUS/`: devir ve geliştirme durumları

## Belge öncelik sırası

Çelişki halinde:

1. `Docs/STATUS/CURRENT_STATUS.md`
2. `Docs/STANDARDS/`
3. `Docs/PRODUCTS/`
4. Roadmap ve plan belgeleri
5. Sohbet geçmişi

Repository belgeleri teknik gerçek için ana kaynaktır.

## Terminal çalışma disiplini

- Tüm dosya ve kod işlemleri terminalden yapılır.
- Bir seferde yalnızca bir terminal işlemi verilir.
- Kullanıcı çıktısı görülmeden sonraki adıma geçilmez.
- Manuel editör talimatı verilmez.
- `git add .` kullanılmaz.
- Yalnızca ilgili dosyalar stage edilir.
- Test-first ilerlenir.
- Yeşil adımlar commit edilir ve uygun noktada push edilir.
- Kullanıcı onayı olmadan başka konuya veya ürüne geçilmez.
- Çıktı üreten komutlar mümkün olduğunda `tee` ve `pbcopy` ile tamamlanır.

## Yeni motor için kesin talimat

Yeni motor:

1. Bu belgeyi okumalı.
2. `CURRENT_STATUS.md` belgesini esas almalı.
3. Gerekli ayrıntılar için ilgili ürün veya standart belgesini istemeli.
4. Tamamlanmış işleri yeniden başlatmamalı.
5. Yalnız sıradaki tek terminal işlemiyle devam etmelidir.

---

## Zorunlu dokümantasyon güncelleme kuralı

ATLAS_ENGINE geliştirmesinde kod ile dokümantasyon birlikte ilerler.

Her anlamlı geliştirme adımından sonra aşağıdaki sıra uygulanmalıdır:

1. Kod değişikliği tamamlanır.
2. İlgili testler çalıştırılır ve doğrulanır.
3. İlgili dokümantasyon güncellenir.
4. Tamamlanan kararlar kalıcı olarak kaydedilir.
5. Henüz tamamlanmayan maddeler açıkça belirtilir.
6. Sıradaki tek teknik işlem yazılır.
7. CURRENT_STATUS.md güncellenir.
8. Bundan sonra commit yapılır.

Dokümantasyon hiçbir zaman koddan geride bırakılmamalıdır.

Belge sorumlulukları:

- Docs/STANDARDS/
  Genel ve tüm ürünlere uygulanacak kurallar.

- Docs/PRODUCTS/
  Belirli bir ürüne ait teknik kararlar, doğrulamalar, istisnalar ve ilerleme durumu.

- Docs/STATUS/
  Projenin kesin güncel durumu ve sıradaki tek teknik adım.

Yeni bir geliştirme oturumunda bu çalışma yöntemi varsayılan kabul edilir.

### Dalyan kaya mezarları nihai rölyef varyantı

Görsel karşılaştırma sonucunda nihai üretim varyantı kilitlendi:

- Kaynak: illumination-normalized
- Ürün profili: `ROCK_CARVED_LANDMARK`
- Üretim preset'i: `DALYAN_ROCK_TOMBS_PRODUCTION_PRESET`
- Reddedilen alternatif: `rock-carved-landmark-detail`

Standart profil; mezar cephelerini ve oyma sınırlarını yeterli açıklıkta korurken,
detail profilindeki yüksek frekanslı kaya gürültüsünü baskıya taşımadığı için seçildi.

### Dalyan kaya mezarları fiziksel STL üretimi

Seçilen `DALYAN_ROCK_TOMBS_PRODUCTION_PRESET` sonucu artık genel rölyef STL export hattına bağlanmıştır.

Eklenen genel motor bileşeni:

- `CORE/atlas_relief_stl_exporter.py`
- `AtlasReliefSTLExporter.export_pipeline_result(...)`

Exporter:

- `relief_image_pipeline_result`
- içindeki `relief_result["mesh"]`
- ve mevcut `EXPORT.atlas_stl_writer.AtlasSTLWriter`

arasında ince, yeniden kullanılabilir bir üretim katmanı oluşturur.

Dalyan preview scripti artık kilitli production sonucunu doğrudan şu fiziksel STL dosyasına aktarır:

- `OUTPUT/RELIEF/dalyan_rock_tombs/dalyan_rock_tombs_relief_80x50mm.stl`

Doğrulanan üretim sonucu:

- fiziksel ölçü: `80 × 50 mm`
- üçgen sayısı: `95.036`
- solid adı: `DALYAN_ROCK_TOMBS_RELIEF`
- üretim varyantı: illumination-normalized + `ROCK_CARVED_LANDMARK`
- exporter focused test sonucu: `4 passed`

Sıradaki teknik işlem:

Dalyan STL dosyasının topolojisini, minimum kalınlığını ve fiziksel baskı uygunluğunu doğrulamak.


## Kalıcı üretim paketleri

ATLAS ürünleri yalnız geçici STL çıktıları olarak tutulmaz. Her tamamlanan lokasyon, daha sonra yeniden hazırlık yapılmadan basılabilecek kalıcı bir üretim paketi olarak saklanır.

Dalyan Kaya Mezarları için ilk relief üretim paketi:

- Paket: `OUTPUT/PRODUCTS/dalyan_rock_tombs_80x50mm/`
- Nihai STL: `STL/dalyan_rock_tombs_relief_80x50mm_FINAL.stl`
- Önizleme: `PREVIEW/dalyan_rock_tombs_FINAL_shaded.png`
- İşlenmiş kaynak: `SOURCE/rock_tombs_illumination_normalized.png`
- Kalite raporu: `REPORTS/print_quality_report.json`
- Manifest: `production_manifest.json`
- Planlanan nihai Bambu dosyası: `dalyan_rock_tombs_80x50mm_FINAL.3mf`

Mevcut Dalyan STL kapalı, manifold ve baskıya uygun topolojiye sahiptir. Çok renkli nihai ürün için renk/parça ayrımı ve Bambu Studio doğrulaması henüz tamamlanmamıştır.

## Relief semantik malzeme ayrımı

Çok renkli relief ürünlerinde yalnız gri ton eşiklerine göre renk ayrımı yapılmaz. Gri tonlar kaya, oyuk, gölge, bitki ve mimari cepheleri güvenilir biçimde ayıramadığı için renk üretimi semantik bölge maskeleri üzerinden yürütülür.

Yeni temel sözleşme:

- Modül: `CORE/atlas_relief_semantic_material_map.py`
- Test: `Test/test_relief_semantic_material_map.py`
- Varsayılan bölge bir ana malzemeye atanır.
- Adlandırılmış maskeler ayrı malzeme kimlikleri alır.
- Maskelerin relief çözünürlüğüyle aynı olması zorunludur.
- Üst üste binen maskeler reddedilir.

Dalyan Kaya Mezarları için planlanan ilk semantik sınıflar:

- `rock`
- `vegetation`
- `tomb_facade`

Bu aşamada gerçek Dalyan maskeleri ve çok renkli STL/3MF üretimi henüz tamamlanmamıştır.

## Relief semantik maske girişi

Semantik malzeme haritasında kullanılacak bölge maskeleri PNG gibi görüntü dosyalarından yüklenebilir.

Yeni giriş sözleşmesi:

- Modül: `CORE/atlas_relief_semantic_mask_input.py`
- Test: `Test/test_relief_semantic_mask_input.py`
- `L` ve `RGB` görüntüler gri tona dönüştürülür.
- Varsayılan eşik değeri `128`'dir.
- Eşik ve üzerindeki pikseller aktif maske bölgesi kabul edilir.
- Beklenen çözünürlük verilirse uyumsuz maskeler reddedilir.
- Eşik değeri `0..255` aralığında olmak zorundadır.

Bu modül yalnız maske dosyasını güvenli ve deterministik biçimde yükler. Gerçek Dalyan `vegetation` ve `tomb_facade` maskelerinin üretimi ayrı aşamadır.

## Relief semantik maske seti

- Modül: `CORE/atlas_relief_semantic_mask_set.py`
- Test: `Test/test_relief_semantic_mask_set.py`
- Birden fazla adlandırılmış PNG maskesini tek sözleşmede yükler.
- Her maske `AtlasReliefSemanticMaskInput` üzerinden doğrulanır.
- Maskeler `AtlasReliefSemanticMaterialMap` ile tek bir `uint8` malzeme kimlik haritasına dönüştürülür.
- Ortak görüntü boyutu zorunludur.
- Çakışan semantik bölgeler reddedilir.
- Varsayılan malzeme maskelenmemiş pikselleri temsil eder.

## Dalyan relief semantik maske sözleşmesi

- Modül: `CORE/atlas_dalyan_relief_semantic_masks.py`
- Test: `Test/test_dalyan_relief_semantic_masks.py`
- Aktif relief görüntü boyutu: `240 × 99`
- Varsayılan malzeme: `rock`
- Semantik maske yolları:
  - `Data/RELIEF/dalyan_rock_tombs/MASKS/vegetation_240x99.png`
  - `Data/RELIEF/dalyan_rock_tombs/MASKS/tomb_facade_240x99.png`
- Bu modül yalnız Dalyan sahnesine ait deterministik dosya ve boyut sözleşmesini tanımlar.
- Gerçek PNG maskelerinin üretilmesi ve pipeline entegrasyonu sonraki aşamadır.

## 31 Temmuz 2026 — Teknik paketlerin kalıcılaştırılması

Çalışma ağacında uzun süredir izlenmeyen durumda bulunan geliştirmeler incelendi. Körlemesine silme yapılmadı; her paket focused testlerle doğrulandı, ayrı commit edildi ve GitHub'a push edildi.

Kalıcılaştırılan paketler:

- `7585a68 Add MediaPipe relief landmark adapter`
  - Python 3.12 MediaPipe/OpenCV ortamı doğrulandı.
  - Yeniden kurulum listesi:
    `Docs/ENVIRONMENTS/requirements-landmarks-python312.txt`
  - Adapter testi: `17 passed`

- `056ab94 Add terrain contour generation system`
  - contour band, mesh, terrace ve orchestration katmanları
  - Focused test: `41 passed`

- `8952793 Add terrain-following landcover builder`
  - Terrain yüzeyini izleyen kapalı landcover geometrisi
  - Focused test: `9 passed`

- `798542e Add green area sampling and WorldCover aggregation`
  - Deterministik yeşil alan ağaç örnekleme
  - WorldCover hücrelerini yüzey gruplarına toplama
  - Focused test: `20 passed`

- `4ff45f1 Add relief normal processing pipeline`
  - normal height integrator
  - screened normal integrator
  - normal gradient limiter
  - structure/detail decomposition
  - confidence applier
  - Focused test: `101 passed`

- `0253fb2 Add relief face semantic calibration layers`
  - landmark regions
  - semantic detail weighting
  - structure confidence
  - anchor enhancement
  - interior calibration mask
  - detail composition
  - Focused test: `191 passed`

- `bff4629 Add relief semantic height adjustment`
  - Semantik maskelere göre kontrollü yükseklik ayarı
  - Focused test: `2 passed`

- `17f4f10 Improve ancient theatre and building relation handling`
  - Arkeolojik/harabe bağlamıyla antik tiyatro sınıflandırması
  - OSM building relation okuma iyileştirmeleri
  - Focused test: `16 passed`

- `34265d1 Refine Wall Collection label and material standards`
  - Etiket plakası ve çerçeve bandı uyumu
  - Malzeme profili ve landmark renk grubu
  - Askı ve ürün yerleşim standardı
  - Focused test: `52 passed`

Temizlik kararı:

- Eski Galata `end_taper` prototipi, daha genel ve doğrulanmış
  `road_approaches` hattı tarafından geçersiz kılındığı için silindi.
- Boş artık dosyalar `0:`, `255` ve `main` silindi.
- Eski `.bak` dosyaları güncel sürümlerle karşılaştırıldıktan sonra silindi.
- `.venv-landmarks` korunuyor; Relief/MediaPipe hattı için gerekli Python 3.12 ortamıdır.
- `Data/` klasörü üretim girdileri içerdiği için topluca silinmeyecektir.

Güncel teknik yön:

- Relief ve terrain altyapısındaki eski izlenmeyen çekirdek paketler artık ana dalda kalıcıdır.
- Yeni lokasyon geliştirmesine geçmeden önce preview, doküman, yardımcı test ve veri klasörleri son kez sınıflandırılacaktır.

## Yapılacaklar Listesi

### AtlasPhysicalDetailResolver v0.1

### Church Landmark Profile v0.1 Pilot

## 1 Ağustos 2026 — Bonn Church Landmark mimarisi

Bonn Münsterplatz Wall Collection ürünü aktif Church Landmark Profile v0.1 pilotudur.

Ürün ölçüleri:

- Dış ürün: `170 × 170 mm`
- Harita açıklığı: `150 × 150 mm`
- Çerçeve genişliği: `10 mm`
- Ölçek: `1:3000`
- Resmî yapı: Bonner Münster
- Etiket:
  - `BONN`
  - `GEBURTSORT`
  - doğum günü pastası simgesi

Kalıcılaştırılan kilise mimarisi:

- gerçek OSM footprint yönelimi
- gerçek footprint tabanlı kilise gövdesi
- kademeli dış nef ve ana nef gövdesi
- mimari çatı profil sistemi
- gable ve polygon-pyramid çatı geometrileri
- kilise kule profil sistemi
- polygon ve box kule gövdeleri
- polygon spire çatıları
- dış kulelerin gerçek footprint içine güvenli yerleştirilmesi
- merkez kule için iki kademeli sekizgen üst geçiş
- merkez kule külah yüksekliğinin fiziksel üst halka açıklığından türetilmesi

İlgili commit zinciri:

- `4930663 Orient church geometry to real footprint`
- `fe6027c Extrude church body from real footprint`
- `6aa954d Add church roof profile system`
- `26d4a38 Add church roof mesher`
- `168ab85 Integrate architectural church roofs`
- `e99fe7e Add stepped church body levels`
- `3601e5e Add church tower profile system`
- `a2f30f9 Add church tower mesher`
- `bff4d6f Integrate architectural church towers`
- `baa2cc2 Calibrate Bonner Münster tower proportions`
- `31d73ef Correct Bonner Münster outer tower placement`
- `5ddb18f Refine Bonner Münster outer tower proportions`
- `2d4f5d6 Place church outer towers from real footprint`
- `919f857 Refine crossing tower roof transition`
- `6ecdc41 Derive crossing tower spire height from roof span`
- `006aa15 Center cathedral crossing tower on transept`
- `c5f1266 Align crossing tower with resolved octagonal tower center`

Kule penceresi denemesi:

- Standalone pencere mesheri korunmaktadır:
  - `CORE/atlas_church_tower_window_mesher.py`
  - `Test/test_church_tower_window_mesher.py`
- İlk üretim entegrasyonu kapalı prizma çakışmaları ve görsel artefaktlar oluşturduğu için geri alınmıştır.
- Revert commit:
  - `d5df3a7 Revert "Integrate church tower windows"`
- Pencere sistemi daha sonra recessed/inlay ve yüzeye bağlı geometri olarak yeniden tasarlanmalıdır.

Bonn güncel STL üretimi:

- `OUTPUT/STL/bonn_muensterplatz_city_150mm.stl`
- `OUTPUT/STL/bonn_muensterplatz_wall_collection_170mm.stl`
- `OUTPUT/STL/bonn_muensterplatz_multicolor/bonn_muensterplatz_170mm__white.stl`
- `OUTPUT/STL/bonn_muensterplatz_multicolor/bonn_muensterplatz_170mm__red.stl`
- `OUTPUT/STL/bonn_muensterplatz_multicolor/bonn_muensterplatz_170mm__green.stl`
- `OUTPUT/STL/bonn_muensterplatz_multicolor/bonn_muensterplatz_170mm__black.stl`

Son üretim:

- şehir STL: `57.056` triangle
- final Wall Collection STL: `57.204` triangle
- white: `20.338`
- red: `9.982`
- green: `33.868`
- black: `148`

### Bonn için açık kritik sorun

Uzun külahlı merkez kule, görsel Bambu Studio doğrulamasında büyük sekizgen yapının tam merkezine oturmuş kabul edilmemiştir.

Önemli ayrım:

- `crossing_tower`: uzun külahlı kule
- `outer_polygon_tower`: büyük sekizgen yapı
- Profil oranlarını doğrudan eşitlemek yeterli değildir.
- `outer_polygon_tower` merkezi footprint-safe resolver tarafından üretim sırasında değiştirilmektedir.
- Son commit `c5f1266`, iki yapının çözümlenmiş yerel merkezlerini eşitlemeyi amaçlamaktadır.
- Buna rağmen kullanıcı görsel doğrulaması merkezlemenin hâlâ doğru olmadığını göstermiştir.
- Bu nedenle merkezleme işi **tamamlanmış veya kilitlenmiş değildir**.
- Yeni tahminî oran verilmemelidir.
- Bir sonraki adım, üretilen gerçek Bonn mesh halkalarının geometrik merkezlerini ve görsel olarak kastedilen sekizgen yapıyı yeniden doğrulamaktır.

Bonn için sıradaki tek teknik işlem:

Gerçek Bonn üretim meshinde uzun kulenin taban halkası ile kullanıcının kastettiği büyük sekizgen gövdenin gerçek taban/üst halka merkezlerini aynı koordinat sisteminde ölçmek; hedef gövde kesinleşmeden yeni yerleşim değişikliği yapmamak.

## 4 Ağustos 2026 — Master Landmark Catalog V1

Master Landmark Catalog V1 tamamlanmış ve ana branch'e push edilmiştir.

Son temiz commit:

- `afbf46f Drive bridge foundation components from catalog flags`

Son tam regresyon:

- `2162 passed in 9.27s`

Merkezi katalog şu landmark kararlarını yönetir:

- Bonn Münster kilise grameri ve geometri override'ı
- Kreuzkirche Bonn kilise grameri
- Galata Tower özel kule profili
- Galata Bridge özel köprü profili
- Galata Bridge support ve parapet bileşenleri

Kullanılan katalog alanları:

- `landmark_family`
- `grammar_name`
- `profile_name`
- `component_flags`
- `geometry_overrides`

`CORE/` üretim kodunda bu dört landmark için doğrudan sabit Wikidata
kararı kalmamıştır.

Güncel aktif öncelik yeniden Köln Premium V1 fiziksel baskı
doğrulamasıdır. Nihai filamentlerle baskı alınmalı; yalnız gerçek baskı
veya Bambu Studio sonucundan çıkan somut probleme göre revizyon
yapılmalıdır.

Bu bölüm, belgenin daha eski Bonn merkez-kule “bir sonraki adım”
kayıtlarına göre önceliklidir.

