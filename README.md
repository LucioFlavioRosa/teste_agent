# Projeto Agente Revisor IA

## Configuração de Ambiente

### Variáveis de Ambiente Necessárias

- `OPENAI_API_KEY`: Chave de API da OpenAI para análises LLM.
- `github_token`: Token de acesso ao GitHub para leitura de repositórios.

Essas variáveis devem ser configuradas no ambiente do Google Colab via:

python
from google.colab import userdata
userdata.set('OPENAI_API_KEY', 'sua-chave-openai')
userdata.set('github_token', 'seu-token-github')


## Instalação de Dependências

bash
pip install -r requirements.txt


## Uso da API Flask

Endpoint principal:


POST /executar_analise


Exemplo de requisição:


{
  "tipo_analise": "pentest",
  "repositorio": "usuario/repositorio",
  "codigo": null,
  "instrucoes_extras": "Verificar vulnerabilidades X, Y, Z."
}


Resposta:


{
  "tipo_analise": "pentest",
  "resultado": "..."
}

