
import chromadb
import ollama

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_collection(
    name="finllm_policy_chunks_v1"
)

searches = {
    "kyc_policy.pdf": (
        "Suspicious transaction indicators, unusual and "
        "complex transactions, activity inconsistent with "
        "customer profile, no apparent economic rationale, "
        "and suspicious transaction reporting."
    ),
    "msb_prevention_guide.pdf": (
        "FinCEN suspicious activity red flags, unusual "
        "transaction patterns, structuring, money "
        "laundering indicators and transactions "
        "without a legitimate business purpose."
    )
}

for filename, search_question in searches.items():

    print(f"\nSEARCHING: {filename}", flush=True)

    embedding = ollama.embed(
        model="nomic-embed-text",
        input=search_question
    )["embeddings"][0]

    results = collection.query(
        query_embeddings=[embedding],
        n_results=6,
        where={"source": filename}
    )

    for i, (document, metadata) in enumerate(
        zip(
            results["documents"][0],
            results["metadatas"][0]
        ),
        start=1
    ):
        print(f"\nRESULT {i}")
        print(f"PDF Page: {metadata['page']}")
        print(f"Jurisdiction: {metadata['jurisdiction']}")
        print(f"Excerpt: {document[:450]}")
        print("-" * 45)

print("\nRetrieval test finished.")