# ATLAS DECISIONS

## Foundation-First

- Terrain önce üretilir.
- Terrain STL'nin ana objesidir.
- Bütün objeler terrain üzerine yerleştirilir.
- Objeler terrain'i değiştirmez.
- Objeler terrain yüksekliğini örnekleyerek yerleşir.

---

## Mimari Kural

Yatay büyüme DURDURULDU.

Yeni geliştirmeler yalnızca:

- Foundation
- Roads
- Water
- Vegetation
- Bridges
- Details

şeklinde dikey olarak eklenecektir.

---

## Legacy

Eski atlas_engine.py korunacaktır.

Yeni geliştirmeler Foundation-First mimarisi üzerinde yapılacaktır.

---

## Current Milestone

✓ Terrain

✓ Buildings

→ Roads

→ Water

→ Vegetation

→ Modern Mesh Optimization
