from __future__ import annotations

from collections.abc import Mapping

import numpy as np


_REQUIRED_REGION_NAMES = (
    "eye_glasses",
    "nose_bridge",
    "nose_body",
    "nose_base",
    "philtrum",
    "upper_lip",
    "lower_lip",
    "left_cheek",
    "right_cheek",
    "chin",
    "face_interior",
    "face_boundary_falloff",
)


class AtlasReliefFaceStructureConfidenceMap:
    """
    Build a landmark-controlled confidence map for structure normals.

    The map keeps broad identity-bearing facial structure while reducing
    structure leakage caused by glasses, nostrils, lip lines, philtrum and
    face boundaries.

    This module does not reconstruct normals or height. It only produces
    a soft float64 confidence map in the closed range 0..1.
    """

    @staticmethod
    def build(
        subject_mask: np.ndarray,
        *,
        landmark_regions: Mapping[str, np.ndarray],
        glasses_confidence: float = 0.35,
        glasses_core_confidence: float = 0.12,
        nose_base_confidence: float = 0.40,
        philtrum_confidence: float = 0.30,
        upper_lip_confidence: float = 0.38,
        lower_lip_confidence: float = 0.45,
        boundary_confidence: float = 0.20,
        outside_face_confidence: float = 0.02,
    ) -> np.ndarray:
        subject = np.asarray(
            subject_mask,
            dtype=np.float64,
        )

        AtlasReliefFaceStructureConfidenceMap._validate_subject_mask(
            subject
        )

        regions = (
            AtlasReliefFaceStructureConfidenceMap
            ._validate_landmark_regions(
                landmark_regions,
                shape=subject.shape,
            )
        )

        glasses_value = (
            AtlasReliefFaceStructureConfidenceMap
            ._validate_unit_value(
                glasses_confidence,
                name="glasses_confidence",
            )
        )
        glasses_core_value = (
            AtlasReliefFaceStructureConfidenceMap
            ._validate_unit_value(
                glasses_core_confidence,
                name="glasses_core_confidence",
            )
        )
        nose_base_value = (
            AtlasReliefFaceStructureConfidenceMap
            ._validate_unit_value(
                nose_base_confidence,
                name="nose_base_confidence",
            )
        )
        philtrum_value = (
            AtlasReliefFaceStructureConfidenceMap
            ._validate_unit_value(
                philtrum_confidence,
                name="philtrum_confidence",
            )
        )
        upper_lip_value = (
            AtlasReliefFaceStructureConfidenceMap
            ._validate_unit_value(
                upper_lip_confidence,
                name="upper_lip_confidence",
            )
        )
        lower_lip_value = (
            AtlasReliefFaceStructureConfidenceMap
            ._validate_unit_value(
                lower_lip_confidence,
                name="lower_lip_confidence",
            )
        )
        boundary_value = (
            AtlasReliefFaceStructureConfidenceMap
            ._validate_unit_value(
                boundary_confidence,
                name="boundary_confidence",
            )
        )
        outside_face_value = (
            AtlasReliefFaceStructureConfidenceMap
            ._validate_unit_value(
                outside_face_confidence,
                name="outside_face_confidence",
            )
        )

        clipped_subject = np.clip(
            subject,
            0.0,
            1.0,
        )

        # Structure confidence starts fully active everywhere inside
        # the subject. Face-interior and face-boundary masks are not used
        # here because their transitions create a second contour inside
        # the physical head silhouette.
        confidence = np.ones(
            subject.shape,
            dtype=np.float64,
        )

        glasses_region = regions["eye_glasses"]

        confidence = (
            AtlasReliefFaceStructureConfidenceMap
            ._apply_regional_floor(
                confidence,
                glasses_region,
                target_confidence=glasses_value,
            )
        )

        # A cubic response isolates the strongest center of the soft
        # glasses mask without expanding its spatial support. The broad
        # mask keeps a gradual transition, while the core receives
        # stronger suppression.
        glasses_core = np.power(
            glasses_region,
            3.0,
        )

        confidence = (
            AtlasReliefFaceStructureConfidenceMap
            ._apply_regional_floor(
                confidence,
                glasses_core,
                target_confidence=glasses_core_value,
            )
        )

        confidence = (
            AtlasReliefFaceStructureConfidenceMap
            ._apply_regional_floor(
                confidence,
                regions["nose_base"],
                target_confidence=nose_base_value,
            )
        )

        confidence = (
            AtlasReliefFaceStructureConfidenceMap
            ._apply_regional_floor(
                confidence,
                regions["philtrum"],
                target_confidence=philtrum_value,
            )
        )

        confidence = (
            AtlasReliefFaceStructureConfidenceMap
            ._apply_regional_floor(
                confidence,
                regions["upper_lip"],
                target_confidence=upper_lip_value,
            )
        )

        confidence = (
            AtlasReliefFaceStructureConfidenceMap
            ._apply_regional_floor(
                confidence,
                regions["lower_lip"],
                target_confidence=lower_lip_value,
            )
        )

        confidence *= clipped_subject

        return np.ascontiguousarray(
            np.clip(
                confidence,
                0.0,
                1.0,
            ),
            dtype=np.float64,
        )

    @staticmethod
    def _apply_regional_floor(
        confidence: np.ndarray,
        region: np.ndarray,
        *,
        target_confidence: float,
    ) -> np.ndarray:
        """
        Blend confidence toward a lower regional target.

        Despite the helper name, this operation never raises confidence.
        The target is interpreted as the confidence retained at region=1.
        """

        target = (
            confidence
            * (
                1.0 - region
            )
            + target_confidence
            * region
        )

        return np.minimum(
            confidence,
            target,
        )

    @staticmethod
    def _validate_subject_mask(
        subject_mask: np.ndarray,
    ) -> None:
        if subject_mask.ndim != 2:
            raise ValueError(
                "subject_mask must be a two-dimensional array"
            )

        if not np.all(
            np.isfinite(subject_mask)
        ):
            raise ValueError(
                "subject_mask must contain only finite values"
            )

        if not np.any(
            subject_mask > 0.0
        ):
            raise ValueError(
                "subject_mask must contain at least one active pixel"
            )

    @staticmethod
    def _validate_landmark_regions(
        landmark_regions: Mapping[str, np.ndarray],
        *,
        shape: tuple[int, int],
    ) -> dict[str, np.ndarray]:
        if not isinstance(
            landmark_regions,
            Mapping,
        ):
            raise TypeError(
                "landmark_regions must be a mapping"
            )

        validated: dict[str, np.ndarray] = {}

        for name in _REQUIRED_REGION_NAMES:
            if name not in landmark_regions:
                raise ValueError(
                    "landmark_regions is missing required "
                    f"region: {name}"
                )

            region = np.asarray(
                landmark_regions[name],
                dtype=np.float64,
            )

            if region.shape != shape:
                raise ValueError(
                    f"landmark region {name!r} "
                    f"must have shape {shape}"
                )

            if not np.all(
                np.isfinite(region)
            ):
                raise ValueError(
                    f"landmark region {name!r} "
                    "must contain only finite values"
                )

            if (
                np.any(region < 0.0)
                or np.any(region > 1.0)
            ):
                raise ValueError(
                    f"landmark region {name!r} "
                    "must contain values between 0 and 1"
                )

            validated[name] = np.ascontiguousarray(
                region,
                dtype=np.float64,
            )

        return validated

    @staticmethod
    def _validate_unit_value(
        value: float,
        *,
        name: str,
    ) -> float:
        numeric = float(value)

        if (
            not np.isfinite(numeric)
            or numeric < 0.0
            or numeric > 1.0
        ):
            raise ValueError(
                f"{name} must be finite and between 0 and 1"
            )

        return numeric
