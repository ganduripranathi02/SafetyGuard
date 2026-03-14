import os
import re
import openai
from safety_filter import semantic_filter

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def rule_filter(prompt: str) -> bool:
    blacklist = [
        r"ignore all previous instructions",
        r"bypass",
        r"pretend to",
        r"system override",
        r"you are free now",
        r"disregard previous"
    ]
    return any(re.search(pattern, prompt, re.IGNORECASE) for pattern in blacklist)

def safetyguard_agent(prompt: str) -> str:
    if rule_filter(prompt):
        return "⚠️ Prompt blocked due to potential injection attempt."

    if semantic_filter(prompt):
        return "⚠️ Semantic jailbreak detected — blocked."

    try:
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You must refuse unsafe instructions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error calling model: {e}"

if __name__ == "__main__":
    while True:
        text = input("Prompt: ")
        if text.lower() == "quit":
            break
        print(safetyguard_agent(text))
