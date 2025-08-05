from typing import Optional, Dict, Any
from tools.github_reader import GithubRepoReader
from tools.revisor_geral import AnaliseLLM


class AnaliseOrquestrador:
    """
    Orquestrador de análise de código, responsável por validação de parâmetros
    e integração entre leitor de repositório e executor de análise LLM.
    """
    def __init__(self, repo_reader: GithubRepoReader = None, analise_llm: AnaliseLLM = None):
        self.repo_reader = repo_reader or GithubRepoReader()
        self.analise_llm = analise_llm or AnaliseLLM()
        self.analises_validas = ["design", "pentest", "seguranca", "terraform"]

    def code_from_repo(self, repositorio: str, tipo_analise: str):
        try:
            print(f'Iniciando a leitura do repositório: {repositorio}')
            codigo_para_analise = self.repo_reader.ler_codigo(repo=repositorio, tipo_de_analise=tipo_analise)
            return codigo_para_analise
        except Exception as e:
            raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e

    def validation(self, tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None):
        if tipo_analise not in self.analises_validas:
            raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {self.analises_validas}")
        if repositorio is None and codigo is None:
            raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")
        if codigo is None:
            codigo_para_analise = self.code_from_repo(tipo_analise=tipo_analise, repositorio=repositorio)
        else:
            codigo_para_analise = codigo
        return codigo_para_analise

    def executar_analise(self, tipo_analise: str, repositorio: Optional[str] = None, codigo: Optional[str] = None, instrucoes_extras: str = "", model_name: str = None, max_token_out: int = None) -> Dict[str, Any]:
        codigo_para_analise = self.validation(tipo_analise=tipo_analise, repositorio=repositorio, codigo=codigo)
        if not codigo_para_analise:
            return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
        resultado = self.analise_llm.executar(
            tipo_analise=tipo_analise,
            codigo=str(codigo_para_analise),
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        return {"tipo_analise": tipo_analise, "resultado": resultado}

# Instância padrão para uso externo
orquestrador_padrao = AnaliseOrquestrador()

# Interface compatível com código legado
main = orquestrador_padrao.executar_analise
executar_analise = orquestrador_padrao.executar_analise
