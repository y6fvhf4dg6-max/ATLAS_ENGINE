from CORE.atlas_landmark_geometry import AtlasLandmarkGeometry


class AtlasObeliskBuilder:
    DEFAULT_HEIGHT_M = 55.0

    @staticmethod
    def _try_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def build(landmark):
        height_m = AtlasObeliskBuilder._try_float(
            landmark.tags.get("height")
        )

        if height_m is None:
            height_m = AtlasObeliskBuilder.DEFAULT_HEIGHT_M

        return AtlasLandmarkGeometry(
            footprint=landmark.geometry,
            height_m=height_m,
        )
