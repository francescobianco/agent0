# agent0

`agent0` e' un esperimento di agente automodificante in un singolo file `sh` POSIX.

La copia nella repo e' ibernata. `make start` la copia in `/tmp/agent0.sh` e la avvia in background. Da Make usa `nohup /tmp/agent0.sh &` per non far morire il processo quando termina la shell del target; l'agente resta comunque un normale script lanciato in background.

## Uso

```sh
make start
make connect
```

Alla prima partenza, se non ha una chiave incorporata, entra in avvio latente: resta vivo in background e chiede la API key attraverso il terminale FIFO in `/tmp/agent0.sh.d/`. La chiave viene salvata dentro `/tmp/agent0.sh`, quindi l'agente vivo se la porta dietro quando migra.

Per fermarlo:

```sh
make stop
```

Per validare la copia ibernata:

```sh
make check
```

## Terminale

La connessione e' esterna all'agente:

```sh
make connect
```

Non ci sono argomenti o sottocomandi CLI per `agent0.sh`: quando viene chiamato parte e basta.
