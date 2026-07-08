# ATLAS_ENGINE_CLEANUP_PLAN.md

**Belge Sürümü:** 1.0  
**Tarih:** 2026-07-07  
**Proje:** ATLAS ENGINE  
**Durum:** Aktif Geliştirme

---

# GİRİŞ

ATLAS Engine artık deneysel bir proje olmaktan çıkmış, gerçek ürün üretme aşamasına gelmiştir.

Bu nedenle bundan sonraki geliştirme sürecinde temel hedef **yeni özellik eklemek değil**, mevcut çekirdeği güvenilir, hızlı, okunabilir ve sürdürülebilir hale getirmektir.

Bugüne kadar yapılan geliştirmeler sayesinde;

- gerçek arazi (SRTM) kullanılabilmektedir,
- şehir modeli üretilebilmektedir,
- terrain ve binalar aynı STL içerisinde üretilebilmektedir,
- ilk gerçek topoğrafik şehir modeli başarıyla oluşturulmuştur.

Ancak bu süreçte doğal olarak bazı geçici çözümler, test amaçlı kodlar ve yeni fikirler çekirdek yapıya eklenmiştir.

Bu belge, bundan sonraki geliştirme sürecinin kurallarını belirlemek amacıyla hazırlanmıştır.

**Temel prensip:**

> Önce çalışan motor korunacak.
> Sonra temizlenecek.
> Daha sonra optimize edilecek.
> En son yeni özellikler eklenecektir.

---

# 1. Mevcut Durum

## Çalışan Sistemler

- OSM PBF okuma
- Coordinate Engine
- Scale Engine
- Mesh Builder
- Scene Builder
- STL Export
- SRTM Terrain
- Terrain Mesh
- Terrain + Building STL
- Foundation Engine (ilk sürüm)

Son başarılı üretim:

```
Meshes    : 486
Triangles : 8668
Buildings : 485
Roads     : 0
XY Scale  : 5500
Z Scale   : 5500
```

---

# 2. Ana Problem

Yazılım büyüdükçe aşağıdaki belirtiler ortaya çıkmıştır.

- Çok sayıda yeni dosya açıldı.
- Bazı modüller deneysel kaldı.
- atlas_engine.py fazla büyüdü.
- Geçici test kodları kalıcı hale gelmeye başladı.
- Test süresi 7–8 dakikaya ulaştı.
- Yeni fikirler mevcut mimariye eklenmeye başladı.

Bu durum kontrol altına alınmalıdır.

---

# 3. Kesin Öncelik

Bundan sonra geliştirme sırası değişmiştir.

```
1. Temizlik

↓

2. Stabil çalışan çekirdek

↓

3. Performans

↓

4. Test yapısı

↓

5. Yeni geliştirmeler
```

---

# 4. Şimdilik Yapılmayacaklar

Aşağıdaki çalışmalar geçici olarak durdurulmuştur.

- Landmark Engine
- Road Engine
- Tree Engine
- Water Engine
- Platform sistemi
- Construction Engine genişletmesi
- Yeni deneysel modüller
- Yeni büyük mimari değişiklikler

Önce mevcut sistem temizlenecektir.

---

# 5. Kalıcı Çekirdek

Şimdilik üretim çekirdeği olarak kabul edilen dosyalar:

```
atlas_local_osm_reader.py

atlas_scale_engine.py

atlas_coordinate_engine.py

atlas_mesh_builder.py

atlas_scene_builder.py

atlas_scene_normalizer.py

atlas_scene_fitter.py

atlas_srtm_provider.py

atlas_terrain_mesh_generator.py

atlas_foundation_engine.py

atlas_stl_writer.py
```

Bu dosyalar mümkün olduğunca sade tutulacaktır.

---

# 6. Deneysel Modüller

Şimdilik deneysel kabul edilen modüller:

```
atlas_construction_engine.py

atlas_foundation_pad_builder.py

atlas_terrain_height_sampler.py

atlas_terrain_downloader.py
```

Silinmeyeceklerdir.

Ancak üretim motorunun zorunlu parçaları olarak kabul edilmeyeceklerdir.

---

# 7. Temizlik Planı

## Aşama 1

Bugünkü çalışan sistem "Baseline" olarak korunacaktır.

Hedef:

- Terrain
- Buildings
- STL

üçlüsünün sorunsuz çalışmasıdır.

---

## Aşama 2

Debug çıktıları sadeleştirilecektir.

Normal çalışmada yalnızca:

```
Reader

Meshes

Triangles

Runtime

Output
```

gösterilecektir.

Detaylı rapor yalnızca debug modunda çalışacaktır.

---

## Aşama 3

