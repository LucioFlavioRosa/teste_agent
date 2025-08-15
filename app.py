from flask import Flask, request, jsonify
from agents import agente_revisor
import logging
import os


app = Flask(__name__)

# Configuração básica de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)


@app.route('/executar_analise', methods=['POST'])
def rodar_analise():
    logger.info("Requisição recebida no endpoint /executar_analise")

    dados = request.get_json(silent=True)

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
        logger.info("Iniciando análise do tipo '%s'", tipo_analise)

        resultado = agente_revisor.main(
            tipo_analise=tipo_analise,
            repositorio=repositorio,
            codigo=codigo,
            instrucoes_extras=instrucoes_extras
        )

        logger.info("Análise concluída com sucesso.")
        return jsonify(resultado), 200

    except Exception:
        logger.exception("A execução do agente falhou.")
        return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500


@app.route("/")
def index():
    return "<h1>Servidor de Agentes de IA está no ar!</h1><p>Use o endpoint <b>/executar_analise</b> via POST para rodar uma análise.</p>"


if __name__ == '__main__':
    debug_flag = os.getenv('FLASK_DEBUG', 'false').lower() in ('1', 'true', 'yes', 'on')
    port = int(os.getenv('PORT', '5000'))
    app.run(host='0.0.0.0', port=port, debug=debug_flag)
