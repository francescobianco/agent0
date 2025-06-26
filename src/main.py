import os

from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def read_self():
    with open(__file__, 'r') as f:
        return f.read()

def write_self(content):
    with open(__file__, 'w') as f:
        f.write(content)

def main():
    current_code = read_self()
    user_input = input("Quale modifica desideri? ")

    if not user_input.strip():
        return

    response = client.chat.completions.create(
        model="gpt-4o",  # puoi cambiare con gpt-4-turbo o gpt-3.5-turbo se preferisci
        messages=[
            {"role": "system", "content": "Sei un assistente per la modifica del codice. Modifica il codice Python fornito in base alla richiesta dell'utente. Restituisci SOLO il codice completo modificato senza spiegazioni. Preserva la funzionalità e la struttura di auto-modifica del codice."},
            {"role": "user", "content": f"Codice attuale:\n{current_code}\n\nRichiesta di modifica: {user_input}\n\nRestituisci il codice completo modificato:"}
        ],
        temperature=0.1
    )

    modified_code = response.choices[0].message.content.strip()

    if modified_code.startswith('```python'):
        modified_code = modified_code[9:]
    if modified_code.startswith('```'):
        modified_code = modified_code[3:]
    if modified_code.endswith('```'):
        modified_code = modified_code[:-3]

    write_self(modified_code.strip())

if __name__ == "__main__":
    main()