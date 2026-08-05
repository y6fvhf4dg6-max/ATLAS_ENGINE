from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AtlasChurchLandmarkProfile:
    landmark_class: str = "church"
    grammar_name: str = "auto"
    profile_name: str = "generic_church"

    has_nave: bool = True
    has_transept: bool = True
    has_apse: bool = True

    tower_count: int = 1
    has_spires: bool = True
    has_buttresses: bool = True
    has_window_bays: bool = True

    roof_sections: tuple[str, ...] = (
        "nave",
        "transept",
        "apse",
        "tower",
    )

    scale_ratio: float = 5500.0
    nozzle_diameter_mm: float = 0.4

    def __post_init__(self) -> None:
        landmark_class = str(
            self.landmark_class
        ).strip().lower()
        grammar_name = str(
            self.grammar_name
        ).strip().lower()
        profile_name = "_".join(
            str(
                self.profile_name
            ).strip().lower().split()
        )

        if not grammar_name:
            raise ValueError(
                "grammar_name must not be blank"
            )

        if not profile_name:
            raise ValueError(
                "profile_name must not be blank"
            )

        if landmark_class not in {
            "church",
            "cathedral",
        }:
            raise ValueError(
                "landmark_class must be church or cathedral"
            )

        tower_count = self.tower_count

        if (
            isinstance(tower_count, bool)
            or not isinstance(tower_count, int)
            or tower_count < 0
            or tower_count > 2
        ):
            raise ValueError(
                "tower_count must be an integer from 0 to 2"
            )

        scale_ratio = float(self.scale_ratio)
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

        roof_sections = tuple(
            str(section).strip()
            for section in self.roof_sections
        )

        if not roof_sections:
            raise ValueError(
                "roof_sections must not be empty"
            )

        object.__setattr__(
            self,
            "landmark_class",
            landmark_class,
        )
        object.__setattr__(
            self,
            "grammar_name",
            grammar_name,
        )
        object.__setattr__(
            self,
            "profile_name",
            profile_name,
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
        object.__setattr__(
            self,
            "roof_sections",
            roof_sections,
        )
