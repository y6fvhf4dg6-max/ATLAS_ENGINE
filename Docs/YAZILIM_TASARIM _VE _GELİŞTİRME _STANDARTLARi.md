# ATLAS
# YAZILIM TASARIM VE GELİŞTİRME STANDARTLARI

**Belge Durumu:** Resmî Teknik Referans (Anayasa)  
**Belge Türü:** Yazılım Tasarım ve Geliştirme Standardı  
**Belge Kapsamı:** ATLAS Projesinin tamamı  
**Belge Önceliği:** En Üst Teknik Referans

---

# ÖNSÖZ

Bu doküman, ATLAS projesinin resmi yazılım anayasasıdır.

ATLAS içerisinde geliştirilecek her algoritma, her dosya, her modül, her klasör yapısı, her veri modeli ve her yazılım kararı bu dokümanda tanımlanan ilkelere uygun olmak zorundadır.

Bu belge, yalnızca mevcut yazılımı tanımlamaz; aynı zamanda gelecekte yapılacak tüm geliştirmelerin sınırlarını belirler.

Kod bu belgeye uyacaktır.

Bu belge hiçbir zaman mevcut koda göre değiştirilmeyecektir.

Kod gerekiyorsa değiştirilir.

Mimari korunur.

---

# 1. AMAÇ

ATLAS'ın amacı;

Gerçek dünyadaki herhangi bir coğrafi alanı,

fiziksel olarak üretilebilir,

yüksek kaliteli,

ölçeklenebilir,

ticari olarak satılabilir

üç boyutlu modellere dönüştüren profesyonel bir yazılım platformu geliştirmektir.

---

# 2. VİZYON

ATLAS;

dünya üzerindeki herhangi bir konumu,

dakikalar içerisinde,

yüksek doğrulukta,

3B yazıcı ile üretilebilir modele dönüştürebilen,

uluslararası ölçekte kullanılabilir profesyonel bir sistem olacaktır.

---

# 3. MİSYON

ATLAS;

coğrafi verileri,

üretilebilir fiziksel modellere dönüştüren,

kararlı,

güvenilir,

bakımı kolay,

uzun ömürlü

bir yazılım altyapısı oluşturmaktır.

---

# 4. TEMEL FELSEFE

ATLAS;

bir CAD programı değildir.

Bir GIS yazılımı değildir.

Bir oyun motoru değildir.

Bir STL dönüştürücüsü değildir.

ATLAS;

gerçek coğrafyayı,

fiziksel olarak üretilebilir,

ticari ürüne dönüştüren

bir üretim motorudur.

---

# 5. TEMEL İLKELER

ATLAS;

- Basit olacaktır.
- Okunabilir olacaktır.
- Modüler olacaktır.
- Genişletilebilir olacaktır.
- Test edilebilir olacaktır.
- Tekrar üretilebilir olacaktır.
- Ticari kullanıma uygun olacaktır.

---

# 6. GELİŞTİRME FELSEFESİ

Kod yazmak amaç değildir.

Doğru mimari oluşturmak amaçtır.

Yeni dosya oluşturmak başarı değildir.

Mevcut sistemi sadeleştirmek başarıdır.

Karmaşıklık hiçbir zaman çözüm değildir.

En iyi çözüm;

en az kod,

en az bağımlılık,

en fazla okunabilirlik sağlayan çözümdür.

---

# 7. MİMARİ FELSEFE

ATLAS;

bağımsız çalışan küçük modüllerden oluşacaktır.

Her modül yalnızca kendi görevini yerine getirecektir.

Hiçbir modül başka bir modülün sorumluluğunu üstlenmeyecektir.

---

# 8. TEK SORUMLULUK İLKESİ

Her dosyanın yalnızca bir görevi vardır.

Her sınıfın yalnızca bir sorumluluğu vardır.

Her fonksiyon tek bir problemi çözer.

Bir dosya;

hem veri okumaz,

hem mesh üretmez,

hem STL yazmaz.

---

# 9. BAĞIMLILIK İLKESİ

Hiçbir modül gereksiz bağımlılık oluşturamaz.

Bir modül yalnızca ihtiyaç duyduğu modülleri kullanabilir.

Dairesel bağımlılık oluşturulamaz.

---

# 10. DOSYA FELSEFESİ

Yeni dosya açmak son çaredir.

Önce mevcut mimari değerlendirilir.

Yeni dosya;

yalnızca gerçekten yeni bir sorumluluk oluştuğunda oluşturulur.

---

# 11. REFACTORING FELSEFESİ

Refactoring;

algoritma değiştirmek değildir.

