# Makefile
.PHONY: help build run stop logs shell test clean connect dev

# Variabili
COMPOSE_FILE := docker-compose.yml
SERVICE_NAME := adaptive-agent
CONTAINER_NAME := adaptive-software
PORT := 2323

# Colori per output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Mostra questo help
@echo "$(BLUE)🤖 Software Auto-Adattivo - Comandi Docker$(NC)"
@echo ""
@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Costruisce l'immagine Docker
@echo "$(YELLOW)🔨 Costruendo l'immagine Docker...$(NC)"
docker-compose build

run: ## Avvia il container
@echo "$(GREEN)🚀 Avviando il software auto-adattivo...$(NC)"
docker-compose up -d
@echo "$(GREEN)✅ Container avviato! Connettiti con: make connect$(NC)"

dev: ## Avvia in modalità sviluppo (con logs)
@echo "$(YELLOW)🛠️  Modalità sviluppo attivata...$(NC)"
docker-compose up

stop: ## Ferma il container
@echo "$(RED)🛑 Fermando il container...$(NC)"
docker-compose down

restart: stop run ## Riavvia il container

logs: ## Mostra i logs
@echo "$(BLUE)📋 Logs del container:$(NC)"
docker-compose logs -f $(SERVICE_NAME)

shell: ## Apre una shell nel container
@echo "$(BLUE)🐚 Aprendo shell nel container...$(NC)"
docker exec -it $(CONTAINER_NAME) /bin/bash

connect: ## Connetti al server telnet
@echo "$(GREEN)📞 Connessione al server telnet...$(NC)"
@echo "$(YELLOW)Per disconnetterti: Ctrl+] poi 'quit'$(NC)"
@telnet localhost $(PORT) || (echo "$(RED)❌ Errore connessione. Il container è avviato?$(NC)" && make status)

nc-connect: ## Connetti via netcat
@echo "$(GREEN)📞 Connessione via netcat...$(NC)"
@nc localhost $(PORT) || (echo "$(RED)❌ Errore connessione netcat$(NC)" && make status)

status: ## Mostra lo stato dei container
@echo "$(BLUE)📊 Stato dei container:$(NC)"
@docker-compose ps

test: ## Testa la connessione
@echo "$(YELLOW)🧪 Testando la connessione...$(NC)"
@timeout 5 bash -c "</dev/tcp/localhost/$(PORT)" && echo "$(GREEN)✅ Server raggiungibile$(NC)" || echo "$(RED)❌ Server non raggiungibile$(NC)"

clean: ## Rimuove container, immagini e volumi
@echo "$(RED)🧹 Pulizia completa...$(NC)"
docker-compose down -v --rmi all --remove-orphans
docker system prune -f

backup: ## Crea backup dello stato
@echo "$(BLUE)💾 Creando backup...$(NC)"
@mkdir -p backups
@docker cp $(CONTAINER_NAME):/agent/adaptive_state.pkl backups/state_$(shell date +%Y%m%d_%H%M%S).pkl 2>/dev/null || echo "$(YELLOW)⚠️  Nessuno stato da salvare$(NC)"
@docker cp $(CONTAINER_NAME):/agent/src/ backups/src_$(shell date +%Y%m%d_%H%M%S)/ 2>/dev/null || echo "$(YELLOW)⚠️  Errore backup src$(NC)"

restore: ## Ripristina backup (specificare con BACKUP_FILE=file.pkl)
@if [ -z "$(BACKUP_FILE)" ]; then \
echo "$(RED)❌ Specifica il file: make restore BACKUP_FILE=state_xxx.pkl$(NC)"; \
else \
echo "$(BLUE)📥 Ripristinando backup $(BACKUP_FILE)...$(NC)"; \
docker cp backups/$(BACKUP_FILE) $(CONTAINER_NAME):/agent/adaptive_state.pkl; \
fi

monitor: ## Avvia il monitoraggio
@echo "$(BLUE)👁️  Avviando monitoraggio...$(NC)"
docker-compose --profile monitoring up agent-monitor

update-deps: ## Aggiorna le dipendenze Python
@echo "$(YELLOW)📦 Aggiornando dipendenze...$(NC)"
docker exec $(CONTAINER_NAME) pip install --upgrade -r requirements.txt

info: ## Mostra informazioni sul setup
@echo "$(BLUE)ℹ️  Informazioni Setup:$(NC)"
@echo "  🐳 Container: $(CONTAINER_NAME)"
@echo "  🌐 Porta: $(PORT)"
@echo "  📁 Volume: $(shell pwd):/agent"
@echo "  🔑 API Key: $(if $(OPENAI_API_KEY),configurata,non configurata)"
@echo ""
@echo "$(GREEN)📞 Comandi di connessione:$(NC)"
@echo "  telnet localhost $(PORT)"
@echo "  nc localhost $(PORT)"
@echo "  make connect"

# Target per sviluppatori
rebuild: clean build ## Ricostruisce tutto da zero

quick-test: build run test ## Test rapido completo

# Esempio di utilizzo con API key
run-with-key: ## Avvia con API key (OPENAI_API_KEY=xxx make run-with-key)
@if [ -z "$(OPENAI_API_KEY)" ]; then \
echo "$(RED)❌ Specifica OPENAI_API_KEY=your-key make run-with-key$(NC)"; \
else \
echo "$(GREEN)🔑 Avviando con API key configurata...$(NC)"; \
OPENAI_API_KEY=$(OPENAI_API_KEY) docker-compose up -d; \
fi