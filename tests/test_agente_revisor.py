import unittest
from unittest.mock import patch, MagicMock
from agents.agente_revisor import code_from_repo, validation

class TestAgenteRevisor(unittest.TestCase):

    @patch('agents.agente_revisor.github_reader.main')
    def test_code_from_repo_retorno_valido(self, mock_github_reader):
        mock_github_reader.return_value = 'codigo_exemplo'
        resultado = code_from_repo('repositorio_exemplo', 'design')
        self.assertEqual(resultado, 'codigo_exemplo')

    def test_validation_tipo_analise_invalido(self):
        with self.assertRaises(ValueError) as context:
            validation('tipo_invalido')
        self.assertIn("Tipo de análise 'tipo_invalido' é inválido.", str(context.exception))

if __name__ == '__main__':
    unittest.main()
