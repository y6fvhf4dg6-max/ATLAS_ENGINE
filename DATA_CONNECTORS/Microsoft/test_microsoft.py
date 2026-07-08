from DATA_CONNECTORS.Microsoft.microsoft_connector import MicrosoftConnector

m = MicrosoftConnector()
m.info()
m.list_files()
from DATA_CONNECTORS.Microsoft.microsoft_downloader import MicrosoftDownloader

d = MicrosoftDownloader()

d.status()