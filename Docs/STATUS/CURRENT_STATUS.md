# ATLAS_ENGINE — CURRENT STATUS

## Belgenin görevi

Bu dosya, ATLAS_ENGINE geliştirmesinin kesin güncel durumunu ve sıradaki tek işlemi tanımlar.

Yeni bir çalışma oturumunda önce:

- Docs/START_HERE.md
- Docs/STATUS/CURRENT_STATUS.md

okunmalıdır.

---

## Güncelleme tarihi

2026-07-28

---

## Aktif ticari ürün

ATLAS My Life Map Wall Collection

Temel fikir:

Every important memory has a location.

---

## Aktif referans ürün

Köln — Pädagogische Fakultät

Kurallar:

- İlk referans ürün Köln'dür.
- Köln tamamlanmadan Bonn'a geçilmez.
- Köln gerçek baskı ile doğrulanmadan standart kilitlenmez.

Sonraki ürün:

Bonn

---

## Onaylanmış ürün standardı

- Dış ölçü: 150 × 150 mm
- Şehir açıklığı: 134 × 134 mm
- Çerçeve: 8 mm
- Çerçeve derinliği: 6 mm
- Referans ölçek: 1:5500

Etiket plakası:

- 118 × 11 × 1.2 mm
- Alt çerçeve bandına gömme: 5 mm

Yazı:

- Font: DejaVu Sans Bold
- Primary: 4.2 mm
- Secondary: 2.8 mm
- Yazı derinliği: 0.6 mm
- Maksimum genişlik: 108 mm

---

## Fiziksel renk standardı

Hedef yazıcı:

Bambu Lab P2S Combo

Toplam fiziksel renk:

En fazla 5

Köln Premium V1 kilitli paleti:

1. Beyaz
   - frame
   - terrain
   - roads
   - building walls
   - label text
2. Kırmızı
   - building roofs
   - ileride seçili vurgu binası
3. Yeşil
   - parks
   - trees
4. Siyah
   - label plate
   - ileride plaka simgesi
5. Mavi
   - water

Köln PBF sahnesinde su mesh'i bulunmadığı için mevcut gerçek paket dört STL üretmektedir:

- white
- red
- green
- black

Su bulunan ürünlerde blue STL otomatik olarak eklenir.


---

## Mevcut üretim zinciri

OSM / SRTM
→ terrain
→ roads
→ parks
→ trees
→ buildings
→ semantic wall / roof separation
→ frame
→ hidden keyhole hanger
→ label plate
→ label text
→ combined STL
→ aligned multicolor STL package

Üretim çıktıları:

1. Birleşik referans STL
2. Aynı koordinat sisteminde renk bazlı ayrı STL dosyaları

Köln gerçek çok renkli paket çıktıları:

- `koeln_paedagogische_fakultaet_150mm__white.stl`
- `koeln_paedagogische_fakultaet_150mm__red.stl`
- `koeln_paedagogische_fakultaet_150mm__green.stl`
- `koeln_paedagogische_fakultaet_150mm__black.stl`

Çıktı klasörü:

`OUTPUT/STL/koeln_paedagogische_fakultaet_multicolor/`

---

## Dijital preview durumu

Preview katmanları:

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

Desteklenen çıktılar:

- PNG renk karşılaştırma preview
- OBJ interaktif geometri preview
- MTL material tanımları

Etiket preview zinciri tamamlandı ve ilgili regresyon paketi `49 passed` sonucu verdi.

---

## Kilitlenen etiket tasarımı

Wall Collection v1 etiket geometrisi dijital olarak kilitlenmiştir:

- Şehir geometrisi küçültülmez veya yukarı taşınmaz.
- Etiket plakası alt çerçeve bandına gömülür.
- Plaka ölçüsü: 118 × 11 × 1.2 mm
- Çerçeve gömme miktarı: 5 mm
- Yazı kabartması: 0.6 mm
- Primary yazı yüksekliği: 4.2 mm
- Secondary yazı yüksekliği: 2.8 mm
- Ekran görüntüsüne dayanarak daha fazla mikro ayar yapılmaz.
- Sonraki revizyon yalnız fiziksel baskı veya Bambu Studio doğrulamasına dayanır.

Bu kilit yalnız etiket tasarımını kapsar. Köln fiziksel baskıyla doğrulanmadan genel Wall Collection standardı nihai olarak kilitlenmiş sayılmaz.

