# ATLAS TERRAIN SYSTEM

## Status

Terrain Framework v1.0

---

# Purpose

The Terrain System provides real-world elevation for ATLAS.

Terrain data is completely independent from OSM data.

Terrain is responsible only for:

- ground elevation
- hills
- valleys
- mountains
- cliffs
- terrain mesh

Buildings are NOT part of Terrain.

---

# Architecture

```text
Terrain Manager
        │
        ▼
Terrain Engine
        │
        ▼
Terrain Provider
        │
 ┌──────┼──────────────┬─────────────┐
 │      │              │             │
Flat   SRTM      Copernicus      LiDAR
```

The Terrain Engine never knows where elevation data comes from.

It only requests:

```python
terrain.get_height(lat, lon)
```

---

# Current Providers

## Flat Provider

Purpose:

Fallback provider.

Always returns:

```text
0.0 meters
```

Used when no DEM exists.

---

## SRTM Provider

Status:

Skeleton completed.

Future responsibilities:

- load SRTM tiles
- cache loaded tiles
- return elevation
- support worldwide terrain

---

## Copernicus Provider

Future provider.

Advantages:

- higher quality than SRTM
- excellent European coverage
- preferred terrain source

---

## LiDAR Provider

Premium terrain source.

Used when available.

Highest priority.

Suitable for:

- museums
- premium products
- engineering models

---

# Terrain Priority

Terrain sources are selected in this order:

```text
1. LiDAR

2. Copernicus DEM

3. SRTM

4. Flat Terrain
```

ATLAS must always be able to generate a model.

If high-quality terrain exists,
terrain quality improves automatically.

---

# Terrain Manager

Responsibilities:

- choose provider
- verify installed datasets
- fallback handling
- logging
- future automatic updates

Terrain Manager is the only component that decides which provider is active.

---

# Data Structure

```text
Data/

TERRAIN/

    SRTM/

    COPERNICUS/

    LIDAR/
```

Future:

```text
CACHE/

DOWNLOADS/

ARCHIVE/
```

---

# Terrain Cache Strategy

Terrain data is downloaded only when required.

Workflow:

```text
Customer Order

↓

Required Country

↓

Terrain Available?

↓

YES

↓

Use Cache

↓

NO

↓

Download

↓

Cache

↓

Generate STL
```

No unnecessary worldwide downloads.

---

# Future Development

Terrain Engine roadmap:

Phase 1

- Flat terrain
- Architecture

Phase 2

- SRTM reading

Phase 3

- Copernicus support

Phase 4

- LiDAR support

Phase 5

- Terrain mesh generation

Phase 6

- Buildings placed on terrain

Phase 7

- Roads follow terrain

Phase 8

- Rivers and lakes

---

# Design Rule

Terrain must remain completely independent from:

- OSM Engine
- Building Engine
- Landmark Engine

Terrain only provides elevation.

Nothing more.

---

# Long-Term Goal

ATLAS should support worldwide terrain generation using multiple interchangeable elevation providers.

Terrain quality should improve automatically whenever better data becomes available, without changing the Terrain Engine itself.
# ATLAS Terrain and Competitor Research
Version: 0.1
Date: 2026-07-07

---

# Executive Summary

Bu belge, ATLAS projesi için gerçekleştirilen ilk rakip ve teknik altyapı araştırmasını içerir.

Amaç:

- Avrupa'da ATLAS benzeri firmaları belirlemek
- Ürün yapılarını incelemek
- Muhtemel teknik altyapılarını analiz etmek
- ATLAS için doğru teknik mimariyi belirlemek

Bu çalışma ilk fazdır.

İkinci fazda;

- 30-50 firma
- ayrıntılı teknik tersine mühendislik
- fiyat analizi
- üretim analizi
- STL üretim zinciri

ayrı bir rapor halinde hazırlanacaktır.

---

# 1. Rakip Firma Analizi

## 1.1 CITYFRAMES

Ülke

Germany

Kuruluş

2019

Ürün

- 3D City Models
- Wall Art
- Corporate Products

Üretim

Made in Germany

Dünya genelinde

200+ şehir

90+ ülkeye satış

10.000+ müşteri

Resmi açıklamalar

- kendi geliştirdikleri CitySculpt sistemi
- hand processed 3D Data
- high resolution satellite data
- GIS data
- extensive manual refinement
- advanced 3D printing

Teknik çıkarım

