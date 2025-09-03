from typing import Dict, List, Optional
from tools.repository_reader_factory import RepositoryReaderFactory
from config.analysis_registry import AnalysisRegistry
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Mantém compatibilidade com a API existente
def obter_arquivos_para_analise(repo_nome: str, tipo_analise: str, 
                               max_workers: int = 4, max_depth: Optional[int] = None) -> Dict[str, str]:
    """
    Função de compatibilidade que mantém a API original.
    Internamente utiliza a nova arquitetura refatorada.
    
    Args:
        repo_nome: Nome do repositório
        tipo_analise: Tipo de análise
        max_workers: Número máximo de workers (mantido para compatibilidade)
        max_depth: Profundidade máxima (mantido para compatibilidade)
        
    Returns:
        Dicionário com arquivos e conteúdos
    """
    try:
        # Utiliza o novo sistema de registro para obter extensões
        registry = AnalysisRegistry()
        extensoes_alvo = registry.get_extensions_for_analysis(tipo_analise)
        
        if not extensoes_alvo:
            logging.warning(f"Nenhuma extensão encontrada para análise '{tipo_analise}'")
            return {}
        
        # Cria reader através da factory
        factory = RepositoryReaderFactory()
        reader = factory.create_reader('github', 'colab')
        
        # Lê os arquivos
        arquivos_encontrados = reader.read_files(repo_nome, extensoes_alvo, max_depth)
        
        logging.info(f"Arquivos encontrados para análise '{tipo_analise}': {list(arquivos_encontrados.keys())}")
        return arquivos_encontrados
        
    except Exception as e:
        logging.error(f"Erro ao obter arquivos para análise '{tipo_analise}': {e}")
        raise

# Funções mantidas para compatibilidade (delegam para nova implementação)
def conectar_ao_github(repositorio_nome: str):
    """
    Função de compatibilidade - delegada para nova implementação.
    """
    factory = RepositoryReaderFactory()
    reader = factory.create_reader('github', 'colab')
    return reader.connect(repositorio_nome)

def ler_arquivos_repositorio_github(repositorio_nome: str, tipo_analise: str, 
                                   max_workers: int = 4, max_depth: Optional[int] = None):
    """
    Função de compatibilidade - delegada para nova implementação.
    """
    return obter_arquivos_para_analise(repositorio_nome, tipo_analise, max_workers, max_depth)
