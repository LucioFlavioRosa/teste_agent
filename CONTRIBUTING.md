# Guia de Contribuição

Bem-vindo(a)! Siga estas diretrizes para contribuir com o Agent-Vinna.

## Fluxo de Trabalho GitFlow Simplificado
- **Branches:**
  - Use o formato: `tipo/JIRA-ID-descricao-curta`
    - Exemplos: `feature/AP-1234-integracao-github`, `fix/AP-5678-corrige-bug-token`
  - Tipos válidos: `feature`, `fix`, `hotfix`, `refactor`, `docs`
- **Atualização da branch:**
  - Antes do Pull Request, atualize sua branch com `develop` usando:
    bash
    git pull --rebase origin develop
    

## Processo de Pull Request
- Use o template padrão (`.github/pull_request_template.md`).
- Aguarde pelo menos 1 hora para revisão após abrir o PR.
- Inclua link para issue ou JIRA no PR.
- Checklist obrigatório:
  - Testes passando
  - Código revisado
  - Sem segredos hardcoded
  - Documentação atualizada
  - Confirmação de rebase com `develop`

## Padrões de Código Python
- Siga a [PEP 8](https://peps.python.org/pep-0008/).
- Use nomes descritivos para variáveis, funções e classes.
- Documente funções e módulos com docstrings.

## Convenções de Commit
- Mensagens no formato:
  - `<tipo>: <mensagem curta>`
  - Exemplo: `fix: corrige leitura do token do GitHub`

## Aprovação de Release em Produção
- Releases para produção exigem aprovação do CAB (Change Approval Board).
- O Tech Lead deve apresentar as mudanças e plano de rollback.
- Releases ocorrem quinzenalmente às terças-feiras, 22:00-23:00 (horário de Brasília).
