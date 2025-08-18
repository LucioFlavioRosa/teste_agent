# Guia de Contribuição

Obrigado pelo interesse em contribuir com nosso projeto! Este documento fornece diretrizes para contribuir de forma eficaz.

## Fluxo de Contribuição

1. **Fork do repositório**
   - Crie um fork do repositório para sua conta

2. **Clone o fork**
   bash
   git clone https://github.com/seu-usuario/nome-do-repo.git
   cd nome-do-repo
   

3. **Crie uma branch**
   - Para novas funcionalidades:
     bash
     git checkout -b feat/nome-da-funcionalidade
     
   - Para correções de bugs:
     bash
     git checkout -b fix/descricao-do-bug
     
   - Para melhorias de documentação:
     bash
     git checkout -b docs/descricao-da-melhoria
     
   - Para refatorações:
     bash
     git checkout -b refactor/descricao-da-refatoracao
     

4. **Faça suas alterações**
   - Implemente as mudanças necessárias
   - Adicione ou atualize testes conforme apropriado
   - Atualize a documentação se necessário

5. **Commit das alterações**
   - Siga a convenção de Conventional Commits (veja abaixo)

6. **Push para o seu fork**
   bash
   git push origin nome-da-sua-branch
   

7. **Abra um Pull Request**
   - Vá para o repositório original e abra um PR da sua branch para a main
   - Preencha o template de PR com todas as informações necessárias

## Convenção de Commits

Usamos o padrão [Conventional Commits](https://www.conventionalcommits.org/) para mensagens de commit:


<tipo>[escopo opcional]: <descrição>

[corpo opcional]

[rodapé(s) opcional(is)]


### Tipos de Commit

- **feat**: Uma nova funcionalidade
- **fix**: Correção de um bug
- **docs**: Alterações apenas na documentação
- **style**: Alterações que não afetam o significado do código (espaços em branco, formatação, etc)
- **refactor**: Alteração de código que não corrige um bug nem adiciona uma funcionalidade
- **perf**: Alteração de código que melhora o desempenho
- **test**: Adição ou correção de testes
- **build**: Alterações no sistema de build ou dependências externas
- **ci**: Alterações nos arquivos de configuração de CI
- **chore**: Outras alterações que não modificam arquivos de código ou de teste

### Exemplos


feat(agente): adiciona suporte para análise de código Java

fix(github): corrige erro na leitura de repositórios privados

docs: atualiza instruções de instalação no README


## Padrões de Código

### Formatação

- Usamos **black** para formatação de código Python
  bash
  black .
  

- Usamos **isort** para ordenar imports
  bash
  isort .
  

### Linting

- Usamos **flake8** para verificar a qualidade do código
  bash
  flake8
  

### Tipagem

- Usamos anotações de tipo (type hints) em todas as funções e métodos
- Verificamos a tipagem com **mypy**
  bash
  mypy .
  

## Preparando o Ambiente Local

1. Instale as dependências de desenvolvimento:
   bash
   pip install -r requirements-dev.txt
   

2. Configure os hooks de pre-commit:
   bash
   pre-commit install
   

## Antes de Submeter um PR

Execute a seguinte checklist:

1. Rode os linters e formatadores:
   bash
   black .
   isort .
   flake8
   mypy .
   

2. Execute os testes:
   bash
   pytest
   

3. Verifique se a documentação foi atualizada, se necessário

4. Verifique se todas as alterações têm testes correspondentes

## Checklist para PRs

- [ ] O código segue os padrões de estilo do projeto
- [ ] Todos os testes estão passando
- [ ] A documentação foi atualizada, se necessário
- [ ] As alterações têm testes correspondentes
- [ ] O código foi revisado por pelo menos uma pessoa
- [ ] As mensagens de commit seguem a convenção Conventional Commits
- [ ] O PR está vinculado a uma issue

## Dúvidas?

Se você tiver dúvidas sobre o processo de contribuição, abra uma issue com o label "question" ou entre em contato com os mantenedores do projeto.