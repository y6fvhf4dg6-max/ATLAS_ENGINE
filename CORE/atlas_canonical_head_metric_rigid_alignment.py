from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadMetricRigidAlignmentResult:
    aligned_source_points: np.ndarray
    rotation: np.ndarray
    translation: np.ndarray
    scale_factor: float
    alignment_mode: str
    alignment_admissibility: str
    coordinate_system_state: str
    anchor_sufficiency: str
    initialization: str
    reflection_state: str
    icp_refinement_state: str
    multiple_initialization_sensitivity: str
    anchor_subset_sensitivity: str
    solver_stability: str
    transform_stability: str
    icp_free_agreement: str

    def __post_init__(self) -> None:
        aligned = np.asarray(
            self.aligned_source_points,
            dtype=np.float64,
        )
        rotation = np.asarray(
            self.rotation,
            dtype=np.float64,
        )
        translation = np.asarray(
            self.translation,
            dtype=np.float64,
        )

        if (
            aligned.ndim != 2
            or aligned.shape[1] != 3
            or aligned.shape[0] == 0
        ):
            raise ValueError(
                "aligned_source_points must have shape (N, 3)."
            )

        if rotation.shape != (3, 3):
            raise ValueError(
                "rotation must have shape (3, 3)."
            )

        if translation.shape != (3,):
            raise ValueError(
                "translation must have shape (3,)."
            )

        if not (
            np.all(np.isfinite(aligned))
            and np.all(np.isfinite(rotation))
            and np.all(np.isfinite(translation))
        ):
            raise ValueError(
                "alignment result values must be finite."
            )

        aligned = aligned.copy()
        rotation = rotation.copy()
        translation = translation.copy()

        aligned.setflags(write=False)
        rotation.setflags(write=False)
        translation.setflags(write=False)

        object.__setattr__(
            self,
            "aligned_source_points",
            aligned,
        )
        object.__setattr__(
            self,
            "rotation",
            rotation,
        )
        object.__setattr__(
            self,
            "translation",
            translation,
        )

        scale_factor = float(
            self.scale_factor
        )

        if (
            not np.isfinite(scale_factor)
            or scale_factor != 1.0
        ):
            raise ValueError(
                "scale_factor must be exactly 1.0 "
                "for rigid alignment."
            )

        object.__setattr__(
            self,
            "scale_factor",
            scale_factor,
        )

        allowed_states = {
            "alignment_mode": (
                "RIGID_SCALE_FIXED",
            ),
            "alignment_admissibility": (
                "ADMISSIBLE",
                "INADMISSIBLE",
                "UNRESOLVED",
            ),
            "coordinate_system_state": (
                "VERIFIED",
                "UNRESOLVED",
            ),
            "anchor_sufficiency": (
                "SUFFICIENT",
                "INSUFFICIENT",
                "UNRESOLVED",
            ),
            "initialization": (
                "DETERMINISTIC_CLOSED_FORM",
                "EXPLICIT_INITIALIZATION",
                "UNRESOLVED",
            ),
            "reflection_state": (
                "NOT_APPLIED",
                "APPLIED",
                "UNRESOLVED",
            ),
            "icp_refinement_state": (
                "NOT_APPLIED",
                "APPLIED",
                "UNRESOLVED",
            ),
            "multiple_initialization_sensitivity": (
                "NOT_APPLICABLE_CLOSED_FORM",
                "VERIFIED_STABLE",
                "UNSTABLE",
                "UNRESOLVED",
            ),
            "anchor_subset_sensitivity": (
                "VERIFIED_STABLE",
                "UNSTABLE",
                "UNRESOLVED",
            ),
            "solver_stability": (
                "VERIFIED_STABLE",
                "UNSTABLE",
                "UNRESOLVED",
            ),
            "transform_stability": (
                "VERIFIED_STABLE",
                "UNSTABLE",
                "UNRESOLVED",
            ),
            "icp_free_agreement": (
                "NOT_APPLICABLE_NO_ICP",
                "AGREES",
                "DISAGREES",
                "UNRESOLVED",
            ),
        }

        for field_name, allowed in allowed_states.items():
            value = getattr(self, field_name)
            if not isinstance(value, str):
                raise TypeError(
                    f"{field_name} must be a string."
                )

            normalized = value.strip().upper()
            if normalized not in allowed:
                raise ValueError(
                    f"{field_name} must be one of {allowed}."
                )

            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        if self.alignment_admissibility == "ADMISSIBLE":
            if self.coordinate_system_state != "VERIFIED":
                raise ValueError(
                    "ADMISSIBLE alignment requires VERIFIED "
                    "coordinate_system_state."
                )

            required_stable_fields = (
                "anchor_subset_sensitivity",
                "solver_stability",
                "transform_stability",
            )

            unstable_or_unresolved = tuple(
                field_name
                for field_name in required_stable_fields
                if getattr(self, field_name) != "VERIFIED_STABLE"
            )

            if unstable_or_unresolved:
                raise ValueError(
                    "ADMISSIBLE alignment requires VERIFIED_STABLE "
                    "anchor-subset, solver, and transform stability."
                )


