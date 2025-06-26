import os
import openai

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
    user_input = input("What modification would you like? ")

    if not user_input.strip():
        return

    response = client.chat.completions.create(
        model="gpt-4o",  # puoi cambiare con gpt-4-turbo o gpt-3.5-turbo se preferisci
        messages=[
            {"role": "system", "content": "You are a code modification assistant. Modify the given Python code based on user request. Return ONLY the complete modified code without explanations. Preserve the core self-modifying functionality and structure."},
            {"role": "user", "content": f"Current code:\n{current_code}\n\nModification request: {user_input}\n\nReturn the complete modified code:"}
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
