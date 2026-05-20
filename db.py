# db.py
import sqlite3
from datetime import date
from config import DB_NAME

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            currency TEXT NOT NULL,
            rate REAL NOT NULL,
            date TEXT NOT NULL,
            UNIQUE(currency, date)
        )
    """)
    conn.commit()
    conn.close()

def save_rates(rates):
    if not rates:
        return
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today = date.today().isoformat()
    for currency, rate in rates.items():
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO rates (currency, rate, date) VALUES (?, ?, ?)",
                (currency, rate, today)
            )
        except Exception as e:
            print(f"Ошибка сохранения {currency}: {e}")
    conn.commit()
    conn.close()
