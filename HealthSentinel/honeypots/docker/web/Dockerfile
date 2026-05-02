# HealthSentinel Honeypot - Web Portal
FROM python:3.9-slim

WORKDIR /app

RUN pip install flask requests

COPY honey_web.py .

EXPOSE 5000

CMD ["python", "honey_web.py"]
