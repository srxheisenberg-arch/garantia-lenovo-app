# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables for Chrome and ChromeDriver
ENV CHROME_VERSION "121.0.6167.85-1"
ENV CHROMEDRIVER_VERSION "121.0.6167.85"
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    --no-install-recommends

# Install Google Chrome
RUN wget -q https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb \
    && apt-get install -y ./google-chrome-stable_${CHROME_VERSION}_amd64.deb \
    && rm google-chrome-stable_${CHROME_VERSION}_amd64.deb

# Install ChromeDriver
RUN wget -q https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip \
    && unzip chromedriver-linux64.zip \
    && mv chromedriver-linux64/chromedriver /usr/bin/chromedriver \
    && rm chromedriver-linux64.zip \
    && rm -rf chromedriver-linux64

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
