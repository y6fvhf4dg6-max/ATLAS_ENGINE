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
