# ATLAS_ENGINE — PORTRE REKONSTRÜKSİYONU EYLEM PLANI

**Tarih:** 20 Temmuz 2026
**Durum:** Kilitli mimari yön ve uygulama planı
**Son temiz commit:** `52ce7e5 Integrate relief product profile`
**Son doğrulanmış tam regresyon:** `854 passed in 4.87s`
**Ana ortam:** `/Users/Kubi/ATLAS_ENGINE/.venv`
**Ana Python:** `3.14.6`
**Platform:** Apple Silicon / arm64

---

# 1. AMAÇ

ATLAS_ENGINE’in 2.5D portre hattını, fotoğraf parlaklığından veya genel sahne depth modellerinden geometri üretmeye çalışan deneysel yaklaşımdan çıkarıp anatomik olarak anlamlı bir yüz tabanına dayandırmak.

Yeni temel yaklaşım:

Parametrik 3B yüz tabanı
+ fotoğraftan kimlik oranları
+ saç / gözlük / sakal yardımcı katmanları
+ kontrollü bas-relief sıkıştırması
= tanınabilir ve basılabilir kişisel rölyef

Ana ürün vaadi:

> Tek veya birkaç fotoğraftan, kişiyi ilk bakışta tanınabilir kılan stilize ve fiziksel olarak basılabilir 2.5D portre rölyefi.

Amaç biyometrik olarak kusursuz tam 360 derece büst üretmek değildir.
---

# 2. KESİN MİMARİ KARAR

Portre rölyefinin ana yüz hacmi artık aşağıdaki kaynaklardan üretilmeyecektir:

- Doğrudan fotoğraf luminansı
- Genel monocular depth
- Depth Anything V2
- Bambu depth ve fotoğraf hibriti
- PIL posterizasyonu
- Eliptik face-volume maskesi
- Gaussian anatomy prior
- Fotoğraftaki ışık ve gölge tonlarının doğrudan geometriye çevrilmesi

Ana yüz depth kaynağı şu olacaktır:

> Landmarklarla kişiye uyarlanmış parametrik 3B yüz yüzeyi.

Fotoğrafın rolü:

- Yüz oranlarını belirlemek
- Landmark üretmek
- Yüz silüetini korumak
- Saç çizgisini belirlemek
- Kaş karakterini korumak
- Burun ve çene kimliğini desteklemek
- Gözlük, sakal ve bıyık katmanlarını üretmek
- Düşük genlikli yüzey detayını sağlamak

Fotoğraf, ana yüz hacmini doğrudan üretmeyecektir.
---

# 3. ARAŞTIRMA SONUÇLARI

ABD, Japonya ve diğer uluslararası kaynaklardan çıkarılan ortak sonuçlar:

1. Fotoğraf parlaklığı fiziksel derinlik değildir.
2. Genel sahne depth modelleri kişi–arka plan ayrımında başarılı olsa da yüz anatomisinde yetersizdir.
3. Başarılı portre sistemleri önce anatomik bir 3B yüz tabanı kurar.
4. Landmarklar parametrik yüz yüzeyini kişiye oturtmak için kullanılır.
5. Saç, gözlük, kaş, sakal ve kıyafet ana yüz geometrisinden ayrı katmanlar olarak ele alınır.
6. Tek fotoğraf kontrollü bir tahmin sağlar.
7. İki veya üç fotoğraf burun, çene ve profil çıkıntısını belirgin biçimde iyileştirir.
8. Başarılı bas-relief sistemleri form ve detayı ayrı işler.
9. Normal, gradient ve yüzey formu, ham grayscale displacement yaklaşımından daha güvenilir sonuç verir.
10. Tam otomasyon mümkün olsa da düşük güven durumları için kullanıcı veya operatör düzeltme akışı gerekir.
---

# 4. KAPATILMIŞ DENEYSEL YOLLAR

## 4.1 Doğrudan luminance

Sonuç:

- Manifold STL üretildi.
- Yüz anatomisi oluşmadı.
- Gözlük ve kıyafet tonları yanlış yükseklikler üretti.
- Işık ve gölge fiziksel geometriye dönüştü.

Karar:

> Ana yüz depth kaynağı olarak kapatıldı.

## 4.2 Depth Anything V2

Sonuç:

- Sahne depth’i üretildi.
- Yüz genelleştirilmiş kubbeye dönüştü.
- Gözlük artefakt olarak baskınlaştı.
- Burun, yanak, alın ve çene doğru sıralanmadı.

Karar:

> Gamma, contrast veya smoothing ile yeniden denenmeyecek.

## 4.3 Bambu Make My Statue

Sonuç:

- Temiz ve basılabilir mesh üretildi.
- Kişisel benzerlik zayıftı.
- Genel bir yüz anatomisi oluştu.

Karar:

> Nihai kişisel portre tabanı değildir.

## 4.4 Bambu depth ve fotoğraf hibriti

Sonuç:

- Hizalama iyileştirildi.
- Ancak sonuç “genel kafa + fotoğraf izi” olarak kaldı.
- Kimlik ayrıntıları geri gelmedi.
- Gözlük baskın kaldı.