Refactoring;

kodu daha okunabilir,

daha sade,

daha sürdürülebilir

hale getirmektir.

Refactoring sırasında;

çıktı değişmez.

Davranış değişmez.

Sadece yapı iyileştirilir.

---

# 12. TEST FELSEFESİ

Her önemli modül test edilebilir olmalıdır.

Yeni özellik;

mevcut sistemi bozmamalıdır.

Hatalar mümkün olduğunca erken tespit edilmelidir.

---

# 13. VERİ FELSEFESİ

ATLAS;

veri sağlayıcısına bağımlı olmayacaktır.

Bugün;

OpenStreetMap,

SRTM

kullanılabilir.

Yarın;

LiDAR,

Copernicus,

veya başka veri kaynakları sisteme eklenebilir.

Çekirdek mimari değişmeyecektir.

---

# 14. ÜRETİM FELSEFESİ

ATLAS'ın çıktısı;

ekran görüntüsü değildir.

ATLAS'ın çıktısı;

fiziksel olarak üretilebilir,

yüksek kaliteli,

3B yazıcı uyumlu

bir modeldir.

---

# 15. TİCARİ FELSEFE

ATLAS;

ticari kullanım amacıyla geliştirilmektedir.

Her teknik karar;

ürün kalitesini,

üretim güvenilirliğini,

bakım kolaylığını,

müşteri memnuniyetini

arttırmalıdır.

---

# 16. DOKÜMANTASYON FELSEFESİ

Kod açıklama değildir.

Dokümantasyon açıklamadır.

Önemli her mimari karar belgelenir.

Dokümantasyonsuz geliştirme yapılmaz.

---

# 17. GELİŞTİRME SIRASI

ATLAS geliştirilirken aşağıdaki sıra izlenir.

1. Problem tanımlanır.
2. Mimari değerlendirilir.
3. Mevcut çözüm araştırılır.
4. Gerekirse tasarım güncellenir.
5. Kod yazılır.
6. Test edilir.
7. Dokümantasyon güncellenir.

Bu sıra değiştirilemez.

---

# 18. ATLAS GELİŞTİRME PRENSİBİ

Önce Tasarım.

Sonra Mimari.

Sonra Kod.

Hiçbir zaman bunun tersi uygulanmayacaktır.

---

# 19. YAZILIMIN ÖNCELİĞİ

Öncelik sırası;

1. Mimari
2. Güvenilirlik
3. Doğruluk
4. Okunabilirlik
5. Performans
6. Yeni Özellik

Yeni özellik;

hiçbir zaman mimariden daha önemli değildir.

---

# 20. ATLAS GELİŞTİRME KURALI

Her geliştirme sırasında şu soru sorulacaktır.

"Bu değişiklik ATLAS'ı daha sade, daha güçlü ve daha sürdürülebilir hale getiriyor mu?"

Cevap "Hayır" ise geliştirme yeniden değerlendirilir.

---

# 21. ATLAS'IN DEĞİŞMEYECEK HEDEFİ

ATLAS'ın temel hedefi;

gerçek dünyadaki herhangi bir coğrafi alanı,

yüksek doğrulukta,

fiziksel olarak üretilebilir,

ticari olarak satılabilir,

yüksek kaliteli

üç boyutlu modellere dönüştüren,

uluslararası standartlarda,

profesyonel bir yazılım platformu oluşturmaktır.

Bu hedef, projenin değiştirilemeyecek temel ilkesidir.

---

# SON HÜKÜM

Bu belge;

ATLAS projesinin resmi yazılım anayasasıdır.

Bundan sonra geliştirilecek tüm yazılım bileşenleri,

dosya organizasyonu,

algoritmalar,

modüller,

veri yapıları,

refactoring çalışmaları,

test süreçleri

ve gelecekte projeye katılacak tüm geliştiriciler

bu belgede tanımlanan ilkelere uymak zorundadır.

Bu belge, ATLAS'ın teknik kimliğini temsil eder.

Kod zamanla değişebilir.

Teknolojiler değişebilir.

Algoritmalar gelişebilir.

Ancak bu belgede tanımlanan temel ilkeler, ATLAS'ın uzun vadeli sürdürülebilirliğinin ve mühendislik disiplininin temelini oluşturacaktır.


1. DATA
   - OSM Reader
   - SRTM Provider

2. GEOMETRY
   - Coordinate
   - Scale
   - Polygon
   - Mesh

3. CONSTRUCTION
   - Terrain
   - Foundation
   - Construction

4. QUALITY
   - Mesh Validator
   - Geometry Inspector