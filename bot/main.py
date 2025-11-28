from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from celery import Celery
from datetime import datetime
import os
import requests

app = FastAPI(title="Gateway de E-mail Inteligente")

# Permite que o HTML aceda à API (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações
MONGO_URL = "mongodb://mongo:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client.atendimento_db
sessions_collection = db.sessoes      # Guarda o estado atual da conversa
historico_collection = db.historico   # Guarda as mensagens para o Inbox

# Configuração do Celery (Conecta ao RabbitMQ para enviar tarefas)
celery_app = Celery('bot_sender', broker='amqp://guest:guest@rabbitmq:5672//')

# Árvore de Decisão
ARVORE = {
    "inicio": {
        "texto": "Olá! Recebemos o seu e-mail. Já é nosso cliente? (Responda: 1. Sim / 2. Não)",
        "opcoes": {"1": "pergunta_plano", "2": "oferta_cadastro"}
    },
    "oferta_cadastro": {
        "texto": "Gostaria de criar um cadastro? (1. Sim / 2. Não)",
        "opcoes": {"1": "encaminhar_VENDAS", "2": "fim_conversa"}
    },
    "pergunta_plano": {
        "texto": "Qual é o seu plano atual? (1. Básico / 2. Premium)",
        "opcoes": {"1": "menu_opcoes", "2": "menu_opcoes"}
    },
    "menu_opcoes": {
        "texto": "O que deseja? (1. Mudar Plano / 2. Problema Técnico)",
        "opcoes": {"1": "oferta_upgrade", "2": "encaminhar_SUPORTE"}
    },
    "oferta_upgrade": {
        "texto": "Aceita o Plano Turbo? (1. Sim / 2. Não)",
        "opcoes": {"1": "encaminhar_FINANCEIRO", "2": "recusa_oferta"}
    }
}

class EmailEntrada(BaseModel):
    remetente: str
    texto: str

def enviar_resposta_por_email(para_quem: str, texto_resposta: str):
    celery_app.send_task(
        'enviar_email_simulado',
        args=[para_quem, "Re: Atendimento Operadora", texto_resposta]
    )

def notificar_marketing(email_cliente: str):
    """Chama o serviço de Marketing na porta 8002"""
    try:
        print(f"--- [BOT] Avisando Marketing sobre recusa de {email_cliente} ---")
        requests.post("http://marketing_service:8002/evento-recusa", json={"email": email_cliente}, timeout=2)
    except Exception as e:
        print(f"Erro ao contactar marketing: {e}")

async def registrar_mensagem(email: str, texto: str, origem: str):
    doc = {
        "email": email,
        "texto": texto,
        "origem": origem,
        "data": datetime.now()
    }
    await historico_collection.insert_one(doc)

async def realizar_transbordo(email_cliente: str, departamento: str):
    historico = []
    async for h in historico_collection.find({"email": email_cliente}).sort("data", 1):
        quem = "CLIENTE" if h['origem'] == 'cliente' else "BOT"
        linha = f"[{h['data']}] {quem}: {h['texto']}"
        historico.append(linha)
    
    resumo = "\n".join(historico)
    
    corpo_email_funcionario = f"NOVO CHAMADO: {departamento}\n\nHISTÓRICO:\n{resumo}"
    email_funcionario = f"atendimento.{departamento.lower()}@operadora.com"
    
    celery_app.send_task(
        'enviar_email_simulado',
        args=[email_funcionario, f"Ticket: {email_cliente}", corpo_email_funcionario]
    )
    
    # Salva no banco com o email do funcionário para aparecer no Painel de Tickets
    await registrar_mensagem(email_funcionario, corpo_email_funcionario, "sistema_transbordo")
    
    msg_final = f"O seu caso foi passado para o departamento {departamento}. Um humano responderá em breve."
    enviar_resposta_por_email(email_cliente, msg_final)
    await registrar_mensagem(email_cliente, msg_final, "bot")

# Endpoints
@app.post("/webhook-email")
async def receber_email(email: EmailEntrada, background_tasks: BackgroundTasks):
    cliente_email = email.remetente
    texto_usuario = email.texto.strip()

    await registrar_mensagem(cliente_email, texto_usuario, "cliente")

    sessao = await sessions_collection.find_one({"cliente_id": cliente_email})
    
    if not sessao:
        await sessions_collection.insert_one({"cliente_id": cliente_email, "estado": "inicio"})
        resposta = ARVORE["inicio"]["texto"]
        enviar_resposta_por_email(cliente_email, resposta)
        await registrar_mensagem(cliente_email, resposta, "bot")
        return {"status": "ok"}

    estado_atual = sessao["estado"]
    no_atual = ARVORE.get(estado_atual)
    proximo_estado = no_atual["opcoes"].get(texto_usuario)

    if not proximo_estado:
        resposta = "Não entendi a sua resposta. \n" + no_atual["texto"]
        enviar_resposta_por_email(cliente_email, resposta)
        await registrar_mensagem(cliente_email, resposta, "bot")
        return {"status": "erro_validacao"}

    if proximo_estado.startswith("encaminhar_"):
        dept = proximo_estado.replace("encaminhar_", "")
        await realizar_transbordo(cliente_email, dept)
        await sessions_collection.delete_one({"cliente_id": cliente_email})
        return {"status": "transbordo"}
    
    elif proximo_estado == "fim_conversa":
        msg = "Atendimento finalizado. Obrigado!"
        enviar_resposta_por_email(cliente_email, msg)
        await registrar_mensagem(cliente_email, msg, "bot")
        await sessions_collection.delete_one({"cliente_id": cliente_email})
        return {"status": "fim"}

    elif proximo_estado == "recusa_oferta":
        msg = "Que pena! Mas entendemos. Se precisar de algo, estamos aqui."
        enviar_resposta_por_email(cliente_email, msg)
        await registrar_mensagem(cliente_email, msg, "bot")
        print(f"--- [BOT DEBUG] Enviando tarefa para fila 'marketing_queue' para: {cliente_email} ---")
        celery_app.send_task(
            'marketing.processar_recusa',  
            args=[cliente_email],
            queue='marketing_queue'        
        )
        await sessions_collection.delete_one({"cliente_id": cliente_email})
        return {"status": "fim_com_marketing"}

    await sessions_collection.update_one({"cliente_id": cliente_email}, {"$set": {"estado": proximo_estado}})
    
    resposta = ARVORE[proximo_estado]["texto"]
    enviar_resposta_por_email(cliente_email, resposta)
    await registrar_mensagem(cliente_email, resposta, "bot")
    
    return {"status": "ok"}

