#!/usr/bin/env sh

mkdir -p /root/.ssh
echo "OPENAI_API_KEY=$OPENAI_API_KEY" > /root/.ssh/environment
chmod 600 /root/.ssh/environment

exec "$@"
