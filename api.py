# api.py
from abc import ABC, abstractmethod
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from config import CBR_URL, CURRENCIES

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
