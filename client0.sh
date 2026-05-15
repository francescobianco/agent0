#!/usr/bin/env bash

IN=/tmp/agent0.sh.d/in
OUT=/tmp/agent0.sh.d/out

if [[ ! -p "$IN" || ! -p "$OUT" ]]; then
    echo "agent0 not running" >&2
    exit 1
fi

exec 3>"$IN"
exec 4<"$OUT"

( while :; do cat <&4; sleep 1; done ) &
trap "kill $! 2>/dev/null; exit" INT TERM EXIT

while IFS= read -r line; do
    printf '%s\n' "$line" >&3
done
