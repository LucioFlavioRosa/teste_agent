from typing import List, Dict

class MessageBuilder:
    @staticmethod
    def build_messages(prompt_sistema: str, codigo: str, analise_extra: str) -> List[Dict]:
        if not codigo or not isinstance(codigo, str):
            raise ValueError('O código fornecido está vazio ou inválido.')
        analise_extra = analise_extra if analise_extra and analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'
        return [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": codigo},
            {"role": "user", "content": f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}'}
        ]
