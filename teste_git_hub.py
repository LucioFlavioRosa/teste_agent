# -*- coding: utf-8 -*-
"""
Arquivo de teste e execução direta.
A interface de usuário (API Flask) foi extraída para 'interface/api_flask.py'.
Este arquivo agora apenas demonstra uso programático do orquestrador.
"""

from agents.agente_revisor import AnalysisOrchestrator
from factories.code_source_factory import CodeSourceFactory
from factories.analysis_executor_factory import AnalysisExecutorFactory
import os

if __name__ == '__main__':
    nome_do_repositorio = "LucioFlavioRosa/agent-vinna"
    github_token = os.environ.get('GITHUB_TOKEN')
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    prompt_dir = os.path.join(os.path.dirname(__file__), 'tools', 'prompts')

    code_source = CodeSourceFactory.create('github', github_token=github_token)
    analysis_executor = AnalysisExecutorFactory.create('openai', openai_api_key=openai_api_key, prompt_dir=prompt_dir)
    orchestrator = AnalysisOrchestrator(code_source, analysis_executor)

    resposta_design = orchestrator.executar_analise(tipo_analise='pentest', repositorio=nome_do_repositorio)
    print(resposta_design['resultado'])
