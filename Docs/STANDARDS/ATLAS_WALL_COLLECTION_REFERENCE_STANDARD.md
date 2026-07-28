# ATLAS WALL COLLECTION — REFERENCE STANDARD

## Belgenin amacı

Bu belge, ATLAS My Life Map Wall Collection ürün ailesinde kullanılacak ortak ürün standardını tanımlar.

Bu standart:

- Köln referans ürününden çıkarılmıştır.
- Gelecekteki bütün Wall Collection lokasyonlarına uygulanacaktır.
- Lokasyona özel koordinat, etiket metni, PBF yolu ve sahne kararlarını içermez.
- Ürün bazlı bilgiler `Docs/PRODUCTS/` altındaki referans belgelerinde tutulur.

Köln fiziksel baskıyla doğrulanmadan bu standart tamamen kilitlenmiş sayılmaz.

---

## Ürün kimliği

Ürün ailesi:

ATLAS My Life Map Wall Collection

Temel ürün fikri:

Every important memory has a location.

Ürün tipi:

- Duvara asılabilir
- Çerçeve dahil tek ürün
- 3B şehir veya lokasyon modeli
- Etiket plakalı
- Çok renkli FDM baskıya uygun
- Koleksiyon mantığıyla çoğaltılabilir
- Premium fiziksel görünüm hedefli

---

## Fiziksel dış ölçüler

Standart dış ürün ölçüsü:

150 × 150 mm

Standart şehir açıklığı:

134 × 134 mm

Standart çerçeve genişliği:

8 mm

Standart çerçeve derinliği:

6 mm

Referans ölçek:

1:5500

Ürün dış ölçüsü, lokasyon değiştiğinde varsayılan olarak değiştirilmez.

Lokasyona göre içerik kırpımı ve merkez koordinatı değişebilir; fiziksel ürün standardı korunur.

---

## Çerçeve standardı

Çerçeve:

- Ürünün ayrılmaz parçasıdır.
- Final ürün geometrisine dahildir.
- Dış ürün sınırını oluşturur.
- Şehir modeliyle fiziksel olarak uyumlu olmalıdır.
- Duvara asılabilir yapıyı desteklemelidir.
- Premium ve temiz bir dış siluet oluşturmalıdır.

Varsayılan fiziksel sınıf:

Frame + Label Plate

Varsayılan renk:

Siyah veya antrasit

---

## Şehir alanı standardı

Şehir modeli çerçevenin içindeki 134 × 134 mm açıklığa yerleştirilir.

Şehir alanı şu bileşenleri içerebilir:

- terrain
- roads
- parks
- trees
- buildings
- building roofs
- water
- landmarks

Bütün geometriler:

- baskıya uygun olmalı,
- fiziksel olarak anlamlı minimum kalınlıklara sahip olmalı,
- görünür çakışma oluşturmamalı,
- final STL içinde doğru konumlanmalıdır.

---

## Etiket plakası standardı

Standart etiket plakası:

- Genişlik: 118 mm
- Yükseklik: 11 mm
- Derinlik: 1.2 mm
- Alt çerçeve bandına gömme: 5 mm

Etiket plakası:

- Çerçeve sistemiyle görsel olarak bütünleşmelidir.
- Alt çerçeve bandına 5 mm gömülmelidir.
- Şehir geometrisinin küçültülmesini veya yukarı taşınmasını gerektirmemelidir.
- Harita alanına sınırlı ve kontrollü biçimde taşabilir.
- Final ürün STL dosyasına dahil edilmelidir.
- Lokasyon adını ve gerekli ikincil bilgiyi taşımalıdır.
- Fiziksel renk sınıfı olarak çerçeveyle aynı grupta değerlendirilir.
- Bu geometri Wall Collection v1 dijital etiket standardıdır.
- Fiziksel baskı doğrulaması olmadan yalnız ekran görünümüne dayalı ek mikro ayar yapılmaz.

---

## Yazı standardı

Varsayılan font:

DejaVu Sans Bold

