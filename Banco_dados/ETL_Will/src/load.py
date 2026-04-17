"""
clean.py — Etapa 3: Tratamento dos dados
Lê as coleções raw_, aplica limpeza e grava nas coleções _clean.
 
Problemas tratados:
  - Tipos incorretos (ano como string -> int)
  - Anos inválidos (0, nulos, fora de 1800-2030) -> None
  - Registros duplicados (id_pessoa repetido)
  - Nomes / títulos com espaços extras
  - IDs de produção sem título (descartados)
  - papéis nulos ou brancos em equipe
  - ids de pessoa/produção em equipe sem correspondência
 
Correção de performance:
  - Usa insert_many em vez de bulk_write com UpdateOne/upsert
  - Batch reduzido para 2.000 documentos
  - socketTimeoutMS aumentado para 5 minutos
"""
 
import os
import sys
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
 
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = "bd_producao_artistica"
 
TIPO_MAP = {
    1: "Filme",
    2: "Série de TV",
    3: "Episódio de TV",
    4: "Mini-série",
    5: "Documentário",
    6: "Curta-metragem",
    7: "Video Game / Outro",
}
 
ANO_MIN = 1800
ANO_MAX = 2030
BATCH   = 2_000
 
 
def clean_string(value):
    if value is None:
        return None
    v = str(value).strip()
    return v if v else None
 
 
def parse_ano(value):
    try:
        ano = int(value)
        if ANO_MIN <= ano <= ANO_MAX:
            return ano
    except (TypeError, ValueError):
        pass
    return None
 
 
def insert_batch(col, docs):
    if not docs:
        return
    try:
        col.insert_many(docs, ordered=False)
    except BulkWriteError as e:
        erros_graves = [
            d for d in e.details.get("writeErrors", [])
            if d.get("code") != 11000
        ]
        if erros_graves:
            print(f"  [WARN] Erros inesperados no batch: {erros_graves[:2]}")
 
 
def clean_pessoa(db):
    print("── Limpando pessoa ──")
    raw = db["raw_pessoa"]
    col = db["pessoa_clean"]
    col.drop()
    col.create_index("id_pessoa", unique=True)
 
    raw_ok = duplicatas = sem_nome = 0
    seen_ids = set()
    batch = []
 
    for doc in raw.find({}, {"_id": 0}):
        id_pessoa = doc.get("id_pessoa")
        nome      = clean_string(doc.get("nome"))
 
        if not nome:
            sem_nome += 1
            continue
        if id_pessoa in seen_ids:
            duplicatas += 1
            continue
        seen_ids.add(id_pessoa)
 
        batch.append({"id_pessoa": id_pessoa, "nome": nome})
        raw_ok += 1
 
        if len(batch) >= BATCH:
            insert_batch(col, batch)
            batch = []
            print(f"  -> {raw_ok:,} processados...", end="\r")
 
    insert_batch(col, batch)
    print(f"  [OK] {raw_ok:,} pessoas | {duplicatas} duplicatas | {sem_nome} sem nome")
    return seen_ids
 
 
def clean_producao(db):
    print("── Limpando producao ──")
    raw = db["raw_producao"]
    col = db["producao_clean"]
    col.drop()
    col.create_index("id_producao", unique=True)
    col.create_index("ano")
    col.create_index("tipo_id")
 
    raw_ok = ano_inv = sem_titulo = 0
    batch = []
 
    for doc in raw.find({}, {"_id": 0}):
        id_prod = doc.get("id_producao")
        titulo  = clean_string(doc.get("titulo"))
        ano     = parse_ano(doc.get("ano"))
        tipo_id = doc.get("tipo_id")
 
        if not titulo:
            sem_titulo += 1
            continue
        if ano is None and doc.get("ano") is not None:
            ano_inv += 1
 
        batch.append({
            "id_producao": id_prod,
            "titulo":      titulo,
            "ano":         ano,
            "tipo_id":     tipo_id,
            "tipo_nome":   TIPO_MAP.get(tipo_id, "Desconhecido"),
        })
        raw_ok += 1
 
        if len(batch) >= BATCH:
            insert_batch(col, batch)
            batch = []
            print(f"  -> {raw_ok:,} processados...", end="\r")
 
    insert_batch(col, batch)
    print(f"  [OK] {raw_ok:,} producoes | {ano_inv:,} anos invalidos (->null) | {sem_titulo} sem titulo")
 
    return set(doc["id_producao"] for doc in col.find({}, {"id_producao": 1, "_id": 0}))
 
 
def clean_equipe(db, ids_pessoa_validos, ids_producao_validos):
    print("── Limpando equipe ──")
    raw = db["raw_equipe"]
    col = db["equipe_clean"]
    col.drop()
    col.create_index([("id_producao", 1), ("id_pessoa", 1)])
    col.create_index("papel")
 
    raw_ok = papel_nulo = sem_ref = 0
    batch = []
 
    for doc in raw.find({}, {"_id": 0}):
        id_prod   = doc.get("id_producao")
        id_pessoa = doc.get("id_pessoa")
        papel = clean_string(
            doc.get("papel") or doc.get("role") or doc.get("funcao") or doc.get("cargo")
        )
 
        if not papel:
            papel_nulo += 1
            continue
        if id_prod not in ids_producao_validos or id_pessoa not in ids_pessoa_validos:
            sem_ref += 1
            continue
 
        batch.append({
            "id_producao": id_prod,
            "id_pessoa":   id_pessoa,
            "papel":       papel.title(),
        })
        raw_ok += 1
 
        if len(batch) >= BATCH:
            insert_batch(col, batch)
            batch = []
            print(f"  -> {raw_ok:,} processados...", end="\r")
 
    insert_batch(col, batch)
    print(f"  [OK] {raw_ok:,} vinculos | {papel_nulo} papel nulo | {sem_ref} sem referencia")
 
 
def main():
    print(f"Conectando ao MongoDB: {MONGO_URI}")
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10_000,
        socketTimeoutMS=300_000,    # 5 minutos - aguenta batches grandes
        connectTimeoutMS=10_000,
    )
 
    try:
        client.admin.command("ping")
        print("Conexao OK!\n")
    except Exception as e:
        print(f"[ERRO] {e}")
        sys.exit(1)
 
    db = client[DB_NAME]
 
    ids_pessoa   = clean_pessoa(db)
    print()
    ids_producao = clean_producao(db)
    print()
    clean_equipe(db, ids_pessoa, ids_producao)
    print()
 
    print("Tratamento concluido!")
    client.close()
 
 
if __name__ == "__main__":
    main()