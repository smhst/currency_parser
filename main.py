# main.py
import time
from datetime import datetime, date
from parser import fetch_rates, get_fetcher
from config import CURRENCIES, ACTIVE_API
from cli import parse_args
from db import init_db, save_rates, get_history, get_missing_dates
from plotter import plot_currency

def fetch_with_retry(fetcher, req_date, max_retries=3):
    """Выполняет fetcher.fetch с повторными попытками при ошибках 429."""
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

def get_period_days(args):
    """Определяет количество дней на основе аргументов --days, --months, --years."""
    if args.years:
        return args.years * 365
    if args.months:
        return args.months * 30
    return args.days or 30

def main():
    args = parse_args()
    init_db()
    api_name = args.api

    # Определяем, запрошена ли история через любой из способов
    history_days = None
    if args.history is not None:
        history_days = args.history
    elif args.months or args.years:
        # пользователь указал месяцы/годы без --history -> выводим историю
        history_days = get_period_days(args)

    # --- Режим графика ---
    if args.plot:
        currency = args.plot.upper()
        days = get_period_days(args)
        currencies = [currency]
        print(f"Подготовка данных для графика {currency} за {days} дней (API: {api_name or ACTIVE_API})...")
        missing = get_missing_dates(currencies, days)
        if missing:
            print(f"Отсутствуют данные за {len(missing)} дат(ы). Загружаем...")
            fetcher = get_fetcher(api_name)
            for d_str in missing:
                dt = datetime.strptime(d_str, "%Y-%m-%d")
                req_date = dt.strftime("%d.%m.%Y")
                rates, _ = fetch_with_retry(fetcher, req_date)
                if rates:
                    filtered = {c: rates[c] for c in currencies if c in rates}
                    if filtered:
                        save_rates(filtered, d_str)
                time.sleep(0.1)
            print("Загрузка завершена.")
        else:
            print("Все данные уже в базе.")
        history = get_history(currency, days)
        plot_currency(currency, history, days)
        return

    # --- Режим истории ---
    if history_days:
        currencies = args.currencies if args.currencies else CURRENCIES
        print(f"Проверка истории за {history_days} дней (API: {api_name or ACTIVE_API})...")
        missing = get_missing_dates(currencies, history_days)
        if missing:
            print(f"Отсутствуют данные за {len(missing)} дат(ы). Загружаем...")
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
                time.sleep(0.1)
            print("Загрузка завершена.")
        else:
            print("Все данные уже в базе.")
        
        for currency in currencies:
            rows = get_history(currency, history_days)
            if rows:
                print(f"\nИстория {currency} за {history_days} дней:")
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