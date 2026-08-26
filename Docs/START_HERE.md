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

## 5 Ağustos 2026 — Karaköy gerçek ibadethane doğrulaması

Son temiz ve push edilmiş kod commit’i:

- `aef280d Catalog Kılıç Ali Paşa Mosque grammar`

Son tam regresyon:

- `2267 passed in 9.88s`

Tamamlanan genel motor çalışması:

- building-part hiyerarşisinden cami grammar çıkarımı
- building-part hiyerarşisinden kilise kule grammar çıkarımı
- katalog grammar kararının component çıkarımına göre önceliği
- gerçek footprint içinde güvenli çoklu kubbe/minare yerleşimi
- component sayılarının üretim profil sınırlarında tutulması

İlgili commit:

- `5dbbffa Infer worship and church grammars from components`

Gerçek Karaköy doğrulama yapıları:

- Kılıç Ali Paşa Camii
  - OSM way `165574748`
  - Wikidata `Q862848`
- Surp Krikor Lusavoriç Ermeni Kilisesi
  - OSM way `165575977`
  - Wikidata `Q20472836`

İlk kontrolde Kılıç Ali Paşa Camii yalnız güvenli
`footprint_fallback` gövdesi üretti. Mesh kapalı ve manifold olmasına
rağmen cami olarak okunabilir değildi.

Master Landmark Catalog’a şu kayıt eklendi:

- key: `kilic-ali-pasha-mosque`
- family: `mosque`
- grammar: `single_dome_single_minaret`

Katalog bağlantısından sonraki production preview’da:

- ana kubbe
- kasnak
- tek minare
- şerefe
- minare külahı

başarıyla üretildi ve yapı cami olarak okunabilir hale geldi.

Surp Krikor Kilisesi üretimi korunmuştur:

- nef
- transept
- apsis
- çatı sistemi
- tek batı kulesi

Yerel görsel doğrulama çıktısı:

- `OUTPUT/STL/karakoy_kilic_ali_pasa_surp_krikor_catalog_preview_1_3000.stl`

Yerel PBF fixture ve preview STL `.gitignore` kapsamındadır; repoya
dahil edilmemiştir.

Bu sonuç grammar ve production-routing doğrulamasıdır; Kılıç Ali Paşa
Camii’nin tarihî rekonstrüksiyonu değildir. Landmark’a özel mesher
yazılmayacaktır. Gelecek kalite artışı genel Semantic Architecture,
facade/detail ve LoD sistemlerinden gelmelidir.

Karaköy doğrulama paketi tamamlanmıştır. Yeni Karaköy özel durumuna
geçilmeden roadmap ve ürün öncelikleri esas alınmalıdır.

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


# 7 Ağustos 2026 — Güncel roadmap girişi

Official LoD V1 tamamlandıktan sonra aktif ana roadmap paketi
**Automatic Print Optimization and Reporting** olarak devam etmektedir.

Tamamlanan ilk alt paket:

- [x] 7.1 `AtlasPrintOptimizationReport` contract

7.1 ile genel immutable print optimization report/issue veri sözleşmesi
oluşturuldu. Status/decision ile issue-code kavramları birbirinden ayrıldı.
Bu aşamada fiziksel analiz algoritmaları production pipeline'a bağlanmadı.

Doğrulama:

- focused: `15 passed in 0.02s`
- print/quality related regression: `81 passed in 0.32s`
- full regression: `2700 passed in 12.55s`

Sıradaki tek roadmap adımı:

- **7.2 Minimum wall/thickness analysis**

Yeni oturumda `Docs/STATUS/CURRENT_STATUS.md` içindeki
`7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.1`
bölümü güncel kesin çalışma noktası olarak esas alınmalıdır.


## 7 Ağustos 2026 — Print Optimization 7.2

Automatic Print Optimization and Reporting ilerleme durumu:

- [x] 7.1 `AtlasPrintOptimizationReport` contract
- [x] 7.2 Minimum wall/thickness analysis

7.2 ile genel ve landmark-bağımsız minimum thickness değerlendirme
sözleşmesi eklendi.

Doğrulama:

- focused: `20 passed in 0.02s`
- ilgili regression: `51 passed in 0.09s`
- full regression: `2720 passed in 12.31s`

Sıradaki tek roadmap adımı:

- **7.3 Overhang/support analysis**

Güncel kesin ayrıntılar için `Docs/STATUS/CURRENT_STATUS.md` içindeki
`7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.2`
bölümü esas alınmalıdır.


## 7 Ağustos 2026 — Print Optimization 7.3

Automatic Print Optimization and Reporting ilerleme durumu:

- [x] 7.1 `AtlasPrintOptimizationReport` contract
- [x] 7.2 Minimum wall/thickness analysis
- [x] 7.3 Overhang/support analysis

7.3 ile genel ve landmark-bağımsız overhang/support değerlendirme
sözleşmesi eklendi. Relief slope sistemi değiştirilmedi.

Doğrulama:

- focused: `22 passed in 0.02s`
- ilgili regression: `77 passed in 0.12s`
- full regression: `2742 passed in 12.31s`

Sıradaki tek roadmap adımı:

- **7.4 Fragile connection analysis**

Güncel kesin ayrıntılar için `Docs/STATUS/CURRENT_STATUS.md` içindeki
`7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.3`
bölümü esas alınmalıdır.


## 7 Ağustos 2026 — Print Optimization 7.4

Automatic Print Optimization and Reporting ilerleme durumu:

- [x] 7.1 `AtlasPrintOptimizationReport` contract
- [x] 7.2 Minimum wall/thickness analysis
- [x] 7.3 Overhang/support analysis
- [x] 7.4 Fragile connection analysis

7.4 ile genel ve landmark-bağımsız fragile connection analizi eklendi.

Temel ölçüt:

- `connection_width_mm / component_span_mm`

Bu analiz 7.2 mutlak thickness kontrolünden ayrı tutulur.

Doğrulama:

- focused final: `28 passed in 0.03s`
- ilgili regression: `86 passed in 0.22s`
- full regression: `2770 passed in 12.33s`

Sıradaki tek roadmap adımı:

- **7.5 Nozzle-based detail analysis**

Güncel kesin ayrıntılar için `Docs/STATUS/CURRENT_STATUS.md` içindeki
`7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.4`
bölümü esas alınmalıdır.


## 7 Ağustos 2026 — Print Optimization 7.5

Automatic Print Optimization and Reporting ilerleme durumu:

- [x] 7.1 `AtlasPrintOptimizationReport` contract
- [x] 7.2 Minimum wall/thickness analysis
- [x] 7.3 Overhang/support analysis
- [x] 7.4 Fragile connection analysis
- [x] 7.5 Nozzle-based detail analysis

7.5 ile genel ve landmark-bağımsız nozzle/detail audit sözleşmesi eklendi.

Temel karar:

- detail ölçüsü nozzle çapından küçükse `below nozzle`
- eşit veya büyükse safe

`AtlasPhysicalDetailResolver` değiştirilmedi; production-side
`preserve / enlarge / omit` mantığı ayrı tutuldu.

Doğrulama:

- focused: `25 passed in 0.02s`
- ilgili regression: `103 passed in 0.15s`
- full regression: `2795 passed in 12.37s`

Sıradaki tek roadmap adımı:

- **7.6 Color-change analysis**

Güncel kesin ayrıntılar için `Docs/STATUS/CURRENT_STATUS.md` içindeki
`7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.5`
bölümü esas alınmalıdır.


## 7 Ağustos 2026 — Print Optimization 7.6

Automatic Print Optimization and Reporting ilerleme durumu:

- [x] 7.1 `AtlasPrintOptimizationReport` contract
- [x] 7.2 Minimum wall/thickness analysis
- [x] 7.3 Overhang/support analysis
- [x] 7.4 Fragile connection analysis
- [x] 7.5 Nozzle-based detail analysis
- [x] 7.6 Color-change analysis

7.6 ile gerçek slicer/production color-change sayısını audit eden
genel sözleşme eklendi.

Önemli ayrım:

- `color_count` / `part_count` gerçek color-change sayısı değildir.
- 7.6 yalnız ölçülmüş `color_change_count` üzerinden karar verir.

Doğrulama:

- focused: `20 passed in 0.02s`
- ilgili regression: `91 passed in 0.11s`
- full regression: `2815 passed in 12.52s`

Sıradaki tek roadmap adımı:

- **7.7 Triangle/file-count analysis**

Güncel kesin ayrıntılar için `Docs/STATUS/CURRENT_STATUS.md` içindeki
`7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.6`
bölümü esas alınmalıdır.


## 7 Ağustos 2026 — Print Optimization 7.7

Automatic Print Optimization and Reporting ilerleme durumu:

- [x] 7.1 `AtlasPrintOptimizationReport` contract
- [x] 7.2 Minimum wall/thickness analysis
- [x] 7.3 Overhang/support analysis
- [x] 7.4 Fragile connection analysis
- [x] 7.5 Nozzle-based detail analysis
- [x] 7.6 Color-change analysis
- [x] 7.7 Triangle/file-count analysis

7.7 ile triangle count ve file count iki bağımsız üretim karmaşıklığı
sinyali olarak audit edilmektedir.

Önemli ayrım:

- 7.7 mevcut STL writer veya multicolor exporter sayaçlarını yeniden üretmez.
- analyzer yalnız verilen gerçek count değerlerini threshold'lara karşı değerlendirir.
- otomatik mesh simplification veya dosya birleştirme yapılmaz.

Doğrulama:

- focused: `31 passed in 0.02s`
- ilgili regression: `88 passed in 0.20s`
- full regression: `2846 passed in 12.33s`

Sıradaki tek roadmap adımı:

- **7.8 Aggregate optimizer/report builder**

Güncel kesin ayrıntılar için `Docs/STATUS/CURRENT_STATUS.md` içindeki
`7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.7`
bölümü esas alınmalıdır.


## 7 Ağustos 2026 — Print Optimization 7.8

Automatic Print Optimization and Reporting ilerleme durumu:

- [x] 7.1 `AtlasPrintOptimizationReport` contract
- [x] 7.2 Minimum wall/thickness analysis
- [x] 7.3 Overhang/support analysis
- [x] 7.4 Fragile connection analysis
- [x] 7.5 Nozzle-based detail analysis
- [x] 7.6 Color-change analysis
- [x] 7.7 Triangle/file-count analysis
- [x] 7.8 Aggregate optimizer/report builder

