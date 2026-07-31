# ATLAS_ENGINE DEVİR — 2026-07-23

Bu belge, ATLAS_ENGINE’in 3D coğrafi modelleme motoru ile 2.5D kişiselleştirilmiş rölyef motorunun güncel durumunu, bu geliştirme penceresinde edinilen teknik tecrübeleri ve yeni pencerede devam edilecek kesin noktayı devretmektedir.

---

## Yeni Pencereye Başlangıç Cümlesi

**ATLAS_ENGINE devir dosyasındaki 2026-07-23 mola noktasından devam edelim. Önceliğimiz yalnız 2.5D portre rölyef hattıdır; mevcut structure/detail normal ayrımı, semantic detail kontrolü ve screened Poisson mimarisi korunacak, sıradaki işlem landmark tabanlı gerçek yüz bölgelerinin oluşturulması olacaktır.**

---

# 1. ATLAS Projesinin Genel Tanımı

## 1.1 ATLAS 3D Coğrafi Modelleme Projesi

- Gerçek coğrafi verilerden fiziksel olarak basılabilir 3D modeller üretme
- OSM tabanlı bina, yol, park, kale, sur ve landmark geometrileri
- SRTM ve diğer yükseklik kaynaklarından terrain üretimi
- Foundation-first şehir modeli mimarisi
- Manifold STL üretimi
- Mesh doğrulama ve onarım
- Anıtkabir, Rumeli Hisarı, Hohenzollern ve Burghausen test alanları
- Castle Engine
- Building-part desteği
- Terrain, su, doğa, bina ve landmark katmanları
- Uzun vadeli kişiselleştirilmiş ürün aileleri:
  - My Life Map
  - Our Love Map
  - Family Heritage
- Temel marka ilkesi:
  - **Every important memory has a location.**

## 1.2 ATLAS 2.5D Kişiselleştirilmiş Rölyef Projesi

- Müşteri portre fotoğrafından fiziksel rölyef ürün üretme
- İlk ticari hedef:
  - tek portre fotoğrafı
  - kabul edilebilir shaded preview
  - müşteri onayı
  - manifold STL
- Gelecekte 1–3 kişilik kompozisyon desteği
- Gelecekte kontrollü gerçekçi veya hafif karikatürize kompozisyon
- Şimdilik arka plan, tema ve dekoratif nesne yok
- Shaded preview kabul edilmeden STL üretimi yok

---

# 2. Bu Penceredeki Ana Hedef

## Tek portreden kimliği koruyan 2.5D yüz rölyefi

- Baş hacmi düzleşmemeli
- Alın, yanak, burun, dudak ve çene okunmalı
- Gözlük yüz anatomisi gibi aşırı kabarmamalı
- Fotoğraf ışığı doğrudan geometriye dönüşmemeli
- Tişört kırışıkları ve arka plan artefaktları taşınmamalı
- Yüzey şerit, dalga veya fingerprint artefaktı üretmemeli
- Çıktı ticari rölyef önizlemesine yaklaşmalı

---

# 3. Kullanılan Gerçek Portre Verileri

## Kaynak görüntüler

- `Data/RELIEF/real_portrait_01/portrait_crop.png`
- `Data/RELIEF/real_portrait_01/portrait_crop_320x400.png`
- `Data/RELIEF/real_portrait_01/subject_mask.png`
- `Data/RELIEF/real_portrait_01/subject_mask_320x400.png`
- `Data/RELIEF/real_portrait_01/atlas_real_portrait_01_square.png`
- `Data/RELIEF/real_portrait_01/ai_depth_16bit.png`
- `Data/RELIEF/real_portrait_01/dsine_normal_map.npy`

## Temel boyutlar

- Portre çalışma boyutu: `320 × 400`
- DSINE normal haritası: `400 × 320 × 3`
- Normal dtype: `float32`
- AI depth: 16-bit grayscale

