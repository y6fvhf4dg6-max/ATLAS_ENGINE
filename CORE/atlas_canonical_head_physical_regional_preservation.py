from __future__ import annotations

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadPhysicalRegionalPreservation:
    representation_id: str
    representation_kind: str
    region_name: str
    observation_state: str
    digital_reference: str | None
    physical_reference: str | None
    observation_provenance: str
    preservation_state: str

    SUPPORTED_REPRESENTATION_KINDS = (
        "relief",
        "bust",
        "figurine_head",
        "story_kit_component",
    )

    SUPPORTED_REGIONS = (
        "nose",
        "jaw_chin",
        "orbital",
        "cheek_midface",
        "mouth_perioral",
        "forehead_cranial",
        "silhouette",
        "profile",
    )

    SUPPORTED_OBSERVATION_STATES = (
        "OBSERVED",
        "UNRESOLVED",
        "NOT_OBSERVABLE",
    )

    OBSERVED_PRESERVATION_STATES = (
        "PRESERVED",
        "DEGRADED",
        "LOST",
    )

    NON_OBSERVED_PRESERVATION_STATES = (
        "UNRESOLVED",
        "NOT_OBSERVABLE",
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

        region_name = self._normalize_lower_identifier(
            self.region_name,
            field_name="region_name",
        )

        if region_name not in self.SUPPORTED_REGIONS:
            raise ValueError(
                "region_name must be one of "
                f"{self.SUPPORTED_REGIONS}."
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

        observation_provenance = self._required_text(
            self.observation_provenance,
            field_name="observation_provenance",
        )

        preservation_state = self._normalize_upper_identifier(
            self.preservation_state,
            field_name="preservation_state",
        )

        if observation_state == "OBSERVED":
            if (
                preservation_state
                not in self.OBSERVED_PRESERVATION_STATES
            ):
                raise ValueError(
                    "OBSERVED evidence requires preservation_state "
                    "to be one of "
                    f"{self.OBSERVED_PRESERVATION_STATES}."
                )

            digital_reference = self._required_text(
                self.digital_reference,
                field_name="digital_reference",
            )
            physical_reference = self._required_text(
                self.physical_reference,
                field_name="physical_reference",
            )
        else:
            if (
                preservation_state
                != observation_state
            ):
                raise ValueError(
                    "non-observed preservation_state must match "
                    "observation_state."
                )

            if self.digital_reference is not None:
                raise ValueError(
                    "digital_reference must be None when "
                    f"observation_state is {observation_state}."
                )

            if self.physical_reference is not None:
                raise ValueError(
                    "physical_reference must be None when "
                    f"observation_state is {observation_state}."
                )

            digital_reference = None
            physical_reference = None

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
            "region_name",
            region_name,
        )
        object.__setattr__(
            self,
            "observation_state",
            observation_state,
        )
        object.__setattr__(
            self,
            "digital_reference",
            digital_reference,
        )
        object.__setattr__(
            self,
            "physical_reference",
            physical_reference,
        )
        object.__setattr__(
            self,
            "observation_provenance",
            observation_provenance,
        )
        object.__setattr__(
            self,
            "preservation_state",
            preservation_state,
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
