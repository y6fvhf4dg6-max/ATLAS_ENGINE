from __future__ import annotations

from dataclasses import dataclass


def _normalize_identifier(
    value,
    *,
    field_name: str,
) -> str:
    normalized = "_".join(
        str(value).strip().lower().split()
    )

    if not normalized:
        raise ValueError(
            f"{field_name} must not be blank"
        )

    return normalized


@dataclass(frozen=True, slots=True)
class AtlasLoDLevel:
    level: int
    name: str
    included_features: tuple[str, ...]

    def __post_init__(self) -> None:
        level = self.level

        if (
            isinstance(level, bool)
            or not isinstance(level, int)
            or not 0 <= level <= 4
        ):
            raise ValueError(
                "level must be an integer in the 0..4 range"
            )

        name = _normalize_identifier(
            self.name,
            field_name="name",
        )

        included_features = tuple(
            _normalize_identifier(
                feature,
                field_name="included_feature",
            )
            for feature in self.included_features
        )

        if not included_features:
            raise ValueError(
                "included_features must not be empty"
            )

        if (
            len(included_features)
            != len(set(included_features))
        ):
            raise ValueError(
                "included_features must be unique"
            )

        object.__setattr__(
            self,
            "level",
            level,
        )
        object.__setattr__(
            self,
            "name",
            name,
        )
        object.__setattr__(
            self,
            "included_features",
            included_features,
        )

    def supports(
        self,
        feature,
    ) -> bool:
        normalized = _normalize_identifier(
            feature,
            field_name="feature",
        )

        return normalized in self.included_features


LOD_0 = AtlasLoDLevel(
    level=0,
    name="footprint_mass",
    included_features=(
        "footprint",
        "base_mass",
    ),
)

LOD_1 = AtlasLoDLevel(
    level=1,
    name="primary_form",
    included_features=(
        *LOD_0.included_features,
        "main_body",
        "primary_roof",
    ),
)

LOD_2 = AtlasLoDLevel(
    level=2,
    name="major_components",
    included_features=(
        *LOD_1.included_features,
        "tower",
        "dome",
        "apse",
        "major_component",
    ),
)

LOD_3 = AtlasLoDLevel(
    level=3,
    name="structural_detail",
    included_features=(
        *LOD_2.included_features,
        "facade_opening",
        "structural_detail",
    ),
)

LOD_4 = AtlasLoDLevel(
    level=4,
    name="ornament_relief",
    included_features=(
        *LOD_3.included_features,
        "ornament",
        "architectural_relief",
    ),
)


class AtlasLoDLevelCatalog:
    _LEVELS = (
        LOD_0,
        LOD_1,
        LOD_2,
        LOD_3,
        LOD_4,
    )

    @classmethod
    def levels(
        cls,
    ) -> tuple[AtlasLoDLevel, ...]:
        return cls._LEVELS

    @classmethod
    def resolve(
        cls,
        level,
    ) -> AtlasLoDLevel:
        if (
            isinstance(level, bool)
            or not isinstance(level, int)
        ):
            raise ValueError(
                "level must be an integer in the 0..4 range"
            )

        if not 0 <= level < len(cls._LEVELS):
            raise ValueError(
                "level must be an integer in the 0..4 range"
            )

        return cls._LEVELS[level]
