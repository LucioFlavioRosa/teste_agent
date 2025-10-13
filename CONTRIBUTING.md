# Guia de Contribuição

Obrigado por contribuir com o Agent Vinna!

## Fluxo de Trabalho GitFlow Simplificado
- **Branches:**
  - Use sempre o padrão: `tipo/JIRA-ID-descricao-curta` (ex: `feature/AP-1234-integracao-github`)
  - Tipos: `feature`, `fix`, `hotfix`, `refactor`, `docs`
- **Atualização antes do PR:**
  - Sempre rebase sua branch com `develop` antes do Pull Request:
    bash
    git pull --rebase origin develop
    

## Processo de Pull Request
- Use o template padrão (`.github/pull_request_template.md`)
- Aguarde pelo menos 1 hora para revisão
- Inclua link para issue/JIRA
- Checklist obrigatório:
  - [ ] Testes passam localmente
  - [ ] Código revisado
  - [ ] Sem segredos hardcoded
  - [ ] Documentação atualizada
  - [ ] Rebase com `develop` realizado

## Padrões de Código Python
- Siga rigorosamente a [PEP 8](https://peps.python.org/pep-0008/)
- Utilize docstrings e comentários claros
- Prefira nomes descritivos para variáveis e funções

## Convenções de Commit
- Mensagens no imperativo e em português
- Inclua o ID do JIRA quando aplicável
- Exemplo: `feat(AP-1234): adiciona integração com GitHub`

## Aprovação de Release
- Toda release para produção requer aprovação do CAB
- Apresente as mudanças e plano de rollback na reunião de segunda-feira
- Releases em produção: terça-feira, 22:00-23:00 (quinzenal)
