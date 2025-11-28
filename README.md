# 📡 Sistema Distribuído de Comunicação Inteligente para Operadora

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-Messaging-orange?style=for-the-badge&logo=rabbitmq)
![Celery](https://img.shields.io/badge/Celery-Distributed_Task_Queue-green?style=for-the-badge&logo=celery)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-47A248?style=for-the-badge&logo=mongodb)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?style=for-the-badge&logo=fastapi)

> **Disciplina:** Computação Paralela e Distribuída  
> **Professor:** Paulo Alexandre Bressan  
> **Autores:** João Victor Fernandes Rocha & Thiago Aquino Guedes Barbosa
> Um sistema de microsserviços para orquestração de atendimento, marketing e disparo de e-mails em massa utilizando arquitetura orientada a eventos.

---

## 📋 Sobre o Projeto

Este projeto simula o ecossistema de comunicação de uma Operadora de Telefonia. O objetivo é demonstrar na prática conceitos de **Sistemas Distribuídos**, **Processamento Paralelo** e **Comunicação Assíncrona**.

Diferente de uma aplicação monolítica, este sistema é dividido em microsserviços independentes que se comunicam através de um Broker de Mensagens (RabbitMQ), garantindo desacoplamento, resiliência e escalabilidade.

### 🚀 Principais Funcionalidades

1.  **Processamento Paralelo (Workers):** Disparo de milhares de e-mails simulados distribuídos entre múltiplos workers simultâneos.
2.  **Atendimento Automatizado (Bot):** Chatbot com árvore de decisão para triagem de clientes.
3.  **Marketing Reativo (Event-Driven):** Um serviço "invisível" que escuta eventos de recusa de oferta e, após um *cooldown*, envia uma contraproposta automática.
4.  **Monitoramento em Tempo Real:** Painel para visualizar filas, tarefas e saúde dos nós.

---

## 🏗️ Arquitetura

O sistema é composto pelos seguintes containers Docker:

| Serviço | Porta | Descrição |
| :--- | :--- | :--- |
| **Dashboard (Manager)** | `8000` | Painel central administrativo. Gerencia campanhas e monitora o sistema. |
| **Bot (Client)** | `8001` | Interface de chat para o cliente final. Comunica-se com o Marketing via filas. |
| **Marketing Worker** | `N/A` | Microsserviço de background. Escuta a fila `marketing_queue`, processa lógica de retenção (Win-back) e grava no banco. |
| **Worker E-mails** | `N/A` | Instâncias escaláveis do Celery responsáveis pelo processamento pesado (envio de e-mails). |
| **RabbitMQ** | `5672` | Broker de mensagens que orquestra a comunicação assíncrona. |
| **MongoDB** | `27017` | Banco de dados NoSQL para persistência de histórico e sessões. |
| **Flower** | `5555` | Ferramenta visual para monitoramento dos workers Celery. |

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.10
* **Framework Web:** FastAPI
* **Filas & Tarefas:** Celery + RabbitMQ
* **Banco de Dados:** MongoDB (Motor)
* **Containerização:** Docker & Docker Compose
* **Frontend:** HTML5/JS (Integrado via StaticFiles)

---

## ⚙️ Como Rodar o Projeto

### Pré-requisitos
* [Docker](https://www.docker.com/) e Docker Compose instalados.

### Passo a Passo

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/nome-do-repo.git](https://github.com/seu-usuario/nome-do-repo.git)
    cd nome-do-repo
    ```

2.  **Suba os containers (com build):**
    ```bash
    docker-compose up --build --scale worker_emails=2
    ```
    *A flag `--scale worker_emails=2` inicia duas instâncias do worker de e-mail para demonstrar o paralelismo.*

3.  **Aguarde a inicialização:**
    Espere até ver os logs indicando que os workers estão conectados ao RabbitMQ (`[INFO/MainProcess] Connected to amqp://...`).

---

## 🧪 Roteiro de Testes (Uso)

Para validar os requisitos do projeto, siga este roteiro:

### 1. Acessar o Painel Central
Abra **[http://localhost:8000](http://localhost:8000)**.
Aqui você tem a visão geral de todos os microsserviços.

### 2. Testar Paralelismo (Disparo em Massa)
1.  No Painel Central, vá em **"Disparador de Campanhas"**.
2.  Defina 200 e-mails e clique em **"Iniciar Processamento Paralelo"**.
3.  Abra o **Flower** em [http://localhost:5555](http://localhost:5555).
4.  **Resultado:** Observe no gráfico que as tarefas são distribuídas simultaneamente entre os múltiplos workers (`worker_emails-1`, `worker_emails-2`).

### 3. Testar Sistema Distribuído (Fluxo de Marketing)
1.  No Painel Central, clique em **"Abrir Chat do Cliente"** (ou vá para [http://localhost:8001](http://localhost:8001)).
2.  Use o botão vermelho **"🗑️ Limpar Conversa"** na lateral.
3.  Interaja com o Bot simulando uma recusa:
    * *Você já é cliente?* -> **1** (Sim)
    * *Deseja Upgrade?* -> **1** (Sim)
    * *Aceita o Plano Turbo?* -> **2** (Não - Recusa)
4.  O Bot encerrará a conversa.
5.  Clique em **"🔄 Atualizar"**. Nada acontecerá imediatamente (Simulação de tempo de análise).
6.  Aguarde **10 segundos** (Cooldown do Marketing).
7.  Clique em **"🔄 Atualizar"** novamente.
8.  **Resultado:** O microsserviço de Marketing (que roda isolado) injetou uma contraproposta de 20% de desconto na caixa de entrada do cliente.

---

## 📂 Estrutura de Pastas

```bash
├── app/                  # Microsserviço 1: Dashboard e API de Campanhas
│   ├── main.py           # Dashboard Central
│   └── tasks.py          # Definição das tarefas do Celery
├── bot/                  # Microsserviço 2: Chatbot e Interface do Cliente
│   ├── main.py           # Lógica da Árvore de Decisão
│   └── static/           # Frontend (HTML/CSS/JS)
├── marketing/            # Microsserviço 3: Worker de Retenção
│   └── main.py           # Lógica de Win-back e Cooldown
├── docker-compose.yml    # Orquestração dos containers
├── Dockerfile            # Imagem base
└── requirements.txt      # Dependências Python# Sistema Distribuído de Comunicação Inteligente para Operadora 
