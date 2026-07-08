# ATLAS ENGINE STATUS UPDATE
## Tarih
2026-07-05 (Devam)

---

# Genel Durum

ATLAS artık yalnızca bina üreten bir motor değildir.

Motor;

- Area First mimarisine geçti.
- Scene First mimarisine geçti.
- Yol katmanını okuyabiliyor.
- Yol mesh üretebiliyor.
- STL içerisine bina ve yolu birlikte yazabiliyor.

Bu, ATLAS'ın ilk gerçek şehir sahnesine geçişidir.

---

# Tamamlanan Çalışmalar

## 1. Area First Product Mode

Eski yaklaşım:

- Rastgele bina seçimi
- Seçilen binaları bir araya toplama

tamamen kaldırıldı.

Yeni yaklaşım:

Kullanıcının seçtiği harita alanı üründür.

ATLAS artık;

- 10x10
- 14x14
- 18x18
- 20x20
- 26x26
- 52x52

gibi ürün ölçülerine göre seçilen alanı ölçeklemektedir.

---

## 2. Scene Architecture

Yeni mimari oluşturuldu.

Reader

↓

Scene Builder

↓

Scene

↓

Normalize

↓

Fit

↓

Exporter

Bu yapı ileride;

- Terrain
- Water
- Parks
- Trees
- Railways
- Bridges
- POI

katmanlarının eklenmesine uygun hale getirildi.

---

## 3. Road Engine

Reader artık;

- roads
- pedestrian_paths

okuyabiliyor.

İlk Road Mesh Builder yazıldı.

Road mesh;

- extrusion
- triangle
- mesh

oluşturabiliyor.

İlk defa;

Buildings + Roads

aynı STL içerisine yazıldı.

---

## 4. Base Plate

İlk Base Plate Builder geliştirildi.

İlk testlerde;

Base Plate

↓

Road

↓

Building

katmanları oluşturuldu.

Ancak Base Plate ile diğer meshler arasında Z koordinatı problemi tespit edildi.

---

# Mimari Kararlar

## Universal Data Architecture

ATLAS yalnızca OSM motoru olmayacaktır.

Gelecekte;

- OSM
- Belediye GIS
- GeoJSON
- Shapefile
- CityGML
- PostGIS
- Kullanıcı yüklemeleri
- Tarihsel veri

aynı motor tarafından okunacaktır.

---

## Data Fusion Engine

Yeni prensip kabul edildi.

Farklı veri kaynakları doğrudan kullanılmayacaktır.

Bütün kaynaklar;

AtlasDataFusionEngine

tarafından;

- doğrulanacak
- çelişkileri çözülecek
- güven puanı verilecek

ve daha sonra AtlasScene oluşturulacaktır.

---

## Place-Centric Principle

ATLAS'ın amacı;

kişileri analiz etmek değildir.

ATLAS;

- bina
- yol
- çevre
- doğal yapı
- şehir dokusu

ile ilgilenir.

Fotoğraflardaki insanlar analiz hedefi değildir.

Bu prensip gelecekte;

Atlas History

için temel mimari karar olarak kabul edildi.

---

## Heritage Program

Yeni uzun vadeli fikir geliştirildi.

Kullanıcılar;

40 yıl ve üzeri eski fotoğraflarını sisteme yükleyebilecek.

ATLAS;

bu fotoğrafların;

- arka planını
- bina bilgilerini
- çevresini
- şehir dokusunu

kullanacaktır.

Yüz tanıma yapılmayacaktır.

Katılımcılara;

- indirim
- ücretsiz model
- puan sistemi

gibi ödüller verilmesi planlandı.

---

# Teknik Sorun

Şu anda tek aktif problem bulunmaktadır.

Problem:

Base Plate eklendiğinde;

- bina
- yol

meshleri doğru üretilmesine rağmen;

Base Plate ile Z koordinatında çakışmaktadır.

Testler göstermiştir ki;

Base Plate kapatıldığında;

