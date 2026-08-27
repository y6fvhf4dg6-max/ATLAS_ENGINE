from __future__ import annotations

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadSemanticRegionMappingEvidence:
    region_name: str
    mapping_state: str
    mapping_name: str
    mapping_scope: str
    evidence_origin: str
    source_reference: str
    permitted_claim: str
    prohibited_claims: tuple[str, ...]

    REQUIRED_REGIONS = (
        "jaw",
        "chin",
        "nose_bridge",
        "nose_body",
        "nose_base_tip",
        "left_orbital",
        "right_orbital",
        "left_cheek",
        "right_cheek",
        "upper_lip",
        "lower_lip",
        "perioral",
        "forehead",
        "cranial_head_envelope",
    )

    MAPPING_STATES = (
        "provider_verified",
        "independently_verified_atlas_derived",
        "anchor_supported_only",
        "unresolved_blocked",
    )

    EVIDENCE_ORIGINS = (
        "directly_observed",
        "multiview_constrained",
        "model_prior_inferred",
        "generated_completion",
        "unresolved",
    )

    def __post_init__(
        self,
    ) -> None:
        region_name = self._normalize_identifier(
            self.region_name,
            field_name="region_name",
        )
        mapping_state = self._normalize_identifier(
            self.mapping_state,
            field_name="mapping_state",
        )

        if region_name not in self.REQUIRED_REGIONS:
            raise ValueError(
                "region_name must be one of the exact "
                "Item 9.2 required semantic regions."
            )

        if mapping_state not in self.MAPPING_STATES:
            raise ValueError(
                "mapping_state must be one of the exact "
                "Item 9.2 mapping states."
            )

        mapping_name = self._normalize_required_text(
            self.mapping_name,
            field_name="mapping_name",
        )
        mapping_scope = self._normalize_required_text(
            self.mapping_scope,
            field_name="mapping_scope",
        )
        evidence_origin = self._normalize_identifier(
            self.evidence_origin,
            field_name="evidence_origin",
        )

        if evidence_origin not in self.EVIDENCE_ORIGINS:
            raise ValueError(
                "evidence_origin must be one of the exact "
                "Item 9.2 evidence-origin states."
            )

        source_reference = self._normalize_required_text(
            self.source_reference,
            field_name="source_reference",
        )
        permitted_claim = self._normalize_required_text(
            self.permitted_claim,
            field_name="permitted_claim",
        )
        prohibited_claims = self._normalize_prohibited_claims(
            self.prohibited_claims,
        )

        object.__setattr__(
            self,
            "region_name",
            region_name,
        )
        object.__setattr__(
            self,
            "mapping_state",
            mapping_state,
        )
        object.__setattr__(
            self,
            "mapping_name",
            mapping_name,
        )
        object.__setattr__(
            self,
            "mapping_scope",
            mapping_scope,
        )
        object.__setattr__(
            self,
            "evidence_origin",
            evidence_origin,
        )
        object.__setattr__(
            self,
            "source_reference",
            source_reference,
        )
        object.__setattr__(
            self,
            "permitted_claim",
            permitted_claim,
        )
        object.__setattr__(
            self,
            "prohibited_claims",
            prohibited_claims,
        )

    @staticmethod
    def _normalize_identifier(
        value: object,
        *,
        field_name: str,
    ) -> str:
        normalized = "_".join(
            str(value).strip().lower().split()
        )

        if not normalized:
            raise ValueError(
                f"{field_name} must not be blank."
            )

        return normalized

    @staticmethod
    def _normalize_required_text(
        value: object,
        *,
        field_name: str,
    ) -> str:
        normalized = str(value).strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must not be blank."
            )

        return normalized

    @classmethod
    def _normalize_prohibited_claims(
        cls,
        value: object,
    ) -> tuple[str, ...]:
        if isinstance(
            value,
            (str, bytes),
        ):
            raise TypeError(
                "prohibited_claims must be a non-empty sequence."
            )

        try:
            raw_claims = tuple(value)
        except TypeError as exc:
            raise TypeError(
                "prohibited_claims must be a non-empty sequence."
            ) from exc

        if not raw_claims:
            raise ValueError(
                "prohibited_claims must not be empty."
            )

        return tuple(
            cls._normalize_required_text(
                claim,
                field_name="prohibited_claims",
            )
            for claim in raw_claims
        )
