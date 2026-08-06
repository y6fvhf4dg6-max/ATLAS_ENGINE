from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_facade_region_analyzer import (
    AtlasFacadeRegionAnalysis,
)


@dataclass(frozen=True, slots=True)
class AtlasFacadeBay:
    level_index: int
    bay_index: int
    region_name: str
    u_min: float
    u_max: float
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

        if (
            isinstance(self.bay_index, bool)
            or not isinstance(self.bay_index, int)
            or self.bay_index < 0
        ):
            raise ValueError(
                "bay_index must be a non-negative integer"
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

        u_min = float(self.u_min)
        u_max = float(self.u_max)
        min_z = float(self.min_z)
        max_z = float(self.max_z)

        if (
            u_min < 0.0
            or u_max > 1.0
            or u_max <= u_min
        ):
            raise ValueError(
                "bay horizontal bounds must satisfy "
                "0 <= u_min < u_max <= 1"
            )

        if max_z <= min_z:
            raise ValueError(
                "max_z must be greater than min_z"
            )

        object.__setattr__(
            self,
            "region_name",
            region_name,
        )
        object.__setattr__(
            self,
            "u_min",
            u_min,
        )
        object.__setattr__(
            self,
            "u_max",
            u_max,
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
class AtlasFacadeBayAnalysis:
    level_count: int
    bay_count: int
    bays: tuple[
        AtlasFacadeBay,
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

        if (
            isinstance(self.bay_count, bool)
            or not isinstance(self.bay_count, int)
            or self.bay_count < 1
        ):
            raise ValueError(
                "bay_count must be a positive integer"
            )

        bays = tuple(self.bays)

        if len(bays) != (
            self.level_count
            * self.bay_count
        ):
            raise ValueError(
                "bays must match level_count * bay_count"
            )

        if any(
            not isinstance(
                bay,
                AtlasFacadeBay,
            )
            for bay in bays
        ):
            raise TypeError(
                "bays must contain AtlasFacadeBay instances"
            )

        identities = {
            (
                bay.level_index,
                bay.bay_index,
            )
            for bay in bays
        }

        if len(identities) != len(bays):
            raise ValueError(
                "duplicate facade bay identity"
            )

        object.__setattr__(
            self,
            "bays",
            bays,
        )

    def bays_for_level(
        self,
        level_index,
    ) -> tuple[
        AtlasFacadeBay,
        ...,
    ]:
        if (
            isinstance(level_index, bool)
            or not isinstance(level_index, int)
            or level_index < 0
            or level_index >= self.level_count
        ):
            raise ValueError(
                "level_index is outside facade analysis"
            )

        return tuple(
            bay
            for bay in self.bays
            if bay.level_index == level_index
        )


class AtlasFacadeBayAnalyzer:
    @classmethod
    def analyze(
        cls,
        *,
        region_analysis,
        bay_count,
    ) -> AtlasFacadeBayAnalysis:
        if not isinstance(
            region_analysis,
            AtlasFacadeRegionAnalysis,
        ):
            raise TypeError(
                "region_analysis must be an "
                "AtlasFacadeRegionAnalysis instance"
            )

        if (
            isinstance(bay_count, bool)
            or not isinstance(bay_count, int)
            or bay_count < 1
        ):
            raise ValueError(
                "bay_count must be a positive integer"
            )

        bay_width = 1.0 / bay_count
        bays = []

        for floor_band in (
            region_analysis.floor_bands
        ):
            for bay_index in range(
                bay_count
            ):
                u_min = (
                    bay_index
                    * bay_width
                )
                u_max = (
                    1.0
                    if bay_index == bay_count - 1
                    else (
                        bay_index + 1
                    ) * bay_width
                )

                bays.append(
                    AtlasFacadeBay(
                        level_index=(
                            floor_band.level_index
                        ),
                        bay_index=bay_index,
                        region_name=(
                            floor_band.region_name
                        ),
                        u_min=u_min,
                        u_max=u_max,
                        min_z=floor_band.min_z,
                        max_z=floor_band.max_z,
                    )
                )

        return AtlasFacadeBayAnalysis(
            level_count=(
                region_analysis.level_count
            ),
            bay_count=bay_count,
            bays=tuple(bays),
        )
