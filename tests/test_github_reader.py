import unittest
from unittest.mock import patch
from tools.github_reader import conection

class TestGithubReader(unittest.TestCase):

    @patch('tools.github_reader.Github')
    @patch('tools.github_reader.userdata.get')
    def test_conection_invalid_token(self, mock_userdata_get, mock_github):
        mock_userdata_get.return_value = 'invalid_token'
        mock_github.side_effect = Exception('Invalid token')
        with self.assertRaises(Exception):
            conection('some/repo')

if __name__ == '__main__':
    unittest.main()
