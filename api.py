# api.py
from abc import ABC, abstractmethod
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, date
from config import CBR_URL
from db import get_currencies

def parse_cbr_date(date_str):
    """Преобразует дату из формата ЦБ (ДД.ММ.ГГГГ) в ISO (ГГГГ-ММ-ДД)"""
    return datetime.strptime(date_str, "%d.%m.%Y").strftime("%Y-%m-%d")

class BaseFetcher(ABC):
    @abstractmethod
    def fetch(self, date_str=None):
        pass

class CbrFetcher(BaseFetcher):
    def fetch(self, date_str=None):
        url = CBR_URL
        if date_str:
            url += f"?date_req={date_str}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            raw_date = root.attrib.get("Date")
            actual_date = parse_cbr_date(raw_date)
            rates = {}
            currencies = get_currencies()
            for valute in root.findall("Valute"):
                char_code = valute.find("CharCode").text
                if char_code in currencies:
                    value = valute.find("Value").text
                    value = float(value.replace(",", "."))
                    rates[char_code] = value
            return rates, actual_date
        except Exception as e:
            print(f"Ошибка получения курсов: {e}")
            return None, None

class ErApiFetcher(BaseFetcher):
    """Бесплатный API exchangerate.host, без ключа, курсы к RUB."""
    URL = "https://api.exchangerate.host/latest?base=RUB"

    def fetch(self, date_str=None):
        try:
            response = requests.get(self.URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            rates = {}
            currencies = get_currencies()
            for code in currencies:
                if code in data['rates']:
                    rate = 1 / data['rates'][code]
                    rates[code] = round(rate, 4)
            today = date.today().isoformat()
            return rates, today
        except Exception as e:
            print(f"Ошибка получения курсов через ER API: {e}")
            return None, None