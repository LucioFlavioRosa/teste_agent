# Agente de Revisão de Código

Este projeto implementa um agente de IA para revisão automatizada de código, capaz de realizar análises de design, segurança, pentest e infraestrutura como código (Terraform).

## Funcionalidades

- Análise de design de código
- Análise de segurança
- Testes de penetração (pentest)
- Revisão de código Terraform
- API REST para integração com outros sistemas
- Suporte para análise de repositórios GitHub ou snippets de código

## Pré-requisitos

- Python 3.8 ou superior
- Conta na OpenAI com acesso à API
- Token de acesso ao GitHub (para análise de repositórios)

## Instalação

1. Clone o repositório:
   bash
   git clone https://github.com/seu-usuario/agente-revisor.git
   cd agente-revisor
   

2. Instale as dependências:
   bash
   pip install -r requirements.txt
   

3. Configure as variáveis de ambiente:
   bash
   cp .env.example .env
   # Edite o arquivo .env com suas credenciais
   

## Uso

### Via API

Inicie o servidor Flask:

bash
python app.py


Envie uma requisição POST para `/executar_analise`:

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
    repositorio='usuario/repositorio'
)

print(resultado['resultado'])


## Como Rodar os Testes

O projeto utiliza pytest para testes. Para executar a suíte de testes completa:

bash
python -m pytest -v


Para executar testes específicos:

bash
python -m pytest tests/test_agente_revisor.py -v


Para verificar a cobertura de testes:

bash
python -m pytest --cov=agents --cov=tools


## Deploy na Azure App Service

### Requisitos

- Conta Azure com permissões para criar recursos
- Azure CLI instalado e configurado
- Arquivo de configuração `azure-pipelines.yml` (incluído no repositório)

### Passos para Deploy

1. **Criar o App Service Plan**:
   bash
   az appservice plan create --name revisor-app-plan --resource-group seu-resource-group --sku B1 --is-linux
   

2. **Criar o Web App**:
   bash
   az webapp create --resource-group seu-resource-group --plan revisor-app-plan --name revisor-app --runtime "PYTHON:3.8"
   

3. **Configurar as variáveis de ambiente**:
   bash
   az webapp config appsettings set --resource-group seu-resource-group --name revisor-app --settings @env-settings.json
   

4. **Deploy via GitHub Actions ou Azure DevOps**:
   - Configure o workflow do GitHub Actions usando o template fornecido em `.github/workflows/azure-deploy.yml`
   - Ou use o Azure DevOps com o pipeline definido em `azure-pipelines.yml`

5. **Verificar o deploy**:
   bash
   curl https://revisor-app.azurewebsites.net/
   

### Troubleshooting no Azure

- **Logs**: Acesse os logs do aplicativo através do portal Azure ou via CLI:
  bash
  az webapp log tail --name revisor-app --resource-group seu-resource-group
  

- **Reiniciar o serviço**: Se necessário, reinicie o App Service:
  bash
  az webapp restart --name revisor-app --resource-group seu-resource-group
  

## Contribuição

Veja o arquivo [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes sobre como contribuir para este projeto.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.