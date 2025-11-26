# -*- coding: utf-8 -*-
"""Testes unitários para teste_git_hub.py

Testes abrangentes para o endpoint /executar_analise cobrindo:
- Casos de sucesso
- Validação de parâmetros obrigatórios
- Tratamento de erros internos
- Validação de JSON inválido
- Isolamento de dependências com mocks
"""

import unittest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Adiciona o diretório raiz ao path para importar o módulo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import do módulo a ser testado
from teste_git_hub import app


class TestExecutarAnaliseEndpoint(unittest.TestCase):
    """Classe de testes para o endpoint /executar_analise"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Dados válidos padrão para testes
        self.dados_validos = {
            'tipo_analise': 'pentest',
            'repositorio': 'LucioFlavioRosa/agent-vinna',
            'instrucoes_extras': 'Análise detalhada'
        }
        
        # Resposta mock padrão do agente_revisor
        self.resposta_mock_sucesso = {
            'resultado': 'Análise concluída com sucesso',
            'status': 'success',
            'detalhes': 'Análise de pentest realizada'
        }
    
    @patch('teste_git_hub.agente_revisor.executar_analise')
    def test_executar_analise_endpoint_success(self, mock_executar_analise):
        """Teste: Endpoint retorna 200 e JSON esperado com parâmetros válidos"""
        # Arrange
        mock_executar_analise.return_value = self.resposta_mock_sucesso
        
        # Act
        response = self.app.post('/executar_analise',
                               data=json.dumps(self.dados_validos),
                               content_type='application/json')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data, self.resposta_mock_sucesso)
        
        # Verifica se o agente foi chamado com os parâmetros corretos
        mock_executar_analise.assert_called_once_with(
            tipo_analise='pentest',
            repositorio='LucioFlavioRosa/agent-vinna',
            codigo=None,
            instrucoes_extras='Análise detalhada'
        )
    
    @patch('teste_git_hub.agente_revisor.executar_analise')
    def test_executar_analise_success_with_codigo(self, mock_executar_analise):
        """Teste: Endpoint funciona corretamente com parâmetro 'codigo' em vez de 'repositorio'"""
        # Arrange
        mock_executar_analise.return_value = self.resposta_mock_sucesso
        dados_com_codigo = {
            'tipo_analise': 'seguranca',
            'codigo': 'def exemplo(): pass',
            'instrucoes_extras': ''
        }
        
        # Act
        response = self.app.post('/executar_analise',
                               data=json.dumps(dados_com_codigo),
                               content_type='application/json')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        mock_executar_analise.assert_called_once_with(
            tipo_analise='seguranca',
            repositorio=None,
            codigo='def exemplo(): pass',
            instrucoes_extras=''
        )
    
    def test_executar_analise_missing_tipo_analise(self):
        """Teste: Ausência do parâmetro 'tipo_analise' retorna 400 com mensagem apropriada"""
        # Arrange
        dados_sem_tipo = {
            'repositorio': 'LucioFlavioRosa/agent-vinna',
            'instrucoes_extras': 'Teste'
        }
        
        # Act
        response = self.app.post('/executar_analise',
                               data=json.dumps(dados_sem_tipo),
                               content_type='application/json')
        
        # Assert
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('erro', response_data)
        self.assertEqual(response_data['erro'], "O parâmetro 'tipo_analise' é obrigatório.")
    
    def test_executar_analise_missing_repositorio_and_codigo(self):
        """Teste: Ausência simultânea de 'repositorio' e 'codigo' retorna 400 com mensagem adequada"""
        # Arrange
        dados_sem_repo_e_codigo = {
            'tipo_analise': 'pentest',
            'instrucoes_extras': 'Teste'
        }
        
        # Act
        response = self.app.post('/executar_analise',
                               data=json.dumps(dados_sem_repo_e_codigo),
                               content_type='application/json')
        
        # Assert
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('erro', response_data)
        self.assertEqual(response_data['erro'], 
                        "É obrigatório fornecer pelo menos um dos parâmetros: 'repositorio' ou 'codigo'.")
    
    @patch('teste_git_hub.agente_revisor.executar_analise')
    def test_executar_analise_internal_error(self, mock_executar_analise):
        """Teste: Exceção durante execução do agente retorna 500 com mensagem de erro correta"""
        # Arrange
        mock_executar_analise.side_effect = Exception("Erro simulado no agente")
        
        # Act
        response = self.app.post('/executar_analise',
                               data=json.dumps(self.dados_validos),
                               content_type='application/json')
        
        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.data)
        self.assertIn('erro', response_data)
        self.assertIn('Ocorreu um erro interno no servidor', response_data['erro'])
        self.assertIn('Erro simulado no agente', response_data['erro'])
    
    def test_executar_analise_invalid_json_body(self):
        """Teste: Requisição com corpo inválido ou não-JSON retorna 400 com mensagem adequada"""
        # Act - Enviando dados inválidos (não é JSON)
        response = self.app.post('/executar_analise',
                               data='dados inválidos não-json',
                               content_type='application/json')
        
        # Assert
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('erro', response_data)
        self.assertEqual(response_data['erro'], "Corpo da requisição inválido ou não é um JSON.")
    
    def test_executar_analise_empty_body(self):
        """Teste: Requisição com corpo vazio retorna 400"""
        # Act
        response = self.app.post('/executar_analise',
                               data='',
                               content_type='application/json')
        
        # Assert
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('erro', response_data)
        self.assertEqual(response_data['erro'], "Corpo da requisição inválido ou não é um JSON.")
    
    @patch('teste_git_hub.agente_revisor.executar_analise')
    def test_executar_analise_with_both_repositorio_and_codigo(self, mock_executar_analise):
        """Teste: Endpoint funciona quando ambos 'repositorio' e 'codigo' são fornecidos"""
        # Arrange
        mock_executar_analise.return_value = self.resposta_mock_sucesso
        dados_completos = {
            'tipo_analise': 'design',
            'repositorio': 'LucioFlavioRosa/agent-vinna',
            'codigo': 'def exemplo(): pass',
            'instrucoes_extras': 'Análise completa'
        }
        
        # Act
        response = self.app.post('/executar_analise',
                               data=json.dumps(dados_completos),
                               content_type='application/json')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        mock_executar_analise.assert_called_once_with(
            tipo_analise='design',
            repositorio='LucioFlavioRosa/agent-vinna',
            codigo='def exemplo(): pass',
            instrucoes_extras='Análise completa'
        )
    
    def test_index_endpoint(self):
        """Teste: Endpoint raiz retorna página de informações"""
        # Act
        response = self.app.get('/')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Servidor de Agentes de IA', response.data)
        self.assertIn(b'/executar_analise', response.data)


class TestExecutarAnaliseIntegration(unittest.TestCase):
    """Testes de integração para verificar comportamento end-to-end"""
    
    def setUp(self):
        """Configuração inicial para testes de integração"""
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('teste_git_hub.agente_revisor.executar_analise')
    def test_full_request_response_cycle(self, mock_executar_analise):
        """Teste: Ciclo completo de requisição-resposta com logging"""
        # Arrange
        mock_executar_analise.return_value = {
            'resultado': 'Análise de integração concluída',
            'timestamp': '2024-01-01T00:00:00Z'
        }
        
        dados_teste = {
            'tipo_analise': 'pentest',
            'repositorio': 'test/repo',
            'instrucoes_extras': 'Teste de integração'
        }
        
        # Act
        with self.app as client:
            response = client.post('/executar_analise',
                                 data=json.dumps(dados_teste),
                                 content_type='application/json')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('resultado', response_data)
        self.assertEqual(response_data['resultado'], 'Análise de integração concluída')


if __name__ == '__main__':
    # Configuração para execução dos testes
    unittest.main(verbosity=2, buffer=True)