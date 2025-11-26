# Agent Vinna - Sistema de Análise de Código com IA

## 📋 Sobre o Projeto

O Agent Vinna é um sistema inteligente de análise de código que utiliza IA para realizar auditorias automatizadas de repositórios GitHub. O sistema oferece diferentes tipos de análise incluindo design, segurança, penetration testing e infraestrutura como código (Terraform).

## 🚀 Funcionalidades

- **Análise de Design**: Avaliação da arquitetura e padrões de código
- **Análise de Segurança**: Identificação de vulnerabilidades e práticas inseguras
- **Penetration Testing**: Simulação de ataques para identificar falhas de segurança
- **Análise de Terraform**: Auditoria de infraestrutura como código
- **API REST**: Interface HTTP para integração com outros sistemas
- **Suporte Multi-linguagem**: Análise de projetos Python, JavaScript, Terraform e mais

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**
- **Flask** - Framework web
- **OpenAI GPT-4** - Modelo de linguagem para análises
- **PyGithub** - Integração com GitHub API
- **Google Colab** - Ambiente de execução (opcional)

## 📦 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- Conta no GitHub com token de acesso
- Chave da API OpenAI
- Git

### Passo a Passo

1. **Clone o repositório**
   bash
   git clone https://github.com/LucioFlavioRosa/agent-vinna.git
   cd agent-vinna
   

2. **Crie um ambiente virtual**
   bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   

3. **Instale as dependências**
   bash
   pip install -r requirements.txt
   

4. **Configure as variáveis de ambiente**
   bash
   cp .env.example .env
   # Edite o arquivo .env com suas credenciais
   

5. **Execute a aplicação**
   bash
   python teste_git_hub.py
   

## ⚙️ Configuração

### Variáveis de Ambiente

Configure as seguintes variáveis no arquivo `.env`:

- `OPENAI_API_KEY`: Sua chave da API OpenAI
- `GITHUB_TOKEN`: Token de acesso pessoal do GitHub
- `FLASK_ENV`: Ambiente de execução (development/production)
- `FLASK_DEBUG`: Modo debug (True/False)

### Configuração no Google Colab

Se estiver usando Google Colab, configure os secrets:

1. Acesse o painel de secrets no Colab
2. Adicione `OPENAI_API_KEY` com sua chave OpenAI
3. Adicione `github_token` com seu token GitHub

## 🔧 Uso

### API REST

A aplicação expõe uma API REST no endpoint `/executar_analise`:

bash
curl -X POST http://localhost:5000/executar_analise \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_analise": "pentest",
    "repositorio": "usuario/repositorio",
    "instrucoes_extras": "Foque em vulnerabilidades de autenticação"
  }'


### Parâmetros da API

- `tipo_analise` (obrigatório): Tipo de análise ("design", "pentest", "seguranca", "terraform")
- `repositorio` (opcional): Nome do repositório GitHub no formato "usuario/repo"
- `codigo` (opcional): Código fonte direto para análise
- `instrucoes_extras` (opcional): Instruções adicionais para a análise

### Uso Programático

python
from agents import agente_revisor

resultado = agente_revisor.executar_analise(
    tipo_analise='seguranca',
    repositorio='usuario/repositorio',
    instrucoes_extras='Verificar vulnerabilidades SQL injection'
)

print(resultado['resultado'])


## 🧪 Testes

bash
# Executar todos os testes
python -m pytest

# Executar testes com cobertura
python -m pytest --cov=agents --cov=tools

# Executar teste específico
python teste_git_hub.py


## 📁 Estrutura do Projeto


agent-vinna/
├── agents/
│   └── agente_revisor.py      # Agente principal de análise
├── tools/
│   ├── github_reader.py       # Leitor de repositórios GitHub
│   ├── revisor_geral.py       # Interface com OpenAI
│   └── prompts/               # Templates de prompts para análises
├── teste_git_hub.py           # Script de teste e aplicação Flask
├── requirements.txt           # Dependências do projeto
├── .env.example              # Exemplo de variáveis de ambiente
└── README.md                 # Este arquivo


## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, leia o [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes sobre nosso código de conduta e processo de submissão de pull requests.

## 📝 Changelog

Veja [CHANGELOG.md](CHANGELOG.md) para um histórico detalhado das mudanças.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

Se você encontrar algum problema ou tiver dúvidas:

1. Verifique as [Issues existentes](https://github.com/LucioFlavioRosa/agent-vinna/issues)
2. Crie uma nova issue se necessário
3. Entre em contato com os mantenedores

## 🔒 Segurança

Para relatar vulnerabilidades de segurança, por favor envie um email privado aos mantenedores ao invés de criar uma issue pública.

---

**Desenvolvido com ❤️ pela comunidade**