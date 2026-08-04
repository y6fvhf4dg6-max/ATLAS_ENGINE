from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AtlasMosqueLandmarkProfile:
    grammar_name: str = (
        "single_dome_single_minaret"
    )

    dome_count: int = 1
    minaret_count: int = 1

    has_dome_drum: bool = True
    has_balcony: bool = True
    uses_real_footprint: bool = True

    scale_ratio: float = 5500.0
    nozzle_diameter_mm: float = 0.4

    def __post_init__(self) -> None:
        grammar_name = str(
            self.grammar_name
        ).strip().lower()

        if grammar_name != (
            "single_dome_single_minaret"
        ):
            raise ValueError(
                "grammar_name must be "
                "single_dome_single_minaret"
            )

        for field_name, value in (
            ("dome_count", self.dome_count),
            ("minaret_count", self.minaret_count),
        ):
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or value != 1
            ):
                raise ValueError(
                    f"{field_name} must be exactly 1"
                )

        scale_ratio = float(
            self.scale_ratio
        )
        nozzle_diameter_mm = float(
            self.nozzle_diameter_mm
        )

        if scale_ratio <= 0.0:
            raise ValueError(
                "scale_ratio must be positive"
            )

        if nozzle_diameter_mm <= 0.0:
            raise ValueError(
                "nozzle_diameter_mm must be positive"
            )

        object.__setattr__(
            self,
            "grammar_name",
            grammar_name,
        )
        object.__setattr__(
            self,
            "scale_ratio",
            scale_ratio,
        )
        object.__setattr__(
            self,
            "nozzle_diameter_mm",
            nozzle_diameter_mm,
        )
