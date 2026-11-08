FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    "fastapi>=0.100.0" \
    "uvicorn[standard]>=0.30.0" \
    "python-dotenv>=1.0.0" \
    "email-validator>=2.0.0" \
    "psycopg[binary]>=3.1.0" \
    "sqlalchemy>=2.0.0"

COPY postgress-infra/main.py ./main.py
COPY web ./web

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
