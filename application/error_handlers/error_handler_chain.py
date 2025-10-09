class ErrorHandlerChain:
    def __init__(self):
        self.handlers = []
    def register(self, handler):
        self.handlers.append(handler)
    def handle(self, exception):
        for handler in self.handlers:
            if handler.can_handle(exception):
                handler.handle(exception)
                return
        raise exception
