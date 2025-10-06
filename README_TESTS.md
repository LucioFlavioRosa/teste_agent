# Guia de Testes Unitários

## Visão Geral

Este projeto implementa uma suíte completa de testes unitários para garantir a qualidade e confiabilidade do código. Os testes cobrem os módulos críticos do sistema com foco em cenários de erro e isolamento de dependências externas.

## Estrutura dos Testes


tests/
├── __init__.py
├── test_revisor_geral.py      # Testes para tools/revisor_geral.py
├── test_github_reader.py      # Testes para tools/github_reader.py
└── test_flask_endpoints.py    # Testes para endpoints Flask


## Executando os Testes

### Pré-requisitos

bash
pip install -r requirements.txt


### Executar todos os testes

bash
pytest


### Executar testes com cobertura

bash
pytest --cov=tools --cov-report=html


### Executar testes específicos

bash
# Testes de um módulo específico
pytest tests/test_revisor_geral.py

# Teste específico
pytest tests/test_revisor_geral.py::TestRevisorGeral::test_openai_api_key_ausente_lanca_erro


## Cobertura de Testes

### Módulo `tools/revisor_geral.py`

- ✅ Validação de chave API OpenAI ausente
- ✅ Carregamento de arquivos de prompt (sucesso e falha)
- ✅ Execução de análise LLM (sucesso e falha na API)
- ✅ Tratamento de instruções extras

### Módulo `tools/github_reader.py`

- ✅ Conexão ao GitHub (sucesso e token inválido)
- ✅ Verificação de extensões de arquivo
- ✅ Leitura de arquivos com retry
- ✅ Coleta de arquivos e diretórios
- ✅ Limite de profundidade na leitura
- ✅ Leitura paralela com isolamento de dependências

### Endpoints Flask

- ✅ Endpoint raiz (`/`)
- ✅ Endpoint `/executar_analise` (sucesso com repositório e código)
- ✅ Validação de parâmetros obrigatórios
- ✅ Tratamento de exceções internas
- ✅ Validação de JSON malformado

## Estratégias de Teste

### Isolamento de Dependências

Todos os testes utilizam mocks para isolar dependências externas:

- **OpenAI API**: Mockada para evitar chamadas reais
- **GitHub API**: Mockada para evitar dependência de rede
- **Google Colab userdata**: Mockado para simular configurações

### Cenários de Erro

Os testes cobrem extensivamente cenários de falha:

- Chaves de API ausentes ou inválidas
- Arquivos não encontrados
- Falhas de rede
- Dados corrompidos
- Limites de profundidade

### Testes de Retry

Implementação de testes para verificar mecanismos de retry:

- Falhas temporárias de rede
- Recuperação após tentativas
- Limite máximo de tentativas

## Integração Contínua

Os testes são executados automaticamente via GitHub Actions em:

- Push para branches `main` e `develop`
- Pull requests para `main`
- Múltiplas versões do Python (3.8, 3.9, 3.10, 3.11)

## Boas Práticas Implementadas

1. **Nomenclatura Clara**: Nomes de testes descritivos
2. **Isolamento**: Cada teste é independente
3. **Mocking Abrangente**: Dependências externas mockadas
4. **Cobertura de Cenários**: Sucesso e falha cobertos
5. **Documentação**: Docstrings explicativas
6. **Configuração Centralizada**: `pytest.ini` para configurações

## Métricas de Qualidade

- **Cobertura de Código**: >90% para módulos críticos
- **Tempo de Execução**: <30 segundos para suíte completa
- **Isolamento**: 100% dos testes usam mocks para dependências externas
- **Cenários de Erro**: >80% dos fluxos de exceção cobertos