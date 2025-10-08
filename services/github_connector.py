from github import Github
from github.Auth import Token
from google.colab import userdata
import logging

class GitHubConnector:
    """Classe responsável pela conexão com o GitHub"""
    
    def conectar_ao_github(self, repositorio_nome: str):
        """Estabelece conexão com o repositório GitHub"""
        try:
            GITHUB_TOKEN = userdata.get('github_token')
            if not GITHUB_TOKEN:
                logging.error("Token do GitHub não encontrado em userdata.")
                raise ValueError("Token do GitHub não encontrado.")
            
            auth = Token(GITHUB_TOKEN)
            github_client = Github(auth=auth)
            repositorio = github_client.get_repo(repositorio_nome)
            
            logging.info(f"Conexão bem-sucedida com o repositório: {repositorio_nome}")
            return repositorio
            
        except (ValueError, RuntimeError, KeyError, TypeError) as e:
            logging.error(f"Erro ao conectar ao GitHub para o repositório '{repositorio_nome}': {e}")
            raise