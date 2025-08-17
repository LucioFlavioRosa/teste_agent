from agents import agente_revisor
import os


if __name__ == '__main__':
    # Exemplo simples de uso via CLI. Use variáveis de ambiente para tokens.
    tipo = os.getenv('TIPO_ANALISE', 'terraform')
    repositorio = os.getenv('REPO')  # Ex.: 'org/nome_repo'
    codigo = os.getenv('CODIGO')  # Opcional: quando fornecido, não acessa o GitHub

    if not repositorio and not codigo:
        print("Defina REPO (org/repo) ou CODIGO para executar o exemplo.")
    else:
        resp = agente_revisor.executar_analise(
            tipo_analise=tipo,
            repositorio=repositorio,
            codigo=codigo,
            instrucoes_extras=os.getenv('INSTRUCOES', '')
        )
        print(resp)
