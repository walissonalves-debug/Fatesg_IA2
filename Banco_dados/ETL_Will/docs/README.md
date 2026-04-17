# BD_Producao_Artistica — Pipeline ETL com MongoDB

Trabalho prático de ETL e armazenamento em banco não relacional (SENAI).

## Pré-requisitos

- Docker e Docker Compose
- Python 3.10+
- pip

## Instalação das dependências Python

```bash
pip install pymongo psycopg2-binary
```

## Como executar

### 1. Suba os bancos com Docker

```bash
cd docker
docker-compose up -d
```

> MongoDB ficará em `localhost:27017` e PostgreSQL em `localhost:5432`.

### 2. Coloque os dados na pasta `data/`

Baixe os arquivos JSONL do dataset e coloque em:

```
data/
├── pessoa.jsonl
├── producao.jsonl
└── equipe.jsonl
```

### 3. Execute o pipeline em ordem

```bash
# Etapa 2 – Ingestão bruta
python src/ingest.py

# Etapa 3 – Tratamento
python src/clean.py

# Etapa 4 – Coleção documental enriquecida
python src/load.py

# Etapa 5 – Consultas MongoDB
python src/queries.py

# Etapa 6 – Carga e comparação com PostgreSQL (opcional)
python src/postgres_compare.py
```

## Estrutura das coleções MongoDB

| Coleção | Descrição |
|---|---|
| `raw_pessoa` | Pessoas como vieram do JSONL |
| `raw_producao` | Produções como vieram do JSONL |
| `raw_equipe` | Equipe como veio do JSONL |
| `pessoa_clean` | Pessoas sem duplicatas e nomes limpos |
| `producao_clean` | Produções com `ano` tipado e `tipo_nome` adicionado |
| `equipe_clean` | Vínculos com referências válidas e papéis padronizados |
| `producoes_com_participantes` | Coleção documental rica (dados aninhados) |

## Variáveis de ambiente

| Variável | Padrão |
|---|---|
| `MONGO_URI` | `mongodb://localhost:27017` |
| `PG_DSN` | `host=localhost port=5432 dbname=bd_producao_artistica user=etl_user password=etl_pass` |
