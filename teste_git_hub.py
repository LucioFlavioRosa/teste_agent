# -*- coding: utf-8 -*-
"""API Flask para execução de análises de código via agentes de IA.

Este script expõe uma API Flask para executar análises de código através do
módulo agents.agente_revisor. Fornece um endpoint principal (/executar_analise)
para submeter código para análise e iniciar o servidor na porta 5000.
"""

from agents import agente_revisor

nome_do_repositorio = "LucioFlavioRosa/agent-vinna"

resposta_desing = agente_revisor.executar_analise(tipo_analise='pentest', repositorio=nome_do_repositorio)

print(resposta_desing['resultado'])

# app.py
from flask import Flask, request, jsonify
from agents import agente_revisor
import traceback


app = Flask(__name__)


@app.route('/executar_analise', methods=['POST'])
def rodar_analise():
    """Endpoint para executar análises de código.
    
    Espera um payload JSON com os seguintes campos:
    - tipo_analise: Tipo de análise a ser realizada (obrigatório)
    - repositorio: Nome do repositório GitHub (opcional se 'codigo' for fornecido)
    - codigo: Código-fonte a ser analisado (opcional se 'repositorio' for fornecido)
    - instrucoes_extras: Instruções adicionais para a análise (opcional)
    
    Returns:
        JSON com o resultado da análise e código de status HTTP:
        - 200: Análise concluída com sucesso
        - 400: Parâmetros inválidos
        - 500: Erro interno do servidor
    """

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
            instrucoes_extras=instrucoes_extras
        )

        print("INFO: Análise concluída com sucesso.")
        return jsonify(resultado), 200

    except Exception as e:
        print(f"ERRO: A execução do agente falhou. Causa: {e}")
        traceback.print_exc()
        return jsonify({"erro": f"Ocorreu um erro interno no servidor: {e}"}), 500

@app.route("/")
def index():
    """Rota raiz que exibe uma mensagem de boas-vindas.
    
    Returns:
        HTML simples informando que o servidor está no ar e como usar o endpoint principal.
    """
    return "<h1>Servidor de Agentes de IA está no ar!</h1><p>Use o endpoint <b>/executar_analise</b> via POST para rodar uma análise.</p>"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

