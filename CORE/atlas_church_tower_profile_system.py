from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AtlasChurchTowerProfile:
    tower_type: str
    body_shape: str
    polygon_sides: int
    roof_shape: str
    roof_sides: int

    center_longitudinal_ratio: float
    center_lateral_ratio: float

    longitudinal_ratio: float
    lateral_ratio: float

    body_top_ratio: float
    roof_top_ratio: float


@dataclass(frozen=True, slots=True)
class AtlasChurchTowerProfileCollection:
    towers: tuple[AtlasChurchTowerProfile, ...]

    def tower(
        self,
        tower_type,
    ) -> AtlasChurchTowerProfile:
        for tower in self.towers:
            if tower.tower_type == tower_type:
                return tower

        raise KeyError(
            f"Unknown church tower type: {tower_type}"
        )


class AtlasChurchTowerProfileSystem:
    @classmethod
    def resolve(
        cls,
        *,
        longitudinal_span,
        lateral_span,
        building_height,
        landmark_class,
    ) -> AtlasChurchTowerProfileCollection:
        longitudinal_span = float(
            longitudinal_span
        )
        lateral_span = float(
            lateral_span
        )
        building_height = float(
            building_height
        )
        landmark_class = str(
            landmark_class
        ).strip().lower()

        if longitudinal_span <= 0.0:
            raise ValueError(
                "longitudinal_span must be greater than zero"
            )

        if lateral_span <= 0.0:
            raise ValueError(
                "lateral_span must be greater than zero"
            )

        if building_height <= 0.0:
            raise ValueError(
                "building_height must be greater than zero"
            )

        if landmark_class not in {
            "church",
            "cathedral",
        }:
            raise ValueError(
                "landmark_class must be church or cathedral"
            )

        if landmark_class == "cathedral":
            towers = (
                AtlasChurchTowerProfile(
                    tower_type="crossing_tower",
                    body_shape="polygon",
                    polygon_sides=8,
                    roof_shape="polygon_spire",
                    roof_sides=8,
                    center_longitudinal_ratio=0.02,
                    center_lateral_ratio=0.0,
                    longitudinal_ratio=0.28,
                    lateral_ratio=0.42,
                    body_top_ratio=0.84,
                    roof_top_ratio=0.96,
                ),
                AtlasChurchTowerProfile(
                    tower_type="outer_polygon_tower",
                    body_shape="polygon",
                    polygon_sides=8,
                    roof_shape="polygon_spire",
                    roof_sides=8,
                    center_longitudinal_ratio=0.32,
                    center_lateral_ratio=0.42,
                    longitudinal_ratio=0.22,
                    lateral_ratio=0.34,
                    body_top_ratio=0.54,
                    roof_top_ratio=0.65,
                ),
                AtlasChurchTowerProfile(
                    tower_type="west_tower_left",
                    body_shape="box",
                    polygon_sides=4,
                    roof_shape="polygon_spire",
                    roof_sides=4,
                    center_longitudinal_ratio=-0.41,
                    center_lateral_ratio=-0.24,
                    longitudinal_ratio=0.16,
                    lateral_ratio=0.18,
                    body_top_ratio=0.72,
                    roof_top_ratio=0.88,
                ),
                AtlasChurchTowerProfile(
                    tower_type="west_tower_right",
                    body_shape="box",
                    polygon_sides=4,
                    roof_shape="polygon_spire",
                    roof_sides=4,
                    center_longitudinal_ratio=-0.41,
                    center_lateral_ratio=0.24,
                    longitudinal_ratio=0.16,
                    lateral_ratio=0.18,
                    body_top_ratio=0.72,
                    roof_top_ratio=0.88,
                ),
            )
        else:
            towers = (
                AtlasChurchTowerProfile(
                    tower_type="crossing_tower",
                    body_shape="polygon",
                    polygon_sides=8,
                    roof_shape="polygon_spire",
                    roof_sides=8,
                    center_longitudinal_ratio=0.0,
                    center_lateral_ratio=0.0,
                    longitudinal_ratio=0.18,
                    lateral_ratio=0.26,
                    body_top_ratio=0.76,
                    roof_top_ratio=0.94,
                ),
                AtlasChurchTowerProfile(
                    tower_type="front_polygon_tower",
                    body_shape="polygon",
                    polygon_sides=6,
                    roof_shape="polygon_spire",
                    roof_sides=6,
                    center_longitudinal_ratio=-0.22,
                    center_lateral_ratio=0.0,
                    longitudinal_ratio=0.14,
                    lateral_ratio=0.20,
                    body_top_ratio=0.60,
                    roof_top_ratio=0.76,
                ),
                AtlasChurchTowerProfile(
                    tower_type="west_tower_left",
                    body_shape="box",
                    polygon_sides=4,
                    roof_shape="polygon_spire",
                    roof_sides=4,
                    center_longitudinal_ratio=-0.40,
                    center_lateral_ratio=0.0,
                    longitudinal_ratio=0.16,
                    lateral_ratio=0.18,
                    body_top_ratio=0.68,
                    roof_top_ratio=0.84,
                ),
            )

        return AtlasChurchTowerProfileCollection(
            towers=towers
        )
