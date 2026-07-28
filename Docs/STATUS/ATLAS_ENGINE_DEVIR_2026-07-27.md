cd /Users/Kubi/ATLAS_ENGINE && bash -c '
cat > Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-07-27_PART_1_1-6.md <<'"'"'EOF'"'"'
# ATLAS_ENGINE DEVİR DOSYASI — BÖLÜM 1
## Tarih: 27 Temmuz 2026
## Kapsam: Maddeler 1–6

---

# 1. GENEL DURUM

ATLAS_ENGINE, prototip aşamasını büyük ölçüde geride bırakmıştır.

Çekirdek üretim hattı gerçek dünya verileri üzerinde doğrulanmıştır. Şehir modeli, terrain, bina, yol, park, landmark, etiket, duvar ürünü ve STL üretim zincirleri birlikte çalışmaktadır.

Yaklaşık teknik durum:

- Genel teknik tamamlanma: `%75–77`
- 3D City / Terrain / Landmark Engine: `%82+`
- 2.5D Relief Engine: `%75 civarı`
- Ticari MVP hazırlığı: `%65 civarı`

Aktif yönelim artık temel motor mimarisinden çok:

- ürün kalibrasyonu,
- görsel kalite,
- baskı güvenliği,
- ürün otomasyonu,
- ticari sunum

üzerindedir.

---

# 2. ANA ÜRETİM ZİNCİRİ

Çalışan genel zincir:

