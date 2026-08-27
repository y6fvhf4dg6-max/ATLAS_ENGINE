from __future__ import annotations

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadEvaluationSpaceClaimBoundaryResult:
    allowed: bool
    status: str
    failure_reason: str | None


class AtlasCanonicalHeadEvaluationSpaceClaimBoundary:
    EVALUATION_SPACES = (
        "2d_observation",
        "canonical_model",
        "metric_3d_ground_truth",
        "physical_output",
    )

    EVIDENCE_KINDS = (
        "landmark_fit",
        "2d_reprojection",
        "canonical_model_displacement",
        "printability",
        "aggregate_improvement",
    )

    CLAIM_KINDS = (
        "landmark_fit",
        "surface_accuracy",
        "2d_reprojection",
        "metric_3d_accuracy",
        "canonical_model_displacement",
        "anatomical_millimetres",
        "printability",
        "identity_preservation",
        "aggregate_improvement",
        "uniform_regional_improvement",
    )

    FORBIDDEN_PROMOTIONS = frozenset(
        {
            ("landmark_fit", "surface_accuracy"),
            ("2d_reprojection", "metric_3d_accuracy"),
            (
                "canonical_model_displacement",
                "anatomical_millimetres",
            ),
            ("printability", "identity_preservation"),
            (
                "aggregate_improvement",
                "uniform_regional_improvement",
            ),
        }
    )

    @classmethod
    def evaluate(
        cls,
        *,
        evidence_kind: object,
        claim_kind: object,
    ) -> AtlasCanonicalHeadEvaluationSpaceClaimBoundaryResult:
        evidence_kind = cls._normalize(
            evidence_kind,
            name="evidence_kind",
        )
        claim_kind = cls._normalize(
            claim_kind,
            name="claim_kind",
        )

        if evidence_kind not in cls.EVIDENCE_KINDS:
            raise ValueError(
                f"evidence_kind must be one of {cls.EVIDENCE_KINDS}."
            )

        if claim_kind not in cls.CLAIM_KINDS:
            raise ValueError(
                f"claim_kind must be one of {cls.CLAIM_KINDS}."
            )

        if (
            evidence_kind,
            claim_kind,
        ) in cls.FORBIDDEN_PROMOTIONS:
            return AtlasCanonicalHeadEvaluationSpaceClaimBoundaryResult(
                allowed=False,
                status="BLOCKED",
                failure_reason="UNSUPPORTED_CLAIM_PROMOTION",
            )

        if evidence_kind == claim_kind:
            return AtlasCanonicalHeadEvaluationSpaceClaimBoundaryResult(
                allowed=True,
                status="ALLOWED",
                failure_reason=None,
            )

        return AtlasCanonicalHeadEvaluationSpaceClaimBoundaryResult(
            allowed=False,
            status="BLOCKED",
            failure_reason="UNSUPPORTED_CLAIM_PROMOTION",
        )

    @staticmethod
    def _normalize(
        value: object,
        *,
        name: str,
    ) -> str:
        normalized = "_".join(
            str(value).strip().lower().split()
        )

        if not normalized:
            raise ValueError(
                f"{name} must be non-blank."
            )

        return normalized