Karar:

> `HYBRID V3` veya benzer deformasyon denemeleri yapılmayacak.

## 4.5 PIL ve posterizasyon

Sonuç:

- Kontrollü yüz düzlemleri yerine ton lekeleri oluştu.
- Ağız, çene ve kıyafet sorunlu kaldı.

Karar:

> Nihai stilize portre üretim yöntemi değildir.

## 4.6 Gaussian anatomy prior

Sonuç:

- Burun, yanak, ağız ve çene yaklaşık alanlarla modellenmeye çalışıldı.
- Shaded preview’de gerçek yüz anatomisi okunmadı.
- Sonuç sentetik lekeler ve genel kubbe biçiminde kaldı.

Karar:

> Gaussian anatomy prior tamamen kapatıldı.
---

# 5. MEVCUT KABUL EDİLMİŞ PORTRE VERİLERİ

Ana master görsel:

`Data/RELIEF/real_portrait_01/stylized_portrait/PORTRAIT_GRAPHIC_V1_MASTER.png`

Dosya özellikleri:

- Boyut: `1122 × 1402`
- Mod: `RGB`
- SHA256: `a3e7ad97256b42ba3884269106572d327badc3e53aef7beafdaf245892456afa`

Üretilen teknik maskeler:

- `PORTRAIT_GRAPHIC_V1_SUBJECT_MASK.png`
- `PORTRAIT_GRAPHIC_V1_FACE_VOLUME_MASK.png`
- `PORTRAIT_GRAPHIC_V1_GLASSES_FRAME_MASK_V2.png`

Kabul edilen yüz ROI:

- `x0 = 284`
- `y0 = 245`
- `x1 = 888`
- `y1 = 838`

Bu koordinatlar yalnız mevcut kalibrasyon portresine aittir.

CORE içine hard-code edilmeyecektir.

Depth denemeleri:

- `PORTRAIT_GRAPHIC_V1_DEPTH_PREVIEW_V1.png`
- `PORTRAIT_GRAPHIC_V1_DEPTH_PREVIEW_V2.png`
- `PORTRAIT_GRAPHIC_V1_DEPTH_PREVIEW_V3.png`
- `PORTRAIT_GRAPHIC_V1_DEPTH_SHADED_V3.png`

Sonuç:

- V1 yüz hacmi düz ve kubbe benzeri kaldı.
- V2 tonal modülasyon yüz detayını artırdı ancak ışığı geometriye taşıdı.
- V3 sentetik anatomy prior ekledi ancak shaded preview’de gerçek yüz yüzeyi okunmadı.
- V3 başarısız kabul edildi.
- STL üretilmedi.
---

# 6. YENİ HEDEF MİMARİ

Yeni portre hattı aşağıdaki bağımsız katmanlardan oluşacaktır:

1. Portrait Input
2. Facial Landmark Provider
3. Parametric Face Model
4. Face Model Fitter
5. Portrait Depth Renderer
6. Accessory and Identity Layers
7. Relief Composition
8. Mesh / STL / Risk Pipeline

Ana akış:

fotoğraf
→ input ve kalite kontrolü
→ yüz tespiti
→ dense facial landmarks
→ baş pozu tahmini
→ parametrik yüz fitting
→ anatomik depth render
→ bas-relief compression
→ saç / gözlük / sakal yardımcı katmanları
→ relief composition
→ shaded preview
→ kullanıcı onayı
→ manifold mesh
→ STL
---

# 7. PORTRAIT INPUT

Görevleri:

- EXIF orientation
- Görüntü yükleme
- Tek veya çoklu fotoğraf kabulü
- Ana fotoğraf seçimi
- Ön / sol / sağ görünüş sınıflandırması
- Görüntü kalite kontrolü
- Yüz alanı ve crop
- Kaynak metadata üretimi

Önerilen sınıflar:

- `AtlasPortraitInput`
- `AtlasPortraitReference`
- `AtlasPortraitReferenceSet`
- `AtlasPortraitInputResult`

Önerilen çıktı sözleşmesi:

```python
{
    "type": "portrait_input_result",
    "primary_reference": ...,
    "secondary_references": ...,
    "image_width": ...,
    "image_height": ...,
    "orientation": ...,
    "view_type": ...,
    "quality_report": ...,
    "metadata": ...,
}
---

# 8. FACIAL LANDMARK PROVIDER

Görevleri:

- Yüz tespiti
- Dense facial landmark üretimi
- Göz köşeleri
- Göz merkezleri
- Kaş sınırları
- Burun kökü
- Burun sırtı
- Burun ucu
- Burun kanatları
- Ağız köşeleri
- Dudak merkezleri
- Çene ucu
- Jawline
- Yüz dış sınırı
- Baş pozu
- Güven skoru

İlk spike adayı:

- `MediaPipe Face Landmarker`

Gerçek provider doğrudan CORE içine gömülmeyecektir.

Önerilen provider yolu:

- `CORE/providers/portrait/atlas_portrait_landmark_provider.py`

Standart çıktı sözleşmesi:

```python
{
    "type": "portrait_landmark_result",
    "image_width": ...,
    "image_height": ...,
    "landmarks": ...,
    "head_pose": ...,
    "confidence": ...,
    "provider_id": ...,
    "metadata": ...,
}
---

