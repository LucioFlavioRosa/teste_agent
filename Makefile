# Makefile para automação de testes e desenvolvimento

.PHONY: help install test test-unit test-integration test-all coverage lint format clean docker-test

# Variáveis
PYTHON := python3
PIP := pip3
PYTEST := pytest
DOCKER_COMPOSE := docker-compose

# Cores para output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Mostra esta mensagem de ajuda
	@echo "$(BLUE)Comandos disponíveis:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Instala dependências de produção
	@echo "$(YELLOW)Instalando dependências de produção...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Dependências instaladas com sucesso!$(NC)"

install-dev: ## Instala dependências de desenvolvimento e teste
	@echo "$(YELLOW)Instalando dependências de desenvolvimento...$(NC)"
	$(PIP) install -r requirements.txt -r requirements-test.txt
	@echo "$(GREEN)Dependências de desenvolvimento instaladas!$(NC)"

test-unit: ## Executa apenas testes unitários
	@echo "$(YELLOW)Executando testes unitários...$(NC)"
	$(PYTEST) tests/ -m "not integration" -v

test-integration: ## Executa apenas testes de integração
	@echo "$(YELLOW)Executando testes de integração...$(NC)"
	$(PYTEST) tests/integration/ -m integration -v

test: test-unit ## Executa testes unitários (padrão)

test-all: ## Executa todos os testes (unitários + integração)
	@echo "$(YELLOW)Executando todos os testes...$(NC)"
	$(PYTEST) tests/ -v

coverage: ## Executa testes com relatório de cobertura
	@echo "$(YELLOW)Executando testes com cobertura...$(NC)"
	$(PYTEST) tests/ --cov=tools --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)Relatório de cobertura gerado em htmlcov/index.html$(NC)"

lint: ## Executa análise de código (flake8, mypy)
	@echo "$(YELLOW)Executando análise de código...$(NC)"
	flake8 tools/ tests/ --max-line-length=120 --exclude=__pycache__
	mypy tools/ --ignore-missing-imports
	bandit -r tools/ -f json -o bandit-report.json || true
	@echo "$(GREEN)Análise de código concluída!$(NC)"

format: ## Formata código com black e isort
	@echo "$(YELLOW)Formatando código...$(NC)"
	black tools/ tests/ --line-length=120
	isort tools/ tests/ --profile black
	@echo "$(GREEN)Código formatado!$(NC)"

format-check: ## Verifica formatação sem modificar arquivos
	@echo "$(YELLOW)Verificando formatação...$(NC)"
	black tools/ tests/ --line-length=120 --check --diff
	isort tools/ tests/ --profile black --check-only --diff

docker-build: ## Constrói imagem Docker para testes
	@echo "$(YELLOW)Construindo imagem Docker para testes...$(NC)"
	docker build -f Dockerfile.test -t code-analyzer-test .
	@echo "$(GREEN)Imagem Docker construída!$(NC)"

docker-test: ## Executa testes em ambiente Docker
	@echo "$(YELLOW)Executando testes em ambiente Docker...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.test.yml up --build --abort-on-container-exit
	$(DOCKER_COMPOSE) -f docker-compose.test.yml down -v
	@echo "$(GREEN)Testes Docker concluídos!$(NC)"

docker-test-integration: ## Executa apenas testes de integração no Docker
	@echo "$(YELLOW)Executando testes de integração no Docker...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.test.yml run --rm app-test pytest tests/integration/ -v
	$(DOCKER_COMPOSE) -f docker-compose.test.yml down -v

clean: ## Remove arquivos temporários e cache
	@echo "$(YELLOW)Limpando arquivos temporários...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf bandit-report.json
	@echo "$(GREEN)Limpeza concluída!$(NC)"

setup-dev: install-dev ## Configura ambiente de desenvolvimento completo
	@echo "$(YELLOW)Configurando ambiente de desenvolvimento...$(NC)"
	pre-commit install || echo "pre-commit não disponível, pulando..."
	@echo "$(GREEN)Ambiente de desenvolvimento configurado!$(NC)"

ci: format-check lint test-all ## Executa pipeline de CI (formatação, lint, testes)
	@echo "$(GREEN)Pipeline de CI executada com sucesso!$(NC)"

validate: ## Valida configuração e dependências
	@echo "$(YELLOW)Validando configuração...$(NC)"
	$(PYTHON) -c "from tools.config import config; print('Configuração válida!')"
	@echo "$(GREEN)Configuração validada!$(NC)"

# Comandos de desenvolvimento rápido
dev-test: ## Executa testes em modo de desenvolvimento (rápido)
	$(PYTEST) tests/ -x -v --tb=short

dev-watch: ## Executa testes em modo watch (reexecuta quando arquivos mudam)
	$(PYTEST) tests/ -f --tb=short

# Comandos para análise específica
test-github: ## Testa apenas integração com GitHub
	$(PYTEST) tests/integration/test_github_integration.py -v

test-openai: ## Testa apenas integração com OpenAI
	$(PYTEST) tests/integration/test_revisor_integration.py -v

test-e2e: ## Executa apenas testes end-to-end
	$(PYTEST) tests/integration/test_end_to_end.py -v