class AtlasCanonicalHeadMetricRigidAlignment:
    @classmethod
    def solve(
        cls,
        *,
        source_points: object,
        target_points: object,
        alignment_admissibility: str = "UNRESOLVED",
        coordinate_system_state: str = "UNRESOLVED",
        anchor_subset_sensitivity: str = "UNRESOLVED",
        solver_stability: str = "UNRESOLVED",
        transform_stability: str = "UNRESOLVED",
    ) -> AtlasCanonicalHeadMetricRigidAlignmentResult:
        source = cls._normalize_points(
            source_points,
            name="source_points",
        )
        target = cls._normalize_points(
            target_points,
            name="target_points",
        )

        if source.shape != target.shape:
            raise ValueError(
                "source_points and target_points "
                "must have the same shape."
            )

        if source.shape[0] < 3:
            raise ValueError(
                "at least three point correspondences are required."
            )

        source_centroid = source.mean(
            axis=0
        )
        target_centroid = target.mean(
            axis=0
        )

        source_centered_for_rank = (
            source
            - source_centroid
        )
        target_centered_for_rank = (
            target
            - target_centroid
        )

        source_rank = np.linalg.matrix_rank(
            source_centered_for_rank
        )
        target_rank = np.linalg.matrix_rank(
            target_centered_for_rank
        )

        if source_rank < 2 or target_rank < 2:
            raise ValueError(
                "anchor geometry is insufficient for 3D rigid alignment; "
                "at least three non-collinear correspondences are required."
            )

        source_centered = (
            source
            - source_centroid
        )
        target_centered = (
            target
            - target_centroid
        )

        covariance = (
            source_centered.T
            @ target_centered
        )

        u, _, vt = np.linalg.svd(
            covariance
        )

        rotation = (
            vt.T
            @ u.T
        )

        if np.linalg.det(rotation) < 0.0:
            vt = vt.copy()
            vt[-1, :] *= -1.0
            rotation = (
                vt.T
                @ u.T
            )

        translation = (
            target_centroid
            - source_centroid @ rotation.T
        )

        aligned = (
            source @ rotation.T
            + translation
        )

        return AtlasCanonicalHeadMetricRigidAlignmentResult(
            aligned_source_points=aligned,
            rotation=rotation,
            translation=translation,
            scale_factor=1.0,
            alignment_mode="RIGID_SCALE_FIXED",
            alignment_admissibility=alignment_admissibility,
            coordinate_system_state=coordinate_system_state,
            anchor_sufficiency="SUFFICIENT",
            initialization="DETERMINISTIC_CLOSED_FORM",
            reflection_state="NOT_APPLIED",
            icp_refinement_state="NOT_APPLIED",
            multiple_initialization_sensitivity=(
                "NOT_APPLICABLE_CLOSED_FORM"
            ),
            anchor_subset_sensitivity=anchor_subset_sensitivity,
            solver_stability=solver_stability,
            transform_stability=transform_stability,
            icp_free_agreement="NOT_APPLICABLE_NO_ICP",
        )

    @staticmethod
    def _normalize_points(
        value: object,
        *,
        name: str,
    ) -> np.ndarray:
        points = np.asarray(
            value,
            dtype=np.float64,
        )

        if (
            points.ndim != 2
            or points.shape[1] != 3
            or points.shape[0] == 0
        ):
            raise ValueError(
                f"{name} must have shape (N, 3)."
            )

        if not np.all(
            np.isfinite(points)
        ):
            raise ValueError(
                f"{name} must contain only finite values."
            )

        return points.copy()


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadMetricAlignmentLandmarkIndependenceAuditResult:
    alignment_features: tuple[str, ...]
    evaluation_features: tuple[str, ...]
    feature_overlap: tuple[str, ...]
    alignment_regions: tuple[str, ...]
    evaluation_regions: tuple[str, ...]
    region_overlap: tuple[str, ...]
    alignment_bias_leakage_risk: str

    def __post_init__(self) -> None:
        for field_name in (
            "alignment_features",
            "evaluation_features",
            "feature_overlap",
            "alignment_regions",
            "evaluation_regions",
            "region_overlap",
        ):
            value = getattr(self, field_name)

            if not isinstance(value, tuple):
                raise TypeError(
                    f"{field_name} must be a tuple."
                )

            normalized = tuple(
                self._normalize_identifier(
                    item,
                    name=field_name,
                )
                for item in value
            )

            if len(normalized) != len(set(normalized)):
                raise ValueError(
                    f"{field_name} must not contain duplicates."
                )

            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        allowed_risk_states = (
            "OVERLAP_PRESENT",
            "NO_OVERLAP_IDENTIFIED",
        )

        risk = self._normalize_state(
            self.alignment_bias_leakage_risk,
            name="alignment_bias_leakage_risk",
        )

        if risk not in allowed_risk_states:
            raise ValueError(
                "alignment_bias_leakage_risk must be one of "
                f"{allowed_risk_states}."
            )

        expected_feature_overlap = tuple(
            feature
            for feature in self.evaluation_features
            if feature in set(self.alignment_features)
        )
        expected_region_overlap = tuple(
            region
            for region in self.evaluation_regions
            if region in set(self.alignment_regions)
        )

        if self.feature_overlap != expected_feature_overlap:
            raise ValueError(
                "feature_overlap must exactly match the intersection "
                "of alignment_features and evaluation_features."
            )

        if self.region_overlap != expected_region_overlap:
            raise ValueError(
                "region_overlap must exactly match the intersection "
                "of alignment_regions and evaluation_regions."
            )

        expected_risk = (
            "OVERLAP_PRESENT"
            if self.feature_overlap or self.region_overlap
            else "NO_OVERLAP_IDENTIFIED"
        )

        if risk != expected_risk:
            raise ValueError(
                "alignment_bias_leakage_risk must be derived from "
                "feature and region overlap."
            )

        object.__setattr__(
            self,
            "alignment_bias_leakage_risk",
            risk,
        )

    @staticmethod
    def _normalize_identifier(
        value: object,
        *,
        name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{name} entries must be strings."
            )

        normalized = "_".join(
            value.strip().lower().split()
        )

        if not normalized:
            raise ValueError(
                f"{name} entries must not be blank."
            )

        return normalized

    @staticmethod
    def _normalize_state(
        value: object,
        *,
        name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{name} must be a string."
            )

        normalized = "_".join(
            value.strip().upper().split()
        )

        if not normalized:
            raise ValueError(
                f"{name} must not be blank."
            )

        return normalized


