# Agent-Vinna

Sistema de auditoria automatizada de código-fonte com análise por LLM, focado em segurança, design, pentest e infraestrutura como código.

## Descrição
O Agent-Vinna é uma solução para revisão técnica avançada de repositórios de código, utilizando modelos de linguagem (LLM) para análise de design, segurança, pentest e Terraform. O sistema integra-se ao GitHub e à OpenAI, fornecendo relatórios detalhados e recomendações de melhoria.

## Pré-requisitos
- Python 3.8+
- Conta na OpenAI (API Key)
- Conta no GitHub (Personal Access Token)

## Instalação
1. Clone o repositório:
   bash
   git clone https://github.com/SEU_USUARIO/agent-vinna.git
   cd agent-vinna
   
2. Instale as dependências:
   bash
   pip install -r requirements.txt
   
3. Configure as variáveis de ambiente:
   - Copie `.env.example` para `.env` e preencha com suas credenciais.

## Configuração de Variáveis de Ambiente
Veja o arquivo `.env.example` para detalhes das variáveis necessárias e instruções de segurança.

## Como executar a aplicação
- Para rodar a aplicação Flask (API):
  bash
  python teste_git_hub.py
  
- Acesse `http://localhost:5000` para verificar se o servidor está no ar.

## Como executar os testes
- Para rodar todos os testes (ajuste conforme sua suíte de testes):
  bash
  pytest -v
  
- Para rodar apenas testes de unidade:
  bash
  pytest tests/unit
  
- Para rodar apenas testes de integração:
  bash
  pytest tests/integration
  
- Para gerar relatório de cobertura:
  bash
  pytest --cov=agents --cov=tools
  

## Arquitetura e Fluxo de Dados
O projeto é organizado nos seguintes diretórios:

- `agents/`: Agentes de análise (ex: `agente_revisor.py`)
- `tools/`: Utilitários para integração com GitHub, OpenAI, etc.
- `tools/prompt/`: Prompts customizados para cada tipo de análise (design, pentest, segurança, terraform)

### Fluxo de Execução
1. O usuário faz uma requisição para o endpoint `/executar_analise` via API Flask.
2. O agente (`agents/agente_revisor.py`) valida os parâmetros, coleta o código do GitHub e prepara o conteúdo.
3. O código é passado para o LLM via `tools/revisor_geral.py`, que utiliza o prompt adequado de `tools/prompt/`.
4. O resultado é retornado ao usuário via API.

#### Diagrama (ASCII)

[Usuário] -> [Flask API] -> [agente_revisor.py] -> [github_reader.py] -> [revisor_geral.py] -> [OpenAI LLM]


## Contribuição
Consulte o arquivo `CONTRIBUTING.md` para detalhes sobre o fluxo de trabalho, padrões de código e processo de Pull Request.

## Histórico de Mudanças
Veja o arquivo `CHANGELOG.md`.
