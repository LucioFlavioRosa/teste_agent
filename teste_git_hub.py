# -*- coding: utf-8 -*-
"""
Script de exemplo para executar uma análise localmente.
A execução foi isolada sob if __name__ == '__main__' e o app Flask foi movido para app.py.
"""

from agents import agente_revisor


def executar_exemplo():
    nome_do_repositorio = "LucioFlavioRosa/agent-vinna"
    resposta = agente_revisor.executar_analise(tipo_analise='pentest', repositorio=nome_do_repositorio)
    print(resposta.get('resultado'))


if __name__ == '__main__':
    executar_exemplo()
