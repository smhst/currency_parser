# web.py
import os
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for, send_file
import matplotlib
matplotlib.use('Agg')  # чтобы не открывать окна
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io

# Импорт наших модулей
from db import init_db, save_rates, get_history, get_missing_dates, get_currencies, add_currency, remove_currency
from parser import get_fetcher
from config import ACTIVE_API

app = Flask(__name__)
init_db()

fetcher = get_fetcher(ACTIVE_API)

# ------------------- Главная страница (текущие курсы) -------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    currencies = get_currencies()
    if request.method == 'POST':
        # Кнопка "Обновить курсы" или "Добавить валюту"
        if 'refresh' in request.form:
            try:
                rates, actual_date = fetcher.fetch()
                if rates:
                    save_rates(rates, actual_date)
            except Exception as e:
                pass  # обработаем ошибку в шаблоне
        elif 'add_currency' in request.form:
            code = request.form.get('new_currency', '').strip().upper()
            if code:
                add_currency(code)
        elif 'remove_currency' in request.form:
            code = request.form.get('remove_code')
            if code:
                remove_currency(code)
        return redirect(url_for('index'))

    # Получаем последние курсы из БД (или пытаемся загрузить)
    rates_data = {}
    today = date.today().isoformat()
    for currency in currencies:
        rows = get_history(currency, date.today(), date.today())
        if rows:
            rates_data[currency] = rows[0][1]  # (date, rate)
        else:
            # попробуем загрузить
            try:
                rates, actual_date = fetcher.fetch()
                if rates and currency in rates:
                    save_rates(rates, actual_date)
                    rates_data[currency] = rates[currency]
                else:
                    rates_data[currency] = None
            except:
                rates_data[currency] = None
    return render_template('index.html', rates=rates_data, currencies=currencies, today=today)

# ------------------- Страница истории -------------------
@app.route('/history', methods=['GET', 'POST'])
def history():
    currencies = get_currencies()
    rows = []
    currency = currencies[0] if currencies else ''
    d_from_str = (date.today() - timedelta(days=7)).strftime('%Y-%m-%d')
    d_to_str = date.today().isoformat()
    if request.method == 'POST':
        currency = request.form.get('currency')
        d_from_str = request.form.get('date_from')
        d_to_str = request.form.get('date_to')
        try:
            d_from = datetime.strptime(d_from_str, '%Y-%m-%d').date()
            d_to = datetime.strptime(d_to_str, '%Y-%m-%d').date()
            if d_from > d_to:
                error = "Дата начала позже даты окончания"
            else:
                # Проверяем и загружаем недостающие даты
                missing = get_missing_dates([currency], d_from, d_to)
                if missing:
                    for d_str in missing:
                        dt = datetime.strptime(d_str, '%Y-%m-%d')
                        req_date = dt.strftime('%d.%m.%Y')
                        rates, _ = fetcher.fetch(req_date)
                        if rates and currency in rates:
                            save_rates({currency: rates[currency]}, d_str)
                rows = get_history(currency, d_from, d_to)
        except ValueError:
            error = "Неверный формат даты"
    return render_template('history.html', currencies=currencies, rows=rows,
                           selected_currency=currency, date_from=d_from_str, date_to=d_to_str)

# ------------------- Страница графика -------------------
@app.route('/plot', methods=['GET', 'POST'])
def plot_view():
    currencies = get_currencies()
    plot_url = None
    error = None
    today = date.today()
    default_from = today - timedelta(days=30)
    if request.method == 'POST':
        currency = request.form.get('currency')
        mode = request.form.get('mode')  # 'days' или 'range'
        if mode == 'days':
            days = int(request.form.get('days', 30))
            d_to = date.today()
            d_from = d_to - timedelta(days=days)
        else:
            d_from_str = request.form.get('date_from')
            d_to_str = request.form.get('date_to')
            d_from = datetime.strptime(d_from_str, '%Y-%m-%d').date()
            d_to = datetime.strptime(d_to_str, '%Y-%m-%d').date()

        # Загрузка недостающих данных
        missing = get_missing_dates([currency], d_from, d_to)
        if missing:
            for d_str in missing:
                dt = datetime.strptime(d_str, '%Y-%m-%d')
                req_date = dt.strftime('%d.%m.%Y')
                rates, _ = fetcher.fetch(req_date)
                if rates and currency in rates:
                    save_rates({currency: rates[currency]}, d_str)

        # Получаем историю и строим график
        rows = get_history(currency, d_from, d_to)
        if rows:
            dates = [datetime.strptime(d, '%Y-%m-%d') for d, _ in rows]
            values = [r for _, r in rows]

            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(dates, values, marker='o', linestyle='-', linewidth=2)
            ax.set_title(f'{currency} ({d_from} — {d_to})')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=10))
            fig.autofmt_xdate()
            ax.grid(True, linestyle='--', alpha=0.7)
            # Сохраняем в BytesIO
            img = io.BytesIO()
            fig.savefig(img, format='png')
            img.seek(0)
            # Отправляем файл напрямую? Но проще сохранить во временный файл и передать путь.
            # Мы можем вставить как data URL
            import base64
            plot_data = base64.b64encode(img.getvalue()).decode()
            plot_url = f"data:image/png;base64,{plot_data}"
            plt.close(fig)
        else:
            error = "Нет данных для графика"

        return render_template('plot.html', currencies=currencies, plot_url=plot_url, error=error,
                               today=today, default_from=default_from)
    return render_template('plot.html', currencies=currencies, plot_url=None, error=None,
                           today=today, default_from=default_from)

if __name__ == '__main__':
    app.run(debug=True)