Standart OpenStreetMap verisini doğrudan kullanmıyorlar.

Kendi açıklamalarına göre;

- yüksek çözünürlüklü uydu verisi
- GIS
- manuel düzeltme
- kendi CitySculpt Pipeline

kullanılıyor.

ATLAS açısından önemli not

CityFrames'ın en büyük avantajı

ham veriyi

ürüne uygun hale getirmesi.

Bu bizim de hedefimiz olmalıdır.

---

## 1.2 Lichtbild Manufaktur

Ülke

Germany

Ürün

- Custom City Models
- Landscape Models

Ölçek

Şehir modelleri

1:5500

Landscape modelleri

1:85000

Bu dikkat çekicidir.

ATLAS'ın mevcut şehir ölçeği ile neredeyse aynıdır.

Teknik çıkarım

Firma

dünya genelinde

şehir modeli üretebilmektedir.

Muhtemel veri kaynakları

- GIS
- DEM
- özel mesh optimizasyonu

---

## 1.3 Cleencraft

Ülke

Germany / EU

Ürün

Custom 3D City Models

En önemli bilgi

Firma açıkça

OpenStreetMap

kullandığını belirtmektedir.

Bu bizim için önemli bir referanstır.

---

## 1.4 AccuCities

Ülke

United Kingdom

Pazar

B2B

Hedef

- mimarlık
- şehir planlama
- inşaat

Teknik yaklaşım

- aerial imagery
- manuel modelleme
- yüksek doğruluk

Bu firma

hediyelik ürün

değil,

profesyonel şehir modeli üretmektedir.

---

## 1.5 Georelief

Ülke

Germany / Switzerland

Ürün

Raised Relief Maps

Odak

Terrain

Dağ

Topografya

Yükseklik

Bina detayından çok

arazi

ön plandadır.

---

## 1.6 Interkart

Ülke

Germany

Ürün

3D Relief Maps

Hazır ürünler

Avrupa

İber Yarımadası

Alpler

vb.

Terrain odaklıdır.

---

## 1.7 Chapel Prints

Ülke

United Kingdom

Ürün

3D Topographic Maps

Resmi açıklama

Satellite

LiDAR

Terrain

verilerini kullandıklarını belirtmektedir.

Bu çok önemli bir referanstır.

---

## 1.8 ElevationScapes

Ülke

United Kingdom

Ürün

Terrain Models

Odak

yüksek çözünürlüklü elevation data

---

## 1.9 3DMap.fr

Ülke

France

Ürün

Relief Maps

Terrain

şehir

ve

duvar dekorasyonu

karışımı ürünler.

---

## 1.10 LV3D

Ülke

France

Ürün

Özel 3D modelleme

Topografik modeller

Haritadan üretim

---

## 1.11 TopRelieve3D

Ülke

Spain

Ürün

Dağ

Terrain

3D Relief

ödül

ve dekorasyon ürünleri.

---

## 1.12 TerraPrinter

Global

Web tabanlı

Terrain

Buildings

Roads

Water

üreten dijital platform.

STL üretmektedir.

---

## 1.13 TouchTerrain

Akademik

Ücretsiz

Terrain STL

üretmektedir.

Araştırma açısından önemlidir.

---

## 1.14 Map2STL

Harita

↓

Terrain

↓

STL

üreten web sistemi.

ATLAS için önemli referanslardan biridir.

---

# 2. Rakiplerin Muhtemel Teknik Altyapısı

Genel olarak firmalar aşağıdaki yapıyı kullanıyor görünmektedir.

OpenStreetMap

↓

GIS

↓

DEM

↓

Terrain

↓

Mesh Optimization

↓

3D Printing

Ancak

her firma

aynı veri kaynağını kullanmamaktadır.

---

# 3. Terrain Kaynakları

SRTM

Avantaj

- ücretsiz
- dünya kapsaması

Dezavantaj

eski

---

Copernicus DEM

Avantaj

- daha güncel
- Avrupa'da daha kaliteli
- ücretsiz

ATLAS için

ana adaydır.

---

LiDAR

Avantaj

çok yüksek çözünürlük

Dezavantaj

ülkeye göre değişmektedir.

Premium ürünler için uygundur.

---

# 4. Rakiplerin Güçlü Yanları

- iyi tasarım
- temiz mesh
- kaliteli baskı
- güçlü marka

---

# 5. Rakiplerin Zayıf Yanları

Çoğu firma

yalnızca

