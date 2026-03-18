# Wrapper file for accessing the database
import sqlite3

DATABASE_PATH = "timelines.db"

def get_database():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row # Access columns by name
    conn.execute("PRAGMA foreign_keys = ON") # Enforce foreign keys per connection
    return conn

def init_database():
    with get_database() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS timelines (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                description TEXT
            );
        
            CREATE TABLE IF NOT EXISTS events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timeline_id INTEGER NOT NULL,
                title       TEXT    NOT NULL,
                description TEXT,
                event_date  TEXT    NOT NULL -- Stored as YYYY-MM-DD
            ); 
        """)

if __name__ == "__main__":
    init_database()
    print("Database initialised")