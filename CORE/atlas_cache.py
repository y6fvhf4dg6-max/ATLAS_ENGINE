"""
ATLAS Engine

Atlas Cache v1.0
Reads and writes JSON cache files.
"""

import json
from pathlib import Path


class AtlasCache:
    @staticmethod
    def load(path):
        file_path = Path(path)

        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def save(path, data):
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        return path
