from __future__ import annotations

from dataclasses import dataclass
import math

from CORE.atlas_urban_road_hierarchy_resolver import AtlasUrbanRoadHierarchyResolver

@dataclass(frozen=True, slots=True)
class AtlasLinearInfrastructureProfile:
    semantic_class: str
    visual_priority: float
    physical_width_mm: float
    minimum_printable_width_mm: float
    parallel_line_representation: bool
    lod_eligible: bool
    vertical_treatment: str = "surface"

    def __post_init__(self):
        semantic_class = str(self.semantic_class).strip().lower()
        if not semantic_class:
            raise ValueError("semantic_class must not be empty")

        if not math.isfinite(self.visual_priority) or not (
            0.0 <= self.visual_priority <= 1.0
        ):
            raise ValueError("visual_priority must be finite and within 0..1")

        if not math.isfinite(self.physical_width_mm) or self.physical_width_mm <= 0:
            raise ValueError("physical_width_mm must be finite and positive")

        if (
            not math.isfinite(self.minimum_printable_width_mm)
            or self.minimum_printable_width_mm <= 0
        ):
            raise ValueError(
                "minimum_printable_width_mm must be finite and positive"
            )

        if self.minimum_printable_width_mm > self.physical_width_mm:
            raise ValueError(
                "minimum_printable_width_mm must not exceed physical_width_mm"
            )

        if type(self.parallel_line_representation) is not bool:
            raise TypeError("parallel_line_representation must be bool")

        if type(self.lod_eligible) is not bool:
            raise TypeError("lod_eligible must be bool")

        vertical_treatment = "_".join(
            str(self.vertical_treatment).strip().lower().split()
        )

        if not vertical_treatment:
            raise ValueError("vertical_treatment must not be empty")

        object.__setattr__(self, "semantic_class", semantic_class)
        object.__setattr__(
            self,
            "vertical_treatment",
            vertical_treatment,
        )


