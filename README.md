# Agente de Revisão de Código

Este projeto implementa um agente de IA para análise automatizada de código-fonte, oferecendo diferentes tipos de análises como design, segurança, pentest e validação de infraestrutura Terraform.

## Funcionalidades

- Análise de design de código
- Verificação de segurança
- Testes de penetração (pentest)
- Validação de configurações Terraform
- Suporte para análise via repositório GitHub ou código fornecido diretamente

## Pré-requisitos

- Python 3.8+
- Conta na OpenAI com acesso à API
- Token de acesso pessoal do GitHub (para análise de repositórios)

## Instalação

1. Clone o repositório:
   bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
   

2. Instale as dependências:
   bash
   pip install -r requirements.txt
   

3. Configure as variáveis de ambiente:
   bash
   cp .env.example .env
   # Edite o arquivo .env com suas credenciais
   

## Como Usar

### Via API REST

1. Inicie o servidor Flask:
   bash
   python app.py
   

2. Faça uma requisição POST para o endpoint `/executar_analise`:
   bash
   curl -X POST http://localhost:5000/executar_analise \
     -H "Content-Type: application/json" \
     -d '{
       "tipo_analise": "design",
       "repositorio": "usuario/repositorio",
       "instrucoes_extras": "Foque em padrões de design e modularidade"
     }'
   

### Via Importação Direta

python
from agents import agente_revisor

resultado = agente_revisor.executar_analise(
    tipo_analise='seguranca',
    repositorio='usuario/repositorio',
    instrucoes_extras='Verifique vulnerabilidades de injeção SQL'
)

print(resultado['resultado'])


## Como Rodar os Testes

Para executar a suíte completa de testes:

bash
pytest -v


Para executar testes específicos:

bash
pytest tests/test_agente_revisor.py -v


Para verificar a cobertura de testes:

bash
pytest --cov=agents --cov=tools tests/


## Deployment no Azure App Service

### Pré-requisitos

- Conta Azure com acesso ao Azure App Service
- Azure CLI instalado e configurado

### Configuração

1. Crie um App Service no Azure:
   bash
   az webapp create --resource-group seu-grupo-recursos --plan seu-plano-app-service --name seu-app-service --runtime "PYTHON:3.9"
   

2. Configure as variáveis de ambiente necessárias:
   bash
   az webapp config appsettings set --resource-group seu-grupo-recursos --name seu-app-service --settings OPENAI_API_KEY="sua-chave" GITHUB_TOKEN="seu-token" WEBSITE_RUN_FROM_PACKAGE=1
   

3. Deploy do código:
   bash
   # Opção 1: Via GitHub Actions (recomendado)
   # Configure o arquivo .github/workflows/azure-deploy.yml
   
   # Opção 2: Via ZIP deploy
   az webapp deployment source config-zip --resource-group seu-grupo-recursos --name seu-app-service --src ./seu-app.zip
   

### Arquivos de Configuração Específicos para Azure

- **requirements.txt**: Certifique-se de que todas as dependências estão listadas
- **startup.txt**: Se necessário, para personalizar o comando de inicialização
- **web.config**: Para configurações específicas do servidor web

### Monitoramento

Acesse os logs da aplicação:
bash
az webapp log tail --resource-group seu-grupo-recursos --name seu-app-service


## Contribuição

Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para obter detalhes sobre como contribuir para este projeto.

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.