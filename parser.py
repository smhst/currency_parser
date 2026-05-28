# parser.py
from config import ACTIVE_API
from api import CbrFetcher, ErApiFetcher

def get_fetcher(api_name=None):
    if api_name is None:
        api_name = ACTIVE_API
    if api_name == "cbr":
        return CbrFetcher()
    elif api_name == "erapi":
        return ErApiFetcher()
    else:
        raise ValueError(f"Неизвестный API: {api_name}")

def fetch_rates(date_str=None, api_name=None):
    fetcher = get_fetcher(api_name)
    return fetcher.fetch(date_str)
