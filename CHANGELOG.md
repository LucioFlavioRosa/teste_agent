# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não Lançado]

### Adicionado
- Documentação completa do projeto
- Guia de contribuição (`CONTRIBUTING.md`)
- Template de variáveis de ambiente (`.env.example`)
- Seção de testes no README
- Este arquivo de changelog

## [1.0.0] - 2024-01-XX

### Adicionado
- Agente revisor principal (`agente_revisor.py`)
- Leitor de repositórios GitHub (`github_reader.py`)
- Interface com OpenAI para análises (`revisor_geral.py`)
- Suporte para múltiplos tipos de análise:
  - Análise de design
  - Análise de segurança
  - Penetration testing
  - Análise de Terraform
- Servidor Flask para API REST
- Sistema de logging configurável
- Paralelização de leitura de arquivos
- Sistema de retry para operações de rede
- Validação robusta de parâmetros de entrada

### Funcionalidades
- Análise de repositórios GitHub completos
- Análise de código fornecido diretamente
- Suporte a instruções extras do usuário
- Filtragem por tipo de arquivo baseada na análise
- Tratamento de erros abrangente
- Configuração flexível via variáveis de ambiente

### Tipos de Arquivo Suportados
- **Terraform**: `.tf`, `.tfvars`
- **Python**: `.py`
- **CloudFormation**: `.json`, `.yaml`, `.yml`
- **Ansible**: `.yml`, `.yaml`
- **Docker**: `Dockerfile`

### API Endpoints
- `POST /executar_analise` - Executa análise de código
- `GET /` - Página de status do servidor

### Configurações
- Modelo LLM configurável (padrão: gpt-4.1)
- Limite de tokens de saída configurável
- Paralelismo configurável para leitura de arquivos
- Sistema de retry configurável
- Logging configurável

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