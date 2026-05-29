# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime, date, timedelta
import matplotlib
matplotlib.use('TkAgg')  # бэкенд для встраивания в Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates

# Импортируем наши рабочие модули
from db import init_db, save_rates, get_history
from api import CbrFetcher, parse_cbr_date
from parser import get_fetcher
from config import CURRENCIES, ACTIVE_API

class CurrencyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Парсер курсов валют")
        self.root.geometry("800x600")

        self.fetcher = get_fetcher(ACTIVE_API)
        self.init_db_once()

        # Создаём вкладки
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.create_current_tab()
        self.create_history_tab()
        self.create_plot_tab()

    def init_db_once(self):
        init_db()

    # ---------- Вкладка "Текущие курсы" ----------
    def create_current_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Текущие курсы')

        ttk.Button(frame, text='Обновить', command=self.refresh_current).pack(pady=10)

        # Таблица
        columns = ('Валюта', 'Курс', 'Дата')
        self.current_tree = ttk.Treeview(frame, columns=columns, show='headings', height=5)
        for col in columns:
            self.current_tree.heading(col, text=col)
        self.current_tree.pack(fill='both', expand=True, padx=10, pady=10)

        self.status_label = ttk.Label(frame, text='')
        self.status_label.pack()

    def refresh_current(self):
        self.status_label.config(text='Загрузка...')
        threading.Thread(target=self._fetch_current, daemon=True).start()

    def _fetch_current(self):
        try:
            rates, actual_date = self.fetcher.fetch()
            if not rates:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", "Не удалось получить курсы"))
                return
            # Сохраняем в БД (тихо)
            save_rates(rates, actual_date)
            # Обновляем таблицу в главном потоке
            self.root.after(0, self._update_current_table, rates, actual_date)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", str(e)))

    def _update_current_table(self, rates, actual_date):
        for row in self.current_tree.get_children():
            self.current_tree.delete(row)
        for code, rate in rates.items():
            self.current_tree.insert('', 'end', values=(code, rate, actual_date))
        self.status_label.config(text=f'Данные на {actual_date}')

    # ---------- Вкладка "История" ----------
    def create_history_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='История')

        # Панель управления
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill='x', pady=10, padx=10)

        ttk.Label(control_frame, text='Валюта:').pack(side='left')
        self.hist_currency = ttk.Combobox(control_frame, values=CURRENCIES, width=5)
        self.hist_currency.pack(side='left', padx=5)
        self.hist_currency.current(0)

        ttk.Label(control_frame, text='С:').pack(side='left')
        self.hist_start = ttk.Entry(control_frame, width=12)
        self.hist_start.pack(side='left', padx=5)
        self.hist_start.insert(0, (date.today() - timedelta(days=7)).strftime('%d.%m.%Y'))

        ttk.Label(control_frame, text='По:').pack(side='left')
        self.hist_end = ttk.Entry(control_frame, width=12)
        self.hist_end.pack(side='left', padx=5)
        self.hist_end.insert(0, date.today().strftime('%d.%m.%Y'))

        ttk.Button(control_frame, text='Показать', command=self.show_history).pack(side='left', padx=10)

        # Таблица истории
        columns = ('Дата', 'Курс')
        self.hist_tree = ttk.Treeview(frame, columns=columns, show='headings')
        self.hist_tree.heading('Дата', text='Дата')
        self.hist_tree.heading('Курс', text='Курс')
        self.hist_tree.pack(fill='both', expand=True, padx=10, pady=10)

        self.hist_status = ttk.Label(frame, text='')
        self.hist_status.pack()

    def show_history(self):
        currency = self.hist_currency.get()
        try:
            d1 = datetime.strptime(self.hist_start.get(), '%d.%m.%Y').date()
            d2 = datetime.strptime(self.hist_end.get(), '%d.%m.%Y').date()
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты")
            return
        if d1 > d2:
            messagebox.showerror("Ошибка", "Дата начала позже даты окончания")
            return

        self.hist_status.config(text='Загрузка...')
        threading.Thread(target=self._fetch_history, args=(currency, d1, d2), daemon=True).start()

    def _fetch_history(self, currency, d1, d2):
        # Проверяем недостающие даты и загружаем
        from db import get_missing_dates
        missing = get_missing_dates([currency], d1, d2)
        if missing:
            fetcher = self.fetcher
            for d_str in missing:
                dt = datetime.strptime(d_str, '%Y-%m-%d')
                req_date = dt.strftime('%d.%m.%Y')
                rates, _ = fetcher.fetch(req_date)
                if rates:
                    filtered = {c: rates[c] for c in [currency] if c in rates}
                    if filtered:
                        save_rates(filtered, d_str)
        rows = get_history(currency, d1, d2)
        self.root.after(0, self._update_history_table, rows, currency)

    def _update_history_table(self, rows, currency):
        for row in self.hist_tree.get_children():
            self.hist_tree.delete(row)
        for date_str, rate in rows:
            self.hist_tree.insert('', 'end', values=(date_str, rate))
        self.hist_status.config(text=f'{currency}: найдено {len(rows)} записей')

    # ---------- Вкладка "График" ----------
    def create_plot_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='График')

        control_frame = ttk.Frame(frame)
        control_frame.pack(fill='x', pady=10, padx=10)

        ttk.Label(control_frame, text='Валюта:').pack(side='left')
        self.plot_currency = ttk.Combobox(control_frame, values=CURRENCIES, width=5)
        self.plot_currency.pack(side='left', padx=5)
        self.plot_currency.current(0)

        ttk.Label(control_frame, text='Дней:').pack(side='left')
        self.plot_days = ttk.Entry(control_frame, width=5)
        self.plot_days.pack(side='left', padx=5)
        self.plot_days.insert(0, '30')

        ttk.Button(control_frame, text='Построить', command=self.show_plot).pack(side='left', padx=10)

        # Область для графика (будет заполнена позже)
        self.plot_frame = ttk.Frame(frame)
        self.plot_frame.pack(fill='both', expand=True)

        self.plot_status = ttk.Label(frame, text='')
        self.plot_status.pack()

    def show_plot(self):
        currency = self.plot_currency.get()
        try:
            days = int(self.plot_days.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Количество дней должно быть числом")
            return

        self.plot_status.config(text='Построение графика...')
        threading.Thread(target=self._fetch_plot, args=(currency, days), daemon=True).start()

    def _fetch_plot(self, currency, days):
        d_to = date.today()
        d_from = d_to - timedelta(days=days)
        from db import get_missing_dates
        missing = get_missing_dates([currency], d_from, d_to)
        if missing:
            fetcher = self.fetcher
            for d_str in missing:
                dt = datetime.strptime(d_str, '%Y-%m-%d')
                req_date = dt.strftime('%d.%m.%Y')
                rates, _ = fetcher.fetch(req_date)
                if rates:
                    filtered = {c: rates[c] for c in [currency] if c in rates}
                    if filtered:
                        save_rates(filtered, d_str)
        rows = get_history(currency, d_from, d_to)
        self.root.after(0, self._draw_plot, rows, currency, days)

    def _draw_plot(self, rows, currency, days):
        # Удаляем старый график
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        if not rows:
            self.plot_status.config(text='Нет данных для графика')
            return

        dates = [datetime.strptime(d, '%Y-%m-%d') for d, _ in rows]
        rates = [r for _, r in rows]

        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(dates, rates, marker='o', linestyle='-', linewidth=2, markersize=4)
        ax.set_title(f'{currency} за {days} дней')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=10))
        fig.autofmt_xdate()
        ax.grid(True, linestyle='--', alpha=0.7)

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

        self.plot_status.config(text=f'График {currency} за {days} дней')

def main():
    root = tk.Tk()
    app = CurrencyApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()