---

## Fiziksel Köln baskısı ve askı revizyonu

İlk gerçek beyaz Köln baskısı incelendi.

Fiziksel gözlemler:

- filament liflenmesi/stringing mevcut
- tek renk ürün yeterli premium ayrışmayı sağlamıyor
- siyah plaka ve beyaz yazı gerekli
- kırmızı çatılar gerekli
- yeşil alan katmanı gerekli
- Pädagogische Fakultät binası özel olarak ayrıştırılmalı
- plakaya mezuniyet kepi veya alternatif simge eklenmeli

Askı kararı:

- Mevcut revize keyhole askı kabul edildi.
- Çivi başı girişi: 5.0 mm
- Kilit kanalı: 3.0 mm
- Kilitleme hareketi: 1.0 mm
- Kapalı üst taşıyıcı duvar: 1.75 mm
- 150, 200 ve 260 mm ürünlere genel motor standardı olarak uygulanır.
- Commit: `404c0d2 Improve wall hanger nail retention`
- Push tamamlandı.
- Wall Collection ilgili regresyon: 28 passed

## Çok renkli Köln üretim durumu

Tamamlanan:

- `KOELN_PREMIUM_V1` malzeme profili
- semantik bina duvarı / çatı ayrımı
- beş renkli STL paket exporter'ı
- aynı RGB sınıfındaki mesh gruplarını tek STL içinde birleştirme
- gerçek Köln dört renkli STL paketi üretimi
- ilgili entegrasyon paketi: 25 passed

Açık işler:

- Pädagogische Fakultät hedef binasını komple kırmızı ayırmak
- plakaya mezuniyet kepi veya seçilen simgeyi eklemek
- STL parçalarını Bambu Studio'da tek assembly olarak açıp hizalamayı doğrulamak
- filament atamalarını yapmak
- dilimleme süresi ve filament tüketimini ölçmek
- stringing sorununu baskı profili seviyesinde çözmek

## Köln tamamlanma kriterleri

Köln referans ürünü tamamlanmış sayılması için:

- Geometri doğrulanacak.
- Preview kontrol edilecek.
- Final STL üretilecek.
- STL Bambu Studio'da açılacak.
- 5 renk atanacak.
- Baskı süresi kontrol edilecek.
- Filament tüketimi incelenecek.
- Test baskısı yapılacak.
- Gerekli revizyonlar tamamlanacak.
- Standart kilitlenecek.

---

## Dokümantasyon durumu

Tamamlanan:

- Docs/START_HERE.md
- Docs/STATUS/CURRENT_STATUS.md

Sıradaki belgeler:

- Docs/STANDARDS/ATLAS_WALL_COLLECTION_REFERENCE_STANDARD.md
- Docs/PRODUCTS/KOELN_PAEDAGOGISCHE_FAKULTAET_REFERENCE.md

---

## Çalışma kuralları

- Tüm işlemler terminalden yapılır.
- Aynı anda yalnızca bir işlem yapılır.
- Kullanıcı çıktısı görülmeden sonraki adıma geçilmez.
- Manuel editör talimatı verilmez.
- git add . kullanılmaz.
- Yalnız ilgili dosyalar stage edilir.
- Test-first geliştirme uygulanır.
- Doğrulanmış adımlar commit edilir.
- Uygun noktada origin main dalına push edilir.

---

## Sıradaki tek işlem

Köln için üretilen beyaz, kırmızı, yeşil ve siyah STL dosyalarını Bambu Studio'da tek assembly olarak açmak; parçaların aynı koordinatlarda kusursuz hizalandığını doğrulamak ve doğru filament slotlarını atamak.


---

## Oturum kapatma kuralı

Her geliştirme oturumu tamamlanmadan önce bu belge güncellenmelidir.

En az aşağıdaki bilgiler güncel olmalıdır:

- Tamamlanan teknik çalışmalar
- Alınan mimari kararlar
- Güncellenen belgeler
- Varsa yeni standartlar
- Bilinen açık işler
- Sıradaki tek teknik işlem

Bu belge güncellenmeden geliştirme oturumu tamamlanmış kabul edilmez.

Bu kural, ATLAS_ENGINE geliştirme metodolojisinin zorunlu bir parçasıdır.
