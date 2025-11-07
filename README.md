# Sistema Distribuído de Comunicação Inteligente para Operadora 

Projeto de implementação de um sistema distribuído para gerenciamento de comunicação em larga escala (e-mail e chat) para operadoras, utilizando conceitos de paralelismo e arquitetura de microserviços

**Autores:**
* João Victor Fernandes Rocha 
* Thiago Aquino Guedes Barbosa 

**Orientador:**
* Prof. Paulo Alexandre Bressan 

---

## 🎯 Objetivo Geral

Projetar, implementar e avaliar um protótipo de sistema distribuído inteligente, baseado em microserviços, capaz de gerenciar de forma escalável, paralela e resiliente todo o fluxo de comunicação automatizada (e-mail e chat) entre uma operadora de serviços e seus clientes.

### Objetivos Específicos

* **Modelar a Arquitetura:** Definir os limites e as APIs de cada microserviço.
* **Gerenciamento de Tarefas:** Desenvolver o núcleo do sistema com uma fila de tarefas para orquestrar tarefas assíncronas.
* **Workers Paralelos:** Criar *workers* de e-mail que possam ser escalados horizontalmente (ex: via Docker) para processar lotes em paralelo.
* **Bot de Atendimento:** Implementar o serviço de chat interativo de baixa latência.
* **Validar Escalabilidade:** Realizar testes de carga para medir o ganho de desempenho ao adicionar mais *workers*.
* **Integrar Serviços:** Garantir a comunicação entre os serviços de automação e execução.

---

## 🛠️ Arquitetura Proposta

A solução utiliza uma arquitetura de microserviços  [cite_start]com comunicação primariamente assíncrona via mensageria (como RabbitMQ) e APIs (REST/gRPC).

O sistema será dividido nos seguintes serviços:

1.  **Bot Central (Interface e Configuração):** Ponto de entrada administrativo para configurar campanhas e consultar relatórios consolidados.
2.  **Bot de Atendimento ao Cliente:** Contato direto com cliente, oferecendo respostas automáticas e identificando problemas.
3.  **Gerenciador de Tarefas (Orquestrador):** O "cérebro" do sistema. [cite_start]Recebe solicitações, divide-as em lotes e as enfileira.
4.  **Worker de E-mail (Execução Paralela):** Consome tarefas da fila e executa o envio real dos e-mails.
5.  **Serviço de Automação de Marketing:** Analisa interações e agenda o envio automático de ofertas.
6.  **Serviço de Cadastro por E-mail:** Monitora uma caixa de entrada e processa respostas de cadastro.
7.  **Serviço de Monitoramento e Relatórios:** Coleta métricas de todos os outros serviços.

---

## 💻 Tecnologias (Stack Proposto)

* **Linguagem:** Python
* **APIs:** FastAPI 
* **Fila de Tarefas:** Celery 
* **Message Broker:** RabbitMQ 
* **Banco de Dados (Chat):** MongoDB 
* **Contêineres:** Docker (para escalar os workers) 
* **Email (Libs):** IMAP/SMTP 

---

## 📈 Resultados Esperados

* Envio de milhares de e-mails em paralelo, reduzindo o tempo de execução.
* Atendimento a múltiplos clientes simultaneamente via bot.
* [cite_start]Geração de relatórios consolidados de desempenho e faturamento[cite: 53, 54].
* [cite_start]Demonstração clara dos benefícios do paralelismo e escalabilidade[cite: 55].
