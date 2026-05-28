# utils.py
from datetime import datetime, date, timedelta

def resolve_date_range(args):
    """
    Возвращает (date_from, date_to) на основе аргументов.
    Приоритет: period > month > year > days.
    Если ни один не указан, возвращает последние args.days дней.
    """
    if args.period:
        # period задан в формате "ДД.ММ.ГГГГ"
        d1 = datetime.strptime(args.period[0], "%d.%m.%Y").date()
        d2 = datetime.strptime(args.period[1], "%d.%m.%Y").date()
        return min(d1, d2), max(d1, d2)
    elif args.month:
        # month = "2026-05"
        year, month = map(int, args.month.split('-'))
        first_day = date(year, month, 1)
        # следующий месяц, день 1, затем отнять 1 день -> последний день месяца
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        last_day = next_month - timedelta(days=1)
        return first_day, last_day
    elif args.year:
        year = args.year
        first_day = date(year, 1, 1)
        last_day = date(year, 12, 31)
        return first_day, last_day
    else:
        # по умолчанию: последние args.days дней
        today = date.today()
        return today - timedelta(days=args.days), today