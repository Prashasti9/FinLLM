import sys
import re
import sqlite3
import chromadb
import ollama


# ============================================================
# CONFIGURATION
# ============================================================

DB_FILE = "data/database/finllm.db"
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "finllm_policy_chunks_v1"

EMBED_MODEL = "nomic-embed-text"

RESULTS_PER_QUERY = 10
PAGES_PER_DOCUMENT = 2


# ============================================================
# 1. GET CASE ID
# ============================================================

if len(sys.argv) < 2:
    raise SystemExit(
        "Please provide a Case ID.\n"
        "Example:\n"
        "python -u link_case_policy.py CASE-TX1015"
    )

CASE_ID = sys.argv[1].strip()

if not CASE_ID:
    raise SystemExit("Case ID cannot be empty.")


# ============================================================
# 2. CONNECT TO SQLITE
# ============================================================

print("\nConnecting to FinLLM database...")

connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()


# ============================================================
# 3. LOAD REVIEW CASE
# ============================================================

cursor.execute(
    """
    SELECT
        case_id,
        transaction_id,
        customer_id,
        risk_score,
        review_level,
        risk_reasons
    FROM review_cases
    WHERE case_id = ?
    """,
    (CASE_ID,)
)

case = cursor.fetchone()

if case is None:
    connection.close()

    raise SystemExit(
        f"Case not found: {CASE_ID}"
    )


(
    case_id,
    transaction_id,
    customer_id,
    risk_score,
    review_level,
    risk_reasons
) = case


print("\n========== CASE ==========\n")

print("Case ID:", case_id)
print("Transaction:", transaction_id)
print("Customer:", customer_id)
print("Risk score:", risk_score)
print("Review level:", review_level)
print("Reasons:", risk_reasons)


# ============================================================
# 4. LOAD TRANSACTION DETAILS
# ============================================================

cursor.execute(
    """
    SELECT
        amount,
        baseline_average,
        amount_vs_baseline,
        country,
        device_id
    FROM transaction_analysis
    WHERE transaction_id = ?
    """,
    (transaction_id,)
)

transaction = cursor.fetchone()


if transaction is not None:

    (
        amount,
        baseline_average,
        amount_vs_baseline,
        country,
        device_id
    ) = transaction

else:

    amount = None
    baseline_average = None
    amount_vs_baseline = None
    country = None
    device_id = None


print("\n========== TRANSACTION CONTEXT ==========\n")

print("Amount:", amount)
print("Baseline average:", baseline_average)
print("Amount vs baseline:", amount_vs_baseline)
print("Country:", country)
print("Device:", device_id)


# ============================================================
# 5. CONNECT TO CHROMADB
# ============================================================

print("\nConnecting to policy vector database...")

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_collection(
    name=COLLECTION_NAME
)

print(
    f"Connected to {collection.count()} policy chunks."
)


# ============================================================
# 6. BUILD CASE-SPECIFIC SEARCH CONTEXT
# ============================================================

case_context_parts = [
    str(risk_reasons)
]


if amount_vs_baseline is not None:

    case_context_parts.append(
        f"transaction amount is "
        f"{amount_vs_baseline:.2f} times "
        f"customer normal activity"
    )


if country:

    case_context_parts.append(
        "transaction occurred in a country "
        "not previously observed for customer"
    )


if device_id:

    case_context_parts.append(
        "new or unusual customer transaction behavior"
    )


case_context = " ".join(case_context_parts)


# ============================================================
# 7. DOCUMENT-SPECIFIC SEARCH QUERIES
# ============================================================

search_queries = {

    "kyc_policy.pdf": [

        (
            "large and complex transactions "
            "unusual patterns inconsistent with normal "
            "expected activity of customer "
            "no apparent economic rationale "
            "legitimate purpose close monitoring "
            + case_context
        ),

        (
            "monitoring of transactions "
            "customer risk profile "
            "unusual large transaction "
            "customer behavior "
            "transaction requiring review "
            + case_context
        ),

        (
            "transactions inconsistent with customer's "
            "normal activity unusual patterns "
            "large transaction monitoring "
            "risk management "
            + case_context
        )
    ],

    "msb_prevention_guide.pdf": [

        (
            "unusual characteristics or activities "
            "customer activity unusual transactions "
            "patterns of transactions suspicious activity "
            + case_context
        ),

        (
            "transactions inconsistent with normal "
            "customer behavior unusual location "
            "customer activity reports "
            "large transaction suspicious transaction "
            + case_context
        ),

        (
            "identify unusual transactions "
            "customer behavior monitoring "
            "unusual transaction patterns "
            "activity outside normal customer behavior "
            + case_context
        )
    ]
}


