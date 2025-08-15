# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import logging
import os
import traceback
from agents import agente_revisor

# Configuração de logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)


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
        logger.info("Iniciando análise do tipo '%s'...", tipo_analise)

        resultado = agente_revisor.executar_analise(
            tipo_analise=tipo_analise,
            repositorio=repositorio,
            codigo=codigo,
            instrucoes_extras=instrucoes_extras
        )

        logger.info("Análise concluída com sucesso.")
        return jsonify(resultado), 200

    except Exception:
        logger.exception("A execução do agente falhou.")
        # Não vazar detalhes internos do erro ao cliente
        return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500


@app.route("/")
def index():
    return "<h1>Servidor de Agentes de IA está no ar!</h1><p>Use o endpoint <b>/executar_analise</b> via POST para rodar uma análise.</p>"


if __name__ == '__main__':
    debug_flag = os.getenv('FLASK_DEBUG', '0') == '1'
    port = int(os.getenv('PORT', '5000'))
    app.run(host='0.0.0.0', port=port, debug=debug_flag)
