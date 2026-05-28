# db.py
import sqlite3
from datetime import date, timedelta
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

def save_rates(rates, date_str=None):
    if not rates:
        return
    if date_str is None:
        date_str = date.today().isoformat()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for currency, rate in rates.items():
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO rates (currency, rate, date) VALUES (?, ?, ?)",
                (currency, rate, date_str)
            )
        except Exception as e:
            print(f"Ошибка сохранения {currency}: {e}")
    conn.commit()
    conn.close()

def get_history(currency, days):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    since = date.today() - timedelta(days=days)
    cursor.execute(
        "SELECT date, rate FROM rates WHERE currency = ? AND date >= ? ORDER BY date",
        (currency, since.isoformat())
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_missing_dates(currencies, days):
    """Возвращает уникальные даты (ISO), за которые отсутствуют записи хотя бы для одной валюты."""
    today = date.today()
    since = today - timedelta(days=days)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    missing_set = set()
    d = since
    while d <= today:
        d_str = d.isoformat()
        for currency in currencies:
            cursor.execute(
                "SELECT 1 FROM rates WHERE currency = ? AND date = ?",
                (currency, d_str)
            )
            if not cursor.fetchone():
                missing_set.add(d_str)
                break   # достаточно, что одной валюты нет — дату нужно загрузить
        d += timedelta(days=1)
    conn.close()
    return sorted(missing_set)   # список уникальных дат