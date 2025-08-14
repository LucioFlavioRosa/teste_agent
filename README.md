# Agente de Revisão e Análise de Código

Este projeto fornece uma API e utilitários para análise automatizada de código-fonte hospedado em repositórios GitHub, utilizando LLMs para avaliações técnicas como design, segurança, pentest e infraestrutura.

## Estrutura do Projeto

- `agents/`: Contém agentes de alto nível que orquestram a análise de código.
- `tools/`: Utilitários para leitura de repositórios, integração com LLMs e manipulação de prompts.
- `teste_git_hub.py`: Script de exemplo e endpoint Flask para uso e teste da API.

## Como Começar

### Pré-requisitos

- Python 3.9+
- Pip
- Conta no GitHub (token de acesso pessoal)
- Chave de API da OpenAI

### Instalação

1. Clone este repositório.
2. Instale as dependências necessárias:

bash
pip install -r requirements.txt


3. Defina as variáveis de ambiente necessárias (ou configure via `google.colab.userdata` se usar Colab):

- `OPENAI_API_KEY`: Sua chave da OpenAI
- `github_token`: Token de acesso pessoal do GitHub

### Execução

Para rodar o servidor Flask localmente:

bash
python teste_git_hub.py


Acesse `http://localhost:5000/` para verificar se o servidor está ativo.

Para executar uma análise via API, envie um POST para `/executar_analise` com um JSON como:


{
  "tipo_analise": "pentest",
  "repositorio": "usuario/repositorio",
  "codigo": null,
  "instrucoes_extras": "[Instruções adicionais aqui]"
}


## Como Rodar os Testes

> [Instruções detalhadas de execução de testes automatizados aqui.]

## Observações

- Os utilitários requerem tokens válidos e acesso à internet.
- Para uso em notebooks Colab, configure as credenciais via `google.colab.userdata`.
- Consulte as docstrings das funções para exemplos detalhados de uso.