Primary nominal yazı yüksekliği:

4.2 mm

Secondary nominal yazı yüksekliği:

2.8 mm

Maksimum yazı genişliği:

108 mm

Yazı kabartma derinliği:

0.6 mm

Satır aralığı:

1.0 mm

Yazı sistemi:

- Etiket plakasına sığmalıdır.
- Otomatik genişlik kontrolü uygulamalıdır.
- Çok uzun lokasyon adlarında okunabilirliği korumalıdır.
- Baskıda kaybolmayacak fiziksel kalınlığa sahip olmalıdır.
- Varsayılan olarak Building Walls ile aynı fiziksel renk sınıfına dahildir.


---

## Fiziksel renk standardı

Hedef baskı sistemi:

Bambu Lab P2S Combo

Bir üründe kullanılacak toplam fiziksel filament rengi:

En fazla 5

Sabit renk sınıfları:

1. Frame + Label Plate
   Siyah veya antrasit

2. Terrain + Roads
   Sıcak taş, kum veya benzeri nötr zemin tonu

3. Building Walls + Label Text
   Kırık beyaz veya açık mimari ton

4. Building Roofs
   Kırmızı veya terracotta

Çatı rengi bütün Wall Collection ürünlerinde kırmızı veya terracotta kalmalıdır.

---

## Dinamik beşinci renk

Beşinci fiziksel renk, sahnenin karakterine göre belirlenir.

Kara ve yeşil alan ağırlıklı ürün:

Yeşil

Bu sınıfa dahil edilebilecek öğeler:

- parks
- trees
- grass
- green areas

Su ağırlıklı ürün:

Mavi

Bu sınıfa dahil edilebilecek öğeler:

- sea
- river
- lake
- canal
- pool
- harbour water

Aynı üründe hem yeşil hem mavi kullanılması toplam fiziksel renk sayısını beşin üzerine çıkarıyorsa ikisinden yalnızca biri seçilir.

Karar, ürün referans belgesinde açıkça kaydedilmelidir.

---

## Dijital preview standardı

Dijital preview fiziksel baskıdan daha fazla material sınıfı kullanabilir.

Desteklenen temel preview sınıfları:

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

Preview çıktıları:

- OBJ
- MTL
- PNG

Dijital preview içindeki material sayısı, fiziksel baskıdaki filament sayısı değildir.

Preview amacı:

- geometriyi incelemek,
- renk ayrımlarını değerlendirmek,
- çatı ve duvar ayrımını görmek,
- terrain ve yol okunabilirliğini kontrol etmek,
- sahne dengesini değerlendirmek,
- gerçek baskı öncesi görsel hata tespit etmektir.

---

## STL export standardı

Final ürün tek STL dosyası olarak dışa aktarılır.

Final STL şu bileşenleri içermelidir:

- frame
- city
- label plate
- label text

STL formatı material veya renk grubu taşımaz.

Fiziksel renk ataması Bambu Studio içinde yapılır.

STL:

- doğru ölçekte olmalı,
- ürün merkezine göre doğru konumlanmalı,
- final ürün bileşenlerini eksiksiz içermeli,
- geçersiz veya kayıp geometri taşımamalıdır.

---

## Baskıya uygun geometri standardı

Geometri:

- görünür yüzey kaybı oluşturmamalı,
- sıfır alanlı üçgen içermemeli,
- açık kenar oluşturmamalı,
- non-manifold bağlantı üretmemeli,
- gereksiz üst üste binme taşımamalı,
- baskıda kaybolacak kadar ince olmamalıdır.

Bileşenler arasında:

- z-fighting olmamalı,
- fiziksel bağlantı korunmalı,
- renk ayrımı yapılabilecek net sınırlar bulunmalı,
- Bambu Studio içinde seçim ve boyama uygulanabilir olmalıdır.

---

## Bambu Studio doğrulama standardı

Her yeni referans ürün kilitlenmeden önce Bambu Studio içinde açılmalıdır.

Kontrol edilecekler:

