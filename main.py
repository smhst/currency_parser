# main.py
import time
from datetime import datetime, date
from parser import fetch_rates, get_fetcher
from config import ACTIVE_API
from cli import parse_args
from db import init_db, save_rates, get_history, get_missing_dates
from plotter import plot_currency
from utils import resolve_date_range
from db import get_currencies, add_currency, remove_currency

def fetch_with_retry(fetcher, req_date, max_retries=3):
    for attempt in range(max_retries):
        try:
            rates, actual_date = fetcher.fetch(req_date)
            return rates, actual_date
        except Exception as e:
            if "429" in str(e):
                print(f"  Превышен лимит запросов, ждём 2 сек... (попытка {attempt+1})")
                time.sleep(2)
            else:
                print(f"  Ошибка: {e}")
                return None, None
    print("  Не удалось получить данные после нескольких попыток.")
    return None, None

def main():
    args = parse_args()
    init_db()

    if args.add_currency:
        add_currency(args.add_currency)
        return

    if args.remove_currency:
        remove_currency(args.remove_currency)
        return

    if args.gui:
        from gui import main as gui_main
        gui_main()
        return

    # Определяем выбранный API, с учётом ограничений erapi для исторических запросов
    api_name = args.api
    if api_name == "erapi" and (args.history or args.plot or args.period or args.month or args.year):
        print("⚠️  ExchangeRate-API не поддерживает исторические данные. Автоматически переключаемся на ЦБ РФ.")
        api_name = "cbr"

    # Определяем диапазон дат, если нужно (для истории или графика)
    if args.history or args.plot:
        d_from, d_to = resolve_date_range(args)
        currencies = args.currencies if args.currencies else CURRENCIES
        if args.plot:
            currencies = [args.plot.upper()]
        # -- Режим графика --
        if args.plot:
            print(f"Готовлю график {args.plot.upper()} с {d_from} по {d_to} (API: {api_name or ACTIVE_API})...")
            missing = get_missing_dates(currencies, d_from, d_to)
            if missing:
                print(f"Не хватает данных за {len(missing)} дат(ы). Загружаю...")
                fetcher = get_fetcher(api_name)
                for d_str in missing:
                    dt = datetime.strptime(d_str, "%Y-%m-%d")
                    req_date = dt.strftime("%d.%m.%Y")
                    rates, _ = fetch_with_retry(fetcher, req_date)
                    if rates:
                        filtered = {c: rates[c] for c in currencies if c in rates}
                        if filtered:
                            save_rates(filtered, d_str)
                    time.sleep(0.3)
                print("Загрузка завершена.")
            else:
                print("Все данные уже есть.")
            history = get_history(args.plot.upper(), d_from, d_to)
            plot_currency(args.plot.upper(), history, (d_to - d_from).days)
            return

        # -- Режим истории --
        print(f"История с {d_from} по {d_to} (API: {api_name or ACTIVE_API})...")
        missing = get_missing_dates(currencies, d_from, d_to)
        if missing:
            print(f"Не хватает данных за {len(missing)} дат(ы). Загружаю...")
            fetcher = get_fetcher(api_name)
            for d_str in missing:
                dt = datetime.strptime(d_str, "%Y-%m-%d")
                req_date = dt.strftime("%d.%m.%Y")
                rates, _ = fetch_with_retry(fetcher, req_date)
                if rates:
                    filtered = {c: rates[c] for c in currencies if c in rates}
                    if filtered:
                        save_rates(filtered, d_str)
                        print(f"  Загружено за {d_str}: {filtered}")
                time.sleep(0.3)
            print("Загрузка завершена.")
        else:
            print("Все данные уже есть.")

        for currency in currencies:
            rows = get_history(currency, d_from, d_to)
            if rows:
                print(f"\nИстория {currency}:")
                for row_date, rate in rows:
                    print(f"{row_date}: {rate}")
            else:
                print(f"Нет данных для {currency}")
        return

    # --- Обычный режим (сегодня / конкретная дата) ---
    date_str = args.date
    currencies = args.currencies if args.currencies else CURRENCIES

    result = fetch_rates(date_str, api_name)
    if not result or not result[0]:
        print("Не удалось получить курсы.")
        return

    rates, actual_date = result
    filtered = {c: rates[c] for c in currencies if c in rates}
    if filtered:
        print(f"Курсы на {actual_date} ({api_name or ACTIVE_API}): {filtered}")
        save_rates(filtered, actual_date)
        print("Курсы сохранены в базу данных.")
    else:
        print(f"На {actual_date} курсы для выбранных валют не найдены.")

if __name__ == "__main__":
    main()