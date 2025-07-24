FROM python:3.10-slim

# Install minimal dependencies
RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium \
    curl \
    fonts-liberation \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxss1 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libdbus-glib-1-2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment for Chromium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver

# Set work directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

CMD ["python", "app.py"]