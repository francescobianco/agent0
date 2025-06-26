#[BEGIN]
import os
import sys
from openai import OpenAI

def main():
    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

    with open(__file__, 'r') as f:
        current_code = f.read()

    user_input = input("Enter your request: ")

    prompt = f"""You are a code modification assistant. Your task is to modify the following Python code based on the user's request while preserving its self-modifying functionality.

CRITICAL RULES:
1. The code must remain a self-modifying file that can iterate and improve itself
2. Do not remove or change the core logic of reading itself, prompting user, calling OpenAI, and saving modifications
3. Keep the #[BEGIN] and #[END] delimiters intact and in the same positions
4. The modified code must still be able to modify itself in future iterations
5. Only modify what's necessary to fulfill the user's request
6. Maintain the compact and minimal structure

Current code:
{current_code}

User request: {user_input}

Return ONLY the modified code between #[BEGIN] and #[END] delimiters, including these delimiters."""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    modified_code = response.choices[0].message.content

    begin_marker = "#[BEGIN]"
    end_marker = "#[END]"

    if begin_marker in modified_code and end_marker in modified_code:
        start_idx = modified_code.find(begin_marker)
        end_idx = modified_code.find(end_marker) + len(end_marker)
        extracted_code = modified_code[start_idx:end_idx]

        with open(__file__, 'w') as f:
            f.write(extracted_code)

if __name__ == "__main__":
    main()
#[END]