FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:create_app()"]
