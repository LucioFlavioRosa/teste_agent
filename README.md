# Servidor de Análise de Código via Agentes de IA

Este projeto disponibiliza uma API REST baseada em Flask para análise automatizada de código-fonte utilizando agentes de IA. O objetivo é facilitar revisões de segurança, arquitetura e conformidade em repositórios GitHub ou trechos de código enviados diretamente.

## Sumário
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Execução](#execução)
- [Exemplos de Uso](#exemplos-de-uso)
- [Testes](#testes)
- [Arquitetura do Sistema](#arquitetura-do-sistema)
- [Segurança](#segurança)
- [Changelog](#changelog)
- [Contribuição](#contribuição)

## Instalação

Clone este repositório e instale as dependências:

bash
pip install -r requirements.txt


## Configuração

Crie um arquivo `.env` baseado em `.env.example` e preencha as variáveis necessárias:

- `GITHUB_TOKEN`: Token de acesso pessoal do GitHub (obrigatório para análises em repositórios privados ou com alto volume de requisições).
- `FLASK_ENV`: Ambiente do Flask (`development` ou `production`).
- `FLASK_DEBUG`: Ativa/desativa debug do Flask.
- `API_PORT`: Porta para execução da API.

## Execução

Você pode rodar a aplicação de duas formas:

bash
python teste_git_hub.py


ou

bash
flask run


A API ficará disponível em `http://localhost:5000` (ou na porta definida em `API_PORT`).

## Exemplos de Uso

### Requisição de análise via API REST

Endpoint: `POST /executar_analise`

Exemplo de payload JSON:


{
  "tipo_analise": "pentest",
  "repositorio": "usuario/repositorio",
  "instrucoes_extras": "Avalie práticas de segurança."
}


Resposta esperada:


{
  "resultado": "Resumo da análise..."
}


## Testes

Os testes podem ser executados utilizando frameworks como `pytest` (implemente conforme necessidade do projeto).

bash
pytest


## Arquitetura do Sistema

- **agents/**: Implementação dos agentes de análise (ex: `agente_revisor.py`).
- **tools/**: Ferramentas auxiliares, como leitura de repositórios e prompts.
- **tools/prompt/**: Prompts específicos para cada tipo de análise (design, pentest, segurança, terraform).
- **teste_git_hub.py**: Script principal que expõe a API Flask e integra os agentes.

### Fluxo de Execução

1. Requisição chega à API Flask (`/executar_analise`).
2. O endpoint chama o agente revisor (`agents/agente_revisor.py`).
3. O agente utiliza o leitor de repositórios (`tools/github_reader.py`) e os prompts adequados.
4. O resultado é retornado ao usuário via API.

### Diagrama de Componentes


[Usuário/API Client]
        |
        v
[Flask API (teste_git_hub.py)]
        |
        v
[agents/agente_revisor.py]
        |
        v
[tools/github_reader.py] -- [tools/prompt/]


## Segurança

- **GITHUB_TOKEN**: Faça a rotação do token a cada 90 dias.
- **HTTPS**: O uso de HTTPS é obrigatório em ambientes de produção.
- **Rate Limiting**: A API do GitHub possui limite de 5000 requisições/hora por token.
- **Deploys em Produção**: Releases só podem ser feitas após aprovação do Change Approval Board (CAB), conforme calendário quinzenal (terças-feiras, 22:00-23:00).

## Changelog

Consulte o arquivo [CHANGELOG.md](CHANGELOG.md) para histórico detalhado de versões e alterações.

## Contribuição

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para diretrizes detalhadas sobre como contribuir.