# 9. PARAMETRİK YÜZ MODELİ

Bu katman yeni portre hattının kritik çekirdeğidir.

Görevleri:

- Nötr 3B yüz şablonunu yüklemek
- Landmarklara göre yüzü ölçeklemek
- Göz aralığını uyarlamak
- Yüz genişliği ve uzunluğunu uyarlamak
- Burun uzunluğu ve genişliğini uyarlamak
- Çene ve jawline yapısını uyarlamak
- Profil fotoğrafları varsa burun ve çene çıkıntısını düzeltmek
- Anatomik olarak tutarlı 3B yüz yüzeyi üretmek

Önerilen sınıflar:

- `AtlasParametricFaceModel`
- `AtlasParametricFaceParameters`
- `AtlasFaceModelFitter`
- `AtlasFaceSurfaceResult`

Başlangıç modeli şu özelliklere sahip olmalıdır:

- Sabit topoloji
- Nötr ifade
- Kontrollü deformasyon
- Landmark fitting
- Ticari kullanıma uygun lisans
- Apple Silicon üzerinde kullanılabilirlik
- Önden depth render desteği
- Saç ve gözlük içermeyen nötr yüz

İlk parametre grupları:

- `face_width`
- `face_height`
- `eye_spacing`
- `eye_height`
- `nose_width`
- `nose_length`
- `nose_projection`
- `mouth_width`
- `chin_width`
- `chin_length`
- `chin_projection`
- `jaw_width`
- `forehead_height`
- `forehead_slope`
- `cheek_projection`
- `facial_convexity`
---

# 10. FACE MODEL FITTING

Amaç, nötr yüz modelini kişinin fotoğraflarındaki oranlara oturtmaktır.

## 10.1 İlk aşama: frontal 2B fitting

Uyarlanacak parametreler:

- Scale
- Translation
- Rotation
- Face width
- Face height
- Eye spacing
- Eye height
- Nose width
- Nose length
- Mouth width
- Chin width
- Jaw width

## 10.2 İkinci aşama: profil desteği

Yan veya üç çeyrek fotoğraflardan şu parametreler iyileştirilecektir:

- Nose projection
- Chin projection
- Forehead slope
- Facial convexity
- Jaw projection

## 10.3 Tek fotoğraf davranışı

Tek fotoğrafta görünmeyen profil değerleri kontrollü parametrik prior ile tahmin edilecektir.

Sistem bu durumu metadata ve confidence alanlarında belirtecektir.

## 10.4 Çoklu fotoğraf davranışı

Önden, sol ve sağ referanslar varsa fitting aynı kimlik üzerinde birlikte çözülecektir.

Başarı kriteri:

> Fitted mesh’in projekte edilen landmarkları, hedef landmarklara belirlenen hata toleransı içinde oturmalıdır.
---

# 11. PORTRAIT DEPTH RENDERER

Görevleri:

- Fitted 3B yüzü önden render etmek
- Orthographic veya kontrollü perspective kamera kullanmak
- Yüzün gerçek ön–arka sıralamasını korumak
- Burun ve çene çıkıntısını korumak
- Göz çukurlarını tamamen ezmemek
- Yüz yanlarını kontrollü sıkıştırmak
- Normalize `0..1` depth map üretmek
- Normal map üretmek
- Silhouette mask üretmek
- Kamera metadata’sı üretmek

Önerilen çıktı:

```python
{
    "type": "portrait_face_depth_result",
    "depth_map": ...,
    "normal_map": ...,
    "silhouette_mask": ...,
    "camera": ...,
    "face_parameters": ...,
    "metadata": ...,
}
---

# 12. ACCESSORY AND IDENTITY LAYERS

Ana yüz geometrisinden ayrı ele alınacak katmanlar:

- Saç
- Saç çizgisi
- Kaş
- Gözlük
- Sakal
- Bıyık
- Ağız çizgisi
- Yüz dış silüeti
- Boyun
- Kıyafet

Önerilen bileşim:

```text
parametric face depth       = ana hacim
hair layer                  = düşük / orta katkı
glasses layer               = düşük katkı
eyebrow layer               = çok düşük katkı
facial hair layer           = düşük katkı
mouth identity layer        = çok düşük katkı
silhouette correction       = kontrollü katkı
clothing layer              = düşük arka hacim
---

# 13. MEVCUT RELIEF ENGINE İLE ENTEGRASYON

Mevcut 2.5D motor korunacaktır.

Korunacak sistemler:

- `AtlasReliefImageInput`
- Sampling plan
- Bilinear resampling
- Gaussian smoothing
- Base thickness
- Relief height
- Closed manifold mesh
- Quality report
- Print-risk report
- STL writer
- Relief product profile sözleşmesi

Yeni akış:

