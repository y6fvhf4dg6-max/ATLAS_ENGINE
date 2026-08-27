from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadMetricMeshUnitNormalizationResult:
    vertices_mm: np.ndarray
    source_units: str
    target_units: str
    scale_factor: float
    unit_provenance: str
    unit_provenance_reference: str
    unit_transform_kind: str
    metrological_traceability_established: bool

    def __post_init__(self) -> None:
        vertices = np.asarray(
            self.vertices_mm,
            dtype=np.float64,
        )

        if (
            vertices.ndim != 2
            or vertices.shape[1] != 3
            or vertices.shape[0] == 0
        ):
            raise ValueError(
                "vertices_mm must have shape (N, 3)."
            )

        if not np.all(
            np.isfinite(vertices)
        ):
            raise ValueError(
                "vertices_mm must contain only finite values."
            )

        vertices = vertices.copy()
        vertices.setflags(write=False)

        object.__setattr__(
            self,
            "vertices_mm",
            vertices,
        )

        source_units = str(
            self.source_units
        ).strip().lower()

        if source_units not in (
            "mm",
            "cm",
            "m",
        ):
            raise ValueError(
                "source_units must be one of ('mm', 'cm', 'm')."
            )

        object.__setattr__(
            self,
            "source_units",
            source_units,
        )

        if self.target_units != "mm":
            raise ValueError(
                "target_units must be 'mm'."
            )

        scale_factor = float(
            self.scale_factor
        )

        if (
            not np.isfinite(scale_factor)
            or scale_factor <= 0.0
        ):
            raise ValueError(
                "scale_factor must be finite and greater than zero."
            )

        object.__setattr__(
            self,
            "scale_factor",
            scale_factor,
        )

        unit_provenance = str(
            self.unit_provenance
        ).strip().upper()

        if unit_provenance not in (
            "FORMAT_STANDARD_DEFINED",
            "METADATA_DECLARED",
            "CALIBRATION_DERIVED",
        ):
            raise ValueError(
                "unit_provenance must be one of "
                "('FORMAT_STANDARD_DEFINED', 'METADATA_DECLARED', "
                "'CALIBRATION_DERIVED')."
            )

        unit_provenance_reference = str(
            self.unit_provenance_reference
        ).strip()

        if (
            not unit_provenance_reference
            or unit_provenance_reference.upper() == "UNRESOLVED"
        ):
            raise ValueError(
                "unit_provenance_reference must be resolved."
            )

        unit_transform_kind = str(
            self.unit_transform_kind
        ).strip().upper()

        if unit_transform_kind != "EXPLICIT_METRIC_UNIT_CONVERSION":
            raise ValueError(
                "unit_transform_kind must be "
                "'EXPLICIT_METRIC_UNIT_CONVERSION'."
            )

        if not isinstance(
            self.metrological_traceability_established,
            bool,
        ):
            raise TypeError(
                "metrological_traceability_established must be boolean."
            )

        object.__setattr__(
            self,
            "unit_provenance",
            unit_provenance,
        )
        object.__setattr__(
            self,
            "unit_provenance_reference",
            unit_provenance_reference,
        )
        object.__setattr__(
            self,
            "unit_transform_kind",
            unit_transform_kind,
        )


class AtlasCanonicalHeadMetricMeshUnitNormalizer:
    SCALE_TO_MM = {
        "mm": 1.0,
        "cm": 10.0,
        "m": 1000.0,
    }

    @classmethod
    def normalize(
        cls,
        *,
        vertices: object,
        source_units: object,
        unit_provenance: object,
        unit_provenance_reference: object,
    ) -> AtlasCanonicalHeadMetricMeshUnitNormalizationResult:
        source_units = str(
            source_units
        ).strip().lower()

        if source_units not in cls.SCALE_TO_MM:
            raise ValueError(
                "source_units must be one of ('mm', 'cm', 'm'); "
                "unresolved units must not be inferred."
            )

        normalized_unit_provenance = str(
            unit_provenance
        ).strip().upper()

        if normalized_unit_provenance not in (
            "FORMAT_STANDARD_DEFINED",
            "METADATA_DECLARED",
            "CALIBRATION_DERIVED",
        ):
            raise ValueError(
                "unit_provenance must be one of "
                "('FORMAT_STANDARD_DEFINED', 'METADATA_DECLARED', "
                "'CALIBRATION_DERIVED')."
            )

        normalized_unit_provenance_reference = str(
            unit_provenance_reference
        ).strip()

        if (
            not normalized_unit_provenance_reference
            or normalized_unit_provenance_reference.upper() == "UNRESOLVED"
        ):
            raise ValueError(
                "unit_provenance_reference must be resolved."
            )

        array = np.asarray(
            vertices,
            dtype=np.float64,
        )

        if (
            array.ndim != 2
            or array.shape[1] != 3
            or array.shape[0] == 0
        ):
            raise ValueError(
                "vertices must have shape (N, 3)."
            )

        if not np.all(
            np.isfinite(array)
        ):
            raise ValueError(
                "vertices must contain only finite values."
            )

        scale_factor = cls.SCALE_TO_MM[
            source_units
        ]

        vertices_mm = (
            array.copy()
            * scale_factor
        )

        return AtlasCanonicalHeadMetricMeshUnitNormalizationResult(
            vertices_mm=vertices_mm,
            source_units=source_units,
            target_units="mm",
            scale_factor=scale_factor,
            unit_provenance=normalized_unit_provenance,
            unit_provenance_reference=normalized_unit_provenance_reference,
            unit_transform_kind="EXPLICIT_METRIC_UNIT_CONVERSION",
            metrological_traceability_established=False,
        )
