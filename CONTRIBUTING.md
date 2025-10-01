# Guia de Contribuição - Agent Vinna

## 🎯 Como Contribuir

Obrigado por seu interesse em contribuir com o Agent Vinna! Este documento fornece diretrizes para contribuições efetivas.

## 📋 Código de Conduta

Ao participar deste projeto, você concorda em manter um ambiente respeitoso e inclusivo para todos os colaboradores.

## 🚀 Primeiros Passos

### 1. Fork e Clone

bash
# Fork o repositório no GitHub
# Clone seu fork
git clone https://github.com/SEU_USUARIO/agent-vinna.git
cd agent-vinna

# Adicione o repositório original como upstream
git remote add upstream https://github.com/LucioFlavioRosa/agent-vinna.git


### 2. Configuração do Ambiente

bash
# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais


### 3. Configuração de Desenvolvimento

bash
# Instale dependências de desenvolvimento
pip install pytest pytest-cov black flake8 mypy

# Configure pre-commit hooks (opcional)
pip install pre-commit
pre-commit install


## 🔄 Fluxo de Trabalho

### 1. Sincronize com Upstream

bash
git fetch upstream
git checkout main
git merge upstream/main


### 2. Crie uma Branch

bash
# Use nomes descritivos
git checkout -b feature/nova-funcionalidade
# ou
git checkout -b fix/correcao-bug
# ou
git checkout -b docs/atualizacao-readme


### 3. Faça suas Alterações

- Mantenha commits pequenos e focados
- Use mensagens de commit descritivas
- Siga os padrões de código estabelecidos

### 4. Teste suas Alterações

bash
# Execute os testes
python -m pytest

# Verifique a cobertura
python -m pytest --cov=agents --cov=tools

# Execute linting
flake8 agents/ tools/
black --check agents/ tools/
mypy agents/ tools/


### 5. Commit e Push

bash
git add .
git commit -m "feat: adiciona nova funcionalidade X"
git push origin feature/nova-funcionalidade


### 6. Abra um Pull Request

- Use o template de PR fornecido
- Descreva claramente as mudanças
- Referencie issues relacionadas
- Aguarde revisão dos mantenedores

## 📝 Padrões de Código

### Python

- **Formatação**: Use `black` para formatação automática
- **Linting**: Siga as regras do `flake8`
- **Type Hints**: Use type hints sempre que possível
- **Docstrings**: Documente funções e classes públicas
- **Imports**: Organize imports seguindo PEP 8

### Exemplo de Código

python
from typing import Dict, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def processar_dados(dados: Dict[str, str], 
                   opcoes: Optional[List[str]] = None) -> Dict[str, str]:
    """
    Processa dados de entrada aplicando transformações.
    
    Args:
        dados: Dicionário com dados de entrada
        opcoes: Lista opcional de opções de processamento
        
    Returns:
        Dicionário com dados processados
        
    Raises:
        ValueError: Se dados estiverem em formato inválido
    """
    if not dados:
        raise ValueError("Dados não podem estar vazios")
        
    logger.info(f"Processando {len(dados)} itens")
    # Lógica de processamento...
    return dados


### Mensagens de Commit

Use o padrão Conventional Commits:

- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Mudanças na documentação
- `style:` - Formatação, sem mudanças de código
- `refactor:` - Refatoração de código
- `test:` - Adição ou correção de testes
- `chore:` - Tarefas de manutenção

Exemplos:

feat: adiciona suporte para análise de JavaScript
fix: corrige erro de timeout na API do GitHub
docs: atualiza README com instruções de instalação
refactor: melhora estrutura do módulo github_reader


## 🧪 Testes

### Executando Testes

bash
# Todos os testes
python -m pytest

# Testes específicos
python -m pytest tests/test_agente_revisor.py

# Com cobertura
python -m pytest --cov=agents --cov=tools --cov-report=html


### Escrevendo Testes

- Use `pytest` como framework
- Mantenha cobertura acima de 80%
- Teste casos de sucesso e erro
- Use mocks para APIs externas

## 📚 Tipos de Contribuição

### 🐛 Reportar Bugs

- Use o template de issue para bugs
- Inclua passos para reproduzir
- Forneça informações do ambiente
- Adicione logs relevantes

### 💡 Sugerir Funcionalidades

- Use o template de issue para features
- Descreva o problema que resolve
- Proponha uma solução
- Considere alternativas

### 📖 Melhorar Documentação

- Corrija erros de digitação
- Adicione exemplos
- Melhore clareza das instruções
- Traduza conteúdo

### 🔧 Contribuir com Código

- Corrija bugs reportados
- Implemente novas funcionalidades
- Melhore performance
- Adicione testes

## 🔍 Processo de Revisão

### Para Contribuidores

1. Aguarde feedback dos mantenedores
2. Responda a comentários construtivamente
3. Faça alterações solicitadas
4. Mantenha a branch atualizada

### Para Revisores

1. Seja construtivo e respeitoso
2. Foque na qualidade do código
3. Verifique testes e documentação
4. Aprove quando satisfeito

## 🏷️ Labels e Milestones

### Labels Comuns

- `bug` - Correção de bugs
- `enhancement` - Nova funcionalidade
- `documentation` - Melhorias na documentação
- `good first issue` - Boa para iniciantes
- `help wanted` - Precisa de ajuda da comunidade

## 🎉 Reconhecimento

Todos os contribuidores são reconhecidos:

- Nome no arquivo CONTRIBUTORS.md
- Menção em releases relevantes
- Agradecimento nas redes sociais

## 📞 Contato

Dúvidas sobre contribuições?

- Abra uma issue com a label `question`
- Entre em contato com os mantenedores
- Participe das discussões no GitHub

---

**Obrigado por contribuir com o Agent Vinna! 🚀**