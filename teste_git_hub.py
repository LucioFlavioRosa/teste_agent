# -*- coding: utf-8 -*-
"""Exemplo de uso do agente revisor.

Este módulo não executa nada em nível de import. O exemplo só roda quando
executado diretamente via linha de comando.
"""

from agents import agente_revisor


def exemplo_execucao():
    nome_do_repositorio = "LucioFlavioRosa/agent-vinna"
    resposta = agente_revisor.executar_analise(
        tipo_analise='pentest',
        repositorio=nome_do_repositorio,
        instrucoes_extras=''
    )
    print(resposta['resultado'])


if __name__ == '__main__':
    exemplo_execucao()
