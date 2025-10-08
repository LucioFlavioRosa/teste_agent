import logging
import time
from typing import List, Tuple, Optional

MAX_RETRIES = 3
RETRY_DELAY = 2  # segundos

class ArquivoProcessor:
    """Classe responsável pelo processamento de arquivos"""
    
    def arquivo_esta_na_lista_de_extensoes(self, arquivo_obj, extensoes_alvo: List[str]) -> bool:
        """Verifica se o arquivo possui uma das extensões alvo"""
        if extensoes_alvo is None:
            return True
        
        return (any(arquivo_obj.path.endswith(ext) for ext in extensoes_alvo) or 
                arquivo_obj.name in extensoes_alvo)
    
    def ler_conteudo_arquivo_com_retry(self, arquivo_obj) -> Optional[str]:
        """Lê o conteúdo do arquivo com retry em caso de falha"""
        for tentativa in range(1, MAX_RETRIES + 1):
            try:
                conteudo_arquivo = arquivo_obj.decoded_content.decode('utf-8')
                return conteudo_arquivo
            except AttributeError as e:
                logging.error(f"Arquivo sem conteúdo decodificável '{arquivo_obj.path}': {e}")
                return None
            except Exception as e:
                logging.error(f"Erro inesperado na decodificação de '{arquivo_obj.path}' (tentativa {tentativa}/{MAX_RETRIES}): {type(e).__name__}: {e}")
                if tentativa < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                else:
                    return None
    
    def coletar_arquivos_e_diretorios(self, conteudos, extensoes_alvo: List[str]) -> Tuple[List, List[str]]:
        """Separa arquivos e diretórios do conteúdo do repositório"""
        arquivos = []
        diretorios = []
        
        for item in conteudos:
            if item.type == "dir":
                diretorios.append(item.path)
            else:
                if self.arquivo_esta_na_lista_de_extensoes(item, extensoes_alvo):
                    arquivos.append(item)
        
        return arquivos, diretorios