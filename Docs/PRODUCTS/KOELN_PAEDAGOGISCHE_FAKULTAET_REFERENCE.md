# KÖLN PÄDAGOGISCHE FAKULTÄT — PRODUCT REFERENCE

## Belgenin amacı

Bu belge, ATLAS My Life Map Wall Collection ürün ailesinin ilk premium referans ürünü olan Köln Pädagogische Fakultät modeline özgü teknik, görsel ve üretim kararlarını kaydeder.

Genel Wall Collection kuralları şu belgede tutulur:

Docs/STANDARDS/ATLAS_WALL_COLLECTION_REFERENCE_STANDARD.md

Bu belgede yalnızca Köln ürününe özgü bilgiler bulunmalıdır.

---

## Ürün rolü

Ürün ailesi:

ATLAS My Life Map Wall Collection

Referans ürün:

Köln Pädagogische Fakultät

Durum:

İlk premium referans ürün

Temel kural:

Köln ürünü tamamlanmadan ikinci lokasyona geçilmez.

Köln ürünü:

- dijital olarak doğrulanmalı,
- Bambu Studio içinde doğrulanmalı,
- gerçek baskıyla test edilmeli,
- gerekli revizyonları tamamlamalı,
- ardından ürün standardı kilitlenmelidir.

---

## Lokasyon kimliği

Ürün adı:

Köln Pädagogische Fakultät

Merkez koordinatı:

- Enlem: 50.93428235
- Boylam: 6.91972655

Referans ölçek:

1:5500

OSM fixture:

Data/OSM/koeln-paedagogische-fakultaet-test.osm.pbf

---

## Fiziksel ürün ölçüleri

Dış ölçü:

150 × 150 mm

Şehir açıklığı:

134 × 134 mm

Çerçeve genişliği:

8 mm

Çerçeve derinliği:

6 mm

Ürün:

- çerçeve dahil tek fiziksel ürün olacaktır,
- duvara asılabilir olacaktır,
- premium görünüm hedefleyecektir,
- Wall Collection serisinin sonraki ürünleri için ölçü referansı olacaktır.

---

## Etiket plakası

Etiket plakası ölçüsü:

118 × 8 × 1.2 mm

Etiket plakası:

- çerçeveyle aynı fiziksel renk sınıfındadır,
- final STL içine dahil edilir,
- Köln ürününün lokasyon bilgisini taşır,
- şehir modelinin okunabilirliğini engellememelidir.

---

## Yazı sistemi

Font:

DejaVu Sans Bold

Primary nominal yükseklik:

4.2 mm

Secondary nominal yükseklik:

2.8 mm

Maksimum yazı genişliği:

108 mm

Yazı kabartma derinliği:

0.6 mm

Satır aralığı:

1.0 mm

Yazı sınıfı:

Building Walls + Label Text

Etiket metninin kesin içeriği, final preview ve fiziksel okunabilirlik kontrolü sırasında doğrulanacaktır.

---

## Üretim zinciri

Köln ürünü şu üretim hattını kullanır:

OSM / SRTM
→ terrain
→ roads
→ parks
→ trees
→ buildings
→ building roofs
→ frame
→ label plate
→ label text
→ single STL

Final STL içinde:

- frame
- city
- label plate
- label text

bulunmalıdır.

---

## İlgili temel modüller

Wall Collection ürün oluşturucu:

CORE/atlas_wall_collection_product_builder.py

Çerçeve tanımı:

CORE/atlas_wall_frame_spec.py

Çerçeve mesher:

CORE/atlas_wall_frame_mesher.py

Etiket plakası tanımı:

CORE/atlas_label_plate_spec.py

Etiket plakası mesher:

CORE/atlas_label_plate_mesher.py

Yazı tanımı:

CORE/atlas_label_text_spec.py

Yazı mesher:

CORE/atlas_label_text_mesher.py

STL exporter:

CORE/atlas_wall_collection_stl_exporter.py

Renkli preview renderer:

CORE/atlas_product_color_preview_renderer.py

Preview material profili:

CORE/atlas_product_preview_material_profile.py

OBJ exporter:

CORE/atlas_product_color_preview_obj_exporter.py


---

## Fiziksel renk kararı

Köln ürünü kara ve yeşil alan ağırlıklı bir sahnedir.

Bu nedenle dinamik beşinci renk:

Yeşil

olarak seçilir.

Köln için hedef fiziksel renk sınıfları:

1. Frame + Label Plate  
   Siyah veya antrasit

2. Terrain + Roads  
   Sıcak taş veya kum tonu

3. Building Walls + Label Text  
   Kırık beyaz

4. Building Roofs  
   Kırmızı veya terracotta

5. Parks + Trees + Green Areas  
   Yeşil

Çatılar kırmızı veya terracotta kalacaktır.

Köln ürününde mavi fiziksel filament sınıfı kullanılmayacaktır.

---

## Dijital preview kararı

Dijital preview şu sınıfları ayrı gösterebilir:

- frame
- terrain
- roads
- parks
- trees
- building walls
- building roofs
- water

Dijital preview içindeki material sayısı fiziksel filament sayısını belirlemez.

Köln preview kontrolünde özellikle şu noktalar incelenmelidir:

