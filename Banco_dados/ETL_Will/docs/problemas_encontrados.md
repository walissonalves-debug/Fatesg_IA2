# Problemas Encontrados na Base de Dados

## pessoa.jsonl
| Problema | Quantidade | Decisão |
|---|---|---|
| IDs duplicados (`id_pessoa`) | 4 | Mantém a primeira ocorrência, descarta as demais |
| Nomes vazios ou nulos | 0 | N/A |

## producao.jsonl
| Problema | Quantidade | Decisão |
|---|---|---|
| Anos inválidos (valor `"0"` ou fora de 1800–2030) | ~177.750 | Campo `ano` armazenado como `null` |
| Título vazio ou nulo | 1 | Registro descartado |
| IDs duplicados | 0 | N/A |
| Campo `ano` como string em vez de int | Todos | Convertido para `int` no clean |

## equipe.jsonl (a preencher após download)
| Problema esperado | Decisão |
|---|---|
| Papéis nulos ou em branco | Descartados |
| IDs de pessoa sem correspondência em `pessoa_clean` | Descartados |
| IDs de produção sem correspondência em `producao_clean` | Descartados |
| Capitalização inconsistente de papéis | Padronizado com `.title()` |

## Decisões gerais
- **Não foram descartados registros** com `ano = null`; eles são mantidos pois o título ainda tem valor analítico.
- O campo `tipo_nome` foi adicionado na limpeza para evitar lookups frequentes na aplicação.
- A coleção `producoes_com_participantes` foi criada para demonstrar a vantagem do modelo documental (dados aninhados, sem JOIN).
