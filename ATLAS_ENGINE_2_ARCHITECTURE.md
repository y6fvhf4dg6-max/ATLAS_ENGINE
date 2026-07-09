# ATLAS FOUNDATION-FIRST ARCHITECTURE
Version: v2.0
Status: APPROVED
Date: 2026-07-09

---

# NEDEN BU MİMARİYE GEÇİYORUZ?

Günler süren çalışmalar sonucunda görüldü ki mevcut sistem;

Building
→ Placement
→ Terrain

sıralaması nedeniyle sürekli düzeltme (offset, placement, embed vb.)
gerektiriyor.

Bu mimari;

- havada kalan binalar
- terrain içine gömülen binalar
- karmaşık placement algoritmaları
- sürekli Z düzeltmeleri

oluşturuyor.

Bu nedenle mevcut yaklaşım terk edilmiştir.

---

# YENİ HEDEF

ATLAS artık:

"Binaları terrain üzerine taşımayacak."

ATLAS;

"Terrain üzerinde foundation oluşturacak,
binaları doğrudan bu foundation üzerinde üretecek."

Bu karar ATLAS Engine'in temel mimari kararıdır.

---

# FOUNDATION-FIRST PIPELINE

PBF

↓

AtlasLocalOSMReader

↓

Coordinate Engine

↓

Terrain oluştur

↓

Foundation oluştur

↓

Building Mesh oluştur

↓

Road / Water / POI

↓

Scene oluştur

↓

STL Export

---

# FOUNDATION TANIMI

Foundation;

bir binanın 2D footprint alanının
terrain üzerinde oluşturduğu düz baskı yüzeyidir.

Her bina kendi foundation'ına sahip olacaktır.

Foundation;

- terrain'e bağlıdır
- baskıya uygundur
- gerektiğinde terrain içine gömülür
- bina için referans düzlemdir

---

# BUILDING ÜRETİM PRENSİBİ

Eski sistem

Building

↓

Placement

↓

Terrain

Yeni sistem

Terrain

↓

Foundation

↓

Building

Artık bina hiçbir zaman
0 kotunda oluşturulmayacaktır.

Bina doğduğu anda foundation kotunda üretilecektir.

---

# ESKİ SİSTEMDEN KALDIRILACAKLAR

Placement-first yaklaşımı

CITY_Z_OFFSET

Mesh aşağı taşıma mantığı

Sonradan terrain'e oturtma

Çoklu offset düzeltmeleri

---

# YENİ MOTOR

Yeni motor eski motordan tamamen bağımsız geliştirilecektir.

Yeni dosya:

CORE/atlas_foundation_first_engine.py

Eski motor korunacaktır.

Yeni motor başarılı olduktan sonra
varsayılan motor olacaktır.

---

# FOUNDATION-FIRST MOTORUN GÖREVLERİ

1.
Terrain üret

2.
Terrain'i referans kabul et

3.
Her bina için foundation oluştur

4.
Foundation kotunu hesapla

5.
Building mesh'i foundation üzerinde üret

6.
Road

7.
Scene

8.
STL

---

# İLK GELİŞTİRME HEDEFLERİ

Sprint 1

Foundation-first Engine

Sprint 2

Foundation Surface Builder

Sprint 3

Foundation Sampler

Sprint 4

Building Builder

Sprint 5

Road Integration

Sprint 6

Final STL Pipeline

---

# VERİ STRATEJİSİ

Araştırılacak kaynaklar:

- Microsoft Global Building Footprints
- Overture Maps
- OpenStreetMap
- OpenTopography
- Türkiye ulusal yükseklik ve harita verileri

Uzun vadeli hedef:

ATLAS Building Database

---

# MİMARİ PRENSİP

ATLAS'ta hiçbir bina havada doğmaz.

Önce terrain vardır.

Terrain üzerinde foundation oluşturulur.

Bina foundation üzerinde doğar.

Bu kural ATLAS Engine'in değiştirilmeyecek temel prensibidir.