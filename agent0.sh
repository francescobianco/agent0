#!/bin/sh
#[AGENT0_BEGIN]
# agent0: single-file POSIX sh self-modifying agent (FIFO IPC)

AGENT0_BEGIN="#[AGENT0_BEGIN]"
AGENT0_END="#[AGENT0_END]"
AGENT0_MODEL="deepseek-v4-flash"
OPENCODE_API_URL="https://opencode.ai/zen/go/v1/chat/completions"
AGENT0_EMBEDDED_OPENCODE_KEY=''

self_path() {
    case "$0" in
        */*) printf '%s\n' "$0" ;;
        *) command -v "$0" 2>/dev/null || printf '%s\n' "$0" ;;
    esac
}

SELF=$(self_path)
SPACE=$SELF.d
IN_FIFO=$SPACE/in
OUT_FIFO=$SPACE/out
PIDFILE=$SPACE/pid

need() { command -v "$1" >/dev/null 2>&1 || die "missing command: $1"; }
say() { printf '%s\n' "$*"; }
die() { say "agent0: $*" >&2; exit 1; }

setup() {
    mkdir -p "$SPACE/backups" || die "cannot create $SPACE"
    [ -p "$IN_FIFO" ] || mkfifo "$IN_FIFO" || die "cannot create $IN_FIFO"
    [ -p "$OUT_FIFO" ] || mkfifo "$OUT_FIFO" || die "cannot create $OUT_FIFO"
    printf '%s\n' "$$" > "$PIDFILE" || die "cannot write $PIDFILE"
}

active() { [ -n "$AGENT0_EMBEDDED_OPENCODE_KEY" ]; }

read_line() {
    IFS= read -r AGENT0_LINE <&3 || exit 0
}

json_escape() {
    sed 's/\\/\\\\/g; s/"/\\"/g; s/	/\\t/g; s/$/\\n/' | tr -d '\n'
}

shell_quote() {
    awk '
        BEGIN { q = sprintf("%c", 39) }
        {
            gsub(q, q "\\" q q)
            printf "%s%s%s", q, $0, q
        }
    '
}

current_code() {
    awk '
        index($0, "#[AGENT0_BEGIN]") { seen = 1 }
        seen {
            if ($0 ~ /^AGENT0_EMBEDDED_API_KEY=/) {
                lines = lines "AGENT0_EMBEDDED_OPENCODE_KEY='\''__AGENT0_STORED_OPENCODE_KEY__'\''" ORS
            } else if ($0 ~ /^AGENT0_EMBEDDED_OPENCODE_KEY=/) {
                lines = lines "AGENT0_EMBEDDED_OPENCODE_KEY='\''__AGENT0_STORED_OPENCODE_KEY__'\''" ORS
            } else {
                lines = lines $0 ORS
            }
        }
        index($0, "#[AGENT0_END]") { end = length(lines) }
        END { if (end) printf "%s", substr(lines, 1, end) }
    ' "$SELF"
}

extract_code() {
    awk '
        index($0, "#[AGENT0_BEGIN]") { seen = 1 }
        seen { lines = lines $0 ORS }
        index($0, "#[AGENT0_END]") { end = length(lines) }
        END { if (end) printf "%s", substr(lines, 1, end) }
    ' "$1"
}

decode_json_string() {
    sed 's/\\"/"/g; s/\\\\/\\/g; s/\\n/\
/g; s/\\t/	/g'
}

response_text() {
    if command -v jq >/dev/null 2>&1; then
        jq -r '.choices[0].message.content // empty' "$1"
        return
    fi
    tr '\n' ' ' < "$1" |
        sed 's/.*"content"[[:space:]]*:[[:space:]]*"//; s/".*//' |
        decode_json_string
}

save_key() {
    key=$1
    [ -n "$key" ] || die "empty OpenCode Go key"

    quoted=$(printf '%s\n' "$key" | shell_quote)
    tmp=$SPACE/keyed.sh
    backup=$SPACE/backups/agent0.$(date +%Y%m%d%H%M%S).sh

    awk -v line="AGENT0_EMBEDDED_OPENCODE_KEY=$quoted" '
        /^AGENT0_EMBEDDED_OPENCODE_KEY=/ && !done { print line; done = 1; next }
        { print }
    ' "$SELF" > "$tmp" || die "cannot write keyed copy"

    sh -n "$tmp" || die "keyed copy is not valid sh"
    cp "$SELF" "$backup" || die "backup failed"
    cp "$tmp" "$SELF" || die "cannot save key into self"
    chmod +x "$SELF" 2>/dev/null || :
    say "OpenCode Go key saved inside $SELF"
    say "backup: $backup"
}

