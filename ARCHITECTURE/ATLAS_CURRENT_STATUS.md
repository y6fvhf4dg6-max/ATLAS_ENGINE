# ATLAS CURRENT STATUS

**Tarih:** 2026-07-09

---

# DURUM

ATLAS artık eski "Placement-First" mimarisinden çıkmış ve yeni
**Foundation-First Architecture** üzerine taşınmaya başlamıştır.

Yeni ana akış:

PBF
↓
Terrain
↓
Foundation
↓
Building Mesh
↓
Road (henüz bağlanmadı)
↓
Scene
↓
STL

---

# BUGÜN TAMAMLANANLAR

- Foundation-First Engine oluşturuldu.
- Foundation-First Pipeline oluşturuldu.
- Foundation Scene Builder oluşturuldu.
- Foundation Mesh Extruder oluşturuldu.
- Foundation Builder oluşturuldu.
- Foundation Sampler oluşturuldu.
- Foundation Surface Builder oluşturuldu.
- Yeni test dosyası oluşturuldu.

Test:

Test/test_foundation_first_city_preview.py

---

# ÇÖZÜLEN EN BÜYÜK PROBLEM

Binaların eğimli terrain üzerinde havada kalması.

Eski yöntem:

foundation_z = highest

Yeni yöntem:

foundation_z = lowest

Bu değişiklikten sonra binalar terrain üzerine doğru şekilde oturmaya başladı.

---

# MİMARİ KARAR

Artık yeni geliştirmeler eski placement sistemi üzerinde yapılmayacaktır.

Ana geliştirme hattı:

Foundation-First Engine

üzerinden devam edecektir.

---

# AKTİF DOSYALAR

CORE/

atlas_foundation_first_engine.py

atlas_foundation_first_pipeline.py

atlas_foundation_scene_builder.py

atlas_foundation_mesh_extruder.py

atlas_foundation_builder.py

atlas_foundation_sampler.py

atlas_foundation_surface_builder.py

atlas_foundation_mesh_builder.py

---

# LEGACY (ESKİ SİSTEM)

Şimdilik korunacaktır.

atlas_engine.py

atlas_placement_pipeline.py

atlas_foundation_engine.py

atlas_extrusion_engine.py

---

# BİR SONRAKİ HEDEF

Gerçek Foundation Mesh.

Artık bina tek bir foundation_z üzerine değil,
footprint'i takip eden gerçek foundation geometrisi üzerine
extrude edilecektir.

Bu işlem tamamlandıktan sonra
Road sistemi yeni Foundation-First mimarisi üzerine taşınacaktır.
