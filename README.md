# agent0

`agent0` is an experiment in a self-modifying autonomous agent contained in a single POSIX `sh` file.

The repository copy is dormant. `make start` copies it to `/tmp/agent0.sh` and starts it with `/tmp/agent0.sh &`. The agent creates its own runtime space at `/tmp/agent0.sh.d` when it needs it.

## Usage

```sh
make start
make connect
```

On first startup, if no key is embedded, the agent enters latent startup: it stays alive in the background and asks for the OpenCode Go token through its terminal file in `/tmp/agent0.sh.d/`. The key is saved inside `/tmp/agent0.sh`, so the live agent carries it with itself when it migrates.

The agent uses OpenCode Go directly through the Chat Completions compatible API:

```text
endpoint: https://opencode.ai/zen/go/v1/chat/completions
model:    deepseek-v4-flash
```

It does not use `OPENAI_API_KEY`, `OPENAI_BASE_URL`, or other environment variables. The token is embedded in the live agent copy.

To stop it:

```sh
make stop
```

To validate the dormant copy:

```sh
make check
```

To run the non-interactive prompt smoke tests, create `.env` with your OpenCode Go token:

```sh
OPENCODE_API_KEY=your-token
```

Then run:

```sh
make test
```

The test target starts a dedicated `/tmp/agent0-test.sh` instance, sends the prompts in `tests/prompts/`, and writes captured output under `tests/output/`.

## Terminal

Connection is external to the agent:

```sh
make connect
```

There are no CLI arguments or subcommands for `agent0.sh`: when called, it starts.
