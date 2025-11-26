# -*- coding: utf-8 -*-
"""app.py

Servidor Flask para execução de análises de código via API.
"""

from flask import Flask, request, jsonify
from services.analise_service import AnaliseService
import traceback


class AnaliseController:
    """Controller responsável pelos endpoints de análise."""
    
    def __init__(self, analise_service: AnaliseService):
        self.analise_service = analise_service
    
    def executar_analise(self):
        """Endpoint para executar análises de código."""
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
            
            resultado = self.analise_service.executar_analise(
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
    
    def index(self):
        """Endpoint raiz com informações do servidor."""
        return "<h1>Servidor de Agentes de IA está no ar!</h1><p>Use o endpoint <b>/executar_analise</b> via POST para rodar uma análise.</p>"


def create_app():
    """Factory function para criar a aplicação Flask."""
    app = Flask(__name__)
    
    # Injeção de dependência
    analise_service = AnaliseService()
    controller = AnaliseController(analise_service)
    
    # Registro das rotas
    app.add_url_rule('/executar_analise', 'executar_analise', 
                     controller.executar_analise, methods=['POST'])
    app.add_url_rule('/', 'index', controller.index)
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)