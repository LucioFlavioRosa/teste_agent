# -*- coding: utf-8 -*-
"""Testes unitários para teste_git_hub.py

Este módulo contém testes abrangentes para os endpoints Flask,
cobrindo validações de parâmetros, tratamento de exceções e
integração com agentes externos usando mocking.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from teste_git_hub import app


class TestFlaskEndpoints:
    """Classe de testes para os endpoints Flask do teste_git_hub.py"""
    
    @pytest.fixture
    def client(self):
        """Fixture que configura o cliente de teste Flask"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_index_returns_status_200_and_html(self, client):
        """Testa se o endpoint raiz retorna status 200 e HTML esperado"""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'<h1>Servidor de Agentes de IA está no ar!</h1>' in response.data
        assert b'/executar_analise' in response.data
        assert response.content_type.startswith('text/html')
    
    def test_rodar_analise_invalid_json_returns_400(self, client):
        """Testa se requisições com corpo inválido retornam HTTP 400"""
        # Teste com corpo vazio
        response = client.post('/executar_analise')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data
        assert 'Corpo da requisição inválido' in data['erro']
        
        # Teste com JSON malformado
        response = client.post('/executar_analise', 
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_rodar_analise_missing_tipo_analise_returns_400(self, client):
        """Testa se a ausência do parâmetro 'tipo_analise' retorna HTTP 400"""
        payload = {
            'repositorio': 'test/repo',
            'codigo': 'print("hello")',
            'instrucoes_extras': 'test instructions'
        }
        
        response = client.post('/executar_analise',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data
        assert "'tipo_analise' é obrigatório" in data['erro']
    
    def test_rodar_analise_missing_repo_and_codigo_returns_400(self, client):
        """Testa se a ausência de 'repositorio' e 'codigo' retorna HTTP 400"""
        payload = {
            'tipo_analise': 'pentest',
            'instrucoes_extras': 'test instructions'
        }
        
        response = client.post('/executar_analise',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data
        assert "pelo menos um dos parâmetros: 'repositorio' ou 'codigo'" in data['erro']
    
    @patch('teste_git_hub.agente_revisor.executar_analise')
    def test_rodar_analise_success_calls_agente_and_returns_200(self, mock_executar_analise, client):
        """Testa se com parâmetros válidos o endpoint retorna HTTP 200 e resultado esperado"""
        # Configurar o mock
        mock_resultado = {
            'resultado': 'Análise concluída com sucesso',
            'status': 'success',
            'detalhes': 'Nenhum problema encontrado'
        }
        mock_executar_analise.return_value = mock_resultado
        
        payload = {
            'tipo_analise': 'pentest',
            'repositorio': 'test/repo',
            'instrucoes_extras': 'instruções de teste'
        }
        
        response = client.post('/executar_analise',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        # Verificar resposta
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == mock_resultado
        
        # Verificar se o agente foi chamado com os parâmetros corretos
        mock_executar_analise.assert_called_once_with(
            tipo_analise='pentest',
            repositorio='test/repo',
            codigo=None,
            instrucoes_extras='instruções de teste'
        )
    
    @patch('teste_git_hub.agente_revisor.executar_analise')
    def test_rodar_analise_success_with_codigo_parameter(self, mock_executar_analise, client):
        """Testa se o endpoint funciona corretamente com parâmetro 'codigo'"""
        mock_resultado = {'resultado': 'Código analisado'}
        mock_executar_analise.return_value = mock_resultado
        
        payload = {
            'tipo_analise': 'security',
            'codigo': 'def test(): pass',
            'instrucoes_extras': ''
        }
        
        response = client.post('/executar_analise',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == mock_resultado
        
        mock_executar_analise.assert_called_once_with(
            tipo_analise='security',
            repositorio=None,
            codigo='def test(): pass',
            instrucoes_extras=''
        )
    
    @patch('teste_git_hub.agente_revisor.executar_analise')
    def test_rodar_analise_agente_raises_exception_returns_500(self, mock_executar_analise, client):
        """Testa se exceção no agente retorna HTTP 500 com mensagem apropriada"""
        # Configurar o mock para lançar exceção
        mock_executar_analise.side_effect = Exception("Erro interno do agente")
        
        payload = {
            'tipo_analise': 'pentest',
            'repositorio': 'test/repo'
        }
        
        response = client.post('/executar_analise',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        # Verificar resposta de erro
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'erro' in data
        assert 'Ocorreu um erro interno no servidor' in data['erro']
        assert 'Erro interno do agente' in data['erro']
        
        # Verificar se o agente foi chamado
        mock_executar_analise.assert_called_once()
    
    @patch('teste_git_hub.agente_revisor.executar_analise')
    def test_rodar_analise_with_both_repo_and_codigo(self, mock_executar_analise, client):
        """Testa se o endpoint funciona com ambos repositorio e codigo fornecidos"""
        mock_resultado = {'resultado': 'Análise completa'}
        mock_executar_analise.return_value = mock_resultado
        
        payload = {
            'tipo_analise': 'design',
            'repositorio': 'test/repo',
            'codigo': 'print("test")',
            'instrucoes_extras': 'Analisar ambos'
        }
        
        response = client.post('/executar_analise',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == mock_resultado
        
        mock_executar_analise.assert_called_once_with(
            tipo_analise='design',
            repositorio='test/repo',
            codigo='print("test")',
            instrucoes_extras='Analisar ambos'
        )
    
    def test_rodar_analise_empty_tipo_analise_returns_400(self, client):
        """Testa se tipo_analise vazio retorna HTTP 400"""
        payload = {
            'tipo_analise': '',
            'repositorio': 'test/repo'
        }
        
        response = client.post('/executar_analise',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data
        assert "'tipo_analise' é obrigatório" in data['erro']
    
    def test_rodar_analise_empty_strings_for_repo_and_codigo_returns_400(self, client):
        """Testa se strings vazias para repositorio e codigo retornam HTTP 400"""
        payload = {
            'tipo_analise': 'pentest',
            'repositorio': '',
            'codigo': ''
        }
        
        response = client.post('/executar_analise',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data
        assert "pelo menos um dos parâmetros: 'repositorio' ou 'codigo'" in data['erro']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])