import importlib
import sys
import types
import pytest


# Injeta módulos fake antes do import de revisor_geral

def _install_fake_colab(key="fake-openai-key"):
    google_mod = types.ModuleType("google")
    colab_mod = types.ModuleType("google.colab")
    class _UserData(types.ModuleType):
        def get(self, k):
            return key
    userdata_mod = _UserData("google.colab.userdata")
    sys.modules["google"] = google_mod
    sys.modules["google.colab"] = colab_mod
    sys.modules["google.colab.userdata"] = userdata_mod


def _install_fake_openai():
    class FakeOpenAI(types.ModuleType):
        class OpenAI:
            def __init__(self, api_key=None):
                self.api_key = api_key
                # estrutura esperada: .chat.completions.create
                class _Completions:
                    def __init__(self):
                        self._create = None
                    def create(self, *a, **kw):
                        if self._create is None:
                            raise NotImplementedError
                        return self._create(*a, **kw)
                class _Chat:
                    def __init__(self):
                        self.completions = _Completions()
                self.chat = _Chat()
    sys.modules["openai"] = FakeOpenAI("openai")


_install_fake_colab()
_install_fake_openai()

# Importa o módulo após preparar os stubs
import tools.revisor_geral as rg


def test_carregar_prompt_arquivo_inexistente_gera_valueerror():
    with pytest.raises(ValueError) as exc:
        rg.carregar_prompt("tipo_que_nao_existe")
    assert "Arquivo de prompt para a análise" in str(exc.value)


def test_executar_analise_llm_fluxo_sucesso_sem_instrucao_extra(monkeypatch):
    # Mock do prompt
    monkeypatch.setattr(rg, "carregar_prompt", lambda tipo: "PROMPT_SISTEMA")

    captured = {}

    class Choice:
        def __init__(self, content):
            class Msg:
                def __init__(self, c):
                    self.content = c
            self.message = Msg(content)

    def fake_create(model, messages, temperature, max_tokens):
        captured["model"] = model
        captured["messages"] = messages
        captured["temperature"] = temperature
        captured["max_tokens"] = max_tokens
        return types.SimpleNamespace(choices=[Choice("RESPOSTA_OK")])

    # injeta o create fake
    rg.openai_client.chat.completions._create = fake_create

    out = rg.executar_analise_llm(
        tipo_analise="pentest",
        codigo="print('x')",
        analise_extra="   ",  # em branco
        model_name="gpt",
        max_token_out=321,
    )
    assert out == "RESPOSTA_OK"

    assert captured["model"] == "gpt"
    assert captured["max_tokens"] == 321
    assert len(captured["messages"]) == 3
    assert captured["messages"][0]["role"] == "system"
    assert captured["messages"][2]["content"].startswith("Nenhuma instrução extra fornecida")


def test_executar_analise_llm_trata_excecao_da_api(monkeypatch):
    # Mock do prompt
    monkeypatch.setattr(rg, "carregar_prompt", lambda tipo: "PROMPT")

    def fake_create_fail(*a, **k):
        raise Exception("falha api")

    rg.openai_client.chat.completions._create = fake_create_fail

    with pytest.raises(RuntimeError) as exc:
        rg.executar_analise_llm(
            tipo_analise="pentest",
            codigo="x",
            analise_extra="y",
            model_name="m",
            max_token_out=10,
        )
    assert "Erro ao comunicar com a OpenAI" in str(exc.value)


def test_modulo_importa_quando_api_key_disponivel():
    # Reimporta assegurando que a API key existe (stub já instalado)
    mod = importlib.reload(rg)
    assert hasattr(mod, "openai_client")
    assert mod.OPENAI_API_KEY == "fake-openai-key"
