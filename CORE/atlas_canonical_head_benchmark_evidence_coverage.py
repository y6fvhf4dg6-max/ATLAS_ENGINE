from __future__ import annotations

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadBenchmarkEvidenceCoverage:
    candidate_id: str

    identity_preservation_support: str
    multi_view_consistency: str
    silhouette_profile_support: str
    head_ratio_support: str
    jaw_chin_support: str
    nose_projection_support: str
    orbital_cheek_volume_support: str
    expression_separation_support: str
    pose_separation_support: str
    topology_suitability: str
    physical_suitability: str
    apple_silicon_runtime_support: str
    reproducibility_support: str

    SUPPORTED_EVIDENCE_STATES = (
        "MEASURED",
        "PARTIAL",
        "DIRECT",
        "MISSING",
    )

    QUALITY_CHANNELS = (
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
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.candidate_id,
            str,
        ):
            raise TypeError(
                "candidate_id must be a string."
            )

        candidate_id = self.candidate_id.strip()

        if not candidate_id:
            raise ValueError(
                "candidate_id must be non-blank."
            )

        object.__setattr__(
            self,
            "candidate_id",
            candidate_id,
        )

        for field_name in self.QUALITY_CHANNELS:
            value = getattr(
                self,
                field_name,
            )

            if not isinstance(
                value,
                str,
            ):
                raise TypeError(
                    f"{field_name} must be a string."
                )

            normalized = value.strip().upper()

            if (
                normalized
                not in self.SUPPORTED_EVIDENCE_STATES
            ):
                raise ValueError(
                    f"{field_name} must be one of "
                    f"{self.SUPPORTED_EVIDENCE_STATES}."
                )

            object.__setattr__(
                self,
                field_name,
                normalized,
            )

    @property
    def missing_channels(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            field_name
            for field_name in self.QUALITY_CHANNELS
            if getattr(
                self,
                field_name,
            )
            == "MISSING"
        )
