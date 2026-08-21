from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadHeldOutViewObservation:
    observation_id: str
    candidate_id: str
    subject_id: str
    training_view_ids: tuple[str, ...]
    held_out_view_id: str
    shared_identity_component_count: int
    identity_locked: bool
    held_out_pose_camera_only: bool
    held_out_reprojection_iod_nme: float
    held_out_reprojection_bbox_nme: float
    optimizer_success: bool
    processing_time_seconds: float
    expression_fixed_neutral: bool
    projection_model: str

    SUPPORTED_PROJECTION_MODELS = (
        "weak_perspective",
    )

    def __post_init__(self) -> None:
        for field_name in (
            "observation_id",
            "candidate_id",
            "subject_id",
            "held_out_view_id",
        ):
            value = getattr(
                self,
                field_name,
            )

            if not isinstance(value, str):
                raise TypeError(
                    f"{field_name} must be a string."
                )

            normalized = value.strip()

            if not normalized:
                raise ValueError(
                    f"{field_name} must be non-blank."
                )

            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        training_view_ids = self._normalize_view_ids(
            self.training_view_ids
        )

        if self.held_out_view_id in training_view_ids:
            raise ValueError(
                "held_out_view_id must not be present "
                "in training_view_ids."
            )

        object.__setattr__(
            self,
            "training_view_ids",
            training_view_ids,
        )

        component_count = self._normalize_positive_int(
            self.shared_identity_component_count,
            name="shared_identity_component_count",
        )
        object.__setattr__(
            self,
            "shared_identity_component_count",
            component_count,
        )

        for field_name in (
            "identity_locked",
            "held_out_pose_camera_only",
            "optimizer_success",
            "expression_fixed_neutral",
        ):
            value = getattr(
                self,
                field_name,
            )

            if not isinstance(value, bool):
                raise TypeError(
                    f"{field_name} must be boolean."
                )

        if self.identity_locked is not True:
            raise ValueError(
                "identity_locked must be True for held-out validation."
            )

        if self.held_out_pose_camera_only is not True:
            raise ValueError(
                "held_out_pose_camera_only must be True "
                "for held-out validation."
            )

        for field_name in (
            "held_out_reprojection_iod_nme",
            "held_out_reprojection_bbox_nme",
            "processing_time_seconds",
        ):
            object.__setattr__(
                self,
                field_name,
                self._normalize_nonnegative_float(
                    getattr(
                        self,
                        field_name,
                    ),
                    name=field_name,
                ),
            )

        if not isinstance(
            self.projection_model,
            str,
        ):
            raise TypeError(
                "projection_model must be a string."
            )

        projection_model = "_".join(
            self.projection_model
            .strip()
            .lower()
            .split()
        )

        if (
            projection_model
            not in self.SUPPORTED_PROJECTION_MODELS
        ):
            raise ValueError(
                "projection_model must be one of "
                f"{self.SUPPORTED_PROJECTION_MODELS}."
            )

        object.__setattr__(
            self,
            "projection_model",
            projection_model,
        )

    @property
    def training_view_count(
        self,
    ) -> int:
        return len(
            self.training_view_ids
        )

    @staticmethod
    def _normalize_view_ids(
        value: Any,
    ) -> tuple[str, ...]:
        if isinstance(value, str):
            raise TypeError(
                "training_view_ids must be an iterable of strings."
            )

        try:
            raw_values = tuple(value)
        except TypeError as exc:
            raise TypeError(
                "training_view_ids must be an iterable of strings."
            ) from exc

        if not raw_values:
            raise ValueError(
                "training_view_ids must not be empty."
            )

        normalized = []

        for item in raw_values:
            if not isinstance(item, str):
                raise TypeError(
                    "training_view_ids must contain only strings."
                )

            view_id = item.strip()

            if not view_id:
                raise ValueError(
                    "training_view_ids must contain "
                    "non-blank values."
                )

            normalized.append(view_id)

        normalized_tuple = tuple(normalized)

        if len(set(normalized_tuple)) != len(
            normalized_tuple
        ):
            raise ValueError(
                "training_view_ids must be unique."
            )

        return normalized_tuple

    @staticmethod
    def _normalize_positive_int(
        value: Any,
        *,
        name: str,
    ) -> int:
        if isinstance(value, bool) or not isinstance(
            value,
            int,
        ):
            raise TypeError(
                f"{name} must be an integer."
            )

        if value <= 0:
            raise ValueError(
                f"{name} must be positive."
            )

        return value

    @staticmethod
    def _normalize_nonnegative_float(
        value: Any,
        *,
        name: str,
    ) -> float:
        try:
            numeric = float(value)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if not isfinite(numeric) or numeric < 0.0:
            raise ValueError(
                f"{name} must be finite and nonnegative."
            )

        return numeric
