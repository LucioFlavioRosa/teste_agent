# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não Lançado]

### Adicionado
- Documentação completa do projeto
- Templates para issues e pull requests
- Guia de contribuição detalhado
- Arquivo de exemplo de variáveis de ambiente

## [1.0.0] - 2024-01-XX

### Adicionado
- Sistema de análise de código com IA usando GPT-4
- Suporte para análise de design de código
- Análise de segurança e penetration testing
- Análise de infraestrutura Terraform
- Integração com GitHub API para leitura de repositórios
- API REST Flask para execução de análises
- Suporte para múltiplas linguagens de programação
- Sistema de retry e paralelização para leitura de arquivos
- Logging estruturado para debugging
- Tratamento robusto de erros

### Funcionalidades Principais
- **Agente Revisor** (`agents/agente_revisor.py`)
  - Validação de parâmetros de entrada
  - Preparação de código para análise
  - Execução de análises via LLM
  - Tratamento de diferentes tipos de erro

- **GitHub Reader** (`tools/github_reader.py`)
  - Conexão segura com GitHub API
  - Leitura iterativa de repositórios
  - Filtragem por tipo de arquivo
  - Paralelização com controle de rate limiting
  - Sistema de retry para operações falhas

- **Revisor Geral** (`tools/revisor_geral.py`)
  - Integração com OpenAI API
  - Carregamento dinâmico de prompts
  - Configuração flexível de modelos
  - Tratamento de erros de API

- **API REST** (em `teste_git_hub.py`)
  - Endpoint `/executar_analise` para análises
  - Validação de parâmetros de entrada
  - Resposta estruturada em JSON
  - Tratamento de exceções

### Tipos de Análise Suportados
- `design` - Análise de arquitetura e padrões de código
- `pentest` - Análise de penetration testing
- `seguranca` - Análise de segurança geral
- `terraform` - Análise de infraestrutura como código

### Linguagens e Tecnologias Suportadas
- **Python** (`.py`)
- **Terraform** (`.tf`, `.tfvars`)
- **CloudFormation** (`.json`, `.yaml`, `.yml`)
- **Ansible** (`.yml`, `.yaml`)
- **Docker** (`Dockerfile`)

### Configuração e Ambiente
- Suporte para Google Colab com userdata
- Configuração via variáveis de ambiente
- Logging configurável
- Controle de paralelismo e timeouts

---

## Tipos de Mudanças

- `Adicionado` para novas funcionalidades
- `Alterado` para mudanças em funcionalidades existentes
- `Descontinuado` para funcionalidades que serão removidas
- `Removido` para funcionalidades removidas
- `Corrigido` para correções de bugs
- `Segurança` para vulnerabilidades corrigidas

## Links de Comparação

- [Não Lançado]: https://github.com/LucioFlavioRosa/agent-vinna/compare/v1.0.0...HEAD
- [1.0.0]: https://github.com/LucioFlavioRosa/agent-vinna/releases/tag/v1.0.0