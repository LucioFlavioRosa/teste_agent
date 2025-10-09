# -*- coding: utf-8 -*-
from infrastructure.config.colab_config_provider import ColabConfigProvider
from infrastructure.repositories.github_repository import GitHubRepository
from infrastructure.llm.openai_provider import OpenAIProvider
from infrastructure.prompt.prompt_loader import PromptLoader
from application.services.code_fetcher_service import CodeFetcherService
from application.services.analysis_orchestrator import AnalysisOrchestrator
from domain.models.analysis_request import AnalysisRequest
from application.validators.analysis_request_validator import AnalysisRequestValidator

from flask import Flask, request, jsonify
import traceback

app = Flask(__name__)

config_provider = ColabConfigProvider()
github_repo = GitHubRepository(config_provider)
llm_provider = OpenAIProvider(config_provider)
prompt_loader = PromptLoader('tools/prompt')
code_fetcher_service = CodeFetcherService(github_repo)
orchestrator = AnalysisOrchestrator(code_fetcher_service, llm_provider, prompt_loader)
validator = AnalysisRequestValidator()

@app.route('/executar_analise', methods=['POST'])
def rodar_analise():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Corpo da requisição inválido ou não é um JSON."}), 400
    analysis_type = dados.get('tipo_analise')
    repo_name = dados.get('repositorio')
    code = dados.get('codigo')
    extra_instructions = dados.get('instrucoes_extras', '')
    model_name = dados.get('model_name', 'gpt-4.1')
    max_tokens = dados.get('max_tokens', 3000)
    code_source = code if code else github_repo.fetch_code(repo_name, {'extensions': None})
    request_obj = AnalysisRequest(analysis_type, code_source, extra_instructions, model_name, max_tokens)
    errors = validator.validate(request_obj)
    if errors:
        return jsonify({"erro": errors}), 400
    try:
        result = orchestrator.execute_analysis(request_obj)
        return jsonify({"tipo_analise": result.analysis_type, "resultado": result.result}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"erro": f"Ocorreu um erro interno no servidor: {e}"}), 500

@app.route("/")
def index():
    return "<h1>Servidor de Agentes de IA está no ar!</h1><p>Use o endpoint <b>/executar_analise</b> via POST para rodar uma análise.</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
