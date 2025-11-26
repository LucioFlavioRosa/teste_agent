import logging

class ErrorHandler:
    def tratar_erro_validacao(self, ve: Exception):
        logging.error(f"Erro de validação: {ve}")
        raise
    
    def tratar_erro_execucao(self, re: Exception):
        logging.error(f"Erro de execução: {re}")
        raise
    
    def tratar_erro_chave(self, ke: Exception):
        logging.error(f"Erro de chave: {ke}")
        raise
    
    def tratar_erro_tipo(self, te: Exception):
        logging.error(f"Erro de tipo: {te}")
        raise
    
    def tratar_erro(self, e: Exception):
        if isinstance(e, ValueError):
            self.tratar_erro_validacao(e)
        elif isinstance(e, RuntimeError):
            self.tratar_erro_execucao(e)
        elif isinstance(e, KeyError):
            self.tratar_erro_chave(e)
        elif isinstance(e, TypeError):
            self.tratar_erro_tipo(e)
        else:
            logging.error(f"Erro não tratado: {e}")
            raise