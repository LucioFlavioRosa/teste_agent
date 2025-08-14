# -*- coding: utf-8 -*-
"""
teste_git_hub.py

Script de exemplo para uso do agente de revisão e servidor Flask para expor a API de análise.

Inclui endpoints para execução de análise de código e página de status.
"""

from agents import agente_revisor
from flask import Flask, request, jsonify
import traceback

nome_do_repositorio = "LucioFlavioRosa/agent-vinna"

# Exemplo de chamada direta (comentado para evitar execução automática)
# resposta_design = agente_revisor.executar_analise(tipo_analise='pentest', repositorio=nome_do_repositorio)
# print(resposta_design['resultado'])

app = Flask(__name__)

@app.route('/executar_analise', methods=['POST'])
def rodar_analise():
    """
    Endpoint para executar análise de código.

    Recebe JSON com os parâmetros:
        - tipo_analise (str): Tipo da análise ('design', 'pentest', etc).
        - repositorio (str, opcional): Repositório GitHub.
        - codigo (dict, opcional): Código-fonte fornecido diretamente.
        - instrucoes_extras (str, opcional): Instruções adicionais.

    Returns:
        JSON com o resultado da análise ou mensagem de erro.
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

    Returns:
        HTML simples indicando que o servidor está ativo.
    """
    return "<h1>Servidor de Agentes de IA está no ar!</h1><p>Use o endpoint <b>/executar_analise</b> via POST para rodar uma análise.</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
