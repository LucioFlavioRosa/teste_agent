from typing import Dict, Any, Union, Optional
from .interfaces import IRepositoryReader, IAnalysisExecutor, IParameterValidator, ICodeProcessor
from tools import github_reader
from tools.revisor_geral import executar_analise_llm
import logging


class GitHubRepositoryReader(IRepositoryReader):
    """Implementação concreta para leitura de repositórios GitHub."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def obter_arquivos_para_analise(self, repo_nome: str, tipo_analise: str) -> Dict[str, str]:
        """Obtém arquivos do repositório GitHub para análise."""
        try:
            self.logger.info(f'Iniciando a leitura do repositório: {repo_nome}')
            return github_reader.obter_arquivos_para_analise(repo_nome=repo_nome, tipo_analise=tipo_analise)
        except (ValueError, RuntimeError, KeyError, TypeError) as e:
            self.logger.error(f"Falha ao obter arquivos do repositório '{repo_nome}': {e}")
            raise


class LLMAnalysisExecutor(IAnalysisExecutor):
    """Implementação concreta para execução de análises LLM."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def executar_analise_llm(self, tipo_analise: str, codigo: str, 
                           analise_extra: str = "", model_name: str = "gpt-4.1", 
                           max_token_out: int = 3000) -> str:
        """Executa análise usando LLM."""
        try:
            return executar_analise_llm(
                tipo_analise=tipo_analise,
                codigo=codigo,
                analise_extra=analise_extra,
                model_name=model_name,
                max_token_out=max_token_out
            )
        except Exception as e:
            self.logger.error(f"Falha na execução da análise LLM: {e}")
            raise RuntimeError(f"Erro na análise LLM: {e}")


class ParameterValidator(IParameterValidator):
    """Implementação concreta para validação de parâmetros."""
    
    def __init__(self, tipos_validos: list):
        self.tipos_analise_validos = tipos_validos
        self.logger = logging.getLogger(__name__)
    
    def validar_parametros(self, tipo_analise: str, repositorio_nome: Optional[str], 
                          codigo_entrada: Optional[Union[str, Dict[str, str]]]) -> bool:
        """Valida parâmetros de entrada."""
        if tipo_analise not in self.tipos_analise_validos:
            error_msg = f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {self.tipos_analise_validos}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        if repositorio_nome is None and codigo_entrada is None:
            error_msg = "Erro: É obrigatório fornecer 'repositorio' ou 'codigo_entrada'."
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        return True


class CodeProcessor(ICodeProcessor):
    """Implementação concreta para processamento de código."""
    
    def __init__(self, repository_reader: IRepositoryReader):
        self.repository_reader = repository_reader
        self.logger = logging.getLogger(__name__)
    
    def preparar_codigo(self, tipo_analise: str, repositorio_nome: Optional[str], 
                       codigo_entrada: Optional[Union[str, Dict[str, str]]]) -> Union[str, Dict[str, str]]:
        """Prepara código para análise."""
        if codigo_entrada is not None:
            return codigo_entrada
        
        if repositorio_nome is not None:
            return self.repository_reader.obter_arquivos_para_analise(
                repo_nome=repositorio_nome, 
                tipo_analise=tipo_analise
            )
        
        raise ValueError("Nenhuma fonte de código fornecida")
    
    def montar_codigo_para_llm(self, codigo_entrada: Union[str, Dict[str, str]]) -> str:
        """Monta código em formato adequado para LLM."""
        if isinstance(codigo_entrada, dict):
            return '\n\n'.join(f"# Arquivo: {k}\n{v}" for k, v in codigo_entrada.items())
        return str(codigo_entrada)