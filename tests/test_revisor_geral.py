import unittest
from unittest.mock import patch, MagicMock
from tools.revisor_geral import executar_analise_llm

class TestRevisorGeral(unittest.TestCase):

    @patch('tools.revisor_geral.openai_client.chat.completions.create')
    def test_executar_analise_llm_erro_openai(self, mock_openai):
        mock_openai.side_effect = Exception('Erro na API OpenAI')
        with self.assertRaises(RuntimeError) as context:
            executar_analise_llm('design', 'codigo_teste', '', 'gpt-4.1', 3000)
        self.assertTrue('Erro ao comunicar com a OpenAI' in str(context.exception))

if __name__ == '__main__':
    unittest.main()