# ============================================================
# 8. RELEVANCE PHRASES
# ============================================================

relevance_phrases = {

    "kyc_policy.pdf": {

        "large and complex": 10,
        "unusual pattern": 8,
        "inconsistent with": 8,
        "normal activity": 8,
        "expected activity": 8,
        "economic rationale": 9,
        "legitimate purpose": 8,
        "close monitoring": 8,
        "monitoring of transactions": 7,
        "risk profile": 5,
        "customer behavior": 5,
        "unusual transaction": 7
    },

    "msb_prevention_guide.pdf": {

        "unusual characteristics": 10,
        "unusual activity": 8,
        "unusual transaction": 9,
        "patterns of transactions": 9,
        "customer activity": 8,
        "customer behavior": 7,
        "service area": 6,
        "large transaction": 6,
        "suspicious transaction": 5,
        "monitor": 4
    }
}


# ============================================================
# 9. LOW-QUALITY PAGE FILTER
# ============================================================

def is_low_quality_chunk(text):

    if not text:
        return True

    clean = text.strip()
    lower = clean.lower()

    if len(clean) < 100:
        return True

    bad_markers = [

        "table of contents",

        "sr.no. topic page no",

        "sr. no. topic page no",

        "contents page no",

        "index of contents"
    ]

    for marker in bad_markers:

        if marker in lower:
            return True


    # Detect PDF table-of-contents dot leaders such as:
    # ................. 29
    dot_leader = re.search(
        r"(?:\.\s*){8,}",
        clean
    )

    if dot_leader:
        return True


    return False


# ============================================================
# 10. LEXICAL RELEVANCE SCORE
# ============================================================

def lexical_score(
    text,
    filename
):

    lower = text.lower()

    score = 0.0


    # ----------------------------------------
    # Source-specific high-value phrases
    # ----------------------------------------

    for phrase, weight in relevance_phrases[
        filename
    ].items():

        if phrase in lower:
            score += weight


    # ----------------------------------------
    # General compliance concepts
    # ----------------------------------------

    common_terms = {

        "transaction": 1.0,
        "customer": 1.0,
        "monitor": 2.0,
        "unusual": 3.0,
        "pattern": 2.0,
        "activity": 1.0,
        "risk": 1.0
    }


    for term, weight in common_terms.items():

        if term in lower:
            score += weight


    return score


# ============================================================
# 11. SEARCH ONE POLICY DOCUMENT
# ============================================================

def search_policy_document(
    filename,
    queries
):

    print(
        f"\nSearching policy: {filename}"
    )

    candidates_by_page = {}


    # --------------------------------------------------------
    # Run multiple semantic searches
    # --------------------------------------------------------

    for query_number, query_text in enumerate(
        queries,
        start=1
    ):

        print(
            f"  Search query {query_number}/{len(queries)}"
        )


        embedding = ollama.embed(
            model=EMBED_MODEL,
            input=query_text
        )["embeddings"][0]


        results = collection.query(

            query_embeddings=[
                embedding
            ],

            n_results=RESULTS_PER_QUERY,

            where={
                "source": filename
            }
        )


        documents = results["documents"][0]
        metadatas = results["metadatas"][0]


        for rank, (
            document,
            metadata
        ) in enumerate(

            zip(
                documents,
                metadatas
            )

        ):

            if is_low_quality_chunk(document):
                continue


            page = metadata.get("page")

            if page is None:
                continue


            # --------------------------------------------
            # Lexical relevance
            # --------------------------------------------

            score = lexical_score(
                document,
                filename
            )


            # --------------------------------------------
            # Semantic ranking bonus
            # --------------------------------------------

            rank_bonus = (
                RESULTS_PER_QUERY - rank
            ) * 0.25

            score += rank_bonus


            candidate = {

                "score": score,

                "source":
                    metadata.get(
                        "source",
                        filename
                    ),

                "page":
                    page,

                "jurisdiction":
                    metadata.get(
                        "jurisdiction",
                        "Unknown"
                    ),

                "content":
                    document
            }


            # --------------------------------------------
            # Keep best chunk from each PDF page
            # --------------------------------------------

            if page not in candidates_by_page:

                candidates_by_page[
                    page
                ] = candidate

            else:

                existing_score = (
                    candidates_by_page[
                        page
                    ]["score"]
                )

                if score > existing_score:

                    candidates_by_page[
                        page
                    ] = candidate


    # --------------------------------------------------------
    # Rank pages by combined score
    # --------------------------------------------------------

    candidates = list(
        candidates_by_page.values()
    )

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )


    if len(candidates) < PAGES_PER_DOCUMENT:

        raise RuntimeError(
            f"Not enough strong policy evidence "
            f"found in {filename}."
        )


    selected = candidates[
        :PAGES_PER_DOCUMENT
    ]


    print(
        "\n  Selected evidence:"
    )


    for item in selected:

        print(
            f"  PDF page {item['page']} "
            f"| relevance score "
            f"{item['score']:.2f}"
        )


    return selected


