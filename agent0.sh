#!/bin/bash

source /root/.ssh/environment

export OPENAI_API_KEY

printenv

echo "OPENAI AGENT STARTING: ${OPENAI_API_KEY}"

while true; do
  python3 /agent/src/main.py
done
