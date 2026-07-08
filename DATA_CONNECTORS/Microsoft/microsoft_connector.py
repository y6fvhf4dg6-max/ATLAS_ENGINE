"""
ATLAS Engine 2.0

Microsoft Global Building Footprints Connector

Version : 0.1
Status  : Prototype
"""

from pathlib import Path


class MicrosoftConnector:

    def list_files(self):

        if not self.data_folder.exists():
            print("Data folder bulunamadı.")
            return []

        files = list(self.data_folder.glob("*"))

        print("Bulunan Microsoft dosyaları:", len(files))

        for file in files:
            print("-", file.name)

        return files

    def provider_info(self):
        return {
            "name": "Microsoft",
            "display_name": "Microsoft Global ML Building Footprints",
            "priority": 90,
            "quality": 0.85,
            "available": True,
            "capabilities": {
                "buildings": True,
                "height": False,
                "roof": False,
                "landmarks": False,
            },
        }

    def __init__(self):

        self.name = "Microsoft Global ML Building Footprints"

        self.data_folder = Path(
            "DATA_CONNECTORS/Microsoft/DATA"
        )

    def info(self):

        print("=" * 60)
        print(self.name)
        print("=" * 60)

        print("Status : Prototype")
        print("Folder :", self.data_folder)

        if self.data_folder.exists():
            print("Data folder : OK")
        else:
            print("Data folder : Missing")