# Sistema de Agentes de Revisão LLM

Este projeto fornece um sistema de agentes para análise automatizada de código-fonte utilizando modelos de linguagem (LLMs), com integração a repositórios GitHub e suporte a múltiplos tipos de análise (design, pentest, segurança, terraform). Inclui API REST baseada em Flask e utilitários para leitura e orquestração de análises.

## Estrutura do Projeto

- `agents/`: Orquestradores e agentes principais para execução das análises LLM.
- `tools/`: Utilitários para leitura de repositórios, prompts e integração com APIs externas.
- `teste_git_hub.py`: Script de exemplo e servidor Flask para interface REST.
- `README.md`: Este arquivo de documentação.

## Como Começar (Getting Started)

### Pré-requisitos

- Python 3.9+
- Pip
- Conta no GitHub (token pessoal)
- Conta na OpenAI (API Key)

### Instalação

1. Clone o repositório:
   bash
   git clone [URL_DO_REPOSITORIO]
   cd [NOME_DA_PASTA]
   
2. Instale as dependências:
   bash
   pip install -r requirements.txt
   
3. Configure as variáveis de ambiente para tokens do GitHub e OpenAI conforme instruções do Colab ou ambiente local.

### Execução

Para iniciar o servidor Flask de análise:
bash
python teste_git_hub.py


Para uso programático dos agentes, consulte os módulos em `agents/` e `tools/`.

## Como Rodar os Testes

> [Instruções detalhadas de execução dos testes automatizados aqui]

Exemplo (caso utilize pytest):
bash
pytest


## Observações

- Separe a lógica de teste interativo e aplicação Flask para melhor manutenção.
- Consulte as docstrings dos módulos e funções para detalhes de uso e integração.
