# Use the official Python base image
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./ ./app

EXPOSE 8080

CMD ["streamlit", "run", "--server.port", "8080", "--server.enableCORS", "false", "app.py"]