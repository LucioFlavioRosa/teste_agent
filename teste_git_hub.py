# -*- coding: utf-8 -*-
"""
teste_git_hub.ipynb

Original file is located at
    https://colab.research.google.com/drive/11ZTKLHaPzrTy8tcu3IYFSCefnnVtvIEF
"""

# Este arquivo mistura código de teste manual, execução web e lógica de aplicação.
# Recomenda-se separar a API Flask e o código de teste/manual em arquivos distintos.
# Aqui, removemos prints de debug e ajustamos a chamada para o novo nome da função do agente.

from agents import agente_revisor

nome_do_repositorio = "LucioFlavioRosa/agent-vinna"

# Exemplo de chamada para análise de pentest
resposta_pentest = agente_revisor.executar_analise(tipo_analise='pentest', repositorio=nome_do_repositorio)
print(resposta_pentest['resultado'])

# API Flask (deve idealmente estar em app.py separado)
from flask import Flask, request, jsonify
import traceback

app = Flask(__name__)

@app.route('/executar_analise', methods=['POST'])
def rodar_analise():
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
        resultado = agente_revisor.executar_analise(
            tipo_analise=tipo_analise,
            repositorio=repositorio,
            codigo=codigo,
            instrucoes_extras=instrucoes_extras
        )
        return jsonify(resultado), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"erro": f"Ocorreu um erro interno no servidor: {e}"}), 500

@app.route("/")
def index():
    return "<h1>Servidor de Agentes de IA está no ar!</h1><p>Use o endpoint <b>/executar_analise</b> via POST para rodar uma análise.</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
