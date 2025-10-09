from typing import List, Dict

class MessageBuilder:
    def build_messages(self, prompt_sistema: str, codigo: str, analise_extra: str) -> List[Dict]:
        if not codigo.strip():
            raise ValueError('O código fornecido está vazio.')
        analise_extra = analise_extra.strip()
        mensagens = [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": codigo},
            {"role": "user", "content": f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}' if analise_extra else 'Nenhuma instrução extra fornecida pelo usuário.'}
        ]
        return mensagens
