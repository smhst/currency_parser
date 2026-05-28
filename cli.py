# cli.py
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Парсер курсов валют ЦБ РФ")
    parser.add_argument("--date", type=str, help="Дата в формате ДД.ММ.ГГГГ")
    parser.add_argument("--currencies", nargs="+", help="Коды валют через пробел")
    parser.add_argument("--history", type=int, metavar="DAYS", help="Показать историю за последние DAYS дней")
    parser.add_argument("--plot", type=str, metavar="CURRENCY", help="Построить график для валюты")
    parser.add_argument("--days", type=int, default=30, help="Количество дней для графика (по умолч. 30)")
    parser.add_argument("--months", type=int, help="Период в месяцах (для истории/графика)")
    parser.add_argument("--years", type=int, help="Период в годах (для истории/графика)")
    parser.add_argument("--api", type=str, choices=["cbr", "erapi"], help="Выбор API (cbr или erapi)")
    return parser.parse_args()