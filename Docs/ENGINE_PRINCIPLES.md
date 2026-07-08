# ATLAS ENGINE PRINCIPLES

Version: 1.0

Bu belge ATLAS Engine'in değişmeyecek temel mühendislik ilkelerini tanımlar.

Kod değişebilir.

Algoritmalar değişebilir.

Teknolojiler değişebilir.

Ancak bu prensipler korunacaktır.

---

# PR-001

## User Selects Area

ATLAS hiçbir zaman bina seçmez.

ATLAS'ın temel girdisi;

- koordinat
- merkez nokta
- bbox
- kullanıcı tarafından seçilen alan

olacaktır.

Binalar, yollar, parklar, ağaçlar ve diğer nesneler bu alanın içeriğidir.

Ürün, seçilen alandır.

---

# PR-002

## Area First Architecture

ATLAS bir "Area Engine"dir.

Bir "Building Engine" değildir.

Tüm hesaplamalar;

önce alan,

sonra alan içindeki nesneler

mantığı ile yapılacaktır.

---

# PR-003

## One Responsibility

Her modül yalnızca tek iş yapmalıdır.

Örnek:

AtlasAreaSelector

↓

sadece bbox üretir.

AtlasScaleEngine

↓

sadece ölçek hesaplar.

AtlasCoordinateEngine

↓

sadece koordinat dönüştürür.

AtlasMeshBuilder

↓

sadece mesh üretir.

---

# PR-004

## Global Coordinate System

Bütün nesneler aynı dünya koordinat sistemini kullanacaktır.

Hiçbir modül kendi lokal koordinat sistemini oluşturamaz.

---

# PR-005

## Automatic Scaling

Hiçbir ürün ölçüsü kod içine sabit yazılmayacaktır.

Örnek:

❌ xy_scale = 15000

Yerine;

AtlasScaleEngine

otomatik hesap yapacaktır.

---

# PR-006

## Product Independent

ATLAS;

140x140

180x180

260x260

520x520

gibi farklı ürün boyutlarını

aynı motor ile üretebilmelidir.

---

# PR-007

## Modular Engines

Yeni özellikler mevcut kodu bozmayacaktır.

Yeni modüller;

Road Engine

Water Engine

DEM Engine

Tree Engine

Landmark Engine

gibi sisteme eklenebilir olacaktır.

---

# PR-008

## Printable Geometry

Üretilen her mesh;

- manifold
- closed
- printable

olmalıdır.

3D yazıcı tarafından doğrudan basılabilir olmalıdır.

---

# PR-009

## Commercial Quality

ATLAS bir araştırma projesi değildir.

ATLAS ticari üretim motorudur.

Her karar;

ölçeklenebilirlik,

bakım kolaylığı,

ürün kalitesi,

performans

kriterlerine göre alınacaktır.

---

# PR-010

## Reproducibility

Aynı koordinatlar,

aynı ayarlar,

aynı veri kaynağı

kullanıldığında,

ATLAS her zaman aynı modeli üretmelidir.

Deterministik üretim zorunludur.

---

# Son Güncelleme

2026-07-05

ATLAS, "Building Selection" yaklaşımını terk etmiş ve resmen "Area-First Architecture" yaklaşımına geçmiştir.

Bu karar, projenin temel mimari prensibi olarak kabul edilmiştir.
---

# PR-012

## Scene First Architecture

ATLAS Engine'in temel çıktısı STL değildir.

ATLAS önce bir **AtlasScene** üretir.

AtlasScene daha sonra farklı çıktı formatlarına dönüştürülebilir:

- STL
- 3MF
- OBJ
- GLTF
- Web Preview

Bu nedenle STL yalnızca bir export formatıdır.

Ürün nesnesi:

**AtlasScene**

olarak kabul edilir.

Bu karar, ileride çok renkli baskı, web önizleme, farklı yazıcı formatları ve profesyonel üretim akışları için temel mimari prensip olarak korunacaktır.
---

# PR-013

## Data Fusion Before Geometry

ATLAS hiçbir dış veri kaynağını doğrudan doğru kabul etmez.

OSM, belediye GIS verileri, GeoJSON, Shapefile, kullanıcı yüklemeleri, tarihsel arşivler veya gelecekte desteklenecek diğer veri kaynakları önce bir **Data Fusion** katmanından geçirilir.

Bu katmanın görevi:

- aynı nesnenin farklı kaynaklardaki karşılıklarını eşleştirmek,
- çelişkili verileri tespit etmek,
- kaynak güvenilirliğini değerlendirmek,
- zaman bağlamını dikkate almak,
- tek ve tutarlı bir AtlasScene oluşturmaktır.

Geometri üretimi yalnızca Data Fusion işlemi tamamlandıktan sonra başlar.

(deegisik bir proje
# PR-014

## Place-Centric Processing

ATLAS'ın amacı insanları analiz etmek değildir.

ATLAS;

- mekânı,
- yapıları,
- doğal çevreyi,
- şehir dokusunu,
- tarihsel çevreyi

anlamak ve yeniden oluşturmaya odaklanır.

Fotoğraflarda bulunan insanlar sistemin analiz hedefi değildir.

Fotoğraflar yalnızca mekânsal bilginin çıkarılması amacıyla değerlendirilir.

ATLAS hiçbir zaman yüz tanıma, kişi kimliği belirleme veya biyometrik analiz amacıyla geliştirilmeyecektir.)
# PR-015

## Recessed Road Principle

ATLAS’ta yollar varsayılan olarak çıkıntılı değil, gömülü/oyuk yüzey olarak tasarlanacaktır.

Sebep:

- Gerçek şehir dokusunda yollar zeminle aynı veya zeminden hafif düşük algılanır.
- Kaldırım etkisi ayrıca üretilmeden doğal olarak ortaya çıkar.
- Malzeme tüketimi azalır.
- Baskı süresi düşer.
- Uzun vadeli üretimde ekonomik avantaj sağlar.

Yaklaşık hesap:

25x25 cm ürünlerde gömülü yol yaklaşımı, 1000 baskıda yaklaşık 8–9 kg filament ve toplamda yaklaşık 300 € civarı üretim avantajı sağlayabilir.