# ============================================================
# 12. RETRIEVE INDIA + U.S. POLICY EVIDENCE
# ============================================================

retrieved_evidence = []


try:

    for policy_file in [

        "kyc_policy.pdf",
        "msb_prevention_guide.pdf"

    ]:

        selected = search_policy_document(

            policy_file,

            search_queries[
                policy_file
            ]
        )

        retrieved_evidence.extend(
            selected
        )


except RuntimeError as error:

    connection.close()

    raise SystemExit(
        str(error)
    )


# ============================================================
# 13. VALIDATE RETRIEVAL
# ============================================================

india_evidence = [

    item
    for item in retrieved_evidence
    if item["source"] == "kyc_policy.pdf"
]


us_evidence = [

    item
    for item in retrieved_evidence
    if item["source"] ==
    "msb_prevention_guide.pdf"
]


if (
    len(india_evidence) != 2
    or
    len(us_evidence) != 2
):

    connection.close()

    raise SystemExit(
        "Policy evidence validation failed. "
        "Expected exactly two India pages "
        "and two U.S. pages."
    )


# ============================================================
# 14. CREATE POLICY EVIDENCE TABLE
# ============================================================

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS case_policy_evidence (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        case_id TEXT NOT NULL,

        source TEXT NOT NULL,

        page INTEGER NOT NULL,

        jurisdiction TEXT,

        content TEXT NOT NULL,

        UNIQUE(case_id, source, page)
    )
    """
)

connection.commit()


# ============================================================
# 15. DELETE OLD EVIDENCE FOR THIS CASE
# ============================================================

cursor.execute(
    """
    DELETE FROM case_policy_evidence
    WHERE case_id = ?
    """,
    (case_id,)
)

connection.commit()


# ============================================================
# 16. SAVE NEW POLICY EVIDENCE
# ============================================================

for evidence in retrieved_evidence:

    cursor.execute(
        """
        INSERT INTO case_policy_evidence (

            case_id,
            source,
            page,
            jurisdiction,
            content

        )

        VALUES (?, ?, ?, ?, ?)
        """,

        (
            case_id,
            evidence["source"],
            evidence["page"],
            evidence["jurisdiction"],
            evidence["content"]
        )
    )


connection.commit()


# ============================================================
# 17. DISPLAY EXACT SAVED EVIDENCE
# ============================================================

print(
    "\n=========================================="
)

print(
    "          CASE POLICY EVIDENCE"
)

print(
    "==========================================\n"
)


for index, evidence in enumerate(
    retrieved_evidence,
    start=1
):

    print(
        f"[P{index}]"
    )

    print(
        "Source:",
        evidence["source"]
    )

    print(
        "PDF page:",
        evidence["page"]
    )

    print(
        "Jurisdiction:",
        evidence["jurisdiction"]
    )

    print(
        "Retrieval score:",
        round(
            evidence["score"],
            2
        )
    )


    excerpt = (
        evidence["content"]
        .replace(
            "\n",
            " "
        )
        .strip()
    )


    print(
        "Excerpt:",
        excerpt[:500]
    )

    print(
        "-" * 70
    )


# ============================================================
# 18. DATABASE VERIFICATION
# ============================================================

cursor.execute(
    """
    SELECT COUNT(*)
    FROM case_policy_evidence
    WHERE case_id = ?
    """,
    (case_id,)
)

saved_count = cursor.fetchone()[0]


print(
    "\n========== DATABASE VERIFICATION ==========\n"
)

print(
    "Case:",
    case_id
)

print(
    "Policy evidence rows saved:",
    saved_count
)


if saved_count != 4:

    connection.close()

    raise SystemExit(
        "Database verification failed. "
        f"Expected 4 evidence rows, "
        f"found {saved_count}."
    )


# ============================================================
# 19. FINISH
# ============================================================

connection.close()


print(
    f"\nPolicy evidence linked to {case_id}."
)

print(
    "\nPhase 4.3 policy-link test finished."
)