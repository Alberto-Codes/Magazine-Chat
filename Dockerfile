FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/app/ ./app
COPY src/run.py .
COPY src/data/ ./app/data/

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "--timeout", "200", "--threads", "8", "app:create_app()"]