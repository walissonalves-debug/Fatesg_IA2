# Decisões Técnicas

## Modelo de armazenamento

Optamos por manter **duas camadas** no MongoDB:

1. **Coleções separadas limpas** (`pessoa_clean`, `producao_clean`, `equipe_clean`): úteis para consultas flexíveis e atualizações pontuais.
2. **Coleção documental** (`producoes_com_participantes`): documento rico com participantes aninhados, ideal para leitura de uma produção completa com uma só query.

## Por que `tipo_nome` foi desnormalizado?

No MongoDB não há JOIN nativo. Para evitar múltiplas consultas ao buscar o nome do tipo, o campo `tipo_nome` foi adicionado diretamente ao documento de produção durante o `clean.py`. Essa é uma prática comum no design de documentos NoSQL.

## Batch size

Usamos batches de 5.000 documentos para a ingestão e de 2.000 para a coleção documental. Isso equilibra uso de memória e velocidade de escrita.

## Índices criados

| Coleção | Índice |
|---|---|
| `pessoa_clean` | `id_pessoa` (único) |
| `producao_clean` | `id_producao` (único), `ano`, `tipo_id` |
| `equipe_clean` | `(id_producao, id_pessoa)` composto, `papel` |
| `producoes_com_participantes` | `id_producao` (único), `ano`, `tipo_id`, `total_participantes`, `participantes.papel` |

---

# Comparação MongoDB vs PostgreSQL

## Armazenamento

| Critério | MongoDB | PostgreSQL |
|---|---|---|
| Schema | Flexível (schemaless) | Rígido (DDL obrigatório) |
| Dados aninhados | Nativo (arrays, subdocumentos) | Não nativo (JSON/JSONB como workaround) |
| Setup inicial | Rápido | Requer DDL e migrações |

## Consultas

| Consulta | MongoDB | PostgreSQL |
|---|---|---|
| Buscar produção com participantes | 1 query (dados aninhados) | JOIN entre 3 tabelas |
| Filtro simples por campo | `.find({campo: valor})` | `SELECT ... WHERE` |
| Agregações | `$group`, `$unwind` | `GROUP BY`, `JOIN` |
| Ranking | `$sort` + `$limit` | `ORDER BY ... LIMIT` |

## O que foi mais fácil no MongoDB

- Inserção sem schema: não precisou criar DDL antes.
- Dados aninhados: a coleção `producoes_com_participantes` retorna tudo de uma vez.
- Iteração rápida: mudar a estrutura do documento não requer `ALTER TABLE`.

## O que foi mais fácil no PostgreSQL

- Consultas com múltiplos JOINs são mais legíveis em SQL.
- Integridade referencial nativa com FOREIGN KEY.
- Ferramentas de visualização mais maduras (pgAdmin, DBeaver).
- Transações ACID são mais simples de garantir.
