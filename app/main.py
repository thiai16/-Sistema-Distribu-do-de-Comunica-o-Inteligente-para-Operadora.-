from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.tasks import enviar_email_simulado 

app = FastAPI(title="Central de Controle Distribuída")

@app.get("/", response_class=HTMLResponse)
def dashboard_administrativo():
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sistemas Distribuídos - Painel Master</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }
            .header { text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #e1e4e8; }
            .grid-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 25px; max-width: 1400px; margin: 0 auto; }
            .card { background: white; border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 5px solid #bdc3c7; transition: transform 0.2s; display: flex; flex-direction: column; justify-content: space-between; }
            .card:hover { transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
            .card h2 { margin-top: 0; font-size: 1.4em; }
            .card-client { border-top-color: #2ecc71; }
            .card-infra { border-top-color: #e67e22; }
            .card-manager { border-top-color: #3498db; }
            .card-support { border-top-color: #9b59b6; } /* Roxo para Suporte */
            .btn { display: block; width: 100%; padding: 12px 0; margin-top: 15px; text-align: center; border-radius: 6px; text-decoration: none; font-weight: bold; border: none; cursor: pointer; color: white; transition: opacity 0.2s; }
            .btn:hover { opacity: 0.9; }
            .btn-green { background-color: #2ecc71; }
            .btn-orange { background-color: #e67e22; }
            .btn-blue { background-color: #3498db; }
            .btn-purple { background-color: #9b59b6; }
            input { width: 100%; padding: 10px; margin: 5px 0 15px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            .status-tag { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; background: #eee; color: #555; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📡 Central de Controle - Operadora</h1>
            <p>Gerenciamento de Microsserviços e Processamento Paralelo</p>
        </div>

        <div class="grid-container">
            <div class="card card-client">
                <div>
                    <h2>💬 Portal do Cliente <span class="status-tag">Porta 8001</span></h2>
                    <p>Interface onde o cliente conversa com o Chatbot.</p>
                </div>
                <a href="http://localhost:8001/" target="_blank" class="btn btn-green">Abrir Chat do Cliente</a>
            </div>

            <div class="card card-infra">
                <div>
                    <h2>⚙️ Monitoramento (Flower) <span class="status-tag">Porta 5555</span></h2>
                    <p>Veja o paralelismo e o consumo de filas em tempo real.</p>
                </div>
                <a href="http://localhost:5555" target="_blank" class="btn btn-orange">Abrir Painel Flower</a>
            </div>

            <div class="card card-manager">
                <h2>🚀 Disparador de Campanhas</h2>
                <p>Envie tarefas em massa para os Workers.</p>
                <div id="status-msg" style="margin-bottom: 10px; font-size: 0.9em; min-height: 20px;"></div>
                <input type="text" id="assunto" value="Oferta Exclusiva!">
                <input type="number" id="qtd" value="100">
                <button onclick="disparar()" class="btn btn-blue">Iniciar Processamento Paralelo</button>
            </div>

            <div class="card card-support">
                <div>
                    <h2>🛡️ Painel de Chamados <span class="status-tag">Suporte</span></h2>
                    <p>Área dos funcionários para ver tickets gerados pelo Bot.</p>
                    <p style="font-size:0.85em; color:#777;">(O Marketing roda oculto reagindo a recusas e gerando tickets aqui)</p>
                </div>
                <a href="http://localhost:8001/painel-tickets" target="_blank" class="btn btn-purple">Acessar Lista de Chamados</a>
            </div>
        </div>

        <script>
            async function disparar() {
                const assunto = document.getElementById("assunto").value;
                const qtd = document.getElementById("qtd").value;
                const btn = document.querySelector(".btn-blue");
                const status = document.getElementById("status-msg");
                btn.disabled = true; btn.innerText = "Enviando...";
                try {
                    const response = await fetch(`/disparar-campanha-emails?assunto=${encodeURIComponent(assunto)}&total_emails=${qtd}`, { method: "POST" });
                    const data = await response.json();
                    status.innerHTML = `<span style='color:green'>✅ ${data.mensagem}</span>`;
                } catch (e) { status.innerHTML = "<span style='color:red'>❌ Erro.</span>"; } 
                finally { btn.disabled = false; btn.innerText = "Iniciar Processamento Paralelo"; }
            }
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/disparar-campanha-emails", status_code=202)
def disparar_campanha(assunto: str = "Sua Fatura", total_emails: int = 100):
    for i in range(total_emails):
        enviar_email_simulado.delay(f"cliente_{i+1}@empresa.com", f"{assunto} [ID:{i+1}]", "Conteúdo...")
    return {"mensagem": f"Sucesso! {total_emails} tarefas enviadas."}