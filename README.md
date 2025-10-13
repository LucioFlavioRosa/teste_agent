# Agent-Vinna: Agente de IA para Análise de Código

Este projeto implementa um agente de Inteligência Artificial especializado na análise automatizada de código-fonte, incluindo revisão de segurança (pentest), design e melhores práticas. A solução expõe uma API RESTful baseada em Flask, integrando agentes especializados e adaptadores para LLMs (Large Language Models) e ferramentas de leitura de repositórios GitHub.

## Sumário
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração de Ambiente](#configuração-de-ambiente)
- [Como Executar](#como-executar)
- [Exemplo de Uso da API](#exemplo-de-uso-da-api)
- [Como Rodar os Testes](#como-rodar-os-testes)
- [Gestão de Release](#gestão-de-release)
- [Contribuição](#contribuição)
- [Licença](#licença)

## Arquitetura

- **API Flask**: expõe endpoints REST para análise de código.
- **Agents**: agentes especializados para diferentes tipos de análise (design, segurança, pentest).
- **Infrastructure**: adaptadores para provedores LLM (ex: OpenAI).
- **Tools**: utilitários para leitura de repositórios GitHub e prompts customizados.

Fluxo principal: requisição → agente_revisor → providers → ferramentas → resposta estruturada.

## Pré-requisitos
- Python 3.8+
- Git
- Conta e chave de API OpenAI
- Token de acesso ao GitHub (para análises em repositórios privados)

## Instalação

bash
git clone https://github.com/LucioFlavioRosa/agent-vinna.git
cd agent-vinna
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt


## Configuração de Ambiente

Crie um arquivo `.env` na raiz do projeto, baseado em `.env.example`:

bash
cp .env.example .env


Edite o arquivo `.env` e preencha as variáveis:
- `OPENAI_API_KEY`: sua chave da API OpenAI
- `GITHUB_TOKEN`: token de acesso ao GitHub
- `FLASK_ENV`: development ou production
- `FLASK_DEBUG`: True ou False

## Como Executar

bash
python teste_git_hub.py


Ou diretamente com Flask:

bash
export FLASK_APP=teste_git_hub.py
flask run


A API estará disponível em `http://localhost:5000`.

## Exemplo de Uso da API

Endpoint principal: `POST /executar_analise`

**Payload JSON:**

{
  "tipo_analise": "pentest",
  "repositorio": "usuario/repositorio",
  "codigo": "<opcional>",
  "instrucoes_extras": "<opcional>"
}


**Resposta:**

{
  "resultado": "<relatório da análise>"
}


## Como Rodar os Testes

(Adicione aqui instruções de execução dos testes automatizados, se disponíveis. Exemplo:)

bash
pytest tests/


## Gestão de Release

- **Release Train:** As implantações em produção ocorrem quinzenalmente, sempre às terças-feiras entre 22:00 e 23:00 (horário de Brasília).
- **Change Approval Board (CAB):** Toda release para produção requer aprovação do CAB, que se reúne às segundas-feiras. O Tech Lead do projeto deve apresentar as mudanças e o plano de rollback.
- **Versionamento:** O versionamento segue Semantic Versioning (vMAJOR.MINOR.PATCH).

## Contribuição
Consulte o arquivo [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes sobre o fluxo de trabalho, padrões de código e processo de Pull Request.

## Licença
MIT
