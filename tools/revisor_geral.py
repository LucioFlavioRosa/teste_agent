import os
from typing import List, Dict, Optional
from openai import OpenAI
from core.ports import ILLMClient, PromptRepository


class PromptRepositoryFS(PromptRepository):
    """Repositório de prompts baseado em sistema de arquivos."""

    def __init__(self, base_dir: Optional[str] = None) -> None:
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(__file__), 'prompts')
        self._base_dir = base_dir

    def load_prompt(self, tipo_analise: str) -> str:
        caminho = os.path.join(self._base_dir, f'{tipo_analise}.md')
        if not os.path.isfile(caminho):
            raise ValueError(f"Arquivo de prompt para a análise '{tipo_analise}' não encontrado em: {caminho}")
        with open(caminho, 'r', encoding='utf-8') as f:
            return f.read()

    def list_types(self) -> List[str]:
        try:
            arquivos = os.listdir(self._base_dir)
        except FileNotFoundError:
            return []
        tipos = []
        for nome in arquivos:
            if nome.lower().endswith('.md'):
                tipos.append(os.path.splitext(nome)[0])
        return sorted(tipos)


class OpenAIClient(ILLMClient):
    """Cliente OpenAI encapsulado atrás da interface ILLMClient (DIP)."""

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("A chave da API da OpenAI é obrigatória para inicializar o OpenAIClient.")
        self._client = OpenAI(api_key=api_key)

    def chat(self, messages: List[Dict[str, str]], model: str, max_tokens: int, temperature: float) -> str:
        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()


def executar_analise_llm(
    tipo_analise: str,
    codigo: str,
    analise_extra: str,
    client: ILLMClient,
    prompt_repo: PromptRepository,
    model_name: str,
    max_token_out: int,
    temperature: float = 0.5,
) -> str:
    """Executa a análise no LLM utilizando injeção de dependências (cliente e repositório de prompts)."""

    prompt_sistema = prompt_repo.load_prompt(tipo_analise)

    mensagens = [
        {"role": "system", "content": prompt_sistema},
        {"role": "user", "content": codigo},
        {
            'role': 'user',
            'content': (
                f'Instruções extras do usuário a serem consideradas na análise: {analise_extra}'
                if analise_extra and analise_extra.strip()
                else 'Nenhuma instrução extra fornecida pelo usuário.'
            ),
        },
    ]

    try:
        conteudo_resposta = client.chat(
            messages=mensagens,
            model=model_name,
            max_tokens=max_token_out,
            temperature=temperature,
        )
        return conteudo_resposta
    except Exception as e:
        print(f"ERRO: Falha na chamada à API da OpenAI para análise '{tipo_analise}'. Causa: {e}")
        raise RuntimeError(f"Erro ao comunicar com a OpenAI: {e}") from e