class AtlasLinearInfrastructureResolver:

    @classmethod
    def resolve_geometry_kind(
        cls,
        *,
        tags,
        is_closed,
    ) -> str | None:
        if type(is_closed) is not bool:
            raise TypeError("is_closed must be bool")

        semantic_class = cls.resolve_semantic_class(
            tags
        )

        if semantic_class is None:
            return None

        if semantic_class == "infrastructure_corridor":
            if is_closed:
                return "area_strip"
            return None

        if is_closed:
            return None

        return "linear_strip"

    @classmethod
    def is_product_surface_eligible(
        cls,
        tags,
    ) -> bool:
        tags = tags or {}

        if cls.resolve_semantic_class(tags) is None:
            return False

        if (
            cls.resolve_operational_state(tags)
            != "active"
        ):
            return False

        if not cls.is_surface_visible(tags):
            return False

        return True

    @staticmethod
    def resolve_vertical_treatment(
        tags,
    ) -> str:
        tags = tags or {}

        if (
            str(
                tags.get("bridge", "")
            ).strip().lower()
            == "yes"
        ):
            return "bridge_elevated"

        tunnel = str(
            tags.get("tunnel", "")
        ).strip().lower()

        if tunnel in {
            "yes",
            "building_passage",
        }:
            return "subsurface"

        return "surface"

    @staticmethod
    def resolve_parallel_line_representation(
        *,
        gauge_mm,
        scale_ratio,
        line_width_mm,
        minimum_gap_mm,
    ) -> bool:
        gauge_mm = float(gauge_mm)
        scale_ratio = float(scale_ratio)
        line_width_mm = float(line_width_mm)
        minimum_gap_mm = float(minimum_gap_mm)

        for field_name, value in (
            ("gauge_mm", gauge_mm),
            ("scale_ratio", scale_ratio),
            ("line_width_mm", line_width_mm),
            ("minimum_gap_mm", minimum_gap_mm),
        ):
            if not math.isfinite(value):
                raise ValueError(
                    f"{field_name} must be finite"
                )

        if gauge_mm <= 0.0:
            raise ValueError(
                "gauge_mm must be greater than zero"
            )

        if scale_ratio <= 0.0:
            raise ValueError(
                "scale_ratio must be greater than zero"
            )

        if line_width_mm <= 0.0:
            raise ValueError(
                "line_width_mm must be greater than zero"
            )

        if minimum_gap_mm < 0.0:
            raise ValueError(
                "minimum_gap_mm must not be negative"
            )

        center_spacing_mm = gauge_mm / scale_ratio
        printable_gap_mm = (
            center_spacing_mm - line_width_mm
        )

        return printable_gap_mm >= minimum_gap_mm

    @staticmethod
    def resolve_physical_width_mm(
        *,
        real_width_m,
        scale_ratio,
        minimum_printable_width_mm,
    ) -> float:
        return (
            AtlasUrbanRoadHierarchyResolver.resolve_physical_width_mm(
                real_width_m=real_width_m,
                scale_ratio=scale_ratio,
                minimum_printable_width_mm=minimum_printable_width_mm,
            )
        )


    @classmethod
    def resolve_profile(
        cls,
        *,
        tags,
        scale_ratio,
        minimum_printable_width_mm,
        line_width_mm,
        minimum_gap_mm,
    ) -> AtlasLinearInfrastructureProfile | None:
        tags = tags or {}

        semantic_class = cls.resolve_semantic_class(tags)

        if semantic_class is None:
            return None

        physical_width_mm = float(
            minimum_printable_width_mm
        )

        source_width = tags.get("width")

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
            pass
        else:
            physical_width_mm = cls.resolve_physical_width_mm(
                real_width_m=real_width_m,
                scale_ratio=scale_ratio,
                minimum_printable_width_mm=(
                    minimum_printable_width_mm
                ),
            )

        parallel_line_representation = False

        if semantic_class in {
            "railway",
            "light_rail",
            "tram",
        }:
            gauge = tags.get("gauge")

            try:
                gauge_mm = float(gauge)
            except (
                TypeError,
                ValueError,
            ):
                gauge_mm = None

            if (
                gauge_mm is not None
                and math.isfinite(gauge_mm)
                and gauge_mm > 0.0
            ):
                parallel_line_representation = (
                    cls.resolve_parallel_line_representation(
                        gauge_mm=gauge_mm,
                        scale_ratio=scale_ratio,
                        line_width_mm=line_width_mm,
                        minimum_gap_mm=minimum_gap_mm,
                    )
                )

        priorities = {
            "railway": 0.90,
            "light_rail": 0.85,
            "tram": 0.80,
            "infrastructure_corridor": 0.75,
            "embankment": 0.60,
            "cycle_corridor": 0.50,
            "bridleway_corridor": 0.40,
            "pedestrian_path": 0.30,
        }

        visual_priority = priorities.get(
            semantic_class
        )

        if visual_priority is None:
            return None

        return AtlasLinearInfrastructureProfile(
            semantic_class=semantic_class,
            visual_priority=visual_priority,
            physical_width_mm=physical_width_mm,
            minimum_printable_width_mm=(
                minimum_printable_width_mm
            ),
            parallel_line_representation=(
                parallel_line_representation
            ),
            lod_eligible=True,
            vertical_treatment=(
                cls.resolve_vertical_treatment(tags)
            ),
        )

    @staticmethod
    def resolve_semantic_class(
        tags,
    ) -> str | None:
        tags = tags or {}

        railway = str(
            tags.get("railway", "")
        ).strip().lower()

        if railway == "proposed":
            railway = str(
                tags.get("proposed", "")
            ).strip().lower()

        elif railway == "disused":
            railway = str(
                tags.get("disused:railway", "")
            ).strip().lower()

        if railway == "rail":
            return "railway"

        if railway == "light_rail":
            return "light_rail"

        if railway == "tram":
            return "tram"

        highway = str(
            tags.get("highway", "")
        ).strip().lower()

        if highway == "cycleway":
            return "cycle_corridor"

        if highway == "bridleway":
            return "bridleway_corridor"

        if highway in {
            "footway",
            "path",
            "pedestrian",
            "steps",
        }:
            return "pedestrian_path"

        if (
            str(
                tags.get("man_made", "")
            ).strip().lower()
            == "embankment"
        ):
            return "embankment"

        if (
            str(
                tags.get("landuse", "")
            ).strip().lower()
            == "railway"
        ):
            return "infrastructure_corridor"

        return None

    @staticmethod
    def resolve_operational_state(
        tags,
    ) -> str:
        tags = tags or {}

        railway = str(
            tags.get("railway", "")
        ).strip().lower()

        if (
            railway == "proposed"
            or str(
                tags.get("proposed", "")
            ).strip().lower()
            == "yes"
        ):
            return "proposed"

        if (
            railway == "disused"
            or str(
                tags.get("disused", "")
            ).strip().lower()
            == "yes"
        ):
            return "disused"

        return "active"

    @staticmethod
    def is_surface_visible(
        tags,
    ) -> bool:
        tags = tags or {}

        tunnel = str(
            tags.get("tunnel", "")
        ).strip().lower()

        return tunnel not in {
            "yes",
            "building_passage",
        }
