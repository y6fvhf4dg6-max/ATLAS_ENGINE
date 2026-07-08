"""
ATLAS Engine 2.0

Microsoft Downloader
Purpose:
Download or register Microsoft Global ML Building Footprints data.
"""
"""
ATLAS Engine 2.0

Microsoft Downloader
"""

from pathlib import Path


class MicrosoftDownloader:

    def __init__(self):

        self.data_folder = Path(
            "DATA_CONNECTORS/Microsoft/DATA"
        )

    def status(self):

        print("=" * 60)
        print("Microsoft Downloader")
        print("=" * 60)

        if self.data_folder.exists():
            print("DATA klasörü hazır.")
        else:
            print("DATA klasörü bulunamadı.")