# cli.py
import argparse
from datetime import datetime

def valid_date(s):
    """Проверяет, что строка в формате ДД.ММ.ГГГГ, и возвращает её же."""
    try:
        datetime.strptime(s, "%d.%m.%Y")
        return s
    except ValueError:
        raise argparse.ArgumentTypeError(f"Неверный формат даты: '{s}'. Ожидается ДД.ММ.ГГГГ")

def valid_month(s):
    """Проверяет формат ГГГГ-ММ (например, 2026-05)."""
    try:
        datetime.strptime(s, "%Y-%m")
        return s
    except ValueError:
        raise argparse.ArgumentTypeError(f"Неверный формат месяца: '{s}'. Ожидается ГГГГ-ММ")

def valid_year(s):
    """Проверяет, что это целое число – год."""
    try:
        y = int(s)
        if 1990 <= y <= 2100:
            return y
        else:
            raise ValueError
    except ValueError:
        raise argparse.ArgumentTypeError(f"Неверный год: '{s}'. Ожидается число, например 2026")

def parse_args():
    parser = argparse.ArgumentParser(description="Парсер курсов валют ЦБ РФ")
    parser.add_argument("--date", type=valid_date, help="Дата в формате ДД.ММ.ГГГГ")
    parser.add_argument("--currencies", nargs="+", help="Коды валют через пробел (USD EUR CNY)")

    # Диапазоны
    parser.add_argument("--period", nargs=2, type=valid_date, metavar=("DATE_FROM", "DATE_TO"),
                        help="Период с ДД.ММ.ГГГГ по ДД.ММ.ГГГГ")
    parser.add_argument("--month", type=valid_month, help="Месяц в формате ГГГГ-ММ (например, 2026-05)")
    parser.add_argument("--year", type=valid_year, help="Год (например, 2026)")
    parser.add_argument("--days", type=int, default=30, help="Количество последних дней (по умолчанию 30)")

    # Действия
    parser.add_argument("--history", action="store_true", help="Показать историю курсов")
    parser.add_argument("--plot", type=str, metavar="CURRENCY", help="Построить график для валюты (например, USD)")

    parser.add_argument("--add-currency", type=str, help="Добавить валюту (код)")
    parser.add_argument("--remove-currency", type=str, help="Удалить валюту (код)")

    parser.add_argument("--api", type=str, choices=["cbr", "erapi"], help="Выбор API (cbr или erapi)")

    parser.add_argument("--gui", action="store_true", help="Запустить графический интерфейс")
    parser.add_argument("--web", action="store_true", help="Запустить веб-интерфейс на Flask")
    return parser.parse_args()