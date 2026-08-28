from __future__ import annotations

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadMetricDatasetCoverage:
    dataset_id: str

    subject_ids: tuple[str, ...]
    view_ids: tuple[str, ...]
    expressions: tuple[str, ...]
    capture_conditions: tuple[str, ...]

    same_subject_state: str
    session_relation_state: str
    scan_expression_state: str
    image_expression_state: str
    expression_compatibility: str
    scan_posture_state: str
    image_head_pose_state: str
    posture_gravity_compatibility: str

    camera_calibration_availability: str
    raw_scan_availability: str
    source_image_multiview_availability: str

    valid_facial_surface_coverage_state: str
    missing_surface_regions: tuple[str, ...]
    missing_ground_truth_states: tuple[str, ...]

    failure_count: int
    exclusion_count: int

    provenance_reference: str

    SAME_SUBJECT_STATES = (
        "VERIFIED",
        "PARTIAL",
        "UNRESOLVED",
    )

    SESSION_RELATION_STATES = (
        "SAME_SESSION_VERIFIED",
        "CROSS_SESSION_VERIFIED",
        "PARTIAL",
        "UNRESOLVED",
    )

    COMPATIBILITY_STATES = (
        "COMPATIBLE",
        "INCOMPATIBLE",
        "UNRESOLVED",
    )

    AVAILABILITY_STATES = (
        "AVAILABLE",
        "UNAVAILABLE",
        "PARTIAL",
        "UNRESOLVED",
    )

    FACIAL_SURFACE_COVERAGE_STATES = (
        "COMPLETE",
        "PARTIAL",
        "MISSING",
        "UNRESOLVED",
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "dataset_id",
            self._normalize_required_text(
                self.dataset_id,
                name="dataset_id",
                uppercase=False,
            ),
        )

        for field_name in (
            "subject_ids",
            "view_ids",
            "expressions",
            "capture_conditions",
        ):
            object.__setattr__(
                self,
                field_name,
                self._normalize_string_collection(
                    getattr(self, field_name),
                    name=field_name,
                    allow_empty=False,
                ),
            )

        for field_name in (
            "missing_surface_regions",
            "missing_ground_truth_states",
        ):
            object.__setattr__(
                self,
                field_name,
                self._normalize_string_collection(
                    getattr(self, field_name),
                    name=field_name,
                    allow_empty=True,
                ),
            )

        state_contracts = {
            "same_subject_state": self.SAME_SUBJECT_STATES,
            "session_relation_state": self.SESSION_RELATION_STATES,
            "expression_compatibility": self.COMPATIBILITY_STATES,
            "posture_gravity_compatibility": self.COMPATIBILITY_STATES,
            "camera_calibration_availability": self.AVAILABILITY_STATES,
            "raw_scan_availability": self.AVAILABILITY_STATES,
            "source_image_multiview_availability": (
                self.AVAILABILITY_STATES
            ),
            "valid_facial_surface_coverage_state": (
                self.FACIAL_SURFACE_COVERAGE_STATES
            ),
        }

        for field_name, allowed_states in state_contracts.items():
            object.__setattr__(
                self,
                field_name,
                self._normalize_state(
                    getattr(self, field_name),
                    name=field_name,
                    allowed=allowed_states,
                ),
            )

        for field_name in (
            "scan_expression_state",
            "image_expression_state",
            "scan_posture_state",
            "image_head_pose_state",
        ):
            object.__setattr__(
                self,
                field_name,
                self._normalize_required_text(
                    getattr(self, field_name),
                    name=field_name,
                    uppercase=True,
                ),
            )

        for field_name in (
            "failure_count",
            "exclusion_count",
        ):
            object.__setattr__(
                self,
                field_name,
                self._normalize_nonnegative_integer(
                    getattr(self, field_name),
                    name=field_name,
                ),
            )

        object.__setattr__(
            self,
            "provenance_reference",
            self._normalize_required_text(
                self.provenance_reference,
                name="provenance_reference",
                uppercase=False,
            ),
        )

    @property
    def subject_count(
        self,
    ) -> int:
        return len(
            self.subject_ids
        )

    @property
    def view_count(
        self,
    ) -> int:
        return len(
            self.view_ids
        )

    @staticmethod
    def _normalize_required_text(
        value: object,
        *,
        name: str,
        uppercase: bool,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{name} must be a string."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{name} must be non-blank."
            )

        if uppercase:
            normalized = normalized.upper()

        return normalized

    @classmethod
    def _normalize_state(
        cls,
        value: object,
        *,
        name: str,
        allowed: tuple[str, ...],
    ) -> str:
        normalized = cls._normalize_required_text(
            value,
            name=name,
            uppercase=True,
        )

        if normalized not in allowed:
            raise ValueError(
                f"{name} must be one of {allowed}."
            )

        return normalized

    @classmethod
    def _normalize_string_collection(
        cls,
        values: object,
        *,
        name: str,
        allow_empty: bool,
    ) -> tuple[str, ...]:
        if isinstance(
            values,
            (str, bytes),
        ):
            raise TypeError(
                f"{name} must be an iterable of strings."
            )

        try:
            raw_values = tuple(values)
        except TypeError as exc:
            raise TypeError(
                f"{name} must be an iterable of strings."
            ) from exc

        if (
            not allow_empty
            and not raw_values
        ):
            raise ValueError(
                f"{name} must not be empty."
            )

        normalized = tuple(
            cls._normalize_required_text(
                value,
                name=name,
                uppercase=False,
            )
            for value in raw_values
        )

        if len(set(normalized)) != len(normalized):
            raise ValueError(
                f"{name} must contain unique values."
            )

        return normalized

    @staticmethod
    def _normalize_nonnegative_integer(
        value: object,
        *,
        name: str,
    ) -> int:
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
        ):
            raise TypeError(
                f"{name} must be an integer."
            )

        if value < 0:
            raise ValueError(
                f"{name} must be nonnegative."
            )

        return value
