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