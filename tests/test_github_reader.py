import unittest
from unittest.mock import patch
from tools.github_reader import conection

class TestGithubReader(unittest.TestCase):

    @patch('tools.github_reader.Github')
    def test_conection_falha_autenticacao(self, mock_github):
        mock_github.side_effect = Exception('Falha de autenticação')
        with self.assertRaises(Exception) as context:
            conection('repositorio_exemplo')
        self.assertIn('Falha de autenticação', str(context.exception))

if __name__ == '__main__':
    unittest.main()
