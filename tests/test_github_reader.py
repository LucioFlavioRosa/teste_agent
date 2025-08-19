import unittest
from unittest.mock import patch, MagicMock
from github import Github
from tools.github_reader import conection

class TestGithubReader(unittest.TestCase):

    @patch('tools.github_reader.Github')
    def test_conection_valid_token(self, mock_github):
        mock_repo = MagicMock()
        mock_github.return_value.get_repo.return_value = mock_repo
        result = conection('valid/repo')
        self.assertEqual(result, mock_repo)

    @patch('tools.github_reader.Github')
    def test_conection_invalid_token(self, mock_github):
        mock_github.side_effect = Exception('Invalid token')
        with self.assertRaises(Exception):
            conection('invalid/repo')

if __name__ == '__main__':
    unittest.main()
