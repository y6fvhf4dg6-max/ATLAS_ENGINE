# ATLAS_ENGINE — DEVİR BELGESİ

**Tarih:** 08.08.2026

## Amaç

Bu belge, ATLAS_ENGINE geliştirmesinin güncel güvenli durumunu,
Roadmap 8 kapsamında tamamlanan çalışmaları, aktif 8.8 paketini
ve bundan sonraki geliştirme sırasını doğrulanmış biçimde devretmek
için hazırlanmıştır.


# 1. Roadmap çalışma disiplini

ATLAS Urban Fabric geliştirmesi aşağıdaki genel kurallarla yürütülür:

- 8.1 Test-first
- 8.2 General solutions only
- 8.3 Preserve existing architecture
- 8.4 One narrow package at a time
- 8.5 Regression sequence
- 8.6 Documentation

Bu maddeler implementation paketleri değil, bütün Urban Fabric roadmap'inin
geliştirme disiplinidir.

# 2. Urban Fabric Roadmap paket haritası

## Tamamlanan paketler

### 8.0 — Bonn Urban Fabric Ground-Truth Audit

### 8.1 — Urban Fabric Scene Contract

### 8.2 — Road Hierarchy Engine

### 8.3 — Linear Infrastructure Engine

### 8.4 — Urban Block Resolver

### 8.5 — Park & Plaza Semantic Surface Engine

### 8.6 — Vegetation Composition Engine

### 8.7 — Avenue Tree Row Engine

## Aktif paket

### 8.8 — Semantic Surface Texture Engine

Bu paket aktif geliştirme paketidir. Tamamlanmış olarak işaretlenmemiştir.

## Sonraki paketler

### 8.9 — Morphology-Aware Terrain Product Resolver

### 8.10 — Water & Shoreline Composition Engine

### 8.11 — Bridge / Infrastructure Urban Integration

### 8.12 — Building Height Product Normalizer

### 8.13 — Physical Cartographic Exaggeration Resolver

### 8.14 — City Composition LoD

### 8.15 — Scene Morphology Classifier

### 8.16 — Morphology Composition Policy

### 8.17 — Semantic Color / Material Hierarchy

### 8.18 — Customer Preview Parity

### 8.19 — Urban Fabric Quality Report

### 8.20 — Multi-Morphology Acceptance Benchmarks


# 3. 8.0 — Bonn Urban Fabric Ground-Truth Audit

**Durum:** COMPLETED — 7 Ağustos 2026

Bu paket yalnız audit / ground-truth doğrulaması olarak yürütüldü.
Audit sırasında production davranışı değiştirilmedi.

## Benchmark

- merkez: `50.733270, 7.100440`
- ürün alanı: `140 × 140 mm`
- kapsama alanı: `0.44 km²`
- efektif ölçek: yaklaşık `1:4738`
- final benchmark:
  - `922` mesh
  - `70798` triangle

## Doğrulanan temel bulgular

### Railway

- Exact bbox içinde `27` railway way bulundu.
- `AtlasLocalOSMReader` railway kaynaklarını production için toplamıyordu.
- Yüzey adayı olarak:
  - `3` tram way
  - `2` Hauptbahnhof platform kaydı
  belirlendi.
- tunnel / proposed / disused railway kayıtları ayrı policy gerektiriyor.
- Railway eksikliği gerçek bir missing capability olarak doğrulandı.

### Road ve pedestrian fabric

- Highway-line source içinde `353` kayıt bulundu.
- Mevcut road builder:
  - `62` kaydı kabul ediyor
  - `291` kaydı reddediyordu.
- Reddedilenlerin dağılımı:
  - `144` footway
  - `118` pedestrian
  - `23` steps
  - `6` path
- Araç yolu width hierarchy zaten mevcuttu.
- Eksik olan ana katman pedestrian urban fabric idi.

### Plaza / pedestrian square source truth

- Münsterplatz ve Markt gibi önemli Bonn meydanları çoğunlukla
  kapalı plaza polygonu olarak değil,
  line-based `highway=pedestrian` geometrisi olarak bulunuyor.
- Source truth mevcut olmasına rağmen production geometrisinde yeterince
  ifade edilmiyordu.

### Hofgarten

- OSM way `102199952` (`leisure=park`) source zincirinde mevcut.
- Kayıt final terrain-following park mesh'e kadar ulaşıyordu.
- Sorun source eksikliği değil;
  semantic / product-facing ifadenin zayıf olmasıydı.

### Vegetation

Exact bbox:

- `146` gerçek OSM tree
- `276` WorldCover-derived tree sample

Hofgarten içinde:

- `6` OSM tree
- `75` WorldCover-derived tree

Audit sonucu:

- vegetation clutter temel olarak composition problemidir.
- WorldCover tree-cover tekil tree objeleri gibi temsil ediliyordu.
- urban-context semantics eksikti.
- `AtlasGreenAreaTreeSampler` mevcut fakat production'a bağlı değildi.
- nature contract içinde `tree_rows` alanı vardı fakat:
  - producer yoktu
  - production consumer yoktu.

Bu bulgu daha sonraki 8.6 ve 8.7 paketlerini doğrudan gerekçelendirdi.

### Building vertical intervals

Building-part vertical interval double-counting bug bulunmadı.

Elevated parts doğru biçimde:

- `bottom = foundation + min_height`
- `top = foundation + height`

sözleşmesini kullanıyordu.

### Landmark / generic building height ayrımı

- İncelenen yüksek Bonn building-part kayıtları
  Bonner Münster ve Kreuzkirche'ye aitti.
- Bunlar generic-height outlier değildi.
- Generic building height hattı genel olarak tutarlı bulundu.

Universitätshauptgebäude için görülen yüksek ürün ifadesi:

- source-valid historic castle semantics
- `6.0 mm` castle-wing body minimum
- `4.4 mm` multi-gable roof

birleşiminden kaynaklanıyordu.

Bu durum source/parser bug değil,
morphology / product-composition policy problemidir.

### Water

- Inland water source: `4` kayıt
- final mesh: `3`
- `Kaiserbrunnen`, yalnız `amenity=fountain` olduğu için mevcut
  surface-water policy dışında deterministik olarak eleniyordu.
- Water source identity ve name metadata'sı final mesh aşamasına kadar
  korunmuyordu.

### Terrain

- Benchmark SRTM istedi.
- Local `N50E007.hgt` mevcut değildi.
- Sistem mevcut OpenTopography COP30 fallback hattını kullandı.
- Terrain scaling bug tespit edilmedi.
- Ancak gerçek provider / fallback provenance final result metadata'sında
  korunmuyordu.

### Urban block morphology

Bonn exact bbox içinde:

- `435` ana building polygon

Proximity cluster sonuçları:

- `2 m` → `43` cluster
- `4 m` → `39` cluster
- `6 m` → `24` cluster
- `10 m` → `6` cluster

Bu, Bonn'un doğal olarak yoğun block morphology'ye sahip olduğunu doğruladı.

### Product-scale footprint boyutları

Yaklaşık `1:4738` ölçekte:

- `59` footprint `< 1 mm²`
- `201` footprint `< 4 mm²`
- `340` footprint `< 9 mm²`

### Existing building printability filtering

Mevcut scene rejection sonuçları:

- `48` area-below-minimum
- `47` width-below-minimum
- `6` depth-below-minimum
- `1` triangulation failure

Bu nedenle mevcut minimum-size filtering bilinçli ve gerekli kabul edildi.

8.4 için çıkarılan kritik sınır:

- yeni uncontrolled minimum-size filter yazılmamalı
- küçük binalar keyfi olarak merge edilmemeli
- çözüm block-aware composition / LoD olmalı.

## Audit sonucu

8.0'ın ana sonucu:

> Bonn'daki temel eksiklik OSM source truth'un bulunmaması değildir.
> Eksiklik; mevcut roads, pedestrian fabric, blocks, parks, vegetation,
> rail, water, terrain, generic buildings ve landmark priorities katmanlarını
> product scale'de bir araya getiren coherent semantic composition layer'ın
> bulunmamasıdır.

8.0 böylece sonraki Urban Fabric paketlerinin gerekçesini doğruladı ve
gerçek missing capability'ler ile yalnız product/morphology-aware composition
gerektiren mevcut davranışları birbirinden ayırdı.


# 4. 8.1 — Urban Fabric Scene Contract

**Durum:** COMPLETED — 7 Ağustos 2026

**Commit:** `00e60c0 Add urban fabric scene contract`

Bu paket Urban Fabric V1 için ortak semantic scene sözleşmesini oluşturdu.

8.1 yalnız classification / scene contract katmanını değiştirdi.

**Final production geometry davranışı değiştirilmedi.**

## Eklenen ana dosyalar

- `CORE/atlas_urban_fabric_scene_contract.py`
- `Test/test_urban_fabric_scene_contract.py`

Commit ayrıca güncelledi:

- `Docs/Roadmap/URBAN_FABRIC_PRODUCT_COMPOSITION_V1.md`
- `Docs/START_HERE.md`
- `Docs/STATUS/CURRENT_STATUS.md`

Commit kapsamı:

- `5` dosya
- `968` insertion
- `45` deletion

## Ana immutable contract'lar

8.1 ile üç temel immutable scene contract tanımlandı:

- `AtlasUrbanFabricElement`
- `AtlasUrbanFabricRelationship`
- `AtlasUrbanFabricScene`

Bu sözleşmeler Urban Fabric katmanlarının daha sonraki paketlerde ortak ve
deterministik bir semantic model üzerinden konuşabilmesi için temel oluşturdu.

## Korunan element bilgileri

`AtlasUrbanFabricElement` ve scene sözleşmesi şu temel bilgileri korur:

- source identity
- semantic class
- product priority
- LoD eligibility
- geometry reference
- element relationships

Böylece Urban Fabric sistemi yalnız geometry listeleriyle değil,
kaynak kimliği ve semantic rolü korunmuş scene elementleriyle çalışabilecek
bir mimari taban kazandı.

## Relationship contract

8.1 relationship katmanında:

- typed relationships
- relationship identity
- source / target endpoint
- scene-level referential integrity

sözleşmeleri oluşturuldu.

Bu sayede daha sonraki paketlerde:

- road ↔ block
- park ↔ path
- vegetation ↔ park
- infrastructure ↔ urban fabric
- landmark ↔ surrounding scene

gibi ilişkilerin ortak scene modeli içinde güvenli biçimde ifade edilebilmesi
için temel oluşturuldu.

## Urban Fabric V1 minimum semantic coverage

Scene contract'ın zorunlu minimum semantic class'ları:

- `road`
- `railway`
- `pedestrian_path`
- `urban_block`
- `generic_building`
- `park`
- `plaza`
- `vegetation`
- `water`
- `infrastructure_corridor`
- `terrain`

Bu liste kapalı enum değildir.

Kritik karar:

> Bu class'lar Urban Fabric V1 için minimum gerekli coverage'dır.
> Semantic-class sistemi extensible kalır.

Bu nedenle sonraki paketler yeni semantic class ekleyebilir ancak
mevcut temel scene sözleşmesini kırmamalıdır.

## Scene validation davranışları

8.1 ile aşağıdaki davranışlar kilitlendi:

- deterministic element lookup
- semantic-class filtering
- duplicate element-ID rejection
- duplicate relationship-ID rejection
- relationship endpoint validation
- legacy related-element reference validation
- deterministic present-class reporting
- deterministic missing-required-class reporting

## Referential integrity

Scene içindeki relationship kayıtları yalnız geçerli element endpoint'lerine
referans verebilir.

Böylece dangling / kayıp element referanslarının sonraki composition
motorlarına taşınması engellendi.

Aynı yaklaşım legacy related-element referanslarına da uygulandı.

## Determinism

8.1'in önemli kabul kriterlerinden biri scene davranışının deterministik
olmasıdır.

Özellikle:

- element lookup
- semantic filtering
- present-class reporting
- missing-required-class reporting

aynı source input için kararlı sonuç üretir.

## Mimari sınırlar

8.1 sırasında bilinçli olarak yapılmayanlar:

- road hierarchy behavior eklenmedi
- railway geometry üretilmedi
- pedestrian geometry üretilmedi
- park geometry değiştirilmedi
- building geometry değiştirilmedi
- vegetation behavior değiştirilmedi
- terrain sistemi değiştirilmedi
- final STL / production geometry değiştirilmedi

8.1 yalnız daha sonraki Urban Fabric paketlerinin üzerine kurulacağı semantic
scene contract katmanını kilitledi.

## Doğrulama

- focused: `40 passed`
- related regression: `120 passed in 0.53s`
- full regression: `2913 passed in 12.75s`

## LOCK sonucu

8.1 aşağıdaki nedenle tamamlanmış kabul edildi:

- ortak immutable Urban Fabric element / relationship / scene contract'ı var
- source identity korunuyor
- semantic class korunuyor
- product priority ve LoD eligibility scene sözleşmesinde temsil ediliyor
- element ilişkileri typed ve referential-integrity kontrollü
- minimum Urban Fabric semantic coverage tanımlı
- semantic system extensible
- scene davranışı deterministik
- mevcut production geometry davranışı bozulmadı

## 8.2'ye devredilen temel

8.1'in doğrudan sonraki pakete devrettiği ana yapı:

> Urban Fabric elementleri artık ortak semantic scene contract içinde
> temsil edilebildiği için 8.2 Road Hierarchy Engine road source'larını
> yalnız ham OSM geometry olarak değil, product-priority ve semantic role
> taşıyan Urban Fabric elementleri olarak çözebilir.



# 5. 8.2 — Road Hierarchy Engine

**Durum:** COMPLETED — 7 Ağustos 2026

**Commit:** `e75cb10 Add urban road hierarchy engine`

Bu paket Urban Fabric V1 için product-scale road hierarchy katmanını
oluşturdu.

8.2'nin temel amacı ham OSM `highway=*` sınıflarını yalnız yol geometrisi
olarak kullanmak yerine semantic priority, fiziksel ürün genişliği,
printability, vertical treatment ve LoD davranışı taşıyan ortak road
profillerine çözmekti.

Bonn'a özel width, coordinate veya landmark exception eklenmedi.

## Eklenen ana dosyalar

- `CORE/atlas_urban_road_hierarchy_resolver.py`
- `Test/test_urban_road_hierarchy_resolver.py`
- `Test/test_road_foundation_builder_urban_hierarchy.py`
- `Test/test_foundation_first_road_hierarchy_integration.py`

## Entegre edilen production dosyaları

- `CORE/atlas_road_foundation_builder.py`
- `CORE/atlas_foundation_first_engine.py`

Commit ayrıca güncelledi:

- `Docs/Roadmap/URBAN_FABRIC_PRODUCT_COMPOSITION_V1.md`
- `Docs/START_HERE.md`
- `Docs/STATUS/CURRENT_STATUS.md`

Commit kapsamı:

- `9` dosya
- `1303` insertion
- `46` deletion

## Ana immutable product contract

8.2 ile:

- `AtlasUrbanRoadProfile`

immutable product contract'ı oluşturuldu.

Bu contract bir road source'un yalnız OSM sınıfını değil,
ürün içindeki semantic ve fiziksel davranışını da temsil eder.

## Ana resolver

Road hierarchy çözümlemesi:

- `AtlasUrbanRoadHierarchyResolver`

tarafından yürütülür.

Resolver source highway class'larını deterministik biçimde product-semantic
road class'larına dönüştürür.

## Highway → semantic road class çözümlemesi

Aşağıdaki source sınıfları:

- `motorway`
- `trunk`
- `primary`
- `secondary`
- `tertiary`

şu semantic class'a çözülür:

- `major_road`

Aşağıdaki source sınıfları:

- `residential`
- `living_street`
- `unclassified`
- `road`

şu semantic class'a çözülür:

- `local_road`

Ayrıca:

- `service` → `service_road`
- `footway` → `pedestrian_path`
- `path` → `pedestrian_path`
- `pedestrian` → `pedestrian_path`
- `steps` → `pedestrian_path`
- `cycleway` → `cycleway`
- `bridleway` → `bridleway`

olarak çözülür.

## Cycleway ve bridleway sınırı

`cycleway` ve `bridleway` 8.2 içinde semantic olarak tanınır.

Ancak bunların physical corridor profilleri bilinçli olarak 8.2'ye
eklenmedi.

Bu davranış:

> 8.3 — Linear Infrastructure Engine

paketine bırakıldı.

Böylece 8.2 road hierarchy kapsamı gereksiz biçimde linear infrastructure
motoruna genişletilmedi.

## Road product profile bilgileri

`AtlasUrbanRoadProfile` aşağıdaki product-facing bilgileri taşır:

- semantic priority
- physical width
- minimum printable width
- vertical treatment
- LoD eligibility
- simplification priority

Bu yapı daha sonraki composition ve LoD paketlerinin road class'larını
yalnız OSM tag'lerine bakarak yeniden yorumlamasını önler.

## Physical width resolution

8.2'de fiziksel yol genişliği çözümlemesi source truth'u koruyacak şekilde
tanımlandı.

Geçerli OSM:

- `width=*`

değeri varsa gerçek source width kullanılır.

Source width:

- yoksa
- geçersizse

mevcut ATLAS vehicle-class default width davranışı korunur.

Gerçek dünya genişliği daha sonra product millimeter ölçeğine çevrilir.

Ardından minimum printable width uygulanır.

Bu sayede source truth korunurken fiziksel baskıda okunamayacak kadar ince
road geometry üretilmesi engellenebilir.

## Pedestrian width policy

Pedestrian path için kritik farklılık:

> Source'ta gerçek width yoksa sistem hayali bir real-world fallback width
> üretmez.

`footway`, `path`, `pedestrian` ve `steps` için geçerli source width
bulunmuyorsa doğrudan explicit printable minimum kullanılır.

Bu karar pedestrian fabric'in fiziksel üründe görünür olmasını sağlarken
OSM'de bulunmayan gerçek dünya genişliklerinin uydurulmasını engeller.

## Relative visual hierarchy

8.2 aşağıdaki product hierarchy'yi doğruladı:

`major_road > local_road > service_road > pedestrian_path`

Bu göreli hiyerarşi profile karşılaştırmalarında üç temel alanda korunur:

- semantic priority
- physical width
- simplification priority

Böylece ürün ölçeğinde ana yollar ile tali/pedestrian ağının aynı görsel
ağırlıkta temsil edilmesi engellenir.

## Production integration

8.2 production hattına opt-in ve backward-compatible biçimde bağlandı.

`AtlasRoadFoundationBuilder.build_roads(...)` yeni optional parametreyi
kabul eder:

- `minimum_printable_width_mm`

Bu parametre verilmezse:

- legacy vehicle-road behavior korunur.

Parametre verilirse:

- semantic road profiles kullanılabilir
- pedestrian paths production road/fabric zincirine dahil edilebilir
- printable minimum uygulanabilir.

## Foundation First Engine entegrasyonu

`AtlasFoundationFirstEngine.generate_city_stl(...)` seviyesine yeni optional
parametre açıldı:

- `road_minimum_printable_width_mm`

Default değer:

- `None`

olarak bırakıldı.

Bu kritik backward-compatibility kararı sayesinde mevcut ATLAS ürünlerinin
road geometry davranışı 8.2 eklendi diye sessizce değiştirilmedi.

Yeni hierarchy davranışı explicit olarak etkinleştirilebilir.

## Mimari sınırlar

8.2 sırasında bilinçli olarak yapılmayanlar:

- Bonn'a özel road width yazılmadı
- Bonn'a özel coordinate exception eklenmedi
- landmark-specific road exception eklenmedi
- cycleway physical corridor behavior eklenmedi
- bridleway physical corridor behavior eklenmedi
- railway corridor sistemi eklenmedi
- genel linear infrastructure motoru yazılmadı
- mevcut legacy road davranışı default olarak değiştirilmedi

Bu sınırlar 8.2'nin yalnız Road Hierarchy Engine olarak kalmasını sağladı.

## Doğrulama

- focused + integration: `69 passed`
- related regression: `82 passed in 1.25s`
- full regression: `2982 passed in 12.70s`

## LOCK sonucu

8.2 aşağıdaki nedenle tamamlanmış kabul edildi:

- OSM highway sınıfları product-semantic road class'larına çözülüyor
- immutable `AtlasUrbanRoadProfile` mevcut
- semantic priority tanımlı
- physical width resolution tanımlı
- minimum printable width destekleniyor
- vertical treatment profile içinde temsil ediliyor
- LoD eligibility temsil ediliyor
- simplification priority temsil ediliyor
- source `width=*` truth korunuyor
- pedestrian path için uydurma real-world fallback width kullanılmıyor
- road visual hierarchy deterministik
- production integration opt-in
- legacy behavior default olarak korunuyor
- Bonn-specific hack bulunmuyor

## 8.3'e devredilen temel

8.2'nin 8.3'e doğrudan devrettiği ana sınır:

> Road hierarchy artık vehicle road ve pedestrian fabric'i semantic olarak
> sınıflandırabiliyor; ayrıca cycleway ve bridleway'i tanıyor.
> Ancak railway, tram, cycleway, bridleway ve benzeri line-based urban
> infrastructure öğelerinin ortak physical corridor üretimi henüz
> çözülmüş değildir.

Bu nedenle sıradaki paket:

> **8.3 — Linear Infrastructure Engine**

road hierarchy'nin dışındaki line-based urban infrastructure source'larını
ortak semantic ve printable corridor modeline taşımalıdır.


# 6. 8.3 — Linear Infrastructure Engine

**Durum:** COMPLETED / LOCKED — 7 Ağustos 2026

**Commit:** `b6d8eaf Add linear infrastructure engine`

Bu paket Urban Fabric V1 için genel, source-driven ve product-semantic
Linear Infrastructure Engine'i oluşturdu.

8.3'ün amacı railway, tram, cycle corridor, pedestrian path, embankment ve
diğer line-based urban infrastructure öğelerini yalnız dekoratif çizgiler
olarak değil; semantic class, fiziksel ürün genişliği, printability,
vertical treatment ve LoD davranışı taşıyan gerçek urban-fabric öğeleri
olarak çözmekti.

Location-specific infrastructure rule eklenmedi.

## Eklenen ana CORE modülleri

- `CORE/atlas_linear_infrastructure_geometry_builder.py`
- `CORE/atlas_linear_infrastructure_resolver.py`
- `CORE/atlas_linear_infrastructure_solid_builder.py`

## Entegre edilen source reader

- `CORE/atlas_local_osm_reader.py`

Reader artık 8.3 kapsamındaki linear infrastructure source kayıtlarını
toplayıp public result contract içinde expose eder.

Önemli değişikliklerden biri:

- `cycleway` kayıtlarının legacy pedestrian-path bucket'ından ayrılmasıdır.

Böylece cycle corridors kendi semantic ve physical infrastructure
davranışını taşıyabilir.

## Eklenen test paketleri

- `Test/test_linear_infrastructure_geometry_builder.py`
- `Test/test_linear_infrastructure_resolver.py`
- `Test/test_linear_infrastructure_solid_builder.py`
- `Test/test_local_osm_reader_linear_infrastructure.py`

Ayrıca güncellendi:

- `Test/test_local_osm_reader_elevated_areas.py`

Commit ayrıca dokümantasyonu güncelledi:

- `Docs/Roadmap/URBAN_FABRIC_PRODUCT_COMPOSITION_V1.md`
- `Docs/START_HERE.md`
- `Docs/STATUS/CURRENT_STATUS.md`

Commit kapsamı:

- `12` dosya
- `2299` insertion
- `20` deletion

## Desteklenen minimum infrastructure sınıfları

8.3 aşağıdaki source-driven linear infrastructure sınıflarını kapsar:

- railway
- light rail
- tram
- cycle corridors
- bridleway corridors
- pedestrian paths
- embankments
- infrastructure corridors

Railway özellikle incidental decorative line olarak ele alınmaz.

Kritik ilke:

> Şehir morfolojisi açısından önemli rail corridors ürün ölçeğinde
> okunabilir kalmalıdır.

## Semantic resolution

Linear infrastructure source kayıtları için resolver aşağıdaki product
özelliklerini çözer:

- semantic class
- visual priority
- physical width
- printable minimum width
- parallel-line representation
- LoD eligibility
- operational state
- vertical treatment
- product-surface eligibility

Bu sayede line-based infrastructure yalnız geometry primitive olarak değil,
urban morphology'nin semantic parçası olarak temsil edilir.

## Operational-state resolution

8.3 aşağıdaki operational state ayrımını destekler:

- active
- proposed
- disused

Bu ayrım product-surface eligibility kararında kullanılabilir.

Proposed veya disused source kayıtları active infrastructure ile aynı
physical davranışı otomatik olarak almaz.

## Surface visibility / product eligibility

Infrastructure source kayıtları için explicit olarak çözülür:

- surface visibility
- product-surface eligibility

Bu yaklaşım tunnel / underground / proposed / disused kaynakların yanlışlıkla
ürün yüzeyine fiziksel corridor olarak taşınmasını engeller.

## Vertical treatment

8.3 üç temel vertical treatment davranışını destekler:

- surface
- bridge-elevated
- subsurface

Bu sözleşme infrastructure öğelerinin road, bridge ve terrain sistemleriyle
aynı Z davranışına zorlanmasını önler.

Özellikle bridge-elevated ve subsurface kaynaklar surface corridor gibi
davranmaz.

## Immutable infrastructure product profiles

8.3 ile infrastructure öğeleri immutable product profile üzerinden temsil
edilir.

Profile temel olarak şu bilgileri taşır:

- semantic role
- visual priority
- physical width
- printable minimum
- vertical treatment
- LoD eligibility
- operational state
- representation mode

