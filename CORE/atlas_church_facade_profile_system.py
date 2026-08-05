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
class AtlasChurchFacadeProfile:
    facade_rhythm: str
    bay_spacing_ratio: float
    opening_width_ratio: float
    opening_height_ratio: float
    arch_shape: str
    recess_depth_ratio: float
    front_composition: str
    rear_composition: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "facade_rhythm",
            _normalize_identifier(
                self.facade_rhythm,
                field_name="facade_rhythm",
            ),
        )
        object.__setattr__(
            self,
            "arch_shape",
            _normalize_identifier(
                self.arch_shape,
                field_name="arch_shape",
            ),
        )
        object.__setattr__(
            self,
            "front_composition",
            _normalize_identifier(
                self.front_composition,
                field_name="front_composition",
            ),
        )
        object.__setattr__(
            self,
            "rear_composition",
            _normalize_identifier(
                self.rear_composition,
                field_name="rear_composition",
            ),
        )

        for field_name in (
            "bay_spacing_ratio",
            "opening_width_ratio",
            "opening_height_ratio",
            "recess_depth_ratio",
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


class AtlasChurchFacadeProfileSystem:
    _PROFILES = {
        "regular": AtlasChurchFacadeProfile(
            facade_rhythm="regular",
            bay_spacing_ratio=0.18,
            opening_width_ratio=0.28,
            opening_height_ratio=0.34,
            arch_shape="simple_arch",
            recess_depth_ratio=0.04,
            front_composition="single_arch_portal",
            rear_composition="single_arch_opening",
        ),
        "heavy_round_arch": AtlasChurchFacadeProfile(
            facade_rhythm="heavy_round_arch",
            bay_spacing_ratio=0.22,
            opening_width_ratio=0.24,
            opening_height_ratio=0.30,
            arch_shape="round_arch",
            recess_depth_ratio=0.06,
            front_composition="portal_with_oculus",
            rear_composition="round_arch_opening",
        ),
    }

    @classmethod
    def resolve(
        cls,
        facade_rhythm,
    ) -> AtlasChurchFacadeProfile:
        normalized_facade_rhythm = _normalize_identifier(
            facade_rhythm,
            field_name="facade_rhythm",
        )

        profile = cls._PROFILES.get(
            normalized_facade_rhythm
        )

        if profile is None:
            raise ValueError(
                "unsupported church facade_rhythm: "
                f"{normalized_facade_rhythm}"
            )

        return profile
