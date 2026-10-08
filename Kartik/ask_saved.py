
import chromadb
import ollama

print("Connecting to ChromaDB...", flush=True)

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(
    name="fintech_policy_test_v2"
)

question = (
    "What suspicious transaction indicators "
    "are mentioned in both documents?"
)

print("Embedding question...", flush=True)

embedding = ollama.embed(
    model="nomic-embed-text",
    input=question
)["embeddings"][0]

context = ""

for filename in [
    "kyc_policy.pdf",
    "msb_prevention_guide.pdf"
]:
    print(f"Searching {filename}...", flush=True)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=2,
        where={"source": filename}
    )

    for document, metadata in zip(
        results["documents"][0],
        results["metadatas"][0]
    ):
        page = metadata["page"]

        print(
            f"Found: {filename}, PDF page {page}",
            flush=True
        )

        context += (
            f"\nSOURCE: {filename}\n"
            f"PDF PAGE: {page}\n"
            f"CONTENT: {document[:1200]}\n"
        )

print("\nGenerating answer with Qwen...", flush=True)

stream = ollama.chat(
    model="qwen3:4b",
    think=False,
    stream=True,
    messages=[
        {
            "role": "system",
            "content": (
                "Compare the supplied document excerpts. "
                "Use only the provided evidence. "
                "Cite filenames and PDF page numbers. "
                "Distinguish US and Indian policies. "
                "If evidence is insufficient, say so."
            )
        },
        {
            "role": "user",
            "content": (
                f"Question: {question}\n\n"
                f"Evidence:\n{context}"
            )
        }
    ],
    options={
        "num_ctx": 4096,
        "num_predict": 350
    }
)

print("\nFINLLM ANSWER\n", flush=True)

for chunk in stream:
    print(
        chunk["message"]["content"],
        end="",
        flush=True
    )

print("\n\nTest finished.")