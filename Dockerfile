FROM python:3.10-slim

WORKDIR /app

# Copia os requisitos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# IMPORTANTE: Copia TUDO da pasta atual (incluindo a pasta 'app') para dentro do container
COPY . .

# O comando será executado pelo docker-compose, mas deixamos este padrão
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]