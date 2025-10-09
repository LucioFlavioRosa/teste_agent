class IFileFilterStrategy:
    def filtrar(self, arquivo_obj):
        raise NotImplementedError

class ExtensionFilterStrategy(IFileFilterStrategy):
    def __init__(self, extensoes):
        self.extensoes = extensoes

    def filtrar(self, arquivo_obj):
        if self.extensoes is None:
            return True
        if any(arquivo_obj.path.endswith(ext) for ext in self.extensoes) or arquivo_obj.name in self.extensoes:
            return True
        return False