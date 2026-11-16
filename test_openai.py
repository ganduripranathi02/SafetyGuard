import os
from openai import OpenAI

key = os.getenv("OPENAI_API_KEY")
if not key:
    raise SystemExit("OPENAI_API_KEY is not set")
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")   # was hard-coded -> caused the Ollama 404
print("Key prefix:", key[:8], "| model:", model, "| base_url:", os.getenv("OPENAI_BASE_URL", "default"))

try:
    r = OpenAI(api_key=key).chat.completions.create(
        model=model, messages=[{"role": "user", "content": "Hello!"}])
    print("✅ Model reply:", r.choices[0].message.content)
except Exception as e:
    print("❌ Error:", e)