```text
portrait face depth
→ accessory layer composition
→ physical sampling
→ height-map processing
→ closed manifold mesh
→ quality report
→ print-risk report
→ shaded preview
→ kullanıcı onayı
→ STL
---

# 14. NİHAİ MÜŞTERİ AKIŞI

Normal akış:

```text
kullanıcı fotoğraf yükler
→ otomatik orientation
→ otomatik yüz tespiti
→ otomatik landmark
→ otomatik parametrik fitting
→ otomatik accessory layers
→ shaded preview
→ kullanıcı onayı
→ STL
Kullanıcı şunlarla uğraşmayacaktır:

* ROI koordinatları
* Subject mask dosyaları
* Face mask dosyaları
* Gözlük maskesi
* Terminal
* Depth katsayıları
* Gaussian alanlar
* Landmark JSON dosyaları
Düşük güven akışı:
düşük confidence
→ kullanıcı crop veya landmark düzeltmesi
veya
→ operatör inceleme kuyruğu
Manuel landmark işaretleme yalnız kalibrasyon, ground-truth ve düşük güven fallback aracı olacaktır.
---

# 15. UYGULAMA FAZLARI

## FAZ 0 — Mimari karar ve eski deney dalının kapatılması

Amaç:

- Yeni teknik yönü kalıcı olarak belgelemek
- Başarısız yöntemlerin yeniden açılmasını önlemek
- Provider ve CORE sınırlarını belirlemek

Çıktılar:

- Bu eylem planı
- Roadmap güncellemesi
- Gerekirse Architecture Decision Record
- Kapatılmış deneyler listesi

Kabul kriteri:

> Ana portre depth kaynağı parametrik 3B yüz yüzeyidir. Luminance, genel depth ve Gaussian anatomy ana yüz kaynağı değildir.

## FAZ 1 — Landmark sözleşmesi

Önerilen dosyalar:

- `CORE/atlas_portrait_landmark_result.py`
- `CORE/providers/portrait/atlas_portrait_landmark_provider.py`
- `Test/test_portrait_landmark_result.py`
- `Test/test_portrait_landmark_provider.py`

Test kapsamı:

- Immutable sözleşme
- Görüntü boyutları
- Normalize koordinatlar
- Piksel koordinatları
- Finite kontrolü
- Confidence kontrolü
- Zorunlu landmark kontrolü
- Bilinmeyen landmark reddi
- Deterministik serialization
- Provider kimliği

Kabul kriteri:

> Gerçek ML modeli olmadan sentetik landmark fixture ile tüm testler geçmelidir.

## FAZ 2 — Manuel ground-truth fixture

Amaç:

- Mevcut kabul edilmiş master üzerinde gerçek referans landmark seti oluşturmak
- Otomatik provider doğruluğunu ölçmek
- Fitting algoritmasını doğrulamak

Minimum landmarklar:

- Sol ve sağ göz iç köşeleri
- Sol ve sağ göz dış köşeleri
- Göz merkezleri
- Kaş merkezleri ve sınırları
- Burun kökü
- Burun sırtı
- Burun ucu
- Burun kanatları
- Ağız köşeleri
- Üst dudak merkezi
- Alt dudak merkezi
- Çene ucu
- Jawline referansları
- Yüz sağ ve sol sınırları
- Saç çizgisi referansları

Ground-truth JSON şunları içermelidir:

- Master görüntü yolu
- Master SHA-256
- Görüntü boyutları
- Piksel koordinatları
- Normalize koordinatlar
- Landmark isimleri
- Fixture metadata

Özel portre verileri Git’e eklenmeyecektir.

## FAZ 3 — Landmark provider spike

İlk aday:

- `MediaPipe Face Landmarker`

Ana `.venv` korunacaktır.

Provider ayrı ortamda çalıştırılabilir:

- `.venv_portrait`

Ölçülecekler:

- Apple Silicon / arm64 kurulumu
- Python uyumluluğu
- Model boyutu
- Lisans
- Offline çalışma
- Tek görüntü çalışma süresi
- Gözlük altında landmark doğruluğu
- Profil fotoğrafı desteği
- Ground-truth hata oranı
- Standart JSON sözleşmesine dönüşüm

Başarı kriterleri:

- Master fotoğrafta yüz bulunmalı
- Zorunlu landmarklar çıkarılmalı
- Confidence üretilmeli
- Ground-truth karşılaştırması yapılmalı
- Çıktı CORE sözleşmesine dönüştürülebilmeli

## FAZ 4 — Nötr parametrik yüz modeli

Amaç:

- Sabit topolojili
- Ticari kullanıma uygun
- Hafif
- Kontrol edilebilir
- Landmark fitting’e uygun

bir nötr yüz modeli seçmek veya oluşturmak.

Model seçilmeden önce:

1. Lisans kontrolü
2. Ticari kullanım kontrolü
3. Yeniden dağıtım koşulları
4. Vertex topolojisi
5. Blendshape veya deformasyon uygunluğu
6. Apple Silicon uyumluluğu
7. Dosya boyutu
8. Test fixture üretilebilirliği

