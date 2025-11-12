# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set environment variables for Chrome and ChromeDriver
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libffi-dev \
    chromium-browser \
    chromium-chromedriver \
    wget \
    unzip \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Set display port to avoid crash
ENV DISPLAY=:99

# Set working directory
WORKDIR /app

# Copy and install requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port Gunicorn will run on
EXPOSE 10000

# Set the command to run the application
CMD ["gunicorn", "--worker-class", "gevent", "--bind", "0.0.0.0:10000", "app:app"]