# ATLAS_ENGINE Kısa Devir — 26 Temmuz 2026

## Aktif konu

Atakule’nin observation tower profili yerine düz silindir görünmesi.

## Kesin teşhis

Aynı OSM nesnesi hem `buildings` hem `landmarks` koleksiyonuna giriyordu.

Atakule:

- OSM id: `72079962`
- `man_made=tower`
- `tower:type=observation`
- `building:part=yes`
- `height=125`

Landmark hattı doğru çalışıyor:

- profil: `observation`
- 6 ring
- 188 triangle
- footprint ve yükseklik korunuyor

Ancak aynı nesne building hattında da düz gövde olarak üretildiği için landmark geometrisini kapatıyordu.

## Yapılan değişiklik

Yeni dosya:

- `CORE/atlas_landmark_building_deduplicator.py`

Yeni test:

- `Test/test_landmark_building_deduplicator.py`

Davranış:

- Landmark ile aynı OSM id’ye sahip observation tower building listesinden çıkarılıyor.
- `minaret`, `bell_tower`, `staircase`, `office` building hattında korunuyor.
- Normal binalar etkilenmiyor.

Entegrasyon:

- `CORE/atlas_foundation_first_engine.py`
- `raw_buildings`, landmark listesi alındıktan sonra filtreleniyor.

## Doğrulama

Focused test sonucu:

- `11 passed`

Çalıştırılan preview:

```bash
PYTHONPATH=. python Test/preview_atakule.py
