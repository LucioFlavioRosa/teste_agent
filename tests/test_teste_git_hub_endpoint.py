import importlib
import sys
import types


def _load_app_with_stubbed_agent(result_payload=None, raise_error=False):
    # Prepara stub de agents.agente_revisor para evitar execuções reais
    agents_pkg = types.ModuleType("agents")
    stub_agent = types.ModuleType("agents.agente_revisor")

    def exec_stub(**kwargs):
        if raise_error:
            raise RuntimeError("erro simulado")
        return result_payload if result_payload is not None else {"tipo_analise": kwargs.get("tipo_analise", ""), "resultado": "ok"}

    stub_agent.executar_analise = exec_stub

    # registra nos módulos
    sys.modules["agents"] = agents_pkg
    sys.modules["agents.agente_revisor"] = stub_agent

    # Importa o app Flask (executará o código de topo, mas com stub seguro)
    app_module = importlib.import_module("teste_git_hub")
    return app_module.app, app_module


def test_endpoint_validacoes_400():
    app, mod = _load_app_with_stubbed_agent()
    client = app.test_client()

    # 1) Corpo ausente
    r = client.post("/executar_analise")
    assert r.status_code == 400
    assert "Corpo da requisição inválido" in r.get_json()["erro"]

    # 2) Sem tipo_analise
    r = client.post("/executar_analise", json={"repositorio": "org/repo"})
    assert r.status_code == 400
    assert "'tipo_analise' é obrigatório" in r.get_json()["erro"]

    # 3) Sem repositorio e codigo
    r = client.post("/executar_analise", json={"tipo_analise": "pentest"})
    assert r.status_code == 400
    assert "fornecer pelo menos um dos parâmetros" in r.get_json()["erro"]


def test_endpoint_sucesso_200_com_mock():
    payload = {"tipo_analise": "pentest", "resultado": "ANALISE_MOCK"}
    app, mod = _load_app_with_stubbed_agent(result_payload=payload)
    client = app.test_client()

    r = client.post("/executar_analise", json={
        "tipo_analise": "pentest",
        "repositorio": "org/repo"
    })
    assert r.status_code == 200
    assert r.get_json() == payload


def test_endpoint_tratamento_erro_500():
    app, mod = _load_app_with_stubbed_agent(raise_error=True)
    client = app.test_client()

    r = client.post("/executar_analise", json={
        "tipo_analise": "pentest",
        "repositorio": "org/repo"
    })
    assert r.status_code == 500
    assert "Ocorreu um erro interno no servidor" in r.get_json()["erro"]


def test_index_responde_ok():
    app, mod = _load_app_with_stubbed_agent()
    client = app.test_client()

    r = client.get("/")
    assert r.status_code == 200
    assert b"Servidor de Agentes de IA est\xc3\xa1 no ar" in r.data
