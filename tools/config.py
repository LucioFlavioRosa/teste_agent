import os
from typing import Optional
from google.colab import userdata
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Config:
    """Configuração centralizada da aplicação usando variáveis de ambiente."""
    
    # Configurações de GitHub
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_API_URL: str = os.getenv('GITHUB_API_URL', 'https://api.github.com')
    GITHUB_MAX_RETRIES: int = int(os.getenv('GITHUB_MAX_RETRIES', '3'))
    GITHUB_RETRY_DELAY: int = int(os.getenv('GITHUB_RETRY_DELAY', '2'))
    GITHUB_MAX_PARALLELISM: int = int(os.getenv('GITHUB_MAX_PARALLELISM', '4'))
    
    # Configurações de OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4')
    OPENAI_MAX_TOKENS: int = int(os.getenv('OPENAI_MAX_TOKENS', '2000'))
    OPENAI_TEMPERATURE: float = float(os.getenv('OPENAI_TEMPERATURE', '0.5'))
    
    # Configurações de análise
    MAX_DEPTH: Optional[int] = None
    ANALYSIS_TIMEOUT: int = int(os.getenv('ANALYSIS_TIMEOUT', '300'))
    
    # Configurações de logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    def __init__(self):
        """Inicializa a configuração carregando variáveis de ambiente."""
        self._load_environment_variables()
        self._validate_required_config()
    
    def _load_environment_variables(self):
        """Carrega variáveis de ambiente e tokens do Google Colab userdata."""
        try:
            # Tenta carregar do Google Colab userdata primeiro
            self.GITHUB_TOKEN = userdata.get('github_token')
            logger.info("GitHub token carregado do Google Colab userdata")
        except Exception:
            # Fallback para variável de ambiente
            self.GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
            if self.GITHUB_TOKEN:
                logger.info("GitHub token carregado de variável de ambiente")
        
        try:
            # Tenta carregar do Google Colab userdata primeiro
            self.OPENAI_API_KEY = userdata.get('OPENAI_API_KEY')
            logger.info("OpenAI API key carregada do Google Colab userdata")
        except Exception:
            # Fallback para variável de ambiente
            self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
            if self.OPENAI_API_KEY:
                logger.info("OpenAI API key carregada de variável de ambiente")
        
        # Configuração de profundidade máxima (opcional)
        max_depth_str = os.getenv('MAX_DEPTH')
        if max_depth_str and max_depth_str.isdigit():
            self.MAX_DEPTH = int(max_depth_str)
    
    def _validate_required_config(self):
        """Valida se todas as configurações obrigatórias estão presentes."""
        missing_configs = []
        
        if not self.GITHUB_TOKEN:
            missing_configs.append('GITHUB_TOKEN (via userdata ou env var)')
        
        if not self.OPENAI_API_KEY:
            missing_configs.append('OPENAI_API_KEY (via userdata ou env var)')
        
        if missing_configs:
            error_msg = f"Configurações obrigatórias ausentes: {', '.join(missing_configs)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Todas as configurações obrigatórias foram carregadas com sucesso")
    
    def get_github_config(self) -> dict:
        """Retorna configurações específicas do GitHub."""
        return {
            'token': self.GITHUB_TOKEN,
            'api_url': self.GITHUB_API_URL,
            'max_retries': self.GITHUB_MAX_RETRIES,
            'retry_delay': self.GITHUB_RETRY_DELAY,
            'max_parallelism': self.GITHUB_MAX_PARALLELISM
        }
    
    def get_openai_config(self) -> dict:
        """Retorna configurações específicas da OpenAI."""
        return {
            'api_key': self.OPENAI_API_KEY,
            'model': self.OPENAI_MODEL,
            'max_tokens': self.OPENAI_MAX_TOKENS,
            'temperature': self.OPENAI_TEMPERATURE
        }
    
    def get_analysis_config(self) -> dict:
        """Retorna configurações específicas de análise."""
        return {
            'max_depth': self.MAX_DEPTH,
            'timeout': self.ANALYSIS_TIMEOUT
        }
    
    def is_test_environment(self) -> bool:
        """Verifica se está executando em ambiente de teste."""
        return os.getenv('ENVIRONMENT', '').lower() in ['test', 'testing']
    
    def configure_logging(self):
        """Configura o sistema de logging baseado nas configurações."""
        log_level = getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            force=True
        )
        logger.info(f"Logging configurado para nível: {self.LOG_LEVEL}")


# Instância global da configuração
config = Config()
