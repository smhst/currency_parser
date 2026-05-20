# main.py
from parser import fetch_rates
from db import init_db, save_rates

def main():
    print("Парсер курсов валют ЦБ РФ")
    init_db()
    rates = fetch_rates()
    if rates:
        print(f"Получены курсы: {rates}")
        save_rates(rates)
        print("Курсы сохранены в базу данных.")
    else:
        print("Не удалось получить курсы.")

if __name__ == "__main__":
    main()
