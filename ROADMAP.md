# GraphRAG V1 — Yol Haritası

Bu belge, projenin evrim planını ve öncelikli geliştirme adımlarını tanımlar.

---

## Mevcut Durum: `v1.0` — PoC (Kavram Kanıtlama)

- [x] Flask backend ile temel API altyapısı
- [x] Graphiti ile serbest metin → bilgi grafiği enjeksiyonu
- [x] Neo4j üzerinde kalıcı graf depolama
- [x] 3D / 2D interaktif graf görselleştirmesi
- [x] Graph RAG sorgu pipeline (Retrieval → Augment → Generate)
- [x] Modern, glassmorphism tabanlı web arayüzü

---

## v1.1 — Altyapı Güçlendirme

> **Hedef:** PoC'yi güvenli ve sürdürülebilir bir yapıya taşımak.

- [ ] **Yapılandırma yönetimi:** Tüm sırları `.env` + `python-dotenv`'e taşı
- [ ] **Async düzeltmesi:** `asyncio.run()` yerine Flask 2.x async view veya `aiohttp` tabanlı çözüm
- [ ] **Hata yönetimi:** Merkezi `error_handler`, anlamlı HTTP durum kodları
- [ ] **Loglama:** `structlog` ile JSON formatında yapılandırılmış log akışı
- [ ] **Docker Compose:** `app`, `neo4j` ve `ollama` servislerini tek komutla ayağa kaldır
- [ ] **Temel testler:** `/api/process` ve `/api/ask` endpoint'leri için pytest suite

---

## v1.2 — Graf Kalitesi & Retrieval İyileştirmesi

> **Hedef:** Ham triplet çekimini zeki ve ölçeklenebilir bir retrieval'a dönüştürmek.

- [ ] **Semantik retrieval:** Soruya göre Neo4j tam tarama yerine vektör benzerliği ile ilgili alt-graf seçimi
- [ ] **Graf filtreleme:** Düğüm tipi (Entity / Episodic / Community) bazlı sorgu filtreleri
- [ ] **Bağlam sıkıştırma:** Büyük graflarda prompt token limitini aşmamak için triplet önceliklendirme
- [ ] **Graf istatistikleri endpoint'i:** `GET /api/stats` — düğüm/kenar sayısı, tip dağılımı, son ekleme zamanı
- [ ] **Graf arama:** `/api/search?q=...` — ada göre düğüm araması

---

## v1.3 — Arayüz & Deneyim

> **Hedef:** Görselleştirmeyi analitik bir araca dönüştürmek.

- [ ] **Düğüm detay paneli:** Tıklanan düğümün tüm özelliklerini yan panelde göster
- [ ] **Alt-graf izolasyonu:** Seçili düğümün 1–2 hop komşularını vurgula, geri kalanı soldur
- [ ] **Graf arama arayüzü:** Metin bazlı düğüm filtresi (gerçek zamanlı)
- [ ] **Sohbet geçmişi:** Oturum bazlı soru-cevap geçmişini tarayıcı `localStorage`'a kaydet
- [ ] **Karanlık/Açık tema:** Sistem temasına uyumlu CSS değişken tabanlı geçiş
- [ ] **Responsive tasarım:** Tablet ve mobil ekranlar için panel düzeni adaptasyonu

---

## v2.0 — Çoklu Ajan & Uzun Süreli Hafıza

> **Hedef:** Mimarinin gerçek bir otonom ajan sistemine evrilmesi.

- [ ] **Çok kullanıcılı oturum yönetimi:** Her kullanıcıya izole hafıza alanı (namespace)
- [ ] **Ajan kimliği:** Her bilgi parçasının kaynağını izle (hangi ajan, hangi zaman damgası)
- [ ] **Zamana duyarlı hafıza:** Graphiti'nin temporal API'sini kullanarak geçmiş durumları sorgula
- [ ] **Hafıza konsolidasyonu:** Belirli aralıklarla yinelenen/çelişen tripletleri birleştiren arka plan görevi
- [ ] **Webhook / olay tetikleme:** Yeni bilgi eklendiğinde dış sistemlere bildirim gönder
- [ ] **Embedding depolama (Milvus):** Graphiti'nin Milvus entegrasyonunu etkinleştir

---

## v2.x — Üretim Hazırlığı

> **Hedef:** Üretime alınabilir, gözlemlenebilir bir sistem.

- [ ] **Kimlik doğrulama:** JWT tabanlı API güvenliği
- [ ] **Rate limiting:** `flask-limiter` ile endpoint bazlı istek sınırı
- [ ] **Metrik izleme:** Prometheus + Grafana ile uçtan uca gecikme ve hata oranı takibi
- [ ] **CI/CD:** GitHub Actions ile otomatik test + Docker image build pipeline
- [ ] **Graf yedekleme:** Zamanlanmış Neo4j dump → nesne depolama (S3/MinIO)
- [ ] **Model hot-swap:** Çalışırken LLM modelini değiştirme (config endpoint)

---

## Öncelik Matrisi

| Görev | Etki | Çaba | Öncelik |
|---|---|---|---|
| `.env` yapılandırması | Yüksek | Düşük | **P0** |
| Docker Compose | Yüksek | Orta | **P0** |
| Async düzeltmesi | Yüksek | Orta | **P1** |
| Semantik retrieval | Çok Yüksek | Yüksek | **P1** |
| Düğüm detay paneli | Orta | Düşük | **P2** |
| Çok kullanıcılı oturum | Yüksek | Yüksek | **P2** |
| Kimlik doğrulama | Yüksek | Orta | **P2** |

---

> Son güncelleme: Şubat 2026
