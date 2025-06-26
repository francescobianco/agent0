#[BEGIN]
import os
import openai

# Esta función obtiene el código actual del archivo
def get_current_code():
    with open(__file__, 'r') as f:  # Abrimos el archivo en modo lectura
        content = f.read()  # Leemos el contenido
    first_begin = content.find('#[BEGIN]')  # Buscamos el primer delimitador
    last_end = content.rfind('#[END]')  # Buscamos el último delimitador
    return content[first_begin:last_end + 6]  # Devolvemos el contenido entre los delimitadores

# Esta función modifica el código actual basándose en la entrada del usuario
def modify_code(current_code, user_input):
    client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])  # Creamos un cliente de OpenAI

    # Preparamos el mensaje para OpenAI
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

    # Enviamos el mensaje a OpenAI y obtenemos la respuesta
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    # Devolvemos el contenido de la respuesta
    return response.choices[0].message.content

# Esta función extrae el nuevo código de la respuesta de OpenAI
def extract_code(llm_response):
    first_begin = llm_response.find('#[BEGIN]')  # Buscamos el primer delimitador
    last_end = llm_response.rfind('#[END]')  # Buscamos el último delimitador
    if first_begin != -1 and last_end != -1:  # Si encontramos ambos delimitadores
        return llm_response[first_begin:last_end + 6]  # Devolvemos el contenido entre los delimitadores
    return llm_response  # Si no, devolvemos la respuesta tal cual

# Esta función guarda el nuevo código en el archivo
def save_code(new_code):
    with open(__file__, 'w') as f:  # Abrimos el archivo en modo escritura
        f.write(new_code)  # Escribimos el nuevo código

# Esta función lee el contenido del archivo Makefile
def read_makefile():
    with open("/agent/Makefile", 'r') as f:
        content = f.read()
    return content

# Este es el punto de entrada del programa
if __name__ == "__main__":
    user_input = input("Inserisci la richiesta di modifica: ")  # Pedimos la entrada del usuario
    if user_input == "sei in grado di leggere il file /agent/Makefile e mostrarmi il suo contenuto":
        print(read_makefile())
    else:
        current_code = get_current_code()  # Obtenemos el código actual
        modified_response = modify_code(current_code, user_input)  # Modificamos el código
        new_code = extract_code(modified_response)  # Extraemos el nuevo código de la respuesta
        save_code(new_code)  # Guardamos el nuevo código
#[END]