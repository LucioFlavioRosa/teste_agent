import unittest
from unittest.mock import patch, MagicMock
from tools.github_reader import conection

class TestGithubReader(unittest.TestCase):

    @patch('tools.github_reader.Github')
    def test_conection_com_mock(self, mock_github):
        mock_repo = MagicMock()
        mock_github.return_value.get_repo.return_value = mock_repo
        resultado = conection('repositorio_teste')
        self.assertEqual(resultado, mock_repo)

if __name__ == '__main__':
    unittest.main()