@app.get("/inbox/{email}")
async def get_inbox(email: str):
    msgs = []
    async for m in historico_collection.find({"email": email}).sort("data", -1):
        m["_id"] = str(m["_id"])
        msgs.append(m)
    return msgs

@app.get("/reset/{email}")
async def reset(email: str):
    await sessions_collection.delete_one({"cliente_id": email})
    await historico_collection.delete_many({"email": email})
    return {"msg": "Resetado"}

@app.get("/limpar-tudo")
async def limpar_tudo():
    """Endpoint usado pelos botões de pânico (Webmail e Tickets)"""
    await sessions_collection.delete_many({})
    await historico_collection.delete_many({})
    return {"msg": "Banco de dados 100% limpo! Pronto para apresentação."}

@app.get("/painel-tickets", response_class=HTMLResponse)
async def ver_todos_tickets():
    cards_html = ""
    # Busca e-mails de funcionários (que começam com 'atendimento.')
    async for m in historico_collection.find({"email": {"$regex": "^atendimento\."}}).sort("data", -1):
        data_str = m['data'].strftime("%d/%m/%Y %H:%M")
        texto_html = m['texto'].replace("\n", "<br>") if m.get('texto') else "(Sem conteúdo)"
        
        card = f"""
        <div class="ticket">
            <div class="ticket-header">
                <span class="destinatario">📥 {m.get('email', 'Sem Destinatário')}</span>
                <span class="data">{data_str}</span>
            </div>
            <div class="ticket-body">{texto_html}</div>
            <div class="ticket-footer">Status: <span class="badge">Aberto</span></div>
        </div>
        """
        cards_html += card

    if not cards_html:
        cards_html = "<div style='text-align:center; color:#888; margin-top:50px;'>Nenhum chamado de suporte encontrado.</div>"

    pagina = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Painel de Chamados - Suporte</title>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 20px; }}
            h1 {{ color: #1a1a1a; text-align: center; margin-bottom: 30px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .ticket {{ background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; overflow: hidden; border-left: 5px solid #e74c3c; }}
            .ticket-header {{ background: #f8f9fa; padding: 15px 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }}
            .destinatario {{ font-weight: bold; color: #2c3e50; font-size: 1.1em; }}
            .data {{ color: #7f8c8d; font-size: 0.9em; }}
            .ticket-body {{ padding: 20px; color: #34495e; line-height: 1.6; font-family: Consolas, "Courier New", monospace; background-color: #fff; }}
            .ticket-footer {{ padding: 10px 20px; background: #f8f9fa; border-top: 1px solid #eee; text-align: right; font-size: 0.9em; color: #555; }}
            .badge {{ background: #2ecc71; color: white; padding: 3px 10px; border-radius: 15px; font-size: 0.8em; font-weight: bold; }}
            .btn-container {{ display: flex; justify-content: center; gap: 10px; margin-bottom: 20px; }}
            .refresh-btn {{ display: inline-block; width: 200px; padding: 10px; background: #3498db; color: white; text-align: center; text-decoration: none; border-radius: 5px; font-weight: bold; cursor: pointer; border: none; }}
            .refresh-btn:hover {{ background: #2980b9; }}
            .clear-btn {{ display: inline-block; width: 200px; padding: 10px; background: #e74c3c; color: white; text-align: center; text-decoration: none; border-radius: 5px; font-weight: bold; cursor: pointer; border: none; }}
            .clear-btn:hover {{ background: #c0392b; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ Painel de Chamados (Funcionário)</h1>
            <div class="btn-container">
                <a href="javascript:location.reload()" class="refresh-btn">🔄 Atualizar Lista</a>
                <button onclick="limparTudo()" class="clear-btn">⚠️ Limpar Tudo</button>
            </div>
            {cards_html}
        </div>
        <script>
            async function limparTudo() {{
                if(!confirm("Tem certeza que deseja apagar TODOS os registos? Esta ação não pode ser desfeita.")) return;
                try {{
                    await fetch('/limpar-tudo');
                    alert("Sistema limpo com sucesso!");
                    location.reload();
                }} catch (e) {{ alert("Erro ao limpar sistema."); }}
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=pagina)

if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")