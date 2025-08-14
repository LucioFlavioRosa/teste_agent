# Sistema de Revisão e Análise de Código Python

Este projeto fornece uma API e utilitários para análise automatizada de repositórios de código Python, com foco em revisão de design, segurança, infraestrutura como código e testes de segurança (pentest). Ele integra-se ao GitHub para extração de código e utiliza a OpenAI para análises baseadas em LLM.

## Estrutura do Projeto

- `agents/`: Contém agentes de orquestração e interface principal para análise de código.
- `tools/`: Utilitários para integração com GitHub, OpenAI e manipulação de prompts.
- `teste_git_hub.py`: Script de exemplo e servidor Flask para expor a API de análise.

## Como Começar (Getting Started)

### Pré-requisitos

- Python 3.8+
- Pip
- Conta no GitHub (token pessoal)
- Chave de API da OpenAI

### Instalação

1. Clone o repositório:
   bash
   git clone https://github.com/[SEU_USUARIO]/[NOME_DO_REPOSITORIO].git
   cd [NOME_DO_REPOSITORIO]
   
2. Instale as dependências:
   bash
   pip install -r requirements.txt
   
3. Configure as variáveis de ambiente:
   - `OPENAI_API_KEY` (sua chave da OpenAI)
   - `github_token` (token pessoal do GitHub, se estiver usando Google Colab, configure via `userdata`)

### Execução

Para rodar o servidor Flask localmente:
bash
python teste_git_hub.py


O endpoint principal estará disponível em:

POST http://localhost:5000/executar_analise


Exemplo de payload JSON:

{
  "tipo_analise": "design",
  "repositorio": "usuario/repositorio",
  "codigo": null,
  "instrucoes_extras": "[Instruções adicionais aqui, se necessário]"
}


## Como Rodar os Testes

*[Instruções detalhadas de execução de testes automatizados aqui, caso existam]*

## Observações

- O projeto foi rigorosamente documentado conforme PEP 257 e Google Style.
- Consulte as docstrings das funções para exemplos de uso e detalhes de integração.
