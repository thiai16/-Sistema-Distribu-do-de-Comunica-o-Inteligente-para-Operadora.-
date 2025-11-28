from fastapi import FastAPI, Body
from celery import Celery
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import asyncio

app = FastAPI(title="Serviço de Automação de Marketing")

# 1. Configuração do Banco (Para o email aparecer na tela do simulador)
MONGO_URL = "mongodb://mongo:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client.atendimento_db
historico_collection = db.historico

# 2. Configuração do Celery (Para mandar a ordem para o Worker real)
celery_app = Celery('marketing_sender', broker='amqp://guest:guest@rabbitmq:5672//')

async def salvar_no_visual(email_cliente, texto):
    """Salva a mensagem no banco para aparecer no site simulado (Webmail)"""
    doc = {
        "email": email_cliente,
        "texto": texto,
        "origem": "bot", # Aparece como vindo da Operadora
        "data": datetime.now()
    }
    await historico_collection.insert_one(doc)

@app.post("/evento-recusa")
async def processar_recusa(dados: dict = Body(...)):
    """
    Recebe o aviso do Bot de que um cliente recusou a oferta.
    Inicia a estratégia de recuperação (Win-back).
    """
    email_cliente = dados.get("email")
    print(f"--- [MARKETING] Cliente {email_cliente} recusou. Agendando estratégia... ---")

    # O conteúdo do e-mail de marketing
    assunto = "Psiu... mudou de ideia? 🎁"
    corpo = "Olá! Vimos que recusou o Turbo. Que tal 20% de desconto nos 3 primeiros meses? Responda QUERO20 para ativar!"

    # 1. Agenda o envio real no Worker (bastidores)
    # countdown=10 faz o worker esperar 10 segundos antes de enviar
    celery_app.send_task(
        'enviar_email_simulado',
        args=[email_cliente, assunto, corpo],
        countdown=10 
    )

    # 2. Agenda a aparição no Site Visual (Simulação)
    # Esperamos 10s aqui também para simular o tempo real do marketing agir na tela
    await asyncio.sleep(10) 
    await salvar_no_visual(email_cliente, f"[MARKETING] {corpo}")

    return {"status": "Estratégia executada com sucesso"}