7.8 ile 7.1–7.7 analizleri tek genel
`AtlasPrintOptimizationReport` içinde aggregate edilmektedir.

Final status precedence:

- `MUST_THICKEN`
- `SUPPORT_REQUIRED`
- `MUST_SIMPLIFY`
- `WARNING`
- `PRINTABLE`

Builder yalnız report üretir; geometri, slicer, exporter veya LoD davranışını
değiştirmez.

Doğrulama:

- focused: `19 passed in 0.03s`
- 7.1–7.8 regression: `180 passed in 0.13s`
- geniş regression: `239 passed in 0.31s`
- full regression: `2865 passed in 12.31s`

Sıradaki tek roadmap adımı:

- **7.9 Real production validation**

Güncel kesin ayrıntılar için `Docs/STATUS/CURRENT_STATUS.md` içindeki
`7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.8`
bölümü esas alınmalıdır.


## 7 Ağustos 2026 — Print Optimization 7.9

Automatic Print Optimization and Reporting ilerleme durumu:

- [x] 7.1 `AtlasPrintOptimizationReport` contract
- [x] 7.2 Minimum wall/thickness analysis
- [x] 7.3 Overhang/support analysis
- [x] 7.4 Fragile connection analysis
- [x] 7.5 Nozzle-based detail analysis
- [x] 7.6 Color-change analysis
- [x] 7.7 Triangle/file-count analysis
- [x] 7.8 Aggregate optimizer/report builder
- [x] 7.9 Real production validation

7.9 ile genel read-only Bambu `.3mf` production validator eklendi.

Gerçek Köln FINAL production artifact doğrulaması:

- object faces: `64776`
- part faces: `64776`
- parts: `4`
- mesh repairs: `0`
- printer: `Bambu Lab P2S`
- nozzle: yaklaşık `0.4 mm`
- layer height: `0.2 mm`
- support: disabled
- bed: `textured_plate`
- structurally valid: `True`

Validator mevcut `.3mf` içinde güvenilir olmayan print time, filament gramı
ve color-change count değerlerini tahmin etmez.

Doğrulama:

- focused: `8 passed in 0.04s`
- ilgili regression: `192 passed in 0.18s`
- full regression: `2873 passed in 12.34s`

Sıradaki tek roadmap adımı:

- **7.10 Full regression + documentation + final lock**

Güncel kesin ayrıntılar için `Docs/STATUS/CURRENT_STATUS.md` içindeki
`7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.9`
bölümü esas alınmalıdır.


## 7 Ağustos 2026 — Print Optimization 7.10 FINAL LOCK

**Automatic Print Optimization and Reporting V1 tamamlandı ve kilitlendi.**

Final roadmap:

- [x] 7.1 Report contract
- [x] 7.2 Minimum thickness
- [x] 7.3 Overhang/support
- [x] 7.4 Fragile connection
- [x] 7.5 Nozzle detail
- [x] 7.6 Color changes
- [x] 7.7 Triangle/file count
- [x] 7.8 Aggregate report builder
- [x] 7.9 Real Bambu 3MF production validation
- [x] 7.10 Final regression + documentation + lock

Final production-analysis zinciri:

- thickness
- overhang/support
- fragile connection
- nozzle detail
- real slicer color-change measurement
- triangle/file count
- aggregate print optimization report
- read-only Bambu `.3mf` structural validation

Final aggregate status precedence:

`MUST_THICKEN > SUPPORT_REQUIRED > MUST_SIMPLIFY > WARNING > PRINTABLE`

Gerçek Köln production artifact:

- `64776` object faces
- `64776` part faces
- `4` parts
- `0` mesh repairs
- Bambu Lab P2S
- yaklaşık `0.4 mm` nozzle
- `0.2 mm` layer height
- support disabled
- textured plate
- structurally valid

Final tests:

- 7.1–7.9 package regression: `188 passed in 0.15s`
- full regression: `2873 passed in 12.30s`

Bu V1 geometriyi otomatik değiştirmez ve bulunmayan slicer ölçümlerini tahmin
etmez.

Güncel kesin durum için `Docs/STATUS/CURRENT_STATUS.md` içindeki
`7 Ağustos 2026 — Automatic Print Optimization and Reporting 7.10 FINAL LOCK`
bölümü esas alınmalıdır.

## 7 Ağustos 2026 — ACTIVE ROADMAP: Urban Fabric & Product Composition V1

Automatic Print Optimization and Reporting V1 tamamlandı ve kilitlendi.

Yeni aktif geliştirme paketi:

`Docs/Roadmap/URBAN_FABRIC_PRODUCT_COMPOSITION_V1.md`

Baseline güvenli commit:

`50daf58a00e31dd99f403af5eb8a6ac2edef3bba`

Ana hedef:

`best-in-class urban coherence + ATLAS landmark intelligence + ATLAS LoD/print infrastructure`

İlk kontrollü benchmark:

- Bonn
- center: `50.733270, 7.100440`
- product size: `140 × 140 mm`
- coverage: `0.44 km²`
- equivalent scale: yaklaşık `1:4738`
- output: `OUTPUT/STL/bonn_lichtbild_14cm_exact_0_44km2.stl`
- meshes: `922`
- triangles: `70798`

### 8.0 Bonn Urban Fabric Ground-Truth Audit — TAMAMLANDI

8.0 read-only audit tamamlandı; production davranışı değiştirilmedi.

Ana sonuç:

- Bonn'daki temel problem genel olarak source truth eksikliği değil.
- Railway ve pedestrian fabric gibi bazı source sınıfları production'a
  taşınmıyor.
- Hofgarten ve water gibi bazı öğeler production'da mevcut fakat semantic
  expression / metadata zayıf.
- WorldCover vegetation mevcut şehir bağlamından bağımsız isolated tree
  üretimi nedeniyle clutter oluşturuyor.
- Generic building height ve building-part vertical interval için genel bir
  parser/geometri bug doğrulanmadı.
- Urban blocks doğal olarak yoğun; mevcut minimum-size filtering zaten aktif.
- Terrain exact benchmarkta SRTM yerine COP30 fallback kullandı; belirgin
  scaling bug bulunmadı fakat provider provenance downstream'de kayboluyor.

Detaylı audit sonucu:
`Docs/Roadmap/URBAN_FABRIC_PRODUCT_COMPOSITION_V1.md`

### 8.1 Urban Fabric Scene Contract — TAMAMLANDI

8.1 test-first tamamlandı.

Yeni immutable semantic contract katmanı:

- `AtlasUrbanFabricElement`
- `AtlasUrbanFabricRelationship`
- `AtlasUrbanFabricScene`

Contract artık source identity, semantic class, product priority,
LoD eligibility, geometry reference ve urban-element relationships
bilgilerini koruyor.

Minimum Urban Fabric V1 semantic kapsamı road, railway, pedestrian path,
urban block, generic building, park, plaza, vegetation, water,
infrastructure corridor ve terrain sınıflarını içeriyor.

Semantic class sistemi extensible kalır; bu liste kapalı enum değildir.

Doğrulama:

- focused: `40 passed`
- related: `120 passed in 0.53s`
- full: `2913 passed in 12.75s`

8.1 final production geometry davranışını değiştirmedi.

### 8.2 Road Hierarchy Engine — TAMAMLANDI

8.2 test-first tamamlandı.

Yeni ana sözleşmeler:

- `AtlasUrbanRoadProfile`
- `AtlasUrbanRoadHierarchyResolver`

Road hierarchy artık source highway sınıflarını major road, local road,
service road ve pedestrian path product semantics altında çözüyor.

Fiziksel genişlik çözümü source `width=*`, mevcut vehicle defaultları,
product scale ve explicit printable minimum bilgisini birlikte kullanıyor.

Pedestrian path source width yoksa gerçek-metre genişliği uydurulmuyor;
explicit printable minimum kullanılıyor.

Relative hierarchy:

`major_road > local_road > service_road > pedestrian_path`

`cycleway` ve `bridleway` semantic olarak tanınıyor ancak fiziksel corridor
davranışları 8.3 Linear Infrastructure Engine'e bırakıldı.

Production entegrasyonu opt-in:

- road builder: `minimum_printable_width_mm=None`
- FoundationFirst: `road_minimum_printable_width_mm=None`

Default `None` olduğu için mevcut ürün davranışı sessizce değiştirilmedi.

Doğrulama:

- focused + integration: `69 passed`
- related: `82 passed in 1.25s`
- full: `2982 passed in 12.70s`

### 8.3 Linear Infrastructure Engine — TAMAMLANDI / LOCKED

8.3 test-first tamamlandı.

Ana sistem:

- `AtlasLinearInfrastructureResolver`
- `AtlasLinearInfrastructureGeometryBuilder`
- `AtlasLinearInfrastructureSolidBuilder`

Kapsam:

- railway / light rail / tram
- cycle / bridleway corridors
- pedestrian paths
- embankments
- infrastructure corridors
- active / proposed / disused state
- surface visibility
- vertical treatment
- source-driven physical width
- printable minimum width
- gauge-aware parallel-line readability
- LoD eligibility
- linear-strip / area-strip geometry
- product XY footprint
- terrain-following closed solid

`AtlasLocalOSMReader` artık linear infrastructure verisini toplar ve
`read()` sonucunda expose eder.

Anıtkabir cycleway regression'ı yeni semantic contract'a geçirildi:
way `883691085` artık `cycle_corridor` olarak korunur.

Bonn exact benchmark'ta product-surface eligible infrastructure:
`3 tram + 1 landuse=railway corridor`.

Doğrulama:

- focused: `102 passed in 0.09s`
- related: `105 passed in 0.35s`
- full: `3085 passed in 12.59s`

Son güvenli/push edilmiş commit hâlâ:

`e75cb10d64d8e2ab3f52fd88a7c9df12ce1bea3c`

8.3 commit henüz oluşturulmadı.

### Sıradaki tek adım

**8.4 Urban Block Resolver**

8.4 test-first yürütülecek.

Generic building grupları block-aware composition altında çözülecek;
source footprint, courtyard, semantic landmark ve mevcut LoD sözleşmeleri
korunacak.

8.4 tamamlanmadan 8.5 veya sonraki behavior başlamaz.

Detaylı teknik sözleşme, roadmap, kısıtlar ve acceptance kriterleri için:

`Docs/Roadmap/URBAN_FABRIC_PRODUCT_COMPOSITION_V1.md`

Güncel operasyonel durum için:

`Docs/STATUS/CURRENT_STATUS.md`

### 8.4 Urban Block Resolver — TAMAMLANDI

8.4 test-first tamamlandı.

Kilitlenen ana davranışlar:

- road-defined urban block polygonization
- generic-building block membership
- deterministic exclusive multi-block assignment
- source-footprint and courtyard preservation
- block density and shared-boundary metrics
- local median-height and landmark-proximity reporting
- existing LoD level pass-through
- `urban_block` scene integration with `contains_building` relationships

Doğrulama:

- focused: `39 passed in 0.06s`
- related: `379 passed in 0.35s`
- full: `3124 passed in 12.86s`

### Sıradaki tek adım

**8.5 Park & Plaza Semantic Surface Engine**

### 8.5 Park & Plaza Semantic Surface Engine — TAMAMLANDI

8.5 test-first tamamlandı.

Kilitlenen ana davranışlar:

- park / garden / plaza / pedestrian_square / courtyard / grass_area / cemetery / sports_field semantics
- immutable semantic profile contract
- distinct ground surface roles
- profile-aware deterministic composition layers
- source record enrichment without mutation
- internal paths / tree rows / vegetation clusters / clearings / borders / edges metadata preservation
- plaza ve pedestrian-square için park-only composition suppression
- geometry-derived courtyard semantics
- reader `pedestrian_paths` koleksiyonundan park içi path çözümü
- boundary-crossing path rejection
- internal path deduplication and deterministic ordering

Doğrulama:

- focused: `35 passed in 0.05s`
- related: `206 passed in 0.24s`
- full: `3159 passed in 12.98s`

### Sıradaki tek adım

**8.6 Vegetation Composition Engine**

### 8.6 Vegetation Composition Engine — TAMAMLANDI

8.6 test-first tamamlandı ve production vegetation hattına bağlandı.

Kilitlenen ana davranışlar:

- `isolated_tree` / `tree_row` / `tree_cluster` / `forest_canopy` semantic rolleri
- source-context-aware vegetation resolution
- gerçek OSM tree kayıtlarının isolated tree olarak korunması
- WorldCover sampled tree kayıtlarının tekil ağaç olarak kullanılmaması
- WorldCover forest hücrelerinin deterministic spatial canopy gruplarına ayrılması
- source `resolution_m` değerinin connectivity kararında kullanılması
- WorldCover double representation'ın engellenmesi
- forest canopy polygonlarının mevcut WorldCover dissolve hattıyla üretilmesi
- kapalı/manifold `forest_canopy_foundation` fiziksel temsili
- FoundationFirstEngine production entegrasyonu
- `mesh_groups["forest_canopies"]`
- preview'da `forest_canopies → trees` material batch
- multicolor output'ta canopy'nin green STL içine taşınması
- `castle_only` vegetation suppression davranışının korunması

8.6 sınırları:

- tree-row detection / physical row producer 8.7 kapsamındadır
- avenue / boulevard / promenade alignment çözümü 8.7 kapsamındadır
- Bonn/Hofgarten-specific kural eklenmedi

Doğrulama:

- focused vegetation resolver: `51 passed in 0.07s`
- vegetation + engine integration: `57 passed in 0.16s`
- related regression: `154 passed in 0.36s`
- full regression: `3217 passed in 12.60s`

### 8.7 Avenue Tree Row Engine — TAMAMLANDI

8.7 test-first tamamlandı ve production vegetation hattına bağlandı.

Kilitlenen ana davranışlar:

- gerçek OSM `natural=tree_row` way ingestion
- reader ve nature-provider tree-row evidence merge
- source geometry, direction ve segment diagnostic çözümü
- strong / weak evidence classification
- gerçek iki noktalı OSM tree-row kayıtlarının desteklenmesi
- OSM way vertexlerinin gerçek tree spacing olarak yorumlanmaması
- explicit tree spacing desteği
- product-readability fallback spacing
- fallback spacing'in fiziksel tree-symbol çapı + nozzle üzerinden çözülmesi
- deterministic polyline layout
- controlled `park_tree_symbol` member üretimi
- deterministic row ordering
- gerçek XY scale ve nozzle-aware production davranışı
- nearby parallel road / pedestrian-path context resolution
- crossing / non-parallel context rejection
- 20 m adjacency sınırı
- source-gap diagnostic resolution
- büyük source gap'lerin yapay ağaçlarla doldurulmaması
- row context metadata'nın production member kayıtlarına taşınması
- final engine metadata:
  - `reader_tree_rows`
  - `tree_row_members`

Gerçek veri doğrulaması:

- Köln Regierungsbezirk:
  - `7408` gerçek `natural=tree_row` way
  - naive current-model members: `88639`
  - gap-aware members: `83250`
  - source-gap preservation ile `5389` yapay member bastırıldı
  - `363` row gerçek üretim davranışında etkilendi
- Köln Pädagogische Fakultät referans sahnesi:
  - `6` gerçek tree row
  - `6/6` strong
  - `58` controlled tree-row member
  - `0` source gap
  - `5/6` row geçerli paralel road/path context ile eşleşti
  - gerçek STL / Bambu Studio görünümünde formal tree rhythm belirgin biçimde doğrulandı

Doğrulama:

- focused tree-row regression: `70 passed in 0.36s`
- related vegetation / park / nature / engine regression: `156 passed in 0.35s`
- full regression: `3267 passed in 12.78s`

### Sıradaki tek adım

**8.8 Semantic Surface Texture Engine**



## 9 Ağustos 2026 — Urban Fabric 8.8 + 8.9

Son güvenli ve uzak depoya push edilmiş commit:

- `1607154 Add semantic surfaces and morphology-aware terrain`
- branch: `main`
- `HEAD == origin/main`

### 8.8 Semantic Surface Texture Engine — TEKNİK OLARAK YEŞİL / GÖRSEL ACCEPTANCE AÇIK

8.8 kapsamında semantic open-surface fiziksel dili production hattına eklendi.

Ana yetenekler:

- park / grass / plaza / pedestrian-square / garden / cemetery /
  sports-field / courtyard semantic surface profilleri
- deterministic shallow-relief pattern üretimi
- terrain-following semantic surface mesh üretimi
- Foundation First production entegrasyonu
- source semantic identity preservation
- dense boundary contract
- constrained surface triangulation
- tolerance-aware shared-edge handling
- deterministic interior-edge refinement

Gerçek Köln topology problemi çözüldü:

- önceki textured park open edges: `1340`
- düzeltme sonrası textured park open edges: `0`

Topology fix sonrası görsel olarak tespit edilen uzun radial/fan interior
triangle problemi ayrıca çözüldü.

Kalıcı regression:

- `test_semantic_surface_limits_long_interior_edges`

Refinement sonrası gerçek Köln:

- city triangles: `43122`
- preview triangles: `49856`
- tüm textured park yüzeylerinde `> 2 × pitch`: `0`
- tüm textured park yüzeylerinde `> 4 × pitch`: `0`
- textured park open edges: `0`

Son preview:

- `OUTPUT/PREVIEW/koeln_paedagogische_fakultaet_competitor_comparison_v1.png`

8.8 için kalan tek acceptance:

- son `49856` triangle Köln preview'ın nihai görsel değerlendirmesi

Bu nedenle 8.8 henüz LOCK olarak işaretlenmedi.

### 8.9 Morphology-Aware Terrain Product Resolver — TAMAMLANDI

8.9 test-first geliştirildi ve terrain pipeline'a entegre edildi.

Yeni ana modül:

- `CORE/atlas_morphology_aware_terrain_product_resolver.py`

Desteklenen morphology sınıfları:

- `dense_urban`
- `historic_core`
- `suburban`
- `rural`
- `mountain`
- `landscape_nature`

Resolver:

- mevcut terrain pipeline'ını terrain truth kaynağı olarak korur
- source elevation verisini değiştirmez
- morphology-aware terrain emphasis üretir
- product size değerini dikkate alır
- urban density bilgisini taşır
- landmark presence üzerinden semantic-content protection sinyali üretir
- fiziksel terrain relief'i printable min/max aralığına resolve eder
- deterministic product-facing terrain profile üretir

Terrain pipeline entegrasyonu:

- 8.9 parametreleri verilmezse legacy davranış değişmez
- `delta_height_m` mevcut terrain truth üzerinden alınır
- fiziksel relief:
  `delta_height_m / z_scale * 1000`
- resolver sonucu:
  `metadata["terrain_product_profile"]`
- terrain grid değiştirilmez
- `delta_height_m` değiştirilmez
- `z_scale` değiştirilmez

Doğrulama:

- resolver focused: `13 passed in 0.02s`
- resolver + pipeline focused: `16 passed in 0.06s`
- 8.8 + 8.9 related regression: `102 passed in 2.11s`
- full regression: `3338 passed in 15.03s`

### Sıradaki tek adım

**8.8 son Köln preview görsel acceptance.**

Bu acceptance tamamlandıktan sonra roadmap sırasındaki:

**8.10 Water & Shoreline Composition Engine**

paketine geçilecek.


## 9 Ağustos 2026 — 8.9 Terrain Sampling & Presentation Update

### 8.9 Morphology-Aware Terrain Product Resolver — AKTİF / LOCK DEĞİL

8.9 terrain incelemesi Köln Pädagogische Fakultät gerçek ürün sahnesi
üzerinde derinleştirildi.

Önemli mimari bulgular:

- canonical terrain truth ile fiziksel terrain triangulation arasında
  ölçülebilir Z farkı bulundu
- mevcut 25 x 25 terrain grid'de:
  - mean truth/mesh farkı: `0.084182 mm`
  - p95: `0.241056 mm`
  - p99: `0.318434 mm`
  - maksimum: `0.486493 mm`
- canonical terrain'i daha yoğun presentation grid ile örneklemek bu farkı
  belirgin biçimde düşürdü
- 97 x 97 presentation referansında maksimum fark:
  `0.030406 mm`

Köln terrain kaynağı doğrulandı:

- Köln için local `N50E006.hgt` mevcut değildir
- production terrain hattı OpenTopography `COP30` fallback kullanır
- kullanılan gerçek cache:
  `CACHE/DEM/COP30_50_930972_6_914474_50_937593_6_924979.asc`

Provider sampling bulgusu:

- SRTM provider nearest-neighbor örnekleme kullanıyordu
- SRTM provider için bilinear interpolation test-first eklendi
- focused test: `2 passed`
- Köln sahnesi SRTM kullanmadığı için bu değişiklik Köln çözümünden ayrıdır

OpenTopography / COP30:

- `_height_from_grid()` nearest-neighbor örnekleme kullanıyordu
- bilinear interpolation için kırmızı regression oluşturuldu
- önceki sonuç: `300.0`
- beklenen bilinear sonuç: `250.0`
- provider bilinear hale getirildi
- focused test: `1 passed`

Gerçek Köln COP30 doğrulaması:

- bilinear 49 x 49:
  - triangles: `9600`
  - elevation delta: `15.97770217888565 m`
- bilinear 97 x 97:
  - triangles: `37632`
  - elevation delta: `16.30764222143206 m`
- Bambu Studio A/B incelemesinde nearest-neighbor kaynaklı sert
  basamak/plato karakteri belirgin biçimde azaldı

Production grid sözleşmesi:

- `AtlasFoundationFirstEngine.generate_city_stl()` artık
  `terrain_grid_size` parametresi expose eder
- legacy default: `25`
- değer gerçek production çağrısında
  `AtlasTerrainPipeline.build_terrain_slab()` içine propagate edilir
- focused integration: `4 passed`

Gerçek Köln full-city 97 x 97 entegrasyonu:

- city STL: `74762` triangle
- color preview scene: `81404` triangle
- binalar, yollar, parklar, vegetation ve foundation yerleşimi görsel olarak
  sağlam kaldı
- belirgin floating geometry veya yeni terrain-integration kırılması görülmedi

### Kalan 8.9 işi

Terrain artık daha doğru ve sürekli örnekleniyor; ancak beyaz/single-color yakın
görünümde kaynak DEM raster yapısından kalan hafif banding/faceting hâlâ
görülebiliyor.

Sıradaki tek geliştirme:

**deterministic presentation-surface regularization**

Kural:

- canonical terrain truth değişmeyecek
- foundation placement truth değişmeyecek
- source DEM elevation değerleri bozulmayacak
- yeni topoğrafik detay icat edilmeyecek
- yalnız product-facing visible terrain surface düzenlenecek
- test-first ilerlenilecek

8.9 bu iş ve ilgili regresyon/görsel acceptance tamamlanmadan LOCK değildir.

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

## 12 Ağustos 2026 — Güncel Production Checkpoint / Jamaica

Bu bölüm, yukarıdaki 11 Ağustos `768fa05` checkpoint kaydını supersede eder.

### Son güvenli ve push edilmiş commit

- Commit: `9efa03c`
- Commit mesajı: `Update Jamaica production checkpoint docs`
- Branch: `main`
- `HEAD == origin/main == 9efa03c` son doğrulanmış güvenli checkpoint'tir.

Bu checkpoint sonrasında Jamaica Wall Collection / wedding-rings çalışması
çalışma ağacında devam etmiştir ve henüz ayrı commit/full-regression ile
kilitlenmemiştir.

### Aktif referans ürün

Jamaica / Mavis Bank / Blue Mountains:

- center: `18.0314032, -76.6583705`
- outer product: `170 × 170 mm`
- city/map area: `150 × 150 mm`
- scale: `1:5000`
- ground coverage: yaklaşık `750 × 750 m`

Ürün label kontratı:

- primary: `JAMAICA`
- secondary: `MAVIS BANK / BLUE MOUNTAINS`
- kişisel ikon: interlocking wedding rings

Paylaşılan fiziksel palette:

- Black: frame + roads/hardscape + label text/icon
- Desert Tan: terrain + building walls + label plate
- Brick Red: roofs
- Dark Green: parks + trees + vegetation
- Blue: water; Jamaica sahnesinde kullanılmıyor

### Scale-Aware WorldCover Vegetation — LOCK

WorldCover `tree_cover` verisi fiziksel ürün scale bilgisi çözüldükten sonra
Foundation/product context içinde deterministic minimum-distance /
blue-noise-like yöntemle yeniden örneklenir.

Kilitlenen fiziksel kontrat:

- minimum tree-center spacing: `4.0 mm`
- `1:5000` için source spacing: `20.0 m`
- deterministic source-cell jitter
- jitter limit: source resolution değerinin `%40`ı
- OSM/non-WorldCover trees korunur
- raw `tree_cover` yoksa mevcut sampled WorldCover trees korunur
- raw `tree_cover` varsa legacy WorldCover sample set yeniden oluşturulur
- sampled WorldCover trees varsa duplicate forest-canopy fill/slab üretilmez

Reddedilen continuous canopy/slab ve hole-aware `inner_rings` deneyleri
production çözümünden çıkarılmıştır.

Gerçek WorldCover production doğrulaması:

- buildings: `249`
- roads: `6`
- WorldCover tree meshes: `623`
- forest canopy meshes: `0`
- terrain elevation delta: `264.70549808231567 m`
- triangles: `158722`
- open edges: `0`
- non-manifold edges: `0`

Validation STL:

`OUTPUT/STL/jamaica_mavis_bank_blue_mountains_150mm_5000_PRODUCTION_WORLDCOVER_TREE_FIX.stl`

WorldCover milestone regression:

- vegetation related: `106 passed in 0.40s`
- full ATLAS: `3661 passed in 16.22s`

### Gerçek Bambu Studio / AMS production benchmarkı

Jamaica ürünü dört hizalı multicolor STL parçası olarak gerçek Bambu Studio
ve AMS 2 Pro hattında slice edilmiştir.

AMS eşlemesi:

- A1: Black — PLA Basic
- A2: Desert Tan — PLA Matte
- A3: Brick Red — PLA Matte
- A4: Dark Green — PLA Matte

Son karşılaştırma benchmarkı:

- gerçek model/product mass: `210.53 g`
- purge: `142.04 g`
- prime tower: `44.18 g`
- total filament: `396.75 g`
- product dışı filament: `186.22 g`
- product dışı oran: yaklaşık `%47`
- filament changes: `616`
- estimated print time: `19 h 53 min`
- purge multiplier: `0.60`

Bu slice fiziksel baskı için kabul edilmemiştir ve `HOLD` durumundadır.

### Yeni production acceptance dersi

Closed/manifold geometri ve doğru semantic color split artık tek başına
production-ready kriteri değildir.

Çok renkli fiziksel ürünlerde aşağıdaki metrikler zorunlu acceptance
metrikleridir:

- filament-change count
- purge mass
- prime-tower mass
- product mass
- total filament mass
- estimated print time

Jamaica benchmarkı, aynı Z katmanlarında birçok semantic rengin tekrar
etmesinin AMS tarafında çok yüksek color-change maliyeti oluşturduğunu
kanıtlamıştır.

`616` değişimin ana çözümü purge multiplier'ı düşürmek değildir.
Kalıcı çözüm color/layer architecture ve multicolor export stratejisinde
aranacaktır.

### Jamaica / Mavis Bank ürününün rolü

Mevcut ürün silinmeyecek veya başarısız deney olarak sınıflandırılmayacaktır.

Bu sahne:

- ilk gerçek AMS production-cost benchmarkıdır
- multicolor optimization için regression/reference ürünüdür
- fiziksel product architecture kararlarının kaynağı olarak korunacaktır

### Park edilmiş alternatif ürün yönü

`Jamaica Island Relief` fikri park edilmiştir:

- `170 × 170 mm` bütün Jamaica adası
- gerçek ada silueti
- topography / Blue Mountains relief
- geniş doğal/vegetation bölgeleri
- Mavis Bank / honeymoon kişisel işareti
- frame + Jamaica label

Amaç aynı şehir detayını bütün adaya taşımak değildir.
Ada ölçekli ürün daha geniş renk bölgeleri ve çok daha az filament değişimi
sağlayabilecek ayrı bir fiziksel ürün yaklaşımı olarak değerlendirilecektir.

### Sıradaki iş

Mevcut `616` değişimli Jamaica slice basılmayacaktır.

Devam:

1. Bambu Studio layer preview ile color-change yoğun Z bölgelerini ölç.
2. Değişimleri üreten semantic mesh kombinasyonlarını belirle.
3. Görsel kaliteyi koruyarak color/layer architecture çözümü tasarla.
4. Yeni STL setini slice et.
5. Sonucu mevcut Jamaica benchmarkına karşılaştır.
6. Atık ve değişim sayısı kabul edilebilir olmadan fiziksel baskıyı başlatma.

Jamaica deneyimi production standardına işlendiği için daha sonraki
lokasyonlarda aynı AMS maliyet hatası tekrarlanmamalıdır.

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

## Physical Production Checkpoint — 14 Ağustos 2026

### Jamaica Premium Island Relief V1

Önce park edilmiş olan `Jamaica Island Relief` yönü artık aktif prototip
değildir; gerçek Bambu Studio production package seviyesine ulaşmıştır.

Kilit fiziksel ürün geometrisi:

- outer product: `170 × 170 mm`
- map opening: `150 × 150 mm`
- frame width: `10 mm`
- island footprint: yaklaşık `140.000 × 55.189 mm`
- island relief Z: `1.600 .. 9.788 mm`
- island mesh: `68,444` triangles
- closed physical relief geometry

Hizalı multicolor production STL seti:

- `JAMAICA_FRAME_BLACK.stl`
- `JAMAICA_SEA_BLUE.stl`
- `JAMAICA_ISLAND_GREEN.stl`
- `JAMAICA_LABEL_PLATE_WHITE.stl`
- `JAMAICA_LABEL_TEXT_RINGS_BLACK.stl`

Label:

- primary: `JAMAICA`
- secondary: `BLUE MOUNTAINS · MAVIS BANK`
- icon: interlocking wedding rings

Yeni Jamaica island architecture gerçek Bambu Studio slice'ında önceki
Mavis Bank şehir benchmarkına göre production cost'u dramatik biçimde
düşürmüştür:

- estimated total time: yaklaşık `2 h 54 min`
- total filament: yaklaşık `88.62 g`
- filament changes: `40`

Önceki şehir-temelli Jamaica benchmarkı:

- `616` filament changes
- `396.75 g` total filament
- `19 h 53 min`

silinmeyecektir; multicolor optimization regression/reference benchmarkı
olarak korunacaktır.

Jamaica Bambu Studio production project'i `.3mf` olarak kaydedilmiştir.