Bu yapı sonraki urban composition paketlerinin ham OSM tag'lerini yeniden
yorumlamasını önler.

## Width resolution

Source width mevcut ve geçerliyse ölçeklenerek product-space width'e
dönüştürülür.

Kritik karar:

> Source'ta gerçek width yoksa sistem hayali bir real-world infrastructure
> width icat etmez.

Bunun yerine açık printable minimum kullanılır.

Bu davranış 8.2 pedestrian width policy ile uyumludur ve source truth'u
korur.

## Printable minimum width

Her infrastructure profile için explicit minimum printable width
tanımlanabilir.

Böylece gerçek scale sonucu fiziksel baskıda kaybolacak kadar ince corridor
üretimi engellenir.

## Gauge-aware railway readability

Railway / tram infrastructure için gauge bilgisi uygun olduğunda parallel-line
readability kararında kullanılabilir.

Amaç:

- ray corridor'unu tek anlamsız çizgiye indirgememek
- product scale'de okunabilir rail identity korumak

Bu davranış source-driven kalır.

## Geometry contracts

8.3 iki temel geometry contract oluşturdu:

- `linear_strip`
- `area_strip`

Bu contract'lar source geometry'nin product-space corridor footprint'ine
çevrilmesi için kullanılır.

Linear source kayıtları doğrudan STL çizgisi olarak yazılmaz.

Önce product-space printable corridor geometry üretilir.

## Product-space footprint conversion

Source geometry:

- ölçeklenir
- physical width uygulanır
- printable minimum kontrol edilir
- representation mode'a göre corridor footprint'e dönüştürülür

Böylece infrastructure geometry gerçek ürün koordinat sisteminde fiziksel
alan kaplayan bir yapı olur.

## Terrain-following closed solids

`AtlasLinearInfrastructureSolidBuilder` infrastructure footprint'lerini
terrain üzerinde kapalı 3D solid olarak üretir.

Kilitlelenen davranışlar:

- terrain-following placement
- closed solid
- printable physical thickness
- source geometry identity'nin korunması
- deterministic solid generation

Bu sayede infrastructure yalnız açık top-surface mesh olarak kalmaz.

## Road / bridge / urban fabric ilişkisi

8.3 contract seviyesi şu ilişkileri dikkate alacak şekilde tasarlandı:

- infrastructure ↔ roads
- infrastructure ↔ bridges
- infrastructure ↔ terrain
- infrastructure ↔ surrounding urban fabric

Ancak 8.3 bütün urban integration problemlerini çözmeye çalışmadı.

Daha geniş bridge / infrastructure urban integration davranışı sonraki
roadmap paketlerinde ele alınacaktır.

## Bonn exact-benchmark doğrulaması

8.3 gerçek Bonn benchmark'ında doğrulandı.

Bonn exact benchmark içinde:

- `3` active surface tram corridor
- `1` closed railway land-use corridor

korundu.

Bu validation, 8.0 audit'te belirlenen gerçek railway missing capability'nin
8.3 ile source-driven biçimde kapatıldığını doğruladı.

## Mimari sınırlar

8.3 sırasında bilinçli olarak yapılmayanlar:

- Bonn-specific rail rule eklenmedi
- coordinate-specific infrastructure exception eklenmedi
- railway yalnız dekoratif line olarak temsil edilmedi
- source olmayan corridor icat edilmedi
- proposed/disused infrastructure active surface gibi zorlanmadı
- cycleway pedestrian-path bucket içinde bırakılmadı
- bridge engine yeniden yazılmadı
- road hierarchy yeniden yazılmadı
- terrain sistemi yeniden yazılmadı

8.3 mevcut ATLAS mimarisini koruyarak yalnız linear infrastructure
katmanını ekledi.

## Doğrulama

Final pre-commit lock:

- focused 8.3 package: `102 passed in 0.09s`
- related regression: `105 passed in 0.35s`
- full regression: `3085 passed in 12.59s`

## LOCK sonucu

8.3 aşağıdaki nedenle tamamlanmış / kilitlenmiş kabul edildi:

- railway semantic olarak first-class infrastructure öğesi
- tram / light rail destekleniyor
- cycle corridors destekleniyor
- bridleway corridors destekleniyor
- pedestrian path infrastructure semantics destekleniyor
- embankment / infrastructure corridor semantics mevcut
- operational state çözülüyor
- surface visibility explicit
- product-surface eligibility explicit
- vertical treatment explicit
- immutable infrastructure product profiles mevcut
- source width truth korunuyor
- printable minimum uygulanıyor
- gauge-aware parallel readability destekleniyor
- `linear_strip` / `area_strip` geometry contract'ları mevcut
- product-space footprint conversion mevcut
- terrain-following closed solid üretimi mevcut
- reader integration mevcut
- Bonn real-data validation başarılı
- location-specific hack bulunmuyor

## 8.4'e devredilen temel

8.3 sonunda Urban Fabric sistemi artık:

- road hierarchy
- pedestrian fabric
- rail / tram infrastructure
- cycle corridor semantics
- other linear infrastructure

katmanlarını ayrı fakat ortak product-semantic sözleşmelerle temsil
edebiliyordu.

Ancak şehir dokusunun building / street ilişkisini block ölçeğinde
çözümleyen ortak morphology katmanı henüz yoktu.

Bu nedenle sıradaki paket:

> **8.4 — Urban Block Resolver**

olarak devam etti.

8.4'ün görevi mevcut building printability filtresini değiştirmek değil;
source buildings, street context ve proximity ilişkilerini kullanarak
block-aware urban composition bilgisi üretmektir.


# 7. 8.4 — Urban Block Resolver

**Durum:** COMPLETED / LOCKED — 7 Ağustos 2026

**Commit:** `e93f217 Add urban block resolver`

Bu paket generic city geometry'yi keyfi biçimde birleştirmeden,
source building footprint ve semantic identity'yi koruyarak block-scale
urban coherence üretmek için geliştirildi.

Ana hedef:

> Dense şehir alanları birbirinden kopuk tekil extrusion kümeleri gibi değil,
> block ve street structure olarak okunmalıdır.

## Eklenen ana dosyalar

- `CORE/atlas_urban_block_resolver.py`
- `Test/test_urban_block_resolver.py`

Commit ayrıca güncelledi:

- `Docs/Roadmap/URBAN_FABRIC_PRODUCT_COMPOSITION_V1.md`
- `Docs/START_HERE.md`
- `Docs/STATUS/CURRENT_STATUS.md`

Commit kapsamı:

- `5` dosya
- `1841` insertion
- `9` deletion

## Ana problem

8.0 Bonn audit'i şu iki gerçeği doğrulamıştı:

- Bonn doğal olarak yoğun building morphology'ye sahip
- çok sayıda footprint product scale'de fiziksel olarak küçük

Ancak mevcut minimum building printability filtering zaten bilinçli ve
doğru çalışıyordu.

Bu nedenle 8.4'ün görevi:

- daha agresif minimum-size filtering yazmak değildi
- yakın binaları tek mesh'e merge etmek değildi
- source footprint uydurmak değildi

Görev, mevcut source buildings arasında block-level composition bilgisini
çözmekti.

## Resolver kapsamı

Urban Block Resolver aşağıdaki ilişkileri değerlendirecek biçimde
tasarlandı:

- road-defined urban blocks
- aynı block'a ait buildings
- street-wall continuity
- courtyard ve internal void readability
- block density
- local building-height relationships
- landmark proximity
- block-level LoD decisions

Bu bilgiler generic building geometry'nin semantic olarak daha tutarlı
ürün davranışı göstermesi için kullanılabilir.

## Source geometry koruma ilkesi

8.4'ün temel mimari kararı:

> Urban coherence üretmek source building footprint'lerini silmek veya
> değiştirmek anlamına gelmez.

Resolver source building identity ve geometry referanslarını korur.

Block membership bir composition ilişkisidir; doğrudan geometry merge
talimatı değildir.

## Building membership

Resolver yakınlık, road context ve block ilişkilerini kullanarak hangi
generic buildings'in aynı urban block içinde değerlendirilmesi gerektiğine
ilişkin deterministik bilgi üretir.

Bu ilişki:

- geometry merge değildir
- source replacement değildir
- missing footprint invention değildir.

## Street-wall continuity

8.4 street-facing building dizilerinin birbirinden bağımsız objeler gibi
değil, aynı urban frontage bağlamında değerlendirilmesine temel oluşturdu.

Amaç:

- gerçek street edge ilişkisini korumak
- yoğun dokuda bina ritmini okunabilir kılmak
- tekil küçük footprint'lerin toplam urban form içindeki rolünü çözmek

oldu.

## Courtyard ve internal void koruması

Kritik acceptance sınırı:

> Gerçek courtyard ve internal void alanları kapatılmamalıdır.

Block coherence gerekçesiyle:

- courtyard doldurulmaz
- source boşluklar yapay bina ile kapatılmaz
- gerçek internal void geometry kaybedilmez.

## Block density

Resolver block-level density bilgisini üretir.

Bu bilgi daha sonraki composition ve LoD sistemlerinin:

- dense urban
- daha gevşek urban fabric
- sparse building groups

arasında ayrım yapabilmesine temel oluşturur.

## Local height relationships

8.4 building height parser'ı yeniden yazmaz.

Bunun yerine mevcut building height sonuçlarının block bağlamındaki göreli
ilişkilerini değerlendirebilecek composition bilgisi oluşturur.

8.0'da doğrulanan generic height hattının genel olarak tutarlı olduğu
kararı korunmuştur.

## Landmark proximity

Semantic landmark'lar generic urban block composition içinde kaybolmamalıdır.

Bu nedenle landmark proximity block resolution kapsamındadır.

Kritik sınır:

- semantic landmark suppression yapılmaz
- generic block davranışı landmark geometry üzerinde öncelik kazanmaz.

## Block-level LoD

8.4 block-level LoD kararlarına temel olacak semantic bilgiyi üretir.

Ancak mevcut genel LoD architecture yeniden yazılmaz.

Block resolver:

- LoD input/context üretebilir
- fakat LoD motorunun yerine geçmez.

## Bilinçli olarak yapılmayanlar

8.4 aşağıdaki davranışları özellikle reddeder:

- unrelated building merge
- tüm yakın buildings'i tek mesh'e dönüştürme
- real courtyard closing
- internal void filling
- semantic landmark suppression
- missing building footprint invention
- Bonn-specific block rule
- Hofgarten-specific rule
- coordinate-specific morphology exception
- mevcut building printability minimumlarını değiştirme
- mevcut terrain architecture'ı değiştirme
- mevcut LoD architecture'ı yeniden yazma

## General architecture ilkesi

8.4 Bonn benchmark'ından doğmuş olsa da Bonn'a özel geliştirilmedi.

Primary rule:

> Block coherence genel morphology ve source ilişkilerinden çözülmelidir;
> belirli koordinatlara veya belirli şehir objelerine göre hard-code
> edilmemelidir.

## Doğrulama

8.4 lock sırasında:

- focused: `39 passed in 0.06s`
- related regression: `379 passed in 0.35s`
- full regression: `3124 passed in 11.68s`

## LOCK sonucu

8.4 aşağıdaki nedenle tamamlanmış / kilitlenmiş kabul edildi:

- generic buildings block-scale semantic context içinde çözülebiliyor
- source building identity korunuyor
- source footprint geometry korunuyor
- road/block ilişkisi değerlendirilebiliyor
- same-block membership temsil edilebiliyor
- street-wall continuity bilgisi üretilebiliyor
- courtyard/internal void korunuyor
- block density çözülebiliyor
- local height relationships composition context içinde değerlendirilebiliyor
- landmark proximity korunuyor
- block-level LoD context oluşturulabiliyor
- uncontrolled building merge yapılmıyor
- missing building invention yapılmıyor
- location-specific hack bulunmuyor

## 8.5'e devredilen temel

8.4 sonunda Urban Fabric sistemi artık:

- road hierarchy
- linear infrastructure
- pedestrian fabric
- generic building groups
- urban block morphology

katmanlarını semantic composition bağlamında temsil edebiliyordu.

Ancak açık urban surfaces hâlâ kendi semantic kullanım karakterlerini yeterli
ölçüde ifade etmiyordu.

Özellikle:

- park
- plaza
- pedestrian square
- garden
- grass area
- cemetery
- sports field
- courtyard

gibi yüzeylerin product-facing semantic rolleri ortak bir surface contract
üzerinden çözülmemişti.

Bu nedenle sıradaki paket:

> **8.5 — Park & Plaza Semantic Surface Engine**

olarak devam etti.


# 8. 8.5 — Park & Plaza Semantic Surface Engine

**Durum:** COMPLETED / LOCKED — 7 Ağustos 2026

**Commit:** `4a4d5bb Add park and plaza semantic surface engine`

Bu paket parks, plazas ve ilgili açık urban surfaces için explicit
product-semantic surface katmanını oluşturdu.

8.5'in temel amacı açık alanları yalnız renk verilmiş generic ground
polygonları olarak değil, kaynak verinin anlamını ve kullanım biçimini
koruyan semantic urban systems olarak temsil etmekti.

Hofgarten ilk Bonn validation örneği olarak kullanıldı.

**Hofgarten'a özel kural eklenmedi.**

## Eklenen ana dosyalar

- `CORE/atlas_park_plaza_semantic_resolver.py`
- `Test/test_park_plaza_semantic_resolver.py`

Commit ayrıca güncelledi:

- `Docs/Roadmap/URBAN_FABRIC_PRODUCT_COMPOSITION_V1.md`
- `Docs/START_HERE.md`
- `Docs/STATUS/CURRENT_STATUS.md`

Commit kapsamı:

- `5` dosya
- `1024` insertion
- `8` deletion

## Ana resolver

8.5'in temel semantic çözümleyicisi:

- `AtlasParkPlazaSemanticResolver`

Bu resolver source tags ve gerektiğinde geometry role bilgisini kullanarak
açık urban surfaces için product-facing semantic class ve ground role üretir.

## Desteklenen minimum semantic sınıflar

8.5 en az aşağıdaki semantic surface sınıflarını ayırır:

- `park`
- `garden`
- `plaza`
- `pedestrian_square`
- `courtyard`
- `grass_area`
- `cemetery`
- `sports_field`

Bu ayrım kritiktir.

Örneğin:

- park
- plaza
- pedestrian square
- courtyard
- grass area

aynı generic ground surface olarak değerlendirilmez.

## Ground surface role contract

Semantic class çözümlemesinden sonra product-facing ground surface role
üretilir.

Başlıca roller:

- `park` → `park_ground`
- `plaza` → `plaza_ground`
- `pedestrian_square` → `pedestrian_square_ground`
- `garden` → `garden_ground`
- `grass_area` → `grass_ground`
- `cemetery` → `cemetery_ground`
- `sports_field` → `sports_field_ground`
- `courtyard` → `courtyard_ground`

Bu role contract daha sonraki 8.8 Semantic Surface Texture Engine için
doğrudan temel oluşturdu.

## Park composition contract

8.5'in önemli kararı:

> Bir park yalnız colored ground polygon değildir.

Source data destekliyorsa park sistemi aşağıdaki composition layer'larını
taşıyabilir:

- ground surface
- internal paths
- open lawns / clearings
- tree rows
- vegetation clusters
- borders
- edges

Bu yapı parkı tek bir polygon yerine coherent semantic system olarak
tanımlamaya temel oluşturur.

## Internal path resolution

Park ve garden gibi internal-path destekleyen surface türlerinde mevcut
pedestrian path geometrileri değerlendirilebilir.

Bir pedestrian path:

- park polygonu içinde bulunuyorsa
- geçerli line geometry taşıyorsa

internal path composition layer'ına dahil edilebilir.

Bu işlem source-driven'dır.

Park içine olmayan path yapay olarak eklenmez.

## Deterministic internal path behavior

Internal path kayıtlarında:

- duplicate path ID'leri engellenir
- deterministic ordering uygulanır

Böylece aynı source input için park composition sonucu kararlı kalır.

## Tree-row support contract

Park ve garden semantic profile'ları:

- tree-row support bilgisini

taşıyabilir.

Ancak 8.5 tree-row fiziksel üreticisi değildir.

Tree-row detection / spacing / member production daha sonraki:

> **8.7 — Avenue Tree Row Engine**

paketine bırakıldı.

## Vegetation-cluster support

Park ve garden semantic contract'ı:

- vegetation clusters

composition layer'ını destekleyebilir.

Ancak vegetation source'larının isolated tree / cluster / canopy gibi
fiziksel representation kararları 8.5 içinde çözülmedi.

Bu görev:

> **8.6 — Vegetation Composition Engine**

paketine devredildi.

## Clearings / borders / edges

Park semantic profile gerektiğinde aşağıdaki extended composition
layer'larını destekleyebilir:

- clearings
- borders
- edges

Bunların yalnız source data varsa kullanılması temel ilkedir.

Source olmayan park detayları decorative amaçla icat edilmez.

## Plaza davranışı

Plaza açık urban surface olarak park'tan ayrı semantic class'tır.

Plaza:

- `plaza_ground`

rolünü alır.

Plaza'nın product-facing görünümü vegetation ağırlıklı park sistemi olarak
yorumlanmaz.

Bu ayrım 8.8'de farklı physical surface language uygulanmasına temel
oluşturdu.

## Pedestrian square davranışı

`highway=pedestrian` + `area=yes` gibi source-backed alanlar:

- `pedestrian_square`

semantic class'ına çözülebilir.

Ground role:

- `pedestrian_square_ground`

olarak korunur.

Bu, 8.0 audit'te Münsterplatz / Markt gibi alanlarda görülen pedestrian
fabric probleminin semantic temelini oluşturur.

## Garden davranışı

Garden:

- `garden_ground`

rolünü alır.

Ayrıca uygun source evidence varsa:

- internal paths
- tree rows
- vegetation clusters

composition layer'larını destekleyebilir.

Garden bu nedenle generic grass polygon ile aynı contract'a sahip değildir.

## Grass-area davranışı

`landuse=grass` gibi source-backed alanlar:

- `grass_area`
- `grass_ground`

olarak çözülür.

Bu distinction daha sonra 8.8'de park lawn ve generic grass yüzeylerinin
farklı texture language kullanabilmesini mümkün kıldı.

## Cemetery davranışı

Cemetery:

- `cemetery`
- `cemetery_ground`

semantic contract'ına sahiptir.

Bu surface generic park veya grass alanı değildir.

Daha sonraki product-surface treatment katmanları cemetery identity'yi
kaybetmeden özel surface language uygulayabilir.

## Sports field davranışı

`leisure=pitch` gibi alanlar:

- `sports_field`
- `sports_field_ground`

olarak çözülür.

Bu sayede sports field generic lawn olarak değerlendirilmez.

## Courtyard davranışı

Geometry role açıkça:

- `courtyard`

olarak verilirse resolver courtyard semantic class'ını korur.

Ground role:

- `courtyard_ground`

olarak çözülür.

Bu karar 8.4 Urban Block Resolver ile uyumludur:

> Gerçek courtyard boşlukları block coherence gerekçesiyle kapatılmaz;
> kendi semantic surface identity'sini koruyabilir.

## Semantic profile capability flags

Surface profile yalnız semantic class adı taşımaz.

Aşağıdaki capability bilgilerini de taşıyabilir:

- supports internal paths
- supports tree rows
- supports vegetation clusters
- supports clearings
- supports borders
- supports edges

Bu sayede farklı surface türlerine aynı composition davranışı körlemesine
uygulanmaz.

## Composition layers

Resolver çıktısı semantic surface için deterministic composition layer listesi
üretebilir.

İlk layer her zaman semantic ground role'dür.

Source evidence ve profile capability destekliyorsa buna:

- internal paths
- tree rows
- vegetation clusters
- clearings
- borders
- edges

eklenebilir.

## Source truth ilkesi

8.5'in temel ilkesi:

> Open-space composition semantic source evidence'dan gelmelidir.

Bu nedenle:

- olmayan internal path icat edilmez
- olmayan tree row icat edilmez
- olmayan vegetation cluster icat edilmez
- olmayan clearing icat edilmez
- decorative border/edge keyfi eklenmez

## Park / plaza ayrımı

Primary visual-semantic kabul kriteri:

> Plazas ve pedestrian squares park veya generic terrain gibi
> okunmamalıdır.

Benzer biçimde:

> Büyük parklar ürün ölçeğinde tek coherent park system olarak
> okunmalıdır.

## Mimari sınırlar

8.5 sırasında bilinçli olarak yapılmayanlar:

- Hofgarten-specific rule eklenmedi
- Bonn coordinate rule eklenmedi
- park içine source olmayan path eklenmedi
- tree-row physical producer yazılmadı
- vegetation composition engine yazılmadı
- surface texture geometry yazılmadı
- park mesh sistemi yeniden yazılmadı
- terrain sistemi yeniden yazılmadı
- road hierarchy yeniden yazılmadı
- urban block resolver yeniden yazılmadı

8.5 yalnız semantic surface identity ve composition capability contract'ını
kilitledi.

## Doğrulama

Bilinen 8.5 pre-commit doğrulaması:

- focused: `35 passed in 0.05s`
- related park / semantic surface regression: `206 passed in 0.24s`

Paket bu doğrulamalar sonrasında scoped commit ile kilitlendi.

## LOCK sonucu

8.5 aşağıdaki nedenle tamamlanmış / kilitlenmiş kabul edildi:

- park semantic class explicit
- garden semantic class explicit
- plaza semantic class explicit
- pedestrian square semantic class explicit
- courtyard semantic class explicit
- grass area semantic class explicit
- cemetery semantic class explicit
- sports field semantic class explicit
- her semantic class için product-facing ground role çözülebiliyor
- park internal path composition destekleniyor
- tree-row capability contract mevcut
- vegetation-cluster capability contract mevcut
- clearing / border / edge capability contract mevcut
- composition layer'ları deterministic
- source evidence korunuyor
- plaza ile park ayrımı semantic olarak explicit
- Hofgarten validation example olarak kullanıldı, special-case olmadı

## 8.6'ya devredilen temel

8.5 sonunda açık urban surfaces artık semantic identity taşıyordu.

Ancak park ve diğer green surfaces içindeki vegetation hâlâ fiziksel
representation açısından çözülmemişti.

Özellikle ayrım gerekiyordu:

- gerçek isolated OSM tree
- tree row
- tree cluster
- WorldCover-derived forest canopy

Bu nedenle sıradaki paket:

> **8.6 — Vegetation Composition Engine**

olarak devam etti.

8.6'nın görevi 8.5'in semantic park/surface contract'ını kullanarak
vegetation source'larını doğru product representation rollerine ayırmak,
WorldCover double representation'ı engellemek ve forest canopy davranışını
production zincirine bağlamaktı.


# 9. 8.6 — Vegetation Composition Engine

**Durum:** COMPLETED / LOCKED — 7 Ağustos 2026

**Commit:** `9b0aa22 Add vegetation composition engine`

Bu paket vegetation öğelerini yalnız tekrar eden bağımsız tree objeleri olarak
değil, source context ve product scale'e bağlı semantic vegetation systems
olarak çözmek için geliştirildi.

Ana acceptance ilkesi:

> Daha az fakat semantic olarak organize edilmiş vegetation öğeleri,
> kontrolsüz tree sayısından daha güçlü landscape ve urban readability
> üretmelidir.

## Eklenen ana CORE modülleri

- `CORE/atlas_vegetation_composition_resolver.py`
- `CORE/atlas_forest_canopy_foundation_builder.py`

## Production entegrasyonu

8.6 aşağıdaki production katmanlarına bağlandı:

- `CORE/atlas_foundation_first_engine.py`
- `CORE/atlas_product_color_preview_renderer.py`

Böylece vegetation semantics yalnız bağımsız resolver seviyesinde kalmadı;
Foundation First üretim hattına ve color preview/material routing'e taşındı.

## Eklenen / güncellenen test paketleri

- `Test/test_vegetation_composition_resolver.py`
- `Test/test_foundation_first_engine_tree_water_filter.py`
- `Test/test_product_color_preview_renderer.py`
- `Test/test_wall_collection_multicolor_stl_exporter.py`

Commit ayrıca güncelledi:

- `Docs/Roadmap/URBAN_FABRIC_PRODUCT_COMPOSITION_V1.md`
- `Docs/START_HERE.md`
- `Docs/STATUS/CURRENT_STATUS.md`

Commit kapsamı:

- `11` dosya
- `1961` insertion
- `22` deletion

## Desteklenen semantic vegetation roller

8.6 minimum olarak aşağıdaki vegetation rollerini ayırır:

- `isolated_tree`
- `tree_row`
- `tree_cluster`
- `forest_canopy`

Bu roller aynı physical representation'a zorlanmaz.

Representation mode source context ve product scale'e bağlıdır.

## Isolated tree davranışı

Önemli ve source-backed tekil tree kayıtları:

- `isolated_tree`

olarak korunabilir.

Bu davranış gerçek ve anlamlı tekil ağaçların tamamen cluster veya canopy
içine kaybolmasını engeller.

Ancak 8.6'nın amacı tüm tree source'larını isolated objelere dönüştürmek
değildir.

## Tree-row semantic role

Formal alignment taşıyan vegetation source'ları:

- `tree_row`

semantic rolünü destekler.

8.6 bu rolü composition contract seviyesinde tanır.

Ancak tree-row spacing, ordered layout ve physical member production
8.6 kapsamına alınmadı.

Bu davranış bilinçli olarak:

> **8.7 — Avenue Tree Row Engine**

paketine bırakıldı.

## Tree-cluster davranışı

Park veya benzeri source context içinde vegetation:

- `tree_cluster`

representation mode'una çözülebilir.

Amaç:

- yoğun vegetation alanını kontrolsüz isolated-tree scattering olarak
  üretmemek
- park içinde daha okunabilir ve kontrollü vegetation composition oluşturmak.

## Forest-canopy davranışı

Forest source context:

- `forest_canopy`

olarak çözülür.

Bu kritik bir değişikliktir.

Forest artık:

- uniform decorative dots
- yüzlerce bağımsız tree symbol

olarak temsil edilmek zorunda değildir.

Bunun yerine continuous canopy mass olarak okunabilir.

## Forest canopy production

8.6 ile:

- `AtlasForestCanopyFoundationBuilder`

eklendi.

Bu builder forest-canopy surface'larını fiziksel foundation meshlerine
dönüştürür.

Kilitlenen davranışlar:

- semantic role korunur
- source identity korunur
- terrain üstünde foundation-style physical geometry üretilir
- final mesh closed/manifold kalır
- product rendering zincirine bağlanabilir.

## WorldCover semantics

8.0 audit'te WorldCover tree-cover'ın isolated tree objeleri gibi
örneklendiği ve clutter ürettiği doğrulanmıştı.

8.6 bu problemi semantic composition seviyesinde ele aldı.

WorldCover-derived forest records:

- isolated decorative trees olarak zorlanmaz
- forest-canopy semantics'e çözülebilir
- continuous canopy representation'a taşınabilir.

Bu karar vegetation density problemini source kaybetmeden azaltır.

## Double representation kontrolü

8.6 vegetation composition'ın önemli amaçlarından biri aynı source/context'i
birden fazla fiziksel vegetation representation ile gereksiz tekrar
etmemektir.

Örneğin forest area için:

- isolated tree scattering
- canopy mass

aynı anda kontrolsüz biçimde üretilmemelidir.

Semantic resolver representation mode'u belirleyerek bu tür double
representation riskini azaltır.

## Representation mode

Vegetation profile yalnız semantic role değil, fiziksel representation
kararını da taşır.

Örnek semantic davranışlar:

- important isolated tree → individual object
- avenue vegetation → ordered row
- park vegetation → controlled cluster
- forest → continuous canopy

Bu karar product scale ve source context ile uyumludur.

## Density control ilkesi

8.6 açıkça şu davranışları engellemeyi hedefler:

- uncontrolled isolated-tree scattering
- excessive tree density
- formal alignments'in kaybolması
- forest alanlarının uniform dot pattern'e dönüşmesi.

Amaç vegetation count'u maksimize etmek değildir.

Amaç semantic readability'yi maksimize etmektir.

## Production mesh-group entegrasyonu

Forest canopy meshes Foundation First Engine final scene assembly'ye
eklenebilir.

8.6 ile final vegetation output içinde:

- tree meshes
- forest canopy meshes

ayrı semantic mesh group'lar olarak korunabilir.

Bu yapı sonraki renderer/exporter katmanlarının vegetation'ı doğru material
batch'e yönlendirmesine imkân verir.

## Color preview entegrasyonu

`CORE/atlas_product_color_preview_renderer.py` güncellendi.

Forest canopy geometry:

- vegetation/tree material ailesine

yönlendirilebilir.

Böylece canopy semantic olarak doğru green material batch içinde görünür.

## Multicolor exporter uyumu

`Test/test_wall_collection_multicolor_stl_exporter.py` güncellendi.

Amaç:

- forest-canopy geometry'nin multicolor product export zincirinde kaybolmaması
- vegetation green part ile uyumlu kalması.

## Castle-only davranışının korunması

8.6 Foundation First entegrasyonunda mevcut:

- `castle_only`

vegetation suppression davranışı korunmuştur.

Yani vegetation composition eklendi diye castle-only ürünlerinde istenmeyen
vegetation geometry yeniden ortaya çıkmaz.

## Bilinçli kapsam sınırları

8.6 sırasında yapılmayanlar:

- tree-row spacing resolver yazılmadı
- avenue alignment resolver yazılmadı
- tree-row physical member producer yazılmadı
- Bonn/Hofgarten-specific vegetation rule eklenmedi
- source olmayan tree cluster icat edilmedi
- forest source generic decorative dots'a zorlanmadı
- road hierarchy yeniden yazılmadı
- park semantic resolver yeniden yazılmadı
- terrain architecture yeniden yazılmadı

Tree-row detection / physical row producer açıkça 8.7 kapsamına bırakıldı.

## Doğrulama

Final 8.6 doğrulaması:

- focused vegetation resolver: `51 passed in 0.07s`
- vegetation + engine integration: `57 passed in 0.16s`
- related regression: `154 passed in 0.36s`
- full regression: `3217 passed in 12.60s`

## LOCK sonucu

8.6 aşağıdaki nedenle tamamlanmış / kilitlenmiş kabul edildi:

- vegetation semantic role ayrımı mevcut
- `isolated_tree` destekleniyor
- `tree_row` semantic role destekleniyor
- `tree_cluster` destekleniyor
- `forest_canopy` destekleniyor
- representation mode source context'e bağlı
- uncontrolled tree scattering azaltılıyor
- WorldCover forest source canopy semantics'e taşınabiliyor
- forest-canopy physical builder mevcut
- Foundation First Engine entegrasyonu mevcut
- color preview entegrasyonu mevcut
- multicolor exporter uyumu doğrulandı
- castle-only suppression korunuyor
- source olmayan vegetation icat edilmiyor
- Hofgarten-specific hack bulunmuyor

## 8.7'ye devredilen temel

8.6 sonunda vegetation semantic composition katmanı oluşmuştu.

Ancak `tree_row` hâlâ yalnız semantic role seviyesindeydi.

Eksik kalan fiziksel davranışlar:

- real OSM `natural=tree_row` ingestion
- source geometry direction
- strong / weak evidence
- source spacing interpretation
- product-readable fallback spacing
- deterministic polyline layout
- ordered physical tree members
- road/path parallel context
- source-gap preservation

Bu nedenle sıradaki paket:

> **8.7 — Avenue Tree Row Engine**

olarak devam etti.

8.7'nin görevi 8.6'da tanımlanan `tree_row` semantic rolünü gerçek,
source-driven ve printable physical tree-row sistemine dönüştürmekti.


# 10. 8.7 — Avenue Tree Row Engine

**Durum:** COMPLETED / LOCKED — 7 Ağustos 2026

**Commit:** `956b099 Add avenue tree row engine`

Bu paket 8.6 Vegetation Composition Engine içinde semantic role olarak
tanımlanan `tree_row` kavramını gerçek source evidence'a dayanan,
product-scale'de okunabilir ve fiziksel olarak üretilebilir formal tree-row
sistemine dönüştürdü.

Ana acceptance ilkesi:

> Formal tree alignments should read as intentional urban rhythm rather than
> as unrelated individual trees.

Temel mimari sınır:

> Source trees ve source tree-row geometry evidence base olarak kalmalıdır.
> Product readability için spacing regularization yapılabilir ancak source
> evidence bulunmayan arbitrary tree rows icat edilmemelidir.

## Commit kapsamı

Commit:

- `20` dosya
- `2973` insertion
- `14` deletion

8.7 yalnız bağımsız bir resolver eklemedi.

Paket:

- OSM ingestion
- semantic resolution
- context resolution
- spacing resolution
- polyline layout
- physical member production
- terrain attachment
- Foundation First production integration

zincirini birlikte oluşturdu.

## Eklenen ana CORE modülleri

- `CORE/atlas_tree_row_resolver.py`
- `CORE/atlas_tree_row_context_resolver.py`
- `CORE/atlas_tree_row_spacing_resolver.py`
- `CORE/atlas_tree_row_layout_resolver.py`
- `CORE/atlas_tree_row_member_producer.py`

## Güncellenen production modülleri

- `CORE/atlas_foundation_first_engine.py`
- `CORE/atlas_local_osm_reader.py`
- `CORE/atlas_tree_foundation_builder.py`

## Eklenen ana test paketleri

- `Test/test_tree_row_resolver.py`
- `Test/test_tree_row_context_resolver.py`
- `Test/test_tree_row_spacing_resolver.py`
- `Test/test_tree_row_layout_resolver.py`
- `Test/test_tree_row_member_producer.py`

## Güncellenen integration / regression testleri

- `Test/test_foundation_first_engine_tree_water_filter.py`
- `Test/test_foundation_first_road_hierarchy_integration.py`
- `Test/test_local_osm_reader.py`
- `Test/test_tree_foundation_builder.py`

Commit ayrıca güncelledi:

- `Docs/Roadmap/URBAN_FABRIC_PRODUCT_COMPOSITION_V1.md`
- `Docs/START_HERE.md`
- `Docs/STATUS/CURRENT_STATUS.md`

## Candidate tree-row context'leri

8.7 formal tree alignment için en az aşağıdaki urban / landscape
context'lerini dikkate alacak mimariyi oluşturdu:

- roads
- boulevards
- promenades
- park axes
- formal park boundaries
- pedestrian corridors

Tree row yalnız geometrik olarak aynı doğrultuda bulunan tree noktaları
olarak değerlendirilmez.

Çevresindeki urban context de semantic kararın parçasıdır.

## OSM ingestion

`CORE/atlas_local_osm_reader.py` güncellendi.

Böylece gerçek source tree-row kayıtları production input zincirine
alınabilir.

Özellikle source-backed:

- `natural=tree_row`

geometry'sinin ayrı semantic evidence olarak korunmasına temel oluşturuldu.

Bu önemli bir ayrımdır:

> Tree row yalnız mevcut isolated tree noktalarından tahmin edilmek zorunda
> değildir; OSM'nin doğrudan verdiği formal row geometry de kullanılabilir.

## Tree Row Resolver

`AtlasTreeRowResolver` formal vegetation alignment'ın semantic
çözümlemesini yapar.

Resolver'ın görevi bir candidate source'un:

- gerçek tree-row evidence taşıyıp taşımadığını
- hangi semantic role sahip olduğunu
- source geometry continuity bilgisini
- row direction bilgisini
- spacing evidence'ını

değerlendirmektir.

Bu katman physical tree mesh üretmez.

Semantic tree-row kararını oluşturur.

## Evidence-first ilkesi

8.7'nin en kritik kurallarından biri:

> Source evidence olmadan arbitrary tree row üretilmez.

Formal alignment kararı source-backed olmalıdır.

Evidence aşağıdaki türlerden gelebilir:

- explicit tree-row source geometry
- source trees arasında güçlü alignment
- source continuity
- adjacent road/path context
- formal landscape geometry

Ancak yalnız görsel olarak güzel olacağı gerekçesiyle yeni row
oluşturulmaz.

## Strong / weak evidence ayrımı

Tree-row çözümlemesi evidence gücünü dikkate alabilecek biçimde ayrıştırıldı.

Amaç:

- explicit source geometry
- güçlü source-tree alignment
- daha zayıf contextual indication

gibi durumları aynı güven seviyesinde değerlendirmemektir.

Bu yapı arbitrary row invention riskini azaltır.

## Tree Row Context Resolver

`AtlasTreeRowContextResolver` tree-row candidate ile çevresindeki urban
structure arasındaki ilişkiyi çözer.

Candidate context'ler:

- road
- path
- pedestrian corridor
- park axis
- formal boundary

gibi yapılardır.

Context resolver özellikle formal row'un:

- adjacent road/path ile ilişkisini
- parallel urban rhythm oluşturup oluşturmadığını
- çevredeki semantic corridor ile uyumunu

değerlendirmek için temel sağlar.

## Road / pedestrian integration

8.7, daha önce tamamlanan:

- 8.2 Road Hierarchy Engine
- pedestrian fabric

bilgisinden yararlanabilecek biçimde geliştirildi.

Bu nedenle avenue tree row artık road network'ten tamamen bağımsız bir
vegetation objesi değildir.

Formal alignment ile adjacent corridor arasındaki ilişki semantic olarak
korunabilir.

## Tree Row Spacing Resolver

`AtlasTreeRowSpacingResolver` row boyunca kullanılacak spacing kararını
çözer.

Spacing çözümlemesinde iki hedef dengelenir:

1. source truth'u korumak
2. product scale'de okunabilir ve basılabilir spacing sağlamak

Source spacing evidence yeterliyse bu bilgi korunabilir.

Product scale'de aşırı sık representation oluşuyorsa explicit printable /
readable minimum spacing uygulanabilir.

## Product-scale minimum spacing

8.7 gerçek dünya spacing'ini körlemesine ürün geometrisine taşımaz.

Çünkü gerçek ağaç aralıkları küçültüldüğünde:

- tree meshes birbirine girebilir
- aşırı yoğun vegetation oluşabilir
- formal rhythm okunamaz hale gelebilir.

Bu nedenle product-scale minimum spacing kavramı explicit olarak
çözümlenir.

Ancak bu işlem yeni tree row icat etmek için kullanılmaz.

Yalnız mevcut source-backed row'un product representation'ını düzenler.

## Source spacing ve fallback davranışı

Source spacing güvenilir biçimde çözülebiliyorsa tercih edilir.

Source spacing bulunamıyor veya product scale açısından kullanışsızsa
product-readable fallback spacing uygulanabilir.

Fallback'in amacı:

- source olmayan geometry üretmek değil
- source-backed row'u fiziksel üründe okunabilir hale getirmektir.

## Tree Row Layout Resolver

`AtlasTreeRowLayoutResolver` semantic row geometry'sini ordered physical
member positions'a dönüştürür.

Layout çözümlemesi:

- polyline direction
- segment lengths
- spacing
- endpoints
- source continuity
- source gaps

bilgilerini dikkate alır.

Sonuç deterministik ordered tree-member positions'dır.

## Polyline-aware layout

Tree row yalnız düz tek segment olmak zorunda değildir.

Layout resolver polyline boyunca member dağılımı yapabilecek biçimde
geliştirildi.

Böylece source tree-row geometry:

- yön değiştirdiğinde
- birden fazla segment içerdiğinde

formal alignment korunabilir.

## Row direction

Row direction source geometry'den türetilir.

Bu direction daha sonraki:

- member ordering
- spacing
- road/path relationship
- product composition

kararları için korunur.

## Source continuity

8.7 yalnız başlangıç ve bitiş noktalarını kullanarak row'u yeniden
uydurmaz.

Source continuity dikkate alınır.

Amaç source geometry'nin formal ritmini mümkün olduğunca korumaktır.

## Gap preservation

Tree-row source'unda anlamlı gap varsa bu boşluk körlemesine doldurulmaz.

Kritik ilke:

> Product regularization source-backed gaps'i otomatik olarak yok etmemelidir.

Böylece:

- girişler
- yol kesişimleri
- gerçek vegetation boşlukları
- source continuity break'leri

keyfi tree insertion ile kapatılmaz.

## Tree Row Member Producer

`AtlasTreeRowMemberProducer` resolved layout positions'ı fiziksel tree
members'a dönüştürür.

Bu katman:

- semantic row
- ordered member layout
- physical tree representation

arasındaki production bağlantısını oluşturur.

Böylece 8.6'da yalnız semantic role olan `tree_row`, 8.7 sonunda gerçek
physical member producer'a sahip oldu.

## Tree Foundation Builder entegrasyonu

`CORE/atlas_tree_foundation_builder.py` güncellendi.

Tree-row members mevcut terrain/foundation architecture'a bağlandı.

Bu sayede row üyeleri:

- bağımsız havada duran dekoratif objeler değildir
- mevcut terrain attachment sistemini kullanır
- final physical scene ile aynı foundation-first kurallarına uyar.

## Foundation First Engine entegrasyonu

`CORE/atlas_foundation_first_engine.py` 8.7 production zinciri için
güncellendi.

Tree-row pipeline artık final city generation içinde:

- source ingestion
- semantic resolution
- context
- spacing
- layout
- member production
- terrain placement

zincirinden geçebilir.

Bu nedenle 8.7 yalnız teorik resolver paketi değildir.

Production integration mevcuttur.

## Determinism

Aynı:

- source geometry
- source tags
- context
- scale
- spacing policy

için tree-row layout deterministik olmalıdır.

Member ordering ve positions run-to-run keyfi değişmemelidir.

Bu özellik fiziksel ürün reproducibility açısından kritiktir.

## 8.6 ile ilişki

8.6 şu semantic vegetation rollerini oluşturmuştu:

- isolated tree
- tree row
- tree cluster
- forest canopy

8.7 bu sistemin yalnız:

- `tree_row`

kolunu fiziksel production seviyesine genişletti.

Bu nedenle 8.7, 8.6'yı değiştiren alternatif vegetation engine değildir.

8.6'nın üzerine kurulan specialized formal-alignment paketidir.

## Bilinçli olarak yapılmayanlar

8.7 sırasında:

- arbitrary tree rows icat edilmedi
- Bonn-specific avenue rule eklenmedi
- Hofgarten-specific row rule eklenmedi
- coordinate-specific alignment yazılmadı
- source gaps otomatik doldurulmadı
- bütün isolated trees tree-row'a dönüştürülmedi
- bütün road kenarlarına dekoratif trees eklenmedi
- forest-canopy sistemi yeniden yazılmadı
- park semantic engine yeniden yazılmadı
- road hierarchy yeniden yazılmadı
- terrain architecture değiştirilmedi.

## Mimari acceptance sonucu

8.7 sonunda formal tree alignments artık:

- unrelated isolated trees

gibi görünmek zorunda değildir.

Source evidence desteklediğinde:

- ordered
- regularly readable
- context-aware
- terrain-attached
- product-scale printable

urban vegetation rhythm olarak üretilebilir.

## LOCK sonucu

8.7 aşağıdaki nedenle tamamlanmış / kilitlenmiş kabul edildi:

- tree-row source ingestion mevcut
- explicit source evidence korunuyor
- row direction çözülebiliyor
- spacing regularity çözülebiliyor
- source continuity dikkate alınıyor
- gaps korunabiliyor
- product-scale minimum spacing mevcut
- source spacing kullanılabiliyor
- readable fallback spacing mevcut
- adjacent road/path context çözülebiliyor
- deterministic polyline layout mevcut
- ordered physical tree members üretilebiliyor
- tree foundation entegrasyonu mevcut
- Foundation First production entegrasyonu mevcut
- source olmayan arbitrary rows üretilmiyor
- location-specific hack bulunmuyor

## 8.8'e devredilen temel

8.7 sonunda Urban Fabric sistemi artık:

- road hierarchy
- linear infrastructure
- pedestrian fabric
- urban blocks
- semantic parks / plazas
- isolated vegetation
- vegetation clusters
- forest canopies
- formal tree rows

katmanlarını product-semantic biçimde temsil edebiliyordu.

Ancak açık urban surfaces'in kendileri hâlâ büyük ölçüde düz physical
surfaces olarak okunuyordu.

Özellikle semantic farklar:

- plaza paving
- pedestrian square
- park path
- park lawn
- courtyard
- cemetery
- sports field
- generic grass

physical surface language ile yeterince ifade edilmiyordu.

Bu nedenle sıradaki ve güncel aktif paket:

> **8.8 — Semantic Surface Texture Engine**

olarak açıldı.

8.8'in görevi 8.5 tarafından oluşturulan semantic surface identity'yi,
terrain ve foundation mimarisini bozmadan gerçek printable micro-geometry
ile fiziksel olarak ifade etmektir.


# 11. 8.8 — Semantic Surface Texture Engine

**Durum:** ACTIVE / NOT LOCKED — 8 Ağustos 2026

**Commit:** Henüz yok.

8.8 şu anda aktif çalışma paketidir.

Bu paket henüz tamamlanmış veya LOCK edilmiş kabul edilmemelidir.

## Roadmap contract

Amaç:

> Open land ve non-building urban surfaces için shallow, printable ve
> semantic source evidence'a dayanan fiziksel surface language üretmek.

Candidate semantic treatments:

- farmland rows
- grass texture
- forest ground texture
- park lawn texture
- urban plaza texture
- controlled contour / slope texture

Kritik contract:

- texture image değildir
- gerçek physical geometry olmalıdır
- semantic surface identity korunmalıdır
- product readability korunmalıdır
- printability korunmalıdır
- relief depth restrained kalmalıdır
- LoD ile uyumlu olmalıdır
- roads / buildings / landmarks / terrain üzerinde baskın hale gelmemelidir
- semantic source evidence olmadan decorative noise üretilmemelidir

Primary acceptance principle:

> Open surfaces should communicate what kind of place they represent without
> becoming visually or physically noisy.

## 8.8 başlangıç mimari kararı

8.8 mevcut terrain pipeline'ını değiştirmek için açılmadı.

Existing terrain pipeline terrain truth olarak kalır.

Semantic Surface Texture Engine yalnız source-backed açık yüzeylere
product-facing micro-geometry ekler.

Texture sistemi:

- terrain replacement değildir
- image/displacement texture değildir
- arbitrary decorative noise generator değildir.

## 8.5 ile bağlantı

8.8 yeni bir semantic classification sistemi yazmadı.

8.5 tarafından oluşturulan ground surface role contract doğrudan temel
olarak kullanıldı.

Relevant mevcut roller:

- `park_ground`
- `grass_ground`
- `plaza_ground`
- `pedestrian_square_ground`
- `garden_ground`
- `cemetery_ground`
- `sports_field_ground`
- `courtyard_ground`

Bu sayede texture behavior raw OSM tag'lerini yeniden yorumlamak yerine
önceden çözülmüş semantic surface identity üzerinden çalışır.

## Eklenen yeni CORE modülleri

Henüz commit edilmemiş yeni 8.8 modülleri:

- `CORE/atlas_semantic_surface_texture_resolver.py`
- `CORE/atlas_semantic_surface_texture_pattern.py`
- `CORE/atlas_semantic_surface_texture_applier.py`
- `CORE/atlas_semantic_surface_texture_mesher.py`

## Eklenen yeni test modülleri

Henüz commit edilmemiş:

- `Test/test_semantic_surface_texture_resolver.py`
- `Test/test_semantic_surface_texture_pattern.py`
- `Test/test_semantic_surface_texture_applier.py`
- `Test/test_semantic_surface_texture_mesher.py`

## Güncellenen production / regression dosyaları

Tracked değişiklikler:

- `CORE/atlas_foundation_first_engine.py`
- `CORE/atlas_mesh_validator.py`
- `CORE/atlas_park_foundation_builder.py`
- `Test/test_foundation_first_engine_tree_water_filter.py`
- `Test/test_park_foundation_builder.py`

Current tracked diff snapshot:

- `5` tracked dosya
- `391` insertion

Untracked 8.8 CORE/test dosyaları diff-stat içinde görünmemektedir.

## Semantic Surface Texture Resolver

`AtlasSemanticSurfaceTextureResolver` semantic ground role'u physical
surface-language profile'a çözer.

İlk desteklenen semantic mapping'ler:

- `park_ground` → `lawn`
- `grass_ground` → `grass`
- `plaza_ground` → `paving`
- `pedestrian_square_ground` → `paving`
- `garden_ground` → `lawn`
- `cemetery_ground` → `ordered_ground`
- `sports_field_ground` → `field`
- `courtyard_ground` → `paving`

Resolver unknown / unsupported role için zorla texture üretmez.

## Physical texture profile contract

Texture profile aşağıdaki product-facing fiziksel bilgileri taşır:

- `texture_language`
- `relief_depth_mm`
- `feature_pitch_mm`
- `lod_min_level`

İlk profile sınırları restrained relief amacıyla düşük tutuldu.

Doğrulanan profile limitleri arasında:

- park/lawn: relief `<= 0.20 mm`
- grass: relief `<= 0.20 mm`
- plaza/paving: relief `<= 0.16 mm`
- pedestrian square/paving: relief `<= 0.16 mm`

bulunur.

Semantic texture relief genel scene geometry yanında secondary kalmalıdır.

## Texture languages

8.8 pattern motorunda şu fiziksel surface languages geliştirildi:

- `paving`
- `lawn`
- `grass`
- `ordered_ground`
- `field`

Bu pattern'ler yalnız renk farkı değildir.

Her biri XY noktasında controlled physical Z emboss üretir.

## Non-negative emboss kararı

Surface texture için önemli fiziksel karar:

> Texture nominal surface'in altına oyulmayacak; restrained positive emboss
> olarak üretilecek.

Özellikle paving pattern ilk denemede negatif değerlere düşüyordu.

Bu davranış test-first düzeltilerek:

- minimum offset `>= 0`
- maximum offset profile relief depth sınırında

olacak şekilde kilitlendi.

Aynı non-negative emboss ilkesi lawn / grass / ordered_ground / field
pattern'lerine de uygulandı.

## Lawn ve grass ayrımı

`lawn` ile `grass` aynı pattern değildir.

Amaç:

- controlled/bakımlı park lawn
- generic grass surface

arasında fiziksel dil farkı oluşturmak.

Her ikisi de restrained emboss üretir ancak farklı pattern ve pitch
davranışına sahip olabilir.

## Ordered ground ve field ayrımı

Cemetery-like ordered ground ile sports field generic lawn olarak
yorumlanmaz.

8.8 içinde:

- `ordered_ground`
- `field`

ayrı surface language olarak desteklenir.

Bu distinction ileride morphology/product calibration için korunmalıdır.

## İlk Semantic Surface Texture Applier

`AtlasSemanticSurfaceTextureApplier` mevcut closed surface mesh'in yalnız
top contract'ını semantic pattern ile değiştirmek için geliştirildi.

İlk applier yaklaşımı:

- source mesh'i mutate etmez
- bottom'u korur
- top Z'lerini değiştirir
- triangle references'i yeni top points'e remap eder
- semantic texture metadata ekler.

