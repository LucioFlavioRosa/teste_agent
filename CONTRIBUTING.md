# Guia de Contribuição

Obrigado por considerar contribuir para este projeto! Este documento fornece as diretrizes e o fluxo de trabalho para contribuir efetivamente.

## Configurando o Ambiente de Desenvolvimento

1. **Clone o repositório**:
   bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
   

2. **Configure as variáveis de ambiente**:
   - Copie o arquivo `.env.example` para `.env`
   - Preencha as variáveis necessárias, incluindo:
     - `OPENAI_API_KEY` - Sua chave de API da OpenAI
     - `GITHUB_TOKEN` - Token de acesso pessoal do GitHub

3. **Instale as dependências**:
   bash
   pip install -r requirements.txt
   

## Fluxo de Trabalho para Contribuições

1. **Crie uma branch para sua feature ou correção**:
   bash
   git checkout -b feature/nome-da-feature
   # ou
   git checkout -b fix/nome-do-bug
   

2. **Faça suas alterações seguindo os padrões de código**:
   - Use nomes descritivos para variáveis e funções
   - Adicione docstrings para funções e classes
   - Mantenha a consistência com o estilo de código existente
   - Adicione testes para novas funcionalidades

3. **Execute os testes**:
   bash
   pytest -v
   

4. **Commit suas alterações**:
   bash
   git add .
   git commit -m "Descrição clara e concisa das alterações"
   

5. **Envie para o repositório remoto**:
   bash
   git push origin feature/nome-da-feature
   

6. **Abra um Pull Request**:
   - Use um título claro e descritivo
   - Descreva as alterações realizadas
   - Referencie issues relacionadas usando #numero-da-issue

## Padrões de Código

- **Python**: Siga o PEP 8 para estilo de código
- **Docstrings**: Use o formato Google para documentação de funções e classes
- **Imports**: Organize imports em ordem alfabética e separe bibliotecas padrão, terceiros e módulos locais
- **Testes**: Escreva testes unitários para novas funcionalidades usando pytest

## Revisão de Código

Todos os Pull Requests serão revisados por pelo menos um mantenedor do projeto. O revisor pode solicitar alterações antes de aprovar e mesclar as alterações.

## Relatando Bugs

Use o template de issue fornecido para relatar bugs. Certifique-se de incluir:
- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs. comportamento atual
- Ambiente (sistema operacional, versão do Python, etc.)

## Propondo Novas Funcionalidades

Antes de implementar uma nova funcionalidade, abra uma issue para discutir a proposta. Isso ajuda a garantir que seu trabalho esteja alinhado com a direção do projeto.

---

Agradecemos suas contribuições para tornar este projeto melhor!