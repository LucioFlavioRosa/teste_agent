# Sistema de Agentes de Revisão de Código

Este projeto oferece um conjunto de agentes para análise automatizada de repositórios de código, com foco em revisão técnica, segurança, design e infraestrutura como código. Utiliza LLMs para avaliações profundas e integra-se a repositórios GitHub.

## Estrutura do Projeto

- `agents/`: Agentes principais de revisão (ex: `agente_revisor.py`).
- `tools/`: Utilitários para leitura de repositórios e execução de análises via LLM.
- `teste_git_hub.py`: Exemplo de uso e endpoint Flask para execução via API.
- `__init__.py`: Arquivos para explicitar pacotes Python.

## Como Começar

### Pré-requisitos
- Python 3.9+
- Pip
- Conta na OpenAI (API Key)
- Conta no GitHub (token pessoal)

### Instalação
1. Clone este repositório.
2. Instale as dependências:
bash
pip install -r requirements.txt

3. Configure as variáveis de ambiente ou o `google.colab.userdata` com suas chaves:
   - `OPENAI_API_KEY` para acesso à OpenAI
   - `github_token` para acesso ao GitHub

### Execução
Para rodar o agente principal via Flask:
bash
python teste_git_hub.py

O servidor Flask estará disponível em `http://0.0.0.0:5000/`.

Para executar uma análise diretamente:
python
from agents import agente_revisor
resultado = agente_revisor.main(tipo_analise='pentest', repositorio='usuario/repositorio')
print(resultado['resultado'])


## Como Rodar os Testes

> [Instruções detalhadas de execução de testes automatizados aqui]

Sugestão: Utilize `pytest` para testes unitários e de integração.

bash
pytest

