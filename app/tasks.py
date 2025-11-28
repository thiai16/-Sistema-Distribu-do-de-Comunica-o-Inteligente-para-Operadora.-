import time
from celery import Celery

# Configuração do Celery
celery_app = Celery(
    'tasks',
    broker='amqp://guest:guest@rabbitmq:5672//',
    backend='rpc://' 
)

@celery_app.task(name="enviar_email_simulado")
def enviar_email_simulado(destinatario: str, assunto: str, corpo: str):
    """
    Tarefa que simula o envio de e-mail.
    """
    print(f"--- [WORKER EMAIL] Iniciando envio SMTP ---")
    print(f"PARA: {destinatario}")
    print(f"ASSUNTO: {assunto}")
    print(f"CORPO: {corpo}")
    print(f"-------------------------------------------")
    
    # Simula o tempo de conexão e envio (2 segundos)
    time.sleep(2) 
    
    return f"E-mail enviado com sucesso para {destinatario}"