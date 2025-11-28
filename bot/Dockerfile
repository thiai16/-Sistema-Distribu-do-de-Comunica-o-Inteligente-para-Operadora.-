FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da pasta bot para dentro do container
COPY . .

# Comando para rodar na porta 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]