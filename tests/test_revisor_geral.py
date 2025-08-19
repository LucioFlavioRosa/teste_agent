import unittest
from unittest.mock import patch, MagicMock
from tools.revisor_geral import executar_analise_llm

class TestRevisorGeral(unittest.TestCase):

    @patch('tools.revisor_geral.openai_client.chat.completions.create')
    def test_executar_analise_llm_success(self, mock_openai):
        mock_openai.return_value.choices = [MagicMock(message=MagicMock(content='Valid response'))]
        result = executar_analise_llm('design', 'some code', '', 'gpt-4.1', 3000)
        self.assertEqual(result, 'Valid response')

    @patch('tools.revisor_geral.openai_client.chat.completions.create')
    def test_executar_analise_llm_failure(self, mock_openai):
        mock_openai.side_effect = Exception('API failure')
        with self.assertRaises(RuntimeError):
            executar_analise_llm('design', 'some code', '', 'gpt-4.1', 3000)

if __name__ == '__main__':
    unittest.main()
