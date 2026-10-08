import sqlite3

DB_FILE = "data/database/finllm.db"

print("\nConnecting to FinLLM database...\n")

connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()

tables = cursor.execute(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
    """
).fetchall()

print("========== FINLLM DATABASE TABLES ==========\n")

for table_row in tables:

    table_name = table_row[0]

    print(f"\nTABLE: {table_name}")
    print("-" * 50)

    columns = cursor.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    for column in columns:

        column_name = column[1]
        column_type = column[2]

        print(
            f"{column_name:<25} {column_type}"
        )

connection.close()

print("\nDatabase inspection finished.")