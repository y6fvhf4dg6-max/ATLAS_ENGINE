# ATLAS PLATFORM KABİLİYET ENVANTERİ

**Belge Durumu:** Aktif  
**Belge Türü:** Yaşayan Teknik Envanter  
**Amaç:** ATLAS Platformu'nun mevcut teknik kabiliyetlerini, eksik genel motorlarını ve geliştirme önceliklerini tek belgede toplamak.

---

# Bu Belgenin Amacı

Bu belge bir yapılacaklar (TODO) listesi değildir.

Bu belge, ATLAS Platformu'nun bugün hangi teknik kabiliyetlere sahip olduğunu, hangi alanlarda olgunlaştığını ve hangi genel motorların gelecekte geliştirilmesi gerektiğini gösteren yaşayan bir mühendislik envanteridir.

Her önemli geliştirme sonrasında güncellenir ve platformun gerçek teknik durumunu yansıtır.

---

# Yeni Sohbetlerde Kullanımı

Yeni bir sohbet başlatıldığında aşağıdaki ifade yeterlidir:

> **"Docs/ATLAS_PLATFORM_KABILIYET_ENVANTERI.md dosyasını incele ve kaldığımız yerden devam edelim."**

Bu belge yeni oturumun;

- ATLAS'ın vizyonunu,
- mevcut teknik seviyesini,
- tamamlanan kabiliyetlerini,
- eksik motorlarını,
- geliştirme önceliklerini

kısa sürede anlayabilmesi amacıyla hazırlanmıştır.

---

# Durum Göstergeleri

| Durum | Anlamı |
|--------|---------|
| ✓ | Tamamlandı |
| ◐ | Kısmen tamamlandı |
| ✗ | Henüz başlanmadı |

---

# Platform Özeti

ATLAS yalnızca STL üreten bir yazılım değildir.

ATLAS;

- coğrafi verileri,
- tarihi yapıları,
- doğal çevreyi,
- kişisel anıları,
- görüntüleri

fiziksel olarak üretilebilir premium ürünlere dönüştürmeyi hedefleyen genel amaçlı bir **Geographic Manufacturing Platform** olarak geliştirilmektedir.

Temel hedef;

kullanıcının seçtiği herhangi bir lokasyonu mümkün olan en yüksek otomasyon seviyesinde, estetik, fiziksel olarak üretilebilir ve ticari kaliteye sahip bir ürüne dönüştürmektir.

---

# Ticari Hedef

ATLAS'ın amacı mevcut başarılı şehir modeli platformlarının kullanıcı deneyimi ve ticari olgunluğunu referans almak; ancak bunu daha güçlü, daha genel ve daha geniş kabiliyetlere sahip tek bir üretim motoruyla gerçekleştirmektir.

ATLAS;

- otomatik şehir modeli,
- topoğrafik modeller,
- tarihi yapılar,
- kişiselleştirilmiş haritalar,
- 2.5D rölyef ürünleri

gibi farklı ürün ailelerini aynı platform altında üretebilecek şekilde tasarlanmaktadır.

---

# Genel Teknik Seviye

Platform artık deneysel prototip aşamasını geride bırakmıştır.

Geliştirme yaklaşımı;

- modüler mimari,
- test odaklı geliştirme,
- deterministik üretim,
- fiziksel üretilebilirlik,
- genel amaçlı motor geliştirme

ilkeleri üzerine kuruludur.

Temel geliştirme prensibi:

> Önce genel motor geliştirilir.
>
> Daha sonra regresyon testleri yazılır.
>
> Son olarak gerçek dünya doğrulaması yapılır.

---

# KABİLİYET ENVANTERİ

## Arazi (Terrain) Motoru

**Durum:** ✓

Mevcut Kabiliyetler

- Terrain üretimi
- Foundation sistemi
- Topoğrafya
- Terrain örnekleme
- Terrace altyapısı
- Contour band ve contour mesh üretimi
- Kapalı contour terrace geometrisi
- Terrain Pipeline

---

## Yapı Motoru

**Durum:** ✓

Mevcut Kabiliyetler

- Genel bina üretimi
- Fiziksel minimum boyutlar
- Building:part desteği
- Manifold mesh üretimi

---

## Çatı Motoru

**Durum:** ◐

Mevcut

- Flat
- Gable
- Hipped
- Dome (başlangıç)

Eksikler

- Mansard
- Gambrel
- Barrel
- Sawtooth
- Karmaşık çatı tipleri

---

## Yol Motoru

**Durum:** ◐

Mevcut

- Yol tabanı
- Temel yol üretimi

Eksikler

- Yol geometrisi
- Kavşak sistemleri
- Döner kavşaklar
- Gelişmiş yol detayları

---

## Kale Motoru

**Durum:** ✓

Mevcut

- Castle relation desteği
- Kale kabuğu
- Sur sistemi
- Kuleler
- Mazgallar

---

## Doğa Motoru

**Durum:** ◐

Mevcut

- Parklar
- Çimen alanları
- Deterministik yeşil alan ağaç örnekleme
- WorldCover yüzey agregasyonu
- Terrain-following landcover geometrisi
- WorldCover entegrasyonu