```text
OSM
→ Product Area
→ Terrain
→ Foundation
→ Buildings
→ Roads
→ Parks
→ Trees
→ Landmarks
→ Labels
→ Product Frame
→ STL
→ Mesh Validation
Gerçek saha doğrulamaları:

* Anıtkabir
* Rumeli Hisarı
* Burghausen
* Hohenzollern
* Steinbach
* Galata Köprüsü
* Atakule
* Şile Feneri
* Köln / My Life Map Wall Collection sahası

⸻

3. BİNA VE ÇATI SİSTEMİ

Tamamlanan başlıca yetenekler:

* building:part desteği
* Parent / child bina ilişkileri
* Küçük fakat fiziksel olarak basılabilir yapı parçaları
* Flat roof
* Gable roof
* Hipped roof
* Castle shell
* Hole polygon desteği
* Minimum printable building kuralları
* Terrain üzerinde foundation-first bina yerleşimi
* Bina meshleri için ayrı topology doğrulaması

Bina meshleri tek tek doğrulandığında:
Open edges       : 0
Non-manifold     : 0
4. TERRAIN VE DOĞAL ÇEVRE

Çalışan bileşenler:

* SRTM terrain
* Foundation-first terrain pipeline
* Terraced terrain
* Terrain sampler
* Foundation sampler
* WorldCover tree sampling
* OSM green-area tree sampling
* WorldCover surface aggregation
* Terrain-following placement

Steinbach sahası doğal görünüm ve bitki yoğunluğu açısından ana kalibrasyon alanı olmaya devam etmektedir.

⸻

5. LANDMARK SİSTEMİ

Aktif desteklenen landmark türleri:

* Bridge
* Lighthouse
* Obelisk
* Tower
* Observation Tower
* Castle
* Theatre altyapısı

Şile Feneri

Tamamlananlar:

* Gerçek OSM footprint foundation hesabında korunuyor.
* Görsel radial lighthouse profili ile terrain foundation footprint ayrıldı.
* Landmark artık terrain üzerinde doğru tabana oturuyor.

Atakule

Kesin teşhis:

* Aynı OSM nesnesi hem bina hem landmark hattına giriyordu.
* Düz bina gövdesi, observation tower profilini görsel olarak kapatıyordu.

Çözüm:

* Landmark / building deduplication sistemi eklendi.
* Observation tower landmark hattı korunuyor.
* Observation profile katmanlı ring geometrisi çalışıyor.

Açık konu:

* Platform ve gövde oranlarının fiziksel ürün ölçeğinde son kalibrasyonu.

Galata Köprüsü

Tamamlananlar:

* Köprü üretim geometrisi
* Pier doğrulamaları
* Geçersiz pier değerleri için fallback
* Manifold parapet
* Parapet / deck birleşimi
* 0 open edges
* 0 non-manifold edges
* Yol referanslı yaklaşım geometrisi
* Dinamik road target çözümü

İlgili önemli commitler:
33e670e Make Galata bridge parapets manifold with deck
7cea124 Add road-aware bridge approach geometry
6. MY LIFE MAP WALL COLLECTION

27 Temmuz 2026 tarihinde ürünleştirme hattında önemli ilerleme kaydedildi.

İlgili plan dosyası:
Docs/STATUS/MY_LIFE_MAP_WALL_COLLECTION_PLAN_2026-07-27.md
Çalışan ürün bileşenleri:

* Duvar tipi koleksiyon ürünü
* Ürün çerçevesi
* Şehir sahnesi
* Birincil ürün etiketi
* İkincil ürün etiketi
* Label plate
* Kabartma label text
* STL export
* Preview CLI
* Etiket yapılandırma doğrulaması

Etiket kuralı:

* İkincil etiket, birincil etiket olmadan kullanılamaz.

İlgili commitler:
992fce7
703c3b1
59c8386
8659b87 Add configurable wall product labels
EOF

cat > Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-07-27_PART_2_7-13.md <<’”’”‘EOF’”’”’

ATLAS_ENGINE DEVİR DOSYASI — BÖLÜM 2

Tarih: 27 Temmuz 2026

Kapsam: Maddeler 7–13

⸻

7. KÖLN SAHNESİ VE YOL TOPOLOJİSİ

Köln kişiselleştirilmiş şehir ürünü üzerinde yol sınırı problemi tespit edildi.

Eski yaklaşım:
Ürün sınırını aşan yol meshlerini kesmek
Bu yaklaşım yol uçlarında açık kenar oluşturuyordu.

Eski sonuç:
Open edges: 78
Yeni genel motor yaklaşımı:
Ürün sınırının tamamen içinde kalan yol meshlerini korumak
Ürün sınırını geçen yol meshlerini dışarıda bırakmak
Yeni sonuç:
Open edges: 0
Bu çözüm yalnız Köln testine özel bırakılmadı; ana engine içine genelleştirildi.

İlgili commit:
9fa4199 Keep road meshes inside product bounds
8. MESH VALIDATOR İNCELEMESİ

Köln ürününde birleşik validation sonucu:
Open edges       : 0
Non-manifold     : 263
Ayrıntılı teşhis yapıldı.

Grup bazında sonuç
buildings ↔ buildings : 205 ortak kenar
parks ↔ parks         : 58 ortak kenar
Tekil mesh doğrulaması

Toplam şehir meshi:
913
Her mesh ayrı ayrı doğrulandığında:
Individual open edges       : 0
Individual non-manifold     : 0
Bütün şehir meshleri tek bir global üçgen kümesi olarak değerlendirildiğinde:
Merged non-manifold edges   : 263
Kritik yorum

Bu aşamada fiziksel meshlerin tek tek bozuk olduğuna dair kanıt yoktur.

Validator:

* farklı kapalı meshlerde,
* aynı koordinatlarda bulunan,
* ortak veya kısmen örtüşen kenarları

tek bir global triangle soup içinde değerlendiriyor.

Bu nedenle ayrı kapalı cisimler arasındaki ortak kenarlar global non-manifold olarak raporlanabiliyor.

Tespit edilen yoğun çakışmalar
buildings[168] ↔ buildings[440]
shared edges     : 147
shared triangles : 74

buildings[260] ↔ buildings[271]
shared edges     : 51
shared triangles : 28

parks[1] ↔ parks[18]
shared edges     : 33
shared triangles : 20
Meshler tam kopya değildir.

Bazı bina ve park geometrileri kısmen örtüşmektedir.

Karar

Bu konu şu aşamada:
ERTELENMİŞ VALIDATOR / OSM ÖRTÜŞME İNCELEMESİ
olarak bırakılmıştır.

Ana ürün geliştirme hattından daha fazla sapılmayacaktır.

Şu anda yapılmayacaklar:

* Rastgele bina silme
* Rastgele park silme
* OSM nesnelerini kanıtsız filtreleme
* Meshleri zorla birleştirme
* Boolean union sistemine plansız geçiş
* Validator uyarısını gizleme

Gelecekte ele alınacak doğru çözüm adayları:

1. Validator’a mesh-component farkındalığı kazandırmak
2. Ayrı kapalı cisimleri ayrı topology bileşenleri olarak doğrulamak
3. OSM parent / part örtüşmelerini kontrollü incelemek
4. Park polygon örtüşmeleri için source-level deduplication tasarlamak
5. Product-level topology ile object-level topology sonuçlarını ayırmak

⸻

9. TEŞHİS SIRASINDA DOSYA GÜVENLİĞİ

Köln topology teşhislerinde ana kaynak dosyalarda değişiklik yapılmadı.

Teşhisler:

* yalnızca mevcut motoru çalıştırdı,
* mevcut mesh metadata bilgilerini okudu,
* geçici STL dosyalarını /tmp altında üretti.

Geçici dosya örnekleri:
/tmp/atlas_koeln_topology_diagnostic.stl
/tmp/atlas_koeln_edge_collision_diagnostic.stl
/tmp/atlas_koeln_metadata_diagnostic.stl
Bu teşhis komutları repository kaynak kodunu değiştirmedi.

Son önerilen OSM source-inspection komutu çalıştırılmadı.

⸻

10. TEST-FIRST VE GIT DİSİPLİNİ

Proje geliştirme yöntemi:
RED
→ GREEN
→ Focused Regression
→ Relevant Full Regression
→ Selective Git Stage
→ Commit
→ Push
Kurallar:

* Terminal üzerinden çalışma
* Tek komutluk adımlar
* Manuel dosya düzenleme yok
* git add . kullanılmaz
* Yalnız ilgili dosyalar stage edilir
* Her değişiklik regresyon testiyle korunur
* Kullanıcının çıktısı görülmeden sonraki adıma geçilmez

Terminal komutlarının sonunda kullanılan standart:
2>&1 | tee /tmp/atlas_last.log && pbcopy < /tmp/atlas_last.log
11. 2.5D RELIEF MOTORU

Mevcut zincir:
Image
→ Subject Mask
→ Depth / Normal
→ Structure Decomposition
→ Semantic Weighting
→ Gradient Limiting
→ Screened Poisson
→ Height Field
→ Mesh
→ STL
Tamamlanan başlıca modüller:

* Image input
* Subject mask
* DSINE normal
* Structure / detail decomposition
* Semantic detail weighting
* Gradient limiter
* Face anchor enhancement
* Screened Poisson integrator
* FLAME altyapısı
* Weak-perspective fitting altyapısı
* Fitted FLAME mesh üretim altyapısı

Kalan ana konu:

* Yüz kimliğini koruyan,
* gözlük ve ağız artefaktlarını azaltan,
* ticari baskı kalitesine ulaşan

son relief kalibrasyonu.

⸻

12. TİCARİ ÜRÜN AİLESİ

Planlanan ana ürün aileleri:

* My Life Map
* Our Love Map
* Family Heritage
* Personalized City Models
* Wall Collection
* Landmark Products
* 2.5D Portrait Relief Products

Ana marka fikri:

Every important memory has a location.

İlk canonical ATLAS modeli:
Anıtkabir
İlk gerçek model olduğuna dair küçük metadata imzası eklenmesi uzun vadeli ürün tercihidir.
13. ÜRETİM ALTYAPISI

Mevcut:

* Bambu Lab P2S Combo
* 200 mm ürün sınıfı doğrulandı
* 1:5500 ölçek doğrulandı
* STL üretim hattı çalışıyor
* Wall Collection ürün iskeleti çalışıyor
* Etiket üretimi çalışıyor
* Printability kontrolleri mevcut

Hazırlık aşamasında:

* Tek komutluk ürün üretimi
* Otomatik preview
* Ürün presetleri
* Baskı profilleri
* Sipariş entegrasyonu
* Web sitesi ürün yapılandırıcısı
* Müşteri konum ve etiket girişi
* Otomatik ürün onayı
    EOF

cat > Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-07-27_PART_3_14-17.md <<’”’”‘EOF’”’”’

ATLAS_ENGINE DEVİR DOSYASI — BÖLÜM 3

Tarih: 27 Temmuz 2026

Kapsam: Maddeler 14–17

⸻

14. SON TAMAMLANAN GENELLEŞTİRMELER

Köln / Wall Collection çalışmasından ana motora aktarılanlar:

1. Yol sınırı clipping yerine bounds filtering
2. Road topology regresyon testleri
3. Ürün çerçevesi
4. Configurable wall labels
5. Label plate
6. Label text
7. Label validation
8. Wall Collection STL exporter
9. Preview CLI
10. Product-level mesh group diagnostics

Bunlar yalnız Köln sahasına özel geçici çözümler değildir.

⸻

15. ŞU ANKİ KESİN MOLA NOKTASI

Ana ürün hattı güvenli durumdadır.

Kesin doğrulananlar:
Road open edges                   : 0
Individual city mesh open edges  : 0
Individual non-manifold edges    : 0
Frame topology                    : clean
Label plate topology              : clean
Label text topology               : clean
Açık fakat ertelenmiş konu:
Global city validation:
263 coincident / shared non-manifold edge report
Bu raporun büyük bölümü:
building ↔ building
park ↔ park
örtüşmelerinden kaynaklanmaktadır.

Bu konu için daha fazla işlem yapılmadan önce:

* hedef açıkça belirlenmeli,
* validator davranışı ile gerçek baskı riski ayrılmalı,
* source-level deduplication için test-first sözleşme hazırlanmalıdır.

⸻

16. SIRADAKİ ÖNERİLEN ANA YOL

Validator incelemesini şimdilik durdur.

Öncelik sırası:

1. Wall Collection ürün akışını kullanıcı açısından tamamlamak
2. Gerçek ürün preview çıktısını değerlendirmek
3. Ürün ölçüleri ve etiket yerleşimini kalibre etmek
4. Güncel Anıtkabir üretimi almak
5. Atakule observation profile oranlarını sonlandırmak
6. Steinbach doğal görünümünü iyileştirmek
7. Tam regresyon çalıştırmak
8. Daha sonra validator component modelini ayrı paket olarak ele almak

⸻

17. GENEL DEĞERLENDİRME

ATLAS_ENGINE temel mühendislik problemlerinin önemli bölümünü çözmüştür.

Şehir, terrain, bina, yol, park, landmark, duvar çerçevesi ve etiket bileşenleri artık tek bir ürün hattında bir araya gelebilmektedir.

Köln çalışması sırasında bulunan yol topology problemi ana motorda genelleştirilerek çözülmüştür.

Kalan 263 non-manifold raporu şu anda doğrudan bir bozuk STL kanıtı değildir. Tekil meshlerin tamamı temizdir. Sorun global validator semantiği ile örtüşen ayrı nesnelerin birlikte değerlendirilmesi arasındadır.

Ana hedef:
Teknik araştırmada kaybolmadan,
ATLAS_ENGINE'i gerçek, basılabilir ve satılabilir ürüne dönüştürmek.
EOF

printf “\nOluşturulan dosyalar:\n”
printf “1. Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-07-27_PART_1_1-6.md\n”
printf “2. Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-07-27_PART_2_7-13.md\n”
printf “3. Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-07-27_PART_3_14-17.md\n”
’ 2>&1 | tee /tmp/atlas_last.log && pbcopy < /tmp/atlas_last.log