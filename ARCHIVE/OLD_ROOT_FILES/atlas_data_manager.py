"""
ATLAS Engine 2.0

Module : Data Manager
Version: 0.1

Purpose:
Manage all external data providers used by ATLAS.
"""

from DATA_CONNECTORS.Microsoft.microsoft_connector import MicrosoftConnector
from DATA_CONNECTORS.Overture.overture_connector import OvertureConnector
from DATA_CONNECTORS.OpenBuildingMap.openbuilding_connector import OpenBuildingConnector


class AtlasDataManager:

    def __init__(self):
        self.providers = {}

    def register_default_providers(self):
        self.providers["Microsoft"] = MicrosoftConnector()
        self.providers["Overture"] = OvertureConnector()
        self.providers["OpenBuildingMap"] = OpenBuildingConnector()

    def status(self):
        print("=" * 60)
        print("ATLAS DATA MANAGER")
        print("=" * 60)

        print("Registered providers:", len(self.providers))

        for name, provider in self.providers.items():
            print("-", name, ":", provider.name)


def main():
    manager = AtlasDataManager()
    manager.register_default_providers()
    manager.status()


if __name__ == "__main__":
    main()