Eksikler

- Orman çeşitleri
- Kayalık alanlar
- Uçurumlar
- Şelaleler
- Kıyı detayları

---

## Rölyef Motoru

**Durum:** ◐

Mevcut

- Görüntü işleme altyapısı
- Height Map üretimi
- Relief Pipeline
- MediaPipe landmark adapter
- Yüz landmark bölge haritaları
- Normal structure/detail ayrımı
- Normal gradient limiter
- Confidence tabanlı normal kontrolü
- Screened normal entegrasyonu
- Semantik detail ve height ayarı
- Deterministik üretim yaklaşımı

Devam Eden Çalışmalar

- Portre rekonstrüksiyonu
- Kimlik doğruluğu
- Baskı kalitesi optimizasyonu

---

# HENÜZ BULUNMAYAN GENEL MOTORLAR

## Semantik Landmark Motoru

**Durum:** ◐

Mevcut

- Landmark sınıflandırması
- Tower, observation tower, lighthouse, obelisk ve bridge profilleri
- Ancient theatre arkeolojik bağlam sınıflandırması
- Landmark/building deduplication
- Foundation-first landmark yerleşimi
- Yapı tipine özel geometri üreticileri

Eksikler

- Daha geniş dünya landmark kataloğu
- Otomatik landmark kalite derecelendirmesi
- Karmaşık landmark parça ilişkileri

---

## Köprü Motoru

**Durum:** ◐

Mevcut

- OSM köprü tespiti
- Basılabilir kapalı deck geometrisi
- Pier ve support geometrisi
- Galata Köprüsü parapet ve support profili
- Yol yaklaşım rampası altyapısı
- Gerçek PBF topoloji regresyonu

Eksikler

- Genel yol ağıyla tam otomatik bağlantı
- Daha geniş köprü tipleri
- Karmaşık çok açıklıklı köprü profilleri

---

## Demiryolu Motoru

**Durum:** ✗

Hedef

- Ray geometrisi
- Travers sistemi
- İstasyon entegrasyonu
- Köprü ve tünel desteği

---

## Su Yapıları Motoru

**Durum:** ✗

Hedef

- Barajlar
- Liman yapıları
- İskeleler
- Marinalar

---

## Dini Yapılar Motoru

**Durum:** ✗

Hedef

- Kiliseler
- Katedraller
- Sinagoglar
- Tapınaklar
- Genişletilmiş cami mimarisi

---

## Şehir Donatıları Motoru

**Durum:** ✗

Hedef

- Saat kuleleri
- Heykeller
- Anıtlar
- Deniz fenerleri
- Su kuleleri

---

## Endüstriyel Yapılar Motoru

**Durum:** ✗

Hedef

- Fabrikalar
- Silolar
- Depolar
- Bacalar

---

## Ulaşım Altyapısı Motoru

**Durum:** ✗

Hedef

- Tüneller
- Viyadükler
- Büyük kavşak sistemleri

---

## Üretim Motoru

**Durum:** ✗

Hedef

- Üretim profilleri
- Baskı optimizasyonu
- Üretim manifestoları
- Kalite raporları

---

## Ürün Motoru

**Durum:** ◐

Mevcut

- Wall Collection ürün oluşturucu
- Çerçeveli ve duvara asılabilir ürün
- Etiket plakası ve iki satırlı yazı
- Mezuniyet kepi ve doğum günü pastası sembolleri
- Çok renkli STL dışa aktarımı
- Malzeme profilleri ve preview renderer
- Köln ve Bonn referans ürünleri

Eksikler

- Genel ürün preset kataloğu
- Tek komutlu üretim manifestosu
- Otomatik Bambu Studio / 3MF üretimi
- Sipariş sistemi entegrasyonu

---

# Geliştirme Önceliği

Yeni geliştirilecek her genel motor aşağıdaki üç soruya olumlu cevap vermelidir.

1. Dünya genelinde tekrar kullanılabilir mi?
2. Ürün kalitesini gözle görülür şekilde artırıyor mu?
3. Platformun ticari değerini yükseltiyor mu?

Bu üç koşulu sağlamayan geliştirmeler düşük önceliklidir.

Platforma yeni kabiliyet kazandırmayan, yalnızca belirli bir şehir veya yapı için yazılan çözümler tercih edilmez.

---

# Belgenin Güncellenmesi

Her önemli geliştirme sonunda;

- tamamlanan kabiliyetler güncellenir,
- yeni motorlar eklenir,
- geliştirme öncelikleri yeniden değerlendirilir.

Bu belge her zaman ATLAS Platformu'nun gerçek teknik seviyesini yansıtmalıdır.

---

# Nihai Hedef

ATLAS'ın nihai hedefi;

kullanıcının seçtiği herhangi bir lokasyonu mümkün olan en yüksek otomasyon seviyesinde, estetik, fiziksel olarak üretilebilir ve ticari kaliteye sahip premium bir ürüne dönüştüren dünya çapında bir platform oluşturmaktır.

Bu belge, o hedefe ulaşırken platformun teknik gelişimini takip etmek amacıyla tutulmaktadır.