from abc import ABC, abstractmethod
from typing import Dict
from domain.value_objects.file_filter import FileFilter

class CodeRepository(ABC):
    @abstractmethod
    def fetch_files(self, filters: 'FileFilter') -> Dict[str, str]:
        pass
