import ollama
import config


def ask_llm(prompt, system=None):
    """Send a prompt to the local Qwen model and return a clean answer."""
    # "/no_think" goes in the system message so Qwen treats it as a setting, not text
    system_text = "/no_think\n" + (system or "")
    messages = [
        {"role": "system", "content": system_text},
        {"role": "user", "content": prompt},
    ]

    reply = ollama.chat(model=config.LLM_MODEL, messages=messages, think=False, options={"temperature": 0, "num_predict": 700, "num_ctx": 8192})
    text = reply["message"]["content"]

    # Safety nets: drop any leaked thinking, and any echoed switch
    if "</think>" in text:
        text = text.split("</think>", 1)[1]
    text = text.replace("/no_think", "")

    return text.strip()
