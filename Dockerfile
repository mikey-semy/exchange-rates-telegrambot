FROM python:3.11-slim

COPY requirements.txt /app/

# Установка зависимостей
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# Копирование кода бота
COPY . /app

CMD ["python", "-m", "./app/bot/__main__.py"]