from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AtlasUrbanRoadProfile:
    semantic_class: str
    semantic_priority: float
    physical_width_mm: float
    minimum_printable_width_mm: float
    vertical_treatment: str
    lod_eligible: bool
    simplification_priority: float

    def __post_init__(self) -> None:
        semantic_class = "_".join(
            str(self.semantic_class).strip().lower().split()
        )
        vertical_treatment = "_".join(
            str(self.vertical_treatment).strip().lower().split()
        )

        if not semantic_class:
            raise ValueError(
                "semantic_class must not be blank"
            )

        if not vertical_treatment:
            raise ValueError(
                "vertical_treatment must not be blank"
            )

        semantic_priority = float(
            self.semantic_priority
        )
        simplification_priority = float(
            self.simplification_priority
        )
        physical_width_mm = float(
            self.physical_width_mm
        )
        minimum_printable_width_mm = float(
            self.minimum_printable_width_mm
        )

        for field_name, value in (
            ("semantic_priority", semantic_priority),
            (
                "simplification_priority",
                simplification_priority,
            ),
        ):
            if not math.isfinite(value):
                raise ValueError(
                    f"{field_name} must be finite"
                )
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{field_name} must be in the 0.0..1.0 range"
                )

        for field_name, value in (
            ("physical_width_mm", physical_width_mm),
            (
                "minimum_printable_width_mm",
                minimum_printable_width_mm,
            ),
        ):
            if not math.isfinite(value):
                raise ValueError(
                    f"{field_name} must be finite"
                )
            if value <= 0.0:
                raise ValueError(
                    f"{field_name} must be greater than zero"
                )

        if minimum_printable_width_mm > physical_width_mm:
            raise ValueError(
                "minimum_printable_width_mm must not exceed "
                "physical_width_mm"
            )

        if not isinstance(self.lod_eligible, bool):
            raise TypeError(
                "lod_eligible must be a bool"
            )

        object.__setattr__(
            self,
            "semantic_class",
            semantic_class,
        )
        object.__setattr__(
            self,
            "semantic_priority",
            semantic_priority,
        )
        object.__setattr__(
            self,
            "physical_width_mm",
            physical_width_mm,
        )
        object.__setattr__(
            self,
            "minimum_printable_width_mm",
            minimum_printable_width_mm,
        )
        object.__setattr__(
            self,
            "vertical_treatment",
            vertical_treatment,
        )
        object.__setattr__(
            self,
            "simplification_priority",
            simplification_priority,
        )


