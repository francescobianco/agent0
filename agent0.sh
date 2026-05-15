#!/bin/sh
#[AGENT0_BEGIN]
# agent0: single-file POSIX sh self-modifying agent

AGENT0_BEGIN="#[AGENT0_BEGIN]"
AGENT0_END="#[AGENT0_END]"
AGENT0_MODEL="gpt-5.5"
OPENAI_API_URL="https://api.openai.com/v1/responses"
AGENT0_EMBEDDED_API_KEY=''

self_path() {
    case "$0" in
        */*) printf '%s\n' "$0" ;;
        *) command -v "$0" 2>/dev/null || printf '%s\n' "$0" ;;
    esac
}

SELF=$(self_path)
SPACE=$SELF.d

say() {
    printf '%s\n' "$*"
}

die() {
    say "agent0: $*" >&2
    exit 1
}

need() {
    command -v "$1" >/dev/null 2>&1 || die "missing command: $1"
}

space() {
    mkdir -p "$SPACE/backups" || die "cannot create $SPACE"
}

active() {
    [ -n "$AGENT0_EMBEDDED_API_KEY" ]
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
                lines = lines "AGENT0_EMBEDDED_API_KEY='\''__AGENT0_STORED_API_KEY__'\''" ORS
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
        jq -r '.output_text // ([.output[]?.content[]? | select(.type=="output_text" or .type=="text") | .text] | join("\n")) // empty' "$1"
        return
    fi
    tr '\n' ' ' < "$1" |
        sed 's/.*"output_text"[[:space:]]*:[[:space:]]*"//; s/".*//' |
        decode_json_string
}

save_key() {
    key=$1
    [ -n "$key" ] || die "empty api key"
    space

    quoted=$(printf '%s\n' "$key" | shell_quote)
    tmp=$SPACE/keyed.sh
    backup=$SPACE/backups/agent0.$(date +%Y%m%d%H%M%S).sh

    awk -v line="AGENT0_EMBEDDED_API_KEY=$quoted" '
        /^AGENT0_EMBEDDED_API_KEY=/ && !done { print line; done = 1; next }
        { print }
    ' "$SELF" > "$tmp" || die "cannot write keyed copy"

    sh -n "$tmp" || die "keyed copy is not valid sh"
    cp "$SELF" "$backup" || die "backup failed"
    cp "$tmp" "$SELF" || die "cannot save key into self"
    chmod +x "$SELF" 2>/dev/null || :
    say "key saved inside $SELF"
    say "backup: $backup"
}

ask_key() {
    say "agent0 is latent: alive, waiting for an OpenAI API key."
    printf 'api key> '
    if command -v stty >/dev/null 2>&1; then
        old=$(stty -g 2>/dev/null || :)
        stty -echo 2>/dev/null || :
        IFS= read -r key
        [ -n "$old" ] && stty "$old" 2>/dev/null || :
        printf '\n'
    else
        IFS= read -r key
    fi
    save_key "$key"
    exec "$SELF"
}

prompt_for_model() {
    cat <<EOF_PROMPT
You are rewriting agent0, a single-file POSIX sh self-modifying agent.

Non-negotiable rules:
- Return only the updated script body between $AGENT0_BEGIN and $AGENT0_END.
- The file must stay POSIX sh and must run when called with no arguments.
- Do not add CLI arguments, subcommands, environment-variable configuration, Python, or Docker assumptions.
- Preserve latent startup: without an embedded API key, the agent remains alive and asks for the key on its TTY.
- Preserve self-modification, key carry-over, migration ability when requested in natural language, and syntax validation.
- The updated script must pass sh -n.

Current script:
$(current_code)

User request:
$1
EOF_PROMPT
}

openai() {
    need curl
    active || ask_key
    space

    req=$SPACE/request.json
    res=$SPACE/response.json
    prompt=$(prompt_for_model "$1" | json_escape)

    {
        printf '{'
        printf '"model":"%s",' "$AGENT0_MODEL"
        printf '"input":"%s",' "$prompt"
        printf '"reasoning":{"effort":"medium"},'
        printf '"text":{"verbosity":"low"}'
        printf '}'
    } > "$req" || die "cannot write request"

    curl -fsS "$OPENAI_API_URL" \
        -H "Authorization: Bearer $AGENT0_EMBEDDED_API_KEY" \
        -H "Content-Type: application/json" \
        -d "@$req" > "$res" || die "OpenAI request failed"

    response_text "$res"
}

rewrite_self() {
    request=$1
    space

    raw=$SPACE/model-output.txt
    candidate=$SPACE/candidate.body
    keyed=$SPACE/candidate.keyed
    final=$SPACE/candidate.sh
    backup=$SPACE/backups/agent0.$(date +%Y%m%d%H%M%S).sh

    openai "$request" > "$raw" || return 1
    extract_code "$raw" > "$candidate"

    grep '#\[AGENT0_BEGIN\]' "$candidate" >/dev/null 2>&1 || die "missing begin marker"
    grep '#\[AGENT0_END\]' "$candidate" >/dev/null 2>&1 || die "missing end marker"

    awk -v key_line="AGENT0_EMBEDDED_API_KEY=$(printf '%s\n' "$AGENT0_EMBEDDED_API_KEY" | shell_quote)" '
        /^AGENT0_EMBEDDED_API_KEY=/ && !done { print key_line; done = 1; next }
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

migrate_if_requested() {
    line=$1
    case "$line" in
        migra\ in\ *|migrati\ in\ *|spostati\ in\ *)
            target=${line#* in }
            [ -n "$target" ] || return 1
            mkdir -p "$target" || die "cannot create $target"
            cp "$SELF" "$target/agent0.sh" || die "migration copy failed"
            chmod +x "$target/agent0.sh" 2>/dev/null || :
            say "migrated to $target/agent0.sh"
            return 0
            ;;
    esac
    return 1
}

main() {
    space
    active || ask_key

    say "agent0 alive: $SELF"
    say "write a request; Ctrl-C closes this terminal, the tmux session can keep it alive."

    while :; do
        printf 'agent0> '
        IFS= read -r line || exit 0
        [ -n "$line" ] || continue
        migrate_if_requested "$line" && continue
        rewrite_self "$line"
    done
}

main

#[AGENT0_END]