- bina doğru
- yol doğru

çalışmaktadır.

Dolayısıyla;

Road Builder doğru çalışmaktadır.

Sorun;

Base Plate ile Scene birleşim aşamasındadır.

---

# Son Test Sonucu

Başarıyla çalışanlar:

✓ Reader

✓ Coordinate Engine

✓ Scale Engine

✓ Scene Builder

✓ Building Mesh

✓ Road Mesh

✓ Normalize

✓ Fit

✓ STL Export

Çalışmayan:

✗ Base Plate entegrasyonu

---

# Sonraki Hedef

Base Plate'in;

Scene oluşturulduktan,

Normalize tamamlandıktan,

Fit tamamlandıktan

SONRA eklenmesi.

Ardından;

katman sırası şu olacaktır:

Base Plate

↓

Roads

↓

Pedestrian

↓

Buildings

↓

POI

↓

Trees

↓

Terrain

---

# Bundan Sonraki Geliştirme Sırası

1. Base Plate problemi çözülecek.

2. Pedestrian Layer

3. Terrain Layer

4. Water Layer

5. Parks

6. Trees

7. POI

8. Landmark Engine

9. Multi Material Printing

10. ATLAS History altyapısı

---

# Genel Değerlendirme

ATLAS'ın çekirdek mimarisi artık oluşmuştur.

Motor;

tek bir STL üreticisinden çıkarak;

çok katmanlı şehir sahnesi üreten bir sisteme dönüşmüştür.

Şu anda ticari ürüne giden yoldaki en büyük teknik engel yalnızca Base Plate entegrasyonudur.

Bu problem çözüldükten sonra sistem gerçek şehir modelleri üretmeye başlayacaktır.
Benim ek değerlendirmem

Bu rapora bir not daha düşmek istiyorum.

Bugün yaptığımız testler sayesinde önemli bir mühendislik dersi öğrendik:

Yeni katmanları (Road, Base Plate, Terrain vb.) eklerken, bunları mevcut STL zincirine sonradan “eklemek” yerine, en baştan katmanlı bir sahne grafiği (scene graph) mantığıyla yönetmek daha doğru olacaktır.

Bence bu, yarın ilk iş olarak ele almamız gereken konu olmalı. Base Plate sorununu sadece düzeltmek değil, ATLAS’ın katman mimarisini uzun yıllar sorunsuz taşıyacak şekilde yeniden yapılandırmak daha doğru bir yatırım olacaktır. Bu yaklaşım, ileride Terrain, Water, Parks ve ATLAS History gibi katmanların eklenmesini de çok daha kolay hale getirecektir.
## Road Surface Experiments

- Raised road meshes disabled with use_raised_roads=False.
- Road footprints are generated successfully: 53 footprints / 192 segments.
- Road polygon builder works: 53 accepted polygons.
- Segment groove and polygon groove tests proved the concept but are not yet product-safe.
- Current safe product mode: buildings + base plate only.
- Next required step: apply the same normalize/fit transform to road groove meshes without affecting base plate alignment.
# ATLAS ENGINE STATUS – Gün Sonu

## Güvenli mevcut durum

Son kod çalışıyor.

Son başarılı çıktı:

- Meshes: 134
- Triangles: 4744
- Buildings: 80
- Roads: 0
- Output: OUTPUT/STL/latest.stl

Not:
Roads: 0 normaldir. Çünkü eski raised-road sistemi kapalı. Yollar artık `road_groove_meshes` olarak deneysel recessed-road hattından geliyor.

## Bugün çözülenler

- Base plate tekrar geri geldi.
- Raised road sistemi kapalı tutuldu.
- `use_recessed_roads=True` test dosyasına eklendi.
- Road footprint üretimi çalışıyor.
- Road polygon üretimi çalışıyor.
- Polygon groove mesh üretimi çalışıyor.
- 53 yol mesh’i STL’ye ekleniyor.
- `AtlasSceneNormalizer` ve `AtlasSceneFitter` yeniden kullanılabilir transform sistemine geçirildi.
- Yollar ve binalar aynı transform zincirinden geçirilmeye başlandı.

