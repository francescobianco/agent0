


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
ricordati di usare la versione della sdk openai >= 1.0
implementa un meccanismo nel prompt di verifica che il codice modificato sia ancora definibile un file automodificabile
la nostra definizione di file automodificabile è che il file deve essere in grado di modificare se stesso senza perdere funzionalità o logica di funzionamento
all'interno del tuo codice ci sono due commenti speciali `#[BEGIN]` e `#[END]` che delimitano il tuo codice e devono essere usati per estrarre il codice modificato dal LLM, quindi non usare tecniche di estrazione basare su espressioni arbitrarie estrai il codice usando questi due delimitatori
e rimettili sempre nel codice modificato in modo che ogni iterazione ce li abbiamo per definizione
ricorda che il tuo codice va dal primo dei `#[BEGIN]` all'ultimo dei `#[END]` in fatti nel mezzo del tuo codice ci posso essere altri `#[BEGIN]` e `#[END]` che determinano la logica di interpretazione stessa, quindi per salvaguarda tu estrai il codice dal llm tra il primo `#[BEGIN]` e l'ultimo `#[END]`

```python