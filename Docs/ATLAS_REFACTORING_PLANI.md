# ATLAS REFACTORING PLANI

**Belge Durumu:** Aktif Refactoring Planı  
**Amaç:** ATLAS çekirdeğini yeniden yazmadan, çalışan algoritmaları koruyarak sorumlulukları sadeleştirmek.

---

## 1. Temel Kural

Refactoring sırasında algoritma değiştirilmeyecek.

STL çıktısı, mesh sayısı, triangle sayısı ve üretim davranışı korunacak.

Amaç yeni özellik eklemek değil; mevcut çalışan sistemi daha sade, okunabilir ve sürdürülebilir hale getirmektir.

---

## 2. Refactoring Adayları

| Öncelik | Dosya | Mevcut Durum | Hedef |
|---:|---|---|---|
| 1 | CORE/atlas_engine.py | Fazla sorumluluk taşıyor | Sadece pipeline orkestratörü olacak |
| 2 | CORE/atlas_scene_builder.py | Scene yanında validation/factory/offset içeriyor | Katman üretimini sadeleştirecek |
| 3 | CORE/atlas_mesh_builder.py | Geometry hazırlık, mesh üretim ve debug iç içe | Mesh üretimi alt görevlere ayrılacak |

---

## 3. Kesinlikle Yapılmayacaklar

- Çalışan algoritmalar değiştirilmeyecek.
- Yeni özellik eklenmeyecek.
- Water, forest, railway, landmark geliştirmelerine başlanmayacak.
- Birden fazla büyük dosya aynı anda değiştirilmeyecek.
- Test edilmeden commit yapılmayacak.

---

## 4. İlk Refactoring Hedefi

İlk hedef:

`CORE/atlas_engine.py`

Bu dosya yeniden yazılmayacak.  
Önce içindeki görevler sınıflandırılacak.  
Sonra yalnızca güvenli yardımcı fonksiyonlar dışarı alınacak.

---

---

## 5. CORE/atlas_engine.py Görev Ayrıştırma Tablosu

### Mevcut Görevler

| No | Görev | Şu Anki Konum | Doğru Konum | Karar |
|---:|---|---|---|---|
| 1 | Üretim hattını başlatmak | atlas_engine.py | atlas_engine.py | Kalacak |
| 2 | OSM verisini okutmak | atlas_engine.py | Data Reader çağrısı | Kalacak, sadece çağrı olarak |
| 3 | XY scale hesaplatmak | atlas_engine.py | Scale Engine çağrısı | Kalacak, sadece çağrı olarak |
| 4 | Coordinate Engine oluşturmak | atlas_engine.py | atlas_engine.py | Kalacak |
| 5 | Scene oluşturmak | atlas_engine.py | Scene Builder çağrısı | Kalacak, sadece çağrı olarak |
| 6 | Scene normalize etmek | atlas_engine.py | Scene Normalizer çağrısı | Kalacak |
| 7 | Scene fit etmek | atlas_engine.py | Scene Fitter çağrısı | Kalacak |
| 8 | Terrain provider oluşturmak | atlas_engine.py | Terrain pipeline | Şimdilik kalacak |
| 9 | Terrain slab üretmek | atlas_engine.py | Terrain Mesh Generator çağrısı | Kalacak, sadece çağrı olarak |
| 10 | Meshleri terrain üzerine oturtmak | atlas_engine.py | Placement / Foundation pipeline | Taşınacak aday |
| 11 | Mesh Z offset işlemleri | atlas_engine.py | Mesh / Geometry Utility | Taşınacak |
| 12 | XY bounds filtreleme | atlas_engine.py | Geometry Utility | Taşınacak |
| 13 | Triangle sayımı | atlas_engine.py | Mesh Utility | Taşınacak |
| 14 | XY/Z/debug raporları | atlas_engine.py | Diagnostics / Debug Reporter | Taşınacak |
| 15 | STL yazdırmak | atlas_engine.py | STL Writer çağrısı | Kalacak, sadece çağrı olarak |
| 16 | Sonuç sözlüğü döndürmek | atlas_engine.py | atlas_engine.py | Kalacak |

---

### İlk Temizlik Hedefi

İlk refactoring işleminde algoritma değiştirilmeyecek.

Yalnızca aşağıdaki geçici / debug davranışları kontrol altına alınacak:

1. `_print_xy_report`
2. `_print_z_report`
3. `_print_mesh_debug_report`
4. `print("DEBUG >>> _print_z_report çağrılıyor")`

Bu fonksiyonlar hemen silinmeyecek.  
Önce `debug` şartına bağlanacak veya Diagnostics modülüne taşınacak aday olarak işaretlenecek.

---

### Riskli Değişiklikler

Aşağıdaki işlemler ilk adımda yapılmayacak:

- Terrain placement algoritması değiştirilmeyecek.
- Foundation hesaplama değiştirilmeyecek.
- Mesh sırası değiştirilmeyecek.
- STL Writer çağrısı değiştirilmeyecek.
- Road sistemi açılmayacak.
- Water / forest / landmark eklenmeyecek.

---

### Başarı Kriteri

Refactoring sonrası aşağıdaki değerler korunmalıdır:

```text
Meshes
Triangles
Buildings
Output path
Bambu Studio açılışı