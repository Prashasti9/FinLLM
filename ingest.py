import ollama
import chromadb
from pypdf import PdfReader

import config


def read_pdf(path):
    """Return a list of (page_number, text) for pages that contain text."""
    reader = PdfReader(path)
    pages, skipped = [], 0
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = " ".join(text.split())          # collapse messy spacing/newlines
        if len(text) < 50:                      # blank or scanned-image page
            skipped += 1
            continue
        pages.append((page_number, text))
    return pages, skipped


def chunk_text(text, size=config.CHUNK_SIZE, overlap=config.CHUNK_OVERLAP):
    """Split text into overlapping chunks, preferring to cut at the end of a sentence."""
    chunks, start = [], 0
    while start < len(text):
        end = start + size
        if end < len(text):
            cut = text.rfind(". ", start, end)  # last full stop inside the window
            if cut > start + size // 2:         # only use it if chunk stays reasonably long
                end = cut + 1
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = end - overlap                    # step back so chunks overlap
    return chunks


def embed(texts):
    """Turn a list of texts into vectors. 'search_document:' is a hint nomic expects."""
    response = ollama.embed(
        model=config.EMBED_MODEL,
        input=[f"search_document: {t}" for t in texts],
    )
    return response["embeddings"]


def main():
    client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    collection = client.get_or_create_collection(name=config.COLLECTION_NAME)

    pdf_files = sorted(config.POLICY_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDFs found in {config.POLICY_DIR}")
        return

    total_pages = total_chunks = total_skipped = 0

    for pdf in pdf_files:
        print(f"\nReading {pdf.name} ...")
        pages, skipped = read_pdf(pdf)

        # Build chunks with labels saying where each one came from
        ids, documents, metadatas = [], [], []
        for page_number, page_text in pages:
            for i, chunk in enumerate(chunk_text(page_text)):
                ids.append(f"{pdf.stem}_p{page_number}_c{i}")
                documents.append(chunk)
                metadatas.append({"source": pdf.name, "page": page_number, "chunk": i})

        # Remove this file's old chunks so re-running doesn't leave stale ones
        collection.delete(where={"source": pdf.name})

        # Embed and store in batches of 32
        for b in range(0, len(documents), 32):
            batch_docs = documents[b:b + 32]
            collection.add(
                ids=ids[b:b + 32],
                documents=batch_docs,
                embeddings=embed(batch_docs),
                metadatas=metadatas[b:b + 32],
            )
            print(f"  stored {min(b + 32, len(documents))}/{len(documents)} chunks")

        print(f"  {len(pages)} pages read, {skipped} skipped, {len(documents)} chunks")
        total_pages += len(pages)
        total_chunks += len(documents)
        total_skipped += skipped

    print("\n=== Ingestion summary ===")
    print(f"Files:          {len(pdf_files)}")
    print(f"Pages read:     {total_pages}")
    print(f"Pages skipped:  {total_skipped}  (no extractable text)")
    print(f"Chunks stored:  {total_chunks}")
    print(f"Total in DB:    {collection.count()}")

    # Show one stored chunk so you can see what the database holds
    sample = collection.get(limit=1, include=["documents", "metadatas"])
    if sample["ids"]:
        print("\nSample chunk:")
        print(f"  {sample['metadatas'][0]}")
        print(f"  {sample['documents'][0][:300]}...")


if __name__ == "__main__":
    main()
