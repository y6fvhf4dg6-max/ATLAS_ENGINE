"""
ATLAS Engine 2.0

OpenBuildingMap Downloader
Purpose:
Download or register OpenBuildingMap data.
"""

from pathlib import Path


class OpenBuildingDownloader:

    def __init__(self):
        self.data_folder = Path("DATA_CONNECTORS/OpenBuildingMap/DATA")

    def status(self):
        print("=" * 60)
        print("OpenBuildingMap Downloader")
        print("=" * 60)

        if self.data_folder.exists():
            print("DATA klasörü hazır.")
        else:
            print("DATA klasörü bulunamadı.")