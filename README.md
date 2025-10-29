# Agent-Vinna

Agentes de IA para Análise Automatizada de Código

## Descrição
Agent-Vinna é uma plataforma de agentes inteligentes para revisão, pentest e análise de código-fonte em repositórios GitHub, utilizando LLMs (OpenAI API) e automação Python. O sistema foi projetado para facilitar auditorias de segurança, revisão de design e conformidade com padrões de desenvolvimento.

## Propósito
- Automatizar revisões de código e infraestrutura (Terraform, CloudFormation, etc.)
- Detectar vulnerabilidades, problemas de design e violações de padrões
- Integrar facilmente com pipelines CI/CD e fluxos de trabalho de desenvolvimento

## Arquitetura
- **agents/**: Agentes de IA para diferentes tipos de análise
- **tools/**: Ferramentas de integração (GitHub, OpenAI, prompts)
- **tools/prompt/**: Prompts customizados para cada tipo de análise
- **docs/**: Documentação técnica e de API
- **.github/**: Templates de colaboração

Fluxo principal:
1. Requisição via API Flask (`/executar_analise`)
2. Agente seleciona tipo de análise e fonte (código ou repositório)
3. Ferramenta lê arquivos do GitHub e prepara contexto
4. Prompt específico é carregado
5. Chamada à OpenAI API para análise
6. Resposta estruturada é retornada ao usuário

## Instalação

### 1. Clonar o repositório
bash
git clone https://github.com/LucioFlavioRosa/agent-vinna.git
cd agent-vinna


### 2. Instalar dependências Python
bash
pip install -r requirements.txt


### 3. Configurar variáveis de ambiente
Crie um arquivo `.env` (ou use `.env.example` como base):

OPENAI_API_KEY=your_openai_key_here
GITHUB_TOKEN=your_github_token_here
FLASK_ENV=development
FLASK_DEBUG=True


### 4. Executar a aplicação Flask
bash
python teste_git_hub.py


## Uso da API REST

### Endpoint principal
`POST /executar_analise`

#### Parâmetros do body JSON:
- `tipo_analise`: Tipo de análise (`pentest`, `design`, `seguranca`, etc.)
- `repositorio`: Nome do repositório GitHub (`owner/repo`)
- `codigo`: Código-fonte direto (opcional)
- `instrucoes_extras`: Instruções adicionais para o agente (opcional)

#### Exemplo de requisição com curl:
bash
curl -X POST http://localhost:5000/executar_analise \
     -H "Content-Type: application/json" \
     -d '{
           "tipo_analise": "pentest",
           "repositorio": "LucioFlavioRosa/agent-vinna",
           "instrucoes_extras": "Priorize vulnerabilidades críticas"
         }'


#### Respostas
- **200 OK**: Resultado da análise
- **400 Bad Request**: Parâmetros inválidos
- **500 Internal Server Error**: Erro interno

## Testes
- Para rodar testes, utilize scripts específicos ou frameworks como `pytest`.
- Recomenda-se criar casos de teste para cada agente e integração principal.

## Contribuição
Consulte o arquivo [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes sobre o fluxo de trabalho, padrões de código e processo de revisão.

## Licença
Este projeto é protegido e segue as políticas internas da Protecta Seguros.
