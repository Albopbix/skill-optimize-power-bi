# Decision Intelligence no Google Cloud

Adaptação do projeto [jashwanth-sariputi/AI-Driven-Decision-Intelligence](https://github.com/jashwanth-sariputi/AI-Driven-Decision-Intelligence)
(commit `20845fc`) para rodar no GCP. O README original continua em [`README.md`](README.md).

## Arquitetura

```
Usuário ──► Cloud Run (Streamlit, container)
               │  ├─ Cloud SQL PostgreSQL ── usuários, histórico de uploads/modelos/predições
               │  ├─ Cloud Storage ───────── modelos .pkl treinados no AutoML (saved_models/)
               │  ├─ Secret Manager ──────── senha do banco (DB_PASS)
               │  └─ Vertex AI (Gemini) ───── respostas do AI Business Copilot e do AI Chat
               └─ Artifact Registry / Cloud Build ── imagem e CI/CD
Dados Olist ──► Cloud Storage (gs://…/data) ──► BigQuery (opcional)
```

## O que mudou em relação ao original

| Arquivo | Mudança |
|---|---|
| `src/database/database.py` | Dois backends: SQLite (local, padrão) e PostgreSQL/Cloud SQL (quando `DATABASE_URL` ou `INSTANCE_CONNECTION_NAME` está definido). Mesma API pública; conexão compartilhada por processo. |
| `src/storage/model_store.py` | Novo. Lista, envia e baixa modelos `.pkl` do GCS quando `GCS_BUCKET` está definido; senão, usa a pasta `saved_models/`. |
| `src/model_export/model_exporter.py` | Depois de salvar o `.pkl`, envia ao bucket. |
| `app/pages/7_Prediction.py` | Lista e carrega modelos via `model_store` (funciona com GCS). |
| `src/llm/gemini_client.py` | Novo. Cliente Gemini (SDK `google-genai`, modo Vertex AI) que monta um perfil compacto do dataset e responde em linguagem natural. |
| `src/business_copilot/copilot_engine.py`, `src/ai_chat/chat_engine.py` | `ask()` usa o Gemini quando `GEMINI_ENABLED=true`; se a chamada falhar, cai para o motor de regras original (`ask_rules()`). O AI Chat envia o histórico da conversa. |
| `app/`, `src/` (textos) | Interface traduzida para português (páginas, login, menus, mensagens, PDF do relatório executivo). Os motores de regras do Copiloto e do Chat também entendem perguntas em português. |
| `app/pages/13_Model_History.py` | Corrigida uma f-string que só compilava no Python 3.12+ (a imagem usa 3.11). |
| `Dockerfile`, `.dockerignore`, `.streamlit/config.toml` | Container para o Cloud Run (porta `$PORT`, usuário sem root). |
| `deploy/*.sh`, `cloudbuild.yaml` | Provisionamento, deploy e CI/CD. |
| `data/` | CSVs **não** versionados (≈450 MB, acima do limite do GitHub). Ver “Dados”. |

Sem nenhuma variável de ambiente, o app roda exatamente como antes (SQLite e disco local).

## Rodar localmente

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/app.py
```

Para testar contra o Cloud SQL a partir da sua máquina, use o
[Cloud SQL Auth Proxy](https://cloud.google.com/sql/docs/postgres/connect-auth-proxy)
e `DATABASE_URL=postgresql://app_user:SENHA@127.0.0.1:5432/business_ai` (veja `.env.example`).

## Deploy no GCP

Pré-requisitos: `gcloud` autenticado, projeto com faturamento ativo.

```bash
cd gcp-decision-intelligence
gcloud config set project SEU_PROJETO
export REGION=southamerica-east1          # opcional (padrão: São Paulo)

./deploy/setup_gcp.sh   # APIs, Artifact Registry, bucket, Cloud SQL, secret, service account
./deploy/deploy.sh      # Cloud Build + Cloud Run; imprime a URL no final
```

Todos os nomes (serviço, instância, bucket, região, tier) podem ser sobrescritos
por variáveis de ambiente — veja `deploy/config.sh`.

### CI/CD com Cloud Build

Crie um gatilho no Cloud Build ligado a este repositório com
*Build config* = `gcp-decision-intelligence/cloudbuild.yaml` e diretório
`gcp-decision-intelligence`. Dê à service account do Cloud Build os papéis
`roles/run.admin` e `roles/iam.serviceAccountUser` sobre `decision-intel-run`.

## Copiloto com Gemini (Vertex AI)

O **AI Business Copilot** e o **AI Chat** respondem com o Gemini quando
`GEMINI_ENABLED=true` (padrão no deploy). O `setup_gcp.sh` habilita a API
`aiplatform.googleapis.com` e dá `roles/aiplatform.user` à service account do Cloud Run.
Se a chamada falhar (permissão, cota, rede), a tela mostra a resposta do motor de regras
original e um aviso.

| Variável | Padrão | Uso |
|---|---|---|
| `GEMINI_ENABLED` | `false` no código, `true` no deploy | Liga o Gemini |
| `GEMINI_MODEL` | `gemini-3.5-flash` | Troque por `gemini-3.1-flash-lite` (mais barato) ou um modelo Pro |
| `GOOGLE_CLOUD_LOCATION` | `global` | Endpoint do Vertex AI |
| `GEMINI_SAMPLE_ROWS` | `5` | Linhas de amostra enviadas; `0` envia só esquema e estatísticas |
| `GEMINI_LANGUAGE` | idioma da pergunta | Ex.: `Brazilian Portuguese` para forçar PT-BR |

**O que é enviado ao modelo:** nomes e tipos das colunas, nulos, valores únicos,
estatísticas (média, mín., máx., mediana), categorias mais frequentes, as 5 correlações
mais fortes e, por padrão, as 5 primeiras linhas. O dataset completo **nunca** é enviado,
então perguntas que exigem varrer todos os dados (ex.: “qual cliente comprou mais?”)
recebem uma resposta dizendo que isso depende de uma análise do app. Se o dataset tiver
dados pessoais, use `GEMINI_SAMPLE_ROWS=0`.

Teste local: `gcloud auth application-default login` e defina as variáveis do `.env.example`.

## Dados

Os CSVs do dataset Olist ficam fora do Git. Baixe-os do repositório original
(pastas `data/raw` e `data/processed`) ou do Kaggle (*Brazilian E-Commerce Public
Dataset by Olist*) e depois:

```bash
./deploy/upload_data.sh              # copia para gs://<bucket>/data/
LOAD_BQ=1 ./deploy/upload_data.sh    # também carrega no BigQuery (dataset decision_intelligence)
```

Com os dados no BigQuery, dá para conectar o Power BI direto (conector Google BigQuery).

## Pontos de atenção

- **Sessão em memória:** dataset enviado e modelo treinado ficam no `st.session_state`
  da instância. O deploy usa `--session-affinity`; mesmo assim, se a instância for
  reciclada, o usuário precisa reenviar o dataset. Modelos exportados e históricos
  ficam salvos (GCS / Cloud SQL).
- **Acesso público:** o deploy usa `--allow-unauthenticated` e o login do próprio app.
  Para uso interno, troque por `--no-allow-unauthenticated` + IAP.
- **Custo:** Cloud SQL `db-f1-micro` fica ligado 24h (é o principal custo fixo).
  O Gemini é cobrado por token; cada pergunta envia o perfil do dataset (alguns milhares de tokens).
  O Cloud Run escala a zero (`--min-instances 0`).
- **Licença:** o repositório original não tem arquivo de licença. Confirme com o autor
  antes de uso comercial ou publicação.
