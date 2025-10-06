import pytest
import json
from unittest.mock import patch, MagicMock
from teste_git_hub import app


class TestFlaskEndpoints:
    """Testes unitários para os endpoints Flask"""

    @pytest.fixture
    def client(self):
        """Fixture para cliente de teste Flask"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_index_endpoint(self, client):
        """Testa o endpoint raiz"""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b"Servidor de Agentes de IA está no ar!" in response.data
        assert b"/executar_analise" in response.data

    @patch('teste_git_hub.agente_revisor.executar_analise')
    def test_executar_analise_sucesso_com_repositorio(self, mock_executar_analise, client):
        """Testa execução bem-sucedida da análise com repositório"""
        mock_executar_analise.return_value = {
            'status': 'sucesso',
            'resultado': 'Análise concluída'
        }
        
        dados_requisicao = {
            'tipo_analise': 'pentest',
            'repositorio': 'owner/repo',
            'instrucoes_extras': 'Focar em vulnerabilidades críticas'
        }
        
        response = client.post(
            '/executar_analise',
            data=json.dumps(dados_requisicao),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'sucesso'
        assert response_data['resultado'] == 'Análise concluída'
        
        mock_executar_analise.assert_called_once_with(
            tipo_analise='pentest',
            repositorio='owner/repo',
            codigo=None,
            instrucoes_extras='Focar em vulnerabilidades críticas'
        )

    @patch('teste_git_hub.agente_revisor.executar_analise')
    def test_executar_analise_sucesso_com_codigo(self, mock_executar_analise, client):
        """Testa execução bem-sucedida da análise com código direto"""
        mock_executar_analise.return_value = {
            'status': 'sucesso',
            'resultado': 'Código analisado'
        }
        
        dados_requisicao = {
            'tipo_analise': 'seguranca',
            'codigo': 'def vulnerable_function(): pass',
            'instrucoes_extras': ''
        }
        
        response = client.post(
            '/executar_analise',
            data=json.dumps(dados_requisicao),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'sucesso'
        
        mock_executar_analise.assert_called_once_with(
            tipo_analise='seguranca',
            repositorio=None,
            codigo='def vulnerable_function(): pass',
            instrucoes_extras=''
        )

    def test_executar_analise_sem_corpo_requisicao(self, client):
        """Testa erro quando não há corpo na requisição"""
        response = client.post('/executar_analise')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'erro' in response_data
        assert 'Corpo da requisição inválido' in response_data['erro']

    def test_executar_analise_sem_tipo_analise(self, client):
        """Testa erro quando tipo_analise não é fornecido"""
        dados_requisicao = {
            'repositorio': 'owner/repo'
        }
        
        response = client.post(
            '/executar_analise',
            data=json.dumps(dados_requisicao),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'erro' in response_data
        assert "'tipo_analise' é obrigatório" in response_data['erro']

    def test_executar_analise_sem_repositorio_nem_codigo(self, client):
        """Testa erro quando nem repositório nem código são fornecidos"""
        dados_requisicao = {
            'tipo_analise': 'pentest'
        }
        
        response = client.post(
            '/executar_analise',
            data=json.dumps(dados_requisicao),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'erro' in response_data
        assert "pelo menos um dos parâmetros: 'repositorio' ou 'codigo'" in response_data['erro']

    @patch('teste_git_hub.agente_revisor.executar_analise')
    def test_executar_analise_falha_interna(self, mock_executar_analise, client):
        """Testa tratamento de exceção interna no agente"""
        mock_executar_analise.side_effect = Exception("Erro interno do agente")
        
        dados_requisicao = {
            'tipo_analise': 'pentest',
            'repositorio': 'owner/repo'
        }
        
        response = client.post(
            '/executar_analise',
            data=json.dumps(dados_requisicao),
            content_type='application/json'
        )
        
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert 'erro' in response_data
        assert 'Ocorreu um erro interno no servidor' in response_data['erro']
        assert 'Erro interno do agente' in response_data['erro']

    def test_executar_analise_json_invalido(self, client):
        """Testa erro com JSON malformado"""
        response = client.post(
            '/executar_analise',
            data='{ invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'erro' in response_data
        assert 'Corpo da requisição inválido' in response_data['erro']

    @patch('teste_git_hub.agente_revisor.executar_analise')
    def test_executar_analise_com_instrucoes_extras_vazias(self, mock_executar_analise, client):
        """Testa execução com instruções extras não fornecidas (valor padrão)"""
        mock_executar_analise.return_value = {'status': 'sucesso'}
        
        dados_requisicao = {
            'tipo_analise': 'pentest',
            'repositorio': 'owner/repo'
            # instrucoes_extras não fornecidas
        }
        
        response = client.post(
            '/executar_analise',
            data=json.dumps(dados_requisicao),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        mock_executar_analise.assert_called_once_with(
            tipo_analise='pentest',
            repositorio='owner/repo',
            codigo=None,
            instrucoes_extras=''  # Valor padrão
        )