Test süreleri analiz edilecektir.

Ölçülecek süreler:

- OSM okuma
- Terrain okuma
- Terrain mesh
- Building mesh
- STL yazımı
- Debug raporları

---

## Aşama 4

Üç ayrı test profili oluşturulacaktır.

FAST TEST

```
20 bina
```

NORMAL TEST

```
200 bina
```

FULL TEST

```
Tüm şehir
```

Geliştirme sırasında FAST TEST kullanılacaktır.

---

## Aşama 5

atlas_engine.py yalnızca orkestrasyon görevi yapacaktır.

İçinde geometri üretimi bulunmayacaktır.

Görevi yalnızca:

```
Oku

↓

Scale

↓

Scene

↓

Terrain

↓

Birleştir

↓

STL
```

olacaktır.

---

# 8. Performans Planı

Öncelikler:

- max_buildings ile hızlı test
- Debug azaltılması
- Terrain cache
- Gereksiz terrain sampling'in azaltılması
- STL yazımının optimize edilmesi

---

# 9. Mimari Kural

Yeni modül açılmadan önce şu soru cevaplanacaktır.

```
Bu gerçekten yeni bir sorumluluk mu?

Yoksa mevcut modülün görevi mi?
```

Net cevap alınmadan yeni dosya oluşturulmayacaktır.

---

# 10. Geliştirme Kuralı

Her geliştirme aşağıdaki sırayla yapılacaktır.

```
Problemin tanımı

↓

Beklenen sonuç

↓

Minimum kod değişikliği

↓

FAST TEST

↓

FULL TEST

↓

Dokümantasyon
```

---

# 11. Güncel Hedef

Bir sonraki hedef yeni özellik eklemek değildir.

Hedef:

```
Temiz

Kararlı

Hızlı

Bakımı kolay

Tekrarlanabilir

ATLAS çekirdeği
```

oluşturmaktır.

---

# 12. İlk Teknik Görev

İlk uygulanacak çalışma:

```
Runtime Profiler
```

Amaç:

7–8 dakikalık çalışmanın tam olarak hangi aşamada oluştuğunu belirlemek.

Bundan sonra optimizasyon yapılacaktır.

---

# 13. Son Karar

ATLAS artık kişisel bir deneme projesi değildir.

Profesyonel bir üretim motoru olma yolundadır.

Bu nedenle bundan sonraki süreçte;

- rastgele yeni fikirler doğrudan koda eklenmeyecek,
- önce mimari değerlendirilecek,
- minimum değişiklik yapılacak,
- çalışan sistem korunacak,
- her geliştirme dokümante edilecektir.

Bu belge, bundan sonraki tüm geliştirmeler için temel çalışma prensibi olarak kabul edilir.
---

# 14. Refactoring Güvenlik Kuralı

ATLAS Engine üzerinde yapılacak her temizlik (refactoring) çalışması aşağıdaki kurallara uymak zorundadır.

## Temel Prensip

Refactoring hiçbir zaman yazılımın davranışını değiştirmemelidir.

Yalnızca;

- kodun okunabilirliği,
- bakım kolaylığı,
- modülerliği,
- performansı

iyileştirilecektir.

Üretilen STL modeli değişmeyecektir.

---

## Refactoring Kuralları

### Kural 1

Her adımda yalnızca **bir sorumluluk** taşınacaktır.

Örneğin;

```
_count_triangles()
```

taşınacaksa başka hiçbir fonksiyon aynı adımda taşınmayacaktır.

---

### Kural 2

Her taşıma işleminden sonra aşağıdaki test çalıştırılacaktır.

```
FAST TEST

↓

FULL TEST

↓

Bambu Studio Kontrolü
```

Başarısızlık durumunda değişiklik geri alınacaktır.

---

### Kural 3

Birden fazla dosya aynı anda yeniden düzenlenmeyecektir.

Önce tek dosya tamamlanacak.

Sonra diğerine geçilecektir.

---

### Kural 4

Her refactoring sonunda;

```
Triangle sayısı

Mesh sayısı

Model boyutu

STL açılışı
```

önceki sürüm ile karşılaştırılacaktır.

---

### Kural 5

Refactoring tamamlanmadan yeni özellik eklenmeyecektir.

Yeni modül geliştirmeleri bekletilecektir.

---

### Kural 6

Her önemli değişiklik Git Commit'i ile kayıt altına alınacaktır.

İstenilen herhangi bir sürüme birkaç saniye içerisinde geri dönülebilmelidir.

---

## Amaç

ATLAS Engine'in yıllarca geliştirilebilecek temiz, güvenilir ve sürdürülebilir bir mimariye sahip olmasıdır.