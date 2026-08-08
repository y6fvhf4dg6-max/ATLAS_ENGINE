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

### Sıradaki tek adım

**8.7 Avenue Tree Row Engine**