## Son görülen problem

Yollar ve binalar artık birlikte geliyor; ancak sahne 0,0 koordinatına oturduğu için şehir/base plate hizası kaydı.

Sebep:
Fit işlemi artık sahneyi `target_size_mm=180` alanına oturtuyor, fakat base plate merkezde `origin_x=38`, `origin_y=38` ile oluşturuluyor.

Yani:

- şehir/yollar: 0–180 aralığında
- base plate: 38–218 aralığında

Bu nedenle şehir ve bazı yollar base plate dışına kayık görünüyor.

## Henüz yazılmayan son kod

Son önerilen `_offset_meshes_xy` helper kodu henüz yazılmadı.

Yarın başlanacak yer burası.

## Yarın yapılacak ilk işlem

`CORE/atlas_engine.py` içinde:

1. `scene_origin_x = (bed_width_mm - target_size_mm) / 2.0`
2. `scene_origin_y = (bed_depth_mm - target_size_mm) / 2.0`
3. Şehir + road groove meshleri base plate origin kadar XY offsetlenecek.
4. Base plate de aynı `scene_origin_x`, `scene_origin_y` ile oluşturulacak.

Amaç:

- binalar base plate üzerine geri otursun
- recessed yollar da aynı yerde kalsın
- tabla dışına taşma kalksın

## Kritik not

Son önerilen kod uygulanmadı. Yarın buradan devam edilecek.

# ATLAS ENGINE STATUS — 2026-07-06

---

# ATLAS ENGINE PRODUCT STANDARD v1.0

## Ana Mimari Kararı

Bugünden itibaren ATLAS sabit ölçekli ürün motoru mantığıyla geliştirilecektir.

Eski yaklaşım:

```text
bbox ver
↓
Motor ölçek hesaplasın
```

Yeni yaklaşım:

```text
Merkez koordinat
+
Ürün boyutu
+
Sabit ölçek
↓
Atlas Product Area Engine
↓
BBox üret
↓
Reader
↓
Scene
↓
STL
```

Bu mimari bundan sonra değiştirilmeyecektir.

---

# Sabit Ölçek Standardı

ATLAS'ın ilk ticari standardı aşağıdaki şekilde kilitlenmiştir.

```text
XY Scale : 1 : 5500
Z Scale  : 1 : 5500
```

Bundan sonra;

ölçek değişmeyecek,

ürün boyutu büyüdükçe kapsanan gerçek dünya alanı büyüyecek.

---

# Ürün Mantığı

Yeni ürün mantığı aşağıdaki gibidir.

```text
Küçük ürün
↓

Küçük alan

--------------------------------

Büyük ürün
↓

Büyük alan

--------------------------------

Ölçek

↓

HER ZAMAN AYNI
```

Bu sistem profesyonel şehir modeli üreticilerinin kullandığı mantığa yakındır.

---

# Product Area Engine

Yeni modül oluşturuldu.

```text
CORE/atlas_product_area_engine.py
```

Görevi:

```text
Center Latitude

Center Longitude

Product Size

Fixed Scale

↓

BBox üretmek
```

Bu modül artık ürün motorunun temelidir.

---

# Test Ürünü

Bugünkü test

```text
Product Size

200 mm
```

Sonuç

```text
XY Scale

5500

Z Scale

5500

Height

20.8 mm
```

---

# Bina Limiti

Eski

```text
max_buildings = 80
```

tamamen kaldırıldı.

Yeni sistem

```text
Alan içerisinde bulunan

TÜM

uygun binaları işler.
```

Bugünkü sonuç

```text
Buildings

1207
```

---

# Güncel STL Sonucu

```text
After base plate meshes

1208

After base plate triangles

54043

STL written

53905 triangle

XY Scale

5500

Z Scale

5500

Buildings

1207
```