ask_key() {
    say "agent0 is latent: alive, waiting for an OpenCode Go API key."
    say 'opencode key> '
    read_line || exit 0
    save_key "$AGENT0_LINE"
    exec "$SELF"
}

prompt_for_model() {
    cat <<EOF_PROMPT
You are rewriting agent0, a single-file POSIX sh self-modifying agent.

Non-negotiable rules:
- Return only the updated script body between $AGENT0_BEGIN and $AGENT0_END.
- The file must stay POSIX sh and must run when called with no arguments.
- Do not add CLI arguments, subcommands, environment-variable configuration, Python, or Docker assumptions.
- Preserve latent startup: without an embedded OpenCode Go key, the agent remains alive in background and asks for the key through its terminal file.
- Preserve self-modification, key carry-over, migration ability when requested in natural language, and syntax validation.
- The updated script must pass sh -n.

Current script:
$(current_code)

User request:
$1
EOF_PROMPT
}

opencode() {
    need curl
    active || ask_key

    req=$SPACE/request.json
    res=$SPACE/response.json
    curl_cfg=$SPACE/curl.conf
    prompt=$(prompt_for_model "$1" | json_escape)

    {
        printf '{'
        printf '"model":"%s",' "$AGENT0_MODEL"
        printf '"messages":[{"role":"user","content":"%s"}],' "$prompt"
        printf '"temperature":0.2'
        printf '}'
    } > "$req" || die "cannot write request"

    {
        printf '%s\n' "url = \"$OPENCODE_API_URL\""
        printf '%s\n' "header = \"Authorization: Bearer $AGENT0_EMBEDDED_OPENCODE_KEY\""
        printf '%s\n' "header = \"Content-Type: application/json\""
        printf '%s\n' "data = @$req"
        printf '%s\n' "max-time = 180"
        printf '%s\n' "fail"
        printf '%s\n' "show-error"
        printf '%s\n' "silent"
    } > "$curl_cfg" || die "cannot write curl config"

    curl -K "$curl_cfg" > "$res" || die "OpenCode Go request failed"

    response_text "$res"
}

rewrite_self() {
    request=$1

    raw=$SPACE/model-output.txt
    candidate=$SPACE/candidate.body
    keyed=$SPACE/candidate.keyed
    final=$SPACE/candidate.sh
    backup=$SPACE/backups/agent0.$(date +%Y%m%d%H%M%S).sh

    opencode "$request" > "$raw" || return 1
    extract_code "$raw" > "$candidate"

    if ! grep '#\[AGENT0_BEGIN\]' "$candidate" >/dev/null 2>&1; then
        cat "$raw"
        return 0
    fi

    grep '#\[AGENT0_END\]' "$candidate" >/dev/null 2>&1 || {
        cat "$raw"
        return 0
    }

    awk -v key_line="AGENT0_EMBEDDED_OPENCODE_KEY=$(printf '%s\n' "$AGENT0_EMBEDDED_OPENCODE_KEY" | shell_quote)" '
        /^AGENT0_EMBEDDED_OPENCODE_KEY=/ && !done { print key_line; done = 1; next }
        { print }
    ' "$candidate" > "$keyed" || die "cannot preserve key"

    {
        printf '%s\n' '#!/bin/sh'
        cat "$keyed"
    } > "$final" || die "cannot write candidate"

    sh -n "$final" || die "candidate is not valid sh"
    cp "$SELF" "$backup" || die "backup failed"
    cp "$final" "$SELF" || die "rewrite failed"
    chmod +x "$SELF" 2>/dev/null || :
    say "rewritten: $SELF"
    say "backup: $backup"
    exec "$SELF"
}

main() {
    setup
    exec 3<>"$IN_FIFO" 2>/dev/null
    exec 4<>"$OUT_FIFO" 2>/dev/null
    exec >&4 2>&1
    active || ask_key

    say "agent0 alive: $SELF"
    say "write a message; the agent stays alive in background."

    while :; do
        say 'agent0> '
        read_line || exit 0
        line=$AGENT0_LINE
        [ -n "$line" ] || continue
        say '...'
        rewrite_self "$line"
    done
}

main

#[AGENT0_END]
