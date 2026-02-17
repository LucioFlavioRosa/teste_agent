import re
from github import Github
from github.Auth import Token
from google.colab import userdata

def conection(repositorio: str):
    GITHUB_TOKEN = userdata.get('github_token')
    auth = Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    return g.get_repo(repositorio)


MAPEAMENTO_TIPO_EXTENSOES = {
    "terraform": [".tf", ".tfvars"],
    "python": [".py"],
    "cloudformation": [".json", ".yaml", ".yml"],
    "ansible": [".yml", ".yaml"],
    "docker": ["Dockerfile"], 
}

# Configurações para limitar o tamanho da leitura
MAX_ARQUIVO_SIZE_KB = 1024  # Tamanho máximo de arquivo em KB
MAX_TOTAL_SIZE_MB = 50      # Tamanho máximo total em MB
MAX_FILES_COUNT = 100       # Número máximo de arquivos a serem lidos

def _leitura_recursiva_com_debug(repo, extensoes, path="", arquivos_do_repo=None, 
                                 total_size=0, file_count=0, page_size=30, page=0):

    if arquivos_do_repo is None:
        arquivos_do_repo = {}

    # Verificar limites
    if file_count >= MAX_FILES_COUNT:
        print(f"DEBUG: Limite de {MAX_FILES_COUNT} arquivos atingido. Interrompendo leitura.")
        return arquivos_do_repo, total_size, file_count
    
    if total_size >= (MAX_TOTAL_SIZE_MB * 1024 * 1024):
        print(f"DEBUG: Limite de {MAX_TOTAL_SIZE_MB}MB atingido. Interrompendo leitura.")
        return arquivos_do_repo, total_size, file_count

    try:
        # Leitura paginada do conteúdo
        conteudos = repo.get_contents(path, ref="main")
        
        for conteudo in conteudos:
            if conteudo.type == "dir":
                arquivos_do_repo, total_size, file_count = _leitura_recursiva_com_debug(
                    repo, extensoes, conteudo.path, arquivos_do_repo, 
                    total_size, file_count, page_size, page
                )
                
                # Verificar novamente os limites após processar o diretório
                if file_count >= MAX_FILES_COUNT or total_size >= (MAX_TOTAL_SIZE_MB * 1024 * 1024):
                    return arquivos_do_repo, total_size, file_count
            else:
                # Lógica de decisão de leitura
                ler_o_arquivo = False
                if extensoes is None:
                    ler_o_arquivo = True
                else:
                    if any(conteudo.path.endswith(ext) for ext in extensoes) or conteudo.name in extensoes:
                        ler_o_arquivo = True
                    
                if ler_o_arquivo:
                    # Verificar tamanho do arquivo
                    if conteudo.size > (MAX_ARQUIVO_SIZE_KB * 1024):
                        print(f"DEBUG: Arquivo '{conteudo.path}' excede o tamanho máximo permitido ({MAX_ARQUIVO_SIZE_KB}KB). Ignorando.")
                        continue
                        
                    try:
                        codigo = conteudo.decoded_content.decode('utf-8')
                        arquivos_do_repo[conteudo.path] = codigo
                        total_size += len(codigo.encode('utf-8'))
                        file_count += 1
                        
                        # Verificar limites após adicionar o arquivo
                        if file_count >= MAX_FILES_COUNT:
                            print(f"DEBUG: Limite de {MAX_FILES_COUNT} arquivos atingido. Interrompendo leitura.")
                            return arquivos_do_repo, total_size, file_count
                        
                        if total_size >= (MAX_TOTAL_SIZE_MB * 1024 * 1024):
                            print(f"DEBUG: Limite de {MAX_TOTAL_SIZE_MB}MB atingido. Interrompendo leitura.")
                            return arquivos_do_repo, total_size, file_count
                            
                    except Exception as e:
                        print(f"DEBUG: ERRO na decodificação de '{conteudo.path}': {e}")

    except Exception as e:
        print(f"Erro ao ler conteúdo do repositório: {e}")
        
    return arquivos_do_repo, total_size, file_count


def main(repo, tipo_de_analise: str):
    print(f"Iniciando leitura do repositório com limites: {MAX_FILES_COUNT} arquivos, {MAX_ARQUIVO_SIZE_KB}KB por arquivo, {MAX_TOTAL_SIZE_MB}MB total")
    repositorio_final = conection(repositorio=repo)

    extensoes_alvo = MAPEAMENTO_TIPO_EXTENSOES.get(tipo_de_analise.lower())

    arquivos_encontrados, total_size_kb, file_count = _leitura_recursiva_com_debug(
        repositorio_final, extensoes=extensoes_alvo
    )
    
    print(f"Leitura concluída: {file_count} arquivos, {total_size_kb/1024/1024:.2f}MB total")
  
    return arquivos_encontrados