FROM python:3.11-slim-bullseye

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    STATIC_ROOT=/app/static/

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first to leverage Docker cache
COPY pyproject.toml .
COPY swotting/ swotting/
COPY manage.py .

# Install Python dependencies
RUN python -m pip install --upgrade pip && \
    python -m pip install -e .

# Now copy the rest of your project files
COPY . .

# Collect static files
RUN if [ -n "$ALGOLIA_APP_ID" ] && [ -n "$ALGOLIA_API_KEY" ]; then \
        python manage.py collectstatic --no-input; \
    else \
        echo "Skipping collectstatic due to missing Algolia credentials"; \
    fi

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "--timeout", "120", "--capture-output", "swotting.wsgi"]