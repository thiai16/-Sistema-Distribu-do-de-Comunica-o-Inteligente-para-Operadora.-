# -Sistema-Distribu-do-de-Comunica-o-Inteligente-para-Operadora.-
# [cite_start]Sistema Distribuído de Comunicação Inteligente para Operadora 

[cite_start]Projeto de implementação de um sistema distribuído para gerenciamento de comunicação em larga escala (e-mail e chat) para operadoras, utilizando conceitos de paralelismo e arquitetura de microserviços

**Autores:**
* [cite_start]João Victor Fernandes Rocha 
* [cite_start]Thiago Aquino Guedes Barbosa 

**Orientador:**
* [cite_start]Prof. Paulo Alexandre Bressan 

---

## 🎯 Objetivo Geral

[cite_start]Projetar, implementar e avaliar um protótipo de sistema distribuído inteligente, baseado em microserviços, capaz de gerenciar de forma escalável, paralela e resiliente todo o fluxo de comunicação automatizada (e-mail e chat) entre uma operadora de serviços e seus clientes.

### Objetivos Específicos

* [cite_start]**Modelar a Arquitetura:** Definir os limites e as APIs de cada microserviço.
* [cite_start]**Gerenciamento de Tarefas:** Desenvolver o núcleo do sistema com uma fila de tarefas para orquestrar tarefas assíncronas.
* [cite_start]**Workers Paralelos:** Criar *workers* de e-mail que possam ser escalados horizontalmente (ex: via Docker) para processar lotes em paralelo.
* [cite_start]**Bot de Atendimento:** Implementar o serviço de chat interativo de baixa latência.
* [cite_start]**Validar Escalabilidade:** Realizar testes de carga para medir o ganho de desempenho ao adicionar mais *workers*.
* [cite_start]**Integrar Serviços:** Garantir a comunicação entre os serviços de automação e execução.

---

## 🛠️ Arquitetura Proposta

[cite_start]A solução utiliza uma arquitetura de microserviços  [cite_start]com comunicação primariamente assíncrona via mensageria (como RabbitMQ) e APIs (REST/gRPC).

O sistema será dividido nos seguintes serviços:

1.  [cite_start]**Bot Central (Interface e Configuração):** Ponto de entrada administrativo para configurar campanhas e consultar relatórios consolidados.
2.  [cite_start]**Bot de Atendimento ao Cliente:** Contato direto com cliente, oferecendo respostas automáticas e identificando problemas.
3.  **Gerenciador de Tarefas (Orquestrador):** O "cérebro" do sistema. [cite_start]Recebe solicitações, divide-as em lotes e as enfileira.
4.  [cite_start]**Worker de E-mail (Execução Paralela):** Consome tarefas da fila e executa o envio real dos e-mails.
5.  [cite_start]**Serviço de Automação de Marketing:** Analisa interações e agenda o envio automático de ofertas.
6.  [cite_start]**Serviço de Cadastro por E-mail:** Monitora uma caixa de entrada e processa respostas de cadastro.
7.  [cite_start]**Serviço de Monitoramento e Relatórios:** Coleta métricas de todos os outros serviços.

---

## 💻 Tecnologias (Stack Proposto)

* [cite_start]**Linguagem:** Python
* [cite_start]**APIs:** FastAPI 
* [cite_start]**Fila de Tarefas:** Celery 
* [cite_start]**Message Broker:** RabbitMQ 
* [cite_start]**Banco de Dados (Chat):** MongoDB 
* [cite_start]**Contêineres:** Docker (para escalar os workers) 
* [cite_start]**Email (Libs):** IMAP/SMTP 

---

## 📈 Resultados Esperados

* [cite_start]Envio de milhares de e-mails em paralelo, reduzindo o tempo de execução.
* [cite_start]Atendimento a múltiplos clientes simultaneamente via bot[cite: 53].
* [cite_start]Geração de relatórios consolidados de desempenho e faturamento[cite: 53, 54].
* [cite_start]Demonstração clara dos benefícios do paralelismo e escalabilidade[cite: 55].
