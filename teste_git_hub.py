from flask import Flask, request, jsonify
from agents.agente_revisor import orquestrar_analise

app = Flask(__name__)

@app.route('/analise', methods=['POST'])
def endpoint_analise():
    """
    Endpoint HTTP para análise de repositório.
    """
    dados = request.get_json()
    tipo_analise = dados.get('tipo_analise')
    repositorio = dados.get('repositorio')
    caminho_credenciais = dados.get('caminho_credenciais')
    extensoes_personalizadas = dados.get('extensoes_personalizadas')
    resultado = orquestrar_analise(tipo_analise, repositorio, caminho_credenciais, extensoes_personalizadas)
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True)
