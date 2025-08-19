# Guia de Contribuição

Obrigado pelo interesse em contribuir para o nosso projeto! Este documento fornece as diretrizes e o fluxo de trabalho para contribuir de forma eficaz.

## Configuração do Ambiente de Desenvolvimento

1. **Clone o repositório**:
   bash
   git clone https://github.com/LucioFlavioRosa/agent-vinna.git
   cd agent-vinna
   

2. **Configure as variáveis de ambiente**:
   - Copie o arquivo `.env.example` para `.env`
   - Preencha todas as variáveis necessárias, especialmente:
     - `OPENAI_API_KEY` - Sua chave de API da OpenAI
     - `GITHUB_TOKEN` - Token de acesso ao GitHub com permissões para leitura de repositórios

3. **Instale as dependências**:
   bash
   pip install -r requirements.txt
   

## Fluxo de Trabalho para Pull Requests

1. **Crie uma branch para sua feature ou correção**:
   bash
   git checkout -b feature/nome-da-feature
   
   ou
   bash
   git checkout -b fix/nome-do-bug
   

2. **Desenvolva e teste suas alterações localmente**

3. **Execute os testes para garantir que tudo está funcionando**:
   bash
   pytest -v
   

4. **Faça commit das suas alterações**:
   bash
   git add .
   git commit -m "Descrição clara e concisa das alterações"
   

5. **Envie sua branch para o repositório remoto**:
   bash
   git push origin feature/nome-da-feature
   

6. **Abra um Pull Request** no GitHub com as seguintes informações:
   - Título claro e descritivo
   - Descrição detalhada das alterações
   - Referência a issues relacionadas (se aplicável)

## Padrões de Código

1. **Estilo de código**:
   - Siga o PEP 8 para código Python
   - Use nomes descritivos para variáveis e funções
   - Documente funções e classes com docstrings

2. **Testes**:
   - Adicione testes para novas funcionalidades
   - Garanta que todos os testes existentes continuem passando

3. **Commits**:
   - Use mensagens de commit claras e descritivas
   - Prefixe suas mensagens com o tipo de alteração (feat, fix, docs, etc.)

## Revisão de Código

- Seu código será revisado por pelo menos um mantenedor do projeto
- Esteja aberto a feedback e disposto a fazer ajustes quando necessário
- Responda a comentários e perguntas de forma construtiva

## Relatando Bugs

Se você encontrar um bug, por favor, abra uma issue usando o template fornecido, incluindo:

- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs. comportamento atual
- Ambiente (sistema operacional, versão do Python, etc.)

## Dúvidas e Suporte

Se você tiver dúvidas sobre o processo de contribuição ou precisar de ajuda, sinta-se à vontade para abrir uma issue com a tag "question" ou entrar em contato com os mantenedores do projeto.

Agradecemos sua contribuição para tornar este projeto melhor!