class AtlasUrbanRoadHierarchyResolver:
    DEFAULT_WIDTHS_M = {
        "motorway": 12.0,
        "trunk": 10.0,
        "primary": 8.0,
        "secondary": 7.0,
        "tertiary": 6.0,
        "residential": 5.0,
        "service": 4.0,
        "living_street": 4.0,
        "unclassified": 5.0,
        "road": 5.0,
    }

    HIGHWAY_TO_SEMANTIC_CLASS = {
        "motorway": "major_road",
        "trunk": "major_road",
        "primary": "major_road",
        "secondary": "major_road",
        "tertiary": "major_road",
        "residential": "local_road",
        "living_street": "local_road",
        "unclassified": "local_road",
        "road": "local_road",
        "service": "service_road",
        "footway": "pedestrian_path",
        "path": "pedestrian_path",
        "pedestrian": "pedestrian_path",
        "steps": "pedestrian_path",
        "cycleway": "cycleway",
        "bridleway": "bridleway",
    }

    @staticmethod
    def validate_relative_hierarchy(
        profiles,
    ) -> None:
        profiles = tuple(profiles)

        for profile in profiles:
            if not isinstance(
                profile,
                AtlasUrbanRoadProfile,
            ):
                raise TypeError(
                    "profiles must contain "
                    "AtlasUrbanRoadProfile values"
                )

        order = {
            "major_road": 4,
            "local_road": 3,
            "service_road": 2,
            "pedestrian_path": 1,
        }

        ranked = [
            profile
            for profile in profiles
            if profile.semantic_class in order
        ]

        ranked.sort(
            key=lambda profile: order[
                profile.semantic_class
            ],
            reverse=True,
        )

        for more_important, less_important in zip(
            ranked,
            ranked[1:],
        ):
            if (
                more_important.semantic_priority
                <= less_important.semantic_priority
            ):
                raise ValueError(
                    "semantic_priority must preserve "
                    "road hierarchy"
                )

            if (
                more_important.physical_width_mm
                <= less_important.physical_width_mm
            ):
                raise ValueError(
                    "physical_width_mm must preserve "
                    "road hierarchy"
                )

            if (
                more_important.simplification_priority
                <= less_important.simplification_priority
            ):
                raise ValueError(
                    "simplification_priority must preserve "
                    "road hierarchy"
                )

    @classmethod
    def resolve_profile(
        cls,
        *,
        highway,
        source_width,
        scale_ratio,
        minimum_printable_width_mm,
    ) -> AtlasUrbanRoadProfile | None:
        semantic_class = cls.resolve_highway(
            highway
        )

        if semantic_class is None:
            return None

        default_width_m = cls.default_width_m(
            highway
        )

        if semantic_class == "pedestrian_path":
            try:
                candidate = source_width

                if isinstance(candidate, str):
                    candidate = (
                        candidate
                        .replace("m", "")
                        .strip()
                    )

                real_width_m = float(candidate)

                if (
                    not math.isfinite(real_width_m)
                    or real_width_m <= 0.0
                ):
                    raise ValueError
            except (
                TypeError,
                ValueError,
            ):
                physical_width_mm = float(
                    minimum_printable_width_mm
                )
            else:
                physical_width_mm = cls.resolve_physical_width_mm(
                    real_width_m=real_width_m,
                    scale_ratio=scale_ratio,
                    minimum_printable_width_mm=(
                        minimum_printable_width_mm
                    ),
                )
        else:
            if default_width_m is None:
                return None

            real_width_m = cls.resolve_source_width_m(
                source_width=source_width,
                default_width_m=default_width_m,
            )

            physical_width_mm = cls.resolve_physical_width_mm(
                real_width_m=real_width_m,
                scale_ratio=scale_ratio,
                minimum_printable_width_mm=(
                    minimum_printable_width_mm
                ),
            )

        priorities = {
            "major_road": 0.90,
            "local_road": 0.70,
            "service_road": 0.50,
            "pedestrian_path": 0.30,
        }

        priority = priorities.get(
            semantic_class
        )

        if priority is None:
            return None

        return AtlasUrbanRoadProfile(
            semantic_class=semantic_class,
            semantic_priority=priority,
            physical_width_mm=physical_width_mm,
            minimum_printable_width_mm=(
                minimum_printable_width_mm
            ),
            vertical_treatment="foundation_raised",
            lod_eligible=True,
            simplification_priority=priority,
        )

    @classmethod
    def default_width_m(
        cls,
        highway,
    ) -> float | None:
        if highway is None:
            return None

        normalized = str(highway).strip().lower()

        if not normalized:
            return None

        return cls.DEFAULT_WIDTHS_M.get(
            normalized
        )

    @staticmethod
    def resolve_source_width_m(
        *,
        source_width,
        default_width_m,
    ) -> float:
        default_width_m = float(
            default_width_m
        )

        if (
            not math.isfinite(default_width_m)
            or default_width_m <= 0.0
        ):
            raise ValueError(
                "default_width_m must be finite and "
                "greater than zero"
            )

        try:
            candidate = source_width

            if isinstance(candidate, str):
                candidate = (
                    candidate
                    .replace("m", "")
                    .strip()
                )

            candidate = float(candidate)
        except (
            TypeError,
            ValueError,
        ):
            return default_width_m

        if (
            not math.isfinite(candidate)
            or candidate <= 0.0
        ):
            return default_width_m

        return candidate

    @staticmethod
    def resolve_physical_width_mm(
        *,
        real_width_m,
        scale_ratio,
        minimum_printable_width_mm,
    ) -> float:
        real_width_m = float(real_width_m)
        scale_ratio = float(scale_ratio)
        minimum_printable_width_mm = float(
            minimum_printable_width_mm
        )

        for field_name, value in (
            ("real_width_m", real_width_m),
            ("scale_ratio", scale_ratio),
            (
                "minimum_printable_width_mm",
                minimum_printable_width_mm,
            ),
        ):
            if not math.isfinite(value):
                raise ValueError(
                    f"{field_name} must be finite"
                )

            if value <= 0.0:
                raise ValueError(
                    f"{field_name} must be greater than zero"
                )

        scaled_width_mm = (
            real_width_m
            * 1000.0
            / scale_ratio
        )

        return max(
            scaled_width_mm,
            minimum_printable_width_mm,
        )

    @staticmethod
    def resolve_highway(
        highway,
    ) -> str | None:
        if highway is None:
            return None

        normalized = str(highway).strip().lower()

        if not normalized:
            return None

        return (
            AtlasUrbanRoadHierarchyResolver
            .HIGHWAY_TO_SEMANTIC_CLASS
            .get(normalized)
        )
