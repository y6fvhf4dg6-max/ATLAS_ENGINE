# CORE/providers/nature/atlas_nature_provider.py

"""
ATLAS Nature Provider Interface v0.1

Tüm doğa veri sağlayıcıları aynı veri yapısını döndürür.
Bu sayede Nature Pipeline, sağlayıcının OSM, Dynamic World,
Copernicus, WorldCover veya Esri olduğunu bilmek zorunda kalmaz.
"""

from abc import ABC, abstractmethod


class AtlasNatureProvider(ABC):
    """
    Base interface for all ATLAS nature data providers.
    """

    PROVIDER_NAME = "base"

    @abstractmethod
    def fetch(self, bbox):
        """
        Verilen bbox için normalize edilmiş doğa verisi döndürür.

        bbox:
            (south, west, north, east)

        Beklenen dönüş yapısı:

        {
            "trees": [],
            "tree_rows": [],
            "tree_cover": [],
            "forests": [],
            "grass": [],
            "scrub": [],
            "water": [],
            "metadata": {
                "provider": "...",
                "source_resolution_m": None,
                "license": None,
                "confidence": {},
            },
        }
        """
        raise NotImplementedError

    @staticmethod
    def empty_result(provider_name="unknown"):
        return {
            "trees": [],
            "tree_rows": [],
            "tree_cover": [],
            "forests": [],
            "grass": [],
            "scrub": [],
            "water": [],
            "metadata": {
                "provider": provider_name,
                "source_resolution_m": None,
                "license": None,
                "confidence": {},
            },
        }

    @staticmethod
    def validate_bbox(bbox):
        if not bbox or len(bbox) != 4:
            raise ValueError("bbox must be a tuple: (south, west, north, east)")

        south, west, north, east = bbox

        if south >= north:
            raise ValueError("bbox south must be smaller than north")

        if west >= east:
            raise ValueError("bbox west must be smaller than east")

        return True
