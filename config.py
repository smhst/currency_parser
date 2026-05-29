# config.py
import os
CBR_URL = "https://www.cbr.ru/scripts/XML_daily.asp"
DB_NAME = "rates.db"
ACTIVE_API = "cbr"
DEFAULT_CURRENCIES = ["USD", "EUR", "CNY"]
DB_NAME = os.environ.get('DB_PATH', 'rates.db')