değerlendirilecektir.

## FAZ 5 — Landmark-driven fitting

İlk paket:

- Scale
- Translation
- Rotation
- Face width
- Face height
- Eye spacing
- Nose width
- Nose length
- Mouth width
- Chin width
- Jaw width

İkinci paket:

- Nose projection
- Chin projection
- Forehead slope
- Cheek projection
- Facial convexity

Testler:

- Sentetik landmark fitting
- Simetrik yüz
- Asimetrik giriş
- Aşırı parametre sınırları
- Tek fotoğraf fallback
- Üç fotoğraf fitting
- Deterministik çıktı
- Projection error

## FAZ 6 — Depth render ve bas-relief compression

Kurallar:

- İlk kamera tercihi orthographic
- Yüzün ön–arka aralığı ölçülecek
- Burun ucu korunacak
- Çene çıkıntısı korunacak
- Göz çukurları kontrollü tutulacak
- Yüz yanları aşırı ezilmeyecek
- Depth normalize `0..1` üretilecek
- Normal map üretilecek
- Shaded preview zorunlu olacak

Başlangıç fiziksel aralığı:

- Boyut: yaklaşık `80 × 100 mm`
- Base thickness: yaklaşık `0.80 mm`
- Relief height: yaklaşık `1.8–2.2 mm`
- Sampling: yaklaşık `0.5 mm`

Bu değerler fiziksel baskı öncesinde kilitlenmeyecektir.

## FAZ 7 — Yardımcı kimlik katmanları

Uygulama sırası:

1. Yüz dış silüeti
2. Saç çizgisi
3. Kaş
4. Gözlük
5. Sakal ve bıyık
6. Ağız karakteri
7. Boyun ve kıyafet

Her katman ayrı test edilecektir.

## FAZ 8 — Relief Engine entegrasyonu

Amaç:

- Parametrik yüz depth sonucunu mevcut `AtlasReliefPipeline` veya yeni kontrollü portrait giriş sözleşmesine bağlamak
- Mevcut manifold mesh ve risk sistemini korumak

Testler:

- Depth input contract
- Sampling
- Relief height
- Base thickness
- Mesh closure
- Open edges
- Non-manifold edges
- Degenerate triangles
- Print-risk
- Metadata
- Product profile integration

## FAZ 9 — Shaded preview ve kullanıcı onayı

STL’den önce zorunlu görsel kapı:

- Anatomik yüzey okunuyor mu?
- Kişi tanınabiliyor mu?
- Burun ve çene doğru mu?
- Gözlük baskın mı?
- Saç ve sakal kontrollü mü?
- Yüz kubbe gibi mi?
- Işık geometriye dönüşmüş mü?

Shaded preview kabul edilmeden STL üretilmeyecektir.

## FAZ 10 — STL ve fiziksel baskı

Kontroller:

- Open edges
- Non-manifold edges
- Degenerate triangles
- Triangle orientation
- Relief height
- Minimum feature
- Print-risk
- Bambu Studio görünümü
- Fiziksel baskı
- Gerçek tanınabilirlik

Fiziksel baskıdan sonra ürün presetleri kalıcılaştırılabilir.
---

# 16. BAŞARI KRİTERLERİ

## 16.1 Teknik başarı

- Landmark provider güvenilir çalışmalıdır.
- Fitted mesh deterministik olmalıdır.
- Aynı giriş aynı yüz parametrelerini ve aynı mesh sonucunu üretmelidir.
- Depth map anatomik olarak anlamlı olmalıdır.
- Normal map yüzey yönlerini doğru temsil etmelidir.
- Shaded preview’de temel yüz anatomisi okunmalıdır.
- Open edges değeri `0` olmalıdır.
- Non-manifold edges değeri `0` olmalıdır.
- Degenerate triangle değeri `0` olmalıdır.
- Triangle orientation tutarlı olmalıdır.
- Print-risk sonucu `PASS` veya açıklanabilir kontrollü `WARN` olmalıdır.
- Metadata, kullanılan provider ve yüz parametrelerini izlenebilir biçimde kaydetmelidir.
- Gerçek ML provider başarısız olsa bile CORE testleri sentetik fixture ile çalışmalıdır.

## 16.2 Landmark başarısı

- Yüz tespiti ana portrede kararlı olmalıdır.
- Gözlük altında göz ve burun landmarkları kullanılabilir doğrulukta kalmalıdır.
- Burun ucu, burun kanatları, ağız köşeleri ve çene ucu güvenilir bulunmalıdır.
- Landmarklar görüntü boyutundan bağımsız normalize koordinatlar üretmelidir.
- Manuel ground-truth ile otomatik provider sonucu ölçülebilir olmalıdır.
- Projection error için kabul edilebilir hata sınırı testlerle tanımlanmalıdır.
- Düşük confidence durumları açıkça raporlanmalıdır.

## 16.3 Parametrik fitting başarısı

