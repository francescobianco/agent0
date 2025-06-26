# Dockerfile
FROM python:3.11-slim

# Metadata
LABEL maintainer="adaptive-software"
LABEL description="Software Auto-Adattivo con Server Telnet"
LABEL version="2.0.0"

# Imposta variabili d'ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV AGENT_PORT=2323
ENV OPENAI_API_KEY=""

# Crea utente non-root per sicurezza
RUN groupadd -r agent && useradd -r -g agent agent

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y \
telnet \
netcat-openbsd \
curl \
vim \
&& rm -rf /var/lib/apt/lists/*

# Installa dipendenze Python
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Crea directory di lavoro
WORKDIR /agent

# Imposta permessi per l'utente agent
RUN chown -R agent:agent /agent

# Cambia all'utente non-root
USER agent

# Esponi la porta per il server telnet
EXPOSE 2323

# Healthcheck per verificare che il server sia attivo
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
CMD nc -z localhost 2323 || exit 1

# Punto di ingresso predefinito
CMD ["python", "src/main.py"]
