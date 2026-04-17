"""
queries.py — Etapa 5: Consultas e Agregações no MongoDB
Executa todas as consultas exigidas pelo trabalho e imprime os resultados.
 
Consultas simples (filtro):
  Q1 – Produções de um tipo específico
  Q2 – Produções de um ano específico
  Q3 – Produções sem participantes registrados
 
Agregações:
  A1 – Quantidade de produções por tipo
  A2 – Média de participantes por tipo de produção
 
Ranking:
  R1 – Top 10 pessoas com mais participações
 
Vantagem/dificuldade do modelo documental:
  D1 – Todas as produções com seus participantes em UMA só consulta (vantagem)
  D2 – Consulta "quem trabalhou junto" (dificuldade: exige $unwind + $group)
"""
 
import os
import sys
from pprint import pprint
from pymongo import MongoClient
 
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = "bd_producao_artistica"
 
 
def separator(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)
 
 
def main():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5_000)
    try:
        client.admin.command("ping")
    except Exception as e:
        print(f"[ERRO] {e}")
        sys.exit(1)
 
    db  = client[DB_NAME]
    col = db["producoes_com_participantes"]
 
    # ── Q1: Produções do tipo "Filme" (tipo_id=1) ─────────────────────────────
    separator("Q1 – Filmes com mais de 50 participantes (amostra 5)")
    cursor = col.find(
        {"tipo_id": 1, "total_participantes": {"$gt": 50}},
        {"titulo": 1, "ano": 1, "total_participantes": 1, "_id": 0}
    ).sort("total_participantes", -1).limit(5)
    for doc in cursor:
        print(doc)
 
    # ── Q2: Produções de um ano específico ────────────────────────────────────
    separator("Q2 – Produções lançadas em 2000")
    count_2000 = col.count_documents({"ano": 2000})
    print(f"Total de produções em 2000: {count_2000:,}")
    for doc in col.find({"ano": 2000}, {"titulo": 1, "tipo_nome": 1, "_id": 0}).limit(5):
        print(doc)
 
    # ── Q3: Produções sem participantes ───────────────────────────────────────
    separator("Q3 – Produções sem nenhum participante registrado")
    sem_part = col.count_documents({"total_participantes": 0})
    total    = col.count_documents({})
    if total > 0:
        print(f"Sem participantes: {sem_part:,} de {total:,} ({sem_part/total*100:.1f}%)")
    else:
        print("Sem participantes: 0 de 0 (0.0%)")
 
    # ── A1: Quantidade de produções por tipo ──────────────────────────────────
    separator("A1 – Quantidade de produções por tipo")
    pipeline_a1 = [
        {"$group": {
            "_id":       "$tipo_nome",
            "total":     {"$sum": 1},
            "com_ano":   {"$sum": {"$cond": [{"$ne": ["$ano", None]}, 1, 0]}},
        }},
        {"$sort": {"total": -1}},
    ]
    for doc in col.aggregate(pipeline_a1):
        print(f"  {doc['_id']:25s}  total={doc['total']:>8,}  com_ano={doc['com_ano']:>8,}")
 
    # ── A2: Média de participantes por tipo ───────────────────────────────────
    separator("A2 – Média de participantes por tipo")
    pipeline_a2 = [
        {"$group": {
            "_id":   "$tipo_nome",
            "media": {"$avg": "$total_participantes"},
            "max":   {"$max": "$total_participantes"},
        }},
        {"$sort": {"media": -1}},
        {"$project": {
            "_id":   1,
            "media": {"$round": ["$media", 2]},
            "max":   1,
        }},
    ]
    for doc in col.aggregate(pipeline_a2):
        print(f"  {doc['_id']:25s}  média={doc['media']:>6}  max={doc['max']:>5}")
 
    # ── R1: Ranking – Top 10 pessoas com mais participações ───────────────────
    separator("R1 – Top 10 pessoas com mais participações")
    pipeline_r1 = [
        {"$unwind": "$participantes"},
        {"$group": {
            "_id":   "$participantes.nome",
            "total": {"$sum": 1},
            "papeis": {"$addToSet": "$participantes.papel"},
        }},
        {"$sort": {"total": -1}},
        {"$limit": 10},
        {"$project": {
            "nome":  "$_id",
            "total": 1,
            "papeis": {"$slice": ["$papeis", 3]},  # mostra até 3 papéis
            "_id":   0,
        }},
    ]
    for i, doc in enumerate(col.aggregate(pipeline_r1, allowDiskUse=True), start=1):
        print(f"  {i:2}. {doc['nome']:30s} {doc['total']:>5} participações | papéis: {doc['papeis']}")
 
    # ── D1: Vantagem – busca completa sem JOIN ────────────────────────────────
    separator("D1 – Vantagem do modelo documental: busca completa sem JOIN")
    print("Buscando 1 filme com todos os seus participantes (sem nenhum JOIN):")
    doc = col.find_one(
        {"tipo_id": 1, "total_participantes": {"$gt": 10}},
        {"titulo": 1, "ano": 1, "tipo_nome": 1, "participantes": {"$slice": 5}, "_id": 0}
    )
    if doc:
        print(f"\n  Título: {doc['titulo']} ({doc['ano']}) – {doc['tipo_nome']}")
        print("  Primeiros 5 participantes:")
        for p in doc.get("participantes", []):
            print(f"    • {p['nome']} → {p['papel']}")
    print("\n  → No MongoDB, uma única query retorna tudo.")
    print("    No SQL, precisaríamos de JOIN entre 3 tabelas.")
 
    # ── D2: Dificuldade – anos com mais produções ─────────────────────────────
    separator("D2 – Anos com mais produções (top 10)")
    pipeline_d2 = [
        {"$match":  {"ano": {"$ne": None}}},
        {"$group":  {"_id": "$ano", "total": {"$sum": 1}}},
        {"$sort":   {"total": -1}},
        {"$limit":  10},
        {"$project": {"ano": "$_id", "total": 1, "_id": 0}},
    ]
    for doc in col.aggregate(pipeline_d2):
        print(f"  {doc['ano']}: {doc['total']:,} produções")
 
    print("\nConsultas concluídas!")
    client.close()
 
 
if __name__ == "__main__":
    main()