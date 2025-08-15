# -*- coding: utf-8 -*-
from agents import agente_revisor

if __name__ == '__main__':
    # Exemplo simples de execução local (teste).
    nome_do_repositorio = "LucioFlavioRosa/agent-vinna"
    resposta = agente_revisor.main(tipo_analise='pentest', repositorio=nome_do_repositorio)
    print(resposta.get('resultado'))
