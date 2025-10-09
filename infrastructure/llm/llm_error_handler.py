class LLMRateLimitError(Exception):
    pass

class LLMAuthenticationError(Exception):
    pass

class LLMTimeoutError(Exception):
    pass

class LLMInvalidRequestError(Exception):
    pass

class LLMErrorHandler:
    @staticmethod
    def handle_error(e):
        if hasattr(e, 'status_code'):
            if e.status_code == 429:
                raise LLMRateLimitError(str(e))
            elif e.status_code == 401:
                raise LLMAuthenticationError(str(e))
            elif e.status_code == 408:
                raise LLMTimeoutError(str(e))
            elif e.status_code == 400:
                raise LLMInvalidRequestError(str(e))
        raise e
