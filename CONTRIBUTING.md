# Guia de Contribuição

Bem-vindo! Este documento orienta como contribuir para o Agent-Vinna seguindo os padrões da Protecta Seguros.

## Fluxo de Trabalho GitFlow Simplificado
- **Branches:** Use o formato `tipo/JIRA-ID-descricao-curta`.
  - Exemplos: `feature/AP-1234-integracao-github`, `fix/AP-5678-corrige-leitura-token`
  - Tipos permitidos: `feature`, `fix`, `hotfix`, `refactor`, `docs`
- **Sincronização:** Antes do Pull Request, atualize sua branch com `develop` usando:
  bash
  git pull --rebase origin develop
  
- **Pull Requests:** Sempre crie PRs para `develop`.

## Processo de Contribuição
1. **Fork** o repositório
2. Crie uma branch seguindo a nomenclatura acima
3. Implemente sua contribuição
4. Adicione/atualize testes conforme necessário
5. Abra um Pull Request usando o template padrão
6. Aguarde revisão e aprovação do Tech Lead/CAB

## Padrões de Código Python
- Siga o [PEP 8](https://peps.python.org/pep-0008/) para estilo
- Use docstrings para funções e módulos
- Evite código duplicado e complexidade desnecessária
- Priorize legibilidade e clareza

## Testes
- Utilize `pytest` ou similar
- Todo novo código deve ser coberto por testes automatizados
- Inclua instruções de como rodar os testes no PR

## Processo de Revisão
- PRs devem passar por revisão de pelo menos um Tech Lead
- Checklist de validação:
  - [ ] Testes passaram
  - [ ] Código revisado
  - [ ] Documentação atualizada
  - [ ] Sem secrets ou credenciais expostos

## Política de Releases
- Releases são quinzenais, às terças-feiras (22:00-23:00 BRT), após aprovação do CAB
- Consulte o [CHANGELOG.md](CHANGELOG.md) para histórico de mudanças

## Dúvidas?
Abra uma issue ou entre em contato com o Tech Lead do projeto.
