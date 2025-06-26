import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

with open(__file__, 'r') as f:
    current_code = f.read()

user_input = input("Enter modification request: ")

prompt = f"""You are modifying a self-modifying Python file. The file must retain its core functionality:
1. Read its own source code
2. Get user input for modifications
3. Use OpenAI API to modify itself
4. Save the modifications
5. Exit for next iteration

CRITICAL: The modified code MUST still be a self-modifying file with the same core logic and functionality. Do not remove or break the self-modification mechanism.

Current code:
{current_code}

User request: {user_input}

Return ONLY the complete modified Python code that maintains self-modification capability:"""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3
)

new_code = response.choices[0].message.content.strip()

if new_code.startswith("```python"):
    new_code = new_code[9:]
if new_code.endswith("```"):
    new_code = new_code[:-3]

with open(__file__, 'w') as f:
    f.write(new_code.strip())

print("File modified successfully")