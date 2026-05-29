# Используем официальный образ Python 3.14 (slim — облегчённая версия)
FROM python:3.14-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта
COPY . .

# Создаём папку для графиков (если будет использоваться plotter)
RUN mkdir -p charts

# Открываем порт 5000 для Flask
EXPOSE 5000

# Команда по умолчанию: запускаем веб-сервер
CMD ["python", "web.py"]