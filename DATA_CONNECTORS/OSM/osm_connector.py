"""
ATLAS Engine
OSM Connector
"""


class OSMConnector:

    def provider_info(self):
        return {
            "name": "OSM",
            "display_name": "OpenStreetMap",
            "priority": 100,
            "quality": 0.90,
            "available": True,
            "capabilities": {
                "buildings": True,
                "height": True,
                "roof": True,
                "landmarks": True,
            },
        }