- Yüz genişliği ve yüksekliği kaynak kişiye yakın olmalıdır.
- Göz aralığı doğru korunmalıdır.
- Burun genişliği ve uzunluğu genelleştirilmemelidir.
- Burun çıkıntısı profil referansı varsa buna göre düzeltilmelidir.
- Ağız genişliği ve konumu korunmalıdır.
- Çene genişliği, uzunluğu ve çıkıntısı kişiye göre uyarlanmalıdır.
- Jawline genel şablon olarak kalmamalıdır.
- Yüz modeli hedef landmarklara belirlenen tolerans içinde oturmalıdır.
- Tek fotoğraf tahmini ile çoklu fotoğraf fitting sonucu metadata’da ayrılmalıdır.
- Parametreler anatomik sınırların dışına çıkmamalıdır.

## 16.4 Görsel başarı

- Kişi ilk bakışta tanınabilir olmalıdır.
- Yüz genel bir kubbe gibi görünmemelidir.
- Alın, burun kökü, burun sırtı ve burun ucu birbirinden okunmalıdır.
- Elmacık kemikleri ve yanak hacmi dengeli olmalıdır.
- Göz çukurları tamamen düzleşmemelidir.
- Ağız çevresi yalnız çizgi veya koyu ton olarak kalmamalıdır.
- Çene ve jawline silinmemelidir.
- Burun başka bir kişiye aitmiş gibi genelleşmemelidir.
- Gözlük ana yüz anatomisini bastırmamalıdır.
- Saç ve sakal yüz formuyla yarışmamalıdır.
- Fotoğraftaki ışık ve gölge doğrudan kabartıya dönüşmemelidir.
- Farklı sabit ışık yönlerinde yüz formu tutarlı görünmelidir.

## 16.5 Fiziksel ürün başarısı

- Rölyef minimum duvar ve detay sınırlarına uymalıdır.
- Base thickness baskı sırasında güvenli olmalıdır.
- Relief height yüz anatomisini koruyacak kadar yüksek olmalıdır.
- Burun ucu ve gözlük gibi çıkıntılar kırılgan olmamalıdır.
- İnce detaylar slicer tarafından tamamen yok edilmemelidir.
- STL Bambu Studio’da hatasız açılmalıdır.
- Fiziksel baskıda tanınabilirlik shaded preview’e yakın kalmalıdır.
- Baskı yönü ve destek ihtiyacı ürün profilinde tanımlanmalıdır.
- Baskı süresi ve filament miktarı ticari ürün hedefleriyle uyumlu olmalıdır.

## 16.6 Müşteri deneyimi başarısı

- Kullanıcı teknik maskeler hazırlamak zorunda kalmamalıdır.
- Kullanıcı landmark JSON düzenlemek zorunda kalmamalıdır.
- Kullanıcı terminal veya depth parametreleriyle uğraşmamalıdır.
- Normal durumda yalnız fotoğraf yükleme ve önizleme onayı yeterli olmalıdır.
- Düşük güven durumunda düzeltme adımı açık ve sınırlı olmalıdır.
- Kullanıcıya tek fotoğraf ve çoklu fotoğraf kalitesi arasındaki fark açıklanmalıdır.
- STL yalnız kullanıcı onayından sonra üretilmelidir.
---

# 17. RİSKLER VE KARŞI ÖNLEMLER

