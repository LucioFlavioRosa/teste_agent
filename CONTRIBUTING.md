# Guia de Contribuição

## Como Contribuir para o Agent Vinna

Obrigado por seu interesse em contribuir! Este guia irá ajudá-lo a configurar o ambiente de desenvolvimento e entender nosso fluxo de trabalho.

## 🚀 Configuração do Ambiente de Desenvolvimento

### Pré-requisitos
- Python 3.8 ou superior
- Git
- Conta no GitHub
- Tokens de API (GitHub, OpenAI)

### Configuração Local

1. **Fork e Clone do Repositório**
   bash
   git clone https://github.com/SEU_USUARIO/agent-vinna.git
   cd agent-vinna
   

2. **Criação do Ambiente Virtual**
   bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   

3. **Instalação das Dependências**
   bash
   pip install -r requirements.txt
   

4. **Configuração das Variáveis de Ambiente**
   - Copie o arquivo `.env.example` para `.env`
   - Preencha as variáveis com seus tokens reais
   bash
   cp .env.example .env
   

## 📋 Padrões de Código

### Estilo de Código Python
- Seguimos o **PEP 8** para formatação
- Use **type hints** em todas as funções
- Docstrings obrigatórias para funções públicas
- Nomes de variáveis e funções em **snake_case**
- Nomes de classes em **PascalCase**
- Constantes em **UPPER_CASE**

### Estrutura de Commits

tipo(escopo): descrição breve

Descrição detalhada (opcional)

Fixes #numero_da_issue


**Tipos válidos:**
- `feat`: nova funcionalidade
- `fix`: correção de bug
- `docs`: alterações na documentação
- `style`: formatação, sem mudança de lógica
- `refactor`: refatoração de código
- `test`: adição ou correção de testes
- `chore`: tarefas de manutenção

### Exemplo de Commit

feat(agents): adiciona validação de entrada no agente revisor

Implementa validação robusta dos parâmetros de entrada,
incluindo verificação de tipos de análise válidos.

Fixes #123


## 🔄 Fluxo de Trabalho (Pull Requests)

### 1. Criação de Branch
bash
git checkout -b feature/nome-da-funcionalidade
# ou
git checkout -b fix/nome-do-bug


### 2. Desenvolvimento
- Faça commits pequenos e frequentes
- Teste suas alterações localmente
- Execute a suíte de testes antes de enviar

### 3. Testes
bash
# Execute todos os testes
pytest -v

# Execute testes com cobertura
pytest --cov=agents --cov=tools --cov-report=html


### 4. Envio do Pull Request
1. Push da branch para seu fork
   bash
   git push origin feature/nome-da-funcionalidade
   

2. Abra um Pull Request no GitHub com:
   - **Título claro** descrevendo a mudança
   - **Descrição detalhada** do que foi implementado
   - **Referência à issue** relacionada (se houver)
   - **Screenshots** (se aplicável)

### 5. Template do Pull Request
markdown
## Descrição
Descreva brevemente as mudanças implementadas.

## Tipo de Mudança
- [ ] Bug fix (correção que resolve um problema)
- [ ] Nova funcionalidade (mudança que adiciona funcionalidade)
- [ ] Breaking change (mudança que quebra compatibilidade)
- [ ] Documentação

## Como Testar
1. Passo 1
2. Passo 2
3. Resultado esperado

## Checklist
- [ ] Código segue os padrões do projeto
- [ ] Testes foram adicionados/atualizados
- [ ] Documentação foi atualizada
- [ ] Todos os testes passam


## 🧪 Executando Testes

### Testes Unitários
bash
# Todos os testes
pytest

# Testes específicos
pytest tests/test_agente_revisor.py

# Com verbose
pytest -v


### Testes de Integração
bash
# Testes que requerem API externa
pytest tests/integration/ -m "integration"


### Cobertura de Código
bash
pytest --cov=agents --cov=tools --cov-report=term-missing


## 📝 Reportando Issues

### Bugs
- Use o template de bug report
- Inclua steps para reproduzir
- Adicione logs de erro
- Especifique versão do Python e dependências

### Solicitações de Funcionalidade
- Descreva o problema que a funcionalidade resolve
- Proponha uma solução
- Considere alternativas

## 🤝 Código de Conduta

- Seja respeitoso e inclusivo
- Aceite feedback construtivo
- Foque no que é melhor para a comunidade
- Mantenha discussões técnicas e profissionais

## 📞 Contato

Dúvidas? Abra uma issue ou entre em contato com os mantenedores.

---

**Obrigado por contribuir para o Agent Vinna! 🚀**