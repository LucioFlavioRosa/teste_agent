import json
import types

import app as flask_app


def test_endpoint_executar_analise_monkeypatch(monkeypatch):
    # Monkeypatch do agente para evitar I/O real
    def fake_executar_analise(**kwargs):
        return {"tipo_analise": kwargs['tipo_analise'], "resultado": "RESPOSTA_FAKE"}

    monkeypatch.setattr(flask_app.agente_revisor, 'executar_analise', fake_executar_analise)

    client = flask_app.app.test_client()

    payload = {
        "tipo_analise": "pentest",
        "repositorio": "owner/repo",
        "instrucoes_extras": ""
    }

    resp = client.post('/executar_analise', data=json.dumps(payload), content_type='application/json')

    assert resp.status_code == 200
    data = resp.get_json()
    assert data['tipo_analise'] == 'pentest'
    assert data['resultado'] == 'RESPOSTA_FAKE'