| Risk | Karşı önlem |
|---|---|
| Landmarklar gözlük altında bozulur | Manuel ground-truth karşılaştırması, confidence ölçümü ve düşük güven fallback |
| Tek fotoğraf profil bilgisini vermez | Parametrik prior ve çoklu fotoğraf seçeneği |
| Yan veya üç çeyrek fotoğraf yanlış sınıflandırılır | View-type doğrulaması ve baş pozu kontrolü |
| Parametrik model yüzü fazla genelleştirir | Silüet, burun, jawline ve profil parametrelerini ayrı fitting |
| Burun ve çene bas-relief compression sırasında ezilir | Bölgesel compression ve anatomik koruma maskeleri |
| Göz çukurları aşırı derinleşir | Minimum ve maksimum bölgesel depth sınırları |
| Saç, sakal veya gözlük ana anatomiyi bastırır | Ayrı düşük-genlikli katmanlar ve katman bazlı limitler |
| Fotoğraf ışığı geometriye dönüşür | Ana hacmi yalnız parametrik yüz modelinden üretmek |
| Landmark provider lisansı uygun değildir | Lisans kapısı geçilmeden entegrasyon yapılmaması |
| Parametrik yüz modeli ticari kullanıma uygun değildir | Ticari kullanım ve yeniden dağıtım koşullarının yazılı doğrulanması |
| Ağır ML bağımlılığı ana ortamı bozar | Ayrı `.venv_portrait` veya bağımsız provider servisi |
| Python veya Apple Silicon uyumsuzluğu çıkar | Spike aşamasında kurulum ve çalışma testi |
| Model dosyası çok büyük olur | Hafif provider veya ayrı model paketi değerlendirmesi |
| Provider internet bağlantısı gerektirir | Offline çalışma önceliği |
| Gerçek ML modeli testleri kırar | CORE testlerinde stub ve sentetik fixture kullanımı |
| Otomatik fitting deterministik olmaz | Sabit seed, sabit optimizasyon sırası ve deterministik toleranslar |
| Aşırı parametreler anatomiyi bozar | Anatomik alt ve üst sınırlar |
| Çoklu fotoğraflar aynı kişiye ait değil veya uyumsuzdur | Kimlik tutarlılığı ve görüntü kalite kontrolü |
| Shaded preview tek ışıkta yanıltıcı olur | Birden fazla sabit ışık yönüyle doğrulama |
| Preview iyi görünür, fiziksel baskı başarısız olur | Minimum feature, print-risk ve fiziksel baskı kalibrasyonu |
| Rölyef yüksekliği fazla düşük kalır | Profil bazlı minimum relief height |
| Rölyef yüksekliği fazla yüksek olur | Bas-relief compression ve ürün profili sınırları |
| Burun ucu veya gözlük kırılgan olur | Minimum feature ve lokal slope sınırları |
| Mesh açık veya non-manifold olur | Mevcut validator, repair ve regresyon testleri |
| Özel portre verileri Git’e girer | Private data ignore politikası ve staged diff kontrolü |
| Kişiye özel koordinatlar CORE’a hard-code edilir | Tüm kalibrasyon verilerini fixture ve metadata içinde tutmak |
| Manuel landmark aracı kalıcı müşteri akışına dönüşür | Manuel aracı yalnız ground-truth ve fallback olarak sınırlamak |
| Eski başarısız yöntemler yeniden açılır | Bu planı ve kapatılmış deneyleri mimari karar olarak korumak |
| Kullanıcıdan gereksiz teknik işlem istenir | Otomatik akış ve sade düşük güven düzeltme ekranı |
| STL, görsel onaydan önce üretilir | Shaded preview kabul kapısını zorunlu tutmak |
---

# 18. TEST VE GELİŞTİRME DİSİPLİNİ

Her kalıcı paket şu sırayla uygulanacaktır:

1. Hedef test hazırlanır.
2. Üretim kodu eklenir veya değiştirilir.
3. Hedef testler çalıştırılır.
4. İlgili test paketi çalıştırılır.
5. Tam regresyon çalıştırılır.
6. `python -m py_compile` ile sözdizimi doğrulanır.
7. `git diff --check` çalıştırılır.
8. Diff ayrıntılı incelenir.
9. Yalnız hedef dosyalar stage edilir.
10. Staged diff yeniden incelenir.
11. Commit oluşturulur.
12. Çalışma ağacının temiz olduğu doğrulanır.

Geliştirme kuralları:

- Bir seferde yalnızca bir kontrollü paket uygulanacaktır.
- Önce mevcut dosyalar ve sözleşmeler incelenecektir.
- Gereksiz mimari yeniden yazım yapılmayacaktır.
- Kişiye özel ROI, landmark veya profil koordinatları CORE içine hard-code edilmeyecektir.
- Özel portre fotoğrafları, maskeler, landmark fixture’ları ve deneysel görseller Git’e eklenmeyecektir.
- Ağır ML bağımlılıkları ana `.venv` içine kontrolsüz biçimde kurulmayacaktır.
- Gerçek landmark provider, CORE testlerinin zorunlu bağımlılığı olmayacaktır.
- CORE testlerinde stub ve sentetik fixture kullanılacaktır.
- Gerçek provider spike çalışmaları ayrı ortamda yürütülecektir.
- Lisansı doğrulanmamış model veya veri dosyası projeye eklenmeyecektir.
- Görsel deney sonucu kabul edildiğinde kalıcı regresyon testi veya teknik rapor hazırlanacaktır.
- Shaded preview kabul edilmeden STL üretilmeyecektir.
- Başarısız ve kapatılmış yöntemler yeni katsayılarla tekrar açılmayacaktır.
- Her commit tek bir anlaşılır teknik amacı temsil edecektir.
- Tam regresyon başarısızsa commit yapılmayacaktır.

Terminal çalışma düzeni:

- Tüm Bash komutları sözdizimi vurgulu kod penceresinde verilecektir.
- Çıktı üreten her komut şu biçimde loglanacaktır:

`2>&1 | tee /tmp/atlas_last.log`

- Her çıktı komutundan sonra ayrı olarak şu komut verilecektir:

`pbcopy < /tmp/atlas_last.log`

- Uzun dosya değişikliklerinde dosya içeriği eksiksiz ve kontrollü biçimde verilecektir.
- Dosya stage edilmeden önce özel veri ve deney dosyalarının Git durumuna girmediği kontrol edilecektir.
---

# 19. UYGULAMA ÖNCELİK SIRASI

