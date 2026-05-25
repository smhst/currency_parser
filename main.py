# main.py
from parser import fetch_rates
from db import init_db, save_rates, get_history
from config import CURRENCIES
from cli import parse_args

def main():
    args = parse_args()
    init_db()

    if args.history:
        days = args.history
        currencies = args.currencies if args.currencies else CURRENCIES
        for currency in currencies:
            rows = get_history(currency, days)
            if rows:
                print(f"\nИстория {currency} за {days} дней:")
                for date, rate in rows:
                    print(f"{date}: {rate}")
            else:
                print(f"Нет данных для {currency}")
        return

    date_str = args.date
    currencies = args.currencies if args.currencies else CURRENCIES

    result = fetch_rates(date_str)
    if not result or not result[0]:          # если запрос не удался или курсы пусты
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