Model artık yaklaşık

```text
200 x 200 x 20.8 mm
```

ölçüsünde oluşmaktadır.

---

# Yol Sistemi

Bugünkü karar

```text
Road Carving

İPTAL
```

Sebepler

- STL karmaşıklığı
- Boolean problemleri
- Non-manifold oluşumu
- Ticari faydasının düşük olması

Yeni yaklaşım

Yollar;

- görsel detay
- ön izleme
- semantik katman

olarak kullanılacaktır.

---

# Mesh Validator

Geliştirildi.

```text
CORE/atlas_mesh_validator.py
```

Yeni özellikler

- triangle kontrolü
- edge kontrolü
- topology kontrolü
- open edge sayımı
- non-manifold sayımı

---

# Mesh Repair

Yeni modül

```text
CORE/atlas_mesh_repair.py
```

İlk sürüm

- duplicate triangle temizliği
- degenerate triangle temizliği
- vertex snap
- triangle area kontrolü

---

# STL Writer

Yeni işlem

```text
Mesh

↓

Repair

↓

Triangle Filter

↓

ASCII STL
```

Bugünkü temizlik

```text
54043

↓

53905
```

Toplam

```text
138

degenerate triangle
```

otomatik kaldırıldı.

---

# Bambu Studio

Son durum

```text
Open Edges

120

Non Manifold

5
```

Bu hatalar şu anda modeli bozacak seviyede değildir.

Büyük olasılıkla

Base Plate

ile

Final Mesh

birleşiminden kaynaklanmaktadır.

Şimdilik öncelikli değildir.

---

# Ön İzleme Sistemi

ATLAS'ın yeni satış prensibi

## Product Preview Principle

```text
Müşteri

ÖNCE

ne satın alacağını görecek.

STL

DAHA SONRA

oluşturulacak.
```

Bu karar kalıcıdır.

---

# Ön İzleme Katmanları

ATLAS Preview v1

```text
1

Harita

↓

Alan seçimi

-----------------------

2

Gerçek zamanlı

3D WebGL

↓

Döndür

Yakınlaştır

Uzaklaştır

-----------------------

3

Fotogerçekçi Render

↓

Beyaz PLA

Siyah PLA

Mermer PLA

Ahşap PLA

-----------------------

4

Teknik Bilgi

↓

Ürün Boyutu

Alan

Ölçek

Tahmini Baskı Süresi

Filament

Bina Sayısı

Yol Sayısı

Park Sayısı

Su Alanı
```

Bu sistem ATLAS'ın ticari ürün deneyiminin temelidir.

---

# Test Merkezleri

ATLAS'ın standart test şehirleri

```text
1

Paris

Eiffel Tower

--------------------

2

Berlin

Fernsehturm

--------------------

3

Ankara

Anıtkabir
```

Anıtkabir

ATLAS'ın ilk gerçek Landmark ürünü olarak korunacaktır.

---

# Bundan Sonraki Yol Haritası

```text
1

Product Area Engine

↓

Ana Pipeline'a bağlanacak

------------------------

2

Ürün Boyutları

↓

S

M

L

ürün ailesi oluşturulacak

------------------------

3

Eiffel

Berlin

Anıtkabir

↓

karşılaştırmalı testler

------------------------

4

Landmark Engine

↓

özel yapı üretimi

------------------------

5

Building Quality Engine

↓

yükseklik

çatı

ince detay

ölçek optimizasyonu

------------------------

6

Terrain

------------------------

7

Water

------------------------

8

Final Boolean Union

↓

Tek Parça Mesh

↓

Final STL
```

---

# Bugünkü En Büyük Kazanım

Bugün ATLAS tarihinde önemli bir mimari karar alınmıştır.

ATLAS artık

```text
Sabit Ölçekli

Profesyonel

Şehir Modeli

Ürün Motoru
```

mantığıyla geliştirilecektir.

Bundan sonra;

