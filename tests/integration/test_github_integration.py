import pytest
from tools import github_reader
import logging

@pytest.mark.usefixtures('test_config')
def test_github_success(monkeypatch, test_config, caplog, github_file_structure):
    class FakeRepo:
        def get_contents(self, path):
            class FakeFile:
                def __init__(self, path):
                    self.path = path
                    self.type = 'file'
                    self.name = path.split('/')[-1]
                    self.decoded_content = b'conteudo do arquivo'
            return [FakeFile(p) for p in github_file_structure.keys()]
    
    monkeypatch.setattr(github_reader, 'conectar_ao_github', lambda repositorio_nome, config=None: FakeRepo())
    with caplog.at_level(logging.INFO):
        arquivos = github_reader.obter_arquivos_para_analise('repo/fake', 'python', config=test_config)
        assert isinstance(arquivos, dict)
        assert all(isinstance(v, str) for v in arquivos.values())
        assert any('Conexão bem-sucedida' in m for m in caplog.messages)

@pytest.mark.usefixtures('test_config')
def test_github_rate_limit(monkeypatch, test_config, caplog):
    def fake_conectar_ao_github(*args, **kwargs):
        raise RuntimeError('API rate limit exceeded')
    monkeypatch.setattr(github_reader, 'conectar_ao_github', fake_conectar_ao_github)
    with pytest.raises(RuntimeError):
        github_reader.obter_arquivos_para_analise('repo/fake', 'python', config=test_config)
    assert any('Erro ao conectar ao GitHub' in m for m in caplog.messages)
