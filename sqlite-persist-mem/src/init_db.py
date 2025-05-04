import os
import sqlite3
import sys

def init_db():
    """
    Initialize the SQLite database if it doesn't exist.
    Creates the database and tables using the schema in sqlite.sql.
    """
    db_path = './sqlite/chainlit.db'
    
    # Check if database already exists
    if os.path.exists(db_path):
        print(f"Database {db_path} already exists. Skipping initialization.")
        return
    
    print(f"Database {db_path} does not exist. Creating...")
    
    # Read the schema from sqlite.sql
    try:
        with open('sqlite.sql', 'r') as f:
            schema = f.read()
    except FileNotFoundError:
        print("Error: sqlite.sql file not found.")
        sys.exit(1)
    
    # Create the database and execute the schema
    try:
        conn = sqlite3.connect(db_path)
        conn.executescript(schema)
        conn.commit()
        conn.close()
        print(f"Database {db_path} created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