## Printability contract

Applier katmanında minimum printable surface thickness kontrolü eklendi.

Amaç texture emboss nedeniyle mevcut physical surface'in basılabilirliğinin
bozulmamasıdır.

Nozzle diameter product contract'a dahil edildi.

## LoD compatibility

8.8 mevcut ATLAS LoD architecture ile bağlandı.

Texture profile:

- `lod_min_level`

taşır.

Applier optional:

- `lod_level`

kabul eder.

Current behavior:

- requested LoD profile minimumunun altındaysa texture uygulanmaz
- profile minimumuna ulaşıldığında texture uygulanabilir
- uygulanan LoD metadata içinde `applied_lod_level` olarak korunur.

LoD type:

- `AtlasLoDLevel`

olmalıdır.

Bu nedenle 8.8 yeni LoD sistemi yazmamıştır; mevcut LoD contract'ını kullanır.

## İlk applier yaklaşımının gerçek limitinin bulunması

Köln gerçek source incelemesinde kritik limit tespit edildi:

> İlk semantic applier yalnız mevcut surface vertex'lerinin Z değerlerini
> değiştiriyordu; yüzeyi subdivide etmiyordu.

Köln PF source örnekleri:

- park polygonları onlarca source vertex taşıyabiliyor
- grass polygons çoğu zaman çok az vertex taşıyor

Bu nedenle yalnız existing vertices üzerinde pattern sampling yapılması
physical texture'ın yüzey boyunca yeterince görünür olmasını sağlamıyordu.

Bu bulgu dense physical mesher ihtiyacını doğurdu.

## Dense Semantic Surface Texture Mesher

Yeni:

- `AtlasSemanticSurfaceTextureMesher`

geliştirildi.

Bu mesher semantic surface içinde gerçek yeni physical vertices üretir.

Temel davranış:

- polygon boundary densification
- interior grid point generation
- polygon-contained triangulation
- semantic pattern sampling
- closed physical solid
- boundary wall generation.

Bu yaklaşım mevcut water textured solid mesher'daki kanıtlanmış dense
surface prensiplerinden yararlandı ancak semantic surface için ayrı contract
oluşturdu.

## Dense geometry contract

Dense mesher:

- boundary vertex'lerini densify eder
- interior points ekler
- polygon içinde surface triangulation üretir
- top surface'i semantic emboss ile yükseltir
- bottom surface üretir
- boundary walls üretir
- closed/manifold solid oluşturur.

Sonuç metadata:

- `surface_texture_enabled`
- `surface_vertex_count`
- `boundary_vertex_count`
- `interior_vertex_count`
- `maximum_edge_length_mm`

gibi fiziksel bilgileri taşıyabilir.

## Boundary behavior

Dense texture'ın ürün yüzeyinde komşu geometry ile kırık oluşturmaması için
boundary nominal surface height'ta tutulur.

Kural:

- boundary emboss = `0`
- interior semantic emboss > `0` olabilir.

Bu sayede texture yüzey sınırında controlled biçimde söner.

## Mesh validator problemi ve genel çözüm

Dense surface geliştirilirken mevcut `AtlasMeshValidator` şu eski
varsayıma sahipti:

- `len(walls) == len(bottom)`

Bu perimeter-only solids için geçerliydi.

Dense surface'te ise:

- `bottom/top` = boundary + interior vertices
- `walls` = yalnız boundary perimeter

olduğu için valid dense mesh yanlışlıkla:

- `wall_count_mismatch`

olarak reddediliyordu.

Örnek ilk dense square:

- top vertices: `64`
- boundary vertices: `28`
- interior vertices: `36`
- walls: `28`
- triangles: `252`

## Boundary-aware validator contract

`CORE/atlas_mesh_validator.py` genel biçimde güncellendi.

Yeni contract:

- `boundary_top` yoksa legacy behavior korunur
- `boundary_top` varsa wall count boundary vertex count üzerinden doğrulanır
- road-foundation özel davranışı korunur.

Bu değişiklik yalnız semantic texture için hard-coded exception değildir.

Dense physical solids için genel boundary-aware structure contract'tır.

Validation:

- semantic mesher
- water textured solid
- foundation mesh extruder

birlikte çalıştırıldı.

Sonuç:

- `42 passed in 0.11s`

## Terrain truth problemi

İlk dense mesher:

- sabit `bottom_z`
- sabit `surface_z`

ile çalışıyordu.

Bu flat synthetic test için yeterliydi ancak production için doğru değildi.

Gerçek parks mevcut terrain'i takip ediyor.

Dense mesher parkı düzleştirirse 8.8 semantic texture eklerken terrain truth
bozulacaktı.

Bu nedenle production entegrasyonundan önce terrain-following davranış
zorunlu kabul edildi.

## Terrain-following dense mesher

`AtlasSemanticSurfaceTextureMesher.build_terrain_following(...)`
geliştirildi.

Bu method mevcut:

- `AtlasFoundationSampler.terrain_z_at_xy(...)`

altyapısını kullanır.

Her dense XY vertex için:

1. gerçek terrain Z örneklenir
2. bottom = terrain Z
3. nominal top = terrain Z + foundation height
4. interior semantic emboss nominal top üzerine eklenir
5. boundary nominal foundation height'ta kalır.

Böylece:

- terrain truth korunur
- foundation thickness korunur
- semantic micro-relief eklenir.

## Terrain-following topology

Terrain-following semantic surface için test edilen contract:

- bottom Z tek düzlem olmak zorunda değil
- dense vertices gerçek terrain'i takip eder
- boundary top-bottom farkı nominal foundation height'tır
- interior relief yalnız positive emboss olarak eklenir
- final solid closed/manifold kalır.

Terrain-following mesher + applier + park tests:

- `28 passed in 0.10s`

## Park source identity

Production semantic processing için park foundation mesh'lerinin source
identity taşıması gerektiği tespit edildi.

`CORE/atlas_park_foundation_builder.py` güncellendi.

Park mesh artık:

- `source_id`

koruyabilir.

Bu sayede final park mesh doğru OSM park source record ile yeniden
eşleştirilebilir.

## Foundation First semantic source matching

`AtlasFoundationFirstEngine` içinde semantic surface processing helper
eklendi.

Helper:

- park meshes
- original park source records
- pedestrian paths

arasında source identity üzerinden ilişki kurar.

Böylece semantic texture:

- mesh sırasına
- list index'ine
- geometry guess'e

dayanmaz.

Source identity üzerinden doğru surface role bulunur.

## Foundation First production integration

`CORE/atlas_foundation_first_engine.py` 8.8 için güncellendi.

Semantic texture production zinciri:

1. parks source records
2. park foundation meshes
3. source identity matching
4. `AtlasParkPlazaSemanticResolver`
5. semantic ground role
6. `AtlasSemanticSurfaceTextureResolver`
7. LoD eligibility
8. texture pattern
9. dense terrain-following mesher
10. final scene assembly

şeklinde çalışabilir.

## Backward-compatible fallback

Terrain mesh helper'a verilmezse mevcut vertex-level applier yolu fallback
olarak korunmuştur.

Production path'te ise:

- `terrain_mesh=terrain_slab`

bağlantısı yapılmıştır.

Bu sayede gerçek Foundation First product üretimi dense terrain-following
semantic surface geometry kullanabilir.

## Focused production integration validation

8.8 semantic resolver / pattern / applier / mesher / park / Foundation First
ilgili paketleri birlikte çalıştırıldı.

Son bilinen focused integration sonucu:

- `72 passed in 0.24s`

Bu test sonucu full project regression değildir.

8.8 için full regression henüz bu aktif çalışma noktasında yeniden
çalıştırılmamıştır.

## Köln PF gerçek source validation

8.8 gerçek veri üzerinde:

- Köln Pädagogische Fakultät

PBF fixture ile doğrulandı.

Source:

`Data/OSM/koeln-paedagogische-fakultaet-test.osm.pbf`

Merkez:

- `50.93428235`
- `6.91972655`

Scale:

- `1:5500`

City area:

- `134 mm`

## Köln semantic source resolution

Köln fixture içinde:

- `20` park source record

bulundu.

Semantic texture'a çözülen:

- `3` `park_ground`
- `13` `grass_ground`

Toplam textured source:

- `16`

Texture language dağılımı:

- `3` lawn
- `13` grass

Kalan source'lar supported semantic role üretmediği için arbitrary texture
almadı.

Bu source-evidence contract açısından doğru davranıştır.

## İlk Köln semantic STL

Vertex-only semantic texture ile ilk Köln output:

`OUTPUT/STL/koeln_paedagogische_fakultaet_134mm_semantic_surface_texture_8_8.stl`

Sonuç:

- meshes: `731`
- triangles: `35690`
- reader parks: `20`

Bu output semantic role routing'in çalıştığını doğruladı ancak surface
subdivision eksikliğini gösterdi.

## Dense Köln semantic STL

Dense terrain-following mesher production'a bağlandıktan sonra yeni output:

`OUTPUT/STL/koeln_paedagogische_fakultaet_134mm_semantic_surface_texture_8_8_dense.stl`

Sonuç:

- meshes: `731`
- triangles: `42938`
- reader parks: `20`

Önceki semantic STL:

- `35690` triangles

Dense STL:

- `42938` triangles

Artış:

- `+7248` triangles
- yaklaşık `%20.3`

Mesh count aynı kaldı:

- `731`

Bu kritik doğrulama şunu gösterir:

> 8.8 yeni gereksiz scene objects eklemiyor;
> mevcut semantic surfaces içine gerçek dense physical geometry ekliyor.

## OBJ / MTL validation

Dense 8.8 geometry için existing OBJ/MTL exporter ile interactive preview
üretildi.

OBJ:

`OUTPUT/PREVIEW/koeln_paedagogische_fakultaet_134mm_semantic_surface_texture_8_8_dense.obj`

MTL:

`OUTPUT/PREVIEW/koeln_paedagogische_fakultaet_134mm_semantic_surface_texture_8_8_dense.mtl`

Source city STL:

- `42938` triangles

OBJ material scene:

- `39075` triangles

Material profile:

- `COMPETITOR_COMPARISON_V1`

OBJ/MTL export başarılıdır.

## Görsel validation sonucu

Dense geometry teknik olarak başarılıdır.

OBJ/MTL görsel incelemesinde:

- green semantic surfaces doğru material family içinde görünür
- park/grass boundaries okunabilir
- roads ve buildings korunur
- vegetation sistemi korunur
- semantic texture fiziksel geometry olarak mevcuttur.

Ancak mevcut lawn / grass surface calibration henüz acceptance seviyesinde
değildir.

## Mevcut görsel problem

Yakın OBJ görünümünde lawn / grass surfaces üzerinde belirgin:

- triangular
- faceted
- mosaic-like

surface appearance görülmektedir.

Bu görünüm bazı geniş green surfaces'te semantic grass/lawn yerine
triangulated terrain hissi vermektedir.

Bu nedenle 8.8 şu anda:

- teknik geometry validation: başarılı
- production integration validation: başarılı
- visual calibration: henüz başarısız / açık

durumdadır.

## Mevcut lawn / grass profile değerleri

Son gerçek Köln validation sırasında kullanılan bilinen değerler:

- lawn:
  - relief depth yaklaşık `0.18 mm`
  - feature pitch yaklaşık `1.40 mm`

- grass:
  - relief depth yaklaşık `0.18 mm`
  - feature pitch yaklaşık `1.20 mm`

Bu değerler henüz LOCK edilmemelidir.

## İlk görsel calibration yönü

Görsel değerlendirme sonrası candidate calibration yönü:

- lawn:
  - relief depth düşürülebilir
  - feature pitch genişletilebilir

- grass:
  - relief depth düşürülebilir
  - feature pitch kontrollü biçimde genişletilebilir

İlk tartışılan candidate değerler:

- lawn: `0.08 mm / 2.40 mm`
- grass: `0.10 mm / 1.80 mm`

Ancak bunlar henüz accepted veya implemented profile değerleri değildir.

**Devir sırasında bunları LOCK edilmiş değer gibi kullanma.**

## 9 Ağustos 2026 — Lawn / Grass Calibration İlk Test-First Adımı

8.8 lawn / grass calibration için ilk candidate değerler test-first biçimde
production resolver'a uygulanmıştır.

Önce yeni regression testi eklenmiş ve mevcut profile değerleriyle beklenen
kırmızı sonuç alınmıştır:

- `2 failed`
- `15 passed`

Kırmızı test şu candidate product değerlerini talep etmektedir:

- `park_ground / lawn`
  - `relief_depth_mm = 0.08`
  - `feature_pitch_mm = 2.40`

- `grass_ground / grass`
  - `relief_depth_mm = 0.10`
  - `feature_pitch_mm = 1.80`

Ardından yalnız:

- `CORE/atlas_semantic_surface_texture_resolver.py`

içindeki lawn / grass profile değerleri değiştirilmiştir.

Diğer semantic surface profillerine dokunulmamıştır.

Focused resolver validation:

- `17 passed in 0.02s`

Bu değerler artık implementation içinde candidate calibration olarak
bulunmaktadır ancak henüz **LOCK / accepted production standardı değildir**.

Eksik acceptance adımları:

- related 8.8 regression
- dense Köln PF STL yeniden üretimi
- OBJ/MTL yeniden üretimi
- önceki sonuçla A/B görsel karşılaştırma
- faceted / triangular görünümün kabul seviyesine inmesi
- physical relief ve printability kontrolü
- full regression

Bu görsel ve teknik acceptance tamamlanmadan 8.8 LOCK edilmemeli ve 8.9'a
geçilmemelidir.



## 9 Ağustos 2026 — Köln PF Calibrated Dense Production Validation

Candidate lawn / grass calibration gerçek Köln PF benchmark'ında production
hattı üzerinden yeniden doğrulandı.

Uygulanan candidate değerler:

- lawn: `0.08 mm relief / 2.40 mm pitch`
- grass: `0.10 mm relief / 1.80 mm pitch`

Focused resolver validation:

- `17 passed`

Related 8.8 regression:

- `74 passed`

Yeni calibrated dense city STL:

`OUTPUT/STL/koeln_paedagogische_fakultaet_134mm_semantic_surface_texture_8_8_calibrated.stl`

Sonuç:

- triangles: `38426`

Önceki dense city STL referansı:

- triangles: `42938`

Değişim:

- `-4512` triangles
- yaklaşık `%10.5` daha az triangle

Yeni calibrated preview:

`OUTPUT/PREVIEW/koeln_paedagogische_fakultaet_134mm_semantic_surface_texture_8_8_calibrated.obj`

`OUTPUT/PREVIEW/koeln_paedagogische_fakultaet_134mm_semantic_surface_texture_8_8_calibrated.mtl`

OBJ exporter sonucu:

- profile: `COMPETITOR_COMPARISON_V1`
- triangles: `45184`

Eski devir kaydındaki `39075` OBJ triangle değeri ile bu sayı, scene/export
kapsamının bire bir aynı olduğu doğrulanmadan doğrudan calibration metriği
olarak karşılaştırılmamalıdır.

Current acceptance:

- candidate implementation: GREEN
- related regression: GREEN
- real Köln dense STL production: SUCCESS
- OBJ/MTL production: SUCCESS
- visual A/B acceptance: PENDING
- 8.8: `ACTIVE / NOT LOCKED`

Sıradaki kritik iş, calibrated lawn / grass yüzeylerinin görsel A/B
değerlendirmesidir. Faceted / triangular / mosaic-like görünüm kabul
seviyesine düşmeden candidate değerler LOCK edilmemelidir.



## 9 Ağustos 2026 — Köln PF Calibrated Dense Visual Evaluation

Köln PF calibrated dense STL ve preview çıktıları Bambu Studio görsel
incelemesinden geçirildi.

Gözlenen ana sonuçlar:

- lawn / grass calibration sonrası faceted / triangular / mosaic-like açık
  yüzey görünümü belirgin biçimde azalmıştır
- roads / buildings / landmark kütleleri baskın görsel hierarchy'yi korumaktadır
- açık yüzeylerdeki semantic texture artık daha sakin ve daha az gürültülüdür
- ancak lawn / grass surface language bazı alanlarda fazla zayıflamış görünmektedir
- park lawn ile generic grass ayrımı henüz yeterince güçlü okunmamaktadır

Bu nedenle mevcut candidate calibration için görsel karar:

- **improved but not yet accepted**

Current visual interpretation:

- faceting problemi iyileşmiştir
- semantic readability bir miktar zayıflamıştır
- texture tamamen reddedilecek kadar kötü değildir
- ancak 8.8 acceptance için henüz yeterli değildir

Sonuç:

- 8.8 `ACTIVE / NOT LOCKED` olarak kalır
- mevcut candidate değerler final / LOCK standardı değildir
- sıradaki iş küçük bir ikinci calibration turu ile lawn / grass semantic
  okunabilirliğini kontrollü biçimde artırmaktır

Candidate next calibration direction:

- lawn: `0.10 mm / 2.20 mm`
- grass: `0.12 mm / 1.60 mm`

Bu değerler henüz test-first uygulanmış accepted profile'lar değildir; yalnız
bir sonraki dar kapsamlı calibration denemesi için aday yöndür.


## Şu anda yapılmaması gerekenler

8.8 tamamlanmadan:

- 8.9'a geçilmemeli
- 8.8 LOCK ilan edilmemeli
- mevcut lawn/grass değerleri final kabul edilmemeli
- faceted görünüm göz ardı edilmemeli
- texture depth körlemesine artırılmamalı
- source evidence olmayan surfaces'e texture eklenmemeli
- terrain pipeline yeniden yazılmamalı
- dense mesher geri alınmamalı; önce calibration çözülmeli.

## Current git state

8 Ağustos 2026 aktif çalışma ağacı:

Tracked modified:

- `CORE/atlas_foundation_first_engine.py`
- `CORE/atlas_mesh_validator.py`
- `CORE/atlas_park_foundation_builder.py`
- `Test/test_foundation_first_engine_tree_water_filter.py`
- `Test/test_park_foundation_builder.py`

Untracked 8.8 implementation/tests:

- `CORE/atlas_semantic_surface_texture_applier.py`
- `CORE/atlas_semantic_surface_texture_mesher.py`
- `CORE/atlas_semantic_surface_texture_pattern.py`
- `CORE/atlas_semantic_surface_texture_resolver.py`
- `Test/test_semantic_surface_texture_applier.py`
- `Test/test_semantic_surface_texture_mesher.py`
- `Test/test_semantic_surface_texture_pattern.py`
- `Test/test_semantic_surface_texture_resolver.py`

Diğer bilinen untracked dosyalar:

- `Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-08-01.md`
- `Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-08-04.md`
- `Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-08-08.md`
- `Test/preview_church_semantic_surfaces.py`

Bu dosyalar bulk `git add .` ile stage edilmemelidir.

## 8.8 current acceptance state

Tamamlanan teknik alt parçalar:

- semantic texture resolver
- semantic pattern contract
- restrained positive emboss
- LoD gating
- initial top-surface applier
- dense surface mesher
- boundary-aware mesh validation
- terrain-following dense geometry
- park source identity preservation
- Foundation First semantic matching
- production dense-mesher integration
- real Köln PBF validation
- dense STL validation
- OBJ/MTL validation

Açık kalan kritik parça:

> lawn / grass physical surface calibration.

Bu nedenle 8.8 **ACTIVE / NOT LOCKED** kalır.

## Kesin sonraki adım

8.8'de devam edilecek tek ana iş:

> Lawn ve grass profile'larını test-first biçimde kalibre etmek ve aynı Köln
> PF benchmark üzerinde yeni dense STL + OBJ/MTL A/B validation yapmak.

Acceptance kontrolü:

- semantic identity okunmalı
- physical emboss görünmeli
- triangle facets baskın görünmemeli
- roads / buildings / landmarks / terrain secondary hale düşmemeli
- physical relief restrained kalmalı
- printability korunmalı.

Bu validation başarılı olmadan 8.8 LOCK edilmemelidir.

## 8.9'a geçiş koşulu

Sıradaki roadmap paketi:

> **8.9 — Morphology-Aware Terrain Product Resolver**

Ancak 8.9 yalnız şu koşullardan sonra açılmalıdır:

1. lawn/grass calibration kabul edilir
2. focused 8.8 tests yeşildir
3. related regression yeşildir
4. full regression yeşildir
5. gerçek Köln visual acceptance alınır
6. 8.8 dokümantasyonu güncellenir
7. scoped commit yapılır
8. push doğrulanır
9. tracked working tree güvenli hale gelir.



# 12. 8.9–8.20 — Sonraki Urban Fabric Roadmap

Aşağıdaki paketler 8.8 tamamlandıktan sonra sırayla ele alınacaktır.

Bu maddeler henüz implementation / LOCK durumu taşımaz.

## 8.9 — Morphology-Aware Terrain Product Resolver

Terrain presentation ürün alanının morphology karakterine göre
uyarlanacaktır.

Kritik sınır:

> Mevcut terrain pipeline terrain truth olarak kalır.

Bu paket terrain kaynağını yeniden yazmak için değil, mevcut terrain truth'un
ürün ölçeğinde nasıl ifade edileceğini morphology-aware biçimde çözmek için
açılacaktır.

## 8.10 — Water & Shoreline Composition Engine

Water ve waterfront structure için genel product-composition sistemi
oluşturulacaktır.

Amaç su yüzeyini yalnız bağımsız bir polygon/mesh olarak değil,
shoreline ve surrounding urban fabric ilişkisi içinde ifade etmektir.

## 8.11 — Bridge / Infrastructure Urban Integration

Mevcut ATLAS bridge capability'leri Urban Fabric composition sistemi içinde
yeniden kullanılacaktır.

Kritik sınır:

> Bridge engine yeniden yazılmayacaktır.

Amaç mevcut bridge sistemini road, infrastructure ve surrounding city
composition ile daha doğru bağlamaktır.

## 8.12 — Building Height Product Normalizer

Generic building height product readability için normalize edilecektir.

Ancak architecturally meaningful height information korunmalıdır.

8.0 audit sonucu doğrulanan kritik sınır:

- generic height hattı genel olarak tutarlıdır
- landmark / historic morphology exaggeration ile parser bug birbirine
  karıştırılmamalıdır.

Bu nedenle 8.12 source truth'u silen toplu height flattening yapmamalıdır.

## 8.13 — Physical Cartographic Exaggeration Resolver

Strict real-world scale altında fiziksel olarak okunamayacak features için
explicit cartographic exaggeration policy geliştirilecektir.

Amaç exaggeration'ı dağınık minimum değerler ve ad-hoc builder kuralları
yerine ortak product contract üzerinden yönetmektir.

## 8.14 — City Composition LoD

Mevcut ATLAS LoD sistemi individual mesh complexity seviyesinden
whole-city composition seviyesine genişletilecektir.

Kritik sınır:

> Mevcut LoD architecture yeniden yazılmayacaktır.

Urban Fabric layers ve block/morphology context mevcut LoD sistemiyle
birlikte çalışacaktır.

## 8.15 — Scene Morphology Classifier

Product area dominant urban / landscape karakterine göre
sınıflandırılacaktır.

Bu classification daha sonraki composition policy'nin hangi scene
davranışını kullanacağını belirleyecek semantic context'i sağlayacaktır.

## 8.16 — Morphology Composition Policy

Resolved scene morphology'ye göre product-composition behavior uygulanacaktır.

Kritik ilke:

> Relative emphasis değişebilir ancak source truth değişmemelidir.

Bu katman farklı morphology tiplerinde roads, blocks, vegetation, terrain,
water ve landmarks arasındaki göreli product emphasis'i yönetecektir.

## 8.17 — Semantic Color / Material Hierarchy

Urban scenes için product-level semantic material hierarchy oluşturulacaktır.

Color/material seçimi yalnız decorative amaçla yapılmamalıdır.

Amaç:

- semantic role
- product hierarchy
- readability

bilgisini material/color sistemi üzerinden ifade etmektir.

## 8.18 — Customer Preview Parity

Customer-facing preview ile physical production scene aynı semantic
composition policy'yi kullanmalıdır.

Amaç preview ile gerçek baskı arasında:

- semantic content
- emphasis
- material hierarchy
- scene composition

açısından tutarsızlık oluşmasını engellemektir.

## 8.19 — Urban Fabric Quality Report

Urban composition için read-only quality report geliştirilecektir.

Kritik sınır:

> Quality report geometry'yi sessizce değiştirmemelidir.

Görevi scene quality'yi ölçmek, eksikleri raporlamak ve acceptance
kararlarına veri sağlamaktır.

## 8.20 — Multi-Morphology Acceptance Benchmarks

Bonn ilk kontrollü Urban Fabric benchmark'tır.

Ancak Urban Fabric V1 acceptance yalnız Bonn'a dayandırılmayacaktır.

Final V1 acceptance farklı morphology tiplerini kapsayan birden fazla gerçek
benchmark üzerinde yapılmalıdır.

## Roadmap sıra kuralı

8.8 tamamlanmadan 8.9 açılmamalıdır.

Sonraki sıra:

`8.8 → 8.9 → 8.10 → 8.11 → 8.12 → 8.13 → 8.14 → 8.15 → 8.16 → 8.17 → 8.18 → 8.19 → 8.20`

Her paket:

- test-first
- general solution
- narrow scope
- regression
- documentation
- scoped commit
- push doğrulaması

disipliniyle yürütülmelidir.



# 13. Git / Repository Güvenlik Noktası

## Branch

Aktif branch:

- `main`

## Son güvenli HEAD

Doğrulanan HEAD:

`956b0990fa6e71431395dffd0be63abaa8e1549d`

Commit:

