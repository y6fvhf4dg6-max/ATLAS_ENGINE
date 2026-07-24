from CORE.atlas_landmark_geometry import AtlasLandmarkGeometry


class AtlasObeliskBuilder:
    DEFAULT_HEIGHT_M = 55.0

    @staticmethod
    def build(landmark):
        return AtlasLandmarkGeometry(
            footprint=landmark.geometry,
            height_m=AtlasObeliskBuilder.DEFAULT_HEIGHT_M,
        )
