#[BEGIN]
import os
import openai

def get_current_code():
    with open(__file__, 'r') as f:
        content = f.read()
    first_begin = content.find('#[BEGIN]')
    last_end = content.rfind('#[END]')
    return content[first_begin:last_end + 6]

def modify_code(current_code, user_input):
    client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])

    prompt = f"""Stai modificando un file Python che si modifica da solo. Il file deve mantenere la sua funzionalità principale:
1. Deve leggere l'input dell'utente
2. Deve utilizzare OpenAI per modificare se stesso in base a tale input
3. Deve salvare la versione modificata e uscire
4. Deve preservare i delimitatori #[BEGIN] e #[END]
5. Il codice modificato deve ancora essere un file che si modifica da solo con la stessa logica

Codice attuale:
{current_code}

Richiesta dell'utente: {user_input}

Rispondi SOLO con il codice modificato tra i tag #[BEGIN] e #[END]. Il codice deve rimanere auto-modificante e funzionale."""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content

def extract_code(llm_response):
    first_begin = llm_response.find('#[BEGIN]')
    last_end = llm_response.rfind('#[END]')
    if first_begin != -1 and last_end != -1:
        return llm_response[first_begin:last_end + 6]
    return llm_response

def save_code(new_code):
    with open(__file__, 'w') as f:
        f.write(new_code)

if __name__ == "__main__":
    user_input = input("Inserisci la richiesta di modifica: ")
    current_code = get_current_code()
    modified_response = modify_code(current_code, user_input)
    new_code = extract_code(modified_response)
    save_code(new_code)
#[END]