`956b099 Add avenue tree row engine`

## Remote durumu

Doğrulanan:

`origin/main = 956b0990fa6e71431395dffd0be63abaa8e1549d`

Yani:

> `HEAD == origin/main`

8.7 sonuna kadar repository remote ile senkrondur.

Son temiz ve push edilmiş milestone:

> `956b099 Add avenue tree row engine`

## Urban Fabric commit zinciri

Güncel önemli commit sırası:

- `2de13c3` — Add Urban Fabric Product Composition V1 roadmap
- `328137b` — Complete Bonn urban fabric ground-truth audit
- `00e60c0` — Add urban fabric scene contract
- `e75cb10` — Add urban road hierarchy engine
- `b6d8eaf` — Add linear infrastructure engine
- `e93f217` — Add urban block resolver
- `83c0038` — Document preview architecture research
- `4a4d5bb` — Add park and plaza semantic surface engine
- `9b0aa22` — Add vegetation composition engine
- `956b099` — Add avenue tree row engine

Bu zincir 8.0–8.7 tamamlanmış Urban Fabric milestone'larını temsil eder.

## Aktif 8.8 çalışma ağacı

8.8 Semantic Surface Texture Engine henüz commit edilmemiştir.

Tracked modified:

- `CORE/atlas_foundation_first_engine.py`
- `CORE/atlas_mesh_validator.py`
- `CORE/atlas_park_foundation_builder.py`
- `Test/test_foundation_first_engine_tree_water_filter.py`
- `Test/test_park_foundation_builder.py`

Yeni / untracked 8.8 implementation:

- `CORE/atlas_semantic_surface_texture_applier.py`
- `CORE/atlas_semantic_surface_texture_mesher.py`
- `CORE/atlas_semantic_surface_texture_pattern.py`
- `CORE/atlas_semantic_surface_texture_resolver.py`

Yeni / untracked 8.8 tests:

- `Test/test_semantic_surface_texture_applier.py`
- `Test/test_semantic_surface_texture_mesher.py`
- `Test/test_semantic_surface_texture_pattern.py`
- `Test/test_semantic_surface_texture_resolver.py`

Diğer mevcut untracked dosyalar:

- `Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-08-01.md`
- `Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-08-04.md`
- `Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-08-08.md`
- `Test/preview_church_semantic_surfaces.py`

## Staging durumu

Son `git status --short` çıktısında staged değişiklik görünmemektedir.

Tracked 8.8 dosyaları working-tree modification durumundadır.

Yeni 8.8 dosyaları untracked durumdadır.

Bu nedenle sonraki oturum:

> mevcut dosyaları kaybetmeden çalışmaya devam etmelidir.

## Kritik Git güvenlik kuralı

Şu anda:

- `git reset --hard`
- `git clean`
- bulk cleanup
- `git checkout -- .`
- `git restore .`
- `git add .`

gibi geniş kapsamlı komutlar kullanılmamalıdır.

Bunlar aktif ve henüz commit edilmemiş 8.8 çalışmasını silebilir veya
istenmeyen dosyaları stage edebilir.

ATLAS çalışma kuralı korunmalıdır:

- yalnız ilgili dosyalar stage edilir
- önce focused tests
- sonra related regression
- sonra full regression
- documentation güncellenir
- scoped commit yapılır
- push edilir
- `HEAD == origin/main` tekrar doğrulanır.


# 14. Kesin Devam Noktası

Aktif roadmap paketi:

> **8.8 — Semantic Surface Texture Engine**

Durum:

> **ACTIVE / NOT LOCKED**

8.9'a geçilmemelidir.

## Son doğrulanmış teknik nokta

Dense terrain-following semantic surface geometry production'a bağlandı.

Köln PF gerçek benchmark sonucu:

- city size: `134 mm`
- scale: `1:5500`
- source parks: `20`
- textured semantic sources: `16`
- vertex-only STL: `35690` triangles
- dense STL: `42938` triangles
- dense geometry artışı: `+7248` triangles
- scene mesh count: `731`

Dense OBJ/MTL preview:

- OBJ triangles: `39075`
- profile: `COMPETITOR_COMPARISON_V1`

Teknik geometry / topology / production integration başarılıdır.

## Açık kritik problem

Lawn ve grass texture geometry'si yakın görsel incelemede fazla:

- triangular
- faceted
- mosaic-like

okunmaktadır.

Bu nedenle mevcut:

- lawn `~0.18 mm / 1.40 mm`
- grass `~0.18 mm / 1.20 mm`

değerleri final değildir ve LOCK edilmemelidir.

## Sonraki tek geliştirme işi

İlk yapılacak iş:

> Lawn ve grass physical surface calibration'ını test-first biçimde
> geliştirmek.

Ardından aynı Köln PF benchmark üzerinde:

1. dense STL üret
2. OBJ/MTL üret
3. mevcut sonuçla A/B karşılaştır
4. semantic readability kontrol et
5. faceted görünümü kontrol et
6. physical relief'i kontrol et
7. printability'yi kontrol et.

İlk konuşulan candidate calibration:

- lawn: `0.08 mm / 2.40 mm`
- grass: `0.10 mm / 1.80 mm`

Bunlar yalnız candidate değerlerdir.

Test yazılmadan ve görsel kabul alınmadan production standardı yapılmamalıdır.

## 8.8 LOCK koşulları

8.8 ancak aşağıdakilerin tamamı sağlanırsa tamamlanmış kabul edilmelidir:

- lawn calibration accepted
- grass calibration accepted
- texture semantic olarak okunabilir
- faceted triangle görünümü baskın değil
- roads/buildings/landmarks/terrain baskın hierarchy'yi koruyor
- relief restrained
- printability korunuyor
- focused 8.8 tests yeşil
- related regression yeşil
- full regression yeşil
- Köln real-data visual acceptance başarılı
- `Docs/START_HERE.md` güncel
- `Docs/STATUS/CURRENT_STATUS.md` güncel
- Roadmap 8.8 status güncel
- yalnız ilgili dosyalar stage edilmiş
- scoped commit oluşturulmuş
- push başarılı
- `HEAD == origin/main`
- tracked çalışma ağacı güvenli.

Bunlardan önce 8.9 açılmamalıdır.


# 15. Devir Özeti

Yeni oturum / yeni motor bu belgeyi okuduğunda aşağıdaki durumu esas
almalıdır:

1. Urban Fabric Roadmap 8.0–8.7 tamamlandı.
2. Son temiz ve push edilmiş repository noktası `956b099`'dır.
3. 8.8 aktif ve commit edilmemiş durumdadır.
4. 8.8 semantic surface architecture'ın büyük kısmı implementation ve
   focused validation seviyesinde tamamlanmıştır.
5. Dense terrain-following physical texture production'a bağlanmıştır.
6. Köln PF real-data benchmark teknik olarak çalışmaktadır.
7. Mevcut blocker geometry/topology değildir.
8. Mevcut blocker lawn/grass görsel surface calibration'ıdır.
9. Aktif 8.8 working tree korunmalıdır.
10. 8.9'a geçilmemelidir.
11. İlk sonraki işlem lawn/grass calibration için test-first çalışmadır.
12. General solutions only kuralı korunmalıdır; Köln-specific texture hack
    yazılmamalıdır.

Bu belge 8 Ağustos 2026 mola noktasıdır.


## 9 Ağustos 2026 — Dense Park Topology Root-Cause Isolation

- Köln calibrated mesh-group diagnostic: `parks = 1340 open / 0 non-manifold`.
- Diğer ölçülen scene gruplarında open edge: `0`.
- Park meshes: `20`; semantic-textured: `16`; problemli/invalid: `14`.
- Örnek source_id: `241687376=366`, `261884192=50`, `315154036=34`, `315156279=22`, `315156280=140` open edge.
- Kök neden artık dense semantic park geometry hattına daraltılmıştır; genel STL writer problemi olarak değerlendirilmemelidir.
- Sıradaki iş: `AtlasSemanticSurfaceTextureMesher` triangulation ve boundary-wall contractını incelemek ve gerçek Köln polygonlarında boundary failure nedenini bulmak.
- Topology çözülmeden ikinci lawn/grass calibration turuna geçilmez; 8.8 `ACTIVE / NOT LOCKED` kalır.

## 9 Ağustos 2026 — Dense Surface Boundary Contract Root Cause Confirmed

- Köln gerçek parklarında 8.8 open-edge kök nedeni kesin olarak izole edildi.
- Dense surface top/bottom triangulation perimeter ile `dense_boundary` wall perimeter aynı edge setini kullanmıyor.
- `source_id=1376882403`: actual surface perimeter `3`, intended dense boundary `8`, shared `2`, missing `6`, extra `1`, symmetric difference `7`.
- Aynı triangulation bottom yüzeyde tekrarlandığı için `7 top + 7 bottom = 14 open edge`; production sonucu ile bire bir eşleşiyor.
- `source_id=241687376`: boundary symmetric difference `183`; sonuç `366 open edge`; production sonucu ile bire bir eşleşiyor.
- Ana neden `triangulate(MultiPoint(all_points))` yaklaşımının intended polygon boundary edge contractını garanti etmemesidir.
- İlk synthetic concave test ve post-densification 8-point fixture problemi yeniden üretmedi; doğru regression fixture productiona giren pre-dense source boundaryden çıkarılmalıdır.
- Sıradaki iş: problemli gerçek Köln parkının pre-dense boundary koordinatlarını yakalamak, kırmızı focused regression oluşturmak ve ancak sonra general constrained-boundary çözümünü geliştirmek.
- 8.8 `ACTIVE / NOT LOCKED`; ikinci lawn/grass calibration turuna topology çözülmeden geçilmez.

## 9 Ağustos 2026 — 8.8 Topology Fix Validation

- Dense semantic surface triangulation boundary contractı düzeltildi.
- Genel çözüm: densified polygon boundary constrained triangulation ile korunuyor; interior grid pointleri triangle subdivision ile ekleniyor; shared-edge point membership tolerance-aware çalışıyor.
- Focused mesher regression: `12 passed in 0.10s`.
- Gerçek Köln textured park diagnostic: önceki `1340 open edge` -> `0 open edge`; problemli park listesi boş.
- Gerçek Köln final scene: `39250 triangles`, `0 open edge`, `268 non-manifold edge`.
- Ownership analizi: `same_mesh_edges=0`, `cross_mesh_edges=268`; hiçbir tekil mesh kendi içinde non-manifold değil.
- Final cross-mesh non-manifold dağılımı: buildings `205`, parks `59`, forest_canopies `4`.
- Park A/B baseline: texture öncesi `58` cross-mesh non-manifold edge, texture sonrası `59`; her iki durumda `same_mesh_edges=0`.
- Source-pair A/B doğrulaması: baseline ve textured tarafta aynı `5` overlap source-pair mevcut; `new textured pairs=set()`, `lost baseline pairs=set()`.
- Sonuç: 8.8 yeni park overlap ilişkisi yaratmıyor; kalan park non-manifold edge sayısı mevcut source overlap geometrisinin densification/triangulation segmentasyonundan etkileniyor.
- 8.8 topology kaynaklı open-edge blocker çözülmüştür; paket henüz görsel acceptance ve kalan regression doğrulamaları tamamlanmadan LOCK edilmez.

- Full regression after topology fix: `3321 passed in 13.12s`.
- Related 8.8 regression: `77 passed in 0.28s`.
- Topology fix tüm engine regresyonunu bozmadan doğrulandı.
- Sıradaki iş: topology-fix sonrası gerçek Köln calibrated preview/STL çıktısını yeniden üretmek ve görsel acceptance için ikinci lawn/grass calibration turunu değerlendirmek.

## 9 Ağustos 2026 — 8.8 Dense Surface Long-Edge Refinement

8.8 Semantic Surface Texture Engine kapsamında topology fix sonrasında
üretilen gerçek Köln preview'ında park yüzeylerinde uzun radyal/fan
üçgenleri görsel olarak tespit edildi.

Bu aşamada relief/pitch kalibrasyonuna devam edilmedi. Önce ölçülebilir
geometri problemi izole edildi.

Gerçek Köln textured park edge analizi:

- problemli uzun edge'lerin tamamı interior edge idi;
- dense boundary üzerinde uzun-edge problemi yoktu;
- örnek maksimum interior edge değerleri:
  - `241687376 / lawn`: `11.299 mm`
  - `261884192 / grass`: `8.323 mm`
  - `392792497 / lawn`: `14.888 mm`
- bazı yüzeylerde `2 × feature_pitch_mm` sınırını aşan yüzlerce interior
  edge bulunuyordu.

Kalıcı regresyon testi eklendi:

- `test_semantic_surface_limits_long_interior_edges`

İlk durumda test kırmızıydı.

Genel çözüm:

- constrained boundary triangulation korunuyor;
- shared interior edge'ler deterministic olarak analiz ediliyor;
- `2 × feature_pitch_mm` sınırını aşan shared interior edge'in midpoint'i
  ekleniyor;
- edge'in iki komşu üçgeni atomik olarak bölünüyor;
- işlem uzun interior edge kalmayana kadar devam ediyor;
- refinement sırasında oluşan yeni vertex'ler terrain/pattern sampling
  zincirine dahil ediliyor;
- boundary contract değiştirilmedi.

Focused mesher doğrulaması:

- `13 passed in 1.72s`

Gerçek Köln doğrulaması:

- city terrain/scene triangle count: `43122`
- tüm textured park yüzeylerinde `> 2 × pitch`: `0`
- tüm textured park yüzeylerinde `> 4 × pitch`: `0`
- ölçülen maksimum lawn edge: yaklaşık `4.798 mm`
- ölçülen maksimum grass edge: yaklaşık `3.592 mm`
- textured park open-edge diagnostic: `0`

Yeni preview üretildi:

- city triangles: `43122`
- color preview scene triangles: `49856`
- output:
  `OUTPUT/PREVIEW/koeln_paedagogische_fakultaet_competitor_comparison_v1.png`

8.8 teknik geometri/topoloji blocker'ları çözülmüş durumda.

Ancak en son `49856` triangle preview için nihai görsel acceptance henüz
yapılmadı. Bu nedenle 8.8 bu devir kaydında LOCK olarak işaretlenmedi.

---

## 9 Ağustos 2026 — 8.9 Morphology-Aware Terrain Product Resolver

Roadmap 8.9 için yeni resolver eklendi:

- `CORE/atlas_morphology_aware_terrain_product_resolver.py`
- `Test/test_morphology_aware_terrain_product_resolver.py`

Resolver mevcut terrain pipeline'ını terrain truth kaynağı olarak korur.

Kaynak elevation verisini değiştirmez.

Desteklenen morphology sınıfları:

- `dense_urban`
- `historic_core`
- `suburban`
- `rural`
- `mountain`
- `landscape_nature`

Deterministic product-facing profile şu kararları taşır:

- `terrain_emphasis`
- `vertical_compression`
- `source_elevation_range_m`
- `source_elevation_modified=False`
- `product_size_mm`
- `urban_density`
- `urban_density_pressure`
- `landmark_present`
- `semantic_content_priority`
- `physical_relief_range_mm`
- `minimum_printable_relief_mm`
- `maximum_printable_relief_mm`
- `resolved_physical_relief_mm`
- `relative_physical_relief`
- `printability_adjustment`

Printability davranışı:

- fiziksel relief minimum printable değerin altındaysa
  `raised_to_minimum`;
- maksimum printable değerin üstündeyse
  `limited_to_maximum`;
- aralıktaysa `none`.

Product-relative relief:

- `resolved_physical_relief_mm / product_size_mm`

Dense urban roadmap contract'ı:

- terrain emphasis: `secondary`
- vertical compression: `strong`

Diğer morphology sınıflarında roadmap'te açıkça verilmeyen sayısal veya
compression katsayıları tahmin edilmedi.

Resolver focused doğrulaması:

- `13 passed in 0.02s`

Terrain pipeline entegrasyonu eklendi:

- `CORE/atlas_terrain_pipeline.py`
- `Test/test_terrain_pipeline_morphology_product_resolver.py`

Pipeline entegrasyonu:

- 8.9 parametreleri verilmezse legacy terrain davranışı değişmez;
- `delta_height_m` mevcut terrain metadata/grid truth üzerinden alınır;
- fiziksel terrain relief:
  `delta_height_m / z_scale * 1000`
  olarak hesaplanır;
- resolver sonucu
  `metadata["terrain_product_profile"]`
  altında taşınır;
- terrain grid değiştirilmez;
- `delta_height_m` değiştirilmez;
- mevcut `z_scale` değiştirilmez.

Resolver + pipeline focused doğrulaması:

- `16 passed in 0.06s`

8.8 + 8.9 ve ilgili terrain regresyonu:

- `102 passed in 2.11s`

Son tam ATLAS regresyonu:

- `3338 passed in 15.03s`

8.9 resolver ve terrain-pipeline entegrasyonu teknik olarak yeşildir.

Sonraki güvenli işlem:

1. scoped `git status` ve `git diff` ile yalnız 8.8/8.9 değişikliklerini
   sınıflandır;
2. unrelated devir/arşiv dosyalarını stage etme;
3. 8.8'in son preview görsel acceptance durumunu LOCK kararından ayrı tut;
4. uygun değişiklikleri explicit olarak stage et;
5. commit;
6. `origin/main` push;
7. push sonrası `HEAD == origin/main` ve çalışma ağacı durumunu doğrula.


## 9 Ağustos 2026 — 8.9 Terrain Sampling / Presentation Devir Güncellemesi

Aktif roadmap paketi:

**8.9 Morphology-Aware Terrain Product Resolver**

8.9 önceki resolver/pipeline aşamasının ötesinde gerçek terrain product
presentation audit ile genişletildi.

Doğrulanmış bulgular:

1. Canonical FoundationSampler normal terrain'de bilinear interpolation kullanır.
2. Eski 25 x 25 physical terrain triangulation canonical truth ile birebir aynı
   yüzey değildir.
3. Köln 25 x 25 truth/mesh maksimum Z farkı `0.486493 mm` ölçüldü.
4. 97 x 97 canonical presentation referansında maksimum fark `0.030406 mm`
   seviyesine düştü.
5. Köln local SRTM kullanmaz; `N50E006.hgt` mevcut değildir.
6. Köln production terrain OpenTopography COP30 fallback üzerinden gelir.
7. OpenTopography provider nearest-neighbor raster sampling kullanıyordu.
8. Provider test-first bilinear interpolation'a geçirildi.
9. `terrain_grid_size` FoundationFirst production API'sine eklendi;
   default `25` korunur.
10. `terrain_grid_size=97` gerçek FoundationFirst → TerrainPipeline zincirinde
    propagate edildi ve test edildi.
11. Gerçek Köln 97 x 97 full-city üretimi başarılı:
    - city STL: `74762` triangle
    - preview scene: `81404` triangle
12. Bambu Studio incelemesinde terrain continuity belirgin biçimde iyileşti;
    şehir/foundation ilişkisi sağlam kaldı.

Focused doğrulamalar:

- SRTM provider: `2 passed`
- OpenTopography provider: `1 passed`
- FoundationFirst terrain-grid integration: `4 passed`

Henüz yapılmayanlar:

- related regression
- full ATLAS regression
- scoped commit / push
- 8.9 final LOCK

Kalan ana teknik problem:

- source DEM raster karakterinden kalan product-facing terrain
  banding/faceting

Sıradaki tek geliştirme:

**Presentation-Surface Regularization**

Sözleşme:

- canonical terrain truth korunacak
- foundation Z truth korunacak
- source DEM elevation değiştirilmeyecek
- arbitrary terrain feature icat edilmeyecek
- large-scale morphology korunacak
- visible product surface deterministic biçimde regularize edilecek
- test-first ilerlenilecek

8.9 bu paket tamamlanıp related/full regression ve görsel acceptance
alınmadan LOCK değildir.

8.10 Water & Shoreline Composition Engine henüz başlanmayacaktır.

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

## 8.20 Sonrası Aktif Çalışma — Road Boundary Clipping

8.20 tamamlandıktan sonra Erkelenz / Reeser Straße 17 yakın-plan fiziksel ürün testi sırasında yeni bir production bug bulundu.

Son güvenli ve push edilmiş baseline:

- Commit: `c7771ca5368f275280fecbdf2a70fab7029c3087`
- Commit mesajı: `Lock multi-morphology acceptance benchmarks`
- Full regression: `3645 passed`

### Aktif ve henüz commit edilmemiş çalışma

Tracked değişiklikler:

- `CORE/atlas_foundation_first_engine.py`
- `CORE/atlas_road_foundation_builder.py`
- `Test/test_road_foundation_builder_urban_hierarchy.py`

Problem:

Gerçek source veride bulunan yollar, ürün sınırını kesen road polyline geometrileri nedeniyle küçük ölçekli sahnede final STL'den kaybolabiliyordu.

Genel çözüm:

- road centerline geometrisi extrusion öncesinde gerçek product bounds'a clip ediliyor;
- FoundationFirst gerçek product bounds bilgisini road builder'a iletiyor;
- çözüm lokasyona veya belirli OSM ID'lerine özel değildir.

Test-first doğrulama:

- yeni crossing-road regresyon testi RED → GREEN
- road-related regression: `13 passed in 0.30s`

Gerçek Erkelenz fresh production doğrulaması:

- road meshes: `2`
- her iki road mesh:
  - `valid=True`
  - `open_edge_count=0`
  - `non_manifold_edge_count=0`

### Yakın-plan fiziksel ürün bulgusu

Road bug fix'inden ayrı olarak, yaklaşık `1:496` gibi yakın ölçeklerde mevcut semantic vegetation / park / forest-canopy geometrisinin premium fiziksel görünüm için yetersiz kaldığı gözlendi.

Özellikle mevcut forest-canopy hattı fiziksel olarak gerçek canopy/ağaç hacmi değil, terrain-following ince semantic surface üretmektedir.

Bu ikinci konu henüz çözülmemiştir ve ayrı bir sonraki production-readability problemi olarak ele alınmalıdır.

### Çalışma ağacı notu

Aşağıdaki untracked dosyalar bu aktif çalışmayla ilgili değildir ve dokunulmamalıdır:

- `Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-08-01.md`
- `Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-08-04.md`
- `Test/preview_church_semantic_surfaces.py`

Yeni pencere açıldığında `c7771ca` son güvenli baseline kabul edilmeli; yukarıdaki üç tracked road-clipping değişikliği silinmemeli veya resetlenmemelidir.

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

### Aktif sonraki adım

WorldCover vegetation milestone commit/push edilmiştir ve STL topology
doğrulaması tamamlanmıştır.

Aktif iş Jamaica sahnesinin kalan fiziksel ürün doğrulamasıdır.

Jamaica tamamlanmadan Seychelles veya başka lokasyona geçilmeyecektir.

---

## 12 Ağustos 2026 — Jamaica Physical Production Benchmark / HOLD

### Güncel güvenli checkpoint

Son doğrulanmış ve push edilmiş güvenli checkpoint:

- commit: `9efa03c`
- message: `Update Jamaica production checkpoint docs`
- branch: `main`
- `HEAD == origin/main == 9efa03c`

Bu checkpoint sonrasında Jamaica Wall Collection / wedding-rings çalışması
çalışma ağacında devam etmiştir.

Henüz commit/full-regression ile kilitlenmemiş aktif dosyalar korunmalıdır;
broad reset/restore uygulanmamalıdır.

### Jamaica Wall Collection ürün kontratı

Ürün:

- location: Jamaica / Mavis Bank / Blue Mountains
- center: `18.0314032, -76.6583705`
- outer size: `170 × 170 mm`
- city/map area: `150 × 150 mm`
- scale: `1:5000`

Label:

- primary: `JAMAICA`
- secondary: `MAVIS BANK / BLUE MOUNTAINS`
- kişisel ikon: interlocking wedding rings

Fiziksel palette:

- Black: frame + roads/hardscape + label text/icon
- Desert Tan: terrain + building walls + label plate
- Brick Red: roofs
- Dark Green: parks + trees + vegetation
- Blue: water; bu Jamaica sahnesinde kullanılmıyor

### Bambu Studio / AMS doğrulaması

Dört hizalı multicolor STL tek multi-part object olarak Bambu Studio'ya
yüklenmiştir.

AMS eşlemesi:

- A1: Black — PLA Basic
- A2: Desert Tan — PLA Matte
- A3: Brick Red — PLA Matte
- A4: Dark Green — PLA Matte

Prime Tower plaka içine alınmış ve plate-boundary hatası giderilmiştir.

Purging volumes Bambu Studio tarafından yeniden hesaplanmış,
karşılaştırma slice'ında multiplier `0.60` kullanılmıştır.

### Gerçek fiziksel production benchmarkı

Son temiz slice sonucu:

- product/model mass: `210.53 g`
- purge mass: `142.04 g`
- prime tower mass: `44.18 g`
- total filament mass: `396.75 g`
- product dışı filament: `186.22 g`
- product dışı oran: yaklaşık `%47`
- filament changes: `616`
- estimated print time: `19 h 53 min`
- purge multiplier: `0.60`

Bu slice fiziksel baskı için kabul edilmemiştir.

Jamaica ilk fiziksel baskısı şu anda:

`HOLD`

durumundadır.

### Ana production dersi

Closed/manifold geometri ve semantik olarak doğru multicolor STL ayrımı
tek başına `PRODUCTION_READY` anlamına gelmez.

Jamaica gerçek AMS slice'ı şunu ortaya koymuştur:

- aynı Z katmanlarında birçok semantic color bulunması çok yüksek
  filament-change sayısı üretir;
- `616` change, purge ve prime-tower maliyetini fiziksel ürün açısından
  kabul edilemez seviyeye çıkarmıştır;
