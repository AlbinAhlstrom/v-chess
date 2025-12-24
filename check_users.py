import sqlite3
import os

def check(db_path):
    print(f"\n--- Checking DB: {db_path} ---")
    if not os.path.exists(db_path):
        print("File not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables:", tables)

    for table_tuple in tables:
        table = table_tuple[0]
        print(f"\n[{table}] first 5 rows:")
        try:
            cursor.execute(f"SELECT * FROM {table} LIMIT 5")
            rows = cursor.fetchall()
            for r in rows:
                print(r)
        except Exception as e:
            print(f"Error reading {table}: {e}")

    conn.close()

if __name__ == "__main__":
    check("chess.db")
    check("backend/chess.db")
