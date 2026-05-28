# plotter.py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, date
import os

def plot_currency(currency, history, days):
    if not history:
        print(f"Нет данных для {currency}, график не построен.")
        return

    dates = [datetime.strptime(d, "%Y-%m-%d") for d, _ in history]
    rates = [r for _, r in history]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dates, rates, marker='o', linestyle='-', linewidth=2, markersize=4, label=currency)

    ax.set_title(f"{currency} to RUB (last {days} days)", fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("Rate")
    ax.grid(True, linestyle='--', alpha=0.7)

    # Настройка оси дат: формат ДД.ММ.ГГ, авто-интервал
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=10))
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Создаём папку charts, если её нет
    output_dir = "charts"
    os.makedirs(output_dir, exist_ok=True)
    today_str = date.today().strftime("%Y%m%d")
    filename = f"{output_dir}/{currency.lower()}_{days}d_{today_str}.png"
    plt.savefig(filename)
    plt.close()
    print(f"График сохранён как {filename}")