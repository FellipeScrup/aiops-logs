# Estrutura recomendada (escalavel)

```text
aiops-logs/
  api/
    app/
      core/
        config.py
        core.py
        schemas.py
      db/
        postgres.py
      routes/
        logs.py
      scripts/
        seed.py
      services/
        diagnosis_service.py
        milvus_service.py
        minio_service.py
        mlflow_service.py
        ollama_service.py
        silver_service.py
      main.py
    Dockerfile
    requirements.txt
    main.py
  frontend/
    app.py
    Dockerfile
    requirements.txt
  infra/
    sql/
      init.sql
  docs/
    project-structure.md
  data/
    samples/
  docker-compose.yml
  Makefile
```

## Camadas Medallion

- Bronze: logs brutos em JSON no bucket `logs-bronze` no MinIO.
- Silver: logs normalizados no PostgreSQL e copia estruturada no bucket `logs-silver`.
- Gold: diagnostico gerado via RAG (Milvus + Ollama), persistido em `diagnostics` e rastreado no MLflow.
