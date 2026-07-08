"""
ATLAS Engine 2.0

Overture Maps Connector

Version : 0.1
Status  : Prototype
"""

from pathlib import Path


class OvertureConnector:

    def __init__(self):

        self.name = "Overture Maps Buildings"

        self.data_folder = Path("DATA_CONNECTORS/Overture/DATA")

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

    def list_files(self):

        if not self.data_folder.exists():
            print("Data folder bulunamadı.")
            return []

        files = list(self.data_folder.glob("*"))

        print("Bulunan Overture dosyaları:", len(files))

        for file in files:
            print("-", file.name)

        return files

    def provider_info(self):
        return {
            "name": "Overture",
            "display_name": "Overture Maps Buildings",
            "priority": 80,
            "quality": 0.80,
            "available": True,
            "capabilities": {
                "buildings": True,
                "height": True,
                "roof": True,
                "landmarks": True,
            },
        }
