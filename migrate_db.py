import sqlite3
import os

DB_FILES = ["chess.db", "backend/chess.db"]

def migrate(db_file):
    if not os.path.exists(db_file):
        return

    print(f"Migrating {db_file}...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        # Check current schema
        cursor.execute("PRAGMA table_info(games)")
        table_info = cursor.fetchall()
        # info[1] is name, info[2] is type
        columns = {info[1]: info[2].upper() for info in table_info}
        
        needs_recreate = False
        if "white_player_id" in columns and "INT" in columns["white_player_id"]:
            needs_recreate = True
        if "black_player_id" in columns and "INT" in columns["black_player_id"]:
            needs_recreate = True
            
        if needs_recreate:
            print(f"Column type mismatch detected in {db_file}. Recreating games table...")
            # Recreating a table in SQLite to change types safely
            cursor.execute("ALTER TABLE games RENAME TO games_old")
            # The backend init_db will recreate the 'games' table with correct types 
            # based on the SQLAlchemy model on next startup.
            # We just want to make sure it doesn't conflict.
            # Alternatively, we define the table here:
            cursor.execute("""
                CREATE TABLE games (
                    id TEXT PRIMARY KEY,
                    variant TEXT NOT NULL,
                    fen TEXT NOT NULL,
                    move_history TEXT NOT NULL,
                    time_control TEXT,
                    clocks TEXT,
                    last_move_at FLOAT,
                    is_over BOOLEAN DEFAULT 0,
                    winner TEXT,
                    white_player_id TEXT,
                    black_player_id TEXT,
                    white_rating_diff FLOAT,
                    black_rating_diff FLOAT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Try to copy data, but player IDs might be corrupted
            print("Copying data from old table (player IDs may be lost)...")
            cursor.execute("""
                INSERT INTO games (id, variant, fen, move_history, time_control, clocks, last_move_at, is_over, winner, created_at, updated_at)
                SELECT id, variant, fen, move_history, time_control, clocks, last_move_at, is_over, winner, created_at, updated_at FROM games_old
            """)
            cursor.execute("DROP TABLE games_old")
        else:
            # Just add columns if missing
            if "white_player_id" not in columns:
                print(f"Adding white_player_id column to {db_file}...")
                cursor.execute("ALTER TABLE games ADD COLUMN white_player_id TEXT")
            
            if "black_player_id" not in columns:
                print(f"Adding black_player_id column to {db_file}...")
                cursor.execute("ALTER TABLE games ADD COLUMN black_player_id TEXT")

            if "white_rating_diff" not in columns:
                print(f"Adding white_rating_diff column to {db_file}...")
                cursor.execute("ALTER TABLE games ADD COLUMN white_rating_diff FLOAT")

            if "black_rating_diff" not in columns:
                print(f"Adding black_rating_diff column to {db_file}...")
                cursor.execute("ALTER TABLE games ADD COLUMN black_rating_diff FLOAT")

            if "uci_history" not in columns:
                print(f"Adding uci_history column to {db_file}...")
                cursor.execute("ALTER TABLE games ADD COLUMN uci_history TEXT")
            
        # Migrate users table
        cursor.execute("PRAGMA table_info(users)")
        user_table_info = cursor.fetchall()
        user_columns = {info[1] for info in user_table_info}
        
        if "supporter_badge" not in user_columns:
            print(f"Adding supporter_badge column to {db_file}...")
            cursor.execute("ALTER TABLE users ADD COLUMN supporter_badge TEXT")

        # Data Migration: Give all current users the kickstarter badge
        print(f"Ensuring all users have kickstarter badges in {db_file}...")
        cursor.execute("UPDATE users SET supporter_badge = 'kickstarter' WHERE supporter_badge IS NULL")

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
