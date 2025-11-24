# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/spec/v2.0.0.html).

## [Não Lançado]

### Adicionado
- Documentação completa do projeto, incluindo README.md, CONTRIBUTING.md e templates de issues
- Arquivo de exemplo para variáveis de ambiente (.env.example)
- Instruções de deploy para Azure App Service

## [0.1.0] - 2023-06-15

### Adicionado
- Implementação inicial do agente revisor
- Suporte para análise de código via repositório GitHub
- Tipos de análise: design, pentest, segurança e terraform
- API REST com Flask para acesso aos agentes
- Integração com a API da OpenAI para análise de código

### Corrigido
- Tratamento de erros na leitura de repositórios GitHub
- Validação de parâmetros de entrada na API

### Alterado
- Refatoração da estrutura de diretórios para melhor organização
- Melhoria nos prompts de análise para resultados mais precisos