### Niedwiesenstraße 99 physical scene

Niedwiesenstraße 99 fiziksel sahnesi basılmıştır.

Son fiziksel tamamlamalar:

- ayrı Nidda/river insert üretildi
- `NIEDWIESENSTRASSE_99_RIVER_INSERT_WIDE.stl` basıldı
- river insert fiziksel sahneye yerleştirildi/yapıştırıldı
- gift-box lid basıldı
- gift-box base baskıya gönderildi

Gift-box lid geniş beyaz top-surface baskısı premium yüzey standardını
karşılamamıştır; yüzey çizgileri fiziksel olarak gözlenmiştir.

Gift-box base için fiziksel calibration yönü:

- layer height: `0.24 mm`
- sparse infill: `10%`
- top shell layers: `6`
- ironing: `No ironing`
- son slice: yaklaşık `2 h 52 min`
- yaklaşık `172.21 g`

Base baskısının fiziksel yüzey sonucu henüz değerlendirilmemiştir.

Niedwiesenstraße sahnesindeki sıradaki kesin fiziksel iş:

`detachable / separately printable tree and vegetation inserts`

Motorun neden ağaç üretmediğini araştırmak şu anki fiziksel tamamlamanın
ön koşulu değildir; önce mevcut sahneye uygun ayrı ağaç insertleri üretilecektir.


### Gift Box Base Physical Validation — PASS

Niedwiesenstraße Premium Gift Box V1 BASE baskısı fiziksel olarak tamamlandı.

Son fiziksel sonuç:

- geniş iç taban yüzeyi pürüzsüz ve homojen
- önceki lid baskısındaki çizgisel / ipliksi top-surface problemi görülmedi
- köşe kalkması / corner lifting gözlenmedi
- genel geometri ve duvarlar kabul edilebilir
- sağ uzun kenarda elle hissedilebilen hafif inward bow / içe kaçma gözlendi
- bu sapma baskıyı reddedecek seviyede değildir, ancak physical tolerance
  kaydı olarak korunacaktır

Bu baskı ile aşağıdaki ayar kombinasyonu Gift Box düz yüzeyleri için yeni
fiziksel referans olmuştur:

- nozzle: `0.4 mm`
- layer height: `0.24 mm`
- sparse infill: `10%`
- top shell layers: `6`
- ironing: `No ironing`

Bu ayarlar yeni lid baskısında da kullanılacaktır.

Sonuç:

`Gift Box BASE physical surface validation: PASS`

Önceki lid baskısının yüzey standardı supersede edilmiştir.


---

## Physical Tree V1 — 14 Ağustos 2026

ATLAS tree pipeline fiziksel üretim açısından yeniden kalibre edildi.

Kök neden:

- preview ağacı gösterebiliyordu;
- fakat eski canonical tree fiziksel ölçüleri çok küçüktü:
  - trunk diameter: `0.45 mm`
  - crown diameter: `1.55 mm`
  - total height: `2.15 mm`
- gerçek Niedwiesenstraße probe'unda yüzlerce tree mesh üretilmesine rağmen
  bu ölçüler fiziksel baskıda kırıntı / çok ince çıkıntı görünümü oluşturuyordu.

Physical Tree V1 canonical dimensions:

- trunk diameter: `1.125 mm`
- trunk height: `2.000 mm`
- crown diameter: `3.875 mm`
- crown height: `3.375 mm`
- total height: `5.375 mm`

WorldCover physical composition:

- minimum physical spacing: `6.0 mm`
- eski spacing: `4.0 mm`
- deterministic size variants:
  - `0.95×`
  - `1.00×`
  - `1.05×`

Niedwiesenstraße real-scene validation:

- previous large-tree geometry probe: `703` trees
- Physical Tree V1 spacing result: `349` trees
- variant distribution:
  - `0.95×`: `118`
  - `1.00×`: `112`
  - `1.05×`: `119`

Final visual candidate:

- trees: `349`
- triangles: `83,760`
- open edges: `0`
- non-manifold edges: `0`

Bambu Studio visual validation:

`PASS`

Tree geometry, spacing and mild deterministic size variation are accepted as
the current Physical Tree V1 direction.

Validation:

- focused tree regression: `61 passed`
- full regression: `3689 passed in 16.37s`


---

## Bonn Birthplace Production V1 — 14 August 2026

Bonn Münsterplatz birthday gift reached physical production.

- product: `170 × 170 mm`; opening: `150 × 150 mm`; scale: `1:3000`
- label: `BONN / GEBURTSORT`; symbol: baby stroller
- palette: Black frame/roads/text/stroller; White terrain/plate; Desert Tan buildings/generic roofs/landmark walls; Brick Red Bambu-painted historic roofs; Dark Green parks/trees
- water/Blue: intentionally absent
- package: `OUTPUT/STL/BONN_BIRTHPLACE_PRODUCTION_V1/`
- five aligned STL files: every file `0` open / `0` non-manifold
- slice: `121.46 g` model, `45.64 g` purge, `15.15 g` prime tower, `182.25 g` total, `193` changes, `9 h 31 min`
- mapping: A1 Black, A2 White, A3 Desert Tan, A4 Dark Green, External Brick Red
- status: `PRINTING`; external red requires manual intervention
- validation: `109 passed`; full `3704 passed in 16.54s`

---

## Seychellen Premium Archipelago V1 — 15 August 2026

Seychellen anniversary gift reached the physical print queue.

- product: `170 × 170 mm`; opening: `150 × 150 mm`
- composition: true disconnected Seychelles archipelago on a sea slab
- island span: `140.000 × 99.808 mm`
- relief Z: `1.600 .. 10.683 mm`
- German label: `SEYCHELLEN / SILBERHOCHZEIT · 25 JAHRE`
- symbol: intentionally absent
- four physical colors: Black frame/text; White label plate; Dark Green islands; Blue sea
- five aligned STL files because frame and label text remain separate Black parts
- every physical STL: `0` open / `0` non-manifold
- slice: `73.03 g` model, `9.98 g` purge, `3.31 g` prime tower, `86.32 g` total
- production: `40` filament changes; `2 h 32 min`
- project: `seychelles_premium_archipelago_170mm_PRODUCTION_V1.3mf`
- status: `PRINTING`; AMS mapping A1 Black, A2 White, A3 Blue, A4 Dark Green

---

## Modular, Personalized Gift Box & Physical Tree V2 — 15 August 2026

Premium Gift Box now supports Mini `120 mm`, Original `170 mm` and Grande
`220 mm` products, stackable `25 mm` / `50 mm` middle modules and a removable
personalization insert.

- connector system: base male top; middle female bottom / male top; lid female bottom
- engagement: `1.6 mm`; recess: `1.8 mm`; clearance: `0.25 mm/side`
- personalization plates: Mini `80 × 24`, Original `110 × 28`, Grande `140 × 32 mm`
- plate/recess/text: `1.2 / 0.8 / 0.6 mm`; fit clearance `0.20 mm/side`
- maximum personalization lines: `2`
- personalized lid, plate and text: `0` open / `0` non-manifold
- universal tier corner supports: `25 mm` and `50 mm`; four required per level

Physical Tree V2 supersedes V1 for future generated scenes:

- canonical trunk diameter: `1.50 mm`
- smallest `0.95×` trunk: `1.425 mm`
- root collar: `2.20 mm` diameter × `0.80 mm` height
- terrain embed: `0.60 mm`
- visible height and accepted organic crown form preserved
- strengthened tree: `0` open / `0` non-manifold

Validation: related tree package `76 passed`; full regression
`3764 passed in 16.70s`.


---

## Köln Graduation Production V2 — 15 August 2026

Köln Humanwissenschaftliche Fakultät / former Pädagogische Fakultät gift
was rebuilt with the current ATLAS physical product standard.

- recipient context: graduate of the former Pädagogische Fakultät
- verified target: Gebäude `216`, Gronewaldstraße 2; OSM source `125014714`
- product/opening/scale: `170 × 170 mm` / `150 × 150 mm` / `1:3000`
- label: `UNIVERSITÄT ZU KÖLN / PÄDAGOGISCHE FAKULTÄT`
- symbol: graduation cap
- palette: Black frame/text/cap; White terrain/roads/buildings/plate;
  Brick Red painted Gebäude 216 roof; Dark Green parks/Physical Tree V2;
  Blue water
- generated five-color STL package: every part `0` open / `0` non-manifold
- invisible legacy `46`-triangle Brick Red part removed in Bambu Studio;
  Gebäude 216 roof received slicer-verified volumetric Brick Red painting
- slice: `100.77 g` model, `22.90 g` purge, `6.67 g` prime tower,
  `130.33 g` total; `88` changes; `6 h 19 min`
- project:
  `OUTPUT/STL/koeln_paedagogische_fakultaet_multicolor_170mm_PRODUCTION_V2/koeln_paedagogische_fakultaet_170mm_GRADUATION_PRODUCTION_V2.3mf`
- status: `PRINT QUEUE`, behind Seychellen
- validation: focused `25 passed`; related `82 passed`; full `3767 passed in 16.96s`

Production lesson: ATLAS needs a future layer-aware material/change optimizer
that reports per-layer material demand, identifies invisible or redundant
material parts, estimates purge/prime-tower cost and reduces safe transitions
without changing visible semantic colors.

---

## Meckenheim Jungholzweg 2/3 Home Production V2 — 15 August 2026

Meckenheim home-memory gift reached Bambu project readiness.

- verified address targets:
  - Jungholzweg 2/2a/2b: OSM `220593156`
  - Jungholzweg 3: OSM `389176145`
- Apple Maps comparison confirmed Jungholzweg 2 within `7.64 m`
- product/opening/scale: `170 × 170 mm` / `150 × 150 mm` / `1:3000`
- label: `JUNGHOLZWEG 2/3 / MECKENHEIM`; symbol: home
- Black: frame/text/home symbol
- White: terrain/roads/label plate
- Desert Tan: generic buildings and roofs
- Brick Red: only the two verified target roofs
- Dark Green: parks and Physical Tree V2 vegetation
- water/Blue: absent from the real scene
- five physical STL files: every part `0` open / `0` non-manifold
- saved project:
  `meckenheim_jungholzweg_2_3_170mm_HOME_PRODUCTION_V2.3mf`
- status: `BAMBU PROJECT READY`; slice pending
- validation: related `71 passed`; full `3772 passed in 16.90s`

