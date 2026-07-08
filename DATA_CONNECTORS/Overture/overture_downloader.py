"""
ATLAS Engine 2.0

Overture Downloader
Purpose:
Download or register Overture Maps building data.
"""

from pathlib import Path


class OvertureDownloader:

    def __init__(self):

        self.data_folder = Path(
            "DATA_CONNECTORS/Overture/DATA"
        )

    def status(self):

        print("=" * 60)
        print("Overture Downloader")
        print("=" * 60)

        if self.data_folder.exists():
            print("DATA klasörü hazır.")
        else:
            print("DATA klasörü bulunamadı.")