1. STL doğru açılıyor mu?
2. Dış ölçü 150 × 150 mm olarak korunuyor mu?
3. Model doğru yönlendirilmiş mi?
4. Bütün ürün bileşenleri mevcut mu?
5. Beş fiziksel renk atanabiliyor mu?
6. Çatı sınıfı kırmızı veya terracotta olarak ayrılabiliyor mu?
7. Label text okunabilir mi?
8. İnce parçalar baskıda korunuyor mu?
9. Baskı süresi kabul edilebilir mi?
10. Filament tüketimi kabul edilebilir mi?
11. Renk değişim sayısı makul mü?
12. Destek ihtiyacı var mı?
13. Tabla yerleşimi doğru mu?
14. Dilimleme hatası veya boş katman var mı?

---

## Gerçek baskı doğrulama standardı

Bir ürün yalnızca dijital preview ve STL kontrolüyle nihai referans sayılmaz.

Gerçek test baskısında kontrol edilecekler:

- çerçevenin doğruluğu,
- ürünün duvarda duruşu,
- terrain okunabilirliği,
- yolların seçilebilirliği,
- bina duvarlarının görünürlüğü,
- çatıların okunabilirliği,
- ağaç ve park detaylarının yeterliliği,
- label plate hizası,
- label text okunabilirliği,
- renk uyumu,
- yüzey kalitesi,
- katman izleri,
- baskı sonrası temizlik ihtiyacı,
- fiziksel sağlamlık,
- premium ürün algısı.

Gerekli revizyonlardan sonra test baskısı tekrarlanmalıdır.

---

## Standart kilitleme kuralı

Bu standart, Köln Pädagogische Fakultät referans ürünü:

- dijital olarak doğrulandığında,
- Bambu Studio içinde doğrulandığında,
- gerçek baskıyla doğrulandığında,
- gerekli revizyonları tamamlandığında

kilitlenmiş referans standardı haline gelir.

Kilitlendikten sonra değişiklikler:

- gerekçeli olmalı,
- ilgili testlerle doğrulanmalı,
- standardın sürüm kaydına eklenmeli,
- mevcut ürünlere etkisi değerlendirilmelidir.

---

## Lokasyona özel kararlar

Aşağıdaki bilgiler bu genel standart dosyasına yazılmaz:

- merkez koordinatı,
- PBF yolu,
- lokasyon adı,
- etiket metni,
- yerel sahne kırpımı,
- beşinci renk seçimi,
- özel landmark kararı,
- yerel geometri istisnası,
- ürün bazlı preview sonucu,
- ürün bazlı baskı sonucu.

Bunlar ilgili ürün belgesinde tutulur:

Docs/PRODUCTS/<PRODUCT_REFERENCE>.md

---

## Ürün çoğaltma sırası

İlk referans:

1. Köln Pädagogische Fakultät

Köln standardı kilitlendikten sonra aynı sistem sırayla diğer lokasyonlara uygulanır.

Her yeni lokasyon:

- aynı dış ölçüyü,
- aynı çerçeve standardını,
- aynı etiket sistemini,
- aynı renk sınıfı mantığını,
- aynı STL doğrulamasını,
- aynı gerçek baskı doğrulamasını

kullanmalıdır.

---

## Mevcut durum

Bu belge Köln referans ürününden çıkarılan mevcut standardı kaydeder.

Durum:

Taslak referans standardı

Henüz eksik doğrulamalar:

- label plate preview entegrasyonu kararı,
- label text preview entegrasyonu kararı,
- nihai Köln STL üretimi,
- Bambu Studio renk ataması,
- baskı süresi ölçümü,
- filament tüketimi ölçümü,
- gerçek test baskısı,
- baskı sonrası revizyon,
- standardın kilitlenmesi.

---

## Sıradaki ilgili belge

Docs/PRODUCTS/KOELN_PAEDAGOGISCHE_FAKULTAET_REFERENCE.md

Bu belge yalnızca Köln ürününe özgü teknik, görsel ve baskı kararlarını içerecektir.
