from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Integral


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadBenchmarkMeasurementObservation:
    measurement_id: str
    candidate_id: str
    subject_id: str

    view_count: int
    landmarks_per_view: int

    mean_reprojection_iod_nme: float
    mean_reprojection_bbox_nme: float
    cross_view_identity_shape_nme: float

    focal_identifiable: bool
    ground_truth_3d_available: bool
    volumetric_identity_proven: bool

    processing_time_seconds: float

    def __post_init__(self) -> None:
        for field_name in (
            "measurement_id",
            "candidate_id",
            "subject_id",
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

        for field_name in (
            "view_count",
            "landmarks_per_view",
        ):
            value = getattr(
                self,
                field_name,
            )

            if (
                isinstance(value, bool)
                or not isinstance(
                    value,
                    Integral,
                )
            ):
                raise TypeError(
                    f"{field_name} must be an integer."
                )

            normalized = int(
                value
            )

            if normalized <= 0:
                raise ValueError(
                    f"{field_name} must be greater than zero."
                )

            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        for field_name in (
            "mean_reprojection_iod_nme",
            "mean_reprojection_bbox_nme",
            "cross_view_identity_shape_nme",
            "processing_time_seconds",
        ):
            try:
                value = float(
                    getattr(
                        self,
                        field_name,
                    )
                )
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise ValueError(
                    f"{field_name} must be numeric."
                ) from exc

            if (
                not math.isfinite(value)
                or value < 0.0
            ):
                raise ValueError(
                    f"{field_name} must be finite and nonnegative."
                )

            object.__setattr__(
                self,
                field_name,
                value,
            )

        for field_name in (
            "focal_identifiable",
            "ground_truth_3d_available",
            "volumetric_identity_proven",
        ):
            if not isinstance(
                getattr(
                    self,
                    field_name,
                ),
                bool,
            ):
                raise TypeError(
                    f"{field_name} must be boolean."
                )

        if (
            self.volumetric_identity_proven
            and not self.ground_truth_3d_available
        ):
            raise ValueError(
                "volumetric_identity_proven requires "
                "ground_truth_3d_available."
            )
