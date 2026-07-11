# CORE/providers/nature/atlas_osm_provider.py

"""
ATLAS OSM Nature Provider v0.1
"""

from CORE.providers.nature.atlas_nature_provider import (
    AtlasNatureProvider,
)


class AtlasOSMProvider(AtlasNatureProvider):

    PROVIDER_NAME = "osm"

    def fetch(self, bbox):

        self.validate_bbox(bbox)

        result = self.empty_result(self.PROVIDER_NAME)

        # Gerçek OSM entegrasyonu
        # bir sonraki adımda gelecek.

        return result
