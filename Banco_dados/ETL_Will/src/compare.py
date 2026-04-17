"""
postgres_compare.py — Etapa 6: Comparação com banco relacional (PostgreSQL)
Carrega os dados limpos no PostgreSQL e executa consultas equivalentes.
 
Pré-requisito: pip install psycopg2-binary pymongo
"""
 
import os
import sys
import psycopg2
from psycopg2.extras import execute_values
from pymongo import MongoClient
 
# ── Configuração ──────────────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
PG_DSN    = os.getenv(
    "PG_DSN",
    "host=localhost port=5432 dbname=meu_banco user=admin password=senha_segura_123"
)
DB_NAME   = "bd_producao_artistica"
BATCH     = 5_000
 
 
# ── Criação do schema relacional ──────────────────────────────────────────────
DDL = """
DROP TABLE IF EXISTS equipe CASCADE;
DROP TABLE IF EXISTS producao CASCADE;
DROP TABLE IF EXISTS pessoa CASCADE;
DROP TABLE IF EXISTS tipo_producao CASCADE;
 
CREATE TABLE tipo_producao (
    tipo_id   INTEGER PRIMARY KEY,
    tipo_nome VARCHAR(50) NOT NULL
);
 
CREATE TABLE producao (
    id_producao INTEGER PRIMARY KEY,
    titulo      TEXT    NOT NULL,
    ano         INTEGER,
    tipo_id     INTEGER REFERENCES tipo_producao(tipo_id)
);
 
CREATE TABLE pessoa (
    id_pessoa INTEGER PRIMARY KEY,
    nome      TEXT NOT NULL
);
 
CREATE TABLE equipe (
    id_producao INTEGER REFERENCES producao(id_producao),
    id_pessoa   INTEGER REFERENCES pessoa(id_pessoa),
    papel       TEXT,
    PRIMARY KEY (id_producao, id_pessoa, papel)
);
 
CREATE INDEX idx_producao_ano    ON producao(ano);
CREATE INDEX idx_producao_tipo   ON producao(tipo_id);
CREATE INDEX idx_equipe_pessoa   ON equipe(id_pessoa);
CREATE INDEX idx_equipe_producao ON equipe(id_producao);
"""
 
 
def pg_load(mongo_db, pg_conn):
    cur = pg_conn.cursor()
 
    print("Criando schema...")
    cur.execute(DDL)
    pg_conn.commit()
 
    # Tipos
    tipos = [
        (1, "Filme"), (2, "Série de TV"), (3, "Episódio de TV"),
        (4, "Mini-série"), (5, "Documentário"), (6, "Curta-metragem"),
        (7, "Video Game / Outro"),
    ]
    execute_values(cur, "INSERT INTO tipo_producao VALUES %s", tipos)
    pg_conn.commit()
 
    # Pessoas
    print("Carregando pessoas...")
    batch, total = [], 0
    for doc in mongo_db["pessoa_clean"].find({}, {"id_pessoa": 1, "nome": 1, "_id": 0}):
        batch.append((doc["id_pessoa"], doc["nome"]))
        if len(batch) >= BATCH:
            execute_values(cur, "INSERT INTO pessoa VALUES %s ON CONFLICT DO NOTHING", batch)
            total += len(batch); batch = []
            print(f"  → {total:,}...", end="\r")
    if batch:
        execute_values(cur, "INSERT INTO pessoa VALUES %s ON CONFLICT DO NOTHING", batch)
        total += len(batch)
    pg_conn.commit()
    print(f"  [OK] {total:,} pessoas inseridas.")
 
    # Produções
    print("Carregando produções...")
    batch, total = [], 0
    for doc in mongo_db["producao_clean"].find({}, {"id_producao":1,"titulo":1,"ano":1,"tipo_id":1,"_id":0}):
        batch.append((doc["id_producao"], doc["titulo"], doc.get("ano"), doc["tipo_id"]))
        if len(batch) >= BATCH:
            execute_values(cur, "INSERT INTO producao VALUES %s ON CONFLICT DO NOTHING", batch)
            total += len(batch); batch = []
            print(f"  → {total:,}...", end="\r")
    if batch:
        execute_values(cur, "INSERT INTO producao VALUES %s ON CONFLICT DO NOTHING", batch)
        total += len(batch)
    pg_conn.commit()
    print(f"  [OK] {total:,} produções inseridas.")
 
    
    # Equipe
    print("Carregando equipe...")
    batch, total = [], 0

    query_equipe = """
    INSERT INTO equipe (id_producao, id_pessoa, papel)
    VALUES %s
    ON CONFLICT (id_producao, id_pessoa, papel) DO NOTHING
    """

    for doc in mongo_db["equipe_clean"].find({}, {"id_producao":1,"id_pessoa":1,"papel":1,"_id":0}):
        batch.append((doc["id_producao"], doc["id_pessoa"], doc["papel"]))

        if len(batch) >= BATCH:
            execute_values(cur, query_equipe, batch)
            total += len(batch)
            batch = []
            print(f"  → {total:,}...", end="\r")

    if batch:
        execute_values(cur, query_equipe, batch)
        total += len(batch)

    pg_conn.commit()
    print(f"  [OK] {total:,} vínculos inseridos.")
 
 
def pg_queries(pg_conn):
    cur = pg_conn.cursor()
 
    print("\n── Consultas SQL equivalentes ──")
 
    # Q1 equivalente: filmes com mais de 50 participantes
    print("\nQ1 – Top 5 filmes com mais participantes:")
    cur.execute("""
        SELECT p.titulo, p.ano, COUNT(e.id_pessoa) AS participantes
        FROM producao p
        JOIN equipe e ON e.id_producao = p.id_producao
        WHERE p.tipo_id = 1
        GROUP BY p.id_producao, p.titulo, p.ano
        HAVING COUNT(e.id_pessoa) > 50
        ORDER BY participantes DESC
        LIMIT 5;
    """)
    for row in cur.fetchall():
        print(f"  {row}")
 
    # A1 equivalente: produções por tipo
    print("\nA1 – Produções por tipo:")
    cur.execute("""
        SELECT t.tipo_nome, COUNT(*) AS total
        FROM producao p
        JOIN tipo_producao t ON t.tipo_id = p.tipo_id
        GROUP BY t.tipo_nome
        ORDER BY total DESC;
    """)
    for row in cur.fetchall():
        print(f"  {row}")
 
    # R1 equivalente: top 10 pessoas
    print("\nR1 – Top 10 pessoas com mais participações:")
    cur.execute("""
        SELECT pe.nome, COUNT(*) AS participacoes
        FROM equipe e
        JOIN pessoa pe ON pe.id_pessoa = e.id_pessoa
        GROUP BY pe.id_pessoa, pe.nome
        ORDER BY participacoes DESC
        LIMIT 10;
    """)
    for i, row in enumerate(cur.fetchall(), 1):
        print(f"  {i:2}. {row[0]:30s} {row[1]:>5}")
 
 
def main():
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5_000)
    mongo_db     = mongo_client[DB_NAME]
 
    pg_conn = psycopg2.connect(PG_DSN)
 
    print("=== Carga no PostgreSQL ===")
    pg_load(mongo_db, pg_conn)
 
    print("\n=== Consultas SQL ===")
    pg_queries(pg_conn)
 
    pg_conn.close()
    mongo_client.close()
    print("\nComparação concluída!")
 
 
if __name__ == "__main__":
    main()