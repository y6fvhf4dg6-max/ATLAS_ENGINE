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