- purge multiplier azaltılması yalnız ikincil optimizasyondur;
- ana çözüm color/layer architecture ve multicolor export stratejisidir.

Bundan sonra fiziksel ürün acceptance değerlendirmesinde zorunlu metrikler:

- filament-change count
- purge mass
- prime-tower mass
- product mass
- total filament mass
- estimated print time

Bu metrikler STL topology ve semantic correctness kadar önemli production
gate girdileri olarak ele alınacaktır.

### Jamaica / Mavis Bank ürününün statüsü

Mevcut Jamaica / Mavis Bank / Blue Mountains ürünü:

- silinmeyecektir;
- başarısız çalışma olarak sınıflandırılmayacaktır;
- ilk gerçek AMS production-cost benchmarkı olarak korunacaktır;
- multicolor optimization regression/reference sahnesi olacaktır.

Bu ürün sayesinde gerçek fiziksel üretimde daha önce dijital doğrulamalarda
görünmeyen filament-change maliyeti keşfedilmiştir.

### Park edilen Jamaica Island Relief fikri

Ayrı bir ürün yönü olarak park edilmiştir:

`Jamaica Island Relief`

Hedef:

- `170 × 170 mm` bütün Jamaica adası
- gerçek ada silueti
- ada ölçekli topoğrafya
- Blue Mountains relief
- büyük vegetation/natural regions
- Mavis Bank / honeymoon kişisel işareti
- frame + `JAMAICA` label

Amaç mevcut Mavis Bank şehir detayını bütün adaya ölçeklemek değildir.

Ada ölçekli ürünün avantajı daha geniş ve daha az parçalanmış renk bölgeleri
ile çok daha düşük filament-change ihtimali sağlamasıdır.

Bu fikir Jamaica Mavis Bank benchmarkını silmez veya yerine geçmez;
ayrı ürün yaklaşımı olarak park edilmiştir.

### Moladan sonraki kesin devam

Mevcut `616` değişimli slice basılmayacaktır.

Devam sırası:

1. Bambu Studio layer preview üzerinden color-change yoğun Z aralıklarını ölç.
2. `616` değişimi oluşturan semantic mesh kombinasyonlarını belirle.
3. Terrain / roads / buildings / roofs / vegetation / label renk mimarisini
   fiziksel görünümü bozmadan optimize et.
4. Gerekirse multicolor STL export stratejisini layer-aware hale getir.
5. Yeni STL setini üret.
6. Bambu Studio'da yeniden slice et.
7. Yeni sonucu aşağıdaki benchmarka karşılaştır:
   - `210.53 g` product
   - `142.04 g` purge
   - `44.18 g` prime tower
   - `396.75 g` total
   - `616` changes
   - `19 h 53 min`
8. Atık ve filament-change sayısı kabul edilebilir seviyeye inmeden
   Jamaica fiziksel baskısını başlatma.

Seychelles veya diğer sahnelere geçerken bu production dersi
tekrarlanmayacaktır.

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

## Physical Production Devir Checkpoint — 14 Ağustos 2026

Bu kayıt, yukarıdaki Jamaica Island Relief'in `parked` olarak tanımlandığı
eski durumu ve Eschersheim label'ın `pending` olduğu checkpoint'i güncel
fiziksel production durumu açısından supersede eder. Eski kayıtlar tarihsel
bağlam olarak korunur.

### 1. Jamaica Premium Island Relief V1

Whole-island Jamaica relief yaklaşımı başarıyla gerçek production package
seviyesine çıkarıldı.

Final/current physical geometry:

- outer: `170 × 170 mm`
- opening: `150 × 150 mm`
- frame width: `10 mm`
- island width: `140.000 mm`
- island height: `55.189 mm`
- island relief Z: `1.600 .. 9.788 mm`
- top terrain triangles: `33,360`
- total island triangles: `68,444`

Terrain generation reference:

- terrain sample points: `17,196`
- Delaunay top triangles: `33,429`
- rejected outside triangles: `937`
- terrain components: `9`
- removed disconnected artifacts: `69`

Aligned multicolor files:

- `OUTPUT/JAMAICA/jamaica_premium_island_v1_multicolor/JAMAICA_FRAME_BLACK.stl`
- `OUTPUT/JAMAICA/jamaica_premium_island_v1_multicolor/JAMAICA_SEA_BLUE.stl`
- `OUTPUT/JAMAICA/jamaica_premium_island_v1_multicolor/JAMAICA_ISLAND_GREEN.stl`
- `OUTPUT/JAMAICA/jamaica_premium_island_v1_multicolor/JAMAICA_LABEL_PLATE_WHITE.stl`
- `OUTPUT/JAMAICA/jamaica_premium_island_v1_multicolor/JAMAICA_LABEL_TEXT_RINGS_BLACK.stl`

Combined product:

- `OUTPUT/JAMAICA/jamaica_premium_island_v1_WALL_COLLECTION_170mm.stl`

Label content:

- primary: `JAMAICA`
- secondary: `BLUE MOUNTAINS · MAVIS BANK`
- symbol: interlocking wedding rings

Wedding-rings support was added through the generic label architecture rather
than a Jamaica-only geometry hack.

Relevant active code includes:

- `CORE/atlas_label_text_spec.py`
- `CORE/atlas_label_wedding_rings_mesher.py`
- `CORE/atlas_wall_collection_product_builder.py`
- corresponding tests

Bambu Studio production slice:

- total time: approximately `2 h 54 min`
- total filament: approximately `88.62 g`
- filament changes: `40`

Bu yeni island architecture önceki city-based Jamaica benchmarkındaki:

- `616` filament changes
- `210.53 g` product
- `142.04 g` purge
- `44.18 g` prime tower
- `396.75 g` total
- `19 h 53 min`

sonucuna karşı production-cost breakthrough olarak kabul edilir.

Eski `616`-change Jamaica ürünü silinmeyecek; multicolor optimization
benchmark/reference olarak korunacaktır.

Jamaica final/current Bambu Studio project'i `.3mf` olarak kaydedilmiştir.

### 2. Niedwiesenstraße 99 physical scene

Ana fiziksel scene baskısı tamamlandı.

Final scene üzerinde ayrıca:

- wide river insert ayrı üretildi
- `NIEDWIESENSTRASSE_99_RIVER_INSERT_WIDE.stl`
- buffer: yaklaşık `0.80 mm` each side
- thickness: yaklaşık `1.040 mm`
- X span: yaklaşık `128.608 mm`
- Y span: yaklaşık `120.699 mm`
- triangles: `224`
- river insert basıldı ve sahneye fiziksel olarak eklendi

Bu insert mevcut basılmış ürünü yeniden basmadan water layer'ı fiziksel olarak
tamamlama yönteminin ilk pratik örneğidir.

### 3. Premium gift box physical validation

Niedwiesenstraße gift-box lid basıldı.

Label:

- `NIEDWIESENSTRASSE 99`
- `ESCHERSHEIM · FRANKFURT AM MAIN`

Lid üzerindeki geniş beyaz flat top surface fiziksel olarak incelendi.
Yazı geometrisi başarılı olmasına rağmen geniş top-surface üzerinde belirgin
çizgisel / ipliksi yüzey dokusu görüldü. Bu yüzey premium standardı olarak
kabul edilmedi.

Gift-box base:

- file:
  `OUTPUT/STL/eschersheim_niedwiesenstrasse_99_premium_gift_box_v1/eschersheim_niedwiesenstrasse_99_220mm_PREMIUM_GIFT_BOX_V1_BASE.stl`
- physical size yaklaşık `226.8 × 226.8 mm`
- baskıya gönderildi

Calibration denemelerinin temel sonucu:

- `15% -> 10%` infill değişimi süreyi anlamlı azaltmadı
- ironing geniş yüzeyde yaklaşık üç saat ek maliyet oluşturdu
- ironing production için kapatıldı

Baskıya gönderilen son yön:

- layer height: `0.24 mm`
- sparse infill: `10%`
- top shell layers: `6`
- ironing: `No ironing`
- last slice: approximately `2 h 52 min`
- material: approximately `172.21 g`

Base fiziksel yüzey kalitesi baskı tamamlandıktan sonra değerlendirilecek.

### 4. Niedwiesenstraße next exact physical task

Sahnedeki ana görsel eksik artık vegetation / trees'dir.

Moladan sonraki kesin iş:

`separately printable Niedwiesenstraße tree / vegetation insert package`

Amaç:

- mevcut fiziksel sahneyi yeniden basmamak
- mevcut ATLAS canonical tree geometrisini mümkün olduğunca kullanmak
- yeşil filamentle ayrı tree insertler üretmek
- yapıştırılabilir / fiziksel yerleşime uygun taban sağlamak
- aynı boyda mekanik tekrar yerine birkaç küçük boy varyasyonu kullanmak
- doğal kümelenme / tree-row mantığını korumak

Motorun başlangıçta neden tree üretmediğinin araştırılması bu fiziksel
tamamlama işinin ön koşulu değildir.

### 5. Korunacak aktif working tree

Jamaica / wedding-rings ve ilgili preview/test çalışmaları commit edilmeden
önce korunacaktır.

Özellikle mevcut aktif/untracked çalışmalar toplu `reset`, `restore`,
`clean` veya `git add .` işlemine dahil edilmemelidir.

Bilinen aktif alanlar:

- `CORE/atlas_label_text_spec.py`
- `CORE/atlas_product_color_preview_renderer.py`
- `CORE/atlas_wall_collection_product_builder.py`
- `CORE/atlas_label_wedding_rings_mesher.py`
- `Test/test_label_text_spec.py`
- `Test/test_product_color_preview_renderer.py`
- `Test/test_wall_collection_product_builder.py`
- `Test/test_label_wedding_rings_mesher.py`
- `Test/preview_jamaica_mavis_bank_blue_mountains_wall_collection.py`
- `Test/preview_jamaica_premium_island_relief_v1.py`
- `Test/preview_jamaica_premium_island_v1.py`
- `Data/OSM/`

Moladan sonra önce `git status --short --branch` ile gerçek working tree
yeniden doğrulanmalıdır.


### 6. Gift Box BASE physical validation result — PASS

Niedwiesenstraße Premium Gift Box V1 BASE baskısı fiziksel olarak tamamlandı.

Baskı sonrası gözlem:

- geniş iç taban yüzeyi belirgin biçimde pürüzsüz ve homojen çıktı
- önceki lid baskısındaki çizgisel / ipliksi geniş yüzey problemi oluşmadı
- köşelerde kalkma gözlenmedi
- duvar ve taban geometrisi genel olarak stabil
- sağ uzun kenarda hafif inward bow / içe kaçma mevcut
- bu inward bow elle hissedilebiliyor ancak baskıyı reddedecek seviyede değil

Bu sonuç ironing'in gerekli olmadığını fiziksel olarak doğrulamıştır.

Validated production settings:

- nozzle: `0.4 mm`
- layer height: `0.24 mm`
- sparse infill: `10%`
- top shell layers: `6`
- ironing: `No ironing`

Physical decision:

`Premium Gift Box V1 BASE = PASS`

Bu kombinasyon bundan sonra büyük düz Gift Box yüzeyleri için referans
production setting olarak kullanılacaktır.

Önceki lid baskısının geniş beyaz top-surface kalitesi production standardı
olarak kabul edilmez. Lid yeniden basılacaksa BASE ile doğrulanan aynı ayar
kombinasyonu kullanılmalıdır.

Takip edilmesi gereken tolerans konusu:

`long-wall slight inward bow`

Bu sapma sonraki box component baskılarında karşılaştırılacak; artış gösterirse
geometry / cooling / wall-thickness kaynakları ayrıca incelenecektir.


---

## Physical Tree V1 Devir Checkpoint — 14 Ağustos 2026

### Problem

ATLAS preview'de ağaçları gösterebiliyor fakat fiziksel baskıda ağaçlar
kırıntı / çok ince çıkıntı gibi görünüyordu.

Gerçek Niedwiesenstraße probe sonucu:

- tree meshes: `721`
- source: `worldcover`
- each tree: `240` triangles
- old physical height: `2.150 mm`
- old crown footprint: yaklaşık `1.55 × 1.55 mm`

Bu doğrulama tree üretiminin çalıştığını, fakat physical dimension contract'ın
yetersiz olduğunu kanıtladı.

### Physical Tree V1 canonical geometry

Old:

- trunk height: `0.80 mm`
- trunk diameter: `0.45 mm`
- crown height: `1.35 mm`
- crown diameter: `1.55 mm`
- total height: `2.15 mm`

New:

- trunk height: `2.000 mm`
- trunk diameter: `1.125 mm`
- crown height: `3.375 mm`
- crown diameter: `3.875 mm`
- total height: `5.375 mm`

Canonical mesh topology remained closed/manifold.

### WorldCover spacing calibration

Old:

`WORLDCOVER_TREE_MIN_PHYSICAL_SPACING_MM = 4.0`

New:

`WORLDCOVER_TREE_MIN_PHYSICAL_SPACING_MM = 6.0`

At `1:3000`, this corresponds to approximately `18 m` minimum source spacing.

Real Niedwiesenstraße result:

- before 6 mm spacing: `703` Physical V1 trees
- after 6 mm spacing: `349` trees

This reduced excessive visual density without shrinking tree geometry.

### Deterministic natural size variation

WorldCover trees now receive deterministic physical scale variants:

- `0.95×`
- `1.00×`
- `1.05×`

Non-WorldCover trees remain `1.00×`.

All variants preserve Physical V1 minimum print dimensions.

Real scene distribution:

- `0.95×`: `118`
- `1.00×`: `112`
- `1.05×`: `119`

### Final visual candidate

File:

`OUTPUT/CALIBRATION/niedwiesenstrasse_99_TREE_PHYSICAL_V1_SPACING_6MM_VARIANTS.stl`

Metrics:

- trees: `349`
- triangles: `83,760`
- open edges: `0`
- non-manifold edges: `0`

Bambu Studio visual inspection:

`PASS`

The result no longer resembles fragmented / micro tree artifacts. Tree trunks
and crowns are physically readable, overall density is acceptable, and mild
size variation reduces mechanical repetition.

### Regression

Focused combined tree regression:

`61 passed`

Full ATLAS regression:

`3689 passed in 16.37s`

### Files in this milestone

CORE:

- `CORE/atlas_tree_foundation_builder.py`
- `CORE/atlas_foundation_first_engine.py`

Tests:

- `Test/test_tree_foundation_builder.py`
- `Test/test_foundation_first_engine_tree_water_filter.py`
- `Test/test_tree_row_spacing_resolver.py`
- `Test/test_tree_row_resolver.py`

### Working-tree protection

Jamaica / wedding-rings active work remains intentionally separate and must not
be included in the Physical Tree V1 commit.


---

## Bonn Birthplace Physical Production Handoff — 14 August 2026

Status: `PRINTING`.

- product/opening/scale: `170 × 170 mm` / `150 × 150 mm` / `1:3000`
- label/icon: `BONN / GEBURTSORT` / baby stroller
- water intentionally absent
- package: `OUTPUT/STL/BONN_BIRTHPLACE_PRODUCTION_V1/`
- files: `__black`, `__white`, `__desert_tan`, `__brick_red`, `__dark_green`; all `0` open / `0` non-manifold

Added behavior: closed-building fallback, same-material wall/roof preservation, separate `landmark_roofs`, projected landmark overlap filtering, park topology cleanup, physical RGB filename resolution, Bonn profile and baby-stroller symbol.

Automatic roof metadata did not cover every desired visible Münster roof. Desired church/tower roofs were painted Brick Red in Bambu Studio after incorrect red parts were reassigned to Desert Tan. This is stored in `bonn_muensterplatz_170mm_BIRTHPLACE_PRODUCTION_V1.3mf` and is product-local; automatic roof classification is not fully solved. Do not reuse older Bonn COLORGROUP/FINAL projects.

Physical gate: model `121.46 g`; purge `45.64 g`; tower `15.15 g`; total `182.25 g`; `193` changes; `9 h 31 min`. Mapping: A1 Black, A2 White, A3 Desert Tan, A4 Dark Green, External Brick Red. External red requires manual switching.

Permanent rule: preview/colorgroup appearance is not proof of physical color volume. Require closed/manifold solids or slicer-verified volumetric assignment, object/material inspection, plausible gram distribution and purge/prime/change/time review.

Validation: `109 passed`; full `3704 passed in 16.54s`.

Working-tree protection: Jamaica/Seychelles previews and `Data/OSM/` remain outside this Bonn milestone. No broad stage/reset/restore/clean.

---

## Seychellen Premium Archipelago Physical Handoff — 15 August 2026

Status: `PRINT QUEUE`.

- product/opening: `170 × 170 mm` / `150 × 150 mm`
- island span: `140.000 × 99.808 mm`
- relief: `1.600 .. 10.683 mm`
- German label: `SEYCHELLEN / SILBERHOCHZEIT · 25 JAHRE`
- symbol intentionally absent
- palette: Black frame/text, White plate, Dark Green islands, Blue sea
- five aligned STL parts / four physical colors
- all parts: `0` open / `0` non-manifold

Topology correction: preserve all disconnected islands, but separate two
components touching at only one XY vertex by `0.0001 mm`. This removes
four-owner vertical edges while remaining visually and dimensionally
imperceptible.

Bambu physical gate: model `73.03 g`; purge `9.98 g`; tower `3.31 g`;
total `86.32 g`; `40` changes; `2 h 32 min`. Model mass: Black `22.21 g`,
White `1.49 g`, Dark Green `1.72 g`, Blue `47.61 g`.

Saved project:
`seychelles_premium_archipelago_170mm_PRODUCTION_V1.3mf`.

The project is ready but the printer is occupied. Do not regenerate or change
the accepted label, topology or palette unless physical printing exposes a
real defect.

Working-tree protection: Jamaica previews and `Data/OSM/` remain separate.
Do not broad-stage, reset, restore or clean them.

---

## Modular Gift Box, Personalization & Physical Tree V2 Handoff — 15 August 2026

### Gift box

- standards: Mini `120`, Original `170`, Grande `220 mm`
- middle capacities: `25 / 50 mm`
- connector system: base male; middle female/male; lid female
- personalized removable plates:
  `80 × 24`, `110 × 28`, `140 × 32 mm`
- real centered lid recess: `0.8 mm`
- plate: `1.2 mm`; fit: `0.20 mm/side`; text: `0.6 mm`; max two lines
- universal corner-support masters: `25 / 50 mm`, four per level
- all physical parts passed closed/manifold gates

### Physical Tree V2

Physical handling feedback supersedes the V1 attachment contract. Preserve the
accepted crown form and organic distribution, but use:

- canonical trunk `1.50 mm`
- root collar `2.20 mm` diameter, `0.80 mm` height
- terrain embed `0.60 mm`
- smallest scale variant trunk `1.425 mm`
- visible total height remains `5.375 mm`

The root collar, trunk and crown form one connected closed mesh.
Topology: `0` open / `0` non-manifold.

Validation: tree package `76 passed`; full `3764 passed in 16.70s`.

Seychellen is now `PRINTING` with A1 Black, A2 White, A3 Blue and A4 Dark
Green.

Working-tree protection remains mandatory: do not include `Data/OSM/` or the
three Jamaica preview scripts in this milestone. No broad stage/reset/restore/
clean.


---

## Köln Graduation Production V2 Handoff — 15 August 2026

Status: `PRINT QUEUE`, behind Seychellen.

- outer/opening/scale: `170 / 150 mm / 1:3000`
- label/icon:
  `UNIVERSITÄT ZU KÖLN / PÄDAGOGISCHE FAKULTÄT` / graduation cap
- verified focus: Gebäude `216`, Gronewaldstraße 2,
  OSM source `125014714`
- Black: frame/text/cap
- White: terrain/roads/buildings/plate
- Brick Red: Bambu-painted Gebäude 216 roof only
- Dark Green: parks/Physical Tree V2
- Blue: water
- generated five STL parts all `0` open / `0` non-manifold

The automatically generated `46`-triangle Brick Red part was invisible in the
assembled product and was deleted from the Bambu project. The verified Gebäude
216 roof was painted in Bambu Studio; walls remained White. Removing the
redundant part reduced the slice from `89` to `88` changes and from `6 h 20 min`
to `6 h 19 min`.

Final physical gate:

- model `100.77 g`; purge `22.90 g`; tower `6.67 g`;
  total `130.33 g`
- `88` changes; `6 h 19 min`
- Black `22.24 g`; White `71.75 g`; Brick Red `0.16 g`;
  Dark Green approximately `6.37 g`; Blue approximately `0.25 g`

Project:

`OUTPUT/STL/koeln_paedagogische_fakultaet_multicolor_170mm_PRODUCTION_V2/koeln_paedagogische_fakultaet_170mm_GRADUATION_PRODUCTION_V2.3mf`

Validation: focused `25 passed`; related `82 passed`; full `3767 passed in 16.96s`.

Do not enable support for the Black floating-cantilever warning. Layer
inspection proves that the Black label text/cap is supported by the continuous
White label plate.

Parked next engine capability: a generic layer-aware physical material/change
optimizer. It must report per-layer material demand, transition-causing
geometry, redundant/occluded parts and purge/prime-tower cost, then propose
safe reductions without silently changing visible semantic colors.

Working-tree protection remains mandatory: do not include `Data/OSM/` or the
three Jamaica preview scripts. No broad stage/reset/restore/clean.

---

## Meckenheim Jungholzweg 2/3 Production V2 Handoff — 15 August 2026

Status: `BAMBU PROJECT READY`; slicing pending.

- outer/opening/scale: `170 / 150 mm / 1:3000`
- label/icon: `JUNGHOLZWEG 2/3 / MECKENHEIM` / home
- verified targets:
  - OSM `220593156`: Jungholzweg 2/2a/2b
  - OSM `389176145`: Jungholzweg 3
- Apple Maps comparison confirmed the first target within `7.64 m`
- Black frame/text/icon
- White terrain/roads/plate
- Desert Tan generic buildings/roofs
- Brick Red only the two verified target roofs
- Dark Green parks/Physical Tree V2
- no real scene water; no Blue output

The renderer now supports opt-in roof-only highlighted-building separation.
Default same-material closed-solid preservation remains unchanged. Meckenheim
forces closed wall/roof color solids only for the two verified target IDs;
there is no manual or location-specific geometry hack.

Five aligned STLs:

- Black `1848`, White `5832`, Brick Red `20`,
  Desert Tan `10150`, Dark Green `19952` triangles
- every file: `0` open / `0` non-manifold

Project:

`OUTPUT/STL/meckenheim_jungholzweg_2_3_multicolor_170mm_PRODUCTION_V2/meckenheim_jungholzweg_2_3_170mm_HOME_PRODUCTION_V2.3mf`

Validation: related `71 passed`; full `3772 passed in 16.90s`.

Mandatory next production sequence:

1. finish the current Köln print;
2. update P2S firmware;
3. update Bambu Studio;
4. reopen and slice the saved Meckenheim project;
5. inspect object/material mapping, model/purge/tower grams, changes and time;
6. print only after the physical gate passes.

Working-tree protection remains mandatory: do not include `Data/OSM/` or the
three Jamaica preview scripts. No broad stage/reset/restore/clean.
---

## Semantic Relief, Figurative & Kit System V1 — Master Execution Compass

Status: RED CONTRACT

Bu bölüm, ATLAS 2.5D rölyef sisteminin uzun vadeli geliştirme pusulasıdır. Gelecek motor bu belgeyi `Docs/START_HERE.md` ve `Docs/STATUS/CURRENT_STATUS.md` ile birlikte okumadan geliştirmeye başlamamalıdır.

### 1. Program amacı

Program üç ticari yeteneği aynı semantik geometri omurgasında birleştirecektir:

1. Tarihi ve önemli yapılar için mimari 2.5D rölyef: oyma, kakma, heykelcik, figür, yazıt, kemer, pencere, kapı, kubbe, friz, korniş ve cephe süslemeleri.
2. Kişiye özel anlatı rölyefi: kimliği korunan portre veya karikatür, beden pozu, meslek ya da hobi ve sahne aksesuarları. İlk örnek profesör, olta ve balık kovası sahnesidir.
3. Ortak parça kataloğu ve demonte maket sistemi: aynı kemer, pencere, kapı, kubbe, tuğla, kiremit ve süsleme parçaları assembled landmark, facade relief ve construction kit çıktılarında yeniden kullanılabilmelidir.

Hedef yalnız bir fotoğrafı height-map olarak kabartmak değildir. Hedef; nesneleri, parçaları, derinlik ilişkilerini, hedef yüzeyi, fiziksel baskı sınırlarını ve ürün biçimini anlayan semantik bir üretim sistemidir.

### 2. Değişmez mühendislik kuralları

- Test-first: RED contract, minimal implementation, focused test, related regression, full regression.
- Provider algılar ve tanımlar; ATLAS CORE geometriyi, fiziksel kararı ve kalite kapısını üretir.
- Görsel preview tek başına üretim kanıtı değildir.
- Her fiziksel parça closed ve manifold olmalıdır.
- Semantik kimlik, fiziksel malzeme kimliği ve ticari çıktı rolü ayrı tutulmalıdır.
- Görünür anlamlı renkler otomatik olarak birleştirilemez veya değiştirilemez.
- Landmark özel hard-code ancak doğrulanmış katalog verisi olarak bulunabilir; genel motor davranışı yerine kullanılamaz.
- Her faz tek başına geri alınabilir olmalıdır.
- Korunan unrelated dosyalar stage, reset, restore veya clean işlemlerine dahil edilemez.
- `git add .` kullanılmaz; yalnız ilgili dosyalar stage edilir.

