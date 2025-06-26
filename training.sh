#!/usr/bin/env sh

SSH_HOST=localhost
SSH_PORT=2222
SSH_USER=root
SSH_PASSWORD=password

echo "aggiungi dei commenti al tuo codice" | sshpass -p "$SSH_PASSWORD" ssh -tt -o StrictHostKeyChecking=no "$SSH_USER@$SSH_HOST" -p "$SSH_PORT"
