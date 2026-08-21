from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadBenchmarkCandidateObservation:
    candidate_id: str
    architecture_kind: str

    identity_preservation_support: float
    multi_view_consistency: float
    silhouette_profile_support: float
    head_ratio_support: float
    jaw_chin_support: float
    nose_projection_support: float
    orbital_cheek_volume_support: float
    expression_separation_support: float
    pose_separation_support: float
    topology_suitability: float
    physical_suitability: float
    apple_silicon_runtime_support: float
    reproducibility_support: float

    commercial_license_acceptable: bool
    privacy_data_retention_acceptable: bool
    model_weight_restrictions_acceptable: bool
    dataset_restrictions_acceptable: bool

    processing_time_seconds: float
    processing_cost_eur: float

    SUPPORTED_ARCHITECTURE_KINDS = (
        "parametric_fixed_topology",
        "direct_neural_dense",
        "hybrid_canonical_detail",
    )

    def __post_init__(self) -> None:
        candidate_id = str(self.candidate_id).strip()
        if not candidate_id:
            raise ValueError(
                "candidate_id must be non-blank."
            )

        architecture_kind = "_".join(
            str(self.architecture_kind)
            .strip()
            .lower()
            .split()
        )

        if (
            architecture_kind
            not in self.SUPPORTED_ARCHITECTURE_KINDS
        ):
            raise ValueError(
                "architecture_kind must be one of "
                f"{self.SUPPORTED_ARCHITECTURE_KINDS}."
            )

        object.__setattr__(
            self,
            "candidate_id",
            candidate_id,
        )
        object.__setattr__(
            self,
            "architecture_kind",
            architecture_kind,
        )

        for field_name in (
            "identity_preservation_support",
            "multi_view_consistency",
            "silhouette_profile_support",
            "head_ratio_support",
            "jaw_chin_support",
            "nose_projection_support",
            "orbital_cheek_volume_support",
            "expression_separation_support",
            "pose_separation_support",
            "topology_suitability",
            "physical_suitability",
            "apple_silicon_runtime_support",
            "reproducibility_support",
        ):
            value = float(
                getattr(self, field_name)
            )

            if not isfinite(value):
                raise ValueError(
                    f"{field_name} must be finite."
                )

            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{field_name} must be within [0, 1]."
                )

            object.__setattr__(
                self,
                field_name,
                value,
            )

        for field_name in (
            "commercial_license_acceptable",
            "privacy_data_retention_acceptable",
            "model_weight_restrictions_acceptable",
            "dataset_restrictions_acceptable",
        ):
            if not isinstance(
                getattr(self, field_name),
                bool,
            ):
                raise TypeError(
                    f"{field_name} must be boolean."
                )

        for field_name in (
            "processing_time_seconds",
            "processing_cost_eur",
        ):
            value = float(
                getattr(self, field_name)
            )

            if not isfinite(value) or value < 0.0:
                raise ValueError(
                    f"{field_name} must be finite and nonnegative."
                )

            object.__setattr__(
                self,
                field_name,
                value,
            )