### 3. Korunacak mevcut teknik temel

Aşağıdaki mevcut katmanlar silinmeyecek, yeniden yazılmayacak ve yeni semantik omurganın altında yeniden kullanılacaktır:

- image input ve preprocessing;
- multiscale form, detail ve micro-detail ayrıştırması;
- depth composition ve compression;
- subject ve semantic mask sistemi;
- morphology, feathering ve layer separation;
- semantic height ve material düzenleme;
- normal, confidence ve face-region yardımcıları;
- physical relief profile ve sampling plan;
- closed relief mesh builder;
- topology, slope ve print-risk raporları;
- STL ve production-package altyapısı;
- semantic architecture identity modeli;
- facade bay, opening, arch, panel, cornice ve detail üreticileri;
- church facade ve landmark grammar temelleri;
- MediaPipe portrait landmark provider sözleşmeleri.

Bu temel değersiz veya başarısız değildir. Eksik olan height-map matematiğinden önce, bu katmanları doğru semantik sahne kararlarıyla yönetecek üst omurgadır.

### 4. Mevcut mimari boşluk

Mevcut AtlasSemanticArchitectureComponent yalnız identity metadata taşır. Aşağıdaki alanlar henüz canonical değildir:

- kalıcı component ID ve parent component ID;
- kaynak geometrisi ve geometry adapter kimliği;
- local transform, orientation ve fiziksel boyutlar;
- target surface ve projection mode;
- semantic depth band, layer order ve occlusion ilişkisi;
- relief polarity, minimum feature ve exaggeration politikası;
- semantic material role ve fiziksel material role;
- repetition pattern, quantity ve interchangeable-part kimliği;
- assembled landmark, facade relief ve kit output eligibility;
- connector, tolerance ve assembly-interface bilgisi;
- provenance, confidence ve operatör override kaydı.

Mevcut Architectural Relief V1 gerçek anlamda semantik mimari orkestrasyon yapmaz. Architectural kind metadata olarak taşınır; tek normalize height-map düz bir plakaya dönüştürülür. Surface projection, component graph, semantic occlusion ve ortak parça kataloğu eksiktir.

Mevcut production package genel değildir; Dalyan ve 80x50 mm adlandırmalarına bağlı sabitler içerir. Bu katman, mevcut Dalyan paketini bozmadan daha sonra genel relief product manifest sözleşmesine taşınmalıdır.

Figurative sistemde henüz canonical body, pose, gesture, prop, contact, balance ve story-scene graph bulunmaz. Portrait landmark altyapısı vardır; fakat ticari canonical face/head geometry ve identity-preserving fitting hattı tamamlanmamıştır.

Temel eksik akış şudur:

```text
doğrulanmış kaynaklar
→ semantic component graph
→ spatial ve depth composition
→ physical feature resolution
→ geometry adapters
→ surface projection
→ output-mode orchestration
→ topology ve quality gate
→ production package
```

### 5. Portrait karar çelişkisi

Belgelerde çözülmesi gereken iki farklı karar bulunmaktadır:

- Temmuz 2026 devir kaydı, tek fotoğraftan AI-depth ve DSINE ana geometri yolunu appearance-to-geometry leakage nedeniyle dondurmuş; çoklu fotoğraf veya kısa videodan güvenilir 3D face/head reconstruction araştırmasını istemiştir.
- `Docs/DECISIONS.md`, FLAME 2023 Open modelini canonical face geometry olarak seçmiş ve sıradaki paketi AtlasParametricFaceGeometry olarak kaydetmiştir.

Bu çelişki kod yazarak sessizce çözülemez. Phase 8 içinde lisans, gizlilik, Mac uyumu, kimlik koruma, multi-view desteği, aksesuar davranışı ve mesh kalitesi kanıtlarıyla açık bir GO, HOLD veya REJECT kararı verilmelidir. Bu karar verilmeden production portrait geometry geliştirilmeyecektir.

### 6. Ana faz planı — Part A

#### Phase 0 — Audit, karar temizliği ve roadmap kilidi

Yapılacaklar:

- `RELIEF_CURRENT_ARCHITECTURE.md` belgesindeki eski tespitleri güncel kodla karşılaştırmak;
- mevcut relief, architecture, portrait ve production-package public contract envanterini kesinleştirmek;
- tekrar kullanılacak, genelleştirilecek, dondurulacak ve kaldırılmayacak katmanları işaretlemek;
- portrait karar çelişkisini Phase 8 decision gate olarak kilitlemek;
- mevcut full regression baseline sonucunu kaydetmek.

Kabul kapısı:

- üç ana durum belgesi aynı roadmap, aktif faz ve durma noktasını göstermeli;
- unrelated dosyalarda değişiklik olmamalı;
- baseline test sonucu kaydedilmiş olmalı.

#### Phase 1 — Semantic Relief Scene Contract V1

Canonical ve immutable sözleşmeler test-first oluşturulacak:

- `AtlasSemanticReliefComponent`;
- `AtlasSemanticReliefScene`;
- component ID, parent ID ve source reference;
- semantic class ve geometry source kind;
- transform, dimensions ve orientation;
- target surface ve projection mode;
- depth band, layer order ve occlusion policy;
- material role ve physical feature policy;
- repetition, output eligibility ve provenance.

Bu faz mesh üretmeyecek. Yalnız doğrulanmış ve provider-independent sahne sözleşmesi kuracaktır.

Kabul kapısı:

- immutable ve deterministic contract;
- duplicate ID, missing parent, cycle, geçersiz depth order ve geçersiz output mode reddi;
- architecture, portrait, figurative ve kit kullanımlarını temsil eden synthetic fixture;
- mevcut AtlasSemanticArchitectureModel ile geçiş ilişkisi belgelenmiş olmalı.

#### Phase 2 — Geometry Source Adapter Contracts

Semantik component ile geometri kaynağı birbirinden ayrılacaktır. İlk adapter sözleşmeleri:

- height-map relief source;
- existing triangle mesh source;
- parametric primitive source;
- facade grammar source;
- catalog component source;
- future canonical face/head source;
- future body, pose ve prop source.

Provider sonucu doğrudan STL olmayacak. Adapter normalize geometry, local bounds, anchors, confidence, provenance ve supported projection modes döndürecektir.

Kabul kapısı:

- provider ve CORE sorumlulukları ayrı olmalı;
- aynı semantic scene farklı adapter implementation ile çalışabilmeli;
- adapter sonucu deterministic ve inputtan izole olmalı;
- desteklenmeyen projection mode erken ve açık hata vermeli.

### 7. Ana faz planı — Part B

#### Phase 3 — Semantic Depth & Occlusion Composer

Component graph, tek height-map yerine anlamlı derinlik sahnesine dönüştürülecektir.

Yapılacaklar:

- semantic depth band ve local relief range çözümü;
- foreground, middle ground ve background ilişkileri;
- parent-child depth inheritance;
- explicit overlap ve occlusion kuralları;
- contact, embed, recess ve raised-feature politikaları;
- material boundary ile geometry boundary ayrımı;
- deterministik conflict report ve operator override kaydı.

Kabul kapısı:

- melek, kemer, yazıt ve arka duvar gibi üç veya daha fazla katman doğru sıralanmalı;
- çakışan depth band, cycle ve fiziksel olarak imkansız embed reddedilmeli;
- aynı girdi aynı composition planını vermeli;
- composer henüz triangle mesh üretmemeli.

#### Phase 4 — Physical Feature Resolver

Semantik ayrıntılar nozzle, layer height, ürün ölçüsü ve malzemeye göre fiziksel karara dönüştürülecektir.

Her feature için karar:

- preserve;
- enlarge;
- merge;
- simplify;
- convert to engraving;
- omit with report;
- require operator review.

Ölçülecek unsurlar:

- minimum raised width ve height;
- minimum groove width ve depth;
- unsupported projection ve slope;
- fragile neck, limb, wing ve ornament bağlantısı;
- adjacent-feature spacing;
- repeated-detail density;
- semantic importance ve readability priority.

Kabul kapısı:

- kararlar deterministic ve profile-driven olmalı;
- sessiz feature kaybı olmamalı;
- her enlargement veya omission raporlanmalı;
- aynı feature farklı ürün boyutlarında farklı fakat açıklanabilir karar alabilmeli.

#### Phase 5 — Surface Target & Projection V1

Relief ve ornament geometry yalnız düz plakaya değil, doğrulanmış hedef yüzeylere uygulanacaktır.

Uygulama sırası:

1. flat plane;
2. oriented planar quad;
3. bilinear quadrilateral surface;
4. cylindrical surface;
5. dome ve vault surface;
6. arbitrary indexed mesh surface.

Her target surface şunları taşımalıdır:

- stable local UV frame;
- outward normal convention;
- clipping boundary;
- relief direction ve polarity;
- allowable depth envelope;
- attachment ve intersection policy;
- source component ve target component identity.

Kabul kapısı:

- projection sonrası orientation ve winding doğru olmalı;
- target dışı geometri deterministic olarak clip edilmeli veya reddedilmeli;
- relief parent duvar, silindir veya kubbeyle fiziksel olarak bağlı olmalı;
- self-intersection ve depth-envelope ihlali raporlanmalı;
- flat projection mevcut relief davranışını bozmamalı.

### 8. Ana faz planı — Part C

#### Phase 6 — Architectural Ornament Library V1

Genel ve yeniden kullanılabilir ilk semantik mimari parça aileleri oluşturulacaktır:

- arch ve archivolt;
- recessed window ve tracery;
- portal, door surround ve tympanum;
- column, pilaster, capital ve base;
- cornice, frieze ve molding;
- medallion, rosette ve inscription panel;
- geometric ve floral ornament;
- figurative plaque ve statue niche;
- brick, stone block, roof tile ve repeatable surface unit.

Her katalog kaydı şunları taşımalıdır:

- canonical component ID ve version;
- semantic class ve style tags;
- parametric dimensions ve anchors;
- supported projection modes;
- minimum printable profile;
- material role;
- repetition ve symmetry bilgisi;
- assembled, relief ve kit output eligibility;
- license ve provenance kaydı.

Kabul kapısı:

- aynı parça farklı boyutlarda deterministic üretilmeli;
- her katalog parçası tek başına topology gate geçmeli;
- fiziksel olarak okunamayan varyant reddedilmeli veya resolver tarafından dönüştürülmeli;
- tekrar eden parçalar aynı canonical kimliği korumalı.

#### Phase 7 — Architectural Semantic Relief Product V1

İlk gerçek ürün tek bir doğrulanmış tarihi cephe veya anıt yüzeyi üzerinden geliştirilecektir. Hedef, generic height-map ile semantic component graph sonucunu aynı fiziksel üründe karşılaştırmaktır.

Zorunlu içerik:

- en az bir recessed opening;
- en az bir raised ornament;
- en az bir figurative veya emblematic feature;
- en az bir inscription ya da panel;
- en az üç semantic depth band;
- gerçek target-surface projection;
- shaded preview ve physical print coupon.

Kabul kapısı:

- kimlik ve ana mimari ritim kaynakla görsel olarak uyuşmalı;
- semantic sürüm generic height-map baseline sonucundan daha okunabilir olmalı;
- closed/manifold topology zorunlu olmalı;
- slicer layer preview ve minimum feature kontrolü geçmeli;
- fiziksel coupon kabul edilmeden product-ready statüsü verilmemeli.

#### Phase 8 — Canonical Face/Head Decision Gate

Bu faz production portrait kodu yazmadan önce tamamlanacak teknik ve ticari karar paketidir.

Karşılaştırılacak yollar:

- FLAME 2023 Open canonical geometry ve ATLAS fitting;
- ticari kullanıma uygun alternatif parametric face/head modelleri;
- multi-view image reconstruction;
- kısa video tabanlı reconstruction;
- güvenli local veya kontrollü API tabanlı çözümler.

Zorunlu kanıtlar:

- ticari lisans ve attribution yükümlülükleri;
- model ve veri saklama sınırları;
- Apple Silicon uyumu;
- local, API ve gizlilik davranışı;
- tek fotoğraf, üç fotoğraf ve video desteği;
- identity, expression ve pose korunumu;
- gözlük, saç, kulak ve yüz örtücü aksesuar davranışı;
- mesh kalitesi, topology ve işlem süresi;
- relief projection için uygunluk.

Karar yalnız `GO`, `HOLD` veya `REJECT` olabilir. Kanıt olmadan FLAME veya başka bir motor production dependency yapılamaz. Tek fotoğraftan AI-depth ana yüz geometrisi olarak yeniden etkinleştirilemez.

### 9. Ana faz planı — Part D

#### Phase 9 — Identity-Preserving Portrait Relief V1

Yalnız Phase 8 `GO` kararından sonra geliştirilecektir.

Hedef akış:

```text
onaylı müşteri girdisi
→ face/head reconstruction
→ canonical semantic regions
→ identity ve expression kontrolü
→ frontal contact-plane projection
→ feature-sensitive depth compression
→ düşük genlikli residual detail
→ accessory separation
→ shaded preview
→ operator quality gate
→ manifold relief mesh
```

Ana yüz hacmi güvenilir face/head geometry kaynağından gelmelidir. AI-depth yalnız saç, kulak, siluet veya geniş derinlik yardımcısı olabilir. Gölge, yansıma, gözlük camı ve kıyafet deseni ana geometriye dönüşmemelidir.

Kabul kapısı:

- kimlik ve temel ifade operatör tarafından kabul edilmeli;
- alın, yanak, burun, dudak ve çene hacimleri tutarlı olmalı;
- gözlük camı alttaki yüzü bozmamalı, çerçeve ayrı aksesuar olmalı;
- shaded preview kabul edilmeden STL üretilmemeli;
- müşteri verisi ve model provenance kaydı bulunmalı.

#### Phase 10 — Figurative Body, Pose & Prop Grammar V1

Portre başı, semantik beden ve sahne bileşenleriyle birleştirilecektir.

İlk canonical roller:

- head ve neck anchor;
- torso ve pelvis;
- upper arm, forearm ve hand;
- thigh, lower leg ve foot;
- standing support ve ground contact;
- gaze, gesture ve hand-grip targets;
- clothing silhouette;
- prop ve prop-contact anchors.

İlk aksesuar ailesi:

- fishing rod;
- fishing line;
- fish bucket;
- optional fish emblem;
- ground veya shoreline context panel.

Kabul kapısı:

- poz anatomik ve statik olarak okunabilir olmalı;
- el ile olta arasında gerçek contact bulunmalı;
- kova zemine veya ele fiziksel olarak bağlanmalı;
- ince olta ve uzuvlar physical resolver kontrolünden geçmeli;
- silhouette, head identity ve ana hikâye 170 mm ürün boyutunda okunabilmeli;
- karikatür exaggeration kimliği yok etmemeli.

#### Phase 11 — Personalized Story Composer V1

Kullanıcının kişisi, mesleği, hobisi ve hediye bağlamı semantic scene brief haline getirilecektir.

İlk senaryo:

- kişi profesör;
- amatör balıkçılık hobisi var;
- ayakta duruyor;
- bir elinde olta bulunuyor;
- yanında balık kovası bulunuyor;
- yüz kimliği korunmuş, kontrollü karikatür anlatımı kullanılıyor.

Composer şunları üretmelidir:

- normalized story brief;
- selected character, pose, prop ve environment components;
- component graph ve contact graph;
- depth ve occlusion planı;
- material-role planı;
- ambiguity ve operator-review report;
- preview recipe ve product-output request.

Kabul kapısı:

- eksik veya çelişkili brief sessizce tamamlanmamalı;
- kişinin kimliği, mesleği ve hobisi ayrı semantic alanlar olarak korunmalı;
- aksesuarlar bedene rastgele yerleştirilmemeli;
- aynı onaylı brief deterministic scene plan vermeli;
- operatör onayı olmadan ticari STL üretilmemeli.

### 10. Ana faz planı — Part E

#### Phase 12 — Shared Component Catalog & Kit Contract V1

Architectural relief ve demonte maket aynı canonical parça kimliklerini kullanacaktır. Katalog yalnız mesh deposu olmayacak; parametrik, fiziksel ve ticari sözleşme taşıyacaktır.

Canonical kayıt alanları:

- catalog component ID ve version;
- semantic class, style ve period tags;
- geometry generator veya validated asset reference;
- nominal dimensions ve allowed parameter ranges;
- local origin, orientation ve assembly anchors;
- connector family ve tolerance profile;
- minimum wall, minimum feature ve material profile;
- repeatability ve interchangeable-part group;
- allowed output modes;
- license, provenance ve validation status;
- superseded-by ve backward-compatibility bilgisi.

Kit contract alanları:

- part number ve quantity;
- parent assembly ve assembly step;
- connector interface;
- orientation ve placement transform;
- glue-required, friction-fit veya mechanical-lock policy;
- support ve print orientation recommendation;
- color ve material role;
- replacement ve spare-part eligibility.

Kabul kapısı:

- katalog kaydı immutable ve versioned olmalı;
- duplicate ID ve uyumsuz connector reddedilmeli;
- aynı canonical parça relief ve kit çıktısında izlenebilmeli;
- değişen geometri eski BOM kimliğini sessizce bozamamalı;
- her fiziksel parça ayrı topology report taşımalı.

#### Phase 13 — Modular Architectural Kit Prototype V1

İlk prototip, doğrulanmış ve sınırlı bir tarihi cephe ya da yapı bölümü olacaktır. Tam katedral veya cami ile başlanmayacaktır.

Prototipte bulunacaklar:

- en az 12 tekrar eden kemerli pencere;
- ayrı kapı veya portal;
- ayrı duvar panelleri;
- en az bir çatı, kubbe veya tonoz parçası;
- tekrar eden tuğla, taş veya kiremit ailesi;
- connector ve tolerance coupon;
- BOM, parça numaraları ve montaj sırası;
- baskı plakası grupları;
- yedek parça tanımı;
- gerçek fiziksel fit testi.

Kabul kapısı:

- tüm parçalar ayrı closed/manifold solid olmalı;
- parça numarası BOM ile birebir eşleşmeli;
- bağlantılar hedef toleransla fiziksel olarak oturmalı;
- tekrar eden parçalar birbirinin yerine kullanılabilmeli;
- montaj sırası kapalı veya erişilemez bağlantı üretmemeli;
- kırılan tek parça bütün kit yeniden basılmadan değiştirilebilmeli.

#### Phase 14 — Unified Product Orchestration

Aynı semantic component graph, seçilen product output mode değiştirilerek farklı fiziksel ürünlere dönüştürülecektir:

- flat relief;
- projected facade relief;
- framed portrait relief;
- personalized figurative story relief;
- assembled landmark;
- modular construction kit;
- replacement veya spare-part package.

Orchestrator sorumlulukları:

- output mode eligibility kontrolü;
- component selection ve transformation;
- physical profile ve scale resolution;
- material-role batching;
- relief, solid ve kit geometry adapter seçimi;
- topology ve quality gate çağrıları;
- BOM, manifest, preview ve report üretimi;
- deterministic dosya adları ve package layout;
- operator-review ve acceptance status kaydı.

Kabul kapısı:

- aynı kaynak component kimlikleri farklı output modlarında korunmalı;
- unsupported output mode erken reddedilmeli;
- relief, assembled ve kit geometrileri birbirine karıştırılmamalı;
- manifest her fiziksel dosyayı semantic component ve material role ile eşlemeli;
- preview ile gerçek physical part listesi tutarlı olmalı.

#### Phase 15 — Commercial Production Gate

Hiçbir ürün yalnız STL yazıldığı için production-ready sayılmayacaktır.

Zorunlu kapılar:

1. source, license ve provenance kontrolü;
2. semantic completeness ve operator review;
3. physical feature resolution report;
4. closed/manifold topology;
5. self-intersection ve disconnected-part analizi;
6. dimensions, tolerance ve minimum feature kontrolü;
7. shaded veya color preview kabulü;
8. slicer object ve volumetric material structure kontrolü;
9. filament gram distribution sanity check;
10. support, orientation, purge ve prime-tower incelemesi;
11. gerekiyorsa physical coupon veya fit test;
12. final 3MF, STL, manifest, BOM ve report paketi.

Preview doğru görünürken slicer iç hacmi yanlış filamente verebilir. Bu nedenle per-face color veya colorgroup görünümü volumetric material kanıtı değildir. Ayrı physical solids veya slicer tarafında doğrulanmış volumetric assignment zorunludur.

Production status değerleri:

- `DRAFT`;
- `CONTRACT_READY`;
- `GEOMETRY_READY`;
- `PREVIEW_ACCEPTED`;
- `SLICER_VALIDATED`;
- `PHYSICAL_VALIDATED`;
- `PRODUCTION_READY`;
- `HOLD`;
- `REJECTED`.

Statü atlaması yapılamaz. Her geçiş kanıt dosyası veya doğrulanabilir rapor taşımalıdır.

### 11. Test ve fixture stratejisi

Her faz şu sırayla geliştirilecektir:

1. mevcut baseline testlerini çalıştırmak;
2. tek davranış için RED contract test yazmak;
3. minimal production implementation yapmak;
4. focused testi çalıştırmak;
5. related package regression çalıştırmak;
6. `git diff --check` uygulamak;
7. gerekiyorsa deterministic fixture ve preview üretmek;
8. full regression çalıştırmak;
9. üç ana durum belgesini güncellemek;
10. yalnız ilgili dosyaları stage etmek;
11. commit ve push yapmak;
12. HEAD, origin/main ve status doğrulamak.

Zorunlu fixture aileleri:

- synthetic semantic component graph;
- layered architectural facade;
- curved target surface;
- minimum-feature ve occlusion edge cases;
- canonical ornament catalog entries;
- portrait identity ve accessory cases;
- standing body, hand-grip ve prop-contact cases;
- repeated architectural kit parts;
- connector ve tolerance coupons;
- production manifest ve material-batch fixtures.

Her fixture:

- deterministic olmalı;
- lisans ve provenance taşımalı;
- beklenen semantic graph, bounds ve topology değerlerini kaydetmeli;
- input mutation ve output isolation testlerine uygun olmalı;
- büyük binary dosyayı gerekçesiz olarak Git deposuna eklememeli.

### 12. Stop ve rollback kriterleri

Aşağıdaki durumlardan birinde geliştirme durdurulacak ve milestone `HOLD` olarak kaydedilecektir:

- lisans veya ticari kullanım belirsizliği;
- müşteri görseli için gizlilik ve saklama politikası eksikliği;
- kimlik kaybı veya appearance-to-geometry leakage;
- semantic component graph ile fiziksel geometri arasında izlenebilirlik kaybı;
- açık, non-manifold veya self-intersecting production mesh;
- minimum feature ve tolerance kapısının geçilememesi;
- preview ile slicer volumetric material yapısının uyuşmaması;
- deterministic olmayan sonuç;
- baseline regression bozulması;
- fiziksel coupon veya fit testinin başarısız olması;
- roadmap dışı yatay kapsam genişlemesi.

Rollback kuralı:

- son yeşil ve push edilmiş commit korunur;
- unrelated kullanıcı dosyalarına dokunulmaz;
- destructive reset, broad restore veya clean uygulanmaz;
- deneysel sonuç ayrı tutulur ve production dependency yapılmaz;
- başarısızlık nedeni, kanıtı ve yeniden başlama koşulu belgeye yazılır.

### 13. Milestone kayıt sözleşmesi

Her faz sonunda aşağıdaki bilgiler `START_HERE`, `CURRENT_STATUS` ve aktif devir belgesine tutarlı biçimde kaydedilecektir:

- faz adı ve status;
- amaç ve kapsam;
- oluşturulan veya değiştirilen contractlar;
- ilgili CORE ve Test dosyaları;
- focused, related ve full regression sonuçları;
- fixture, preview ve fiziksel validation kanıtları;
- bilinen sınırlar ve kapsam dışı maddeler;
- son güvenli commit ve origin/main durumu;
- korunan unrelated dosyalar;
- bir sonraki kesin tek adım.

Ara durum değerleri:

- `ROADMAP_WRITING`;
- `AUDIT_ACTIVE`;
- `RED_CONTRACT`;
- `IMPLEMENTATION_ACTIVE`;
- `TEST_GREEN`;
- `PHYSICAL_VALIDATION_PENDING`;
- `LOCKED`;
- `HOLD`;
- `REJECTED`.

Bir faz `LOCKED` olmadan sonraki bağımlı faz production implementation olarak başlatılamaz.

### 14. Öncelik ve bağımlılık kuralı

Zorunlu ana sıra:

```text
Phase 0
→ Phase 1
→ Phase 2
→ Phase 3
→ Phase 4
→ Phase 5
→ Phase 6
→ Phase 7
→ Phase 8 decision gate
→ Phase 9
→ Phase 10
→ Phase 11
→ Phase 12
→ Phase 13
→ Phase 14
→ Phase 15
```

Phase 8 araştırması, Phase 1–7 mimari hattını durdurmaz. Ancak Phase 9–11, Phase 8 `GO` kararı olmadan production geliştirmeye geçemez. Phase 12 catalog contract, Phase 13 kit prototipinden önce kilitlenmelidir. Phase 14 ve Phase 15, önceki ürün hatlarından en az birer gerçek validation kanıtı olmadan kilitlenemez.

### 15. Kesin güncel durma noktası

Status: `RED_CONTRACT`

Phase 0 baseline kanıtı:

- kapsam: relief, architectural relief, semantic architecture ve portrait contract testleri;
- sonuç: `1020 passed in 2.28s`;
- command exit: `0`;
- diff check: temiz;
- unrelated untracked dosyalar değişmedi.
- full regression: `3772 passed in 16.84s`, exit `0`;
- Phase 0 status: `LOCKED`.

