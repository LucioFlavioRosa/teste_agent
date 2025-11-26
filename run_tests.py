#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para executar testes unitários com relatórios de cobertura

Este script facilita a execução dos testes unitários e gera relatórios
de cobertura de código em diferentes formatos.

Uso:
    python run_tests.py
    python run_tests.py --verbose
    python run_tests.py --coverage-only
"""

import sys
import subprocess
import argparse
import os


def run_command(command, description):
    """Executa um comando e trata erros
    
    Args:
        command (list): Comando a ser executado
        description (str): Descrição do comando para logs
    
    Returns:
        bool: True se sucesso, False se falha
    """
    print(f"\n{'='*50}")
    print(f"EXECUTANDO: {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=False)
        print(f"\n✅ {description} - SUCESSO")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} - FALHA (código: {e.returncode})")
        return False
    except FileNotFoundError:
        print(f"\n❌ Comando não encontrado: {' '.join(command)}")
        print("Certifique-se de que pytest está instalado: pip install pytest pytest-cov")
        return False


def main():
    """Função principal para executar testes"""
    parser = argparse.ArgumentParser(description='Executar testes unitários com cobertura')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Executar testes em modo verboso')
    parser.add_argument('--coverage-only', '-c', action='store_true',
                       help='Executar apenas relatório de cobertura')
    parser.add_argument('--no-coverage', '-n', action='store_true',
                       help='Executar testes sem relatório de cobertura')
    
    args = parser.parse_args()
    
    print("🧪 INICIANDO EXECUÇÃO DOS TESTES UNITÁRIOS")
    print(f"Diretório atual: {os.getcwd()}")
    
    success = True
    
    if not args.coverage_only:
        # Executar testes unitários
        if args.no_coverage:
            # Testes sem cobertura
            test_command = ['python', '-m', 'pytest', 'test_teste_git_hub.py']
            if args.verbose:
                test_command.extend(['-v', '-s'])
        else:
            # Testes com cobertura
            test_command = [
                'python', '-m', 'pytest', 
                'test_teste_git_hub.py',
                '--cov=teste_git_hub',
                '--cov-report=html',
                '--cov-report=term-missing'
            ]
            if args.verbose:
                test_command.extend(['-v', '-s'])
        
        success = run_command(test_command, "Testes Unitários")
    
    if not args.no_coverage and success:
        # Gerar relatório de cobertura adicional
        coverage_command = [
            'python', '-m', 'pytest', 
            '--cov=teste_git_hub',
            '--cov-report=html:htmlcov',
            '--cov-report=xml:coverage.xml',
            '--cov-report=term-missing',
            'test_teste_git_hub.py'
        ]
        
        run_command(coverage_command, "Relatório de Cobertura Detalhado")
        
        print("\n📊 RELATÓRIOS DE COBERTURA GERADOS:")
        print("   - HTML: htmlcov/index.html")
        print("   - XML: coverage.xml")
        print("   - Terminal: exibido acima")
    
    # Resumo final
    print("\n" + "="*60)
    if success:
        print("🎉 TODOS OS TESTES FORAM EXECUTADOS COM SUCESSO!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("   1. Revisar relatório de cobertura em htmlcov/index.html")
        print("   2. Verificar se cobertura está acima de 90%")
        print("   3. Implementar testes adicionais se necessário")
    else:
        print("💥 ALGUNS TESTES FALHARAM!")
        print("\n🔧 AÇÕES RECOMENDADAS:")
        print("   1. Revisar logs de erro acima")
        print("   2. Corrigir falhas nos testes")
        print("   3. Executar novamente")
    
    print("="*60)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())