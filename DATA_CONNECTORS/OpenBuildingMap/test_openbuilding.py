from DATA_CONNECTORS.OpenBuildingMap.openbuilding_connector import OpenBuildingConnector
from DATA_CONNECTORS.OpenBuildingMap.openbuilding_downloader import OpenBuildingDownloader

o = OpenBuildingConnector()
o.info()
o.list_files()

d = OpenBuildingDownloader()
d.status()