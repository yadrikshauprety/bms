# scripts/init_db.py
import sqlite3
from pathlib import Path

DB_PATH = Path(_file_).resolve().parents[1] / "health_assistant.db"

schema = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  external_id TEXT UNIQUE,          -- e.g., phone/email/user handle (optional)
  name TEXT,
  language TEXT DEFAULT 'en',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vaccinations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  vaccine_name TEXT NOT NULL,
  dose_number INTEGER,
  date_administered TEXT,           -- ISO date string
  notes TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS medical_reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  filename TEXT,                    -- uploaded PDF name
  extracted_text TEXT,              -- text extracted from PDF
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS report_hashes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  report_id INTEGER NOT NULL,
  sha256 TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (report_id) REFERENCES medical_reports(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chats (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  role TEXT CHECK(role IN ('user','assistant')) NOT NULL,
  message TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_vaccinations_user_id ON vaccinations(user_id);
CREATE INDEX IF NOT EXISTS idx_medical_reports_user_id ON medical_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_report_hashes_report_id ON report_hashes(report_id);
CREATE INDEX IF NOT EXISTS idx_chats_user_id ON chats(user_id);
"""

def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(schema)
        conn.commit()
        print(f"Initialized DB at: {DB_PATH}")
    finally:
        conn.close()

if _name_ == "_main_":
    main()