## Kullanılan yüz sınırı

```python
FACE_BOUNDS = (
    55,
    255,
    78,
    244,
)
# 4. Harici Model Deneyleri

## 4.1 Depth Anything / Genel Monoküler Depth

- Genel baş ve gövde hacmi üretildi
- Kimlik ayrıntıları yetersiz kaldı
- Göz, yanak, dudak ve çene düzleşti
- Tek başına ticari portre rölyefi için yeterli bulunmadı

## 4.2 Depth Pro

### Kurulum

- Repo:
  - `/Users/Kubi/ml-depth-pro`
- Ortam:
  - `/Users/Kubi/.venv-depth-pro`
- Checkpoint:
  - `/Users/Kubi/ml-depth-pro/checkpoints/depth_pro.pt`

### Sonuç

- Dış siluet daha temiz
- Baş ve gövde hacmi kararlı
- Burun ve ağızda hafif iyileşme
- Göz, yanak, dudak ve çene hâlâ düz
- Daha yüksek çözünürlük anlamlı sıçrama sağlamadı

### Karar

- Kaba ve kararlı anchor/base volume olarak kullanılabilir
- Tek başına portre kimliği üretmez

## 4.3 DSINE Normal Estimation

### Kurulum

- Repo:
  - `/Users/Kubi/DSINE`
- Commit:
  - `ef0c2af`
- Ortam:
  - `/Users/Kubi/.venv-depth-pro`
- Checkpoint:
  - `/Users/Kubi/DSINE/projects/dsine/checkpoints/exp001_cvpr2024/dsine.pt`

### Yerel değişiklikler

- MPS fallback eklendi
- Float32 NPY çıktı desteği eklendi
- Yerel data ve experiment yolları tanımlandı

### Sonuç

DSINE şimdiye kadarki en değerli yüz formu sinyalini verdi:

- kafa küresi
- alın eğimi
- yanaklar
- burun
- ağız ve çene
- kulak ve yüz yönelimi

### Sorunlar

- Gözlük gradyanları fazla güçlü
- Burun kökü ve burun altı keskin
- Philtrum ve üst dudak bıyık/oyuk etkisi oluşturuyor
- Tişört ve subject sınırı artefakt taşıyor

### Karar

- DSINE TILT ve yönlü normal alanı korunacak
- Yeni genel model kurulmayacak
- DSINE son genel model deneyi olarak kabul edildi

---

# 5. Reddedilen Yaklaşımlar

## 5.1 Luminance tabanlı height map

- Fotoğraf ışığı geometriye dönüştü
- Yüz düzleşti
- Kenar embossing oluştu
- Tişört kırışıkları büyüdü
- Ticari kalite sağlamadı

## 5.2 Fotoğraf high-pass detail ekleme

- Cilt kazınmış gibi göründü
- Gözlük aşırı baskınlaştı
- Yüzey gürültülü oldu
- Kimlik iyileşmedi

## 5.3 Tam DSINE normal entegrasyonu

- Yüz anatomisi üretildi
- Fakat:
  - gözlük aşırı yükseldi
  - ağız ve philtrum bozuldu
  - tişört güçlendi
  - maske kenarı sızdı

## 5.4 Height sonrası weight map çarpımı

- Ağız siyah çukura dönüştü
- Alt dudak beyaz ridge oldu
- Fingerprint/dalga artefaktı oluştu
- Reddedildi

## 5.5 Confidence-weighted kümülatif X/Y entegrasyon

- Yatay ve dikey şeritler oluştu
- Matematiksel olarak kararsız bulundu
- Tekrar kullanılmayacak

## 5.6 AI depth + skaler DSINE TILT additive composite

- Stabil kaldı
- Ancak yüz anatomisinde belirgin iyileşme olmadı
- Skaler tilt, normal yön bilgisini kaybetti
- Reddedildi

## 5.7 Global DSINE gradient calibration

- AI depth gradient ölçeğine indirildi
- Sonuç aşırı yumuşadı
- Yüz iç formu kayboldu
- Anchor, DSINE için doğru global ölçek referansı değil

## 5.8 Face-interior gradient calibration

- Kafa kenarı ve aksesuarlar azaltıldı
- Ancak sonuç yine fazla yumuşak kaldı
- Anchor’ın zayıf yüz içi gradyanı DSINE’i gereğinden fazla küçülttü
- Reddedildi

## 5.9 Sabit oranlı Gaussian semantik bölgeler

- Tişört detail katkısı azaltıldı
- Yüz dışı detail sınırlandı
- Ancak gözlük, burun ve ağız gerçek konumlarıyla tam örtüşmedi
- Gerçek landmark tabanlı semantik bölgelere geçme kararı alındı

---

# 6. Başarılı Teknik Yönler

## 6.1 AI depth anchor

- Kafa ve gövde kütlesi için kararlı taban
- Dış silueti koruyor
- Yüz iç formu zayıf
- Tek başına yeterli değil

## 6.2 Face anchor enhancement

- Anchor içindeki mevcut düşük/orta frekanslı formu hafifçe güçlendiriyor
- Yeni anatomi yaratmıyor
- Screened Poisson anchor’ı olarak korunabilir

## 6.3 Screened Poisson integration

- Kümülatif entegrasyondaki şeritleri ortadan kaldırdı
- Anchor’a bağlı kararlı çözüm üretti
- İlk uncalibrated sürüm şimdiye kadarki en güçlü anatomik sonucu verdi
- Aşırı DSINE gradyanlarının ayrıca kontrol edilmesi gerektiği görüldü

## 6.4 Structure/detail normal decomposition

- DSINE normal alanı gradient-space içinde ayrıldı
- Geniş yüz formu structure katmanında kaldı
- İnce ve sert detaylar detail katmanına ayrıldı
- Sentetik testte yüksek frekanslı ridge enerjisinin yaklaşık `%89`u korundu
- Structure + detail gradyanları özgün girdiyi sayısal hassasiyetle yeniden kurdu

## 6.5 Detail-only gradient limiting

- Structure katmanına dokunulmadı
- Yalnız detail gradyan tepeleri sınırlanmaya başlandı
- Gradyan yönü korundu
- Yüz anatomisi global kalibrasyona göre daha iyi korundu

## 6.6 Semantic detail weighting

- Detail katkısı büyük ölçüde yüz bölgesine sınırlandı
- Tişört ve gövde detayları azaltıldı
- Subject sınırı detail katkısı düşürüldü
- Sabit Gaussian yaklaşımının gerçek landmark olmadan yetersiz olduğu doğrulandı
# 7. Bu Pencerede Eklenen Çekirdek Modüller

## Height ve normal entegrasyonu

- `CORE/atlas_relief_normal_height_integrator.py`
- `CORE/atlas_relief_screened_normal_integrator.py`

## Anchor ve detail kompozisyonu

- `CORE/atlas_relief_detail_weight_map.py`
- `CORE/atlas_relief_face_detail_composer.py`
- `CORE/atlas_relief_face_anchor_enhancer.py`

## Kalibrasyon maskeleri

- `CORE/atlas_relief_face_interior_calibration_mask.py`
- `CORE/atlas_relief_face_semantic_detail_weight_map.py`

## Normal decomposition ve limiting

- `CORE/atlas_relief_normal_structure_detail_decomposer.py`
- `CORE/atlas_relief_normal_gradient_limiter.py`

---

# 8. Bu Pencerede Eklenen Testler

- `Test/test_relief_normal_height_integrator.py`
- `Test/test_relief_screened_normal_integrator.py`
- `Test/test_relief_detail_weight_map.py`
- `Test/test_relief_face_detail_composer.py`
- `Test/test_relief_face_anchor_enhancer.py`
- `Test/test_relief_face_interior_calibration_mask.py`
- `Test/test_relief_normal_structure_detail_decomposer.py`
- `Test/test_relief_normal_gradient_limiter.py`
- `Test/test_relief_face_semantic_detail_weight_map.py`

---

# 9. Focused Test Sonuçları

## Normal height integrator

- `16 passed`

## Screened normal integrator

- `15 passed`

## Detail weight map

- `21 passed`

## Face detail composer

- `22 passed`

## Face anchor enhancer

- `18 passed`

## Face interior calibration mask

- `23 passed`

## Normal structure/detail decomposer

- `21 passed`

## Normal gradient limiter

- `22 passed`

## Face semantic detail weight map

- `34 passed`
# 10. En İyi Görsel Sonuçların Sıralaması

## 1. Structure + limited detail screened

Şimdiye kadarki en doğru teknik yön:

- kafa hacmi korunuyor
- alın, burun, yanak ve çene okunuyor
- global kalibrasyon kadar düzleşmiyor
- şerit artefaktı yok
- gözlük ve ağız hâlâ fazla güçlü

## 2. İlk uncalibrated screened Poisson

- En güçlü yüz anatomisi
- Fakat:
  - gözlük aşırı
  - burun keskin
  - ağız/philtrum bozuk
  - tişört ve maske kenarı güçlü

## 3. Enhanced anchor

- En stabil anchor
- Fakat yüz anatomisi hâlâ düz

## 4. Global ve face-interior calibrated screened

- Fazla yumuşak
- Üretim adayı değil

## 5. Semantic detail screened

- Tişört ve sınır detail’i daha temiz
- Ancak sabit oranlı semantik bölgeler gerçek gözlük/burun/ağız konumlarıyla örtüşmedi
- Önceki structure + limited detail sürümünden üstün değil
# 11. Araştırmadan Çıkan Teknik Sonuçlar

## Uluslararası ortak çözüm modeli

Araştırılan ülke ve çalışma alanları:

- ABD
- Çin
- Japonya
- Almanya
- İngiltere
- Güney Kore

Ortak başarılı yaklaşım:

```text
kararlı kaba yüz hacmi
+ structure normal katmanı
+ kontrollü detail normal katmanı
+ semantik yüz bölgeleri
+ robust / weighted integration
```

## Temel ders

Problem yalnızca “DSINE gradyanları fazla büyük” değildir.

Asıl problem:

```text
yararlı yüz yapısı
+
zararlı aksesuar/kenar detayı
aynı normal alanında karışmıştır
```

## Doğru çözüm yönü

```text
Enhanced AI depth anchor
+
DSINE structure normals
+
landmark kontrollü düşük genlikli detail normals
+
weighted robust screened Poisson
```
# 12. Güncel Teknik Tecrübeler

## Yüz formu ve kimlik

- Monoküler depth genel hacmi verir
- Normal map yüz eğimini verir
- Kimlik için ikisinin birlikte kullanılması gerekir

## Gözlük

- Gözlük çerçevesi anatomi değildir
- Sert kenar gradyanları detail ve bazen structure katmanına sızar
- Gözlük bölgesi gerçek landmark veya tespit edilmiş bölgeyle bastırılmalı

## Burun

- Burun gövdesi structure olarak korunmalı
- Burun deliği ve burun altı yüksek frekanslı negatif detail olarak sınırlanmalı

## Ağız ve philtrum

- Üst dudak ve philtrum koyu görüntü çizgisi olarak depth’e aktarılmamalı
- Dudak hacmi ile dudak çizgisi ayrı ele alınmalı
- Sabit yatay Gaussian bant yeterli değil

## Yanak ve alın

- Geniş düşük frekanslı structure korunmalı
- Global gradyan küçültme yanak ve alın formunu yok ediyor

## Subject mask

- Maskenin bozuk kenarı structure katmanına sızabiliyor
- Decomposition öncesinde mask-aware smoothing veya içe daraltılmış structure mask gerekebilir

## Kıyafet

- Tişört detail’i ticari portre rölyefinde minimum olmalı
- Gövde için coarse anchor yeterli
- DSINE detail katkısı yüz dışında sıfıra yakın olmalı
# 13. Kesin Mola Noktası

## Son tamamlanan paket

- `CORE/atlas_relief_face_semantic_detail_weight_map.py`
- `Test/test_relief_face_semantic_detail_weight_map.py`
- Focused test: `34 passed in 0.05s`

## Son görsel deneme

DSINE  
→ structure/detail decomposition  
→ semantic detail weight  
→ detail gradient limiter  
→ enhanced anchor  
→ screened Poisson

## Son görsel karar

- Semantic map tişört ve sınır detail’ini azalttı
- Gözlük, burun ve ağız artefaktları tam çözülmedi
- Sabit oranlı Gaussian yüz bölgeleri yetersiz
- Gerçek 2D landmark tabanlı bölgeler gerekli
# 14. Yeni Pencerede Yapılacak İlk Adım

## Yeni paket

```text
Test/test_relief_face_landmark_regions.py
CORE/atlas_relief_face_landmark_regions.py
```

## Paket amacı

Önceden elde edilmiş 2D yüz landmark koordinatlarından gerçek yüz bölgeleri oluşturmak:

- eye/glasses region
- nose bridge
- nose body
- nostril/base region
- philtrum
- upper lip
- lower lip
- left cheek
- right cheek
- chin
- face interior
- face boundary falloff

## Önemli mimari sınır

Bu modül:

- FLAME kullanmayacak
- parametric face modeline dönmeyecek
- 3D kafa rekonstrüksiyonu yapmayacak
- yeni genel model kurmayacak
- yalnız 2.5D rölyef detail/structure ağırlık bölgeleri üretecek

## İlk test sözleşmesi

- Aynı görüntü boyutunda region maskeleri
- Float64 ve `0..1` aralığı
- Landmark dışı alanda sıfır
- Eye/glasses bölgesi gerçek göz koordinatlarını takip etmeli
- Nose base gerçek burun altını takip etmeli
- Philtrum dudak ve burun arasında kalmalı
- Cheek bölgeleri gözlük ve ağızdan ayrı olmalı
- Chin alt dudak altında kalmalı
- Bozuk veya eksik landmark girdisi reddedilmeli

---

# 15. Sonraki Teknik Yol Haritası

## Adım 1

- Landmark region contract
- Focused kırmızı test
- Minimal production implementation

## Adım 2

- Gerçek portre için 2D landmark koordinatlarını elde etme
- Landmark bölgelerini panelde doğrulama

## Adım 3

- Detail semantic weight map’i landmark bölgeleriyle üretme
- Sabit oranlı Gaussian bölgeleri kaldırma veya fallback olarak tutma

## Adım 4

- Structure katmanında gözlük/burun kenarı sızıntısını kontrol etme
- Mask-aware structure decomposition geliştirme

## Adım 5

- Landmark-controlled structure + detail normal birleşimi
- Screened Poisson shaded preview

## Adım 6

- Görsel kabul kriterleri:
  - baş hacmi
  - yanak
  - alın
  - burun
  - dudak
  - çene
  - gözlük artefaktı
  - kıyafet temizliği
  - subject sınırı

## Adım 7

- Mevcut FFT screened solver yeterli değilse:
  - SciPy sparse weighted screened Poisson
  - spatially varying confidence
  - robust Huber/Charbonnier weighting
  - subject-shaped domain

## Adım 8

- Shaded preview kabul edilirse relief pipeline entegrasyonu

## Adım 9

- Full regression

## Adım 10

- Commit

## Adım 11

- Yalnız shaded preview ticari olarak kabul edilirse STL üretimi

---

# 16. Çalışma Disiplini

- Test-first
- Tek mikro adım
- Unrelated dosyalara dokunma
- `git add .` kullanma
- Her output komutu:
  - `2>&1 | tee /tmp/atlas_last.log`
- Her output komutundan sonra:
  - `pbcopy < /tmp/atlas_last.log`
- Syntax:
  - `.venv/bin/python -m py_compile`
- Focused test
- `git diff --check`
- Tam regresyon commit öncesinde
- Shaded preview kabul edilmeden STL yok
# 17. Güncel Git Durumu

Bu devir hazırlanırken yeni relief dosyaları henüz untracked durumdadır.

## Untracked CORE dosyaları

- `CORE/atlas_relief_detail_weight_map.py`
- `CORE/atlas_relief_face_anchor_enhancer.py`
- `CORE/atlas_relief_face_detail_composer.py`
- `CORE/atlas_relief_face_interior_calibration_mask.py`
- `CORE/atlas_relief_face_semantic_detail_weight_map.py`
- `CORE/atlas_relief_normal_gradient_limiter.py`
- `CORE/atlas_relief_normal_height_integrator.py`
- `CORE/atlas_relief_normal_structure_detail_decomposer.py`
- `CORE/atlas_relief_screened_normal_integrator.py`

## Untracked TEST dosyaları

- `Test/preview_relief_product_profile_comparison.py`
- `Test/test_relief_detail_weight_map.py`
- `Test/test_relief_face_anchor_enhancer.py`
- `Test/test_relief_face_detail_composer.py`
- `Test/test_relief_face_interior_calibration_mask.py`
- `Test/test_relief_face_semantic_detail_weight_map.py`
- `Test/test_relief_normal_gradient_limiter.py`
- `Test/test_relief_normal_height_integrator.py`
- `Test/test_relief_normal_structure_detail_decomposer.py`
- `Test/test_relief_screened_normal_integrator.py`

## Commit uyarısı

- Bu dosyalar henüz toplu olarak commit edilmemelidir
- Önce landmark region paketi ve gerçek portre doğrulaması yapılmalıdır
- Ardından focused testler ve tam regresyon çalıştırılmalıdır
- `git add .` kesinlikle kullanılmamalıdır

---

# 18. Yeni Pencere İçin Kesin Talimat

Yeni pencerede doğrudan şu noktadan devam edilmelidir:

```text
Mevcut structure/detail normal decomposition,
detail-only gradient limiting,
enhanced AI-depth anchor
ve screened Poisson mimarisi korunacak.

Sıradaki tek işlem:
Test/test_relief_face_landmark_regions.py
için kırmızı sözleşme oluşturmak.
```

Her teknik adım öncesinde şu cümle aynen yazılmalıdır:

**Bu adım, 2.5D relief dışında bir yöne gitmek için hiçbir talimat veya eylem içermemektedir.**
## 2.5D PORTRE RÖLYEFİ — EK DEVİR NOTU

Önceki devir noktasından sonra MediaPipe tabanlı gerçek yüz landmark çıkarımı tamamlandı. Gözlük, burun, dudak, yanak, çene, yüz içi ve yüz sınırı için yumuşak maskeler üretildi. Landmark tabanlı semantic detail control, structure confidence, normal confidence applier, minimum retention ve piksel bazlı retention map mevcut preview zincirine bağlandı.

Yüz içinde oluşan ikinci oval/halo artefaktının `face_interior`, `face_boundary_falloff` ve yüz dışı structure cutoff kullanımından kaynaklandığı doğrulandı. Bu global sınır baskılamaları structure yolundan çıkarıldı ve halo problemi giderildi.

Gözlük için yumuşak bölge + güçlü çekirdek suppression, lokal retention override ve burun–philtrum–dudak bölgesi için lokal retention denendi. Bu değişiklikler yeni halo üretmedi ve yüzün genel hacmini korudu; ancak ticari kalite açısından görsel faydaları sınırlı kaldı.

Flat normals + enhanced anchor kullanılan anchor-only teşhis kolunda gözlük/cam izi görülmeye devam etti. Böylece gözlük, dudak, gölge ve benzeri görünüş bilgilerinin yalnız DSINE normallerinden değil, AI-depth anchor’dan da geometriye sızdığı doğrulandı.

Ana teknik sorun:

`Monoküler portre rölyefinde appearance-to-geometry leakage`

Tek fotoğraftan üretilen AI-depth ve normal haritaları gözlük, cam, gölge, dudak çizgisi, philtrum ve kıyafet desenini gerçek fiziksel geometri olarak yorumlayabiliyor. Bu sorun yalnız blur, threshold, confidence veya retention ayarıyla güvenilir biçimde çözülemiyor.

Bu nedenle aşağıdaki üretim yolu donduruldu:

`tek fotoğraf → AI depth + DSINE structure/detail → confidence/retention düzeltmeleri → ana yüz geometrisi`

Silinen FLAME dosyaları yeniden oluşturulmayacak ve önceki FLAME uygulamasına geri dönülmeyecek. Ancak ana yüz geometrisinin güvenilir bir 3B yüz/baş rekonstrüksiyonundan gelmesi gerektiği kararı korunacak. Kullanılacak sistemin FLAME olması zorunlu değildir.

Kilitlenen yeni yön:

`çoklu fotoğraf veya kısa video → güvenilir 3B yüz/baş rekonstrüksiyonu → rölyefe özgü derinlik sıkıştırma → seçici düşük genlikli mikrodetay → ayrı aksesuar işlemesi → shaded preview → kalite kontrolü → STL`

Tercih edilen müşteri girdisi:

- önden fotoğraf
- yaklaşık 25–35° sol fotoğraf
- yaklaşık 25–35° sağ fotoğraf

Alternatif olarak 5–10 saniyelik yavaş baş çevirme videosu kullanılabilir. Tek fotoğraf yalnız düşük güvenli veya best-effort mod olarak değerlendirilecek.

Yeni katman sorumlulukları:

- Ana alın, yanak, burun, çene ve kafa hacmi: güvenilir 3B yüz/baş rekonstrüksiyonu
- Baş silueti, saç, kulak ve geniş derinlik düzeni: yardımcı AI-depth
- İnce yüzey ayrıntısı: DSINE veya benzeri normal kaynağı, yalnız düşük genlikli residual detail
- Gözlük camı: alttaki yüz geometrisini göstermeli
- Gözlük çerçevesi: ayrı, ince ve düşük profilli aksesuar katmanı
- Yansıma, gölge ve kıyafet deseni: geometriye dönüşmemeli

İlk ticari sürüm tamamen otomatik olmak zorunda değildir:

`otomatik 3B rekonstrüksiyon → otomatik relief projection → otomatik shaded preview → kısa operatör kalite kontrolü → STL`

Şu an durulan kesin nokta:

- Halo problemi çözüldü.
- Landmark ve lokal confidence/retention altyapısı çalışıyor.
- Gözlük ve burun–ağız lokal tuning yaklaşımının faydası sınırlı bulundu.
- Anchor neutralizer geliştirilmedi.
- FLAME uygulamasına geri dönülmedi.
- AI-depth + DSINE ana geometri yolu donduruldu.
- STL aşamasına geçilmedi.
- Sonraki adım kod yazmak değil, ticari kullanıma uygun 3B yüz/baş rekonstrüksiyon motorlarını kısa listeleyip karşılaştırmaktır.

Seçim kriterleri:

- ticari lisans
- Mac uyumu
- yerel çalışma veya güvenli API
- çoklu görüntü/video desteği
- kimlik koruma
- gözlük ve yüz örtücü aksesuar davranışı
- mesh kalitesi
- işlem süresi
- rölyef projeksiyonuna uygunluk