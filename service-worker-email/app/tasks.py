import time
from celery import Celery

# 1. Define o "celery_app" (que o worker-1 estava à procura)
celery_app = Celery(
    'tasks',
    broker='amqp://guest:guest@rabbitmq:5672//',
    backend='rpc://' 
)

# 2. Define a função (que o api-1 estava à procura)
@celery_app.task(name="enviar_email_simulado")
def enviar_email_simulado(email: str, assunto: str):
    """
    Uma tarefa que simula o envio de um e-mail "dormindo" por 2 segundos.
    """
    print(f"Iniciando envio de e-mail para: {email}...")
    
    # Simula um trabalho demorado (ex: chamada de API do SendGrid)
    time.sleep(2) 
    
    print(f"E-mail para {email} com assunto '{assunto}' enviado com SUCESSO.")
    return f"E-mail enviado para {email}"