- Çerçeve ve şehir alanı hizası
- Terrain okunabilirliği
- Yol görünürlüğü
- Yeşil alanların yeterli görünmesi
- Ağaç yoğunluğu
- Bina duvarı ve çatı ayrımı
- Kırmızı çatıların sahne içindeki dengesi
- Ana kampüs yapılarının okunabilirliği
- Label plate konumu
- Label text okunabilirliği
- Premium ürün algısı

---

## Label preview durumu

Label plate ve label text bileşenleri preview ve ürün oluşturma
zincirine entegre edilmiştir.

Doğrulanan kurallar:

- Etiket plakası tamamen alt çerçeve bandının içinde kalır.
- Köln ürününde 8 mm çerçeve bandına uygun 8 mm plaka kullanılır.
- Yazı ve semboller plakanın ön yüzüne ayrı malzeme sınıfıyla yerleştirilir.
- Etiketli ve etiketsiz ürün varyantları ayrı üretilebilir.

---

## Final STL kararı

Köln ürünü tek final STL olarak dışa aktarılacaktır.

Final STL şu bileşenleri içermelidir:

- frame
- city
- label plate
- label text

STL içinde fiziksel renk veya material bilgisi bulunmaz.

Renk ataması Bambu Studio içinde yapılır.

---

## Bambu Studio doğrulama kaydı

Durum:

Henüz yapılmadı

Kontrol edilecek alanlar:

- STL hatasız açılıyor mu?
- Ürün ölçüsü 150 × 150 mm mi?
- Model doğru yönde mi?
- Frame mevcut mu?
- City geometry eksiksiz mi?
- Label plate mevcut mu?
- Label text mevcut mu?
- Beş renk atanabiliyor mu?
- Roof geometry ayrı olarak kırmızıya boyanabiliyor mu?
- Green areas tek fiziksel renk sınıfında yönetilebiliyor mu?
- İnce yollar baskıda korunuyor mu?
- Yazı okunabilir mi?
- Destek gerekiyor mu?
- Baskı süresi nedir?
- Filament tüketimi nedir?
- Renk değişim sayısı nedir?
- Dilimleme hatası var mı?

Sonuçlar bu belgeye yazılmalıdır.

---

## Gerçek baskı doğrulama kaydı

Durum:

Henüz yapılmadı

Gerçek baskıda incelenecekler:

- Çerçeve doğruluğu
- Duvara asılabilirlik
- Genel sağlamlık
- Terrain yüzeyi
- Yol okunabilirliği
- Bina duvarları
- Kırmızı çatılar
- Ağaç ve park görünürlüğü
- Label plate hizası
- Label text okunabilirliği
- Renk dengesi
- Katman kalitesi
- Yüzey temizliği
- Premium ürün algısı
- Baskı sonrası düzeltme ihtiyacı

Baskı sonucu fotoğraflanmalı ve gerekli revizyonlar bu belgede kaydedilmelidir.

---

## Tamamlanma ölçütleri

Köln ürünü tamamlanmış sayılmadan önce:

1. Ürün geometrisi doğrulanmalı.
2. Preview tamamlanmalı.
3. Label plate preview kararı uygulanmalı.
4. Label text preview kararı uygulanmalı.
5. Final STL oluşturulmalı.
6. STL Bambu Studio içinde açılmalı.
7. Beş fiziksel renk atanmalı.
8. Baskı süresi kaydedilmeli.
9. Filament tüketimi kaydedilmeli.
10. Renk değişim sayısı kaydedilmeli.
11. Gerçek test baskısı yapılmalı.
12. Baskı sonucu değerlendirilmelidir.
13. Gerekli revizyonlar tamamlanmalıdır.
14. Genel Wall Collection standardı kilitlenmelidir.

---

## Sonraki lokasyon sırası

Köln tamamlandıktan sonra ilk öncelikli lokasyon:

Dalyan

Dalyan’ın öncelik nedeni:

Hediyeyi alacak kişinin tatilde özellikle sevdiği yer olması.

Dalyan’dan sonraki planlanan lokasyon:

İstanbul

Köln tamamlanmadan Dalyan üretimine başlanmaz.

---

## Ürün durumu

Mevcut durum:

Aktif referans geliştirme

Tamamlananlar:

- Ürün dış ölçü standardı belirlendi.
- Çerçeve standardı belirlendi.
- Etiket plakası standardı belirlendi.
- Yazı standardı belirlendi.
- Beş renk sistemi belirlendi.
- Çatı rengi kırmızı veya terracotta olarak kilitlendi.
- Köln için dinamik beşinci renk yeşil olarak seçildi.
- STL bileşenleri tanımlandı.
- Preview bileşenleri tanımlandı.

Tamamlanan ek üretim aşamaları:

- Label plate preview entegrasyonu
- Label text preview entegrasyonu
- Çok renkli STL katman ayrımı
- Bambu Studio dilimleme doğrulaması
- AMS renk eşlemesi
- Köln `.3mf` proje dosyasının kaydedilmesi

Henüz tamamlanmayanlar:

- Nihai filamentlerle son fiziksel referans baskı
- Baskı sonrası gerekirse son revizyon
- Fiziksel doğrulama sonrasında referans standardının nihai kilitlenmesi

---

## Sıradaki tek teknik işlem

Nihai filamentler geldikten sonra kayıtlı Köln `.3mf` projesi
Bambu Studio'da açılmalı, gerçek AMS eşlemesi son kez doğrulanmalı
ve fiziksel referans baskı alınmalıdır.
