from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AtlasFacadeFloorBand:
    level_index: int
    region_name: str
    min_z: float
    max_z: float

    def __post_init__(self) -> None:
        if (
            isinstance(self.level_index, bool)
            or not isinstance(self.level_index, int)
            or self.level_index < 0
        ):
            raise ValueError(
                "level_index must be a non-negative integer"
            )

        min_z = float(self.min_z)
        max_z = float(self.max_z)

        if max_z <= min_z:
            raise ValueError(
                "max_z must be greater than min_z"
            )

        region_name = "_".join(
            str(self.region_name)
            .strip()
            .lower()
            .split()
        )

        if not region_name:
            raise ValueError(
                "region_name must not be blank"
            )

        object.__setattr__(
            self,
            "region_name",
            region_name,
        )
        object.__setattr__(
            self,
            "min_z",
            min_z,
        )
        object.__setattr__(
            self,
            "max_z",
            max_z,
        )


@dataclass(frozen=True, slots=True)
class AtlasFacadeRegionAnalysis:
    level_count: int
    min_z: float
    max_z: float
    floor_bands: tuple[
        AtlasFacadeFloorBand,
        ...,
    ]

    def __post_init__(self) -> None:
        if (
            isinstance(self.level_count, bool)
            or not isinstance(self.level_count, int)
            or self.level_count < 1
        ):
            raise ValueError(
                "level_count must be a positive integer"
            )

        min_z = float(self.min_z)
        max_z = float(self.max_z)
        floor_bands = tuple(
            self.floor_bands
        )

        if max_z <= min_z:
            raise ValueError(
                "max_z must be greater than min_z"
            )

        if len(floor_bands) != self.level_count:
            raise ValueError(
                "floor_bands must match level_count"
            )

        if any(
            not isinstance(
                band,
                AtlasFacadeFloorBand,
            )
            for band in floor_bands
        ):
            raise TypeError(
                "floor_bands must contain "
                "AtlasFacadeFloorBand instances"
            )

        object.__setattr__(
            self,
            "min_z",
            min_z,
        )
        object.__setattr__(
            self,
            "max_z",
            max_z,
        )
        object.__setattr__(
            self,
            "floor_bands",
            floor_bands,
        )


class AtlasFacadeRegionAnalyzer:
    DEFAULT_FLOOR_HEIGHT_M = 3.5

    @staticmethod
    def _positive_level_count(value):
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return None

        if numeric <= 0.0:
            return None

        level_count = int(numeric)

        if level_count < 1:
            return None

        return level_count

    @classmethod
    def analyze(
        cls,
        *,
        tags,
        total_height_m,
        min_z=0.0,
        default_floor_height_m=None,
    ) -> AtlasFacadeRegionAnalysis:
        tags = tags or {}

        total_height_m = float(
            total_height_m
        )
        min_z = float(min_z)

        if total_height_m <= 0.0:
            raise ValueError(
                "total_height_m must be positive"
            )

        floor_height_m = (
            cls.DEFAULT_FLOOR_HEIGHT_M
            if default_floor_height_m is None
            else float(default_floor_height_m)
        )

        if floor_height_m <= 0.0:
            raise ValueError(
                "default_floor_height_m must be positive"
            )

        level_count = cls._positive_level_count(
            tags.get("building:levels")
        )

        if level_count is None:
            level_count = max(
                1,
                round(
                    total_height_m
                    / floor_height_m
                ),
            )

        max_z = min_z + total_height_m
        resolved_floor_height = (
            total_height_m / level_count
        )

        floor_bands = []

        for level_index in range(
            level_count
        ):
            band_min_z = (
                min_z
                + resolved_floor_height
                * level_index
            )
            band_max_z = (
                max_z
                if level_index
                == level_count - 1
                else min_z
                + resolved_floor_height
                * (level_index + 1)
            )

            if level_count == 1:
                region_name = (
                    "ground_top_floor"
                )
            elif level_index == 0:
                region_name = (
                    "ground_floor"
                )
            elif level_index == level_count - 1:
                region_name = (
                    "top_floor"
                )
            else:
                region_name = (
                    "upper_floor"
                )

            floor_bands.append(
                AtlasFacadeFloorBand(
                    level_index=level_index,
                    region_name=region_name,
                    min_z=band_min_z,
                    max_z=band_max_z,
                )
            )

        return AtlasFacadeRegionAnalysis(
            level_count=level_count,
            min_z=min_z,
            max_z=max_z,
            floor_bands=tuple(
                floor_bands
            ),
        )
