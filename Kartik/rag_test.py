import chromadb
import ollama

# -----------------------------------
# 1. Create local ChromaDB database
# -----------------------------------

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="fintech_knowledge"
)

# -----------------------------------
# 2. Sample fintech knowledge
# -----------------------------------

documents = [
    """
    Credit risk is the possibility that a borrower will fail to repay
    a loan or meet financial obligations. Banks manage credit risk
    using credit scores, collateral, income verification, and
    diversification.
    """,

    """
    Fraud detection systems analyze transactions for unusual behavior.
    Machine learning can identify patterns such as unusual transaction
    amounts, suspicious locations, rapid transactions, and abnormal
    account activity.
    """,

    """
    Anti-Money Laundering, or AML, helps financial institutions detect
    and prevent illegal movement of money. AML systems monitor
    transactions, customer behavior, suspicious activity, and
    regulatory compliance.
    """
]

ids = [
    "credit_risk",
    "fraud_detection",
    "aml"
]

# -----------------------------------
# 3. Convert documents to embeddings
# -----------------------------------

embedding_response = ollama.embed(
    model="nomic-embed-text",
    input=documents
)

embeddings = embedding_response["embeddings"]

# -----------------------------------
# 4. Store documents in ChromaDB
# -----------------------------------

collection.upsert(
    ids=ids,
    documents=documents,
    embeddings=embeddings
)

print("Fintech documents stored in ChromaDB.")

# -----------------------------------
# 5. Ask a question
# -----------------------------------

question = "How can banks detect fraudulent transactions?"

question_embedding = ollama.embed(
    model="nomic-embed-text",
    input=question
)["embeddings"][0]

# -----------------------------------
# 6. Search ChromaDB
# -----------------------------------

results = collection.query(
    query_embeddings=[question_embedding],
    n_results=2
)

context = "\n\n".join(results["documents"][0])

print("\nRetrieved information:")
print(context)

# -----------------------------------
# 7. Send retrieved data to Qwen3
# -----------------------------------

prompt = f"""
You are a fintech AI assistant.

Answer the question using ONLY the information provided in the context.

Context:
{context}

Question:
{question}

Give a clear and concise answer.
"""

response = ollama.chat(
    model="qwen3:4b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

print("\nAI Answer:")
print(response["message"]["content"])