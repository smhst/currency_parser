# main.py
import time
from datetime import datetime
from parser import fetch_rates, get_fetcher
from config import CURRENCIES
from cli import parse_args
from db import init_db, save_rates, get_history, get_missing_dates
from plotter import plot_currency

def main():
    args = parse_args()
    init_db()

    # --- Режим построения графика ---
    if args.plot:
        currency = args.plot.upper()
        days = args.days
        currencies = [currency]
        print(f"Подготовка данных для графика {currency} за {days} дней...")
        missing = get_missing_dates(currencies, days)
        if missing:
            print(f"Отсутствуют данные за {len(missing)} дат(ы). Загружаем...")
            fetcher = get_fetcher()
            for d_str in missing:
                dt = datetime.strptime(d_str, "%Y-%m-%d")
                req_date = dt.strftime("%d.%m.%Y")
                rates, _ = fetcher.fetch(req_date)
                if rates:
                    filtered = {c: rates[c] for c in currencies if c in rates}
                    if filtered:
                        save_rates(filtered, d_str)
            print("Загрузка завершена.")
        else:
            print("Все данные уже в базе.")
        history = get_history(currency, days)
        plot_currency(currency, history, days)
        return

    # --- Режим истории ---
    if args.history:
        days = args.history
        currencies = args.currencies if args.currencies else CURRENCIES
        print(f"Проверка истории за {days} дней...")
        missing = get_missing_dates(currencies, days)
        if missing:
            print(f"Отсутствуют данные за {len(missing)} дат(ы). Загружаем...")
            fetcher = get_fetcher()
            for d_str in missing:
                dt = datetime.strptime(d_str, "%Y-%m-%d")
                req_date = dt.strftime("%d.%m.%Y")
                rates, _ = fetcher.fetch(req_date)
                if rates:
                    filtered = {c: rates[c] for c in currencies if c in rates}
                    if filtered:
                        save_rates(filtered, d_str)
                        print(f"  Загружено за {d_str}: {filtered}")
                time.sleep(0.1)
            print("Загрузка завершена.")
        else:
            print("Все данные уже в базе.")
        
        for currency in currencies:
            rows = get_history(currency, days)
            if rows:
                print(f"\nИстория {currency} за {days} дней:")
                for row_date, rate in rows:
                    print(f"{row_date}: {rate}")
            else:
                print(f"Нет данных для {currency}")
        return

    # --- Обычный режим (сегодня / конкретная дата) ---
    date_str = args.date
    currencies = args.currencies if args.currencies else CURRENCIES

    result = fetch_rates(date_str)
    if not result or not result[0]:
        print("Не удалось получить курсы.")
        return

    rates, actual_date = result
    filtered = {c: rates[c] for c in currencies if c in rates}
    if filtered:
        print(f"Курсы на {actual_date}: {filtered}")
        save_rates(filtered, actual_date)
        print("Курсы сохранены в базу данных.")
    else:
        print(f"На {actual_date} курсы для выбранных валют не найдены.")

if __name__ == "__main__":
    main()