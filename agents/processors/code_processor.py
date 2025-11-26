from typing import Optional, Dict, Any, Union
from tools import github_reader
import logging

class CodeProcessor:
    def obter_codigo_repositorio(self, repositorio_nome: str, tipo_analise: str) -> Dict[str, str]:
        try:
            logging.info(f'Iniciando a leitura do repositório: {repositorio_nome}')
            arquivos_codigo = github_reader.obter_arquivos_para_analise(repo_nome=repositorio_nome, tipo_analise=tipo_analise)
            return arquivos_codigo
        except (ValueError, RuntimeError) as e:
            logging.error(f"Falha ao executar a análise de '{tipo_analise}': {e}")
            raise
        except KeyError as e:
            logging.error(f"Erro de chave ao obter código do repositório: {e}")
            raise
        except TypeError as e:
            logging.error(f"Erro de tipo ao obter código do repositório: {e}")
            raise
    
    def preparar_codigo_para_analise(self, tipo_analise: str, repositorio_nome: Optional[str], codigo_entrada: Optional[Union[str, Dict[str, str]]]):
        if codigo_entrada is not None:
            return codigo_entrada
        return self.obter_codigo_repositorio(repositorio_nome=repositorio_nome, tipo_analise=tipo_analise)
    
    def montar_codigo_para_llm(self, codigo_entrada: Union[str, Dict[str, str]]) -> str:
        if isinstance(codigo_entrada, dict):
            return '\n\n'.join(f"# Arquivo: {k}\n{v}" for k, v in codigo_entrada.items())
        return str(codigo_entrada)