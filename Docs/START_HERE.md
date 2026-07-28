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
- En fazla 5 renk kullanılacak.
- Çatılar kırmızı veya terracotta olacak.

Sabit renk sınıfları:

1. Frame + Label Plate: siyah veya antrasit
2. Terrain + Roads: sıcak taş veya kum tonu
3. Building Walls + Label Text: kırık beyaz
4. Building Roofs: kırmızı veya terracotta

Beşinci renk sahneye göre seçilir:

- Yeşil: parklar, ağaçlar ve çimen
- Mavi: deniz, nehir, göl, kanal ve havuz

Dijital preview içindeki daha fazla material sınıfı fiziksel baskı standardı değildir.

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