1. Bu mimari planın eksiksiz kaydedilmesi
2. Dosyanın Git durumunun doğrulanması
3. Mevcut roadmap ve mimari belgelerle çakışma kontrolü
4. `AtlasPortraitLandmarkResult` immutable sözleşmesi
5. Landmark provider interface
6. Sentetik landmark fixture
7. Manuel ground-truth landmark seti
8. MediaPipe Face Landmarker spike
9. Otomatik landmark sonucunun ground-truth ile karşılaştırılması
10. Landmark hata metriğinin ve kabul eşiğinin tanımlanması
11. Parametrik yüz modeli adaylarının araştırılması
12. Lisans ve ticari kullanım kararının belgelenmesi
13. Parametrik yüz modeli sözleşmesi
14. Nötr yüz mesh fixture’ı
15. Frontal landmark-driven fitting
16. Tek fotoğraf fallback davranışı
17. Çoklu görünüş fitting
18. Burun ve çene projection desteği
19. Frontal depth renderer
20. Normal map üretimi
21. Bas-relief compression
22. Çoklu ışık yönünde shaded preview
23. Yüz dış silüet düzeltmesi
24. Saç çizgisi katmanı
25. Kaş katmanı
26. Gözlük katmanı
27. Sakal ve bıyık katmanı
28. Boyun ve kıyafet katmanı
29. Mevcut Relief Engine ile entegrasyon
30. Product profile entegrasyonu
31. Quality report entegrasyonu
32. Print-risk entegrasyonu
33. Shaded preview kabul kapısı
34. Manifold mesh üretimi
35. STL üretimi
36. Bambu Studio doğrulaması
37. İlk fiziksel baskı
38. Baskı sonrası tanınabilirlik değerlendirmesi
39. Profil parametrelerinin kalibrasyonu
40. Kalıcı portre ürün profili kataloğu

İlk uygulanacak teknik paket:

> Provider’dan bağımsız immutable `AtlasPortraitLandmarkResult` sözleşmesi.

Bu ilk pakette henüz:

- MediaPipe kurulmayacaktır.
- Model indirilmeyecektir.
- Parametrik yüz mesh’i oluşturulmayacaktır.
- Depth map üretilmeyecektir.
- STL üretilmeyecektir.

Önerilen ilk dosyalar:

- `CORE/atlas_portrait_landmark_result.py`
- `Test/test_portrait_landmark_result.py`

İlk sözleşmenin zorunlu alanları:

- `image_width`
- `image_height`
- `landmarks`
- `confidence`
- `provider_id`
- `metadata`

Landmark koordinatları normalize `0..1` olarak saklanacaktır.

Gerekirse piksel koordinatları sözleşme tarafından deterministik biçimde hesaplanacaktır.
---

# 20. MEVCUT KESİN NOKTA VE SIRADAKİ ADIM

Son temiz proje durumu:

- Commit: `52ce7e5 Integrate relief product profile`
- Son tam regresyon: `854 passed in 4.87s`
- Ana çalışma ağacında özel portre dosyaları Git dışında tutulmaktadır.
- Mevcut 2.5D Relief Engine korunacaktır.
- Değiştirilecek temel unsur, portreye ait ana depth kaynağıdır.

Son başarısız deney:

- `PORTRAIT_GRAPHIC_V1_DEPTH_SHADED_V3.png`

Kesin sonuç:

- Burun, yanak, ağız ve çene gerçek yüzey olarak okunmadı.
- Sentetik Gaussian anatomy prior başarısız kabul edildi.
- Yeni katsayı, gamma, smoothing, ambient veya slope denemesi yapılmayacak.
- Depth Anything V2 yeniden açılmayacak.
- Bambu depth ve fotoğraf hibriti yeniden açılmayacak.
- `HYBRID V3` üretilmeyecek.
- Shaded preview kabul edilmeden STL üretilmeyecek.

Yeni ana teknik yön:

> Portre rölyefinin ana yüz geometrisi, landmarklarla kişiye uyarlanmış parametrik 3B yüz yüzeyinden üretilecektir.

Manuel landmark araçlarının rolü:

- Kalibrasyon
- Ground-truth üretimi
- Otomatik provider doğrulaması
- Düşük güven fallback

Manuel landmark işaretleme nihai müşteri iş akışı değildir.

Sıradaki kontrollü teknik paket:

1. Mevcut landmark click-tool dosyalarının yapısı incelenecek.
2. Provider’dan bağımsız immutable `AtlasPortraitLandmarkResult` sözleşmesi tasarlanacak.
3. Önce test dosyası hazırlanacak.
4. Sonra üretim sözleşmesi uygulanacak.
5. Hedef testler çalıştırılacak.
6. İlgili testler çalıştırılacak.
7. Tam regresyon çalıştırılacak.
8. Diff ve Git durumu kontrol edilecek.
9. Yalnız hedef dosyalar commit edilecek.

Bu aşamada yapılmayacaklar:

- MediaPipe kurulumu
- Model indirme
- Parametrik yüz mesh’i seçimi
- Depth map üretimi
- Accessory layer üretimi
- STL üretimi
- Fiziksel baskı

Nihai teknik ilke:

> 3B yüz formu + 2B kimlik ve detay bilgisi = tanınabilir portre rölyefi.

Bu belge, ATLAS_ENGINE portre rekonstrüksiyonu için geçerli ana eylem planıdır.
