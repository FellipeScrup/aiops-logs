# Arquitetura do Sistema AIOps

Este documento descreve a arquitetura de referencia da Semana 1 do TCC, alinhada ao codigo atual do repositorio.

## Visao de containers e componentes

```mermaid
flowchart LR
    UI[Gradio UI\nfrontend/app.py] -->|POST /diagnose| API[FastAPI\napi/app/routes/logs.py]

    API -->|Bronze write JSON| MINIO[(MinIO\nlogs-bronze/logs-silver)]
    API -->|Silver insert| PG[(PostgreSQL\nsilver_logs/diagnostics)]
    API -->|Context search| MILVUS[(Milvus\nvector collection)]
    API -->|Prompt + context| OLLAMA[Ollama\nLLM + Embeddings]
    API -->|Metrics/params/artifacts| MLFLOW[MLflow Tracking]

    SEED[Seed script\napi/app/scripts/seed.py] --> MINIO
    SEED --> PG
    SEED --> MILVUS
```

## Fluxo Medallion (Bronze -> Silver -> Gold)

```mermaid
sequenceDiagram
    participant Client as Frontend/Client
    participant API as FastAPI
    participant MinIO as MinIO (Bronze/Silver)
    participant PG as PostgreSQL
    participant Milvus as Milvus
    participant LLM as Ollama
    participant Track as MLflow

    Client->>API: POST /diagnose (log bruto)
    API->>MinIO: Salva JSON bruto em logs-bronze
    API->>API: Normaliza campos (source/level/message/stacktrace)
    API->>PG: INSERT silver_logs
    API->>MinIO: Salva JSON limpo em logs-silver
    API->>LLM: Gera embedding do erro
    API->>Milvus: Busca contexto semantico
    API->>LLM: Envia prompt final (log + contexto)
    LLM-->>API: JSON de diagnostico
    API->>PG: INSERT diagnostics
    API->>Track: Log de parametros/metricas/artefatos
    API-->>Client: DiagnoseResponse
```

## Fallback ASCII (caso Mermaid nao renderize)

```text
[Gradio UI] -> [FastAPI]
                |-> [MinIO logs-bronze]
                |-> [PostgreSQL silver_logs]
                |-> [MinIO logs-silver]
                |-> [Ollama embeddings] -> [Milvus context search]
                |-> [Ollama chat diagnosis]
                |-> [PostgreSQL diagnostics]
                |-> [MLflow tracking]
```

## Observacoes tecnicas

- O RAG fica efetivo quando a collection do Milvus estiver populada com documentacao/runbooks.
- A etapa de seed atual cria estrutura base (buckets, tabelas e collection), mas nao injeta conhecimento de dominio automaticamente.
- O endpoint principal para diagnostico e `POST /diagnose`.
