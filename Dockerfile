FROM python:3.13-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py index.html PRIVACY.md TERMS.md favicon.svg apple-touch-icon.png icon-192.png icon-512.png manifest.webmanifest ./
RUN mkdir -p /app/data
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--timeout", "45", "app:app"]
