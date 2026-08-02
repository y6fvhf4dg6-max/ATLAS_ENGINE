# ATLAS_ENGINE — Bonn Münsterplatz Devir Kaydı

Tarih: 2 Ağustos 2026

## Ürün

- Lokasyon: Bonn Münsterplatz
- Ana yapı: Bonner Münster
- Ürün dış ölçüsü: 170 × 170 mm
- Harita açıklığı: 150 × 150 mm
- Ölçek: 1:3000
- Etiket:
  - BONN
  - GEBURTSORT

## Kullanıcı tarafından onaylanan Bonner Münster geometrisi

Tam sahneden doğrudan yakalanan 12 bina parçası görsel olarak onaylandı.

Kanonik onaylı dosya:

`OUTPUT/STL/bonn_FINAL_SCENE_exact_muenster_extract_3000.stl`

Özellikler:

- 12 ayrı printable `building:part`
- 932 üçgen
- düzeltilmiş merkez kule yüksekliği
- dört yan kule
- kabul edilen radyal çokgen apsis çatıları
- gable, skillion ve pyramidal çatılar
- pencere detayı eklenmedi
- kullanıcı tarafından doğru kabul edildi

## Kreuzkirche köşe kulesi

Kreuzkirche'nin haritanın güneydoğu köşesindeki bağımsız kulesi doğru kabul edildi.

- Alt gövde: OSM 893056616
- Orta gövde: OSM 893056618
- Piramidal külah: OSM 893056617
- Sekiz köşeli çatı
- Nihai yüksekliği Bonner Münster merkez kulesinden yaklaşık 3.17 mm daha fazla
- Açık kenar: 0
- Non-manifold kenar: 0

## Tespit edilen gerçek sorun

Tam sahnede doğru 12 Bonner Münster bina parçası bulunuyor:

- 321760756
- 321760757
- 321760758
- 321760759
- 321760760
- 321760761
- 321760763
- 321760764
- 321760766
- 321760767
- 321760768
- 321760769

Ancak aynı sahnede Bonner Münster ayrıca eski landmark geometrisiyle ikinci kez üretiliyor:

- landmark_id: 112526702
- landmark_class: cathedral
- name: Bonner Münster
- triangle count: 580
- body meshes: 1
- tower meshes: 4
- roof meshes: 4

Bu eski landmark meshi, kullanıcı tarafından onaylanan 12 parçalı geometrinin üstünü kapatıyor. Nihai haritada eski görünümün kesin kök nedeni budur.

Diğer landmark:

- landmark_id: 304078323
- building: bridge
- triangle count: 12
- Bonner Münster sorunuyla ilgili değil

## Son üretilen fakat henüz nihai kabul edilmeyen ürün dosyaları

- `OUTPUT/STL/bonn_muensterplatz_city_150mm_FINAL_GEOMETRY.stl`
- `OUTPUT/STL/bonn_muensterplatz_wall_collection_170mm_FINAL_GEOMETRY.stl`
- `OUTPUT/STL/bonn_muensterplatz_multicolor_FINAL_GEOMETRY/`

Bu dosyalarda eski Bonner Münster landmark meshi hâlâ bulunuyor. Bu nedenle nihai ürün olarak kabul edilmemelidir.

## Test durumu

`Test/test_landmark_building_deduplicator.py` dosyasına yeni bir regresyon testi eklendi:

`test_removes_parent_cathedral_landmark_when_detailed_building_parts_exist`

Test şu anda beklenen şekilde kırmızı:

`AttributeError: AtlasLandmarkBuildingDeduplicator has no attribute filter_landmarks`

Bu test henüz uygulanmamış varsayımsal `parent_building_id` alanını kullanıyor. Gerçek hiyerarşi bağlantısı doğrulanmadan implementasyon yapılmamalıdır.

Son focused sonuç:

- 4 passed
- 1 failed

## Sıradaki tek teknik iş

Bonner Münster ana landmark meshi `112526702` tam sahneden çıkarılacak; kullanıcı tarafından onaylanan 12 `building:part` korunacak.

Düzeltme yalnız Bonn'a özel geçici STL birleştirmesi olarak değil, gerçek bina hiyerarşisine dayanan güvenli bir genel deduplikasyon kuralıyla yapılmalıdır.

