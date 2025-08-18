from flask import Flask, request, jsonify
from agents import agente_revisor
import os
import traceback

app = Flask(__name__)


@app.route('/executar_analise', methods=['POST'])
def rodar_analise():
    print("INFO: Requisição recebida no endpoint /executar_analise")

    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "Corpo da requisição inválido ou não é um JSON."}), 400

    tipo_analise = dados.get('tipo_analise')
    repositorio = dados.get('repositorio')
    codigo = dados.get('codigo')
    instrucoes_extras = dados.get('instrucoes_extras', '')
    model_name = dados.get('model_name', os.getenv('MODEL_NAME', 'gpt-4.1'))
    max_token_out = int(dados.get('max_token_out', os.getenv('MAX_TOKENS_OUT', '3000')))

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
            model_name=model_name,
            max_token_out=max_token_out
        )
        print("INFO: Análise concluída com sucesso.")
        return jsonify(resultado), 200

    except Exception as e:
        print(f"ERRO: A execução do agente falhou. Causa: {e}")
        traceback.print_exc()
        return jsonify({"erro": f"Ocorreu um erro interno no servidor: {e}"}), 500


@app.route("/")
def index():
    return ("<h1>Servidor de Agentes de IA está no ar!</h1>"
            "<p>Use o endpoint <b>/executar_analise</b> via POST para rodar uma análise.</p>")


if __name__ == '__main__':
    debug_env = os.getenv('FLASK_DEBUG', '0').lower()
    debug = debug_env in {'1', 'true', 'yes', 'on'}
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    app.run(host=host, port=port, debug=debug)
