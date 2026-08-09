class AtlasSemanticSurfaceTextureResolver:
    _PROFILES = {
        "park_ground": {
            "texture_language": "lawn",
            "geometry_mode": "shallow_relief",
            "relief_depth_mm": 0.08,
            "feature_pitch_mm": 2.40,
            "lod_min_level": 1,
        },
        "grass_ground": {
            "texture_language": "grass",
            "geometry_mode": "shallow_relief",
            "relief_depth_mm": 0.10,
            "feature_pitch_mm": 1.80,
            "lod_min_level": 1,
        },
        "plaza_ground": {
            "texture_language": "paving",
            "geometry_mode": "shallow_relief",
            "relief_depth_mm": 0.14,
            "feature_pitch_mm": 1.80,
            "lod_min_level": 1,
        },
        "pedestrian_square_ground": {
            "texture_language": "paving",
            "geometry_mode": "shallow_relief",
            "relief_depth_mm": 0.14,
            "feature_pitch_mm": 1.80,
            "lod_min_level": 1,
        },
        "garden_ground": {
            "texture_language": "lawn",
            "geometry_mode": "shallow_relief",
            "relief_depth_mm": 0.18,
            "feature_pitch_mm": 1.40,
            "lod_min_level": 1,
        },
        "cemetery_ground": {
            "texture_language": "ordered_ground",
            "geometry_mode": "shallow_relief",
            "relief_depth_mm": 0.14,
            "feature_pitch_mm": 1.80,
            "lod_min_level": 1,
        },
        "sports_field_ground": {
            "texture_language": "field",
            "geometry_mode": "shallow_relief",
            "relief_depth_mm": 0.12,
            "feature_pitch_mm": 2.00,
            "lod_min_level": 1,
        },
        "courtyard_ground": {
            "texture_language": "paving",
            "geometry_mode": "shallow_relief",
            "relief_depth_mm": 0.14,
            "feature_pitch_mm": 1.80,
            "lod_min_level": 1,
        },
    }

    @classmethod
    def resolve(
        cls,
        *,
        surface_role,
    ):
        profile = cls._PROFILES.get(
            surface_role
        )

        if profile is None:
            return None

        return {
            "surface_role": surface_role,
            **profile,
        }
