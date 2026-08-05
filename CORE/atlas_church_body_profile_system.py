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


def _validate_ratio(
    value,
    *,
    field_name: str,
) -> float:
    ratio = float(value)

    if ratio <= 0.0 or ratio > 1.0:
        raise ValueError(
            f"{field_name} must be greater than zero "
            "and at most one"
        )

    return ratio


@dataclass(frozen=True, slots=True)
class AtlasChurchBodyProfile:
    plan_type: str

    nave_width_ratio: float
    nave_depth_ratio: float
    outer_aisle_height_ratio: float

    transept_depth_ratio: float
    transept_width_ratio: float
    transept_height_ratio: float

    apse_depth_ratio: float
    apse_width_ratio: float
    apse_height_ratio: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "plan_type",
            _normalize_identifier(
                self.plan_type,
                field_name="plan_type",
            ),
        )

        for field_name in (
            "nave_width_ratio",
            "nave_depth_ratio",
            "outer_aisle_height_ratio",
            "transept_depth_ratio",
            "transept_width_ratio",
            "transept_height_ratio",
            "apse_depth_ratio",
            "apse_width_ratio",
            "apse_height_ratio",
        ):
            object.__setattr__(
                self,
                field_name,
                _validate_ratio(
                    getattr(
                        self,
                        field_name,
                    ),
                    field_name=field_name,
                ),
            )


class AtlasChurchBodyProfileSystem:
    _PROFILES = {
        "cross_plan": AtlasChurchBodyProfile(
            plan_type="cross_plan",
            nave_width_ratio=0.52,
            nave_depth_ratio=0.78,
            outer_aisle_height_ratio=0.72,
            transept_depth_ratio=0.22,
            transept_width_ratio=0.84,
            transept_height_ratio=0.92,
            apse_depth_ratio=0.14,
            apse_width_ratio=0.78,
            apse_height_ratio=0.82,
        ),
        "basilica_cross_plan": AtlasChurchBodyProfile(
            plan_type="basilica_cross_plan",
            nave_width_ratio=0.46,
            nave_depth_ratio=0.82,
            outer_aisle_height_ratio=0.68,
            transept_depth_ratio=0.24,
            transept_width_ratio=0.88,
            transept_height_ratio=0.92,
            apse_depth_ratio=0.16,
            apse_width_ratio=0.74,
            apse_height_ratio=0.82,
        ),
    }

    @classmethod
    def resolve(
        cls,
        plan_type,
    ) -> AtlasChurchBodyProfile:
        normalized_plan_type = _normalize_identifier(
            plan_type,
            field_name="plan_type",
        )

        profile = cls._PROFILES.get(
            normalized_plan_type
        )

        if profile is None:
            raise ValueError(
                "unsupported church plan_type: "
                f"{normalized_plan_type}"
            )

        return profile
