import sys
import time

import ollama
import chromadb
import pypdf

import config


def ok(message):
    print(f"PASS {message}")


def fail(message):
    print(f"FAIL {message}")
    sys.exit(1)   # stop immediately - later checks depend on earlier ones


print("Checking FinLLM setup...\n")

# 1. Is Ollama running?
try:
    installed = ollama.list()
except Exception:
    fail("Cannot reach Ollama. Open the Ollama app, then try again.")
ok("Ollama is running")

# 2. Are both models downloaded?
names = [m.model for m in installed.models]
for needed in [config.LLM_MODEL, config.EMBED_MODEL]:
    if needed in names or f"{needed}:latest" in names:
        ok(f"Model found: {needed}")
    else:
        fail(f"Model missing: {needed}. Run: ollama pull {needed}")

# 3. Can the embedding model turn text into numbers?
vector = ollama.embed(model=config.EMBED_MODEL, input="test sentence")["embeddings"][0]
ok(f"Embeddings work (each text becomes {len(vector)} numbers)")

# 4. Can Qwen answer a question? (think=False skips the slow 'Thinking...' step)
start = time.time()
reply = ollama.chat(
    model=config.LLM_MODEL,
    messages=[{"role": "user", "content": "Reply with exactly: FinLLM ready"}],
    think=False,
)
seconds = time.time() - start
ok(f"Qwen replied in {seconds:.1f}s: {reply['message']['content'].split('</think>')[-1].strip()}")

# 5. Libraries
ok(f"ChromaDB version {chromadb.__version__}")
ok(f"pypdf version {pypdf.__version__}")

# 6. Is there a PDF to work with?
pdfs = list(config.POLICY_DIR.glob("*.pdf"))
if pdfs:
    for p in pdfs:
        ok(f"PDF found: {p.name}")
else:
    fail(f"No PDFs in {config.POLICY_DIR}. Add one and re-run.")

print("\nAll checks passed. Ready for ingestion.")
