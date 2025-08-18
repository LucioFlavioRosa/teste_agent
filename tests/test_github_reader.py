import importlib
import sys
import types
import pytest


def _install_fake_colab(token_value="fake-token"):
    google_mod = types.ModuleType("google")
    colab_mod = types.ModuleType("google.colab")
    class _UserData(types.ModuleType):
        def get(self, key):
            return token_value
    userdata_mod = _UserData("google.colab.userdata")
    sys.modules["google"] = google_mod
    sys.modules["google.colab"] = colab_mod
    sys.modules["google.colab.userdata"] = userdata_mod


_install_fake_colab()

import tools.github_reader as gh


def test_main_tipo_nao_mapeado_le_todos_os_arquivos(monkeypatch):
    # Força conection a retornar um repo sentinel e verifica que extensoes=None é passado
    monkeypatch.setattr(gh, "conection", lambda repositorio: "REPO_SENTINEL")

    seen = {}

    def fake_read(repo, extensoes, path="", arquivos_do_repo=None):
        seen["repo"] = repo
        seen["extensoes"] = extensoes
        return {"a.txt": "conteudo"}

    monkeypatch.setattr(gh, "_leitura_recursiva_com_debug", fake_read)

    # tipo nao mapeado (ex.: pentest) => extensoes_alvo = None
    out = gh.main(repo="org/repo", tipo_de_analise="pentest")
    assert out == {"a.txt": "conteudo"}
    assert seen["repo"] == "REPO_SENTINEL"
    assert seen["extensoes"] is None


def test__leitura_recursiva_filtra_por_extensao_e_dockerfile():
    # Monta uma árvore fake de arquivos
    class Node:
        def __init__(self, type_, path, name=None, content=b""):
            self.type = type_
            self.path = path
            self.name = name if name is not None else path.split("/")[-1]
            self.decoded_content = content

    class FakeRepo:
        def __init__(self):
            self._store = {
                "": [
                    Node("dir", "dir1"),
                    Node("file", "a.tf", content=b"resource \"x\" {}"),
                    Node("file", "b.py", content=b"print('x')"),
                    Node("file", "Dockerfile", name="Dockerfile", content=b"FROM python:3.11"),
                ],
                "dir1": [
                    Node("file", "dir1/c.tfvars", content=b"var=1"),
                    Node("file", "dir1/d.txt", content=b"txt"),
                ],
            }
        def get_contents(self, path=""):
            return self._store.get(path, [])

    repo = FakeRepo()
    extensoes = [".tf", ".tfvars", "Dockerfile"]
    out = gh._leitura_recursiva_com_debug(repo, extensoes)

    assert "a.tf" in out
    assert "Dockerfile" in out
    assert "dir1/c.tfvars" in out
    assert "b.py" not in out
    assert "dir1/d.txt" not in out


def test__leitura_recursiva_trata_unicode_decode_error_sem_interromper(capsys):
    class Node:
        def __init__(self, type_, path, name=None, content=b""):
            self.type = type_
            self.path = path
            self.name = name if name is not None else path.split("/")[-1]
            self.decoded_content = content

    class FakeRepo:
        def __init__(self):
            self._store = {
                "": [
                    Node("file", "ok.tf", content=b"ok=1"),
                    Node("file", "bad.tf", content=b"\xff"),  # inválido UTF-8
                ]
            }
        def get_contents(self, path=""):
            return self._store.get(path, [])

    repo = FakeRepo()
    out = gh._leitura_recursiva_com_debug(repo, extensoes=[".tf"])
    # Arquivo inválido não deve estar presente
    assert "ok.tf" in out
    assert "bad.tf" not in out


def test_conection_usa_token_e_get_repo(monkeypatch):
    # Fakes para Token e Github
    created = {}

    class FakeToken:
        def __init__(self, value):
            created["token_value"] = value

    class FakeGithub:
        def __init__(self, auth=None):
            created["auth"] = auth
        def get_repo(self, repo):
            created["repo"] = repo
            return f"REPO::{repo}"

    monkeypatch.setattr(gh, "Token", FakeToken)
    monkeypatch.setattr(gh, "Github", FakeGithub)

    repo = gh.conection("org/repo")
    assert repo == "REPO::org/repo"
    assert created["token_value"] == "fake-token"
    assert isinstance(created["auth"], FakeToken)
    assert created["repo"] == "org/repo"