Düzeltmeden sonra yeni nihai harita ayrı dosya adıyla üretilecek ve görsel onay alınacaktır.

## Çalışma disiplini

- Henüz commit yapılmadı.
- Henüz push yapılmadı.
- Nihai Bonn haritası henüz tamamlanmış sayılmıyor.
- Onaylı Münster geometrisi kaybolmadı ve kalıcı STL dosyasında mevcut.

# GÜNCELLEME — DOĞRU TAM BONN HEDİYELİK DOSYASI

## Nihai tam geometri

Eski Bonner Münster landmark meshi `112526702`, kontrollü üretim sırasında sahneden çıkarıldı. Kullanıcı tarafından onaylanan 12 parçalı Bonner Münster geometrisi korunarak tam hediyelik ürün yeniden üretildi.

Doğru tam Bonn hediyelik STL:

`OUTPUT/STL/bonn_muensterplatz_wall_collection_170mm_GIFT_FINAL.stl`

Ara şehir STL:

`OUTPUT/STL/bonn_muensterplatz_city_150mm_GIFT_FINAL.stl`

Nihai üretim özeti:

- Şehir meshleri: 821
- Ürün meshleri: 826
- Şehir üçgenleri: 56606
- Nihai ürün üçgenleri: 58450
- Ürün dış ölçüsü: 170 × 170 mm
- Harita açıklığı: 150 × 150 mm
- Ölçek: 1:3000
- Etiket: BONN / GEBURTSORT

Önceki `FINAL_GEOMETRY` dosyaları eski 580 üçgenlik katedral landmark meshini içerdiğinden nihai ürün olarak kullanılmamalıdır.

## Çok renkli STL dosyaları

Mevcut renk dosyaları:

- `OUTPUT/STL/bonn_muensterplatz_multicolor/bonn_muensterplatz_170mm__white.stl`
- `OUTPUT/STL/bonn_muensterplatz_multicolor/bonn_muensterplatz_170mm__red.stl`
- `OUTPUT/STL/bonn_muensterplatz_multicolor/bonn_muensterplatz_170mm__green.stl`
- `OUTPUT/STL/bonn_muensterplatz_multicolor/bonn_muensterplatz_170mm__black.stl`

Bu klasör genel ad taşıdığı için ileride başka üretimle üzerine yazılabilir. Çok renkli baskı için henüz kalıcı Bambu Studio `.3mf` proje dosyası oluşturulmadı.

## Bonn çalışmasının ana motora kattığı genel gelişmeler

Bonn sahnesi sırasında ana motora şu genel kabiliyetler eklendi:

- `building:part` toplam yüksekliğinden `roof:height` değerinin ayrılması
- açıkça verilen gable çatı yüksekliğinin kullanılması
- `skillion` çatı profili ve mesh üretimi
- `apse_gabled` profil desteği
- mimari merkez tabanlı radyal apsis çatı geometrisi
- bina hiyerarşisi için ham bina kayıtlarının korunması
- pyramidal kule çatılarında doğru STL yüksekliği ölçeklemesi
- yükseltilmiş `roof-only building:part` parçalarının korunması
- yükseltilmiş çatı parçaları için minimum destek slabı
- Kreuzkirche gibi katmanlı ve yüksek kulelerde doğru göreli yükseklik üretimi

Bu geliştirmeler Bonn’a özel değildir; benzer katedraller, kiliseler, kuleler ve çok parçalı tarihi yapılar için ana motorda kullanılabilir.

## Kalan ana motor borcu

Ayrıntılı `building:part` hiyerarşisi bulunan landmarkların, eski genel landmark meshiyle ikinci kez üretilmesini kalıcı ve genel biçimde engelleyen deduplikasyon kuralı henüz tamamlanmadı.

Bonn nihai STL’si bu sorun kontrollü üretim filtresiyle çözülerek doğru üretildi; ancak kaynak motorda kalıcı genel çözüm hâlâ gereklidir.

İlgili test:

`Test/test_landmark_building_deduplicator.py`

Mevcut focused durum:

- 4 passed
- 1 failed

Kırmızı test:

`test_removes_parent_cathedral_landmark_when_detailed_building_parts_exist`
