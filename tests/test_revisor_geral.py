import unittest
from unittest.mock import patch, MagicMock
from tools.revisor_geral import executar_analise_llm

class TestRevisorGeral(unittest.TestCase):

    @patch('tools.revisor_geral.openai_client.chat.completions.create')
    def test_executar_analise_llm_resposta_valida(self, mock_openai):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='resposta_valida'))]
        mock_openai.return_value = mock_response

        resultado = executar_analise_llm(
            tipo_analise='design',
            codigo='codigo_exemplo',
            analise_extra='',
            model_name='gpt-4.1',
            max_token_out=3000
        )

        self.assertEqual(resultado, 'resposta_valida')

if __name__ == '__main__':
    unittest.main()
