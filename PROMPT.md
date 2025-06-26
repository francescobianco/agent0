


scrivi il file main.py

che sia un file automoficante sulla base dell'input dell'utente, 
il file viene iterato da questo altro file bash

```sh
while true; do
  python3 /agent/src/main.py
done
```

ad ogni iterazione il file deve presentare un prompt usare il prompt per modificare se stesso usando openai come llm e poi salvare le modifiche e uscire

l'iterazione successiva quindi sara fatto con il file modificato ecc...

mantieni il codice compatto e minimale 
non mettere commenti
non introdurre logiche di comandi speciali
non preoccuparti di come interromere il flusso,
l'unico obbiettivo e scrivere il miglior codice compatto e automodificante possibile
assicurati che il prompt non corrompa il file e non lo deturpi di sue parti, non deve essere persa funzionalita o cambiata la logica di funzionamento
la variabile per la chiave openai è OPENAI_API_KEY
