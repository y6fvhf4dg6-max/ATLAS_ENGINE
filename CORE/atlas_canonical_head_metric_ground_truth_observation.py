from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadMetricGroundTruthObservation:
    observation_id: str
    subject_id: str
    source_id: str
    units: str

    ground_truth_vertices: np.ndarray
    ground_truth_faces: tuple[tuple[int, int, int], ...]

    reconstruction_vertices: np.ndarray
    reconstruction_faces: tuple[tuple[int, int, int], ...]

    source_provenance_state: str
    evaluation_license_state: str
    evaluation_use_only: bool

    acquisition_modality: str
    acquisition_system: str
    acquisition_manufacturer: str
    reconstruction_modality: str
    reconstruction_software: str
    reconstruction_software_version: str
    ground_truth_surface_origin: str
    ground_truth_strength_state: str
    subject_match_state: str
    capture_session_relation: str
    capture_expression: str
    capture_pose: str
    capture_date: str
    physical_resolution_state: str
    physical_resolution_reference: str
    calibration_state: str
    calibration_reference: str
    known_reference_dimension_mm: float | None
    reference_uncertainty_mm: float | None
    calibration_date: str
    reconstruction_scale_factor: float
    scale_transform_provenance: str
    scale_source: str
    scale_uncertainty_mm: float | None
    scale_uncertainty_propagation: str
    source_provenance_reference: str
    license_reference: str
    license_restrictions: str
    ground_truth_admissibility_state: str

    def __post_init__(self) -> None:
        for field_name in (
            "observation_id",
            "subject_id",
            "source_id",
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

        units = str(self.units).strip().lower()

        if units != "mm":
            raise ValueError(
                "units must be 'mm'."
            )

        object.__setattr__(
            self,
            "units",
            units,
        )

        source_provenance_state = str(
            self.source_provenance_state
        ).strip().upper()

        if source_provenance_state not in (
            "VERIFIED",
            "UNRESOLVED",
        ):
            raise ValueError(
                "source_provenance_state must be one of "
                "('VERIFIED', 'UNRESOLVED')."
            )

        object.__setattr__(
            self,
            "source_provenance_state",
            source_provenance_state,
        )

        evaluation_license_state = str(
            self.evaluation_license_state
        ).strip().upper()

        if evaluation_license_state not in (
            "ACCEPTABLE",
            "BLOCKED",
            "UNRESOLVED",
        ):
            raise ValueError(
                "evaluation_license_state must be one of "
                "('ACCEPTABLE', 'BLOCKED', 'UNRESOLVED')."
            )

        object.__setattr__(
            self,
            "evaluation_license_state",
            evaluation_license_state,
        )

        if not isinstance(
            self.evaluation_use_only,
            bool,
        ):
            raise TypeError(
                "evaluation_use_only must be boolean."
            )

        acquisition_modality = self._normalize_state(
            self.acquisition_modality,
            name="acquisition_modality",
            allowed=(
                "MULTIVIEW_IMAGE_CAPTURE",
                "STRUCTURED_LIGHT_CAPTURE",
                "STEREOPHOTOGRAMMETRIC_CAPTURE",
                "LASER_SCAN_CAPTURE",
                "CT_CAPTURE",
                "CBCT_CAPTURE",
                "OTHER_VERIFIED_CAPTURE",
                "UNRESOLVED",
            ),
        )
        reconstruction_modality = self._normalize_state(
            self.reconstruction_modality,
            name="reconstruction_modality",
            allowed=(
                "IMAGE_BASED_MULTIVIEW_RECONSTRUCTION",
                "DIRECT_SENSOR_SURFACE",
                "REGISTERED_SENSOR_SURFACE",
                "MODEL_FITTED_RECONSTRUCTION",
                "GENERATED_OR_INFERRED_RECONSTRUCTION",
                "UNRESOLVED",
            ),
        )
        ground_truth_surface_origin = self._normalize_state(
            self.ground_truth_surface_origin,
            name="ground_truth_surface_origin",
            allowed=(
                "RAW_SENSOR_DERIVED_SURFACE",
                "REGISTERED_SENSOR_DERIVED_SURFACE",
                "RECONSTRUCTED_SENSOR_DERIVED_SURFACE",
                "MODEL_FITTED_TO_SCAN_GEOMETRY",
                "GENERATED_OR_INFERRED_GEOMETRY",
                "UNRESOLVED",
            ),
        )
        ground_truth_strength_state = self._normalize_state(
            self.ground_truth_strength_state,
            name="ground_truth_strength_state",
            allowed=(
                "RAW_SENSOR",
                "REGISTERED_SENSOR",
                "DERIVED_SENSOR",
                "MODEL_FITTED",
                "GENERATED_OR_INFERRED",
                "UNRESOLVED",
            ),
        )
        subject_match_state = self._normalize_state(
            self.subject_match_state,
            name="subject_match_state",
            allowed=(
                "VERIFIED",
                "PARTIAL",
                "UNRESOLVED",
            ),
        )
        capture_session_relation = self._normalize_state(
            self.capture_session_relation,
            name="capture_session_relation",
            allowed=(
                "SAME_SESSION_VERIFIED",
                "CROSS_SESSION_VERIFIED",
                "PARTIAL",
                "UNRESOLVED",
            ),
        )
        physical_resolution_state = self._normalize_state(
            self.physical_resolution_state,
            name="physical_resolution_state",
            allowed=(
                "VERIFIED",
                "PARTIAL",
                "UNRESOLVED",
            ),
        )
        calibration_state = self._normalize_state(
            self.calibration_state,
            name="calibration_state",
            allowed=(
                "VERIFIED",
                "PARTIAL",
                "UNRESOLVED",
            ),
        )
        scale_source = self._normalize_state(
            self.scale_source,
            name="scale_source",
            allowed=(
                "MEASURED",
                "DECLARED",
                "OPTIMIZED",
                "INFERRED",
                "UNRESOLVED",
            ),
        )
        ground_truth_admissibility_state = self._normalize_state(
            self.ground_truth_admissibility_state,
            name="ground_truth_admissibility_state",
            allowed=(
                "ACCEPTABLE",
                "BLOCKED",
                "UNRESOLVED",
            ),
        )

        acquisition_system = self._normalize_required_text(
            self.acquisition_system,
            name="acquisition_system",
            uppercase=False,
        )
        acquisition_manufacturer = self._normalize_required_text(
            self.acquisition_manufacturer,
            name="acquisition_manufacturer",
            uppercase=False,
        )
        reconstruction_software = self._normalize_required_text(
            self.reconstruction_software,
            name="reconstruction_software",
            uppercase=False,
        )
        reconstruction_software_version = self._normalize_required_text(
            self.reconstruction_software_version,
            name="reconstruction_software_version",
            uppercase=False,
        )
        capture_expression = self._normalize_required_text(
            self.capture_expression,
            name="capture_expression",
            uppercase=True,
        )
        capture_pose = self._normalize_required_text(
            self.capture_pose,
            name="capture_pose",
            uppercase=True,
        )
        capture_date = self._normalize_required_text(
            self.capture_date,
            name="capture_date",
            uppercase=False,
        )
        physical_resolution_reference = self._normalize_required_text(
            self.physical_resolution_reference,
            name="physical_resolution_reference",
            uppercase=False,
        )
        calibration_reference = self._normalize_required_text(
            self.calibration_reference,
            name="calibration_reference",
            uppercase=False,
        )
        calibration_date = self._normalize_required_text(
            self.calibration_date,
            name="calibration_date",
            uppercase=False,
        )
        scale_transform_provenance = self._normalize_required_text(
            self.scale_transform_provenance,
            name="scale_transform_provenance",
            uppercase=False,
        )
        scale_uncertainty_propagation = self._normalize_required_text(
            self.scale_uncertainty_propagation,
            name="scale_uncertainty_propagation",
            uppercase=False,
        )
        source_provenance_reference = self._normalize_required_text(
            self.source_provenance_reference,
            name="source_provenance_reference",
            uppercase=False,
        )
        license_reference = self._normalize_required_text(
            self.license_reference,
            name="license_reference",
            uppercase=False,
        )
        license_restrictions = self._normalize_required_text(
            self.license_restrictions,
            name="license_restrictions",
            uppercase=False,
        )

        def normalize_optional_nonnegative(
            value: object,
            *,
            name: str,
        ) -> float | None:
            if value is None:
                return None

            normalized = float(value)

            if (
                not np.isfinite(normalized)
                or normalized < 0.0
            ):
                raise ValueError(
                    f"{name} must be finite and non-negative when provided."
                )

            return normalized

        known_reference_dimension_mm = (
            normalize_optional_nonnegative(
                self.known_reference_dimension_mm,
                name="known_reference_dimension_mm",
            )
        )

        if (
            known_reference_dimension_mm is not None
            and known_reference_dimension_mm <= 0.0
        ):
            raise ValueError(
                "known_reference_dimension_mm must be greater than zero "
                "when provided."
            )

        reference_uncertainty_mm = normalize_optional_nonnegative(
            self.reference_uncertainty_mm,
            name="reference_uncertainty_mm",
        )
        scale_uncertainty_mm = normalize_optional_nonnegative(
            self.scale_uncertainty_mm,
            name="scale_uncertainty_mm",
        )

        reconstruction_scale_factor = float(
            self.reconstruction_scale_factor
        )

        if (
            not np.isfinite(reconstruction_scale_factor)
            or reconstruction_scale_factor <= 0.0
        ):
            raise ValueError(
                "reconstruction_scale_factor must be finite and "
                "greater than zero."
            )

        if calibration_state == "VERIFIED":
            if (
                calibration_reference.upper() == "UNRESOLVED"
                or calibration_date.upper() == "UNRESOLVED"
            ):
                raise ValueError(
                    "VERIFIED calibration requires resolved "
                    "calibration_reference and calibration_date."
                )

            if scale_transform_provenance.upper() == "UNRESOLVED":
                raise ValueError(
                    "VERIFIED calibration requires resolved "
                    "scale_transform_provenance."
                )

            if scale_source == "UNRESOLVED":
                raise ValueError(
                    "VERIFIED calibration requires resolved scale_source."
                )

            if scale_source in (
                "DECLARED",
                "OPTIMIZED",
                "INFERRED",
            ):
                raise ValueError(
                    "scale_source DECLARED, OPTIMIZED or INFERRED cannot "
                    "establish VERIFIED physical calibration."
                )

        if (
            scale_source == "MEASURED"
            and calibration_reference.upper() != "UNRESOLVED"
            and known_reference_dimension_mm is None
        ):
            raise ValueError(
                "MEASURED scale with a resolved calibration_reference "
                "requires known_reference_dimension_mm."
            )

        if (
            scale_uncertainty_mm is not None
            and scale_uncertainty_propagation.upper() == "UNRESOLVED"
        ):
            raise ValueError(
                "scale_uncertainty_propagation must be resolved when "
                "scale_uncertainty_mm is provided."
            )

        compatible_strength_by_surface_origin = {
            "RAW_SENSOR_DERIVED_SURFACE": "RAW_SENSOR",
            "REGISTERED_SENSOR_DERIVED_SURFACE": "REGISTERED_SENSOR",
            "RECONSTRUCTED_SENSOR_DERIVED_SURFACE": "DERIVED_SENSOR",
            "MODEL_FITTED_TO_SCAN_GEOMETRY": "MODEL_FITTED",
            "GENERATED_OR_INFERRED_GEOMETRY": "GENERATED_OR_INFERRED",
        }

        expected_strength = compatible_strength_by_surface_origin.get(
            ground_truth_surface_origin
        )

        if (
            expected_strength is not None
            and ground_truth_strength_state != expected_strength
        ):
            raise ValueError(
                "ground_truth_surface_origin and "
                "ground_truth_strength_state are incompatible."
            )

        if (
            physical_resolution_state == "VERIFIED"
            and physical_resolution_reference.upper() == "UNRESOLVED"
        ):
            raise ValueError(
                "verified physical_resolution_state requires a resolved "
                "physical_resolution_reference."
            )

        if (
            source_provenance_state == "VERIFIED"
            and source_provenance_reference.upper() == "UNRESOLVED"
        ):
            raise ValueError(
                "verified source_provenance_state requires a resolved "
                "source_provenance_reference."
            )

        if evaluation_license_state == "ACCEPTABLE":
            if (
                license_reference.upper() == "UNRESOLVED"
                or license_restrictions.upper() == "UNRESOLVED"
            ):
                raise ValueError(
                    "acceptable evaluation_license_state requires resolved "
                    "license_reference and license_restrictions."
                )

        for field_name, value in (
            ("acquisition_modality", acquisition_modality),
            ("acquisition_system", acquisition_system),
            ("acquisition_manufacturer", acquisition_manufacturer),
            ("reconstruction_modality", reconstruction_modality),
            ("reconstruction_software", reconstruction_software),
            (
                "reconstruction_software_version",
                reconstruction_software_version,
            ),
            ("ground_truth_surface_origin", ground_truth_surface_origin),
            ("ground_truth_strength_state", ground_truth_strength_state),
            ("subject_match_state", subject_match_state),
            ("capture_session_relation", capture_session_relation),
            ("capture_expression", capture_expression),
            ("capture_pose", capture_pose),
            ("capture_date", capture_date),
            ("physical_resolution_state", physical_resolution_state),
            (
                "physical_resolution_reference",
                physical_resolution_reference,
            ),
            ("calibration_state", calibration_state),
            ("calibration_reference", calibration_reference),
            ("calibration_date", calibration_date),
            (
                "scale_transform_provenance",
                scale_transform_provenance,
            ),
            ("scale_source", scale_source),
            (
                "scale_uncertainty_propagation",
                scale_uncertainty_propagation,
            ),
            (
                "source_provenance_reference",
                source_provenance_reference,
            ),
            ("license_reference", license_reference),
            ("license_restrictions", license_restrictions),
            (
                "ground_truth_admissibility_state",
                ground_truth_admissibility_state,
            ),
        ):
            object.__setattr__(
                self,
                field_name,
                value,
            )

        object.__setattr__(
            self,
            "known_reference_dimension_mm",
            known_reference_dimension_mm,
        )
        object.__setattr__(
            self,
            "reference_uncertainty_mm",
            reference_uncertainty_mm,
        )
        object.__setattr__(
            self,
            "reconstruction_scale_factor",
            reconstruction_scale_factor,
        )
        object.__setattr__(
            self,
            "scale_uncertainty_mm",
            scale_uncertainty_mm,
        )

        ground_truth_vertices = self._normalize_vertices(
            self.ground_truth_vertices,
            name="ground_truth_vertices",
        )
        reconstruction_vertices = self._normalize_vertices(
            self.reconstruction_vertices,
            name="reconstruction_vertices",
        )

        ground_truth_faces = self._normalize_faces(
            self.ground_truth_faces,
            vertex_count=ground_truth_vertices.shape[0],
            name="ground_truth_faces",
        )
        reconstruction_faces = self._normalize_faces(
            self.reconstruction_faces,
            vertex_count=reconstruction_vertices.shape[0],
            name="reconstruction_faces",
        )

        object.__setattr__(
            self,
            "ground_truth_vertices",
            ground_truth_vertices,
        )
        object.__setattr__(
            self,
            "ground_truth_faces",
            ground_truth_faces,
        )
        object.__setattr__(
            self,
            "reconstruction_vertices",
            reconstruction_vertices,
        )
        object.__setattr__(
            self,
            "reconstruction_faces",
            reconstruction_faces,
        )

    @staticmethod
    def _normalize_state(
        value: object,
        *,
        name: str,
        allowed: tuple[str, ...],
    ) -> str:
        normalized = str(value).strip().upper()

        if normalized not in allowed:
            raise ValueError(
                f"{name} must be one of {allowed}."
            )

        return normalized

    @staticmethod
    def _normalize_required_text(
        value: object,
        *,
        name: str,
        uppercase: bool,
    ) -> str:
        normalized = str(value).strip()

        if not normalized:
            raise ValueError(
                f"{name} must be non-blank."
            )

        if uppercase:
            normalized = normalized.upper()

        return normalized

    @staticmethod
    def _normalize_vertices(
        value: object,
        *,
        name: str,
    ) -> np.ndarray:
        vertices = np.asarray(
            value,
            dtype=np.float64,
        )

        if (
            vertices.ndim != 2
            or vertices.shape[1] != 3
            or vertices.shape[0] == 0
        ):
            raise ValueError(
                f"{name} must have shape (N, 3)."
            )

        if not np.all(
            np.isfinite(vertices)
        ):
            raise ValueError(
                f"{name} must contain only finite values."
            )

        vertices = vertices.copy()
        vertices.setflags(write=False)

        return vertices

    @staticmethod
    def _normalize_faces(
        value: object,
        *,
        vertex_count: int,
        name: str,
    ) -> tuple[tuple[int, int, int], ...]:
        try:
            raw_faces = tuple(value)
        except TypeError as exc:
            raise TypeError(
                f"{name} must be an iterable of triangles."
            ) from exc

        if not raw_faces:
            raise ValueError(
                f"{name} must not be empty."
            )

        normalized = []

        for raw_face in raw_faces:
            try:
                face = tuple(raw_face)
            except TypeError as exc:
                raise TypeError(
                    f"{name} must contain triangles."
                ) from exc

            if len(face) != 3:
                raise ValueError(
                    f"{name} must contain triangular faces."
                )

            if any(
                isinstance(index, bool)
                or not isinstance(
                    index,
                    (int, np.integer),
                )
                for index in face
            ):
                raise TypeError(
                    f"{name} indices must be integers."
                )

            triangle = tuple(
                int(index)
                for index in face
            )

            if any(
                index < 0
                or index >= vertex_count
                for index in triangle
            ):
                raise ValueError(
                    f"{name} indices must be inside vertex bounds."
                )

            normalized.append(
                triangle
            )

        return tuple(normalized)
