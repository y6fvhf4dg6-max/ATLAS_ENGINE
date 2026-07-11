# CORE/providers/nature/atlas_dynamic_world_provider.py

"""
ATLAS Dynamic World Nature Provider v0.1

Google Dynamic World arazi örtüsü verisi için provider iskeleti.

Bu ilk sürüm:
- bbox doğrular
- standart ATLAS nature sonucu döndürür
- gerçek API bağlantısı sonraki aşamada eklenecektir
"""

from CORE.providers.nature.atlas_nature_provider import (
    AtlasNatureProvider,
)


class AtlasDynamicWorldProvider(AtlasNatureProvider):
    PROVIDER_NAME = "dynamic_world"

    def fetch(self, bbox):
        self.validate_bbox(bbox)

        result = self.empty_result(self.PROVIDER_NAME)

        result["metadata"].update(
            {
                "source_resolution_m": 10,
                "license": "CC BY 4.0",
                "status": "provider_ready_api_not_connected",
                "confidence": {},
            }
        )

        return result
