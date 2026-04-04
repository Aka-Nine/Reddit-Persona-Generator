# Reddit Persona Generator — container image
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY config.py main.py server.py ./
COPY src/ ./src/
COPY utils/ ./utils/
COPY templates/ ./templates/
COPY static/ ./static/

RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)" \
    && python -c "import nltk; nltk.download('punkt_tab', quiet=True)" 2>/dev/null || true

EXPOSE 8080

# Long timeout: scraping + LLM can exceed 30s. PORT is set by many hosts at runtime.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT} --workers 2 --threads 2 --timeout 180 --graceful-timeout 30 --access-logfile - --error-logfile - server:app"]
