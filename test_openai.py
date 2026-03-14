import openai, os

print("Key prefix:", os.getenv("OPENAI_API_KEY")[:8])

try:
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print("✅ Model reply:", response.choices[0].message.content)
except Exception as e:
    print("❌ Error:", e)

