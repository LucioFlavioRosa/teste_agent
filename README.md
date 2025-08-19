# Agent Vinna

## Descrição

Sistema de análise de código automatizada usando IA.

## Instalação

1. Clone o repositório
2. Instale as dependências:
   bash
   pip install -r requirements.txt
   

## Configuração

### Variáveis de Ambiente Necessárias

- `OPENAI_API_KEY`: Chave de API da OpenAI para executar as análises
- `github_token`: Token do GitHub para acessar repositórios (usado no Google Colab)

### Exemplo de configuração

bash
export OPENAI_API_KEY="sua-chave-aqui"


## Uso

### Como servidor Flask

bash
python teste_git_hub.py


O servidor estará disponível em `http://localhost:5000`

### Endpoint de Análise

`POST /executar_analise`

Corpo da requisição:

{
  "tipo_analise": "design",
  "repositorio": "usuario/repo",
  "instrucoes_extras": "Foque em padrões de segurança"
}


## Tipos de Análise Suportados

- `design`: Análise de design e arquitetura
- `pentest`: Análise de segurança e vulnerabilidades
- `seguranca`: Análise focada em segurança
- `terraform`: Análise de código Terraform
