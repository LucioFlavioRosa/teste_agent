# Agente de Análise de Código

## Visão Geral

Este projeto implementa um agente inteligente que lê repositórios do GitHub e executa análises de código via LLM (Large Language Model). O agente é exposto através de uma API REST desenvolvida com Flask, permitindo análises de design, segurança, pentest e configurações Terraform.

## Pré-requisitos

- Python 3.10 ou superior
- Git
- Acesso à API da OpenAI
- Token de acesso ao GitHub

## Instalação

1. Clone o repositório:
   bash
   git clone https://github.com/seu-usuario/nome-do-repo.git
   cd nome-do-repo
   

2. Crie e ative um ambiente virtual:
   bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   

3. Instale as dependências:
   bash
   pip install -r requirements.txt
   

## Configuração do Ambiente

1. Copie o arquivo de exemplo de variáveis de ambiente:
   bash
   cp .env.example .env
   

2. Edite o arquivo `.env` e preencha as variáveis necessárias com seus valores reais:
   - `OPENAI_API_KEY`: Sua chave de API da OpenAI
   - `GITHUB_TOKEN`: Seu token de acesso pessoal do GitHub
   - Outras configurações conforme necessário

## Como Executar a Aplicação

### Usando o script principal

bash
python teste_git_hub.py


### Usando o servidor Flask

bash
flask run --host=0.0.0.0 --port=5000


Ou:

bash
python -m flask run --host=0.0.0.0 --port=5000


## Como Usar a API

### Endpoint: `/executar_analise`

**Método:** POST

**Corpo da Requisição (JSON):**


{
  "tipo_analise": "design",  // Opções: "design", "pentest", "seguranca", "terraform"
  "repositorio": "usuario/nome-do-repo",  // Opcional se 'codigo' for fornecido
  "codigo": "código fonte aqui",  // Opcional se 'repositorio' for fornecido
  "instrucoes_extras": "Instruções adicionais para a análise"  // Opcional
}


**Exemplo de Requisição com cURL:**

bash
curl -X POST http://localhost:5000/executar_analise \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_analise": "design",
    "repositorio": "usuario/nome-do-repo",
    "instrucoes_extras": "Foque na modularidade e padrões de design"
  }'


**Exemplo de Resposta:**


{
  "tipo_analise": "design",
  "resultado": "Análise detalhada do design do código..."
}


## Como Rodar os Testes

bash
pyttest -q


## Troubleshooting

### Problemas Comuns

1. **Erro de Autenticação com GitHub ou OpenAI**
   - Verifique se as chaves de API estão corretas no arquivo `.env`
   - Confirme se as chaves têm permissões suficientes

2. **Falha ao Ler Repositório**
   - Verifique se o repositório existe e é público
   - Confirme se o token do GitHub tem permissão para acessar o repositório

3. **Timeout na Análise**
   - Para repositórios muito grandes, considere analisar apenas partes específicas
   - Ajuste o parâmetro `max_token_out` para valores menores

4. **Erro 'Módulo não encontrado'**
   - Verifique se todas as dependências foram instaladas corretamente
   - Confirme se está executando o código dentro do ambiente virtual ativado