Bu kayıt anında:

- semantic relief programı için CORE implementation başlatılmadı;
- yeni RED contract testi yazılmadı;
- Phase 0 ilgili baseline regression tamamlandı ve yeşil;
- mevcut relief ve facade altyapısına dokunulmadı;
- portrait için FLAME veya başka motor production dependency yapılmadı;
- korunan Jamaica preview dosyaları ve `Data/OSM/` kapsam dışıdır.

Sıradaki kesin iş:

1. Bu ana roadmap kaydını `START_HERE` ve `CURRENT_STATUS` belgelerine kısa ve tutarlı yönlendirmelerle bağlamak.
2. Üç belgenin UTF-8, heading, diff ve status kontrollerini yapmak.
3. Mevcut relief ve semantic architecture baseline testlerini çalıştırmak.
4. Phase 0 audit sonucunu kaydetmek.
5. Yalnız bundan sonra Phase 1 için ilk RED contract testini yazmak.

### Phase 1 ara milestone — Canonical component foundation

Status: `IMPLEMENTATION_ACTIVE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%7`
- CORE: `CORE/atlas_semantic_relief_component.py`
- Test: `Test/test_semantic_relief_component.py`
- Focused validation: `22 passed in 0.03s`
- Related semantic validation: `46 passed in 0.14s`
- Full regression: `3794 passed in 16.84s`
- Diff check: temiz

Tamamlanan canonical davranışlar:

- immutable component contract;
- component ve parent identity normalizasyonu;
- source reference korunumu;
- target surface ve projection mode birlikteliği;
- semantic depth band ve non-negative layer order;
- semantic material role ve physical feature policy;
- non-empty, unique output eligibility;
- provenance ve finite `0.0..1.0` confidence;
- geçersiz projection, layer order, output mode ve confidence girdilerinin reddi.

Phase 1 henüz `LOCKED` değildir. Sıradaki kesin paket immutable transform, orientation ve physical dimensions contractıdır. Ardından repetition contract ve `AtlasSemanticReliefScene` graph doğrulamaları geliştirilecektir.

Kalıcı yüzde kayıt kuralı:

- her anlamlı milestone kaydında `ATLAS genel tamamlanma` ve `Aktif program tamamlanma` birlikte yazılacaktır;
- yüzdeler test sayısına göre değil, kabul kapısı tamamlanan gerçek yeteneklere göre değiştirilecektir;
- Phase veya fiziksel ürün kabul kapısı tamamlanmadan yapay yüzde artışı yapılmayacaktır.

### Phase 1 ara milestone — Transform ve fiziksel yerleşim

Status: `IMPLEMENTATION_ACTIVE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%8`
- CORE: `CORE/atlas_semantic_relief_transform.py`
- Entegrasyon: `CORE/atlas_semantic_relief_component.py`
- Test: `Test/test_semantic_relief_transform.py`
- Focused validation: `31 passed in 0.05s`
- Related semantic validation: `55 passed in 0.16s`
- Full regression: `3803 passed in 16.81s`
- Diff check: temiz

Tamamlanan davranışlar:

- immutable translation, XYZ rotation ve physical dimensions;
- numeric değerlerin deterministic float tuple normalizasyonu;
- finite-value validation;
- positive physical dimensions zorunluluğu;
- explicit `component_local` veya normalize edilmiş coordinate-space kimliği;
- malformed triplet reddi;
- component üzerinde yalnız validated transform nesnesi kabulü.

Bu contract aynı kemer, heykel, pencere veya kit parçasının farklı konum, yön ve fiziksel ölçülerde güvenilir biçimde yeniden kullanılmasını sağlar.

Phase 1 henüz `LOCKED` değildir. Sıradaki kesin paket repetition ve interchangeable-instance contractıdır. Ardından `AtlasSemanticReliefScene` graph doğrulamaları başlayacaktır.

### Phase 1 ara milestone — Repetition ve interchangeable instances

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%9`
- Yeni contract: `CORE/atlas_semantic_relief_repetition.py`
- Yeni test: `Test/test_semantic_relief_repetition.py`
- Canonical alanlar: `repeat_group_id`, pozitif `quantity`, finite `spacing_mm`, strict boolean `interchangeable`.
- Çoklu instance için sıfır spacing reddedilir; tek instance için kabul edilir.
- Component yalnız doğrulanmış repetition nesnesi veya `None` kabul eder.
- Focused: `41 passed in 0.04s`.
- Related: `72 passed in 0.17s`.
- Full regression: `3820 passed in 16.81s`.
- `git diff --check`: temiz.

Bu contract tekrarlanan pencere, kemer, sütun, panel, karo ve kit parçalarını ortak canonical grup ve fiziksel tekrar düzeniyle temsil eder. Gerçek interchangeability fit/tolerance kanıtı sonraki physical resolver ve production gate aşamalarında ayrıca zorunludur.

Sıradaki kesin iş: component, transform ve repetition contractlarını birleştiren immutable `AtlasSemanticReliefScene` graph için ilk RED sözleşme.

### Phase 1 ara milestone — Immutable semantic relief scene graph

Status: `GREEN_MILESTONE`; Phase 1 henüz `LOCKED` değildir.

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%10`
- Yeni contract: `CORE/atlas_semantic_relief_scene.py`
- Yeni test: `Test/test_semantic_relief_scene.py`
- Immutable scene identity ve non-empty typed component koleksiyonu kuruldu.
- Duplicate component ID, missing parent, missing target surface, self-parent ve parent cycle reddedilir.
- `component_for_id`, `children_for_id`, `components_for_target_surface` ve `root_components` deterministic traversal sağlar.
- Focused: `12 passed in 0.02s`.
- Related: `84 passed in 0.19s`.
- Full regression: `3832 passed in 16.78s`.
- `git diff --check`: temiz.

Phase 1 kalan kabul kapıları: component `occlusion_policy`; architecture, portrait, figurative ve kit kullanımını aynı contract ile gösteren synthetic fixture; mevcut `AtlasSemanticArchitectureModel` alanlarının yeni scene/component sözleşmesine geçiş eşlemesinin belgelenmesi. Gerçek adapter Phase 2 kapsamındadır.

Sıradaki kesin iş: `occlusion_policy` için ilk RED contract.

### Phase 1 geçiş ilişkisi — Semantic Architecture → Semantic Relief

Mevcut `AtlasSemanticArchitectureModel` ve component sözleşmesi korunacaktır. Yeni semantic relief contract eski modeli değiştirmez; Phase 2 adapterı doğrulanmış mimari modeli yeni scene graph’a tek yönlü ve deterministic biçimde aktaracaktır.

Alan eşlemesi:

- `role + instance_index` → unique `component_id`; önerilen deterministic biçim `{role}_{instance_index}`;
- `parent_role` → kesin `parent_component_id`; tekrar eden parent rolleri belirsizse adapter açık hata vermelidir;
- `geometry_kind` → doğrudan yeni geometry kaynağı sayılmaz; `geometry_source_kind=semantic_architecture_adapter` kullanılır ve eski geometry kind adapter girdisi/source reference olarak korunur;
- `landmark_family` → scene provenance ve semantic-class çözümleme bağlamı;
- `grammar_name` → adapter configuration/source provenance;
- `profile_name` ve eski flags → körlemesine kopyalanmaz; yalnız açık mapping ile output eligibility, physical policy veya provenance alanlarına aktarılır;
- mevcut component sırası → yeni scene component sırası; deterministic kalmalıdır.

Geçiş kuralları:

- duplicate yeni ID üretilemez;
- missing veya ambiguous parent sessiz fallback yapamaz;
- eski model mutation görmez;
- adapter sonucu `AtlasSemanticReliefScene` doğrulamalarından geçmek zorundadır;
- reverse conversion varsayılmaz;
- gerçek adapter implementation ve mapping testleri Phase 2 kapsamındadır.

### Phase 1 kabul kapısı — LOCKED

Status: `LOCKED`.

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%12`
- `AtlasSemanticReliefComponent`, transform, repetition ve immutable scene graph tamamlandı.
- `occlusion_policy` dahil Phase 1 alan ve validation sözleşmeleri kapatıldı.
- Architecture, portrait, figurative ve modular-kit aileleri synthetic fixture ile aynı scene contractında doğrulandı.
- `AtlasSemanticArchitectureModel` geçiş ilişkisi yukarıda belgelendi; eski model korunur ve gerçek adapter Phase 2 kapsamındadır.
- Focused use-case: `41 passed in 0.06s`.
- Related semantic regression: `87 passed in 0.20s`.
- Full regression: `3835 passed in 16.74s`.
- `git diff --check`: temiz.

Phase 1 yeniden açılmayacaktır; yalnız gerçek regresyon veya açık contract eksikliği kanıtlanırsa düzeltme yapılacaktır. Sıradaki kesin iş Phase 2 provider-independent Geometry Source Adapter result contractı için ilk RED testidir.

### Fiziksel milestone — 25 mm corner support GREEN_PROTOTYPE

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%12`
- Harici female socket ve male pin/pad geometrileri kaldırıldı; yalnız ana 90 derece köşe ile iç taşıyıcı raf korundu.
- Focused paket: `26 passed in 0.08s`; full regression: `3836 passed in 16.80s`.
- Yeni `25MM` STL `64` triangle ve yaklaşık `13 KB` olarak üretildi.
- Dört gerçek PLA parça kalite, tutuş ve sallanma kontrollerini geçti: `GREEN_PROTOTYPE`.
- Mevcut `50MM` STL eski connector geometrisi nedeniyle geçersizdir ve basılmayacaktır.
- Sonraki fiziksel iş tam kutudan önce havuz-yükseltici-kapak geçmeleri için küçük tolerans kuponudur.

### Semantic Relief Phase 2 — Geometry Source Result milestone

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%14`
- Aktif faz: Phase 2 `IMPLEMENTATION_ACTIVE`
- İlk Phase 2 canonical result contractı `AtlasGeometrySourceResult` oluşturuldu.
- Result provider-independent biçimde normalized geometry, local bounds, anchors, confidence, provenance ve supported projection modes taşır.
- Mutable caller inputları resulttan izole edilir; local bounds min/max sırası doğrulanır.
- Projection capability açık contracttır; unsupported mode erken `ValueError` üretir.
- Focused validation: `21 passed in 0.02s`.
- Related semantic regression: `113 passed in 0.27s`.
- Full regression: `3873 passed in 16.79s`, `1` unrelated failure.
- Unrelated failure mevcut untracked Premium Gift Box connector calibration spec/test tutarsızlığıdır; Phase 2 dosyalarından kaynaklanmaz.
- `git diff --check`: temiz.
- Korunan unrelated working-tree dosyalarına stage/reset/restore/clean uygulanmadı.
- Sıradaki kesin tek iş: Phase 2 Geometry Source Adapter Contracts kapsamında provider/CORE responsibility boundary ve adapter interface için ilk RED contract.

### Semantic Relief Phase 2 — Geometry Source Adapter boundary milestone

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%15`
- Aktif faz: Phase 2 `IMPLEMENTATION_ACTIVE`
- `AtlasGeometrySourceAdapter` provider ile ATLAS CORE arasındaki canonical geometry boundary olarak oluşturuldu.
- Provider veya source implementation kendi girdisini anlayabilir; boundary sonrasında CORE yalnız `AtlasGeometrySourceResult` görür.
- Abstract `adapt(source)` contractı zorunludur.
- `validate_result()` provider-specific/non-canonical outputu reddeder.
- Projection support canonical result capability setinden doğrulanır.
- Focused Phase 2 validation: `27 passed in 0.04s`.
- Related semantic regression: `113 passed in 0.25s`.
- Full regression: `3879 passed in 16.74s`, `1` unrelated failure.
- Unrelated failure mevcut untracked Premium Gift Box connector calibration spec/test tutarsızlığıdır; Phase 2 kaynaklı değildir.
- `git diff --check`: temiz.
- Korunan unrelated working-tree dosyalarına stage/reset/restore/clean uygulanmadı.
- Sıradaki kesin tek iş: Master Execution Compass Phase 2 sırasına göre `height-map relief source` için ilk concrete adapter RED contractı.

### Semantic Relief Phase 2 — Height-map Geometry Source Adapter milestone

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%17`
- Aktif faz: Phase 2 `IMPLEMENTATION_ACTIVE`
- İlk concrete Phase 2 adapter `AtlasHeightMapGeometrySourceAdapter` oluşturuldu.
- Existing normalized relief height-map kaynağı canonical `AtlasGeometrySourceResult` biçimine taşınır.
- Source contract 2D numeric, finite, minimum 2x2 ve normalized `0.0..1.0` height field ister.
- Canonical result physical width, depth ve relief height ile deterministic local bounds oluşturur.
- Adapter herhangi bir triangle mesh veya STL üretmez.
- Projection capability yalnız `flat_plane` olarak ilan edilir; curved surface projection Phase 5 kapsamıdır.
- Caller mutable inputları resulttan izole edilir.
- Focused Phase 2 validation: `44 passed in 0.08s`.
- Related semantic/architectural relief regression: `126 passed in 0.28s`.
- Full regression: `3896 passed in 16.73s`, `1` unrelated failure.
- Unrelated failure mevcut untracked Premium Gift Box connector calibration spec/test tutarsızlığıdır; Phase 2 kaynaklı değildir.
- `git diff --check`: temiz.
- Korunan unrelated working-tree dosyalarına stage/reset/restore/clean uygulanmadı.
- Sıradaki kesin tek iş: Master Execution Compass Phase 2 sırasına göre `existing triangle mesh source` için ilk concrete adapter RED contractı.

### Semantic Relief Phase 2 — Existing Triangle Mesh Source Adapter milestone

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%19`
- Aktif faz: Phase 2 `IMPLEMENTATION_ACTIVE`
- İkinci concrete Phase 2 adapter `AtlasTriangleMeshGeometrySourceAdapter` oluşturuldu.
- Existing ATLAS triangle-soup geometry kaynakları canonical `AtlasGeometrySourceResult` biçimine taşınır.
- Source triangles 3 point × 3 coordinate yapısında normalize edilir; numeric, finite ve bool olmayan koordinatlar zorunludur.
- Local bounds bütün source geometry noktalarından deterministic hesaplanır.
- Caller mutable triangle inputları canonical resulttan izole edilir.
- Adapter geometry source normalization sınırıdır; closed/manifold physical-production validation bu contractın kapsamı değildir.
- Focused Phase 2 validation: `55 passed in 0.09s`.
- Related semantic/relief regression: `143 passed in 0.27s`.
- Premium Gift Box calibration stale test ayrıca güncel belgelenmiş production contractına hizalandı; production spec değiştirilmedi.
- Full regression: `3908 passed in 16.80s`.
- `git diff --check`: temiz.
- Korunan unrelated working-tree çalışmalarına reset/restore/clean uygulanmadı.
- Sıradaki kesin tek iş: Master Execution Compass Phase 2 sırasına göre `parametric primitive source` için ilk RED contract.

### Semantic Relief Phase 2 — Parametric Primitive Source Adapter milestone

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%21`
- Aktif faz: Phase 2 `IMPLEMENTATION_ACTIVE`
- Üçüncü concrete Phase 2 adapter `AtlasParametricPrimitiveGeometrySourceAdapter` oluşturuldu.
- İlk desteklenen primitive `closed_cylinder`.
- Parametric descriptor canonical `AtlasGeometrySourceResult` biçimine normalize edilir.
- `closed_cylinder` parameter contract: center_x, center_y, base_z, radius, height, segments.
- Local bounds ve base/top center anchors deterministic türetilir.
- Adapter geometry üretmez; triangle/mesh/STL oluşturmaz.
- Unsupported primitive ve malformed parameter setleri erken fail eder.
- Focused Phase 2 validation: `74 passed in 0.11s`.
- Related semantic/geometry regression: `152 passed in 0.29s`.
- Full regression: `3927 passed in 16.52s`.
- `git diff --check`: temiz.
- Korunan unrelated working-tree çalışmalarına reset/restore/clean uygulanmadı.
- Sıradaki kesin tek iş: Master Execution Compass Phase 2 sırasına göre `facade grammar source` için ilk RED contract.

### Semantic Relief Phase 2 — Facade Grammar Source Adapter milestone

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%23`
- Aktif faz: Phase 2 `IMPLEMENTATION_ACTIVE`
- Dördüncü concrete Phase 2 adapter `AtlasFacadeGrammarGeometrySourceAdapter` oluşturuldu.
- İlk desteklenen grammar `uniform_openings`.
- Facade descriptor canonical `AtlasGeometrySourceResult` biçimine normalize edilir.
- Contract facade width/height, level count, bay count, opening kind ve margin ratios taşır.
- Opening count deterministic olarak `level_count * bay_count` türetilir.
- Local bounds ve facade anchorları deterministic oluşturulur.
- Adapter geometry üretmez; facade mesh/STL/triangle üretimi mevcut mesher sistemlerinde kalır.
- Unsupported grammar ve malformed facade parameter setleri erken fail eder.
- Focused Phase 2 validation: `102 passed in 0.13s`.
- Related semantic/facade regression: `188 passed in 0.37s`.
- Full regression: `3955 passed in 16.66s`.
- `git diff --check`: temiz.
- Korunan unrelated working-tree çalışmalarına reset/restore/clean uygulanmadı.
- Sıradaki kesin tek iş: Master Execution Compass Phase 2 sırasına göre `catalog component source` için ilk RED contract.

### Semantic Relief Phase 2 — Catalog Component Source Adapter milestone

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%25`
- Aktif faz: Phase 2 `IMPLEMENTATION_ACTIVE`
- Beşinci concrete Phase 2 adapter `AtlasCatalogComponentGeometrySourceAdapter` oluşturuldu.
- Existing Master Landmark Catalog entry ile semantic component reference canonical `AtlasGeometrySourceResult` biçiminde birleştirilir.
- Catalog lookup Wikidata ve OSM identity üzerinden yapılabilir.
- Catalog metadata; geometry bounds ve anchor metadata'sından bilinçli olarak ayrı tutulur.
- Flagged catalog entry'lerde undeclared component role erken reddedilir.
- Adapter mesh, triangle veya STL üretmez.
- Focused Phase 2 validation: `116 passed in 0.16s`.
- Related catalog/semantic regression: `137 passed in 0.25s`.
- Full regression: `3969 passed in 16.77s`.
- `git diff --check`: temiz.
- Korunan unrelated working-tree çalışmalarına reset/restore/clean uygulanmadı.
- Sıradaki kesin tek iş: Master Execution Compass Phase 2 sırasındaki `future canonical face/head source` için mevcut face/head geometry contract audit ve ilk RED contract.

### Semantic Relief Phase 2 — Face/Head Geometry Source Adapter milestone

Status: `GREEN_MILESTONE`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%27`
- Aktif faz: Phase 2 `IMPLEMENTATION_ACTIVE`
- Altıncı concrete Phase 2 adapter `AtlasFaceHeadGeometrySourceAdapter` oluşturuldu.
- Existing `AtlasPortraitLandmarkResult` canonical `AtlasGeometrySourceResult` biçimine normalize edilir.
- Geometry kind `face_head_landmarks`; coordinate space `normalized_image_2d`.
- Landmark names canonical snake_case identity kazanır.
- Deterministic local bounds ve `(x, y, 0.0)` semantic anchors oluşturulur.
- Provider confidence ve provenance korunur.
- Adapter mesh, triangle, STL veya canonical 3D head geometry üretmez.
- Phase 8 Face/Head Decision Gate korunmuştur; bu milestone yalnız source-adapter contractıdır.
- Focused Phase 2 validation: `124 passed in 0.18s`.
- Related portrait/face regression: `176 passed in 0.22s`.
- Full regression: `3977 passed in 16.92s`.
- `git diff --check`: temiz.
- Korunan unrelated working-tree çalışmalarına reset/restore/clean uygulanmadı.
- Sıradaki kesin tek iş: Master Execution Compass Phase 2 sırasındaki `future body/pose/prop source` için mevcut figurative/body/pose/prop contract audit ve ilk RED contract.

### Semantic Relief Phase 2 — Geometry Source Adapter Contracts LOCKED

Status: `LOCKED`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%30`
- Phase 2 acceptance gate tamamlandı.
- `AtlasGeometrySourceResult` ve `AtlasGeometrySourceAdapter` canonical boundary olarak kilitlendi.
- Tamamlanan adapter aileleri:
  - height-map relief
  - triangle mesh
  - parametric primitive
  - facade grammar
  - catalog component
  - face/head future boundary
  - body/pose/prop future boundary
- Provider/CORE sorumluluk ayrımı doğrulandı.
- Same semantic scene / different adapter implementation acceptance testi PASS.
- Adapter result determinism ve input isolation contractları PASS.
- Unsupported projection mode early-fail contractı PASS.
- Future face/head ve body/pose/prop sınırlarında olmayan geometry icat edilmedi.
- Phase 2 final focused validation: `137 passed in 0.21s`.
- Full regression: `3990 passed in 16.55s`.
- `git diff --check`: temiz.
- Korunan unrelated working-tree çalışmalarına reset/restore/clean uygulanmadı.
- Sıradaki kesin tek iş: Master Execution Compass Phase 3 `Semantic Depth & Occlusion` audit ve ilk RED contract.

### Semantic Relief Phase 3 — Semantic Depth & Occlusion Composer LOCKED

Status: `LOCKED`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%36`
- Phase 3 acceptance gate tamamlandı.
- Canonical composer: `AtlasSemanticDepthOcclusionComposer`.
- Semantic component graph, triangle mesh üretmeden deterministic composition planına dönüşür.
- Kilitlenen contractlar:
  - semantic depth band → local relief range
  - back-to-front ordering
  - same-band deterministic `layer_order`
  - parent-child / nested depth inheritance
  - explicit occlusion conflict reporting
  - `contact/embed/recess/raised` semantic depth relations
  - impossible-embed rejection
  - material boundary / geometry boundary separation
  - deterministic operator `depth_band` override + audit record
- Numeric relief composerları yeniden yazılmadı; mevcut `AtlasReliefDepthComposer`, `AtlasArchitecturalReliefDepthComposer` ve `AtlasReliefLayerSeparator` ayrı görevlerinde korundu.
- Mesher-level `embed_mm` ile Phase 3 semantic relation birbirine karıştırılmadı.
- Phase 4 `physical_feature_policy` printability kararları Phase 3'e çekilmedi.
- Parent cycle validation `AtlasSemanticReliefScene` sorumluluğunda kaldı.
- Acceptance:
  - wall + arch + inscription/angel 3+ layer ordering: PASS
  - overlapping depth-band rejection: PASS
  - parent-cycle rejection: PASS
  - physically impossible embed rejection: PASS
  - deterministic composition: PASS
  - no triangle mesh production: PASS
- Phase 3 focused: `30 passed in 0.04s`.
- Related regression: `124 passed in 0.18s`.
- Full regression: `4020 passed in 16.68s`.
- `git diff --check`: temiz.
- Korunan unrelated working-tree çalışmalarına reset/restore/clean uygulanmadı.
- Sıradaki kesin tek iş: Master Execution Compass Phase 4 `Physical Feature Resolver` audit ve ilk RED contract.

### Semantic Relief Phase 4 — Physical Feature Resolver LOCKED

Status: `LOCKED`

- ATLAS genel tamamlanma: `%68`
- Aktif program tamamlanma: `%42`
- Phase 4 acceptance gate tamamlandı.
- Canonical resolver: `AtlasPhysicalFeatureResolver`.
- Canonical physical profile: `AtlasPhysicalFeatureProfile`.
- Phase 4 mesh/STL üretmez; semantic feature ölçülerini physical decision planına dönüştürür.
- Mevcut legacy/specialized physical systems yeniden yazılmadı:
  - `AtlasPhysicalDetailResolver`
  - `AtlasPhysicalCartographicExaggerationResolver`
  - `AtlasMinimumThicknessAnalyzer`
  - `AtlasFragileConnectionAnalyzer`
  - `AtlasFacadeOrnamentDensityResolver`
- Phase 4 bunların görevlerini kopyalamadan daha üst canonical semantic karar katmanı oluşturur.
- Kilitlenen fiziksel action vocabulary:
  - `preserve`
  - `enlarge`
  - `merge`
  - `simplify`
  - `convert_to_engraving`
  - `omit`
  - `require_operator_review`
- Ölçüm/karar kapsamı:
  - minimum raised width / height
  - minimum groove width / depth
  - adjacent-feature spacing
  - repeated-detail density
  - unsupported projection
  - unsupported slope
  - fragile connection ratio
  - semantic importance
  - readability priority
  - product size
  - nozzle diameter
  - layer height
  - material identity
- Important unprintable feature otomatik omit edilmez.
- Omission ve enlargement explicit reason/adjustment records taşır.
- Product-size aware raised-feature scaling aynı semantic feature'ın farklı ürün ölçülerinde açıklanabilir farklı karar almasını sağlar.
- Acceptance:
  - deterministic decisions: PASS
  - no silent feature loss: PASS
  - enlargement / omission reporting: PASS
  - high-priority unprintable feature operator review: PASS
  - different product size → different but explainable decision: PASS
- Phase 4 focused: `17 passed in 0.04s`.
- Related regression: `104 passed in 0.14s`.
- Full regression: `4037 passed in 17.01s`.
- `git diff --check`: temiz.
- Korunan unrelated working-tree çalışmalarına reset/restore/clean uygulanmadı.
- Sıradaki kesin tek iş: Master Execution Compass Phase 5 `Surface Target & Projection V1` audit ve ilk RED contract.

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
