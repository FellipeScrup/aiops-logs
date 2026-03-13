.PHONY: build up down logs ps seed pull-ollama init

COMPOSE ?= docker compose

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

# Atalho para subir stack e preparar dados iniciais
init: up seed