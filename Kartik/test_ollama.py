import ollama

response = ollama.chat(
    model="qwen3:4b",
    messages=[
        {
            "role": "user",
            "content": "Explain credit risk in banking in 3 short points."
        }
    ]
)

print(response["message"]["content"])