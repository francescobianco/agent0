#!/bin/bash

source /root/.ssh/environment

export OPENAI_API_KEY

cd /agent || exit 1

while true; do
  python3 /agent/src/main.py
done
