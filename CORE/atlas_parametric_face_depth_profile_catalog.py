from __future__ import annotations

from CORE.atlas_parametric_face_depth_profile import (
    AtlasParametricFaceDepthProfile,
)


class AtlasParametricFaceDepthProfileCatalog:
    """
    Deterministic catalog of named anatomical
    parametric face depth profiles.

    The catalog stores immutable shared profile
    instances only. It performs no measurement,
    fitting, deformation, rendering, triangulation,
    or mesh generation.
    """

    NEUTRAL_ANATOMICAL = AtlasParametricFaceDepthProfile(
        name="neutral-anatomical",
        brow_projection=0.026,
        eye_socket_depth=0.035,
        cheek_projection=0.060,
        nose_bridge_projection=0.110,
        nose_tip_projection=0.160,
        nose_wing_projection=0.045,
        upper_lip_projection=0.035,
        lower_lip_projection=0.045,
        philtrum_depth=0.018,
        labiomental_fold_depth=0.022,
        chin_projection=0.070,
    )

    _PROFILES = {
        NEUTRAL_ANATOMICAL.name: NEUTRAL_ANATOMICAL,
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
    ) -> AtlasParametricFaceDepthProfile:
        if not isinstance(
            name,
            str,
        ):
            raise TypeError(
                "name must be a string."
            )

        normalized_name = name.strip()

        if not normalized_name:
            raise ValueError(
                "name must not be blank."
            )

        try:
            return cls._PROFILES[
                normalized_name
            ]
        except KeyError as exc:
            raise KeyError(
                "unknown parametric face depth profile: "
                f"{normalized_name}"
            ) from exc
