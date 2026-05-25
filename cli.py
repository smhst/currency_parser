# cli.py
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Парсер курсов валют ЦБ РФ")
    parser.add_argument(
        "--date",
        type=str,
        help="Дата в формате ДД.ММ.ГГГГ (например, 15.05.2026)"
    )
    parser.add_argument(
        "--currencies",
        nargs="+",
        help="Коды валют через пробел (USD EUR CNY). По умолчанию все из config.py"
    )
    parser.add_argument(
        "--history",
        type=int,
        metavar="DAYS",
        help="Показать историю курсов из БД за последние DAYS дней"
    )
    return parser.parse_args()
