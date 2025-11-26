from fastapi import FastAPI
# Importação corrigida (sem ponto)
from tasks import enviar_email_simulado # Importa nossa tarefa

app = FastAPI(title="Disparador de Tarefas")

@app.get("/")
def home():
    return {"status": "API do Produtor está online. Acesse /docs para testar."}


@app.post("/disparar-campanha-emails", status_code=202)
def disparar_campanha(
    assunto: str = "Sua Fatura Chegou!", 
    total_emails: int = 100
):
    """
    Este endpoint enfileira 'total_emails' tarefas de envio.
    Ele retorna IMEDIATAMENTE.
    """
    
    print(f"Enfileirando {total_emails} e-mails...")
    
    for i in range(total_emails):
        email_destino = f"cliente_{i+1}@empresa.com"
        
        enviar_email_simulado.delay(
            email=email_destino, 
            assunto=f"{assunto} [ID:{i+1}]"
        )
        
    print("Todas as tarefas foram enfileiradas!")
    return {
        "status": "Aceito",
        "mensagem": f"{total_emails} tarefas de envio de e-mail foram enfileiradas."
    }