from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_facade_region_analyzer import (
    AtlasFacadeRegionAnalysis,
)


@dataclass(frozen=True, slots=True)
class AtlasFacadeCornice:
    cornice_index: int
    boundary_level_index: int
    cornice_kind: str
    z: float
    u_min: float = 0.0
    u_max: float = 1.0

    def __post_init__(self) -> None:
        if (
            isinstance(self.cornice_index, bool)
            or not isinstance(self.cornice_index, int)
            or self.cornice_index < 0
        ):
            raise ValueError(
                "cornice_index must be a non-negative integer"
            )

        if (
            isinstance(self.boundary_level_index, bool)
            or not isinstance(
                self.boundary_level_index,
                int,
            )
            or self.boundary_level_index < 1
        ):
            raise ValueError(
                "boundary_level_index must be a positive integer"
            )

        cornice_kind = "_".join(
            str(self.cornice_kind)
            .strip()
            .lower()
            .split()
        )

        if cornice_kind not in {
            "floor_cornice",
            "top_cornice",
        }:
            raise ValueError(
                "cornice_kind must be floor_cornice or top_cornice"
            )

        z = float(self.z)
        u_min = float(self.u_min)
        u_max = float(self.u_max)

        if (
            u_min < 0.0
            or u_max > 1.0
            or u_max <= u_min
        ):
            raise ValueError(
                "cornice horizontal bounds must satisfy "
                "0 <= u_min < u_max <= 1"
            )

        object.__setattr__(
            self,
            "cornice_kind",
            cornice_kind,
        )
        object.__setattr__(
            self,
            "z",
            z,
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


@dataclass(frozen=True, slots=True)
class AtlasFacadeCorniceAnalysis:
    cornices: tuple[
        AtlasFacadeCornice,
        ...,
    ]
    include_top_cornice: bool = False

    def __post_init__(self) -> None:
        cornices = tuple(
            self.cornices
        )

        if any(
            not isinstance(
                cornice,
                AtlasFacadeCornice,
            )
            for cornice in cornices
        ):
            raise TypeError(
                "cornices must contain AtlasFacadeCornice instances"
            )

        indices = tuple(
            cornice.cornice_index
            for cornice in cornices
        )

        if indices != tuple(
            range(len(cornices))
        ):
            raise ValueError(
                "cornice indices must be ordered and contiguous"
            )

        object.__setattr__(
            self,
            "cornices",
            cornices,
        )
        object.__setattr__(
            self,
            "include_top_cornice",
            bool(self.include_top_cornice),
        )

    @property
    def cornice_count(self):
        return len(
            self.cornices
        )


class AtlasFacadeCorniceLayout:
    @classmethod
    def create(
        cls,
        *,
        region_analysis,
        include_top_cornice=False,
    ) -> AtlasFacadeCorniceAnalysis:
        if not isinstance(
            region_analysis,
            AtlasFacadeRegionAnalysis,
        ):
            raise TypeError(
                "region_analysis must be an "
                "AtlasFacadeRegionAnalysis instance"
            )

        include_top_cornice = bool(
            include_top_cornice
        )

        cornices = []

        for floor_band in (
            region_analysis.floor_bands[:-1]
        ):
            cornices.append(
                AtlasFacadeCornice(
                    cornice_index=len(cornices),
                    boundary_level_index=(
                        floor_band.level_index + 1
                    ),
                    cornice_kind="floor_cornice",
                    z=floor_band.max_z,
                )
            )

        if include_top_cornice:
            cornices.append(
                AtlasFacadeCornice(
                    cornice_index=len(cornices),
                    boundary_level_index=(
                        region_analysis.level_count
                    ),
                    cornice_kind="top_cornice",
                    z=region_analysis.max_z,
                )
            )

        return AtlasFacadeCorniceAnalysis(
            cornices=tuple(cornices),
            include_top_cornice=(
                include_top_cornice
            ),
        )
