from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.tasks import enviar_email_simulado 

app = FastAPI(title="Central de Campanhas")

# --- Interface Visual (HTML/CSS) ---
@app.get("/", response_class=HTMLResponse)
def painel_operadora():
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Central de Campanhas - Operadora</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background-color: #f4f7f6; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); width: 400px; text-align: center; }
            h1 { color: #2c3e50; margin-bottom: 1.5rem; font-size: 24px; }
            .form-group { margin-bottom: 1.5rem; text-align: left; }
            label { display: block; margin-bottom: 0.5rem; color: #7f8c8d; font-weight: bold; }
            select, input { width: 100%; padding: 10px; border: 2px solid #ecf0f1; border-radius: 6px; font-size: 16px; box-sizing: border-box; }
            select:focus, input:focus { border-color: #3498db; outline: none; }
            
            button { background-color: #3498db; color: white; border: none; padding: 12px; width: 100%; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; transition: background 0.3s; }
            button:hover { background-color: #2980b9; }
            button:disabled { background-color: #bdc3c7; cursor: not-allowed; }
            
            #status { margin-top: 1.5rem; padding: 10px; border-radius: 6px; display: none; font-size: 14px; }
            .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .loading { color: #3498db; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🚀 Disparador de Massa</h1>
            
            <div class="form-group">
                <label>Selecione a Campanha:</label>
                <select id="campanha">
                    <option value="Promoção Black Friday">🖤 Promoção Black Friday</option>
                    <option value="Aviso de Fatura">💸 Aviso de Fatura Fechada</option>
                    <option value="Boas Vindas">👋 Boas Vindas aos Novos</option>
                    <option value="Manutenção Programada">⚠️ Aviso de Manutenção</option>
                </select>
            </div>

            <div class="form-group">
                <label>Quantidade de Clientes:</label>
                <input type="number" id="quantidade" value="50" min="1" max="10000">
            </div>

            <button onclick="disparar()" id="btn-enviar">Iniciar Disparo</button>
            <div id="status"></div>
        </div>

        <script>
            async function disparar() {
                const btn = document.getElementById('btn-enviar');
                const status = document.getElementById('status');
                const campanha = document.getElementById('campanha').value;
                const qtd = document.getElementById('quantidade').value;

                btn.disabled = true;
                btn.innerText = "Enfileirando...";
                status.style.display = "block";
                status.className = "loading";
                status.innerText = "Processando pedido...";

                try {
                    const response = await fetch(`/disparar-campanha-emails?assunto=${encodeURIComponent(campanha)}&total_emails=${qtd}`, {
                        method: 'POST'
                    });
                    const data = await response.json();
                    
                    status.className = "success";
                    status.innerHTML = `✅ <b>Sucesso!</b><br>${data.mensagem}<br>Os workers estão processando em segundo plano.`;
                } catch (e) {
                    status.innerText = "❌ Erro ao conectar com o servidor.";
                    status.style.backgroundColor = "#f8d7da";
                    status.style.color = "#721c24";
                } finally {
                    btn.disabled = false;
                    btn.innerText = "Iniciar Disparo";
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content

# --- API (Backend) ---
@app.post("/disparar-campanha-emails", status_code=202)
def disparar_campanha(
    assunto: str = "Sua Fatura Chegou!", 
    total_emails: int = 100
):
    """
    Enfileira 'total_emails' tarefas para serem processadas pelos Workers.
    """
    print(f"Enfileirando {total_emails} e-mails sobre '{assunto}'...")
    
    for i in range(total_emails):
        email_destino = f"cliente_{i+1}@empresa.com"
        
        # Envia a tarefa para a fila do RabbitMQ (Assíncrono)
        enviar_email_simulado.delay(
            destinatario=email_destino, 
            assunto=f"{assunto} [ID:{i+1}]",
            corpo=f"Olá! Esta é uma mensagem automática referente à campanha: {assunto}."
        )
        
    return {
        "status": "Aceito",
        "mensagem": f"{total_emails} e-mails da campanha '{assunto}' foram enviados para a fila."
    }