"""
ingest.py — Etapa 2: Ingestão dos dados brutos no MongoDB
Carrega os arquivos JSONL nas coleções raw_ sem tratamento.
"""

import json
import os
import sys
from pathlib import Path
from pymongo import MongoClient, InsertOne
from pymongo.errors import BulkWriteError

# ── Configuração ──────────────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = "bd_producao_artistica"

DATA_DIR  = Path(__file__).parent / "data"

FILES = {
    "raw_pessoa":   DATA_DIR / "pessoa.jsonl",
    "raw_producao": DATA_DIR / "producao.jsonl",
    "raw_equipe":   DATA_DIR / "equipe.jsonl",
}

BATCH_SIZE = 5_000   # documentos por batch de insert


# ── Helpers ───────────────────────────────────────────────────────────────────
def read_jsonl(filepath: Path):
    """Lê um arquivo JSONL linha a linha e retorna um gerador de dicts."""
    with open(filepath, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                print(f"  [WARN] Linha {lineno} inválida em {filepath.name}: {e}")


def ingest_collection(db, collection_name: str, filepath: Path):
    """Faz a ingestão de um arquivo JSONL em uma coleção raw do MongoDB."""
    if not filepath.exists():
        print(f"  [SKIP] Arquivo não encontrado: {filepath}")
        return

    col = db[collection_name]

    # Remove dados anteriores para evitar duplicação em re-execuções
    deleted = col.delete_many({}).deleted_count
    if deleted:
        print(f"  [INFO] {deleted} documentos antigos removidos de '{collection_name}'")

    batch   = []
    total   = 0
    batches = 0

    for doc in read_jsonl(filepath):
        batch.append(InsertOne(doc))

        if len(batch) >= BATCH_SIZE:
            try:
                col.bulk_write(batch, ordered=False)
            except BulkWriteError as e:
                print(f"  [ERROR] BulkWrite: {e.details}")
            total   += len(batch)
            batches += 1
            batch    = []
            print(f"    → {total:,} docs inseridos...", end="\r")

    # Flush do último batch
    if batch:
        try:
            col.bulk_write(batch, ordered=False)
        except BulkWriteError as e:
            print(f"  [ERROR] BulkWrite: {e.details}")
        total += len(batch)

    print(f"  [OK] '{collection_name}': {total:,} documentos inseridos em {batches+1} batches.")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"Conectando ao MongoDB: {MONGO_URI}")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5_000)

    try:
        client.admin.command("ping")
        print("Conexão OK!\n")
    except Exception as e:
        print(f"[ERRO] Não foi possível conectar ao MongoDB: {e}")
        sys.exit(1)

    db = client[DB_NAME]

    for collection_name, filepath in FILES.items():
        print(f"Ingerindo → {collection_name}  ({filepath.name})")
        ingest_collection(db, collection_name, filepath)
        print()

    print("Ingestão concluída!")
    client.close()


if __name__ == "__main__":
    main()