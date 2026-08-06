from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_facade_bay_analyzer import (
    AtlasFacadeBayAnalysis,
)


def _normalize_identifier(
    value,
    *,
    field_name,
):
    normalized = "_".join(
        str(value).strip().lower().split()
    )

    if not normalized:
        raise ValueError(
            f"{field_name} must not be blank"
        )

    return normalized


@dataclass(frozen=True, slots=True)
class AtlasFacadeOpening:
    level_index: int
    bay_index: int
    opening_index: int
    opening_kind: str
    region_name: str
    u_min: float
    u_max: float
    v_min: float
    v_max: float
    bay_u_min: float
    bay_u_max: float
    floor_v_min: float
    floor_v_max: float

    def __post_init__(self) -> None:
        for field_name in (
            "level_index",
            "bay_index",
            "opening_index",
        ):
            value = getattr(
                self,
                field_name,
            )

            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or value < 0
            ):
                raise ValueError(
                    f"{field_name} must be a "
                    "non-negative integer"
                )

        opening_kind = _normalize_identifier(
            self.opening_kind,
            field_name="opening_kind",
        )
        region_name = _normalize_identifier(
            self.region_name,
            field_name="region_name",
        )

        u_min = float(self.u_min)
        u_max = float(self.u_max)
        v_min = float(self.v_min)
        v_max = float(self.v_max)
        bay_u_min = float(self.bay_u_min)
        bay_u_max = float(self.bay_u_max)
        floor_v_min = float(self.floor_v_min)
        floor_v_max = float(self.floor_v_max)

        if (
            u_min < 0.0
            or u_max > 1.0
            or u_max <= u_min
        ):
            raise ValueError(
                "opening horizontal bounds must satisfy "
                "0 <= u_min < u_max <= 1"
            )

        if (
            v_min < 0.0
            or v_max > 1.0
            or v_max <= v_min
        ):
            raise ValueError(
                "opening vertical bounds must satisfy "
                "0 <= v_min < v_max <= 1"
            )

        if (
            bay_u_min < 0.0
            or bay_u_max > 1.0
            or bay_u_max <= bay_u_min
        ):
            raise ValueError(
                "bay horizontal bounds must satisfy "
                "0 <= bay_u_min < bay_u_max <= 1"
            )

        if (
            floor_v_min < 0.0
            or floor_v_max > 1.0
            or floor_v_max <= floor_v_min
        ):
            raise ValueError(
                "floor vertical bounds must satisfy "
                "0 <= floor_v_min < floor_v_max <= 1"
            )

        object.__setattr__(
            self,
            "opening_kind",
            opening_kind,
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
            "v_min",
            v_min,
        )
        object.__setattr__(
            self,
            "v_max",
            v_max,
        )
        object.__setattr__(
            self,
            "bay_u_min",
            bay_u_min,
        )
        object.__setattr__(
            self,
            "bay_u_max",
            bay_u_max,
        )
        object.__setattr__(
            self,
            "floor_v_min",
            floor_v_min,
        )
        object.__setattr__(
            self,
            "floor_v_max",
            floor_v_max,
        )


@dataclass(frozen=True, slots=True)
class AtlasFacadeOpeningAnalysis:
    openings: tuple[
        AtlasFacadeOpening,
        ...,
    ]

    def __post_init__(self) -> None:
        openings = tuple(
            self.openings
        )

        if any(
            not isinstance(
                opening,
                AtlasFacadeOpening,
            )
            for opening in openings
        ):
            raise TypeError(
                "openings must contain "
                "AtlasFacadeOpening instances"
            )

        identities = {
            (
                opening.level_index,
                opening.bay_index,
                opening.opening_index,
            )
            for opening in openings
        }

        if len(identities) != len(openings):
            raise ValueError(
                "duplicate facade opening identity"
            )

        object.__setattr__(
            self,
            "openings",
            openings,
        )

    @property
    def opening_count(self):
        return len(
            self.openings
        )

    def openings_for_bay(
        self,
        *,
        level_index,
        bay_index,
    ) -> tuple[
        AtlasFacadeOpening,
        ...,
    ]:
        for field_name, value in (
            (
                "level_index",
                level_index,
            ),
            (
                "bay_index",
                bay_index,
            ),
        ):
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or value < 0
            ):
                raise ValueError(
                    f"{field_name} must be a "
                    "non-negative integer"
                )

        return tuple(
            opening
            for opening in self.openings
            if (
                opening.level_index
                == level_index
                and opening.bay_index
                == bay_index
            )
        )


class AtlasFacadeOpeningLayout:
    DEFAULT_HORIZONTAL_MARGIN_RATIO = 0.20
    DEFAULT_VERTICAL_MARGIN_RATIO = 0.20

    @classmethod
    def create_uniform(
        cls,
        *,
        bay_analysis,
        opening_kind,
        horizontal_margin_ratio=None,
        vertical_margin_ratio=None,
    ) -> AtlasFacadeOpeningAnalysis:
        if not isinstance(
            bay_analysis,
            AtlasFacadeBayAnalysis,
        ):
            raise TypeError(
                "bay_analysis must be an "
                "AtlasFacadeBayAnalysis instance"
            )

        opening_kind = _normalize_identifier(
            opening_kind,
            field_name="opening_kind",
        )

        horizontal_margin_ratio = (
            cls.DEFAULT_HORIZONTAL_MARGIN_RATIO
            if horizontal_margin_ratio is None
            else float(
                horizontal_margin_ratio
            )
        )
        vertical_margin_ratio = (
            cls.DEFAULT_VERTICAL_MARGIN_RATIO
            if vertical_margin_ratio is None
            else float(
                vertical_margin_ratio
            )
        )

        for field_name, margin_ratio in (
            (
                "horizontal_margin_ratio",
                horizontal_margin_ratio,
            ),
            (
                "vertical_margin_ratio",
                vertical_margin_ratio,
            ),
        ):
            if (
                margin_ratio < 0.0
                or margin_ratio >= 0.5
            ):
                raise ValueError(
                    f"{field_name} must satisfy "
                    "0 <= margin < 0.5"
                )

        facade_min_z = min(
            bay.min_z
            for bay in bay_analysis.bays
        )
        facade_max_z = max(
            bay.max_z
            for bay in bay_analysis.bays
        )
        facade_height = (
            facade_max_z - facade_min_z
        )

        openings = tuple(
            AtlasFacadeOpening(
                level_index=bay.level_index,
                bay_index=bay.bay_index,
                opening_index=0,
                opening_kind=opening_kind,
                region_name=bay.region_name,
                u_min=horizontal_margin_ratio,
                u_max=(
                    1.0
                    - horizontal_margin_ratio
                ),
                v_min=vertical_margin_ratio,
                v_max=(
                    1.0
                    - vertical_margin_ratio
                ),
                bay_u_min=bay.u_min,
                bay_u_max=bay.u_max,
                floor_v_min=(
                    (
                        bay.min_z
                        - facade_min_z
                    )
                    / facade_height
                ),
                floor_v_max=(
                    (
                        bay.max_z
                        - facade_min_z
                    )
                    / facade_height
                ),
            )
            for bay in bay_analysis.bays
        )

        return AtlasFacadeOpeningAnalysis(
            openings=openings,
        )
