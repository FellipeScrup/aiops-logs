.PHONY: help bootstrap init build up down logs ps seed pull-ollama test lint format clean

COMPOSE ?= docker compose

help:
	@echo "Targets disponiveis:"
	@echo "  make bootstrap  # build + up + pull-ollama + seed"
	@echo "  make init       # alias de bootstrap"
	@echo "  make up         # sobe os servicos"
	@echo "  make down       # derruba os servicos"
	@echo "  make logs       # logs em tempo real"
	@echo "  make seed       # cria buckets/tabelas/collection"
	@echo "  make test       # executa testes (quando existirem)"
	@echo "  make lint       # executa lint (quando configurado)"
	@echo "  make format     # formata codigo (quando configurado)"
	@echo "  make clean      # remove cache python local"

bootstrap: build up pull-ollama seed

init: bootstrap

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

# Inicializa schema SQL e buckets MinIO
seed:
	$(COMPOSE) exec -T api python -m app.scripts.seed

# Faz pull dos modelos locais no Ollama (primeira execucao)
pull-ollama:
	$(COMPOSE) exec -T ollama ollama pull llama3.2:3b
	$(COMPOSE) exec -T ollama ollama pull nomic-embed-text

test:
	$(COMPOSE) exec -T api sh -lc "if [ -d tests ]; then pytest -q; else echo 'No automated tests configured yet.'; fi"

lint:
	$(COMPOSE) exec -T api sh -lc "if command -v ruff >/dev/null 2>&1; then ruff check app; else echo 'Lint tool not configured yet (ruff not installed).'; fi"

format:
	$(COMPOSE) exec -T api sh -lc "if command -v ruff >/dev/null 2>&1; then ruff format app; else echo 'Formatter not configured yet (ruff not installed).'; fi"

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete