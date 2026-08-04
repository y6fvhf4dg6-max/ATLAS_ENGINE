from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_mosque_landmark_profile import (
    AtlasMosqueLandmarkProfile,
)
from CORE.atlas_worship_landmark_fallback_mesher import (
    AtlasWorshipLandmarkFallbackMesher,
)


@dataclass(frozen=True, slots=True)
class AtlasMosqueLandmarkComponent:
    component_type: str
    index: int = 0


@dataclass(frozen=True, slots=True)
class AtlasMosqueLandmarkGeometry:
    landmark_id: int
    grammar_name: str
    footprint: tuple
    height_m: float
    components: tuple[AtlasMosqueLandmarkComponent, ...]
    profile: AtlasMosqueLandmarkProfile


class AtlasMosqueLandmarkBuilder:
    DEFAULT_MOSQUE_HEIGHT_M = 18.0

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
                "Mosque landmark requires at least "
                "three footprint points"
            )

        return footprint

    @classmethod
    def _resolve_height(cls, landmark):
        tags = getattr(
            landmark,
            "tags",
            {},
        ) or {}

        height_m = (
            AtlasWorshipLandmarkFallbackMesher
            ._read_positive_metres(
                tags.get("height")
            )
        )

        if height_m is None:
            return cls.DEFAULT_MOSQUE_HEIGHT_M

        return float(height_m)

    @staticmethod
    def _build_components(profile):
        components = [
            AtlasMosqueLandmarkComponent(
                component_type="prayer_hall",
            ),
        ]

        if profile.has_dome_drum:
            components.append(
                AtlasMosqueLandmarkComponent(
                    component_type="dome_drum",
                )
            )

        for index in range(profile.dome_count):
            components.append(
                AtlasMosqueLandmarkComponent(
                    component_type="main_dome",
                    index=index,
                )
            )

        for index in range(profile.minaret_count):
            components.append(
                AtlasMosqueLandmarkComponent(
                    component_type="minaret_body",
                    index=index,
                )
            )

            if profile.has_balcony:
                components.append(
                    AtlasMosqueLandmarkComponent(
                        component_type=(
                            "minaret_balcony"
                        ),
                        index=index,
                    )
                )

            components.append(
                AtlasMosqueLandmarkComponent(
                    component_type="minaret_cap",
                    index=index,
                )
            )

        return tuple(components)

    @classmethod
    def build(
        cls,
        *,
        landmark,
        profile,
    ) -> AtlasMosqueLandmarkGeometry:
        if not isinstance(
            profile,
            AtlasMosqueLandmarkProfile,
        ):
            raise TypeError(
                "profile must be "
                "AtlasMosqueLandmarkProfile"
            )

        if (
            landmark.landmark_type
            is not AtlasLandmarkType.MOSQUE
        ):
            raise ValueError(
                "landmark must be mosque"
            )

        footprint = cls._normalize_footprint(
            landmark.geometry
        )

        return AtlasMosqueLandmarkGeometry(
            landmark_id=int(landmark.id),
            grammar_name=profile.grammar_name,
            footprint=footprint,
            height_m=cls._resolve_height(
                landmark
            ),
            components=cls._build_components(
                profile
            ),
            profile=profile,
        )
