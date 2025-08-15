from agents import agente_revisor


def test_executar_analise_existe_e_eh_callable():
    assert hasattr(agente_revisor, 'executar_analise'), 'Função executar_analise não está exposta no módulo agente_revisor'
    assert callable(agente_revisor.executar_analise), 'executar_analise não é chamável'