Before slicing or starting another print, finish the current Köln job and
update both P2S firmware and Bambu Studio.

---

## Semantic Relief, Figurative & Kit System V1

Status: `RED_CONTRACT`

ATLAS 2.5D rölyef sistemi için yeni uzun vadeli program; tarihi ve sanatsal mimari rölyefleri, kimliği korunan kişiselleştirilmiş figüratif sahneleri ve yeniden kullanılabilir demonte mimari kit parçalarını aynı semantic component graph omurgasında birleştirecektir.

Ana amaç yalnız fotoğrafı height-map olarak kabartmak değildir. Sistem kaynak nesneleri, component ilişkilerini, semantic depth ve occlusion düzenini, hedef yüzeyi, fiziksel baskı sınırlarını ve seçilen ürün biçimini anlayan bir üst orkestrasyon katmanı kuracaktır.

Program kapsamı:

- kilise, katedral, cami, heykel ve tarihi cephelerdeki oyma, kakma, figür, yazıt ve süslemeler;
- identity-preserving portrait relief;
- body, pose, gesture ve prop grammar;
- profesör, olta ve balık kovası gibi personalized story scenes;
- kemer, pencere, kapı, kubbe, tuğla ve kiremit için shared component catalog;
- assembled landmark, facade relief ve modular construction kit çıktıları;
- topology, slicer, volumetric material ve physical validation kapıları.

Kesin okuma sırası:

1. `Docs/START_HERE.md` içindeki bu bölüm;
2. `Docs/STATUS/CURRENT_STATUS.md` içindeki güncel program durumu;
3. `Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-08-08.md` içindeki `Semantic Relief, Figurative & Kit System V1 — Master Execution Compass` ana roadmap kaydı;
4. gerekli olduğunda mevcut relief architecture ve karar belgeleri.

Güncel kesin durma noktası:

- CORE geliştirmesi başlatılmadı;
- Phase 0 baseline sonucu: `1020 passed in 2.28s`, exit `0`;
- Phase 0 status: `LOCKED`; full regression: `3772 passed in 16.84s`, exit `0`;
- RED contract testi yazılmadı;
- sıradaki iş `CURRENT_STATUS` bağlantı kaydı, belge kontrolleri ve Phase 0 baseline auditidir;
- Phase 1 implementation, Phase 0 kaydedilmeden başlatılamaz;
- portrait implementation, Phase 8 decision gate `GO` olmadan başlatılamaz.

### Semantic Relief güncel ilerleme

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%7`
- Aktif faz: Phase 1 `IMPLEMENTATION_ACTIVE`
- Canonical component foundation: focused `22 passed`; related `46 passed in 0.14s`; full `3794 passed in 16.84s`
- Sıradaki paket: immutable transform, orientation ve physical dimensions contract

Her anlamlı milestone kaydında ATLAS genel yüzdesi ve aktif program yüzdesi birlikte yazılacaktır. Yüzdeler yalnız kabul kapısı tamamlanan gerçek yeteneklere göre değiştirilecektir.

### Semantic Relief transform milestone

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%8`
- Aktif faz: Phase 1 `IMPLEMENTATION_ACTIVE`
- Transform foundation: focused `31 passed`; related `55 passed`; full `3803 passed in 16.81s`
- Tamamlanan: translation, XYZ orientation, positive physical dimensions, coordinate space ve validated component connection
- Sıradaki paket: repetition ve interchangeable-instance contract

### Semantic Relief repetition milestone

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%9`
- Repetition foundation: focused `41 passed`; related `72 passed in 0.17s`; full `3820 passed in 16.81s`.
- Canonical repetition alanları: normalized group identity, positive quantity, finite physical spacing ve strict interchangeability.
- Çoklu instance sıfır spacing ile üst üste bindirilemez.
- Semantic component yalnız doğrulanmış immutable repetition contractını kabul eder.
- Son güvenli push edilmiş commit halen `7f46042`; repetition milestone henüz commit/push edilmedi.
- Sıradaki kesin iş: immutable semantic relief scene/model graph için ilk RED contract.

### Semantic Relief scene graph milestone

Status: `GREEN_MILESTONE`; Phase 1 henüz `LOCKED` değildir.

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%10`
- Scene graph: focused `12 passed`; related `84 passed in 0.19s`; full `3832 passed in 16.78s`.
- Unique identity, parent/target integrity, cycle rejection ve deterministic graph traversal tamamlandı.
- Son güvenli push edilmiş commit halen `5c02518`; scene graph milestone henüz commit/push edilmedi.
- Phase 1 kalanları: `occlusion_policy`, dört kullanım ailesini kapsayan synthetic fixture ve mevcut semantic architecture modelinin geçiş ilişkisi.
- Sıradaki kesin iş: component `occlusion_policy` için ilk RED contract.

### Semantic Relief Phase 1 LOCKED

- Status: `LOCKED`.
- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%12`
- Canonical immutable component, transform, repetition ve scene graph tamamlandı.
- Kimlik, hierarchy, target surface, cycle, physical placement, output, occlusion ve provenance doğrulamaları tamamlandı.
- Architecture, portrait, figurative ve modular-kit synthetic fixture ile temsil edildi.
- Mevcut `AtlasSemanticArchitectureModel` geçiş ilişkisi belgelendi; implementation Phase 2 adapter işidir.
- Phase 1 closeout: focused use-case `41 passed in 0.06s`; related `87 passed in 0.20s`; full `3835 passed in 16.74s`.
- Sıradaki paket: Phase 2 provider-independent Geometry Source Adapter result contractı.

### 25 mm corner support physical acceptance

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%12`
- Status: `GREEN_PROTOTYPE`.
- Connector blokları kaldırılmış sade köşe ve iç raf geometrisi doğrulandı.
- Corner-support paketi: `26 passed`; full regression: `3836 passed in 16.80s`.
- Dört parçalık gerçek baskı kalite, tutuş ve sallanma testlerini geçti.
- Yalnız yeniden üretilmiş `25MM` STL geçerlidir; mevcut `50MM` STL eski ve geçersizdir.
- Sıradaki fiziksel iş: beş sahnelik kutu için geçme toleransı kalibrasyon kuponu.

### Semantic Relief Phase 2 — Geometry Source Result milestone

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%14`
- Aktif faz: Phase 2 `IMPLEMENTATION_ACTIVE`
- Yeni provider-independent contract: `AtlasGeometrySourceResult`
- Contract normalized geometry, local bounds, normalized anchors, confidence, provenance ve supported projection modes taşır.
- Caller mutable inputundan izole snapshot oluşturur; reversed bounds reddedilir.
- Unsupported projection mode `require_projection_mode()` ile erken ve açık hata verir.
- Focused validation: `21 passed in 0.02s`.
- Related semantic regression: `113 passed in 0.27s`.
- Full regression: `3873 passed in 16.79s`, `1` unrelated pre-existing Premium Gift Box calibration failure.
- `git diff --check`: temiz.
- Full regression kırığı Phase 2 ile ilişkili değildir; untracked calibration spec `(0.20, 0.25, 0.30)` kullanırken untracked eski test `(0.05, 0.10, 0.15)` beklemektedir.
- Sıradaki kesin iş: Phase 2 adapter interface/provider responsibility contract için ilk RED test.

### Semantic Relief Phase 2 — Geometry Source Adapter boundary milestone

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%15`
- Aktif faz: Phase 2 `IMPLEMENTATION_ACTIVE`
- Yeni abstract contract: `AtlasGeometrySourceAdapter`
- Concrete geometry-source adapter yalnız `adapt(source)` üzerinden canonical `AtlasGeometrySourceResult` üretir.
- Provider-specific payload CORE geometry contractı olarak kabul edilmez.
- `validate_result()` non-canonical adapter outputunu erken reddeder.
- Projection capability yalnız canonical result üzerinden `validate_projection_mode()` ile doğrulanır.
- Focused Phase 2 validation: `27 passed in 0.04s`.
- Related semantic regression: `113 passed in 0.25s`.
- Full regression: `3879 passed in 16.74s`, `1` unrelated pre-existing Premium Gift Box calibration failure.
- `git diff --check`: temiz.
- Phase 2 kaynaklı regression kırığı yoktur.
- Sıradaki kesin iş: Phase 2 kapsamında ilk concrete geometry-source adapter ailesi için plana göre height-map relief source contractının ilk RED testi.

### Semantic Relief Phase 2 — Height-map Geometry Source Adapter milestone

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%17`
- Aktif faz: Phase 2 `IMPLEMENTATION_ACTIVE`
- İlk concrete geometry-source adapter: `AtlasHeightMapGeometrySourceAdapter`
- Normalized `0.0..1.0` 2D height-map kaynağını physical width/depth/relief-height bilgisiyle canonical `AtlasGeometrySourceResult` sınırına taşır.
- Adapter mesh veya STL üretmez; canonical snapshot yalnız height field, shape ve fiziksel ölçüleri taşır.
- İlk capability yalnız `flat_plane` projection mode olarak ilan edilir; cylindrical/dome/arbitrary surface desteği Phase 5 kapsamındadır.
- Mutable caller height-map/source inputları resulttan izole edilir.
- Malformed, non-finite, non-normalized height-map; geçersiz fiziksel ölçüler ve eksik source alanları reddedilir.
- Focused Phase 2 validation: `44 passed in 0.08s`.
- Related semantic/architectural relief regression: `126 passed in 0.28s`.
- Full regression: `3896 passed in 16.73s`, `1` unrelated pre-existing Premium Gift Box calibration failure.
- `git diff --check`: temiz.
- Phase 2 kaynaklı regression kırığı yoktur.
- Sıradaki kesin iş: Master Execution Compass Phase 2 sırasındaki ikinci concrete adapter ailesi olan `existing triangle mesh source` için ilk RED contract.

### Semantic Relief Phase 2 — Existing Triangle Mesh Source Adapter milestone

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%19`
- Aktif faz: Phase 2 `IMPLEMENTATION_ACTIVE`
- İkinci concrete geometry-source adapter: `AtlasTriangleMeshGeometrySourceAdapter`
- Mevcut ATLAS triangle-soup mesh formatını provider-independent canonical `AtlasGeometrySourceResult` sınırına taşır.
- Canonical geometry snapshot `geometry_kind=triangle_mesh`, isolated triangle tuples ve `triangle_count` içerir.
- Local bounds bütün triangle noktalarından deterministic hesaplanır.
- Mutable caller triangle inputları resulttan izole edilir.
- Empty/malformed triangle collections, yanlış point boyutu, non-numeric/bool/non-finite coordinates ve eksik source alanları erken reddedilir.
- Adapter topology/manifold üretim kapısı değildir; existing source geometry yalnız normalize edilir.
- Focused Phase 2 validation: `55 passed in 0.09s`.
- Related semantic/relief regression: `143 passed in 0.27s`.
- Gift Box stale calibration test güncel production contractına hizalandı; production spec değiştirilmedi.
- Full regression: `3908 passed in 16.80s`.
- `git diff --check`: temiz.
- Phase 2 kaynaklı regression kırığı yoktur.
- Sıradaki kesin iş: Master Execution Compass Phase 2 sırasındaki üçüncü concrete adapter ailesi olan `parametric primitive source` için ilk RED contract.

