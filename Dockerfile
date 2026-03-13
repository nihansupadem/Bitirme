FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV APACHE_RUN_USER=www-data
ENV APACHE_RUN_GROUP=www-data
ENV APACHE_LOG_DIR=/var/log/apache2
ENV APACHE_PID_FILE=/var/run/apache2.pid
ENV APACHE_RUN_DIR=/var/run/apache2
ENV APACHE_LOCK_DIR=/var/lock/apache2

# ── System packages ────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    apache2 \
    php8.1 \
    php8.1-sqlite3 \
    php8.1-curl \
    php8.1-mbstring \
    libapache2-mod-php8.1 \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Python ML packages ─────────────────────────────────────────────────────────
RUN pip3 install --no-cache-dir \
    numpy \
    pandas \
    scikit-learn \
    "tensorflow-cpu<2.16" \
    yfinance \
    requests \
    hmmlearn \
    matplotlib \
    Pillow \
    curl_cffi

# ── Apache: listen on port 7860 (HuggingFace requirement) ─────────────────────
RUN sed -i 's/Listen 80/Listen 7860/' /etc/apache2/ports.conf

# ── Apache virtualhost config ──────────────────────────────────────────────────
COPY apache-hf.conf /etc/apache2/sites-available/000-default.conf

# ── Enable modules ─────────────────────────────────────────────────────────────
RUN a2enmod rewrite php8.1

# ── Copy project files ─────────────────────────────────────────────────────────
# backend/ → /var/www/html/
#   frontend/  → /var/www/html/frontend/   (PHP site)
#   train_model.py → /var/www/html/train_model.py
COPY backend/ /var/www/html/

# ── Writable directories ───────────────────────────────────────────────────────
# cache/  — CSV price cache written by train_model.py (BASE_DIR/cache)
# db      — directory for SQLite database (config.php → __DIR__/../../optrade.db)
RUN mkdir -p /var/www/html/cache && \
    chown -R www-data:www-data /var/www/html && \
    chmod -R 755 /var/www/html && \
    chmod 777 /var/www/html/cache && \
    chmod 777 /var/www/html

EXPOSE 7860

CMD ["apache2ctl", "-D", "FOREGROUND"]
