# Guia de Contribuição

Obrigado por considerar contribuir com este projeto!

## Fluxo de Trabalho GitFlow Simplificado

- **Branches** devem seguir o padrão: `tipo/JIRA-ID-descricao-curta`.
  - Exemplos: `feature/AP-1234-nova-funcionalidade`, `fix/AP-5678-corrige-bug`
  - Tipos: `feature`, `fix`, `hotfix`, `refactor`, `docs`
- Sempre atualize sua branch com `git pull --rebase origin develop` antes de abrir um Pull Request.
- Nunca use `git merge` para sincronizar com `develop`.

## Processo de Pull Request

- Utilize o template obrigatório (`.github/pull_request_template.md`).
- Limite de 400 linhas por PR.
- PRs devem permanecer abertos por no mínimo 1 hora antes de serem aprovados.
- É necessário pelo menos 1 aprovação de revisor.

## Padrões de Código Python

- Siga a [PEP 8](https://pep8.org/) para estilo de código.
- Utilize type hints sempre que possível.
- Prefira nomes descritivos para variáveis, funções e classes.
- Documente funções e módulos com docstrings.

## Testes

- Implemente testes automatizados para novas funcionalidades e correções.
- Utilize frameworks como `pytest`.
- Garanta cobertura mínima de 80%.

## Processo de Release

- Releases para produção só podem ser feitas após aprovação do Change Approval Board (CAB).
- O CAB se reúne às segundas-feiras; releases ocorrem quinzenalmente às terças-feiras, 22:00-23:00 (horário de Brasília).
- Siga o versionamento semântico (vMAJOR.MINOR.PATCH).

## Dúvidas?

Abra uma issue ou entre em contato com os mantenedores.
