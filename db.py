import sqlite3

DB_FILE = "health_assistant.db"

# Initialize DB and tables
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Vaccinations table
    c.execute('''
        CREATE TABLE IF NOT EXISTS vaccinations (
            user_id TEXT,
            vaccine TEXT,
            due_date TEXT
        )
    ''')
    # Symptoms table
    c.execute('''
        CREATE TABLE IF NOT EXISTS symptoms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symptom TEXT,
            triage TEXT,
            advice TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Vaccination functions
def get_due_vaccines(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT vaccine, due_date FROM vaccinations WHERE user_id=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

# Symptom logging
def log_symptom(symptom, triage, advice):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO symptoms (symptom, triage, advice) VALUES (?, ?, ?)",
              (symptom, triage, advice))
    conn.commit()
    conn.close()

# Symptom history
def get_symptom_history():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT symptom, triage, advice FROM symptoms ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows