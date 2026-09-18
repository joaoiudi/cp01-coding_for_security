# Check Point 01 — Coding for Security

## Ambiente

Suba os bancos com Docker:

```bash
docker run -d --name mysql-cp01 -e MYSQL_ROOT_PASSWORD=root -p 3306:3306 mysql:8
docker run -d --name mongo-cp01 -p 27017:27017 mongo:7
```

Instale os pacotes:

```bash
pip install pymongo mysql-connector-python scikit-learn numpy
```

Se sua senha do MySQL for diferente de `root`, ajuste o dicionário `CONFIG` no topo
dos arquivos `ex01`, `ex04` e `ex05`.

## Arquivos

| Arquivo | Exercício |
|---|---|
| `ex01_crud_mysql.py` | 1 — Modelagem e CRUD SQL |
| `ex02_crud_pymongo.py` | 2 — CRUD com PyMongo |
| `ex03_agregacao_top_ips.py` | 3 — Agregação: Top IPs |
| `ex04_sql_injection.py` | 4 — Query parametrizada (defesa) |
| `ex05_transacao_rollback.py` | 5 — Transação com rollback |
| `ex06_indice_desempenho.py` | 6 — Índice e desempenho |
| `ex07_classificador_trafego.py` | 7 — RandomForest |
| `ex08_anomalias.py` | 8 — IsolationForest |
| `ex09_metricas.py` | 9 — Métricas honestas |
| `ex10_pipeline_siem.py` | 10 — Mini-pipeline SIEM |
| `auth.log` | Log de 23 linhas usado no exercício 10 |

Cada script roda sozinho: `python3 ex01_crud_mysql.py`

Todos limpam a tabela/coleção antes de inserir, então podem ser executados
várias vezes sem sujar o banco.

## Detalhes que valem ponto

- **Ex. 1**: `ENUM('baixa','media','alta')` na criticidade, `UNIQUE` no IP e o
  `IntegrityError` capturado na inserção duplicada.
- **Ex. 4**: a função insegura existe só para demonstrar o vazamento — rode
  apenas no banco local.
- **Ex. 5**: a tabela usa `ENGINE=InnoDB`; MyISAM ignora transações silenciosamente.
  O débito e o crédito ficam na mesma transação, com `rollback()` no `except`.
- **Ex. 6**: além da contagem, o script imprime o `explain()` mostrando `IXSCAN`
  em vez de `COLLSCAN` — prova visual de que o índice está sendo usado.
- **Ex. 7/8/10**: `random_state=42` em todos os modelos para reprodutibilidade.
- **Ex. 10**: o dataset dos 3 IPs reais é pequeno demais para treinar; o script
  acrescenta pontos de referência rotulados pela mesma regra (≥ 5 falhas = suspeito)
  para o modelo enxergar a fronteira. Isso está comentado no código.

## Saídas conferidas

Os exercícios 7, 8 e 9 foram executados e batem com o enunciado:
acurácia 1.00 e caso novo malicioso; amostras 4 e 7 como anomalia;
matriz `[[8,0],[1,1]]` com acurácia 0.90 / precisão 1.00 / recall 0.50 / F1 0.67.
Os exercícios com banco precisam do Docker no ar para rodar.
