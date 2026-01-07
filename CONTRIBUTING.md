# Guia de Contribuição

Obrigado por considerar contribuir para o nosso projeto! Este documento fornece diretrizes para ajudar você a contribuir efetivamente.

## Fluxo de Trabalho para Pull Requests

1. **Fork do Repositório**: Faça um fork do repositório principal para sua conta GitHub.

2. **Clone Local**: Clone seu fork para sua máquina local.
   bash
   git clone https://github.com/seu-usuario/nome-do-repositorio.git
   cd nome-do-repositorio
   

3. **Crie uma Branch**: Crie uma branch para sua contribuição.
   bash
   git checkout -b feature/sua-feature
   

4. **Desenvolva**: Faça suas alterações seguindo os padrões de código.

5. **Teste**: Certifique-se de que seus testes passam e adicione novos testes se necessário.
   bash
   pytest -v
   

6. **Commit**: Faça commits com mensagens claras e descritivas.
   bash
   git commit -m "Adiciona funcionalidade X que resolve o problema Y"
   

7. **Push**: Envie suas alterações para seu fork.
   bash
   git push origin feature/sua-feature
   

8. **Pull Request**: Abra um Pull Request para a branch principal do repositório original.

## Padrões de Código

### Python

- Siga o [PEP 8](https://www.python.org/dev/peps/pep-0008/) para estilo de código.
- Use tipagem estática quando possível.
- Documente funções e classes usando docstrings no formato Google ou NumPy.
- Mantenha funções pequenas e com responsabilidade única.

### Testes

- Escreva testes unitários para novas funcionalidades.
- Mantenha a cobertura de testes acima de 80%.
- Use `pytest` para executar os testes.

### Commits

- Use mensagens de commit claras e descritivas.
- Prefixe suas mensagens com o tipo de alteração: `feat:`, `fix:`, `docs:`, `test:`, etc.

## Configuração do Ambiente de Desenvolvimento

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git

### Configuração Inicial

1. **Instale as dependências**:
   bash
   pip install -r requirements.txt
   

2. **Configure as variáveis de ambiente**:
   - Copie o arquivo `.env.example` para `.env`
   - Preencha as variáveis necessárias

3. **Verifique a instalação**:
   bash
   pytest -v
   

## Reportando Bugs

Use o template de issue para reportar bugs. Inclua:

- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs. comportamento atual
- Capturas de tela, se aplicável
- Informações do ambiente (SO, versão do Python, etc.)

## Solicitando Funcionalidades

Para solicitar novas funcionalidades, abra uma issue usando o template apropriado e descreva:

- O problema que a funcionalidade resolve
- Comportamento esperado
- Possíveis implementações ou alternativas

## Dúvidas?

Se você tiver dúvidas sobre o processo de contribuição, abra uma issue com a tag "question" ou entre em contato com os mantenedores do projeto.

Agradecemos sua contribuição!