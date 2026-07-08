from DATA_CONNECTORS.Overture.overture_connector import OvertureConnector
from DATA_CONNECTORS.Overture.overture_downloader import OvertureDownloader

o = OvertureConnector()
o.info()
o.list_files()

d = OvertureDownloader()
d.status()