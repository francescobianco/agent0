# README.md
# 🤖 Software Auto-Adattivo Containerizzato

Software intelligente che può modificare il proprio codice attraverso interazioni telnet, completamente containerizzato con Docker.

## 🚀 Quick Start

```bash
# 1. Clona e entra nella directory
git clone <repo> && cd <repo>

# 2. Crea il file .env
cp .env.example .env
# Modifica .env con la tua OPENAI_API_KEY

# 3. Avvia il software
make run

# 4. Connettiti al server
make connect
```

## 📁 Struttura del Progetto

```
/agent/
├── src/
│   └── main.py                 # Codice principale
├── state/                      # Stato persistente  
├── backups/                    # Backup automatici
├── Dockerfile                  # Immagine Docker
├── docker-compose.yml          # Orchestrazione
├── Makefile                    # Comandi utili
├── requirements.txt            # Dipendenze Python
└── .env                        # Configurazione
```

## 🔧 Comandi Principali

```bash
make help        # Mostra tutti i comandi
make build       # Costruisce l'immagine
make run         # Avvia il container
make connect     # Connetti via telnet
make logs        # Mostra i logs
make stop        # Ferma il container
make clean       # Pulizia completa
```

## 📞 Connessione

```bash
# Metodo 1: Make command
make connect

# Metodo 2: Telnet diretto  
telnet localhost 2323

# Metodo 3: Netcat
nc localhost 2323
```

## 🎯 Esempi di Utilizzo

Una volta connesso:
```
🤖 memorizza gli ultimi campioni di scacchi
🤖 aggiungi una funzione per calcolare fibonacci
🤖 /info
🤖 /help
```

## 🛠️ Sviluppo

```bash
# Modalità sviluppo (con logs in tempo reale)
make dev

# Ricostruzione completa
make rebuild

# Test rapido
make quick-test
```