# HealthSentinel Honeypot - SQL
FROM python:3.9-slim

WORKDIR /app

RUN pip install requests

COPY honey_sql.py .

EXPOSE 5432

CMD ["python", "honey_sql.py"]
