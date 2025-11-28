from celery import Celery
from pymongo import MongoClient
from datetime import datetime
import time

# Configuração do Celery
celery_app = Celery(
    'marketing_worker',
    broker='amqp://guest:guest@rabbitmq:5672//',
    backend='rpc://'
)

celery_app.conf.task_routes = {
    'marketing.processar_recusa': {'queue': 'marketing_queue'},
}

try:
    # Conecta no MongoDB do Docker
    mongo_client = MongoClient("mongodb://mongo:27017")
    
    
    db = mongo_client.atendimento_db 
    historico_collection = db.historico
    print("--- [MARKETING] Conectado ao banco 'bot_db' com sucesso! ---")
except Exception as e:
    print(f"--- [ERRO] Não conectou no Mongo: {e}")

@celery_app.task(name="marketing.processar_recusa")
def processar_recusa_task(email_cliente):

    # Simula um pequeno atraso para parecer natural (1 segundo)
    time.sleep(10)

    assunto = "Psiu... mudou de ideia? 🎁"
    corpo = (
        "Olá! Vimos que você não aceitou o Plano Turbo.\n\n"
        "Temos uma contraproposta: 20% de desconto por 3 meses!\n"
        "Responda 'QUERO20' para ativar."
    )

    msg_doc = {
        "email": email_cliente,
        "texto": f"Assunto: {assunto}\n\n{corpo}",
        "origem": "bot", 
        "data": datetime.now()
    }
    
    try:
        historico_collection.insert_one(msg_doc)
        print(f"✅ [MARKETING] Mensagem gravada no banco para {email_cliente}")
    except Exception as e:
        print(f"❌ [ERRO] Falha ao gravar no banco: {e}")

    # Envia log para o Worker de Email (apenas para registro/paralelismo)
    celery_app.send_task(
        'enviar_email_simulado',
        args=[email_cliente, assunto, corpo],
        queue='celery'
    )
    
    return "Estratégia Finalizada"