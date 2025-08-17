# Agente Revisor de Código

Este projeto executa análises de código (design, segurança, pentest e Terraform) usando um LLM e leitura de repositórios GitHub.

## Pré-requisitos
- Python 3.9+
- Variáveis de ambiente configuradas:
  - OPENAI_API_KEY: chave da API da OpenAI
  - GITHUB_TOKEN: token com acesso de leitura ao repositório
  - LLM_MODEL (opcional): modelo LLM a ser utilizado (padrão: gpt-4o)

Você pode usar o arquivo `.env.example` como referência para os valores necessários.

## Instalação
1. Crie e ative um virtualenv (opcional):
   - python -m venv .venv
   - source .venv/bin/activate (Linux/Mac) ou .venv\\Scripts\\activate (Windows)
2. Instale dependências:
   - pip install -r requirements.txt

## Configuração
Exporte as variáveis de ambiente (exemplos em Linux/Mac):
- export OPENAI_API_KEY=seu_token_openai
- export GITHUB_TOKEN=seu_token_github
- export LLM_MODEL=gpt-4o  # opcional

## Uso via Script de Exemplo
O arquivo `teste_git_hub.py` contém um exemplo de uso e também inicia uma API Flask com o endpoint `/executar_analise`.

## Endpoint Flask
- Rota: POST /executar_analise
- Corpo (JSON):
  - tipo_analise: "design" | "pentest" | "seguranca" | "terraform" (obrigatório)
  - repositorio: "owner/repo" (opcional se `codigo` for fornecido)
  - codigo: string com código fonte (opcional se `repositorio` for fornecido)
  - instrucoes_extras: string (opcional)

Exemplo de requisição:
{
  "tipo_analise": "pentest",
  "repositorio": "owner/repo",
  "instrucoes_extras": "Foque em credenciais hardcoded"
}

Resposta:
{
  "tipo_analise": "pentest",
  "resultado": "...conteúdo da análise..."
}

## Observações
- Os prompts utilizados pelo LLM estão em `tools/prompts/`.
- O modelo padrão pode ser alterado definindo a variável `LLM_MODEL`.
- Certifique-se de que o `GITHUB_TOKEN` possui escopos de leitura do repositório alvo.
