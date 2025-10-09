from typing import List, Optional

class FileFilter:
    def __init__(self, extensions: Optional[List[str]] = None, exclude_patterns: Optional[List[str]] = None, max_depth: Optional[int] = None):
        self.extensions = extensions or []
        self.exclude_patterns = exclude_patterns or []
        self.max_depth = max_depth
