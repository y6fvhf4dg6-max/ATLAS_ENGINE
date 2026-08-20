from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Integral


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadCameraObservation:
    camera_id: str
    projection_mode: str
    image_width: int
    image_height: int
    focal_length_px: float
    principal_point_x_px: float
    principal_point_y_px: float

    SUPPORTED_PROJECTION_MODES = (
        "perspective",
    )

    def __post_init__(self) -> None:
        camera_id = self._normalize_identifier(
            self.camera_id,
            name="camera_id",
        )
        projection_mode = self._normalize_projection_mode(
            self.projection_mode,
        )
        image_width = self._normalize_dimension(
            self.image_width,
            name="image_width",
        )
        image_height = self._normalize_dimension(
            self.image_height,
            name="image_height",
        )
        focal_length_px = self._normalize_positive_numeric(
            self.focal_length_px,
            name="focal_length_px",
        )
        principal_point_x_px = self._normalize_finite_numeric(
            self.principal_point_x_px,
            name="principal_point_x_px",
        )
        principal_point_y_px = self._normalize_finite_numeric(
            self.principal_point_y_px,
            name="principal_point_y_px",
        )

        if not (
            0.0
            <= principal_point_x_px
            < float(image_width)
        ):
            raise ValueError(
                "principal_point_x_px must be inside image bounds."
            )

        if not (
            0.0
            <= principal_point_y_px
            < float(image_height)
        ):
            raise ValueError(
                "principal_point_y_px must be inside image bounds."
            )

        object.__setattr__(
            self,
            "camera_id",
            camera_id,
        )
        object.__setattr__(
            self,
            "projection_mode",
            projection_mode,
        )
        object.__setattr__(
            self,
            "image_width",
            image_width,
        )
        object.__setattr__(
            self,
            "image_height",
            image_height,
        )
        object.__setattr__(
            self,
            "focal_length_px",
            focal_length_px,
        )
        object.__setattr__(
            self,
            "principal_point_x_px",
            principal_point_x_px,
        )
        object.__setattr__(
            self,
            "principal_point_y_px",
            principal_point_y_px,
        )

    @property
    def principal_point_normalized(
        self,
    ) -> tuple[float, float]:
        return (
            self.principal_point_x_px
            / (
                self.image_width
                - 1
            ),
            self.principal_point_y_px
            / (
                self.image_height
                - 1
            ),
        )

    @staticmethod
    def _normalize_identifier(
        value: object,
        *,
        name: str,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{name} must be a string."
            )

        normalized = "_".join(
            value.strip().lower().split()
        )

        if not normalized:
            raise ValueError(
                f"{name} must not be blank."
            )

        return normalized

    @classmethod
    def _normalize_projection_mode(
        cls,
        value: object,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "projection_mode must be a string."
            )

        normalized = value.strip().lower()

        if normalized not in cls.SUPPORTED_PROJECTION_MODES:
            raise ValueError(
                "projection_mode is not supported."
            )

        return normalized

    @staticmethod
    def _normalize_dimension(
        value: object,
        *,
        name: str,
    ) -> int:
        if (
            isinstance(value, bool)
            or not isinstance(
                value,
                Integral,
            )
        ):
            raise TypeError(
                f"{name} must be an integer."
            )

        normalized = int(
            value
        )

        if normalized <= 0:
            raise ValueError(
                f"{name} must be greater than zero."
            )

        return normalized

    @staticmethod
    def _normalize_finite_numeric(
        value: object,
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

        if not math.isfinite(
            numeric
        ):
            raise ValueError(
                f"{name} must be finite."
            )

        return numeric

    @classmethod
    def _normalize_positive_numeric(
        cls,
        value: object,
        *,
        name: str,
    ) -> float:
        numeric = cls._normalize_finite_numeric(
            value,
            name=name,
        )

        if numeric <= 0.0:
            raise ValueError(
                f"{name} must be greater than zero."
            )

        return numeric
