# Agent Vinna

Um sistema de agentes de IA para análise de código, incluindo revisões de design, segurança, pentest e infraestrutura como código (Terraform).

## Funcionalidades

- Análise de código fonte de repositórios GitHub
- Suporte para diferentes tipos de análise:
  - Design de código
  - Segurança
  - Pentest
  - Terraform
- API REST para integração com outros sistemas
- Suporte para análise de código fornecido diretamente ou via repositório GitHub

## Pré-requisitos

- Python 3.8+
- Conta na OpenAI com acesso à API
- Token de acesso ao GitHub (para análise de repositórios)

## Instalação

1. Clone o repositório:
   bash
   git clone https://github.com/LucioFlavioRosa/agent-vinna.git
   cd agent-vinna
   

2. Instale as dependências:
   bash
   pip install -r requirements.txt
   

3. Configure as variáveis de ambiente:
   bash
   cp .env.example .env
   # Edite o arquivo .env com suas credenciais
   

## Uso

### Executando o servidor

bash
python app.py


O servidor estará disponível em `http://localhost:5000`.

### Usando a API

Exemplo de requisição para análise de código:

bash
curl -X POST http://localhost:5000/executar_analise \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_analise": "design",
    "repositorio": "usuario/repositorio",
    "instrucoes_extras": "Foque em padrões de design e estrutura do código"
  }'


## Como Rodar os Testes

Para executar a suíte de testes completa:

bash
pytest -v


Para executar testes específicos:

bash
pytest tests/test_agente_revisor.py -v


## Deploy na Azure App Service

### Pré-requisitos

- Conta Azure com acesso ao Azure App Service
- Azure CLI instalado e configurado
- Plano de App Service criado

### Configuração

1. Crie um Web App no Azure App Service:
   bash
   az webapp create --resource-group seu-grupo-recursos --plan seu-plano-servico --name seu-app-name --runtime "PYTHON|3.9"
   

2. Configure as variáveis de ambiente necessárias:
   bash
   az webapp config appsettings set --resource-group seu-grupo-recursos --name seu-app-name --settings WEBSITES_PORT=5000 OPENAI_API_KEY=sua-chave GITHUB_TOKEN=seu-token
   

3. Deploy do código:
   bash
   az webapp deployment source config-local-git --resource-group seu-grupo-recursos --name seu-app-name
   git remote add azure <URL_GIT_FORNECIDA>
   git push azure main
   

### Variáveis de Ambiente Obrigatórias para Azure

- `WEBSITES_PORT`: Deve ser configurado como 5000 para corresponder à porta do aplicativo Flask
- `OPENAI_API_KEY`: Sua chave de API da OpenAI
- `GITHUB_TOKEN`: Token de acesso ao GitHub
- `AZURE_CONNECTION_STRING`: Se estiver usando serviços adicionais do Azure

## Contribuição

Por favor, leia [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes sobre nosso código de conduta e o processo para enviar pull requests.

## Changelog

Veja [CHANGELOG.md](CHANGELOG.md) para um histórico de todas as alterações do projeto.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.