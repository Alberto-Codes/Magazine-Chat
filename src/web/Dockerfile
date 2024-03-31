# Use the official Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/web/ ./

# Expose the port the app runs on
EXPOSE 8080

# Run the application
CMD ["streamlit", "run", "--server.port", "8080", "--server.enableCORS", "false", "app.py"]