### Semantic Relief Phase 2 — Parametric Primitive Source Adapter milestone

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%21`
- Aktif faz: Phase 2 `IMPLEMENTATION_ACTIVE`
- Üçüncü concrete geometry-source adapter: `AtlasParametricPrimitiveGeometrySourceAdapter`
- İlk desteklenen primitive: `closed_cylinder`
- Adapter existing ATLAS parametric primitive tanımını canonical `AtlasGeometrySourceResult` sınırına taşır.
- Canonical snapshot `geometry_kind=parametric_primitive`, normalized primitive type ve normalized parameter set taşır.
- `closed_cylinder` parametreleri: center X/Y, base Z, radius, height, segments.
- Local bounds ve `base_center` / `top_center` anchors deterministic hesaplanır.
- Adapter mesh veya triangle üretmez; parametric descriptor yalnız geometry-source contract olarak taşınır.
- Unsupported primitive türü, eksik source/parameter, non-finite/non-numeric değerler, invalid radius/height ve invalid segment count erken reddedilir.
- Focused Phase 2 validation: `74 passed in 0.11s`.
- Related semantic/geometry regression: `152 passed in 0.29s`.
- Full regression: `3927 passed in 16.52s`.
- `git diff --check`: temiz.
- Phase 2 kaynaklı regression kırığı yoktur.
- Sıradaki kesin iş: Master Execution Compass Phase 2 sırasındaki dördüncü concrete adapter ailesi olan `facade grammar source` için ilk RED contract.

### Semantic Relief Phase 2 — Facade Grammar Source Adapter milestone

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%23`
- Aktif faz: Phase 2 `IMPLEMENTATION_ACTIVE`
- Dördüncü concrete geometry-source adapter: `AtlasFacadeGrammarGeometrySourceAdapter`
- İlk desteklenen facade grammar: `uniform_openings`
- Adapter facade grammar descriptorını provider-independent canonical `AtlasGeometrySourceResult` sınırına taşır.
- Canonical snapshot; facade width/height, level count, bay count, opening kind, horizontal/vertical margin ratios ve deterministic opening count taşır.
- Local bounds facade yüzey düzleminde `(0,0,0)` → `(width,0,height)` olarak deterministic hesaplanır.
- `bottom_left`, `bottom_center`, `top_center` anchors üretilir.
- Adapter `AtlasFacadeOpeningMesher` veya diğer facade mesh producerlarını çağırmaz; triangle/mesh/STL üretmez.
- Unsupported grammar, malformed source, invalid dimensions/counts/margins ve blank identifiers erken reddedilir.
- Focused Phase 2 validation: `102 passed in 0.13s`.
- Related semantic/facade regression: `188 passed in 0.37s`.
- Full regression: `3955 passed in 16.66s`.
- `git diff --check`: temiz.
- Phase 2 kaynaklı regression kırığı yoktur.
- Sıradaki kesin iş: Master Execution Compass Phase 2 sırasındaki beşinci concrete adapter ailesi olan `catalog component source` için ilk RED contract.

### Semantic Relief Phase 2 — Catalog Component Source Adapter milestone

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%25`
- Aktif faz: Phase 2 `IMPLEMENTATION_ACTIVE`
- Beşinci concrete geometry-source adapter: `AtlasCatalogComponentGeometrySourceAdapter`
- Adapter mevcut `AtlasMasterLandmarkCatalog` kaydı ile semantic component referansını canonical `AtlasGeometrySourceResult` sınırında birleştirir.
- Catalog resolution Wikidata veya OSM identity üzerinden yapılabilir.
- Canonical snapshot catalog key, landmark family, grammar/profile metadata, component flags, geometry overrides, component role, component geometry kind ve instance index taşır.
- Catalog metadata ile geometry metadata ayrıdır; `local_bounds` ve anchors source geometry descriptorından açıkça gelir ve catalog kaydına gömülmez.
- Catalog entry component flags bildiriyorsa undeclared component role erken reddedilir.
- Adapter mesh/triangle/STL üretmez.
- Unresolved catalog entry, malformed source, invalid instance index ve blank semantic identifiers erken fail eder.
- Focused Phase 2 validation: `116 passed in 0.16s`.
- Related catalog/semantic regression: `137 passed in 0.25s`.
- Full regression: `3969 passed in 16.77s`.
- `git diff --check`: temiz.
- Phase 2 kaynaklı regression kırığı yoktur.
- Sıradaki kesin iş: Master Execution Compass Phase 2 sırasındaki altıncı adapter ailesi olan `future canonical face/head source` için mevcut face/head geometry contractlarının audit edilmesi ve ilk RED contract.

### Semantic Relief Phase 2 — Face/Head Geometry Source Adapter milestone

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%27`
- Aktif faz: Phase 2 `IMPLEMENTATION_ACTIVE`
- Altıncı concrete geometry-source adapter: `AtlasFaceHeadGeometrySourceAdapter`
- Adapter mevcut `AtlasPortraitLandmarkResult` contractını canonical `AtlasGeometrySourceResult` sınırına taşır.
- Canonical geometry kind: `face_head_landmarks`.
- Coordinate space: `normalized_image_2d`.
- Landmark kimlikleri canonical snake_case biçimine normalize edilir.
- Local bounds landmark extents üzerinden deterministic hesaplanır.
- Landmarklar aynı semantic kimliklerle 3D anchor formuna `(x, y, 0.0)` taşınır.
- Provider confidence korunur; provenance `portrait_landmark_provider:<provider_id>` olarak kaydedilir.
- Desteklenen projection mode şu aşamada yalnız `flat_plane`.
- Adapter 3D canonical head mesh, vertices, faces, triangles veya STL üretmez.
- Bu milestone Phase 8 Face/Head Decision Gate'i erkenden ihlal etmez; yalnız provider result ile canonical geometry-source sınırını tanımlar.
- Focused Phase 2 validation: `124 passed in 0.18s`.
- Related portrait/face regression: `176 passed in 0.22s`.
- Full regression: `3977 passed in 16.92s`.
- `git diff --check`: temiz.
- Phase 2 kaynaklı regression kırığı yoktur.
- Sıradaki kesin iş: Master Execution Compass Phase 2 sırasındaki yedinci adapter ailesi olan `future body/pose/prop source` için mevcut figurative/body/pose/prop contractlarının audit edilmesi ve ilk RED contract.

### Semantic Relief Phase 2 — Geometry Source Adapter Contracts LOCKED

Status: `LOCKED`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%30`
- Phase 2 `Geometry Source Adapter Contracts` tamamlandı ve acceptance gate geçti.
- Canonical boundary: `AtlasGeometrySourceResult`
- Base adapter boundary: `AtlasGeometrySourceAdapter`
- Kilitlenen adapter aileleri:
  - height-map relief source
  - existing triangle mesh source
  - parametric primitive source
  - facade grammar source
  - catalog component source
  - future canonical face/head source boundary
  - future body/pose/prop source boundary
- Provider-specific payloadlar doğrudan CORE geometry-source sınırını geçemez.
- Aynı semantic scene farklı adapter implementasyonlarıyla çalışabilir.
- Adapter resultları deterministic ve mutable inputtan izole canonical snapshotlardır.
- Unsupported projection mode adapter/result sınırında erken ve açık hata verir.
- Face/head adapterı yalnız normalized portrait landmark descriptorı taşır; canonical 3D head geometry kararı Phase 8'e bırakılmıştır.
- Body/pose/prop adapterı `semantic_reference_only` contractıdır; skeleton/joint/pose/prop geometry icat edilmemiştir.
- Phase 2 final focused validation: `137 passed in 0.21s`.
- Full regression: `3990 passed in 16.55s`.
- `git diff --check`: temiz.
- Phase 2 acceptance gate: PASS.
- Phase 2 kaynaklı regression kırığı yoktur.
- Sıradaki kesin iş: Master Execution Compass Phase 3 `Semantic Depth & Occlusion` audit ve ilk RED contract.

### Semantic Relief Phase 3 — Semantic Depth & Occlusion Composer LOCKED

Status: `LOCKED`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%36`
- Phase 3 `Semantic Depth & Occlusion Composer` tamamlandı ve acceptance gate geçti.
- Yeni canonical composer: `AtlasSemanticDepthOcclusionComposer`.
- Semantic component graph deterministic back-to-front composition planına dönüştürülüyor.
- `depth_band` → configured normalized local relief range çözümü kilitlendi.
- Foreground / middle / background dahil arbitrary semantic depth-band isimleri profile/config üzerinden destekleniyor; numeric ranges hard-code edilmedi.
- Overlapping depth-band ranges reddediliyor; yalnız sınırdan temas eden ranges kabul ediliyor.
- Aynı depth band içinde `layer_order` ve component identity deterministic sıra sağlıyor.
- Parent-child depth inheritance kilitlendi:
  - child `depth_band=primary` ise ilk explicit ancestor bandını transitively miras alabilir;
  - explicit child bandı korunur;
  - root `primary` explicit range olmadan sessizce çözülmez.
- Explicit occlusion policy kontrolü eklendi; anlamsız `occludes_lower_layers` yönü deterministic conflict olarak raporlanıyor.
- Semantic depth relation contractı eklendi:
  - `contact`
  - `embed`
  - `recess`
  - `raised`
