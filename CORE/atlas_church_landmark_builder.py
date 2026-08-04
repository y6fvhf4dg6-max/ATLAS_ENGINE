from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_church_landmark_profile import (
    AtlasChurchLandmarkProfile,
)
from CORE.atlas_church_footprint_resolver import (
    AtlasChurchFootprintResolver,
)
from CORE.atlas_church_tower_profile_system import (
    AtlasChurchTowerProfileCollection,
    AtlasChurchTowerProfileSystem,
)
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_physical_detail_resolver import (
    AtlasPhysicalDetailResolver,
)


@dataclass(frozen=True, slots=True)
class AtlasChurchLandmarkComponent:
    component_type: str
    index: int = 0
    section_name: str | None = None
    physical_action: str | None = None
    resolved_size_mm: float | None = None


@dataclass(frozen=True, slots=True)
class AtlasChurchLandmarkGeometry:
    landmark_id: int
    landmark_class: str
    footprint: tuple
    height_m: float
    components: tuple[AtlasChurchLandmarkComponent, ...]
    profile: AtlasChurchLandmarkProfile
    tower_profile: AtlasChurchTowerProfileCollection


class AtlasChurchLandmarkBuilder:
    DEFAULT_CHURCH_HEIGHT_M = 24.0
    DEFAULT_CATHEDRAL_HEIGHT_M = 42.0

    @staticmethod
    def _try_positive_float(value):
        try:
            result = float(value)
        except (TypeError, ValueError):
            return None

        if result <= 0.0:
            return None

        return result

    @staticmethod
    def _normalize_footprint(geometry):
        exterior = getattr(
            geometry,
            "exterior",
            geometry,
        )
        coordinates = getattr(
            exterior,
            "coords",
            exterior,
        )

        footprint = tuple(
            (
                float(point[0]),
                float(point[1]),
            )
            for point in coordinates
        )

        if (
            len(footprint) > 1
            and footprint[0] == footprint[-1]
        ):
            footprint = footprint[:-1]

        if len(footprint) < 3:
            raise ValueError(
                "Church landmark requires at least three footprint points"
            )

        return footprint

    @classmethod
    def _resolve_height(
        cls,
        *,
        landmark,
        profile,
    ):
        tags = getattr(
            landmark,
            "tags",
            {},
        ) or {}

        height_m = cls._try_positive_float(
            tags.get("height")
        )

        if height_m is not None:
            return height_m

        if profile.landmark_class == "cathedral":
            return cls.DEFAULT_CATHEDRAL_HEIGHT_M

        return cls.DEFAULT_CHURCH_HEIGHT_M

    @staticmethod
    def _build_components(
        profile,
        tower_profile,
    ):
        components = []

        window_decision = (
            AtlasPhysicalDetailResolver.resolve(
                real_size_m=1.80,
                scale_ratio=profile.scale_ratio,
                nozzle_diameter_mm=(
                    profile.nozzle_diameter_mm
                ),
                detail_type="window",
            )
        )

        buttress_decision = (
            AtlasPhysicalDetailResolver.resolve(
                real_size_m=1.20,
                scale_ratio=profile.scale_ratio,
                nozzle_diameter_mm=(
                    profile.nozzle_diameter_mm
                ),
                detail_type="buttress",
            )
        )

        if profile.has_nave:
            components.append(
                AtlasChurchLandmarkComponent(
                    component_type="nave",
                )
            )

        if profile.has_transept:
            components.append(
                AtlasChurchLandmarkComponent(
                    component_type="transept",
                )
            )

        if profile.has_apse:
            components.append(
                AtlasChurchLandmarkComponent(
                    component_type="apse",
                )
            )

        for index, tower in enumerate(
            tower_profile.towers
        ):
            components.append(
                AtlasChurchLandmarkComponent(
                    component_type="tower",
                    index=index,
                    section_name=tower.tower_type,
                )
            )

        if profile.has_buttresses:
            components.append(
                AtlasChurchLandmarkComponent(
                    component_type="buttress_system",
                    physical_action=(
                        buttress_decision.action
                    ),
                    resolved_size_mm=(
                        buttress_decision
                        .resolved_size_mm
                    ),
                )
            )

        if profile.has_window_bays:
            components.append(
                AtlasChurchLandmarkComponent(
                    component_type="window_bay_system",
                    physical_action=(
                        window_decision.action
                    ),
                    resolved_size_mm=(
                        window_decision
                        .resolved_size_mm
                    ),
                )
            )

        for index, section_name in enumerate(
            profile.roof_sections
        ):
            components.append(
                AtlasChurchLandmarkComponent(
                    component_type="roof_section",
                    index=index,
                    section_name=section_name,
                )
            )

        return tuple(components)

    @classmethod
    def build(
        cls,
        *,
        landmark,
        profile,
    ) -> AtlasChurchLandmarkGeometry:
        if not isinstance(
            profile,
            AtlasChurchLandmarkProfile,
        ):
            raise TypeError(
                "profile must be AtlasChurchLandmarkProfile"
            )

        if landmark.landmark_type not in {
            AtlasLandmarkType.CHURCH,
            AtlasLandmarkType.CATHEDRAL,
        }:
            raise ValueError(
                "landmark must be church or cathedral"
            )

        expected_class = (
            "cathedral"
            if landmark.landmark_type
            is AtlasLandmarkType.CATHEDRAL
            else "church"
        )

        if profile.landmark_class != expected_class:
            raise ValueError(
                "profile landmark_class does not match landmark type"
            )

        footprint = cls._normalize_footprint(
            landmark.geometry
        )

        height_m = cls._resolve_height(
            landmark=landmark,
            profile=profile,
        )

        frame = AtlasChurchFootprintResolver.resolve(
            footprint
        )

        tower_profile = (
            AtlasChurchTowerProfileSystem.resolve(
                longitudinal_span=frame.longitudinal_span,
                lateral_span=frame.lateral_span,
                building_height=height_m,
                landmark_class=profile.landmark_class,
                grammar_name=profile.grammar_name,
            )
        )

        return AtlasChurchLandmarkGeometry(
            landmark_id=int(landmark.id),
            landmark_class=profile.landmark_class,
            footprint=footprint,
            height_m=height_m,
            components=cls._build_components(
                profile,
                tower_profile,
            ),
            profile=profile,
            tower_profile=tower_profile,
        )
