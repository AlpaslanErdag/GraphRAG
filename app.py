import os
import asyncio
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
from graphiti_core import Graphiti
from neo4j import GraphDatabase
import requests # Dosyanın en üstüne ekleyin

# ==========================================
# AYARLAR (Ollama & Llama 3.1 Yönlendirmesi)
# ==========================================
os.environ["OPENAI_API_KEY"] = "ollama-local"
os.environ["OPENAI_BASE_URL"] = "http://localhost:11434/v1"
# Graphiti'nin karmaşık JSON yapısını (Tool Calling) çözebilmesi için Llama 3.1 kullanıyoruz
os.environ["OPENAI_MODEL_NAME"] = "mistral:7b" 

# Neo4j Veritabanı Ayarları
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

app = Flask(__name__, template_folder="templates")

# 3D Arayüz için Neo4j'den ham veri çekecek sürücü
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# ==========================================
# GRAPHITI (HAFIZA MOTORU) İŞLEMLERİ
# ==========================================
async def ingest_to_graphiti(text):
    """Graphiti'nin arka planda LLM kullanarak bilgiyi işlemesi ve grafiğe dönüştürmesi"""
    client = Graphiti(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    # 1. İndeks Oluşturma (Zaten varsa hatayı yoksay)
    try:
        await client.build_indices_and_constraints()
    except Exception as e:
        if "EquivalentSchemaRuleAlreadyExists" in str(e):
            print("İndeksler zaten mevcut, devam ediliyor...")
        else:
            print(f"İndeks uyarısı (Önemsiz): {e}")
    
    # 2. Yeni Bilgiyi Hafıza Ağına Ekleme
    try:
        await client.add_episode(
            name="Manuel Arayüz Girişi",
            episode_body=text,
            source_description="Flask Web UI",
            reference_time=datetime.now(timezone.utc) # Graphiti için zorunlu zaman damgası
        )
        print("-> Metin başarıyla işlendi ve bilgi grafiğine eklendi.")
    except Exception as e:
        print(f"-> Hata oluştu: {e}")
    finally:
        await client.close()

# ==========================================
# FLASK WEB ENDPOINT'LERİ
# ==========================================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/process", methods=["POST"])
def process():
    data = request.json
    text = data.get("text", "").strip()
    
    if not text:
        return jsonify({"error": "Metin boş olamaz."}), 400

    # Flask senkron olduğu için async fonksiyonu event loop'ta tetikliyoruz
    asyncio.run(ingest_to_graphiti(text))
    
    return jsonify({"status": "success", "message": "Bilgi başarıyla ajanın hafıza ağına eklendi."})

@app.route("/api/graph", methods=["GET"])
def get_graph():
    """Neo4j'deki düğümleri ve ilişkileri 3D arayüzün anlayacağı JSON formatına çevirir"""
    nodes_dict = {}
    links = []
    
    with driver.session() as session:
        # Yeni Neo4j standartlarına (elementId) uygun, güvenli Cypher sorgusu
        result = session.run("""
            MATCH (n)
            OPTIONAL MATCH (n)-[r]->(m)
            RETURN elementId(n) AS s_id, n.name AS s_name, labels(n)[0] AS s_label,
                   elementId(m) AS t_id, m.name AS t_name, labels(m)[0] AS t_label,
                   type(r) AS relation
        """)
        for record in result:
            # Kaynak (Source) Düğüm
            s_id = str(record["s_id"]) if record["s_id"] is not None else None
            if s_id:
                # İsim yoksa etiketini (örn: Episodic, Entity) isim olarak kullan
                s_name = str(record["s_name"]) if record["s_name"] else str(record["s_label"])
                if s_id not in nodes_dict:
                    nodes_dict[s_id] = {"id": s_id, "name": s_name}
                
            # Hedef (Target) Düğüm ve İlişki
            t_id = str(record["t_id"]) if record["t_id"] is not None else None
            if t_id:
                t_name = str(record["t_name"]) if record["t_name"] else str(record["t_label"])
                if t_id not in nodes_dict:
                    nodes_dict[t_id] = {"id": t_id, "name": t_name}
                    
                links.append({
                    "source": s_id,
                    "target": t_id,
                    "name": str(record["relation"])
                })
                
    return jsonify({"nodes": list(nodes_dict.values()), "links": links})

@app.route("/api/clear", methods=["POST"])
def clear_graph():
    """Neo4j veritabanındaki tüm düğümleri ve ilişkileri kalıcı olarak siler"""
    with driver.session() as session:
        # DETACH DELETE n: Düğümü ve ona bağlı tüm ilişkileri yok eder
        session.run("MATCH (n) DETACH DELETE n")
    return jsonify({"status": "success", "message": "Ajan hafızası tamamen sıfırlandı."})

@app.route("/api/ask", methods=["POST"])
def ask_question():
    """Graph RAG: Soruyu alır, Neo4j'den bilgi grafiğini çeker ve Ollama'ya sorar."""
    data = request.json
    question = data.get("question", "").strip()
    
    if not question:
        return jsonify({"error": "Soru boş olamaz."}), 400

    # 1. RETRIEVAL (Geri Getirme): Neo4j'den tüm mevcut ilişkileri (Triplets) çek
    graph_context = []
    with driver.session() as session:
        # Daha okunaklı bir format için varlık ve ilişkileri metne döküyoruz
        result = session.run("""
            MATCH (n)-[r]->(m)
            RETURN COALESCE(n.name, labels(n)[0]) AS source,
                   type(r) AS relation,
                   COALESCE(m.name, labels(m)[0]) AS target
        """)
        for record in result:
            graph_context.append(f"- {record['source']} ({record['relation']}) {record['target']}")
    
    if not graph_context:
        return jsonify({"answer": "Ajanın hafızası şu an boş. Önce ağa bilgi enjekte edin."})

    context_text = "\n".join(graph_context)

    # 2. AUGMENTATION & GENERATION (Bağlam Ekleme ve Üretim): Ollama'ya gönder
    prompt = f"""Sen bir bilgi grafiği (Knowledge Graph) uzmanı ve otonom ajansın.
Aşağıda sana hafızandaki varlık ilişkileri (triplets) verilmiştir.
Sadece bu grafikteki ilişkileri kullanarak kullanıcının sorusuna adım adım, mantıksal bir çıkarım yaparak Türkçe cevap ver. 
Grafikte olmayan hiçbir bilgiyi uydurma.

Hafıza Ağı (Bilgi Grafiği):
{context_text}

Kullanıcının Sorusu: {question}
Cevap:"""

    try:
        # Llama 3.1'i doğrudan Ollama API'si üzerinden çağırıyoruz
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False
        })
        response.raise_for_status()
        answer = response.json().get("response", "Cevap üretilemedi.")
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"LLM ile iletişimde hata oluştu: {str(e)}"}), 500


if __name__ == "__main__":
    print("Sistem http://127.0.0.1:5000 adresinde ayağa kalktı.")
    app.run(debug=True, port=5000)