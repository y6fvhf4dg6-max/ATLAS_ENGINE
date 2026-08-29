from __future__ import annotations

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadMaterialSensitivity:
    representation_id: str
    representation_kind: str
    reference_material: str
    evaluated_material: str
    reference_material_profile_id: str
    evaluated_material_profile_id: str
    observation_state: str
    evidence_provenance: str
    affected_regions: tuple[str, ...]
    sensitivity_state: str

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

    OBSERVED_SENSITIVITY_STATES = (
        "NO_MATERIAL_CHANGE",
        "MATERIAL_CHANGE",
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

        reference_material = self._normalize_lower_identifier(
            self.reference_material,
            field_name="reference_material",
        )

        evaluated_material = self._normalize_lower_identifier(
            self.evaluated_material,
            field_name="evaluated_material",
        )

        reference_material_profile_id = (
            self._normalize_lower_identifier(
                self.reference_material_profile_id,
                field_name="reference_material_profile_id",
            )
        )

        evaluated_material_profile_id = (
            self._normalize_lower_identifier(
                self.evaluated_material_profile_id,
                field_name="evaluated_material_profile_id",
            )
        )

        observation_state = self._normalize_upper_identifier(
            self.observation_state,
            field_name="observation_state",
        )

        if observation_state not in self.SUPPORTED_OBSERVATION_STATES:
            raise ValueError(
                "observation_state must be one of "
                f"{self.SUPPORTED_OBSERVATION_STATES}."
            )

        evidence_provenance = self._required_text(
            self.evidence_provenance,
            field_name="evidence_provenance",
        )

        affected_regions = self._normalize_regions(
            self.affected_regions,
        )

        sensitivity_state = self._normalize_upper_identifier(
            self.sensitivity_state,
            field_name="sensitivity_state",
        )

        if observation_state == "OBSERVED":
            if sensitivity_state not in self.OBSERVED_SENSITIVITY_STATES:
                raise ValueError(
                    "OBSERVED evidence requires sensitivity_state "
                    "to be one of "
                    f"{self.OBSERVED_SENSITIVITY_STATES}."
                )

            if (
                sensitivity_state == "NO_MATERIAL_CHANGE"
                and affected_regions
            ):
                raise ValueError(
                    "NO_MATERIAL_CHANGE requires affected_regions "
                    "to be empty."
                )

            if (
                sensitivity_state == "MATERIAL_CHANGE"
                and not affected_regions
            ):
                raise ValueError(
                    "MATERIAL_CHANGE requires at least one "
                    "affected region."
                )
        else:
            if sensitivity_state != observation_state:
                raise ValueError(
                    "non-observed sensitivity_state must match "
                    "observation_state."
                )

            if affected_regions:
                raise ValueError(
                    "non-observed evidence must not claim "
                    "affected regions."
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
            "reference_material",
            reference_material,
        )
        object.__setattr__(
            self,
            "evaluated_material",
            evaluated_material,
        )
        object.__setattr__(
            self,
            "reference_material_profile_id",
            reference_material_profile_id,
        )
        object.__setattr__(
            self,
            "evaluated_material_profile_id",
            evaluated_material_profile_id,
        )
        object.__setattr__(
            self,
            "observation_state",
            observation_state,
        )
        object.__setattr__(
            self,
            "evidence_provenance",
            evidence_provenance,
        )
        object.__setattr__(
            self,
            "affected_regions",
            affected_regions,
        )
        object.__setattr__(
            self,
            "sensitivity_state",
            sensitivity_state,
        )

    @classmethod
    def _normalize_regions(
        cls,
        value: object,
    ) -> tuple[str, ...]:
        if isinstance(value, (str, bytes)):
            raise TypeError(
                "affected_regions must be a sequence of region identifiers."
            )

        try:
            raw_regions = tuple(value)
        except TypeError as exc:
            raise TypeError(
                "affected_regions must be iterable."
            ) from exc

        normalized = []
        seen = set()

        for raw_region in raw_regions:
            region = cls._normalize_lower_identifier(
                raw_region,
                field_name="affected_regions",
            )

            if region not in cls.SUPPORTED_REGIONS:
                raise ValueError(
                    "affected_regions must contain only "
                    f"{cls.SUPPORTED_REGIONS}."
                )

            if region in seen:
                continue

            seen.add(region)
            normalized.append(region)

        return tuple(normalized)

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
