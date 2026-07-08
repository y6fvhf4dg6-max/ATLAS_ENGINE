"""
ATLAS Engine

Atlas Nature Object v1.0

Base object for all natural elements inside ATLAS.
"""


class AtlasNatureObject:
    def __init__(
        self,
        object_id,
        object_type,
        source,
        latitude,
        longitude,
        tags=None,
    ):
        self.object_id = object_id
        self.object_type = object_type
        self.source = source

        self.latitude = latitude
        self.longitude = longitude

        self.tags = tags or {}

    def summary(self):
        return {
            "id": self.object_id,
            "type": self.object_type,
            "source": self.source,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }
