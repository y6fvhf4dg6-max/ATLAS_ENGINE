from __future__ import annotations

import math


class AtlasSceneMorphologyClassifier:
    MORPHOLOGIES = (
        "dense_urban",
        "historic_core",
        "suburban",
        "rural",
        "forest",
        "river_city",
        "coastal",
        "mountain",
        "mixed",
    )

    @staticmethod
    def _ratio(value, *, field_name):
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                f"{field_name} must be numeric"
            ) from exc

        if (
            not math.isfinite(value)
            or not 0.0 <= value <= 1.0
        ):
            raise ValueError(
                f"{field_name} must be finite "
                "and within 0..1"
            )

        return value

    @classmethod
    def resolve(
        cls,
        *,
        building_density,
        road_density,
        block_compactness,
        vegetation_coverage,
        forest_coverage,
        water_coverage,
        railway_presence,
        terrain_relief,
        landmark_density,
    ):
        evidence = {
            "building_density": cls._ratio(
                building_density,
                field_name="building_density",
            ),
            "road_density": cls._ratio(
                road_density,
                field_name="road_density",
            ),
            "block_compactness": cls._ratio(
                block_compactness,
                field_name="block_compactness",
            ),
            "vegetation_coverage": cls._ratio(
                vegetation_coverage,
                field_name="vegetation_coverage",
            ),
            "forest_coverage": cls._ratio(
                forest_coverage,
                field_name="forest_coverage",
            ),
            "water_coverage": cls._ratio(
                water_coverage,
                field_name="water_coverage",
            ),
            "railway_presence": railway_presence,
            "terrain_relief": cls._ratio(
                terrain_relief,
                field_name="terrain_relief",
            ),
            "landmark_density": cls._ratio(
                landmark_density,
                field_name="landmark_density",
            ),
        }

        if not isinstance(
            railway_presence,
            bool,
        ):
            raise TypeError(
                "railway_presence must be bool"
            )

        scores = cls._score(evidence)

        ordered = sorted(
            scores.items(),
            key=lambda item: (
                -item[1],
                cls.MORPHOLOGIES.index(
                    item[0]
                ),
            ),
        )

        morphology, winning_score = ordered[0]
        second_score = (
            ordered[1][1]
            if len(ordered) > 1
            else 0.0
        )

        if (
            winning_score < 0.35
            or winning_score - second_score < 0.04
        ):
            morphology = "mixed"

        confidence = max(
            0.01,
            min(
                1.0,
                winning_score,
            ),
        )

        return {
            "morphology": morphology,
            "confidence": confidence,
            "scores": scores,
            "evidence": evidence,
        }

    @staticmethod
    def _score(e):
        urban = (
            0.40 * e["building_density"]
            + 0.30 * e["road_density"]
            + 0.30 * e["block_compactness"]
        )

        green = max(
            e["vegetation_coverage"],
            e["forest_coverage"],
        )

        open_vegetation = max(
            0.0,
            e["vegetation_coverage"]
            - e["forest_coverage"],
        )

        water_dominance = min(
            1.0,
            e["water_coverage"] / 0.30,
        )

        landmark_presence = min(
            1.0,
            e["landmark_density"] / 0.08,
        )

        developed_presence = (
            0.50
            * min(
                1.0,
                e["building_density"] / 0.30,
            )
            + 0.50
            * min(
                1.0,
                e["road_density"] / 0.20,
            )
        )

        vegetation_presence = min(
            1.0,
            e["vegetation_coverage"] / 0.40,
        )

        moderate_urban_character = max(
            0.0,
            1.0
            - abs(urban - 0.35) / 0.35,
        )

        excessive_density = min(
            1.0,
            max(
                e["building_density"],
                e["road_density"],
            )
            / 0.80,
        )

        return {
            "dense_urban": (
                0.70 * urban
                + 0.10 * (
                    1.0
                    - e["vegetation_coverage"]
                )
                + 0.05 * (
                    1.0
                    - e["water_coverage"]
                )
                + 0.05 * (
                    1.0
                    - e["terrain_relief"]
                )
                + 0.10 * float(
                    e["railway_presence"]
                )
            ),
            "historic_core": (
                0.20 * urban
                + 0.40 * landmark_presence
                + 0.30 * e["block_compactness"]
                + 0.10 * (
                    1.0
                    - excessive_density
                )
                + 0.06 * moderate_urban_character
            ),
            "suburban": (
                0.40 * developed_presence
                + 0.35 * (
                    developed_presence
                    * vegetation_presence
                )
                + 0.15 * vegetation_presence
                + 0.05 * (
                    1.0
                    - e["block_compactness"]
                )
                + 0.05 * (
                    1.0
                    - e["terrain_relief"]
                )
            ),
            "rural": (
                0.25 * (
                    1.0
                    - e["building_density"]
                )
                + 0.15 * (
                    1.0
                    - e["road_density"]
                )
                + 0.35 * open_vegetation
                + 0.15 * (
                    1.0
                    - e["block_compactness"]
                )
                + 0.10 * e["terrain_relief"]
            ),
            "forest": (
                0.65 * e["forest_coverage"]
                + 0.20 * e["vegetation_coverage"]
                + 0.10 * (
                    1.0
                    - e["building_density"]
                )
                + 0.05 * (
                    1.0
                    - e["road_density"]
                )
            ),
            "river_city": (
                0.55 * water_dominance
                + 0.25 * urban
                + 0.10 * float(
                    e["railway_presence"]
                )
                + 0.10 * (
                    1.0
                    - e["terrain_relief"]
                )
            ),
            "coastal": (
                0.58 * e["water_coverage"]
                + 0.20 * (
                    1.0
                    - e["terrain_relief"]
                )
                + 0.12 * e["road_density"]
                + 0.10 * e["building_density"]
            ),
            "mountain": (
                0.62 * e["terrain_relief"]
                + 0.18 * green
                + 0.10 * (
                    1.0
                    - e["road_density"]
                )
                + 0.10 * (
                    1.0
                    - e["building_density"]
                )
            ),
            "mixed": 0.0,
        }
