---

## Decision - Data Fusion Layer

**Tarih:** 2026-07-05

ATLAS, tek bir veri kaynağına bağımlı olmayacaktır.

Desteklenmesi planlanan veri kaynakları arasında:

- OpenStreetMap
- Belediye CBS/GIS verileri
- GeoJSON
- Shapefile
- CityGML
- PostGIS
- Kullanıcı yüklemeleri
- Tarihsel arşiv verileri
- Gelecekte desteklenecek diğer coğrafi veri formatları

bulunmaktadır.

Bu nedenle bütün veriler önce ortak bir doğrulama ve birleştirme katmanından geçirilecektir.

Bu katmanın adı:

**AtlasDataFusionEngine**

AtlasScene yalnızca bu katmandan geçmiş verilerle oluşturulacaktır.
---

## Decision - Portrait Canonical Face Geometry

**Tarih:** 2026-07-21

ATLAS 2.5D portre rekonstrüksiyonunun ticari canonical yüz geometrisi ve sabit topoloji temeli olarak:

**FLAME 2023 Open**

seçilmiştir.

Kullanılacak model sürümü yalnızca resmi olarak yayımlanan ve `CC BY 4.0` lisansı altında sunulan `FLAME 2023 Open` modelidir.

Bu kararın teknik dayanakları:

- Sabit canonical mesh topolojisi
- 5.023 vertex
- 9.976 triangle
- Geçerli triangle indeks aralığı
- 0 duplicate triangle
- 0 degenerate triangle
- 400 shape/expression bileşeni
- Son 100 bileşenin expression alanı olarak tanımlanması
- 36 pose-corrective bileşeni
- 5 eklemli skinning yapısı
- 105 noktalı MediaPipe landmark embedding
- Geçerli barycentric landmark koordinatları
- 14 hazır semantik vertex maskesi
- Apple Silicon üzerinde NumPy ve SciPy ile okunabilir model yapısı

Model dosyasının doğrulanan SHA-256 değeri:

`e75a0990728ba038c7da2a420ae4396f7ddd7781366c13026066c5b24f127623`

ATLAS üretim mimarisi:

fotoğraf
→ landmark veya dense correspondence
→ ATLAS identity / expression / pose fitting katmanı
→ FLAME 2023 Open canonical mesh
→ AtlasParametricFaceGeometry
→ frontal contact-plane projection
→ feature-sensitive 2.5D relief compression
→ shaded-preview kabulü
→ manifold mesh ve STL

FLAME yalnız canonical yüz geometrisi, parametre uzayı ve topoloji sağlayacaktır.

Fotoğraftan fitting, kamera normalizasyonu, confidence üretimi, semantic normalization, relief projection ve baskıya uygun compression işlemleri ATLAS tarafından uygulanacaktır.

DECA, MICA ve EMOCA:

- ATLAS production bağımlılığı olmayacaktır.
- Kodları veya model ağırlıkları ticari üretim zincirine eklenmeyecektir.
- Yalnız izole araştırma, benchmark ve teknik karşılaştırma referansı olarak kullanılabilir.
- Gelecekte açık ve uygun bir ticari lisans alınmadıkça bu karar değişmeyecektir.

FLAME model dosyaları, yardımcı maskeler, landmark embedding dosyaları ve lisans materyalleri Git deposuna eklenmeyecektir.

Bu varlıklar repo dışındaki kontrollü ve özel model alanında tutulacaktır:

`/Users/Kubi/ATLAS_FLAME_SPIKE/`

FLAME vertex maskeleri ATLAS’a aktarılırken:

- Tekrarlanan vertex indeksleri deduplicate edilecektir.
- Semantik bölgeler arasındaki doğal overlap korunacaktır.
- Hazır maskelerin kapsamadığı vertexler otomatik olarak yanlış bir semantik sınıfa atanmayacaktır.
- Roadmap’in gerektirdiği daha ayrıntılı bölgeler ATLAS canonical semantic katmanında ayrıca tanımlanacaktır.

Bu karar, portre rekonstrüksiyon planının:

- 17. maddesindeki FLAME feasibility sonucunu,
- 18. maddesindeki kesin lisans ve ticari kullanım kararını

kapatır.

Sıradaki üretim paketi:

**`AtlasParametricFaceGeometry` canonical sözleşmesi**

---

## Decision Update - Portrait Canonical Face Geometry Phase 8 Revalidation

**Tarih:** 2026-08-20

The 2026-07-21 FLAME 2023 Open selection is retained as a historical/provisional architecture decision, but it no longer authorizes a production dependency by itself. The active Phase 8 Canonical Face/Head Decision Gate supersedes the earlier finality of that selection.

Before any face/head provider enters the ATLAS commercial production core, Phase 8 must revalidate commercial licensing and attribution, model/data/weight restrictions, privacy and retention, Apple Silicon/runtime compatibility, identity-expression-pose separation, multi-view consistency, stable topology/correspondence, physical relief/bust/figurine suitability, reproducibility and processing cost.

The preferred architecture direction to benchmark is a hybrid full-3D canonical head: stable parametric/fixed topology plus person-specific detail. FLAME-like geometry remains a strong candidate, not an automatic final dependency. Phase 8 closes only through explicit GO/HOLD/REJECT and LOCK. Phase 9 production work is prohibited before Phase 8 GO + LOCK.
