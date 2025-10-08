from typing import Dict, Any
import logging

class TratadorErros:
    def tratar_erro_validacao(self, ve: Exception) -> Dict[str, Any]:
        """Trata erros de validação"""
        logging.error(f"Erro de validação: {ve}")
        return {"erro": f"Erro de validação: {ve}"}
    
    def tratar_erro_execucao(self, re: Exception) -> Dict[str, Any]:
        """Trata erros de execução"""
        logging.error(f"Erro de execução: {re}")
        return {"erro": f"Erro de execução: {re}"}
    
    def tratar_erro_chave(self, ke: Exception) -> Dict[str, Any]:
        """Trata erros de chave"""
        logging.error(f"Erro de chave: {ke}")
        return {"erro": f"Erro de chave: {ke}"}
    
    def tratar_erro_tipo(self, te: Exception) -> Dict[str, Any]:
        """Trata erros de tipo"""
        logging.error(f"Erro de tipo: {te}")
        return {"erro": f"Erro de tipo: {te}"}
    
    def tratar_erro(self, erro: Exception) -> Dict[str, Any]:
        """Método principal para tratamento de erros"""
        if isinstance(erro, ValueError):
            return self.tratar_erro_validacao(erro)
        elif isinstance(erro, RuntimeError):
            return self.tratar_erro_execucao(erro)
        elif isinstance(erro, KeyError):
            return self.tratar_erro_chave(erro)
        elif isinstance(erro, TypeError):
            return self.tratar_erro_tipo(erro)
        else:
            logging.error(f"Erro não categorizado: {erro}")
            return {"erro": f"Erro não categorizado: {erro}"}
