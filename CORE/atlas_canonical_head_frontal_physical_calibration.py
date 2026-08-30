from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class AtlasCanonicalHeadFrontalPhysicalCalibrationResult:
    axis_scale_x: float
    axis_scale_y: float
    horizontal_scale_factor: float
    source_point_count: int
    target_coordinate_space: str
    calibration_kind: str
    calibration_provenance: str


class AtlasCanonicalHeadFrontalPhysicalCalibration:
    """
    Derives a frontal physical-axis calibration from matched
    canonical X/Y points and normalized-image target points.

    The normalized image targets are first converted into an
    isotropic square-pixel coordinate space using one common
    denominator:

        max(image_width - 1, image_height - 1)

    Independent least-squares X and Y scale estimates are then
    solved. Their ratio is reported as the horizontal physical
    scale factor.

    This class performs no identity fitting, FLAME deformation,
    relief generation, STL export, likeness scoring, production
    approval, or Phase 9 authorization.
    """

    CALIBRATION_KIND = (
        "frontal_square_pixel_axis_scale"
    )
    TARGET_COORDINATE_SPACE = (
        "square_pixel_isotropic"
    )
    CALIBRATION_PROVENANCE = (
        "atlas_canonical_head_frontal_physical_calibration:v1"
    )
    _MINIMUM_SPREAD = 1.0e-15

    @classmethod
    def derive(
        cls,
        *,
        source_points_xy: Any,
        target_points_normalized: Any,
        image_width: Any,
        image_height: Any,
    ) -> AtlasCanonicalHeadFrontalPhysicalCalibrationResult:
        source = cls._points(
            source_points_xy,
            name="source_points_xy",
        )
        target = cls._points(
            target_points_normalized,
            name="target_points_normalized",
        )

        if source.shape != target.shape:
            raise ValueError(
                "source_points_xy and "
                "target_points_normalized must have "
                "matching shapes"
            )

        width = cls._image_dimension(
            image_width,
            name="image_width",
        )
        height = cls._image_dimension(
            image_height,
            name="image_height",
        )

        isotropic_extent = float(
            max(
                width - 1,
                height - 1,
            )
        )

        target_square = np.column_stack(
            (
                target[:, 0]
                * float(width - 1)
                / isotropic_extent,
                target[:, 1]
                * float(height - 1)
                / isotropic_extent,
            )
        )

        scale_x = cls._axis_scale(
            source[:, 0],
            target_square[:, 0],
            axis_name="x",
        )
        scale_y = cls._axis_scale(
            source[:, 1],
            target_square[:, 1],
            axis_name="y",
        )

        if abs(scale_y) <= cls._MINIMUM_SPREAD:
            raise ValueError(
                "derived Y scale is degenerate"
            )

        horizontal_scale_factor = float(
            scale_x / scale_y
        )

        return (
            AtlasCanonicalHeadFrontalPhysicalCalibrationResult(
                axis_scale_x=float(scale_x),
                axis_scale_y=float(scale_y),
                horizontal_scale_factor=(
                    horizontal_scale_factor
                ),
                source_point_count=int(
                    source.shape[0]
                ),
                target_coordinate_space=(
                    cls.TARGET_COORDINATE_SPACE
                ),
                calibration_kind=(
                    cls.CALIBRATION_KIND
                ),
                calibration_provenance=(
                    cls.CALIBRATION_PROVENANCE
                ),
            )
        )

    @classmethod
    def apply_to_canonical_mesh(
        cls,
        *,
        canonical_mesh: Any,
        horizontal_scale_factor: Any,
        calibration_provenance: Any,
    ) -> dict[str, Any]:
        if not isinstance(
            canonical_mesh,
            dict,
        ):
            raise TypeError(
                "canonical_mesh must be a mapping"
            )

        try:
            factor = float(
                horizontal_scale_factor
            )
        except (
            TypeError,
            ValueError,
            OverflowError,
        ) as exc:
            raise ValueError(
                "horizontal_scale_factor must be "
                "positive and finite"
            ) from exc

        if (
            not np.isfinite(factor)
            or factor <= 0.0
        ):
            raise ValueError(
                "horizontal_scale_factor must be "
                "positive and finite"
            )

        provenance = str(
            calibration_provenance
        ).strip()

        if not provenance:
            raise ValueError(
                "calibration_provenance must not be empty"
            )

        raw_vertices = canonical_mesh.get(
            "vertices"
        )

        try:
            vertices = tuple(
                tuple(
                    float(value)
                    for value in point
                )
                for point in raw_vertices
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "canonical_mesh vertices must be numeric"
            ) from exc

        if (
            len(vertices) < 3
            or any(
                len(point) != 3
                for point in vertices
            )
            or not all(
                np.isfinite(value)
                for point in vertices
                for value in point
            )
        ):
            raise ValueError(
                "canonical_mesh vertices must have "
                "shape (N, 3), N >= 3"
            )

        raw_faces = canonical_mesh.get(
            "faces"
        )

        try:
            faces = tuple(
                tuple(
                    int(value)
                    for value in face
                )
                for face in raw_faces
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "canonical_mesh faces must be integer "
                "triangle indices"
            ) from exc

        if (
            not faces
            or any(
                len(face) != 3
                for face in faces
            )
            or any(
                index < 0
                or index >= len(vertices)
                for face in faces
                for index in face
            )
        ):
            raise ValueError(
                "canonical_mesh faces must contain "
                "valid triangle indices"
            )

        calibrated_vertices = tuple(
            (
                point[0] * factor,
                point[1],
                point[2],
            )
            for point in vertices
        )

        result = dict(
            canonical_mesh
        )

        result["vertices"] = (
            calibrated_vertices
        )
        result["faces"] = faces

        result[
            "frontal_physical_calibration"
        ] = {
            "horizontal_scale_factor": factor,
            "axis_policy": "x_only_about_origin",
            "calibration_provenance": provenance,
        }

        return result

    @classmethod
    def _axis_scale(
        cls,
        source: np.ndarray,
        target: np.ndarray,
        *,
        axis_name: str,
    ) -> float:
        source_centered = (
            source
            - float(source.mean())
        )
        target_centered = (
            target
            - float(target.mean())
        )

        denominator = float(
            np.dot(
                source_centered,
                source_centered,
            )
        )

        if denominator <= cls._MINIMUM_SPREAD:
            raise ValueError(
                f"source {axis_name} spread is degenerate"
            )

        return float(
            np.dot(
                source_centered,
                target_centered,
            )
            / denominator
        )

    @staticmethod
    def _points(
        value: Any,
        *,
        name: str,
    ) -> np.ndarray:
        try:
            result = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric"
            ) from exc

        if (
            result.ndim != 2
            or result.shape[1] != 2
            or result.shape[0] < 2
        ):
            raise ValueError(
                f"{name} must have shape (N, 2) "
                "with at least two points"
            )

        if not np.isfinite(
            result
        ).all():
            raise ValueError(
                f"{name} contains non-finite values"
            )

        return result.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _image_dimension(
        value: Any,
        *,
        name: str,
    ) -> int:
        if isinstance(
            value,
            (
                bool,
                np.bool_,
            ),
        ):
            raise ValueError(
                f"{name} must be an integer >= 2"
            )

        try:
            numeric = int(value)
        except (
            TypeError,
            ValueError,
            OverflowError,
        ) as exc:
            raise ValueError(
                f"{name} must be an integer >= 2"
            ) from exc

        if numeric != value or numeric < 2:
            raise ValueError(
                f"{name} must be an integer >= 2"
            )

        return numeric
