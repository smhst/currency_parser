# parser.py
from config import ACTIVE_API
from api import CbrFetcher

def get_fetcher():
    if ACTIVE_API == "cbr":
        return CbrFetcher()
    else:
        raise ValueError(f"Неизвестный API: {ACTIVE_API}")

def fetch_rates(date_str=None):
    fetcher = get_fetcher()
    return fetcher.fetch(date_str)   # возвращает кортеж (rates, actual_date)