şehir modeli satmaktadır.

Kullanıcıya

kişisel platform

sunmamaktadır.

Çoğunda

canlı üretim sistemi

bulunmamaktadır.

---

# 6. ATLAS'ın Avantajı

ATLAS

yalnızca

şehir modeli

üretmeyecek.

Aynı platform içinde

- şehir

- terrain

- landmark

- kişisel anılar

- magnet

- B2B

- STL

- dijital dosya

- fiziksel üretim

bir arada olacaktır.

Bu,

tespit edilen rakiplerde

doğrudan görülmeyen

en önemli farklılaştırıcıdır.

---

# 7. Teknik Sonuç

ATLAS Terrain sıralaması

1

LiDAR

↓

2

Copernicus DEM

↓

3

NASA DEM / SRTM

↓

4

Flat Terrain

Terrain Engine

hiçbir zaman

hangi kaynağın kullanıldığını bilmeyecektir.

Sadece

terrain_provider.get_height()

çağıracaktır.

---

# 8. İlk Karar

ATLAS Terrain Framework

tamamlanmıştır.

Bir sonraki adım

gerçek DEM verisinin

okunmasıdır.

İlk test noktası

Anıtkabir

olacaktır.

Anıttepe yüksekliği

başarıyla okunabildiğinde

terrain mesh

üretimine geçilecektir.

---

# NOT

Bu rapor

ilk araştırma sürümüdür.

Bir sonraki sürümde;

- Avrupa genelinde 30–50 rakip firma
- fiyat analizleri
- STL üretim zincirleri
- baskı teknolojileri
- kullanılan yazılımlar
- veri kaynakları
- üretim maliyetleri
- ticari stratejiler

ayrıntılı olarak incelenecektir.
Firma / Platform

Ülke

Ürün tipi

Açık teknik ipucu

CITYFRAMES

Almanya

3D şehir modelleri

“High-resolution, hand-processed 3D data” diyor; 10.000+ müşteri, 90+ ülke beyanı var.  

Lichtbild Manufaktur

Almanya

Custom city + landscape model

Şehir ölçeğini yaklaşık 1:5500, landscape ölçeğini 1:85.000 olarak veriyor; dünya çapında model ürettiğini söylüyor.  

Cleencraft

AB / Almanya odaklı

Custom 3D city/topography

Açıkça OpenStreetMap data kullandığını söylüyor.  

Georelief / 3D-relief

Almanya / İsviçre

Raised relief maps

Almanya ve İsviçre üretimi, yüksek doğruluklu 3D relief haritalar.  

Interkart

Almanya

3D raised relief maps

Hazır relief haritalar; İber Yarımadası, Avrupa vb. ürünler.  

AccuCities

İngiltere

B2B 3D city models

Aerial imagery ve manual photogrammetry kullanıyor; mimarlık/planlama odaklı.  

CentreMapsLive / Latitude Maps

İngiltere

B2B 3D mapping

UK’de aerial imagery, drone ve manuel 3D capture vurgusu.  

Chapel Prints

İngiltere

3D topographic relief maps

Satellite ve LiDAR field survey verilerini işlediğini belirtiyor.  

ElevationScapes

İngiltere

Bespoke 3D terrain models

High-resolution elevation data kullandığını söylüyor.  

Unique Maps

İngiltere / AB

3D relief-style map art

Relief görünümlü harita sanatı; kişiselleştirilmiş ürünler var.  

3DMap.fr

Fransa

Relief maps

Fransa’da tasarım/üretim, detaylı relief haritalar.  

IGN Boutique

Fransa

Resmî relief haritalar

Fransa ve masifleri için relief haritalar.  

LV3D

Fransa

Custom 3D modelling/topography

Harita, fotoğraf veya fikirden özel 3D modelleme hizmeti.  

Top Relieve 3D

İspanya

Mountain / 3D relief products

Dağ, 3D harita ve trofe ürettiğini söylüyor.  

3D Mapper

Avrupa/global

Web 3D map maker

Browser tabanlı 3D map, heightmap/texture/export odaklı; daha çok dijital araç.  

TerraPrinter

Global

3D printable terrain + buildings

Terrain, buildings, roads, water ve STL/3MF export üretiyor.  

TouchTerrain

ABD / akademik

3D printable terrain web app

Ücretsiz web app, terrain STL üretimi.  

Map2STL

Global

STL terrain/city export

Harita seçimiyle STL üretimi.  