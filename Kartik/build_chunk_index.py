
from pathlib import Path
from hashlib import sha256
from pypdf import PdfReader
import chromadb
import ollama

POLICY_DIR = Path("data/policies")
CHUNK_SIZE = 1200
OVERLAP = 200
BATCH_SIZE = 8

SOURCES = {
    "kyc_policy.pdf": "India",
    "msb_prevention_guide.pdf": "United States"
}

documents = []
metadatas = []
ids = []

# Read and divide the PDFs
for filename, jurisdiction in SOURCES.items():
    path = POLICY_DIR / filename

    if not path.exists():
        raise FileNotFoundError(path)

    print(f"Reading {filename}...", flush=True)
    reader = PdfReader(str(path))

    for page_number, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        text = " ".join(text.split())

        if not text:
            continue

        start = 0

        while start < len(text):
            end = min(start + CHUNK_SIZE, len(text))
            chunk = text[start:end]

            chunk_id = sha256(
                f"{filename}:{page_number}:{start}".encode()
            ).hexdigest()

            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append({
                "source": filename,
                "page": page_number,
                "jurisdiction": jurisdiction,
                "start": start
            })

            if end == len(text):
                break

            start = end - OVERLAP

print(f"Created {len(documents)} chunks.", flush=True)

# Use a new collection to preserve previous tests
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="finllm_policy_chunks_v1"
)

# Generate and store embeddings in small batches
for start in range(0, len(documents), BATCH_SIZE):
    end = min(start + BATCH_SIZE, len(documents))

    batch_documents = documents[start:end]

    response = ollama.embed(
        model="nomic-embed-text",
        input=batch_documents
    )

    collection.upsert(
        ids=ids[start:end],
        documents=batch_documents,
        embeddings=response["embeddings"],
        metadatas=metadatas[start:end]
    )

    print(
        f"Indexed {end}/{len(documents)} chunks",
        flush=True
    )

print(
    f"\nFinished. ChromaDB contains "
    f"{collection.count()} chunks."
)