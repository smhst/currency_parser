# plotter.py
import matplotlib
matplotlib.use('Agg')          # неинтерактивный бэкенд, чтобы не требовалось окно
import matplotlib.pyplot as plt
from datetime import datetime

def plot_currency(currency, history, days):
    """
    Строит и сохраняет график.
    history: список кортежей (дата_iso, курс), отсортированный по дате.
    """
    if not history:
        print(f"Нет данных для {currency}, график не построен.")
        return

    dates = [datetime.strptime(d, "%Y-%m-%d") for d, _ in history]
    rates = [r for _, r in history]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, rates, marker='o', linestyle='-', linewidth=2, markersize=4)
    plt.title(f"{currency} to RUB (last {days} days)", fontsize=14)
    plt.xlabel("Date")
    plt.ylabel("Rate")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()

    filename = f"{currency.lower()}_chart.png"
    plt.savefig(filename)
    plt.close()
    print(f"График сохранён как {filename}")