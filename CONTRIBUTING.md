# Guia de Contribuição

Obrigado por considerar contribuir para este projeto! Este documento fornece diretrizes para contribuir efetivamente com nosso código, que será executado no Azure App Service.

## Fluxo de Trabalho de Contribuição

### 1. Configuração Inicial

1. **Fork o repositório** para sua conta GitHub
2. **Clone seu fork** localmente:
   bash
   git clone https://github.com/SEU-USUARIO/NOME-DO-REPO.git
   cd NOME-DO-REPO
   
3. **Adicione o repositório upstream**:
   bash
   git remote add upstream https://github.com/USUARIO-ORIGINAL/NOME-DO-REPO.git
   

### 2. Mantendo seu Fork Atualizado

bash
git fetch upstream
git checkout main
git merge upstream/main
git push origin main


### 3. Criando uma Feature

1. **Crie uma branch** para sua feature:
   bash
   git checkout -b feature/nome-da-feature
   
2. **Implemente suas mudanças** seguindo os padrões de código
3. **Commit suas alterações** com mensagens claras:
   bash
   git commit -m "feat: adiciona funcionalidade X que resolve Y"
   

### 4. Enviando um Pull Request

1. **Push da sua branch** para seu fork:
   bash
   git push origin feature/nome-da-feature
   
2. **Abra um Pull Request** no GitHub
3. **Preencha o template** de PR com todas as informações necessárias

## Configuração do Ambiente de Desenvolvimento

### Requisitos

- Python 3.8+
- pip
- Acesso ao Azure (para testes de integração com App Service)

### Configuração Local

1. **Instale as dependências**:
   bash
   pip install -r requirements.txt
   

2. **Configure as variáveis de ambiente**:
   - Copie o arquivo `.env.example` para `.env`
   - Preencha as variáveis necessárias

3. **Execute a aplicação localmente**:
   bash
   python app.py
   

## Padrões de Código

### Estilo de Código

- Siga a [PEP 8](https://www.python.org/dev/peps/pep-0008/) para código Python
- Use docstrings no formato Google para documentação de funções e classes
- Mantenha linhas com no máximo 100 caracteres

### Testes

- Escreva testes unitários para novas funcionalidades
- Garanta que todos os testes passem antes de submeter um PR:
  bash
  pytest
  

### Commits

Siga o padrão [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` para novas funcionalidades
- `fix:` para correções de bugs
- `docs:` para alterações na documentação
- `style:` para formatação de código
- `refactor:` para refatorações
- `test:` para adição/modificação de testes
- `chore:` para tarefas de manutenção

## Validação para Azure App Service

Antes de submeter seu PR, verifique se suas alterações são compatíveis com o Azure App Service:

1. **Teste localmente com configurações similares** ao ambiente de produção
2. **Verifique se as dependências** estão corretamente listadas no `requirements.txt`
3. **Confirme que as variáveis de ambiente** necessárias estão documentadas
4. **Teste o deploy em um ambiente de staging** se possível

## Dúvidas e Suporte

Se tiver dúvidas sobre o processo de contribuição, abra uma issue com o label `question` ou entre em contato com os mantenedores do projeto.

Agradecemos sua contribuição para tornar este projeto melhor!