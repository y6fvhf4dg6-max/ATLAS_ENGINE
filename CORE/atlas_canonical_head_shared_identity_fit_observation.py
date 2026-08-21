from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadSharedIdentityFitObservation:
    observation_id: str
    candidate_id: str
    subject_id: str
    view_ids: tuple[str, ...]
    shared_identity_component_count: int
    mean_reprojection_iod_nme: float
    mean_reprojection_bbox_nme: float
    per_view_reprojection_iod_nme: tuple[float, ...]
    identity_coefficient_l2_norm: float
    identity_bound_hit_count: int
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
        ):
            value = getattr(
                self,
                field_name,
            )

            if not isinstance(
                value,
                str,
            ):
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

        view_ids = self._normalize_view_ids(
            self.view_ids
        )
        object.__setattr__(
            self,
            "view_ids",
            view_ids,
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
            "mean_reprojection_iod_nme",
            "mean_reprojection_bbox_nme",
            "identity_coefficient_l2_norm",
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

        per_view = tuple(
            self._normalize_nonnegative_float(
                value,
                name="per_view_reprojection_iod_nme",
            )
            for value in self.per_view_reprojection_iod_nme
        )

        if len(
            per_view
        ) != len(
            view_ids
        ):
            raise ValueError(
                "per_view_reprojection_iod_nme count "
                "must match view_ids count."
            )

        object.__setattr__(
            self,
            "per_view_reprojection_iod_nme",
            per_view,
        )

        bound_hit_count = self._normalize_nonnegative_int(
            self.identity_bound_hit_count,
            name="identity_bound_hit_count",
        )

        if bound_hit_count > component_count:
            raise ValueError(
                "identity_bound_hit_count must not exceed "
                "shared_identity_component_count."
            )

        object.__setattr__(
            self,
            "identity_bound_hit_count",
            bound_hit_count,
        )

        for field_name in (
            "optimizer_success",
            "expression_fixed_neutral",
        ):
            value = getattr(
                self,
                field_name,
            )

            if not isinstance(
                value,
                bool,
            ):
                raise TypeError(
                    f"{field_name} must be boolean."
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
    def view_count(
        self,
    ) -> int:
        return len(
            self.view_ids
        )

    @staticmethod
    def _normalize_view_ids(
        value: Any,
    ) -> tuple[str, ...]:
        if isinstance(
            value,
            str,
        ):
            raise TypeError(
                "view_ids must be an iterable of strings."
            )

        try:
            raw_values = tuple(
                value
            )
        except TypeError as exc:
            raise TypeError(
                "view_ids must be an iterable of strings."
            ) from exc

        if not raw_values:
            raise ValueError(
                "view_ids must not be empty."
            )

        normalized = []

        for item in raw_values:
            if not isinstance(
                item,
                str,
            ):
                raise TypeError(
                    "view_ids must contain only strings."
                )

            view_id = item.strip()

            if not view_id:
                raise ValueError(
                    "view_ids must contain non-blank values."
                )

            normalized.append(
                view_id
            )

        normalized_tuple = tuple(
            normalized
        )

        if len(
            set(
                normalized_tuple
            )
        ) != len(
            normalized_tuple
        ):
            raise ValueError(
                "view_ids must be unique."
            )

        return normalized_tuple

    @staticmethod
    def _normalize_positive_int(
        value: Any,
        *,
        name: str,
    ) -> int:
        if isinstance(
            value,
            bool,
        ) or not isinstance(
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
    def _normalize_nonnegative_int(
        value: Any,
        *,
        name: str,
    ) -> int:
        if isinstance(
            value,
            bool,
        ) or not isinstance(
            value,
            int,
        ):
            raise TypeError(
                f"{name} must be an integer."
            )

        if value < 0:
            raise ValueError(
                f"{name} must be nonnegative."
            )

        return value

    @staticmethod
    def _normalize_nonnegative_float(
        value: Any,
        *,
        name: str,
    ) -> float:
        try:
            numeric = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if not isfinite(
            numeric
        ) or numeric < 0.0:
            raise ValueError(
                f"{name} must be finite and nonnegative."
            )

        return numeric
