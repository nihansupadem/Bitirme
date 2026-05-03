FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Setup permissions for Hugging Face Spaces
# Hugging Face Spaces runs containers with user ID 1000
RUN useradd -m -u 1000 user && \
    mkdir -p /app/cache && \
    chown -R user:user /app && \
    chmod -R 777 /app/cache

USER user

# Expose port 7860 (Hugging Face default)
EXPOSE 7860

# Start the Flask app using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:7860", "--timeout", "360", "app:app"]
