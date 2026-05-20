# Currency Rates Parser (ЦБ РФ)

Простой парсер курсов валют с сайта Центрального Банка России. Сохраняет данные в SQLite.

## Возможности
- Получение курсов USD, EUR (легко добавить другие)
- Сохранение в SQLite с защитой от дубликатов
- Готовность к периодическому запуску (cron/systemd timer)

## Установка и запуск
```bash
git clone https://github.com/smhst/currency_parser.git
cd currency_parser
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py

## Использование в production
Добавьте в crontab ежедневный запуск (пример для Arch/любой Linux):
```cron
0 10 * * * cd /path/to/currency_parser && /path/to/venv/bin/python main.py

!!! Замените /path/to/ на ваш путь к проекту».

## Пример работы

$ python main.py
Парсер курсов валют ЦБ РФ
Получены курсы: {'USD': 70.9509, 'EUR': 81.9823}
Курсы сохранены в базу данных.

$ sqlite3 rates.db "SELECT * FROM rates;"
╭────┬──────────┬─────────┬────────────╮
│ id │ currency │  rate   │    date    │
╞════╪══════════╪═════════╪════════════╡
│  1 │ USD      │ 70.9509 │ 2026-05-20 │
│  2 │ EUR      │ 81.9823 │ 2026-05-20 │
╰────┴──────────┴─────────┴────────────╯
