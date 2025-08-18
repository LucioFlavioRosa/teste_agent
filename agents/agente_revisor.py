"""Agente Revisor de Código.

Este módulo implementa um agente de revisão de código que pode analisar repositórios
GitHub ou código fornecido diretamente, utilizando diferentes tipos de análise.

Dependências:
  - tools.github_reader: Para leitura de repositórios GitHub
  - tools.revisor_geral: Para execução de análises via LLM

Variáveis globais:
  - modelo_llm: Modelo LLM padrão para análises
  - max_tokens_saida: Limite padrão de tokens na saída
  - analises_validas: Lista de tipos de análise suportados
"""

from typing import Optional, Dict, Any
from tools import github_reader
from tools.revisor_geral import executar_analise_llm 


modelo_llm = 'gpt-4.1'
max_tokens_saida = 3000

analises_validas = ["design", "pentest", "seguranca", "terraform"]

def code_from_repo(repositorio: str,
                   tipo_analise: str):
    """Obtém código de um repositório GitHub para análise.
    
    Args:
        repositorio: String com o nome do repositório no formato 'usuario/repo'.
        tipo_analise: Tipo de análise que determinará quais arquivos serão filtrados.
        
    Returns:
        Um dicionário mapeando caminhos de arquivo para seus conteúdos.
        
    Raises:
        RuntimeError: Se ocorrer falha na leitura do repositório.
    """

    try:
      print('Iniciando a leitura do repositório: '+ repositorio)
      codigo_para_analise = github_reader.main(repo=repositorio,
                                                 tipo_de_analise=tipo_analise)
      
      return codigo_para_analise

    except Exception as e:
        raise RuntimeError(f"Falha ao executar a análise de '{tipo_analise}': {e}") from e

def validation(tipo_analise: str,
               repositorio: Optional[str] = None,
               codigo: Optional[str] = None):
    """Valida os parâmetros de entrada e obtém o código para análise.
    
    Args:
        tipo_analise: Tipo de análise a ser realizada, deve estar em analises_validas.
        repositorio: Nome do repositório GitHub no formato 'usuario/repo', opcional.
        codigo: Código-fonte a ser analisado diretamente, opcional.
        
    Returns:
        O código a ser analisado, obtido do repositório ou fornecido diretamente.
        
    Raises:
        ValueError: Se o tipo de análise for inválido ou se nem repositorio nem codigo forem fornecidos.
    """

  if tipo_analise not in analises_validas:
        raise ValueError(f"Tipo de análise '{tipo_analise}' é inválido. Válidos: {analises_validas}")

  if repositorio is None and codigo is None:
        raise ValueError("Erro: É obrigatório fornecer 'repositorio' ou 'codigo'.")

  if codigo is None:
    codigo_para_analise = code_from_repo(tipo_analise=tipo_analise,
                                         repositorio=repositorio)

  else:
    codigo_para_analise = codigo

  return codigo_para_analise

def main(tipo_analise: str,
         repositorio: Optional[str] = None,
         codigo: Optional[str] = None,
         instrucoes_extras: str = "",
         model_name: str = modelo_llm,
         max_token_out: int = max_tokens_saida)-> Dict[str, Any]:
    """Executa uma análise de código com base nos parâmetros fornecidos.
    
    Args:
        tipo_analise: Tipo de análise a ser realizada (design, pentest, seguranca, terraform).
        repositorio: Nome do repositório GitHub no formato 'usuario/repo', opcional.
        codigo: Código-fonte a ser analisado diretamente, opcional.
        instrucoes_extras: Instruções adicionais para a análise, opcional.
        model_name: Nome do modelo LLM a ser utilizado, padrão definido em modelo_llm.
        max_token_out: Limite máximo de tokens na saída, padrão definido em max_tokens_saida.
        
    Returns:
        Dicionário contendo o tipo de análise e o resultado da análise.
        Formato: {"tipo_analise": str, "resultado": str}
        
    Raises:
        ValueError: Se o tipo de análise for inválido ou se nem repositorio nem codigo forem fornecidos.
        RuntimeError: Se ocorrer falha na leitura do repositório ou na execução da análise.
    """

  codigo_para_analise = validation(tipo_analise=tipo_analise,
                                   repositorio=repositorio,
                                   codigo=codigo)
                                   
  if not codigo_para_analise:
    return ({"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'})
    
  else: 
    resultado = executar_analise_llm(
            tipo_analise=tipo_analise,
            codigo=str(codigo_para_analise),
            analise_extra=instrucoes_extras,
            model_name=model_name,
            max_token_out=max_token_out
        )
        
    return {"tipo_analise": tipo_analise, "resultado": resultado}