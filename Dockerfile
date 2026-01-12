FROM python:3.11-slim

WORKDIR /app

# System deps for some packages (e.g., libomp for xgboost)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libomp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 5000

CMD ["gunicorn", "web.app:app", "--bind", "0.0.0.0:5000", "--workers", "2"]