- Semantic depth relation, mesher-level `embed_mm` ve Phase 4 `physical_feature_policy` kararlarından ayrı tutuldu.
- `contact` depth amount almaz; `embed/recess/raised` pozitif amount ve parent attachment gerektirir.
- Resolved local relief envelope'ını tüketen veya aşan embed `impossible embed` olarak reddedilir.
- Material identity ile geometry boundary identity ayrıldı; material eşitliği geometry merge anlamına gelmez.
- `geometry_boundary_id` component identity üzerinden deterministic korunur.
- Deterministic operator override kaydı eklendi; Phase 3'te ilk desteklenen override alanı `depth_band`.
- Override original/override değerleri auditable record olarak tutulur; source scene/component mutate edilmez.
- Parent cycle validation mevcut `AtlasSemanticReliefScene` contractında kalır; composer duplicate cycle implementation taşımaz.
- Composer triangle mesh / STL üretmez.
- Phase 3 acceptance:
  - 3+ semantic layer doğru sıralanıyor: PASS
  - overlapping depth bands reddediliyor: PASS
  - parent cycle reddediliyor: PASS
  - physically impossible embed reddediliyor: PASS
  - identical input → identical composition plan: PASS
  - mesh/triangle üretmeme: PASS
- Phase 3 focused: `30 passed in 0.04s`.
- Related regression: `124 passed in 0.18s`.
- Full regression: `4020 passed in 16.68s`.
- `git diff --check`: temiz.
- Sıradaki kesin iş: Master Execution Compass Phase 4 `Physical Feature Resolver` audit; mevcut printability/minimum-feature/exaggeration altyapısını çıkarmak, ardından ilk RED contract.

### Semantic Relief Phase 4 — Physical Feature Resolver LOCKED

Status: `LOCKED`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%42`
- Phase 4 `Physical Feature Resolver` tamamlandı ve acceptance gate geçti.
- Yeni canonical resolver: `AtlasPhysicalFeatureResolver`.
- Yeni canonical profile: `AtlasPhysicalFeatureProfile`.
- Phase 4 geometry üretmez; semantic feature ölçülerini fiziksel üretim kararına dönüştürür.
- Mevcut `AtlasPhysicalDetailResolver`, `AtlasPhysicalCartographicExaggerationResolver`, `AtlasMinimumThicknessAnalyzer`, `AtlasFragileConnectionAnalyzer` ve ornament-density altyapıları korunmuştur; Phase 4 bunların üstünde canonical karar katmanı oluşturur.
- Kilitlenen karar seti:
  - `preserve`
  - `enlarge`
  - `merge`
  - `simplify`
  - `convert_to_engraving`
  - `omit`
  - `require_operator_review`
- Raised feature için profile-driven minimum width/height çözümü tamamlandı.
- Groove/engraving için ayrı minimum width/depth contractı tamamlandı.
- Sub-minimum önemli feature otomatik kaybedilmez; gerekli durumda operator review'e düşer.
- Çok küçük ve düşük öncelikli feature omission kararı explicit reason + adjustment report ile verilir; silent feature loss yoktur.
- Adjacent-feature spacing minimum altındaysa `merge_if_needed` ile deterministic merge kararı verilebilir.
- Repeated-detail density okunabilir bütçeyi aşarsa `simplify_if_needed` ile deterministic azaltılır.
- İnce raised detail `engrave_if_needed` ile engraving representation'a dönüştürülebilir.
- Unsupported projection profile sınırını aşarsa operator review gerekir.
- Unsupported slope/overhang profile sınırını aşarsa operator review gerekir.
- Fragile connection ratio profile minimumunun altına düşerse operator review gerekir.
- Aynı feature farklı product size profile'larında farklı fakat açıklanabilir fiziksel karar alabilir.
- Profile nozzle diameter, layer height, product size, material, raised/groove minimumları, unsupported projection/slope ve connection ratio eşiklerini taşır.
- Phase 4 acceptance:
  - same input → same physical decision: PASS
  - enlargement / omission silent değil: PASS
  - önemli unprintable feature review'e düşüyor: PASS
  - aynı feature farklı ürün boyutunda açıklanabilir farklı karar alıyor: PASS
- Phase 4 focused: `17 passed in 0.04s`.
- Related regression: `104 passed in 0.14s`.
- Full regression: `4037 passed in 17.01s`.
- `git diff --check`: temiz.
- Sıradaki kesin iş: Master Execution Compass Phase 5 `Surface Target & Projection V1` audit ve ilk RED contract.

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

## Phase 8.10 — Hybrid Canonical Detail Continuity — 23 August 2026

Phase 8 remains the active Human Identity architecture gate.
Phase 9 remains `NOT AUTHORIZED`.

Current safe pushed checkpoint:

- `HEAD == origin/main == 21bea372a35a827cfab70d5bda1a902a50b30ad3`
- commit:
  `21bea37 Add residual detail image sampling boundary`
- last safely pushed full regression:
  `4831 passed in 120.26s`

The existing unrelated working-tree changes remain intentionally preserved.
They must not be bulk-staged, reset or deleted as part of Phase 8.10 work.

### Hybrid canonical-detail architecture boundary

The active hybrid candidate follows this interpretation:

- canonical identity geometry remains owned by the canonical-head architecture;
- DSINE normals are not canonical identity geometry;
- DSINE normals are not metric 3D ground truth;
- DSINE may contribute only bounded low-amplitude residual detail;
- observation, sampling, correspondence, confidence, amplitude policy,
  projection and geometry composition remain separate auditable layers.

### Completed and pushed residual-detail milestones

`f6b2ed2 Add canonical residual detail composition layer`

- canonical residual-detail displacement;
- residual-detail compatibility gate;
- residual-detail composition;
- full regression: `4752 passed`.

`dd5386f Add canonical normal residual detail projection`

- canonical vertex-normal evaluator;
- normal residual-detail projector;
- full regression: `4767 passed`.

`0f360e4 Add residual detail observation correspondence boundary`

- residual-detail observation contract;
- observation/dense-correspondence compatibility gate;
- full regression: `4790 passed`.

`4a244bc Add canonical residual detail amplitude resolver`

- maps raw residual scalar detail and confidence into canonical vertex space;
- raw scalar detail and confidence remain separate;
- no confidence weighting or clipping in the resolver;
- full regression: `4798 passed`.

`d7882b1 Add canonical residual detail amplitude policy`

- explicit confidence weighting;
- symmetric bounded amplitude policy;
- no visibility, projection or geometry generation;
- full regression: `4812 passed`.

`8115a85 Add canonical view residual detail bridge`

- orchestrates observation;
- dense correspondence;
- canonical amplitude resolution;
- bounded amplitude policy;
- does not claim camera, pose, visibility, displacement or geometry;
- full regression: `4821 passed`.

`21bea37 Add residual detail image sampling boundary`

- provider-independent bilinear image/view sampling;
- converts scalar-detail field + separate confidence field +
  normalized sample coordinates into residual-detail observations;
- does not apply confidence weighting;
- full regression: `4831 passed`.

### Real six-view DSINE evidence

Evidence root:

`/Users/Kubi/ATLAS_HYBRID_SPIKE/EVIDENCE/phase8_10_hybrid_dsine_2026-08-23/`

Available normal fields:

- `subject_01_front_dsine_normals.npy`
- `subject_01_side_a_dsine_normals.npy`
- `subject_01_side_b_dsine_normals.npy`
- `subject_02_front_dsine_normals.npy`
- `subject_02_side_a_dsine_normals.npy`
- `subject_02_side_b_dsine_normals.npy`

All six verified as:

- shape `(1152, 1536, 3)`;
- dtype `float32`;
- finite;
- mean normal length `1.0`.

Evidence provenance records:

- architecture class:
  `hybrid_canonical_detail`;
- detail role:
  `bounded_low_amplitude_residual_detail_source_only`;
- DSINE normals are not canonical identity geometry;
- DSINE normals are not 3D ground truth;
- hybrid candidate remains incomplete;
- Phase 9 is not authorized.

Evidence manifest SHA256:

`cd6dbf999899fd50fe8c222070cf465ac55120092756138d0437ea277756eceb`

### Current PRE-COMMIT milestone

The following new Phase 8.10 contract is implemented and currently staged,
but is not yet committed or pushed:

- `CORE/atlas_canonical_head_dsine_residual_detail_field_source.py`
- `Test/test_canonical_head_dsine_residual_detail_field_source.py`

Purpose:

`DSINE normal field`
→ `structure/detail decomposition`
→ `detail normals`
→ `unnormalized residual scalar-detail field`

Implementation boundary:

- reuses `AtlasReliefNormalStructureDetailDecomposer`;
- reuses `AtlasReliefNormalHeightIntegrator`;
- uses `normalize_output=False`;
- zero-centers the residual scalar field;
- explicit confidence is supplied separately;
- confidence is preserved unchanged;
- confidence is not applied during field generation;
- this prevents double confidence weighting because confidence weighting is
  owned by the later canonical amplitude-policy layer.

Current validation:

- focused DSINE field-source:
  `13 passed in 0.05s`;
- related normal/detail regression:
  `99 passed in 0.18s`;
- broad canonical-head regression:
  `567 passed in 0.90s`;
- full regression:
  `4844 passed in 119.90s`;
- staged diff check:
  clean.

This milestone is not safely locked until commit, push and
`HEAD == origin/main` are verified.

### Exact next Phase 8.10 work

After this PRE-COMMIT milestone is safely pushed:

1. run the six real DSINE normal fields through the new field source;
2. preserve explicit confidence as a separate channel;
3. feed scalar-detail + confidence fields through the existing image sampler;
4. create real residual-detail observations;
5. connect those observations through dense correspondence;
6. run the canonical amplitude resolver;
7. apply the bounded amplitude policy;
8. run the view-to-canonical bridge;
9. record quantitative real hybrid-detail evidence;
10. close remaining benchmark evidence gaps;
11. perform architecture-class comparison;
12. issue final Phase 8 `GO / HOLD / REJECT`;
13. only an explicit GO may authorize Phase 9.

### Current gate status

- Phase 8.10: `ACTIVE`
- FLAME benchmark evidence: `AVAILABLE`
- direct-neural PRNet evidence: `AVAILABLE`
- six-view DSINE normal evidence: `AVAILABLE`
- hybrid residual-detail infrastructure: `IMPLEMENTED`
- real DSINE → canonical bounded-detail run: `PENDING`
- final architecture comparison: `PENDING`
- final Phase 8 decision: `PENDING`
- Phase 8 LOCK: `PENDING`
- Phase 9: `NOT AUTHORIZED`

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
