from tools import github_reader
from tools.revisor_geral import executar_analise_llm

class GithubReader:
    def read_code(self, repositorio: str, tipo_analise: str):
        return github_reader.main(repo=repositorio, tipo_de_analise=tipo_analise)

class LLMClient:
    def executar_analise_llm(self, tipo_analise: str, codigo: str, analise_extra: str, model_name: str, max_token_out: int):
        return executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=codigo,
            analise_extra=analise_extra,
            model_name=model_name,
            max_token_out=max_token_out
        )