class AtlasCanonicalHeadMetricAlignmentLandmarkIndependenceAudit:
    @classmethod
    def evaluate(
        cls,
        *,
        alignment_features: object,
        evaluation_features: object,
        alignment_regions: object,
        evaluation_regions: object,
    ) -> AtlasCanonicalHeadMetricAlignmentLandmarkIndependenceAuditResult:
        alignment_features = cls._normalize_identifier_collection(
            alignment_features,
            name="alignment_features",
        )
        evaluation_features = cls._normalize_identifier_collection(
            evaluation_features,
            name="evaluation_features",
        )
        alignment_regions = cls._normalize_identifier_collection(
            alignment_regions,
            name="alignment_regions",
        )
        evaluation_regions = cls._normalize_identifier_collection(
            evaluation_regions,
            name="evaluation_regions",
        )

        alignment_feature_set = set(
            alignment_features
        )
        alignment_region_set = set(
            alignment_regions
        )

        feature_overlap = tuple(
            feature
            for feature in evaluation_features
            if feature in alignment_feature_set
        )
        region_overlap = tuple(
            region
            for region in evaluation_regions
            if region in alignment_region_set
        )

        risk = (
            "OVERLAP_PRESENT"
            if feature_overlap or region_overlap
            else "NO_OVERLAP_IDENTIFIED"
        )

        return AtlasCanonicalHeadMetricAlignmentLandmarkIndependenceAuditResult(
            alignment_features=alignment_features,
            evaluation_features=evaluation_features,
            feature_overlap=feature_overlap,
            alignment_regions=alignment_regions,
            evaluation_regions=evaluation_regions,
            region_overlap=region_overlap,
            alignment_bias_leakage_risk=risk,
        )

    @staticmethod
    def _normalize_identifier_collection(
        value: object,
        *,
        name: str,
    ) -> tuple[str, ...]:
        if isinstance(value, (str, bytes)):
            raise TypeError(
                f"{name} must be an iterable of identifiers."
            )

        try:
            items = tuple(value)
        except TypeError as exc:
            raise TypeError(
                f"{name} must be an iterable of identifiers."
            ) from exc

        normalized = tuple(
            AtlasCanonicalHeadMetricAlignmentLandmarkIndependenceAuditResult
            ._normalize_identifier(
                item,
                name=name,
            )
            for item in items
        )

        if not normalized:
            raise ValueError(
                f"{name} must not be empty."
            )

        if len(normalized) != len(set(normalized)):
            raise ValueError(
                f"{name} must not contain duplicates."
            )

        return normalized
