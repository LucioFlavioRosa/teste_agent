# Agent Vinna

Um sistema de agentes de IA para análise de código e segurança.

## Descrição

O Agent Vinna é uma ferramenta que utiliza modelos de linguagem avançados para realizar análises automatizadas de código-fonte. O sistema suporta diferentes tipos de análises, incluindo revisão de design, testes de penetração, análise de segurança e validação de infraestrutura como código (Terraform).

## Funcionalidades

- Análise de design de código
- Testes de penetração automatizados
- Verificação de segurança
- Validação de configurações Terraform
- Suporte para análise via repositório GitHub ou código direto

## Requisitos

- Python 3.8+
- Chave de API da OpenAI
- Token de acesso do GitHub (para análise de repositórios)

## Instalação

bash
# Clone o repositório
git clone https://github.com/LucioFlavioRosa/agent-vinna.git
cd agent-vinna

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas credenciais


## Uso

### Via API

Inicie o servidor Flask:

bash
python app.py


Faça uma requisição POST para o endpoint `/executar_analise`:

bash
curl -X POST http://localhost:5000/executar_analise \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_analise": "design",
    "repositorio": "usuario/repositorio",
    "instrucoes_extras": "Foque em padrões de design e modularidade"
  }'


### Via Script

python
from agents import agente_revisor

resultado = agente_revisor.main(
    tipo_analise='pentest',
    repositorio='usuario/repositorio'
)

print(resultado['resultado'])


## Como Rodar os Testes

Para executar a suíte de testes completa:

bash
pytest -v


Para executar testes específicos:

bash
pytest tests/test_agente_revisor.py -v


Para verificar a cobertura de testes:

bash
pytest --cov=. tests/


## Deploy na Azure App Service

### Pré-requisitos

- Azure CLI instalado e configurado
- Conta Azure com permissões para criar recursos App Service

### Configuração

1. **Login no Azure**:
   bash
   az login
   

2. **Criar um grupo de recursos** (se não existir):
   bash
   az group create --name agent-vinna-rg --location eastus
   

3. **Criar um plano de App Service**:
   bash
   az appservice plan create --name agent-vinna-plan --resource-group agent-vinna-rg --sku B1 --is-linux
   

4. **Criar o App Service**:
   bash
   az webapp create --resource-group agent-vinna-rg --plan agent-vinna-plan --name agent-vinna-app --runtime "PYTHON|3.8" --deployment-local-git
   

5. **Configurar variáveis de ambiente**:
   bash
   az webapp config appsettings set --resource-group agent-vinna-rg --name agent-vinna-app --settings OPENAI_API_KEY="sua-chave-api" github_token="seu-token-github"
   

6. **Deploy do código**:
   bash
   git remote add azure <URL_DO_GIT_FORNECIDO_PELO_AZURE>
   git push azure main
   

7. **Verificar o status**:
   bash
   az webapp log tail --resource-group agent-vinna-rg --name agent-vinna-app
   

### Comandos de Inicialização

O App Service usará o arquivo `startup.sh` na raiz do projeto para iniciar a aplicação. Certifique-se de que este arquivo contenha:

bash
#!/bin/bash
python app.py


E torne-o executável antes do deploy:

bash
chmod +x startup.sh


## Contribuição

Veja o arquivo [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes sobre como contribuir para este projeto.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
