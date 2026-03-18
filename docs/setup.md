# Setup Reproduzivel (Ambiente do Zero)

Este guia descreve o bootstrap completo em Linux/macOS para um novo desenvolvedor.

## 1) Pre-requisitos

- Docker Engine 24+
- Docker Compose Plugin v2+
- GNU Make 4+
- Python 3.12+ (opcional para chamadas locais e validacoes)

Observacao Windows:
- Preferencialmente usar WSL2 + Docker Desktop.
- Comandos de Make devem ser executados dentro do shell Linux (WSL2).

## 2) Clonar e configurar variaveis

```bash
git clone https://github.com/FellipeScrup/aiops-logs.git
cd aiops-logs
cp .env.example .env
```

## 3) Bootstrap em um comando

```bash
make init
```

O target `init` executa:
1. `make build`
2. `make up`
3. `make pull-ollama`
4. `make seed`

## 4) Subida e operacao diaria

```bash
make up
make logs
make ps
```

## 5) Validar servicos

- FastAPI docs: <http://localhost:8000/docs>
- Gradio UI: <http://localhost:7860>
- MinIO console: <http://localhost:9001>
- MLflow UI: <http://localhost:5000>
- Milvus health endpoint: <http://localhost:9091/healthz>

Healthcheck rapido da API:

```bash
python3 -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health', timeout=5).read().decode())"
```

## 6) Diagnostico de exemplo

```bash
python3 - <<'PY'
import json
import urllib.request

payload = {
    "source": "backend",
    "level": "ERROR",
    "message": "MemoryError: Process killed: Out of memory",
    "timestamp": "2026-03-16T17:20:00Z",
}

data = json.dumps(payload).encode()
req = urllib.request.Request(
    "http://localhost:8000/diagnose",
    data=data,
    headers={"Content-Type": "application/json"},
)
resp = urllib.request.urlopen(req, timeout=120)
print(resp.read().decode())
PY
```

## 7) Dados seed

```bash
make seed
```

Resultado esperado:
- Buckets `logs-bronze`, `logs-silver`, `mlflow`
- Tabelas `silver_logs`, `diagnostics`
- Collection do Milvus `docs_logs_context`

## 8) Testes, lint e format

```bash
make test
make lint
make format
```

Observacao:
- Na base atual do repositorio, testes/lint ainda nao estao completamente configurados.
- Os targets retornam mensagem informativa quando nao ha ferramenta instalada.

## 9) Encerrar ambiente

```bash
make down
```

## 10) Limpeza de cache local

```bash
make clean
```
