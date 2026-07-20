from __future__ import annotations

from CORE.atlas_frontal_face_reference_profile import (
    AtlasFrontalFaceReferenceProfile,
)


class AtlasFrontalFaceReferenceProfileCatalog:
    """
    Deterministic catalog of named frontal face
    reference profiles.

    The catalog stores immutable shared profile
    instances only. It performs no measurement,
    fitting, optimization, rendering, or projection.
    """

    SYNTHETIC_NEUTRAL = AtlasFrontalFaceReferenceProfile(
        name="synthetic-neutral",
        face_width_ratio=0.7500,
        eye_spacing_ratio=0.3250,
        nose_width_ratio=0.1250,
        nose_length_ratio=0.1875,
        mouth_width_ratio=0.2250,
        jaw_width_ratio=0.5500,
        forehead_height_ratio=0.3750,
    )

    _PROFILES = {
        SYNTHETIC_NEUTRAL.name: SYNTHETIC_NEUTRAL,
    }

    @classmethod
    def names(
        cls,
    ) -> tuple[str, ...]:
        return tuple(
            sorted(
                cls._PROFILES,
            )
        )

    @classmethod
    def get(
        cls,
        name: str,
    ) -> AtlasFrontalFaceReferenceProfile:
        if not isinstance(
            name,
            str,
        ):
            raise TypeError("name must be a string.")

        normalized_name = name.strip()

        if not normalized_name:
            raise ValueError("name must not be blank.")

        try:
            return cls._PROFILES[normalized_name]
        except KeyError as exc:
            raise KeyError(
                "unknown frontal face reference profile: " f"{normalized_name}"
            ) from exc
