# -*- coding: utf-8 -*-
"""Aplicação Flask para executar análises via agente.

Este arquivo foi ajustado para remover execução de análise no topo do módulo
(evitando efeitos colaterais na importação) e para padronizar logs via logging.
"""

import logging
from flask import Flask, request, jsonify
from agents import agente_revisor


# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)


@app.route('/executar_analise', methods=['POST'])
def rodar_analise():
    app.logger.info("Requisição recebida no endpoint /executar_analise")

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
        app.logger.info("Iniciando análise do tipo '%s'...", tipo_analise)

        resultado = agente_revisor.executar_analise(
            tipo_analise=tipo_analise,
            repositorio=repositorio,
            codigo=codigo,
            instrucoes_extras=instrucoes_extras
        )

        app.logger.info("Análise concluída com sucesso.")
        return jsonify(resultado), 200

    except Exception as e:
        app.logger.exception("A execução do agente falhou. Causa: %s", e)
        return jsonify({"erro": f"Ocorreu um erro interno no servidor: {e}"}), 500


@app.route("/")
def index():
    return "<h1>Servidor de Agentes de IA está no ar!</h1><p>Use o endpoint <b>/executar_analise</b> via POST para rodar uma análise.</p>"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
