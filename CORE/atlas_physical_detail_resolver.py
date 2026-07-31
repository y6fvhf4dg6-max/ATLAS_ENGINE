from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AtlasPhysicalDetailDecision:
    action: str
    scaled_size_mm: float
    minimum_printable_mm: float
    resolved_size_mm: float
    scale_factor: float


class AtlasPhysicalDetailResolver:
    OMIT_THRESHOLD_RATIO = 0.25

    @classmethod
    def resolve(
        cls,
        *,
        real_size_m: float,
        scale_ratio: float,
        nozzle_diameter_mm: float,
        detail_type: str,
    ) -> AtlasPhysicalDetailDecision:
        real_size_m = float(real_size_m)
        scale_ratio = float(scale_ratio)
        nozzle_diameter_mm = float(nozzle_diameter_mm)

        if real_size_m <= 0.0:
            raise ValueError("real_size_m must be positive")

        if scale_ratio <= 0.0:
            raise ValueError("scale_ratio must be positive")

        if nozzle_diameter_mm <= 0.0:
            raise ValueError(
                "nozzle_diameter_mm must be positive"
            )

        scaled_size_mm = (
            real_size_m * 1000.0 / scale_ratio
        )
        minimum_printable_mm = nozzle_diameter_mm

        if scaled_size_mm >= minimum_printable_mm:
            return AtlasPhysicalDetailDecision(
                action="preserve",
                scaled_size_mm=scaled_size_mm,
                minimum_printable_mm=minimum_printable_mm,
                resolved_size_mm=scaled_size_mm,
                scale_factor=1.0,
            )

        if (
            scaled_size_mm
            < minimum_printable_mm
            * cls.OMIT_THRESHOLD_RATIO
        ):
            return AtlasPhysicalDetailDecision(
                action="omit",
                scaled_size_mm=scaled_size_mm,
                minimum_printable_mm=minimum_printable_mm,
                resolved_size_mm=0.0,
                scale_factor=0.0,
            )

        return AtlasPhysicalDetailDecision(
            action="enlarge",
            scaled_size_mm=scaled_size_mm,
            minimum_printable_mm=minimum_printable_mm,
            resolved_size_mm=minimum_printable_mm,
            scale_factor=(
                minimum_printable_mm / scaled_size_mm
            ),
        )
