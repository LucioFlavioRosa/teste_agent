# Guia de Contribuição

Obrigado por considerar contribuir com o Agent-Vinna! Siga as diretrizes abaixo para garantir um fluxo de colaboração eficiente e alinhado às políticas da Protecta Seguros.

## Fluxo de Trabalho (GitFlow Simplificado)
- O branch `main` reflete a produção.
- O branch `develop` é a base para novas funcionalidades.
- Crie branches a partir de `develop`.

### Nomenclatura de Branches
- Formato: `tipo/JIRA-ID-descricao-curta`
- Tipos: `feature`, `fix`, `hotfix`, `refactor`, `docs`
- Exemplo: `feature/AP-1234-integracao-gateway-pagamento`

### Processo de Pull Request
- Use o template obrigatório (`.github/pull_request_template.md`).
- Limite máximo de 400 linhas por PR.
- PR deve permanecer aberto por no mínimo 1 hora antes do merge.
- Antes de abrir o PR, atualize sua branch com `develop` usando:
  bash
  git pull --rebase origin develop
  
- Adicione reviewers conforme necessário.

## Padrões de Código
- Siga o PEP 8 (Python).
- Utilize type hints sempre que possível.
- Documente funções e módulos com docstrings.

## Processo de Revisão
- Todos os PRs devem ser revisados por pelo menos um membro do time.
- Verifique se os testes passam e a cobertura não diminuiu.
- Não inclua secrets ou credenciais hardcoded.

## Dúvidas
Abra uma issue ou entre em contato com os mantenedores.
