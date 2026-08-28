from __future__ import annotations

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadPhysicalTransform:
    operation: str
    classification: str
    parameters: tuple[tuple[str, str], ...]

    SUPPORTED_OPERATIONS = (
        "scale",
        "orientation",
        "translation",
        "clipping",
        "relief_depth_mapping",
        "relief_depth_compression",
        "lod_decimation",
        "shell_thickness",
        "smoothing",
        "repair",
        "feature_exaggeration",
        "topology_change",
    )

    SUPPORTED_CLASSIFICATIONS = (
        "identity_neutral",
        "identity_sensitive",
        "topology_changing",
    )

    TOPOLOGY_CHANGING_OPERATIONS = (
        "topology_change",
        "lod_decimation",
    )

    IDENTITY_SENSITIVE_OPERATIONS = (
        "clipping",
        "relief_depth_mapping",
        "relief_depth_compression",
        "smoothing",
        "feature_exaggeration",
    )

    def __post_init__(self) -> None:
        operation = self._normalize_identifier(
            self.operation,
            name="operation",
        )
        if operation not in self.SUPPORTED_OPERATIONS:
            raise ValueError(
                "operation must be one of "
                f"{self.SUPPORTED_OPERATIONS}."
            )

        classification = self._normalize_identifier(
            self.classification,
            name="classification",
        )
        if classification not in self.SUPPORTED_CLASSIFICATIONS:
            raise ValueError(
                "classification must be one of "
                f"{self.SUPPORTED_CLASSIFICATIONS}."
            )

        if (
            operation in self.TOPOLOGY_CHANGING_OPERATIONS
            and classification != "topology_changing"
        ):
            raise ValueError(
                f"classification for {operation} must be "
                "'topology_changing'."
            )

        if (
            operation in self.IDENTITY_SENSITIVE_OPERATIONS
            and classification == "identity_neutral"
        ):
            raise ValueError(
                f"classification for {operation} must not be "
                "'identity_neutral'."
            )

        try:
            raw_parameters = tuple(self.parameters)
        except TypeError as exc:
            raise TypeError(
                "parameters must be an iterable of key/value pairs."
            ) from exc

        if not raw_parameters:
            raise ValueError(
                "parameters must not be empty."
            )

        normalized_parameters = []
        parameter_keys = set()

        for raw_parameter in raw_parameters:
            try:
                key, value = tuple(raw_parameter)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "each parameter must contain exactly two values."
                ) from exc

            key = str(key).strip()
            value = str(value).strip()

            if not key:
                raise ValueError(
                    "parameter key must be non-blank."
                )

            if not value:
                raise ValueError(
                    "parameter value must be non-blank."
                )

            if key in parameter_keys:
                raise ValueError(
                    "parameter keys must be unique."
                )

            parameter_keys.add(key)

            normalized_parameters.append(
                (key, value)
            )

        object.__setattr__(
            self,
            "operation",
            operation,
        )
        object.__setattr__(
            self,
            "classification",
            classification,
        )
        object.__setattr__(
            self,
            "parameters",
            tuple(normalized_parameters),
        )

    @staticmethod
    def _normalize_identifier(
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


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadPhysicalAdapterIsolation:
    source_identity_id: str
    source_topology_signature: str
    source_geometry_signature_before: str
    source_geometry_signature_after: str
    source_provenance: str
    representation_id: str
    representation_kind: str
    physical_unit: str
    output_topology_signature: str
    transform_ledger: tuple[
        AtlasCanonicalHeadPhysicalTransform,
        ...
    ]

    SUPPORTED_REPRESENTATION_KINDS = (
        "relief",
        "bust",
        "figurine_head",
        "story_kit_component",
    )

    def __post_init__(self) -> None:
        for field_name in (
            "source_identity_id",
            "source_topology_signature",
            "source_geometry_signature_before",
            "source_geometry_signature_after",
            "source_provenance",
            "representation_id",
            "output_topology_signature",
        ):
            value = str(
                getattr(self, field_name)
            ).strip()

            if not value:
                raise ValueError(
                    f"{field_name} must be non-blank."
                )

            object.__setattr__(
                self,
                field_name,
                value,
            )

        if self.source_identity_id == self.representation_id:
            raise ValueError(
                "representation_id must be distinct from "
                "source_identity_id."
            )

        representation_kind = "_".join(
            str(self.representation_kind)
            .strip()
            .lower()
            .split()
        )

        if (
            representation_kind
            not in self.SUPPORTED_REPRESENTATION_KINDS
        ):
            raise ValueError(
                "representation_kind must be one of "
                f"{self.SUPPORTED_REPRESENTATION_KINDS}."
            )

        object.__setattr__(
            self,
            "representation_kind",
            representation_kind,
        )

        physical_unit = str(
            self.physical_unit
        ).strip().lower()

        if physical_unit != "mm":
            raise ValueError(
                "physical_unit must be 'mm'."
            )

        object.__setattr__(
            self,
            "physical_unit",
            physical_unit,
        )

        try:
            transform_ledger = tuple(
                self.transform_ledger
            )
        except TypeError as exc:
            raise TypeError(
                "transform_ledger must be an iterable."
            ) from exc

        if not transform_ledger:
            raise ValueError(
                "transform_ledger must not be empty."
            )

        for transform in transform_ledger:
            if not isinstance(
                transform,
                AtlasCanonicalHeadPhysicalTransform,
            ):
                raise TypeError(
                    "transform_ledger must contain only "
                    "AtlasCanonicalHeadPhysicalTransform."
                )

        object.__setattr__(
            self,
            "transform_ledger",
            transform_ledger,
        )

    @property
    def source_is_unchanged(self) -> bool:
        return (
            self.source_geometry_signature_before
            == self.source_geometry_signature_after
        )

    @property
    def isolation_state(self) -> str:
        if self.source_is_unchanged:
            return "ISOLATED"

        return "SOURCE_MUTATED"
