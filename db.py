# db.py
import sqlite3
from datetime import date, timedelta
from config import DB_NAME, DEFAULT_CURRENCIES

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Таблица курсов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            currency TEXT NOT NULL,
            rate REAL NOT NULL,
            date TEXT NOT NULL,
            UNIQUE(currency, date)
        )
    """)
    # Таблица валют
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS currencies (
            code TEXT PRIMARY KEY
        )
    """)
    # Если таблица валют пуста, заполняем значениями по умолчанию
    cursor.execute("SELECT COUNT(*) FROM currencies")
    if cursor.fetchone()[0] == 0:
        for code in DEFAULT_CURRENCIES:
            cursor.execute("INSERT OR IGNORE INTO currencies (code) VALUES (?)", (code,))
    conn.commit()
    conn.close()

def get_currencies():
    """Возвращает список кодов валют из БД."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT code FROM currencies ORDER BY code")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def add_currency(code):
    code = code.upper()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO currencies (code) VALUES (?)", (code,))
        conn.commit()
        print(f"Валюта {code} добавлена.")
    except sqlite3.IntegrityError:
        print(f"Валюта {code} уже существует.")
    finally:
        conn.close()

def remove_currency(code):
    code = code.upper()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM currencies WHERE code = ?", (code,))
    if cursor.rowcount > 0:
        print(f"Валюта {code} удалена.")
    else:
        print(f"Валюта {code} не найдена.")
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

def get_history(currency, date_from, date_to):
    """Возвращает записи за период [date_from, date_to]."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date, rate FROM rates WHERE currency = ? AND date >= ? AND date <= ? ORDER BY date",
        (currency, date_from.isoformat(), date_to.isoformat())
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_missing_dates(currencies, date_from, date_to):
    """Возвращает уникальные даты в диапазоне, для которых нет записей хотя бы для одной валюты."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    missing_set = set()
    d = date_from
    while d <= date_to:
        d_str = d.isoformat()
        for currency in currencies:
            cursor.execute(
                "SELECT 1 FROM rates WHERE currency = ? AND date = ?",
                (currency, d_str)
            )
            if not cursor.fetchone():
                missing_set.add(d_str)
                break
        d += timedelta(days=1)
    conn.close()
    return sorted(missing_set)