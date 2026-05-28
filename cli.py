# cli.py
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Парсер курсов валют ЦБ РФ")
    parser.add_argument("--date", type=str, help="Дата в формате ДД.ММ.ГГГГ")
    parser.add_argument("--currencies", nargs="+", help="Коды валют через пробел (USD EUR CNY)")
    parser.add_argument("--history", type=int, metavar="DAYS", help="Показать историю курсов из БД за последние DAYS дней")
    parser.add_argument("--plot", type=str, metavar="CURRENCY", help="Построить график для указанной валюты (например, USD)")
    parser.add_argument("--days", type=int, default=30, help="Количество дней для графика (по умолчанию 30)")
    return parser.parse_args()