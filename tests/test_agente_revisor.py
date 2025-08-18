import importlib
import sys
import types
import pytest


# Utilitário: injeta um módulo fake google.colab.userdata para evitar dependência externa
class _FakeUserDataModule(types.ModuleType):
    def __init__(self, token_value="fake-token"):
        super().__init__("google.colab.userdata")
        self._token_value = token_value

    def get(self, key):
        # usado em github_reader e revisor_geral
        return self._token_value


def _install_fake_colab(token_value="fake-token"):
    google_mod = types.ModuleType("google")
    colab_mod = types.ModuleType("google.colab")
    userdata_mod = _FakeUserDataModule(token_value=token_value)
    sys.modules["google"] = google_mod
    sys.modules["google.colab"] = colab_mod
    sys.modules["google.colab.userdata"] = userdata_mod


# Antes de importar agente_revisor, garantimos que google.colab.userdata existe
_install_fake_colab()

# Também injetamos um stub para tools.revisor_geral a fim de evitar dependência de OpenAI no import
stub_revisor = types.ModuleType("tools.revisor_geral")

def _stub_executar_analise_llm(**kwargs):
    return "STUB_EXECUCAO"

stub_revisor.executar_analise_llm = _stub_executar_analise_llm
sys.modules["tools.revisor_geral"] = stub_revisor

# Agora podemos importar o módulo sob teste
import agents.agente_revisor as ar


def test_validation_tipo_analise_invalido_gera_valueerror():
    with pytest.raises(ValueError) as exc:
        ar.validation(tipo_analise="invalido")
    msg = str(exc.value)
    assert "Tipo de análise 'invalido' é inválido" in msg
    assert "analises_validas" not in msg  # apenas checa mensagem com lista
    for item in ["design", "pentest", "seguranca", "terraform"]:
        assert item in msg


def test_validation_repo_ou_codigo_obrigatorio():
    with pytest.raises(ValueError) as exc:
        ar.validation(tipo_analise="pentest", repositorio=None, codigo=None)
    assert "É obrigatório fornecer 'repositorio' ou 'codigo'" in str(exc.value)


def test_validation_retorna_codigo_quando_fornecido():
    # Se codigo for fornecido, não deve chamar code_from_repo
    sentinel = "print('ok')"

    def _boom(*a, **k):
        raise AssertionError("code_from_repo não deveria ser chamado quando 'codigo' é fornecido")

    original = ar.code_from_repo
    try:
        ar.code_from_repo = _boom  # garantir que não será chamado
        saida = ar.validation(tipo_analise="pentest", codigo=sentinel)
        assert saida == sentinel
    finally:
        ar.code_from_repo = original


def test_validation_chama_code_from_repo_quando_codigo_none(monkeypatch):
    called = {}

    def fake_code_from_repo(repositorio: str, tipo_analise: str):
        called["args"] = (repositorio, tipo_analise)
        return {"file.py": "print('x')"}

    monkeypatch.setattr(ar, "code_from_repo", fake_code_from_repo)
    out = ar.validation(tipo_analise="pentest", repositorio="org/repo", codigo=None)
    assert out == {"file.py": "print('x')"}
    assert called["args"] == ("org/repo", "pentest")


def test_code_from_repo_lanca_runtimeerror_quando_github_reader_falha(monkeypatch):
    def boom(**kwargs):
        raise Exception("falhou GH")

    monkeypatch.setattr(ar.github_reader, "main", boom)
    with pytest.raises(RuntimeError) as exc:
        ar.code_from_repo(repositorio="org/repo", tipo_analise="pentest")
    assert "Falha ao executar a análise de 'pentest'" in str(exc.value)


def test_main_quando_codigo_vazio_retorna_mensagem_sem_codigo():
    resp = ar.main(tipo_analise="pentest", codigo="")
    assert resp["tipo_analise"] == "pentest"
    assert resp["resultado"] == "Não foi fornecido nenhum código para análise"


def test_main_chama_executar_analise_llm_e_formata_resposta(monkeypatch):
    captured = {}

    def fake_exec_llm(tipo_analise, codigo, analise_extra, model_name, max_token_out):
        captured.update({
            "tipo_analise": tipo_analise,
            "codigo": codigo,
            "analise_extra": analise_extra,
            "model_name": model_name,
            "max_token_out": max_token_out,
        })
        return "RESULTADO_OK"

    monkeypatch.setattr(ar, "executar_analise_llm", fake_exec_llm)
    resp = ar.main(tipo_analise="pentest", codigo="print('x')", instrucoes_extras="", model_name="m", max_token_out=123)
    assert resp == {"tipo_analise": "pentest", "resultado": "RESULTADO_OK"}
    assert captured["tipo_analise"] == "pentest"
    assert captured["codigo"] == "print('x')"
    assert captured["model_name"] == "m"
    assert captured["max_token_out"] == 123


def test_modulo_expoe_funcao_executar_analise_para_compatibilidade(monkeypatch):
    assert hasattr(ar, "executar_analise"), "O módulo deve expor a função executar_analise para compatibilidade"

    def fake_exec_llm(tipo_analise, codigo, analise_extra, model_name, max_token_out):
        return "OK_WRAPPER"

    monkeypatch.setattr(ar, "executar_analise_llm", fake_exec_llm)
    out = ar.executar_analise(tipo_analise="pentest", codigo="x")
    assert out == {"tipo_analise": "pentest", "resultado": "OK_WRAPPER"}
