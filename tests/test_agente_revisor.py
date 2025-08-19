import unittest
from unittest.mock import patch, MagicMock
from agents.agente_revisor import code_from_repo, validation

class TestAgenteRevisor(unittest.TestCase):

    @patch('agents.agente_revisor.github_reader.main')
    def test_code_from_repo_valid_repo(self, mock_github_reader):
        mock_github_reader.return_value = 'some code'
        result = code_from_repo('valid/repo', 'design')
        self.assertEqual(result, 'some code')

    @patch('agents.agente_revisor.github_reader.main')
    def test_code_from_repo_invalid_repo(self, mock_github_reader):
        mock_github_reader.side_effect = RuntimeError('Invalid repo')
        with self.assertRaises(RuntimeError):
            code_from_repo('invalid/repo', 'design')

    def test_validation_tipo_analise_invalido(self):
        with self.assertRaises(ValueError):
            validation(tipo_analise='invalid', repositorio='some/repo')

if __name__ == '__main__':
    unittest.main()
