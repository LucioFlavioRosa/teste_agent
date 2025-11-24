# Guia de Contribuição

Obrigado por considerar contribuir para este projeto! Este documento fornece diretrizes para ajudar você a contribuir de forma eficaz.

## Fluxo de Trabalho para Pull Requests

1. **Fork do Repositório**: Crie um fork do repositório para sua conta.

2. **Clone Local**: Clone o fork para sua máquina local.
   bash
   git clone https://github.com/seu-usuario/agent-vinna.git
   cd agent-vinna
   

3. **Crie uma Branch**: Crie uma branch para sua contribuição.
   bash
   git checkout -b feature/nome-da-sua-feature
   

4. **Faça suas Alterações**: Implemente suas mudanças seguindo os padrões de código.

5. **Teste suas Alterações**: Certifique-se de que seus testes passam.
   bash
   pytest -v
   

6. **Commit das Alterações**: Faça commit das suas alterações com mensagens claras.
   bash
   git commit -m "Adiciona funcionalidade X que resolve o problema Y"
   

7. **Push para o GitHub**: Envie suas alterações para seu fork.
   bash
   git push origin feature/nome-da-sua-feature
   

8. **Abra um Pull Request**: Vá até o repositório original e abra um PR da sua branch para a branch principal.

## Padrões de Código

### Python

- Siga a PEP 8 para estilo de código.
- Use tipagem estática com `typing` sempre que possível.
- Documente funções e classes usando docstrings no formato Google Style.
- Mantenha funções pequenas e com responsabilidade única.

### Testes

- Escreva testes unitários para novas funcionalidades.
- Mantenha a cobertura de testes acima de 80%.
- Use `pytest` para executar os testes.

## Configuração do Ambiente de Desenvolvimento

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Acesso à API da OpenAI (para obter uma chave API)
- Acesso ao GitHub (para obter um token de acesso)

### Configuração Inicial

1. **Instale as Dependências**:
   bash
   pip install -r requirements.txt
   

2. **Configure as Variáveis de Ambiente**:
   Crie um arquivo `.env` baseado no `.env.example` e preencha com suas credenciais.

3. **Verifique a Instalação**:
   bash
   python -m pytest -v
   

## Reportando Bugs

Use o template de issue fornecido em `.github/ISSUE_TEMPLATE.md` para reportar bugs. Forneça o máximo de detalhes possível, incluindo passos para reproduzir o problema.

## Propondo Melhorias

Sugestões de melhorias são sempre bem-vindas! Abra uma issue descrevendo sua proposta antes de começar a trabalhar nela, para garantir que ela se alinha com os objetivos do projeto.

## Dúvidas?

Se você tiver alguma dúvida sobre como contribuir, sinta-se à vontade para abrir uma issue pedindo esclarecimentos.
