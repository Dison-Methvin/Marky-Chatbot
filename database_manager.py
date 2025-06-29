import sqlite3
from datetime import datetime
from contextlib import contextmanager
import json
import csv
import os

DB_FILE = "chatbot.db"
LOGS_FILE = "interaction_logs.json"
CSV_FILE = "database.csv"

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_FILE)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """
    Initializes the database and creates the interactions table if it doesn't exist.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL
            )
        ''')
        conn.commit()
    print("Database initialized successfully.")

def insert_intents_from_json(file_path="intents.json"):
    with get_db_connection() as conn:
        cursor = conn.cursor()

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for intent in data['intents']:
            tag = intent['tag']
            cursor.execute("INSERT OR IGNORE INTO intents (tag) VALUES (?)", (tag,))
            conn.commit()

            cursor.execute("SELECT id FROM intents WHERE tag = ?", (tag,))
            intent_id = cursor.fetchone()[0]

            for pattern in intent.get("patterns", []):
                cursor.execute("INSERT INTO patterns (intent_id, pattern) VALUES (?, ?)", (intent_id, pattern))

            for response in intent.get("responses", []):
                cursor.execute("INSERT INTO responses (intent_id, response) VALUES (?, ?)", (intent_id, response))

        conn.commit()
    print("Intents inserted into database.")

def update_database(user_message, bot_response):
    """
    Update all logging mechanisms with the new interaction.
    """
    timestamp = datetime.now().isoformat()
    
    # Update SQLite database
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO interactions (timestamp, user_message, bot_response)
            VALUES (?, ?, ?)
        ''', (timestamp, user_message, bot_response))
        conn.commit()
    
    # Update JSON logs
    log_entry = {
        "timestamp": timestamp,
        "user_message": user_message,
        "bot_response": bot_response
    }
    
    try:
        # Read existing logs
        if os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []
        
        # Append new log
        logs.append(log_entry)
        
        # Write back to file
        with open(LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=4)
    except Exception as e:
        print(f"Error updating JSON logs: {e}")
    
    # Update CSV file
    try:
        file_exists = os.path.exists(CSV_FILE)
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['timestamp', 'user_message', 'bot_response'])
            writer.writerow([timestamp, user_message, bot_response])
    except Exception as e:
        print(f"Error updating CSV file: {e}")
    
    print("Interaction stored in all logging systems.")

def retrieve_logs():
    """
    Retrieve all interaction logs from the database.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM interactions ORDER BY timestamp DESC')
        logs = cursor.fetchall()
    return logs

def get_all_logs():
    """
    Retrieve logs from all sources (database, JSON, and CSV).
    Returns a dictionary with logs from each source.
    """
    logs = {
        'database': retrieve_logs(),
        'json': [],
        'csv': []
    }
    
    # Get JSON logs
    if os.path.exists(LOGS_FILE):
        try:
            with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                logs['json'] = json.load(f)
        except Exception as e:
            print(f"Error reading JSON logs: {e}")
    
    # Get CSV logs
    if os.path.exists(CSV_FILE):
        try:
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                logs['csv'] = list(reader)
        except Exception as e:
            print(f"Error reading CSV logs: {e}")
    
    return logs

# Optional for quick test
if __name__ == "__main__":
    init_db()
    update_database("Hello", "Hi there!")
    all_logs = get_all_logs()
    print("Database logs:", all_logs['database'])
    print("JSON logs:", all_logs['json'])
    print("CSV logs:", all_logs['csv'])