from __future__ import annotations

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadDigitalPhysicalFailureClassification:
    representation_id: str
    representation_kind: str
    failure_id: str
    observation_state: str
    failure_attribution: str
    evidence_provenance: str
    attribution_basis: str

    SUPPORTED_REPRESENTATION_KINDS = (
        "relief",
        "bust",
        "figurine_head",
        "story_kit_component",
    )

    SUPPORTED_OBSERVATION_STATES = (
        "OBSERVED",
        "UNRESOLVED",
        "NOT_OBSERVABLE",
    )

    OBSERVED_FAILURE_ATTRIBUTIONS = (
        "reconstruction",
        "canonical_to_physical_adapter",
        "lod",
        "slicer",
        "printer",
        "material",
        "post_processing",
    )

    NON_OBSERVED_ATTRIBUTIONS = (
        "unresolved",
        "not_observable",
    )

    def __post_init__(self) -> None:
        representation_id = self._required_text(
            self.representation_id,
            field_name="representation_id",
        )

        representation_kind = self._normalize_lower_identifier(
            self.representation_kind,
            field_name="representation_kind",
        )

        if (
            representation_kind
            not in self.SUPPORTED_REPRESENTATION_KINDS
        ):
            raise ValueError(
                "representation_kind must be one of "
                f"{self.SUPPORTED_REPRESENTATION_KINDS}."
            )

        failure_id = self._required_text(
            self.failure_id,
            field_name="failure_id",
        )

        observation_state = self._normalize_upper_identifier(
            self.observation_state,
            field_name="observation_state",
        )

        if (
            observation_state
            not in self.SUPPORTED_OBSERVATION_STATES
        ):
            raise ValueError(
                "observation_state must be one of "
                f"{self.SUPPORTED_OBSERVATION_STATES}."
            )

        failure_attribution = self._normalize_lower_identifier(
            self.failure_attribution,
            field_name="failure_attribution",
        )

        evidence_provenance = self._required_text(
            self.evidence_provenance,
            field_name="evidence_provenance",
        )

        attribution_basis = self._required_text(
            self.attribution_basis,
            field_name="attribution_basis",
        )

        if observation_state == "OBSERVED":
            if (
                failure_attribution
                not in self.OBSERVED_FAILURE_ATTRIBUTIONS
            ):
                raise ValueError(
                    "OBSERVED evidence requires failure_attribution "
                    "to be one of "
                    f"{self.OBSERVED_FAILURE_ATTRIBUTIONS}."
                )
        else:
            expected = observation_state.lower()

            if failure_attribution != expected:
                raise ValueError(
                    "non-observed failure_attribution must match "
                    "observation_state."
                )

        object.__setattr__(
            self,
            "representation_id",
            representation_id,
        )
        object.__setattr__(
            self,
            "representation_kind",
            representation_kind,
        )
        object.__setattr__(
            self,
            "failure_id",
            failure_id,
        )
        object.__setattr__(
            self,
            "observation_state",
            observation_state,
        )
        object.__setattr__(
            self,
            "failure_attribution",
            failure_attribution,
        )
        object.__setattr__(
            self,
            "evidence_provenance",
            evidence_provenance,
        )
        object.__setattr__(
            self,
            "attribution_basis",
            attribution_basis,
        )

    @staticmethod
    def _required_text(
        value: object,
        *,
        field_name: str,
    ) -> str:
        if value is None:
            raise ValueError(
                f"{field_name} must not be blank."
            )

        normalized = str(value).strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must not be blank."
            )

        return normalized

    @staticmethod
    def _normalize_lower_identifier(
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
    def _normalize_upper_identifier(
        value: object,
        *,
        field_name: str,
    ) -> str:
        normalized = "_".join(
            str(value).strip().upper().split()
        )

        if not normalized:
            raise ValueError(
                f"{field_name} must not be blank."
            )

        return normalized
