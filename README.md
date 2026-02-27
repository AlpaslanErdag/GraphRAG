# GraphRAG V1 — Ajan Hafıza Sistemi

> **Graph Retrieval-Augmented Generation** mimarisi üzerine kurulu, yerel LLM destekli bilgi grafiği hafıza motoru.

---

## Mimari

```
Kullanıcı (Web UI)
      │
      ▼
 Flask API (app.py)
      │
      ├──► Graphiti (Hafıza Motoru)
      │         │
      │         └──► Ollama / Mistral 7B  ──► Neo4j (Bilgi Grafiği)
      │
      └──► Graph RAG Sorgu Pipeline
                │
                ├── 1. RETRIEVAL  : Neo4j'den triplet çekimi
                ├── 2. AUGMENT    : Bağlamı prompt'a ekleme
                └── 3. GENERATE   : Ollama / Llama 3.1 ile cevap üretimi
```

---

## Özellikler

| Özellik | Açıklama |
|---|---|
| **Bilgi Enjeksiyonu** | Serbest metin → LLM → Varlık/İlişki grafiği |
| **3D / 2D Graf Görünümü** | `force-graph` tabanlı interaktif görselleştirme |
| **Graph RAG Sorgulama** | Neo4j triplet bağlamı + Llama 3.1 çıkarımı |
| **Hafıza Sıfırlama** | Tek tıkla Neo4j veritabanı temizleme |
| **Tam Yerel Çalışma** | Hiçbir bulut API'si kullanılmaz (Ollama + Neo4j) |

---

## Teknoloji Yığını

| Katman | Teknoloji |
|---|---|
| **Backend** | Python 3.11+, Flask |
| **Hafıza Motoru** | [Graphiti](https://github.com/getzep/graphiti) |
| **Graf Veritabanı** | Neo4j 5.x (Bolt protokolü) |
| **LLM — İnjeksiyon** | Ollama · `mistral:7b` |
| **LLM — Sorgu** | Ollama · `llama3.1:8b` |
| **Frontend** | Vanilla JS, `3d-force-graph`, `force-graph` |
| **Font** | Inter, JetBrains Mono |

---

## Kurulum

### 1. Bağımlılıklar

```bash
pip install flask graphiti-core neo4j requests
```

### 2. Neo4j Başlat

```bash
# Docker ile
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

### 3. Ollama Modelleri İndir

```bash
ollama pull mistral:7b
ollama pull llama3.1:8b
```

### 4. Uygulamayı Çalıştır

```bash
python app.py
```

Uygulama `http://127.0.0.1:5000` adresinde açılır.

---

## Yapılandırma

`app.py` içindeki ortam değişkenleri:

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `OPENAI_API_KEY` | `ollama-local` | Ollama için kukla anahtar |
| `OPENAI_BASE_URL` | `http://localhost:11434/v1` | Ollama OpenAI-compat. endpoint |
| `OPENAI_MODEL_NAME` | `mistral:7b` | Graphiti injeksiyon modeli |
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j bağlantısı |
| `NEO4J_USER` | `neo4j` | Neo4j kullanıcı adı |
| `NEO4J_PASSWORD` | `password` | Neo4j şifresi |

> **Güvenlik:** Üretim ortamında `NEO4J_PASSWORD` ve diğer sırları `.env` dosyasına taşıyın. Asla kaynak koda gömmeyin.

---

## API Referansı

| Endpoint | Metot | Açıklama |
|---|---|---|
| `GET /` | GET | Ana arayüz (index.html) |
| `POST /api/process` | POST | Metin → Graf enjeksiyonu |
| `GET /api/graph` | GET | Tüm düğüm ve ilişkileri döner |
| `POST /api/ask` | POST | Graph RAG sorgusu çalıştırır |
| `POST /api/clear` | POST | Tüm hafızayı siler |

### `/api/process` — İstek

```json
{ "text": "Varlıklar ve ilişkiler içeren metin..." }
```

### `/api/ask` — İstek / Yanıt

```json
// İstek
{ "question": "Bilişsel Motor ne yapar?" }

// Yanıt
{ "answer": "Bilişsel Motor, Ajan Çekirdeğini yönetir ve..." }
```

---

## Proje Yapısı

```
GraphRAG_V1/
├── app.py                  # Flask backend + tüm API endpoint'leri
├── templates/
│   └── index.html          # Modern tek sayfa arayüzü
└── README.md
```

---
