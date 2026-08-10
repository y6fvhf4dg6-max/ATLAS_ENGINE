from __future__ import annotations


class AtlasMorphologyCompositionPolicy:
    PROFILES = {
        "dense_urban": {
            "terrain_emphasis": 0.35,
            "road_emphasis": 0.90,
            "urban_block_emphasis": 0.90,
            "vegetation_emphasis": 0.45,
            "water_emphasis": 0.55,
            "infrastructure_emphasis": 0.85,
            "landmark_emphasis": 0.90,
        },
        "historic_core": {
            "terrain_emphasis": 0.35,
            "road_emphasis": 0.90,
            "urban_block_emphasis": 0.95,
            "vegetation_emphasis": 0.40,
            "water_emphasis": 0.55,
            "infrastructure_emphasis": 0.70,
            "landmark_emphasis": 1.00,
        },
        "suburban": {
            "terrain_emphasis": 0.60,
            "road_emphasis": 0.70,
            "urban_block_emphasis": 0.65,
            "vegetation_emphasis": 0.75,
            "water_emphasis": 0.60,
            "infrastructure_emphasis": 0.60,
            "landmark_emphasis": 0.80,
        },
        "forest": {
            "terrain_emphasis": 0.70,
            "road_emphasis": 0.60,
            "urban_block_emphasis": 0.35,
            "vegetation_emphasis": 1.00,
            "water_emphasis": 0.65,
            "infrastructure_emphasis": 0.50,
            "landmark_emphasis": 0.75,
        },
        "rural": {
            "terrain_emphasis": 0.90,
            "road_emphasis": 0.55,
            "urban_block_emphasis": 0.45,
            "vegetation_emphasis": 0.80,
            "water_emphasis": 0.65,
            "infrastructure_emphasis": 0.45,
            "landmark_emphasis": 0.70,
        },
        "river_city": {
            "terrain_emphasis": 0.55,
            "road_emphasis": 0.70,
            "urban_block_emphasis": 0.65,
            "vegetation_emphasis": 0.60,
            "water_emphasis": 1.00,
            "infrastructure_emphasis": 0.90,
            "landmark_emphasis": 0.85,
        },
        "coastal": {
            "terrain_emphasis": 0.60,
            "road_emphasis": 0.65,
            "urban_block_emphasis": 0.60,
            "vegetation_emphasis": 0.60,
            "water_emphasis": 1.00,
            "infrastructure_emphasis": 0.90,
            "landmark_emphasis": 0.85,
        },
        "mountain": {
            "terrain_emphasis": 1.00,
            "road_emphasis": 0.55,
            "urban_block_emphasis": 0.45,
            "vegetation_emphasis": 0.70,
            "water_emphasis": 0.55,
            "infrastructure_emphasis": 0.50,
            "landmark_emphasis": 0.80,
        },
        "mixed": {
            "terrain_emphasis": 0.65,
            "road_emphasis": 0.65,
            "urban_block_emphasis": 0.65,
            "vegetation_emphasis": 0.65,
            "water_emphasis": 0.65,
            "infrastructure_emphasis": 0.65,
            "landmark_emphasis": 0.80,
        },
    }

    @classmethod
    def resolve(
        cls,
        *,
        morphology,
        scene_evidence=None,
    ):
        normalized = "_".join(
            str(morphology).strip().lower().split()
        )

        if normalized not in cls.PROFILES:
            raise ValueError(
                "morphology must be a supported "
                "scene morphology"
            )

        if normalized != "mixed":
            return {
                "morphology": normalized,
                "profile_source": "named_profile",
                **cls.PROFILES[normalized],
            }

        evidence = dict(
            scene_evidence or {}
        )

        if not evidence:
            return {
                "morphology": normalized,
                "profile_source": "named_profile",
                **cls.PROFILES[normalized],
            }

        def ratio(name):
            value = float(
                evidence.get(
                    name,
                    0.0,
                )
            )

            return min(
                1.0,
                max(
                    0.0,
                    value,
                ),
            )

        building = ratio(
            "building_density"
        )
        road = ratio(
            "road_density"
        )
        block = ratio(
            "block_compactness"
        )
        vegetation = ratio(
            "vegetation_coverage"
        )
        forest = ratio(
            "forest_coverage"
        )
        water = ratio(
            "water_coverage"
        )
        terrain = ratio(
            "terrain_relief"
        )
        landmark = ratio(
            "landmark_density"
        )

        railway = bool(
            evidence.get(
                "railway_presence",
                False,
            )
        )

        urban_signal = min(
            1.0,
            (
                building
                + road
                + block
            )
            / 1.5,
        )

        water_signal = min(
            1.0,
            water / 0.30,
        )

        green_signal = max(
            vegetation,
            forest,
        )

        infrastructure_signal = min(
            1.0,
            0.55 * road
            + 0.30 * water_signal
            + 0.15 * float(
                railway
            ),
        )

        result = {
            "morphology": "mixed",
            "profile_source": "evidence_blend",
            "terrain_emphasis": min(
                1.0,
                max(
                    0.35,
                    0.45
                    + 0.45 * terrain,
                ),
            ),
            "road_emphasis": min(
                1.0,
                max(
                    0.55,
                    0.55
                    + 0.35 * road
                    + 0.10 * urban_signal,
                ),
            ),
            "urban_block_emphasis": min(
                1.0,
                max(
                    0.45,
                    0.45
                    + 0.40 * block
                    + 0.15 * building,
                ),
            ),
            "vegetation_emphasis": min(
                1.0,
                max(
                    0.45,
                    0.45
                    + 0.45 * green_signal,
                ),
            ),
            "water_emphasis": min(
                1.0,
                max(
                    0.50,
                    0.50
                    + 0.50 * water_signal,
                ),
            ),
            "infrastructure_emphasis": min(
                1.0,
                max(
                    0.50,
                    0.50
                    + 0.50 * infrastructure_signal,
                ),
            ),
            "landmark_emphasis": min(
                1.0,
                max(
                    0.70,
                    0.75
                    + 0.25 * landmark,
                ),
            ),
        }

        return result