- ölçek değişmeyecek,
- ürün boyutu değişecek,
- kapsanan alan değişecek,
- kalite standardı korunacaktır.

Bu karar ATLAS'ın gelecekteki tüm ürün ailesinin temelini oluşturmaktadır.
## Road Strategy Decision

Primary road strategy is recessed roads.

However, if recessed roads create repeated manifold or boolean problems, ATLAS will switch to surface-applied roads.

Surface roads are acceptable because real-world roads are commonly constructed as material layers above terrain, not only as excavated grooves.

This keeps STL production robust and commercially viable.
# ATLAS_ENGINE_STATUS.md

**Tarih:** 2026-07-07

---

# ATLAS ENGINE - DURUM RAPORU

## Genel Durum

Bugün itibarıyla ATLAS Engine, yalnızca düz tabanlı şehir modelleri üreten bir sistem olmaktan çıkmış, **gerçek arazi (terrain) destekli şehir modeli üretebilen** bir motora dönüşmüştür.

Bu, projenin en önemli kilometre taşlarından biridir.

---

# Bugün Tamamlanan Çalışmalar

## 1. SRTM Terrain Sistemi

Tamamlandı.

Özellikler:

- SRTM HGT dosyaları okunuyor.
- Gerçek arazi yükseklikleri hesaplanıyor.
- Terrain Grid oluşturuluyor.
- Terrain Mesh oluşturuluyor.
- Closed Terrain Slab başarıyla üretiliyor.

---

## 2. Terrain STL

Başarıyla üretildi.

Son test:

- Grid: 25 × 25
- Min yükseklik: 862 m
- Max yükseklik: 917 m
- Delta: 55 m

Modelde karşılığı:

Yaklaşık **10 mm** gerçek arazi farkı.

---

## 3. Terrain + Şehir Entegrasyonu

Başarıyla tamamlandı.

Artık tek STL içerisinde:

- Terrain
- Buildings

birlikte üretilebiliyor.

Son test:

- Mesh sayısı: 486
- Triangle sayısı: 8668
- Buildings: 485

---

## 4. STL

Başarıyla oluşturuldu.

```
OUTPUT/STL/latest.stl
```

Bambu Studio sorunsuz açıyor.

Open Edge problemi bulunmuyor.

---

# Çalışan Sistemler

✔ Local OSM Reader

✔ Coordinate Engine

✔ Scale Engine

✔ Scene Builder

✔ Mesh Builder

✔ Scene Normalizer

✔ Scene Fitter

✔ Terrain Provider

✔ Terrain Mesh Generator

✔ Terrain Height Sampler (ilk sürüm)

✔ STL Export

---

# Bugün Çözülen Problemler

## Problem 1

Terrain ile şehir aynı STL içinde üretilemiyordu.

### Durum

Çözüldü.

---

## Problem 2

Terrain modeli oluşturulamıyordu.

### Durum

Çözüldü.

---

## Problem 3

Binalar terrain üzerinde görünmüyordu.

### Durum

Çözüldü.

---

## Problem 4

Terrain ölçeği

XY = 5500

Z = 5500

olarak sabitlendi.

Bu karar kalıcıdır.

---

# Bugün Tespit Edilen Problemler

## Problem A

Bina tabanı tamamen düz.

Terrain ise eğimli.

Sonuç:

Bazı binalar

- tek noktadan temas ediyor.
- bazı köşeleri havada kalıyor.

---

## Problem B

Sivri tepe problemi

Örneğin:

Anıtkabir

Eğer bina sivri bir tepeye oturursa:

```
      ███████

        ▲
```

yalnızca tek noktadan temas ediyor.

Bu gerçekçi değil.

---

## Problem C

Büyük binalar

Centroid yöntemi büyük binalarda yeterli değil.

Bina genişledikçe hata büyüyor.

---

# Teknik Değerlendirme

Terrain sistemi doğru çalışıyor.

Sorun terrain değildir.

Sorun bina ile terrain arasındaki fiziksel temastır.

---

# Kararlaştırılan Yol Haritası

## Aşama 1

Embed Sistemi

Bina yaklaşık

```
0.30–0.50 mm
```

terrain içine gömülecek.

Amaç:

- boşluk bırakmamak
- baskıyı güçlendirmek

---

## Aşama 2

Foundation / Platform Sistemi

Belirli büyüklüğün üzerindeki binalar için:

- bina footprint'i hesaplanacak
- çevresinde düz platform oluşturulacak
- platform terrain'e yumuşak geçecek

Bu özellik tüm büyük yapılar için geçerli olacak.

Sadece Anıtkabir için olmayacak.

---

## Aşama 3

Landmark Engine

Normal bina motorundan tamamen bağımsız olacak.

Özel üretilecek yapılar:

- Anıtkabir
- Ayasofya
- Süleymaniye
- Eiffel Tower
- Brandenburg Gate
- Colosseum
- Big Ben
- vb.

---

# Anıtkabir Kararı

İlk gerçek ATLAS modeli

**Anıtkabir**

olmaya devam edecektir.

Ancak önce genel motor tamamlanacaktır.

Anıtkabir için özel kod en son yazılacaktır.

---

# Gelecek Geliştirmeler

## Terrain

- Bilinear Interpolation
- Footprint Sampling
- Foundation Builder

---

## Roads

Henüz terrain'e bağlanmadı.

Sonraki aşamalarda:

- gerçek eğim
- köprü
- viyadük
- tünel

desteklenecek.

---

## Trees

Henüz eklenmedi.

Terrain yüksekliğini kullanacak.

---

## Water

Henüz eklenmedi.

Terrain'e oyularak üretilecek.

---

## POI

Henüz eklenmedi.

Terrain referanslı olacak.

---

# Ürün Kararları

Standart ölçek

```
XY = 1 : 5500

Z = 1 : 5500
```

Bu karar korunacaktır.

---

# Premium Ürün Kararı

Çok yüksek yapılar

(Burj Khalifa vb.)

için

minimum ürün boyutu

```
60 × 60 cm
```

olarak düşünülmektedir.

Bu ürünlerde yaklaşık

```
3.3 km × 3.3 km
```

alan modellenebilecektir.

---

# Genel Mimari

```
OSM

↓

Reader

↓

Coordinate Engine

↓

Scale Engine

↓

Terrain Provider

↓

Terrain Mesh

↓

Terrain Height Sampler

↓

Scene Builder

↓

Building Builder

↓

Foundation Engine (Planlandı)

↓

Landmark Engine (Planlandı)

↓

STL Export
```

---

# Açık Görevler

- [x] Terrain Mesh
- [x] Terrain STL
- [x] Terrain + Building
- [ ] Embed Sistemi
- [ ] Foundation Engine
- [ ] Bilinear Interpolation
- [ ] Footprint Sampling
- [ ] Road Terrain
- [ ] Water
- [ ] Trees
- [ ] POI
- [ ] Landmark Engine

---

# Genel Değerlendirme

Bugünkü çalışma ile birlikte ATLAS projesi önemli bir mimari eşiği geçmiştir.

Artık sistem:

- gerçek arazi üretebilmektedir,
- arazi üzerinde şehir oluşturabilmektedir,
- tek STL içerisinde terrain ve bina üretebilmektedir,
- 3D yazıcıya gönderilebilir modeller oluşturabilmektedir.

Bir sonraki ana hedef, **bina ile arazi arasındaki fiziksel birleşimi profesyonel seviyeye çıkarmaktır.**

Bu amaç doğrultusunda öncelik sırası:

1. Embed Sistemi
2. Foundation Engine
3. Bilinear Interpolation
4. Footprint Sampling
5. Landmark Engine

Bu aşamalar tamamlandığında ATLAS, yalnızca OSM verisini STL'ye dönüştüren bir araç olmaktan çıkıp, profesyonel topoğrafik şehir modeli üreten bir platform haline gelecektir.