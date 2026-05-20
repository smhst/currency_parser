# Currency Rates Parser (ЦБ РФ)

Простой парсер курсов валют с сайта Центрального Банка России. Сохраняет данные в SQLite.

## Возможности
- Получение курсов USD, EUR (легко добавить другие)
- Сохранение в SQLite с защитой от дубликатов
- Готовность к периодическому запуску (cron/systemd timer)

## Установка и запуск
```bash
git clone https://github.com/yourusername/currency_parser.git
cd currency_parser
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py

## Использование в production
Добавьте в crontab ежедневный запуск (пример для Arch/любой Linux):
```cron
0 10 * * * cd /path/to/currency_parser && /path/to/venv/bin/python main.py
