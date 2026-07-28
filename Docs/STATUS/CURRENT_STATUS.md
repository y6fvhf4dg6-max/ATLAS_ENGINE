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

Sabit renkler:

1. Frame + Label Plate
2. Terrain + Roads
3. Building Walls + Label Text
4. Building Roofs (kırmızı / terracotta)

Beşinci renk:

- Yeşil (park, ağaç, çimen)

veya

- Mavi (su alanları)


---

## Mevcut üretim zinciri

OSM / SRTM
→ terrain
→ roads
→ parks
→ trees
→ buildings
→ roof geometry
→ frame
→ label plate
→ label text
→ single STL

Final STL tek dosyada:

- frame
- city
- label plate
- label text

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

Docs/STANDARDS/ATLAS_WALL_COLLECTION_REFERENCE_STANDARD.md

Bu belge, Köln referans ürününden çıkarılan ve gelecekteki tüm Wall Collection ürünlerinde kullanılacak ortak standartları tanımlayacaktır.


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
