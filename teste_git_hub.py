# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from agents import agente_revisor
from tools.revisor_geral import OpenAIClient, PromptRepositoryFS
from tools.github_reader import GithubRepositoryReader
import os
import traceback


app = Flask(__name__)

# Composição das dependências (injeção)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

llm_client = OpenAIClient(OPENAI_API_KEY) if OPENAI_API_KEY else None
repo_reader = GithubRepositoryReader(token=GITHUB_TOKEN)
prompt_repo = PromptRepositoryFS()


@app.route('/executar_analise', methods=['POST'])
def rodar_analise():
    print("INFO: Requisição recebida no endpoint /executar_analise")

    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Corpo da requisição inválido ou não é um JSON."}), 400

    tipo_analise = dados.get('tipo_analise')
    repositorio = dados.get('repositorio')
    codigo = dados.get('codigo')
    instrucoes_extras = dados.get('instrucoes_extras', '')

    if not tipo_analise:
        return jsonify({"erro": "O parâmetro 'tipo_analise' é obrigatório."}), 400
    if not repositorio and not codigo:
        return jsonify({"erro": "É obrigatório fornecer pelo menos um dos parâmetros: 'repositorio' ou 'codigo'."}), 400

    try:
        print(f"INFO: Iniciando análise do tipo '{tipo_analise}'...")

        resultado = agente_revisor.executar_analise(
            tipo_analise=tipo_analise,
            repositorio=repositorio,
            codigo=codigo,
            instrucoes_extras=instrucoes_extras,
            repo_reader=repo_reader,
            prompt_repo=prompt_repo,
            llm_client=llm_client,
        )

        print("INFO: Análise concluída com sucesso.")
        return jsonify(resultado), 200

    except Exception as e:
        print(f"ERRO: A execução do agente falhou. Causa: {e}")
        traceback.print_exc()
        return jsonify({"erro": f"Ocorreu um erro interno no servidor: {e}"}), 500


@app.route("/")
def index():
    return "<h1>Servidor de Agentes de IA está no ar!</h1><p>Use o endpoint <b>/executar_analise</b> via POST para rodar uma análise.</p>"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
