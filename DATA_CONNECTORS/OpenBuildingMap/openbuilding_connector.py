"""
ATLAS Engine 2.0

OpenBuildingMap Connector

Version : 0.1
Status  : Prototype
"""

from pathlib import Path


class OpenBuildingConnector:

    def __init__(self):
        self.name = "OpenBuildingMap"
        self.data_folder = Path("DATA_CONNECTORS/OpenBuildingMap/DATA")

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

        print("Bulunan OpenBuildingMap dosyaları:", len(files))

        for file in files:
            print("-", file.name)

        return files

    def provider_info(self):
        return {
            "name": "OpenBuildingMap",
            "display_name": "OpenBuildingMap",
            "priority": 70,
            "quality": 0.70,
            "available": True,
            "capabilities": {
                "buildings": True,
                "height": True,
                "roof": False,
                "landmarks": False,
            },
        }
