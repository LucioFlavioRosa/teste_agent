import unittest
from unittest.mock import patch, MagicMock
from agents.agente_revisor import code_from_repo, validation

class TestAgenteRevisor(unittest.TestCase):

    @patch('agents.agente_revisor.github_reader.main')
    def test_code_from_repo_excecao(self, mock_github_reader):
        mock_github_reader.side_effect = Exception('Erro ao ler repositório')
        with self.assertRaises(RuntimeError) as context:
            code_from_repo('repositorio_invalido', 'design')
        self.assertTrue('Falha ao executar a análise de' in str(context.exception))

    def test_validation_tipo_analise_invalido(self):
        with self.assertRaises(ValueError) as context:
            validation(tipo_analise='invalido')
        self.assertTrue("Tipo de análise 'invalido' é inválido" in str(context.exception))

if __name__ == '__main__':
    unittest.main()
