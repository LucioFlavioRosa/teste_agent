# Agent Vinna

Sistema de auditoria automática de código-fonte e infraestrutura, utilizando LLMs para análise de design, segurança, pentest e Terraform.

## Índice
- [Descrição do Projeto](#descrição-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração de Variáveis de Ambiente](#configuração-de-variáveis-de-ambiente)
- [Como Executar a Aplicação](#como-executar-a-aplicação)
- [Como Rodar os Testes](#como-rodar-os-testes)
- [Arquitetura e Fluxo de Dados](#arquitetura-e-fluxo-de-dados)
- [Changelog](#changelog)
- [Contribuição](#contribuição)

## Descrição do Projeto
O Agent Vinna automatiza auditorias técnicas em projetos de software, integrando-se ao GitHub e utilizando LLMs para avaliações de design, segurança, pentest e infraestrutura como código. O sistema expõe endpoints via Flask e pode ser utilizado tanto por API quanto por linha de comando.

## Pré-requisitos
- Python 3.8+
- Conta no GitHub (Personal Access Token)
- Chave de API da OpenAI
- Dependências listadas em `requirements.txt`

## Instalação
bash
# Clone o repositório
git clone https://github.com/SEU_USUARIO/agent-vinna.git
cd agent-vinna

# Instale as dependências
pip install -r requirements.txt


## Configuração de Variáveis de Ambiente
1. Copie o arquivo de exemplo:
bash
cp .env.example .env

2. Edite o arquivo `.env` com suas credenciais (NUNCA commite o arquivo real!).
3. Consulte os comentários do `.env.example` para detalhes de segurança e permissões.

## Como Executar a Aplicação
### Modo CLI
bash
python teste_git_hub.py

### Modo API (Flask)
bash
python teste_git_hub.py

Acesse: [http://localhost:5000](http://localhost:5000)

## Como Rodar os Testes
- **Testes de unidade:**
bash
pytest -v tests/unit

- **Testes de integração:**
bash
pytest -v tests/integration

- **Cobertura de testes:**
bash
pytest --cov=agents --cov=tools


## Arquitetura e Fluxo de Dados


+-------------------+       +------------------+       +-------------------+
|    Flask API      | --->  | agente_revisor   | --->  |  revisor_geral    |
+-------------------+       +------------------+       +-------------------+
         |                        |                           |
         v                        v                           v
    github_reader.py    prompt/*.md (instruções)         OpenAI API


- **agents/**: Orquestradores de análise (ex: `agente_revisor.py`).
- **tools/**: Utilitários de integração (ex: `github_reader.py`, `revisor_geral.py`).
- **tools/prompt/**: Prompts especializados para cada tipo de análise.

Fluxo: Usuário faz requisição → Flask API → agente_revisor seleciona prompt e código → revisor_geral chama OpenAI → resposta retornada.

## Changelog
Consulte [CHANGELOG.md](CHANGELOG.md) para histórico de versões.

## Contribuição
Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para diretrizes de contribuição.
