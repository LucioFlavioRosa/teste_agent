from typing import Optional, Dict, Any, Union
from tools import github_reader
import logging

class PreparadorCodigo:
    def __init__(self):
        self.github_reader = github_reader
    
    def obter_codigo_repositorio(self, repositorio_nome: str, tipo_analise: str) -> Dict[str, str]:
        """Obtém código do repositório GitHub"""
        try:
            logging.info(f'Iniciando a leitura do repositório: {repositorio_nome}')
            arquivos_codigo = self.github_reader.obter_arquivos_para_analise(
                repo_nome=repositorio_nome, 
                tipo_analise=tipo_analise
            )
            return arquivos_codigo
        except (ValueError, RuntimeError, KeyError, TypeError) as e:
            logging.error(f"Falha ao executar a análise de '{tipo_analise}': {e}")
            raise
    
    def preparar_codigo_para_analise(self, 
                                   tipo_analise: str, 
                                   repositorio_nome: Optional[str], 
                                   codigo_entrada: Optional[Union[str, Dict[str, str]]]):
        """Prepara o código para análise, seja do repositório ou entrada direta"""
        if codigo_entrada is not None:
            return codigo_entrada
        return self.obter_codigo_repositorio(
            repositorio_nome=repositorio_nome, 
            tipo_analise=tipo_analise
        )