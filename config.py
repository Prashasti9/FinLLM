from pathlib import Path

# ---------- Folders ----------
# BASE_DIR = the FinLLM folder, wherever it lives on any computer
BASE_DIR = Path(__file__).resolve().parent
POLICY_DIR = BASE_DIR / "data" / "policies"   # where PDFs go
CHROMA_DIR = BASE_DIR / "chroma_db"            # where the vector database is saved
LOG_DIR = BASE_DIR / "logs"                    # where Q&A logs are saved

# ---------- Models (run locally by Ollama) ----------
LLM_MODEL = "qwen3:4b"               # writes the answers
EMBED_MODEL = "nomic-embed-text"     # turns text into numbers for search

# ---------- Vector database ----------
COLLECTION_NAME = "fintech_policies"

# ---------- Chunking ----------
CHUNK_SIZE = 900      # characters per chunk
CHUNK_OVERLAP = 150   # characters shared between neighbouring chunks

# ---------- Retrieval ----------
TOP_K = 8             # how many chunks to fetch per question
