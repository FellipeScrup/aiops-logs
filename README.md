# AIOps Logs - Semana 1 (TCC)

Plataforma inicial de AIOps para ingestao, enriquecimento e diagnostico de logs com arquitetura Medallion (Bronze/Silver/Gold), RAG local e rastreabilidade de experimentos.

## 1. Problema

Times de operacao e desenvolvimento recebem grande volume de logs com baixa padronizacao e alto custo de triagem manual. Isso aumenta MTTR, dificulta priorizacao de incidentes e reduz previsibilidade operacional.

## 2. Objetivos

Objetivo geral:
- Construir uma base reproduzivel para diagnostico assistido de erros em logs usando stack local, com trilha de dados e observabilidade de experimentos.

Objetivos especificos (Semana 1):
- Implementar pipeline Medallion para logs (Bronze, Silver, Gold).
- Disponibilizar API para ingestao e diagnostico (`/ingest` e `/diagnose`).
- Integrar armazenamento de objetos (MinIO), banco relacional (PostgreSQL), vetor (Milvus), LLM local (Ollama) e tracking (MLflow).
- Estruturar ambiente containerizado e automatizacao por `Makefile`.

## 3. Escopo e Nao-Escopo

Escopo atual:
- Ingestao de logs brutos em Bronze (MinIO).
- Normalizacao e persistencia em Silver (PostgreSQL + MinIO Silver).
- Diagnostico assistido em Gold com LLM + contexto vetorial.
- Registro de resultados e metadados no MLflow.
- Interface inicial de uso via Gradio.

Nao-escopo (Semana 1):
- Deploy em nuvem e alta disponibilidade.
- Pipeline de CI/CD completa.
- Catalogo de runbooks amplo e curadoria automatica de base de conhecimento.
- Suite abrangente de testes automatizados e gates de qualidade.

## 4. Arquitetura do Sistema

Visao completa de arquitetura e fluxo em:
- `docs/architecture.md`

Resumo dos componentes:
- `frontend/` (Gradio) consome `api/` (FastAPI).
- `api/` persiste Bronze/Silver no MinIO e PostgreSQL.
- `api/` consulta Milvus para contexto semantico.
- `api/` usa Ollama para embeddings e diagnostico.
- `api/` registra execucoes no MLflow.

## 5. Fluxo Medallion (Bronze -> Silver -> Gold)

Bronze:
- Recebe log bruto e salva JSON original em bucket `logs-bronze`.

Silver:
- Normaliza campos principais (`source`, `level`, `message`, `stacktrace`, `timestamp`).
- Persiste tabela `silver_logs` no PostgreSQL.
- Salva versao limpa no bucket `logs-silver`.

Gold:
- Gera embedding do erro.
- Busca contexto em `docs_logs_context` no Milvus.
- Monta prompt e solicita diagnostico ao Ollama.
- Persiste resultado na tabela `diagnostics` e loga experimento no MLflow.

## 6. Stack Tecnologica e Justificativas

- FastAPI: API assincrona simples e bem documentada via OpenAPI.
- Gradio: interface de prototipacao rapida para validacao funcional.
- PostgreSQL: persistencia estruturada para camada Silver/Gold.
- MinIO: object storage local para dados brutos e intermediarios.
- Milvus: banco vetorial para contexto semantico (RAG).
- Ollama: execucao local de modelos de embeddings e chat.
- MLflow: rastreabilidade de parametros, metricas e artefatos.
- Docker Compose + Makefile: reproducao consistente do ambiente.

## 7. Pre-requisitos

- Docker Engine 24+
- Docker Compose Plugin v2+
- GNU Make 4+
- Python 3.12+ (opcional para scripts de validacao local)

## 8. Configuracao de Ambiente

Copiar variaveis de ambiente:

```bash
cp .env.example .env
```

Variaveis principais:
- Credenciais e portas de PostgreSQL/MinIO/Milvus/Ollama.
- Nomes de buckets (`logs-bronze`, `logs-silver`).
- Nome da collection vetorial (`docs_logs_context`).
- Nome do experimento MLflow.

Arquivo de referencia:
- `.env.example`

## 9. Execucao do Sistema

Subir stack:

```bash
make up
```

Bootstrap completo (build + up + pull modelo + seed):

```bash
make init
```

Logs e status:

```bash
make logs
make ps
```

Derrubar ambiente:

```bash
make down
```

Guia completo de setup:
- `docs/setup.md`

## 10. Seed e Testes de Endpoint

Seed:

```bash
make seed
```

Endpoints principais:
- `GET /health`
- `POST /ingest`
- `POST /diagnose`

Documentacao interativa:
- <http://localhost:8000/docs>

Exemplo de diagnostico rapido via Python:

```bash
python3 - <<'PY'
import json
import urllib.request

payload = {
		"source": "backend",
		"level": "ERROR",
		"message": "ValueError: invalid literal for int()",
		"timestamp": "2026-03-16T18:00:00Z",
}

req = urllib.request.Request(
		"http://localhost:8000/diagnose",
		data=json.dumps(payload).encode(),
		headers={"Content-Type": "application/json"},
)
print(urllib.request.urlopen(req, timeout=120).read().decode())
PY
```

## 11. Test, Lint e Format (estado atual)

Targets disponiveis no `Makefile`:

```bash
make test
make lint
make format
```

Estado atual:
- Ainda nao existe suite de testes automatizados consolidada.
- Ainda nao ha ferramenta de lint/format padronizada no repositorio.
- Os targets respondem com mensagens de orientacao quando configuracoes nao estao presentes.

## 12. Estrutura de Pastas (resumo real)

```text
.
|-- api/
|   |-- app/
|   |   |-- core/
|   |   |-- db/
|   |   |-- routes/
|   |   |-- scripts/
|   |   `-- services/
|   |-- main.py
|   |-- requirements.txt
|   `-- Dockerfile
|-- frontend/
|   |-- app.py
|   |-- requirements.txt
|   `-- Dockerfile
|-- infra/sql/init.sql
|-- docs/
|   |-- architecture.md
|   |-- project-structure.md
|   `-- setup.md
|-- docker-compose.yml
|-- Makefile
`-- .env.example
```

## 13. Troubleshooting

- `docker-compose: command not found`:
	- Use `docker compose` (plugin v2) em vez de `docker-compose`.

- Porta ja em uso (ex.: 9002):
	- Finalize containers antigos/orfaos e execute `make down` seguido de `make up`.

- API reiniciando por dependencia Python:
	- Rebuild da imagem da API: `docker compose build --no-cache api`.

- Milvus sem ficar saudavel:
	- Verifique se `milvus-etcd`, `milvusminio` e `milvus` estao em estado `healthy`.

- Modelo Ollama ausente:
	- Execute `make pull-ollama`.

## 14. Roadmap (Semana 2+)

- Implementar teste automatizado minimo para endpoints e servicos criticos.
- Definir padrao de lint/format (ex.: Ruff + Black) e integrar nos targets.
- Ingerir base inicial de runbooks/documentacao em Milvus para melhorar RAG.
- Adicionar observabilidade de latencia/erros por endpoint.
- Evoluir criterios de avaliacao da qualidade do diagnostico.

## 15. Licenca

Licenca do projeto ainda nao definida formalmente neste repositorio.
Recomendacao para proxima etapa: adotar licenca MIT ou equivalente.
