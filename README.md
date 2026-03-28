# Agente de Análise de Código

Este projeto implementa um agente de IA para análise automatizada de código-fonte, oferecendo diferentes tipos de análise como design, segurança, pentest e revisão de infraestrutura Terraform.

## Funcionalidades

- Análise de design de código
- Análise de segurança
- Testes de penetração (pentest)
- Revisão de código Terraform
- Suporte para análise via repositório GitHub ou código fornecido diretamente
- API REST para integração com outros sistemas

## Requisitos

- Python 3.8 ou superior
- Pip (gerenciador de pacotes Python)
- Conta na OpenAI com acesso à API
- Token de acesso ao GitHub (para análise de repositórios)

## Instalação

### 1. Clone o repositório

bash
git clone https://github.com/seu-usuario/nome-do-repositorio.git
cd nome-do-repositorio


### 2. Instale as dependências

bash
pip install -r requirements.txt


### 3. Configure as variáveis de ambiente

Copie o arquivo de exemplo para criar seu arquivo de variáveis de ambiente:

bash
cp .env.example .env


Edite o arquivo `.env` e configure as seguintes variáveis essenciais:

- `OPENAI_API_KEY`: Sua chave de API da OpenAI
- `GITHUB_TOKEN`: Seu token de acesso pessoal do GitHub
- Outras variáveis conforme necessário

## Executando Localmente

### Iniciar o servidor Flask

bash
python app.py


O servidor estará disponível em `http://localhost:5000`.

### Usando a API

Para executar uma análise, envie uma requisição POST para o endpoint `/executar_analise`:

bash
curl -X POST http://localhost:5000/executar_analise \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_analise": "design",
    "repositorio": "usuario/repositorio",
    "instrucoes_extras": "Foque em padrões de design e modularidade"
  }'


Ou para analisar código diretamente:

bash
curl -X POST http://localhost:5000/executar_analise \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_analise": "seguranca",
    "codigo": "def funcao(): pass",
    "instrucoes_extras": "Verifique injeções de SQL"
  }'


## Executando Testes

Para executar a suite de testes:

bash
pytest


Para testes com cobertura:

bash
pytest --cov=. tests/


## Deploy no Azure App Service

### Pré-requisitos

- Azure CLI instalado e configurado
- Conta Azure com permissões para criar recursos App Service

### Passos para Deploy

1. **Faça login no Azure**:

bash
az login


2. **Crie um grupo de recursos** (se não existir):

bash
az group create --name seu-grupo-recursos --location eastus


3. **Crie um plano de serviço de aplicativo**:

bash
az appservice plan create --name seu-plano-servico --resource-group seu-grupo-recursos --sku B1 --is-linux


4. **Crie o aplicativo web**:

bash
az webapp create --resource-group seu-grupo-recursos --plan seu-plano-servico --name seu-app-name --runtime "PYTHON:3.8"


5. **Configure as variáveis de ambiente**:

bash
az webapp config appsettings set --resource-group seu-grupo-recursos --name seu-app-name --settings OPENAI_API_KEY="sua-chave" GITHUB_TOKEN="seu-token"


6. **Deploy do código**:

bash
az webapp up --name seu-app-name --resource-group seu-grupo-recursos --location eastus


Alternativamente, você pode configurar um pipeline CI/CD no GitHub Actions ou Azure DevOps para automatizar o processo de deploy.

## Configurando CI/CD com GitHub Actions

Para configurar um pipeline de CI/CD com GitHub Actions:

1. Crie um diretório `.github/workflows` no seu repositório
2. Adicione um arquivo `azure-deploy.yml` com a configuração do workflow
3. Configure os segredos necessários nas configurações do repositório GitHub

Exemplo de workflow:

yaml
name: Deploy to Azure
on:
  push:
    branches: [ main ]
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Deploy to Azure
      uses: azure/webapps-deploy@v2
      with:
        app-name: 'seu-app-name'
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}


## Contribuição

Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para obter informações sobre como contribuir com este projeto.

## Changelog

Consulte [CHANGELOG.md](CHANGELOG.md) para ver o histórico de alterações do projeto.

## Licença

Este projeto está licenciado sob a licença MIT - consulte o arquivo LICENSE para obter detalhes.