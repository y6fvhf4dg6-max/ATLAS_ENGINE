# CORE/providers/nature/atlas_copernicus_provider.py

"""
ATLAS Copernicus Nature Provider v0.1

Copernicus arazi örtüsü verileri için provider iskeleti.

Amaç:
- OSM'nin eksik doğa verilerini desteklemek
- Ağaç ve orman örtüsünü doğrulamak
- Çim, çalılık ve su alanlarını tespit etmek

Bu ilk sürüm:
- bbox doğrular
- standart ATLAS nature sonucu döndürür
- gerçek veri bağlantısı sonraki aşamada eklenecektir
"""

from CORE.providers.nature.atlas_nature_provider import (
    AtlasNatureProvider,
)


class AtlasCopernicusProvider(AtlasNatureProvider):
    PROVIDER_NAME = "copernicus"

    def fetch(self, bbox):
        self.validate_bbox(bbox)

        result = self.empty_result(self.PROVIDER_NAME)

        result["metadata"].update(
            {
                "source_resolution_m": 10,
                "license": "Copernicus free and open data",
                "status": "provider_ready_api_not_connected",
                "confidence": {},
            }
        )

        return result
