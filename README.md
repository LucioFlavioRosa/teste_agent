# Agente Revisor de Código

Este projeto executa análises automatizadas de repositórios de código (pentest, design, segurança, terraform) usando modelos da OpenAI.

## Pré-requisitos
- Python 3.10+
- Variáveis de ambiente:
  - OPENAI_API_KEY: chave da API da OpenAI
  - GITHUB_TOKEN: token de acesso ao GitHub

Opcionalmente, crie um arquivo `.env` com base em `.env.example` e exporte as variáveis para o ambiente.

## Instalação
1. Crie e ative um virtualenv (recomendado).
2. Instale as dependências:

   pip install -r requirements.txt

## Prompts
Coloque seus prompts em:

- tools/prompts/pentest.md
- tools/prompts/design.md
- tools/prompts/seguranca.md
- tools/prompts/terraform.md

Se algum arquivo não existir, um prompt padrão será utilizado como fallback.

## Execução via Flask
O servidor Flask está definido em `teste_git_hub.py`.

Execute:

python teste_git_hub.py

Endpoint:
- POST /executar_analise

Exemplo de payload:

{
  "tipo_analise": "pentest",
  "repositorio": "owner/repo",
  "instrucoes_extras": "Foque em segredos expostos"
}

Em alternativa ao campo `repositorio`, você pode enviar `codigo` (string) com o conteúdo a ser analisado.

## Variáveis de Ambiente
- OPENAI_API_KEY: chave da OpenAI.
- GITHUB_TOKEN: token do GitHub para leitura do repositório.

## Observações
- Os diretórios `agents/` e `tools/` possuem `__init__.py` para garantir import estável.
- Fora do Google Colab, não há dependência de `google.colab`.
