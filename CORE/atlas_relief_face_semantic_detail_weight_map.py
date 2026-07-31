from __future__ import annotations

from collections.abc import Mapping, Sequence
import numbers

import numpy as np


class AtlasReliefFaceSemanticDetailWeightMap:
    """Build a soft semantic confidence map for portrait detail normals.

    The map preserves useful face-interior detail while suppressing:

    - glasses and eye-frame regions,
    - nostril and nose-under regions,
    - philtrum and upper-lip regions,
    - lateral face boundaries,
    - subject-mask boundaries,
    - neck and torso regions.

    ``face_bounds`` uses inclusive coordinates:

        (top, bottom, left, right)
    """

    @staticmethod
    def build(
        subject_mask: np.ndarray,
        *,
        face_bounds: Sequence[int],
        glasses_suppression_strength: float = 0.90,
        nostril_suppression_strength: float = 0.90,
        philtrum_suppression_strength: float = 0.90,
        boundary_suppression_strength: float = 0.90,
        boundary_width: int = 6,
        landmark_regions: Mapping[str, np.ndarray] | None = None,
    ) -> np.ndarray:
        mask = np.asarray(
            subject_mask,
            dtype=np.float64,
        )

        AtlasReliefFaceSemanticDetailWeightMap._validate_subject_mask(
            mask
        )

        rows, columns = mask.shape

        (
            top,
            bottom,
            left,
            right,
        ) = AtlasReliefFaceSemanticDetailWeightMap._validate_face_bounds(
            face_bounds,
            rows=rows,
            columns=columns,
        )

        glasses_strength = (
            AtlasReliefFaceSemanticDetailWeightMap._validate_unit_strength(
                glasses_suppression_strength,
                name="glasses_suppression_strength",
            )
        )
        nostril_strength = (
            AtlasReliefFaceSemanticDetailWeightMap._validate_unit_strength(
                nostril_suppression_strength,
                name="nostril_suppression_strength",
            )
        )
        philtrum_strength = (
            AtlasReliefFaceSemanticDetailWeightMap._validate_unit_strength(
                philtrum_suppression_strength,
                name="philtrum_suppression_strength",
            )
        )
        boundary_strength = (
            AtlasReliefFaceSemanticDetailWeightMap._validate_unit_strength(
                boundary_suppression_strength,
                name="boundary_suppression_strength",
            )
        )

        width = (
            AtlasReliefFaceSemanticDetailWeightMap._validate_boundary_width(
                boundary_width
            )
        )

        if landmark_regions is not None:
            validated_regions = (
                AtlasReliefFaceSemanticDetailWeightMap
                ._validate_landmark_regions(
                    landmark_regions,
                    shape=mask.shape,
                )
            )

            return (
                AtlasReliefFaceSemanticDetailWeightMap
                ._build_from_landmark_regions(
                    subject_mask=mask,
                    landmark_regions=validated_regions,
                    glasses_suppression_strength=glasses_strength,
                    nostril_suppression_strength=nostril_strength,
                    philtrum_suppression_strength=philtrum_strength,
                    boundary_suppression_strength=boundary_strength,
                )
            )

        row_grid, column_grid = np.mgrid[
            0:rows,
            0:columns,
        ]

        face_height = float(
            bottom - top
        )
        face_width = float(
            right - left
        )

        center_x = 0.5 * (
            left + right
        )
        center_y = top + 0.48 * face_height

        radius_x = max(
            0.50 * face_width,
            1.0,
        )
        radius_y = max(
            0.60 * face_height,
            1.0,
        )

        normalized_x = (
            column_grid - center_x
        ) / radius_x

        normalized_y = (
            row_grid - center_y
        ) / radius_y

        face_envelope = np.exp(
            -0.95
            * (
                normalized_x * normalized_x
                + normalized_y * normalized_y
            )
        )

        face_bounds_mask = np.zeros(
            (rows, columns),
            dtype=np.float64,
        )
        face_bounds_mask[
            top:bottom + 1,
            left:right + 1,
        ] = 1.0

        glasses_envelope = (
            AtlasReliefFaceSemanticDetailWeightMap._gaussian_region(
                row_grid=row_grid,
                column_grid=column_grid,
                center_y=top + 0.37 * face_height,
                center_x=center_x,
                sigma_y=max(
                    0.075 * face_height,
                    1.0,
                ),
                sigma_x=max(
                    0.34 * face_width,
                    1.0,
                ),
            )
        )

        nostril_envelope = (
            AtlasReliefFaceSemanticDetailWeightMap._gaussian_region(
                row_grid=row_grid,
                column_grid=column_grid,
                center_y=top + 0.61 * face_height,
                center_x=center_x,
                sigma_y=max(
                    0.050 * face_height,
                    1.0,
                ),
                sigma_x=max(
                    0.13 * face_width,
                    1.0,
                ),
            )
        )

        philtrum_envelope = (
            AtlasReliefFaceSemanticDetailWeightMap._gaussian_region(
                row_grid=row_grid,
                column_grid=column_grid,
                center_y=top + 0.70 * face_height,
                center_x=center_x,
                sigma_y=max(
                    0.070 * face_height,
                    1.0,
                ),
                sigma_x=max(
                    0.11 * face_width,
                    1.0,
                ),
            )
        )

        lateral_distance = np.abs(
            column_grid - center_x
        ) / max(
            0.5 * face_width,
            1.0,
        )

        lateral_suppression = np.clip(
            (
                lateral_distance - 0.72
            ) / 0.28,
            0.0,
            1.0,
        )

        lower_face_start = (
            top + 0.82 * face_height
        )

        lower_taper = np.ones(
            (rows, columns),
            dtype=np.float64,
        )

        lower_region = (
            row_grid > lower_face_start
        )

        lower_taper[
            lower_region
        ] = np.clip(
            (
                bottom
                - row_grid[lower_region]
            )
            / max(
                bottom - lower_face_start,
                1.0,
            ),
            0.0,
            1.0,
        )

        subject = np.clip(
            mask,
            0.0,
            1.0,
        )

        boundary_distance = (
            AtlasReliefFaceSemanticDetailWeightMap._distance_from_zero(
                subject > 0.0,
                maximum_distance=width,
            )
        )

        boundary_factor = np.clip(
            boundary_distance / float(width),
            0.0,
            1.0,
        )

        boundary_weight = (
            1.0
            - boundary_strength
            * (
                1.0 - boundary_factor
            )
        )

        result = (
            face_envelope
            * face_bounds_mask
            * subject
            * lower_taper
            * boundary_weight
            * (
                1.0
                - boundary_strength
                * lateral_suppression
            )
            * (
                1.0
                - glasses_strength
                * glasses_envelope
            )
            * (
                1.0
                - nostril_strength
                * nostril_envelope
            )
            * (
                1.0
                - philtrum_strength
                * philtrum_envelope
            )
        )

        result[
            row_grid > bottom
        ] = 0.0

        return np.asarray(
            np.clip(
                result,
                0.0,
                1.0,
            ),
            dtype=np.float64,
        )

    @staticmethod
    def _build_from_landmark_regions(
        *,
        subject_mask: np.ndarray,
        landmark_regions: Mapping[str, np.ndarray],
        glasses_suppression_strength: float,
        nostril_suppression_strength: float,
        philtrum_suppression_strength: float,
        boundary_suppression_strength: float,
    ) -> np.ndarray:
        subject = np.clip(
            subject_mask,
            0.0,
            1.0,
        )

        face_interior = landmark_regions[
            "face_interior"
        ]
        face_boundary = landmark_regions[
            "face_boundary_falloff"
        ]

        eye_glasses = landmark_regions[
            "eye_glasses"
        ]
        nose_base = landmark_regions[
            "nose_base"
        ]
        philtrum = landmark_regions[
            "philtrum"
        ]
        upper_lip = landmark_regions[
            "upper_lip"
        ]

        boundary_weight = np.clip(
            1.0
            - boundary_suppression_strength
            * face_boundary,
            0.0,
            1.0,
        )

        glasses_weight = np.clip(
            1.0
            - glasses_suppression_strength
            * eye_glasses,
            0.0,
            1.0,
        )

        nostril_weight = np.clip(
            1.0
            - nostril_suppression_strength
            * nose_base,
            0.0,
            1.0,
        )

        philtrum_region = np.maximum(
            philtrum,
            upper_lip,
        )

        philtrum_weight = np.clip(
            1.0
            - philtrum_suppression_strength
            * philtrum_region,
            0.0,
            1.0,
        )

        result = (
            subject
            * face_interior
            * boundary_weight
            * glasses_weight
            * nostril_weight
            * philtrum_weight
        )

        return np.asarray(
            np.clip(
                result,
                0.0,
                1.0,
            ),
            dtype=np.float64,
        )

    @staticmethod
    def _validate_landmark_regions(
        landmark_regions: Mapping[str, np.ndarray],
        *,
        shape: tuple[int, int],
    ) -> dict[str, np.ndarray]:
        if not isinstance(
            landmark_regions,
            Mapping,
        ):
            raise TypeError(
                "landmark_regions must be a mapping"
            )

        required_names = (
            "eye_glasses",
            "nose_bridge",
            "nose_body",
            "nose_base",
            "philtrum",
            "upper_lip",
            "lower_lip",
            "left_cheek",
            "right_cheek",
            "chin",
            "face_interior",
            "face_boundary_falloff",
        )

        validated: dict[str, np.ndarray] = {}

        for region_name in required_names:
            if region_name not in landmark_regions:
                raise ValueError(
                    "landmark_regions is missing required "
                    f"region: {region_name}"
                )

            region = np.asarray(
                landmark_regions[region_name],
                dtype=np.float64,
            )

            if region.shape != shape:
                raise ValueError(
                    f"landmark region {region_name!r} "
                    f"must have shape {shape}"
                )

            if not np.all(np.isfinite(region)):
                raise ValueError(
                    f"landmark region {region_name!r} "
                    "must contain only finite values"
                )

            if (
                np.any(region < 0.0)
                or np.any(region > 1.0)
            ):
                raise ValueError(
                    f"landmark region {region_name!r} "
                    "must contain values between 0 and 1"
                )

            validated[region_name] = (
                np.ascontiguousarray(
                    region,
                    dtype=np.float64,
                )
            )

        return validated

    @staticmethod
    def _validate_subject_mask(
        subject_mask: np.ndarray,
    ) -> None:
        if subject_mask.ndim != 2:
            raise ValueError(
                "subject_mask must be a two-dimensional array"
            )

        if not np.all(
            np.isfinite(subject_mask)
        ):
            raise ValueError(
                "subject_mask must contain only finite values"
            )

    @staticmethod
    def _validate_face_bounds(
        face_bounds: Sequence[int],
        *,
        rows: int,
        columns: int,
    ) -> tuple[int, int, int, int]:
        if (
            not isinstance(
                face_bounds,
                Sequence,
            )
            or isinstance(
                face_bounds,
                (str, bytes),
            )
            or len(face_bounds) != 4
        ):
            raise ValueError(
                "face_bounds must contain "
                "(top, bottom, left, right)"
            )

        try:
            top, bottom, left, right = (
                int(value)
                for value in face_bounds
            )
        except (
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                "face_bounds must contain integer coordinates"
            ) from error

        if (
            top < 0
            or bottom < 0
            or left < 0
            or right < 0
            or top >= rows
            or bottom >= rows
            or left >= columns
            or right >= columns
            or bottom <= top
            or right <= left
        ):
            raise ValueError(
                "face_bounds must define a valid region "
                "inside the subject_mask"
            )

        return (
            top,
            bottom,
            left,
            right,
        )

    @staticmethod
    def _validate_unit_strength(
        value: float,
        *,
        name: str,
    ) -> float:
        numeric_value = float(
            value
        )

        if (
            not np.isfinite(numeric_value)
            or numeric_value < 0.0
            or numeric_value > 1.0
        ):
            raise ValueError(
                f"{name} must be finite and between 0 and 1"
            )

        return numeric_value

    @staticmethod
    def _validate_boundary_width(
        boundary_width: int,
    ) -> int:
        if (
            isinstance(
                boundary_width,
                bool,
            )
            or not isinstance(
                boundary_width,
                numbers.Integral,
            )
        ):
            raise ValueError(
                "boundary_width must be a positive integer"
            )

        width = int(
            boundary_width
        )

        if width <= 0:
            raise ValueError(
                "boundary_width must be a positive integer"
            )

        return width

    @staticmethod
    def _gaussian_region(
        *,
        row_grid: np.ndarray,
        column_grid: np.ndarray,
        center_y: float,
        center_x: float,
        sigma_y: float,
        sigma_x: float,
    ) -> np.ndarray:
        exponent = (
            (
                (
                    row_grid - center_y
                ) / sigma_y
            ) ** 2
            + (
                (
                    column_grid - center_x
                ) / sigma_x
            ) ** 2
        )

        return np.exp(
            -0.5 * exponent
        )

    @staticmethod
    def _distance_from_zero(
        active_mask: np.ndarray,
        *,
        maximum_distance: int,
    ) -> np.ndarray:
        distance = np.zeros(
            active_mask.shape,
            dtype=np.float64,
        )

        current = active_mask.astype(
            bool,
            copy=True,
        )

        for step in range(
            1,
            maximum_distance + 1,
        ):
            eroded = (
                current
                & np.roll(
                    current,
                    1,
                    axis=0,
                )
                & np.roll(
                    current,
                    -1,
                    axis=0,
                )
                & np.roll(
                    current,
                    1,
                    axis=1,
                )
                & np.roll(
                    current,
                    -1,
                    axis=1,
                )
            )

            eroded[0, :] = False
            eroded[-1, :] = False
            eroded[:, 0] = False
            eroded[:, -1] = False

            newly_interior = (
                current
                & ~eroded
            )

            distance[
                newly_interior
            ] = float(
                step
            )

            current = eroded

            if not np.any(
                current
            ):
                break

        distance[
            current
        ] = float(
            maximum_distance
        )

        return distance
