# -*- coding: utf-8 -*-
"""
Script de exemplo para uso do agente de revisão de código via API Flask.

Inclui exemplo de chamada ao agente revisor e exposição de endpoint HTTP para análise automatizada de repositórios GitHub.

Uso:
    $ python teste_git_hub.py

Acesse http://localhost:5000/ para verificar o status do servidor.
"""

# !pip install PyGithub

from agents import agente_revisor

nome_do_repositorio = "LucioFlavioRosa/agent-vinna"

# Exemplo de chamada direta ao agente revisor
# resposta_desing = agente_revisor.executar_analise(tipo_analise='pentest', repositorio=nome_do_repositorio)
# print(resposta_desing['resultado'])

# app.py
from flask import Flask, request, jsonify
from agents import agente_revisor
import traceback

app = Flask(__name__)

@app.route('/executar_analise', methods=['POST'])
def rodar_analise():
    """
    Endpoint para execução de análise automatizada de código.
    Espera um JSON com os parâmetros:
        - tipo_analise (str)
        - repositorio (str, opcional)
        - codigo (str, opcional)
        - instrucoes_extras (str, opcional)
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
    """
    Endpoint de status do servidor.
    """
    return "<h1>Servidor de Agentes de IA está no ar!</h1><p>Use o endpoint <b>/executar_analise</b> via POST para rodar uma análise.</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
