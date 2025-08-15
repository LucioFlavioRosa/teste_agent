# -*- coding: utf-8 -*-
from agents import agente_revisor

if __name__ == '__main__':
    nome_do_repositorio = "LucioFlavioRosa/agent-vinna"
    resposta = agente_revisor.executar_analise(tipo_analise='pentest', repositorio=nome_do_repositorio)
    print(resposta.get('resultado'))
