import sqlite3
import os

# Check both potential paths
DB_FILES = ["chess.db", "backend/chess.db"]

def migrate(db_file):
    if not os.path.exists(db_file):
        return

    print(f"Migrating {db_file}...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        # Check if columns exist and their types
        cursor.execute("PRAGMA table_info(games)")
        table_info = cursor.fetchall()
        columns = {info[1]: info[2] for info in table_info}
        
        # We want to ensure these are TEXT (String) now
        if "white_player_id" not in columns:
            print(f"Adding white_player_id column to {db_file}...")
            cursor.execute("ALTER TABLE games ADD COLUMN white_player_id TEXT")
        
        if "black_player_id" not in columns:
            print(f"Adding black_player_id column to {db_file}...")
            cursor.execute("ALTER TABLE games ADD COLUMN black_player_id TEXT")
            
        conn.commit()
        print(f"Migration successful for {db_file}.")
    except Exception as e:
        print(f"Migration failed for {db_file}: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    for db in DB_FILES:
        migrate(db)