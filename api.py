# api.py
from abc import ABC, abstractmethod
import requests
import xml.etree.ElementTree as ET
from config import CBR_URL, CURRENCIES
import json
from datetime import datetime, date

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
            raw_date = root.attrib.get("Date")          # например "23.05.2026"
            actual_date = parse_cbr_date(raw_date)      # превращаем в "2026-05-23"
            rates = {}
            for valute in root.findall("Valute"):
                char_code = valute.find("CharCode").text
                if char_code in CURRENCIES:
                    value = valute.find("Value").text
                    value = float(value.replace(",", "."))
                    rates[char_code] = value
            return rates, actual_date
        except Exception as e:
            print(f"Ошибка получения курсов: {e}")
            return None, None

class ErApiFetcher(BaseFetcher):
    """Бесплатный API exchangerate-api.com, без ключа, курсы к RUB."""
    URL = "https://api.exchangerate-api.com/v4/latest/RUB"

    def fetch(self, date_str=None):
        # Этот API не поддерживает историю, date_str игнорируем
        try:
            response = requests.get(self.URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            rates = {}
            for code in CURRENCIES:
                if code in data['rates']:
                    # API возвращает курс, обратный к RUB, поэтому 1 / rate
                    rate = 1 / data['rates'][code]
                    rates[code] = round(rate, 4)
            today = date.today().isoformat()
            return rates, today
        except Exception as e:
            print(f"Ошибка получения курсов через ER API: {e}")
            return None, None