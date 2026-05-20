# parser.py
import requests
import xml.etree.ElementTree as ET
from config import CBR_URL, CURRENCIES

def fetch_rates():
    try:
        response = requests.get(CBR_URL, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        rates = {}
        for valute in root.findall("Valute"):
            char_code = valute.find("CharCode").text
            if char_code in CURRENCIES:
                value = valute.find("Value").text
                value = float(value.replace(",", "."))
                rates[char_code] = value
        return rates
    except Exception as e:
        print(f"Ошибка получения курсов: {e}")
        return None
