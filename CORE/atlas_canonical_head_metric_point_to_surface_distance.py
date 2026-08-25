from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadMetricPointToSurfaceDistanceResult:
    distances_mm: np.ndarray
    mean_distance_mm: float
    max_distance_mm: float

    def __post_init__(self) -> None:
        distances = np.asarray(
            self.distances_mm,
            dtype=np.float64,
        )

        if (
            distances.ndim != 1
            or distances.shape[0] == 0
        ):
            raise ValueError(
                "distances_mm must be a non-empty 1D array."
            )

        if (
            not np.all(np.isfinite(distances))
            or np.any(distances < 0.0)
        ):
            raise ValueError(
                "distances_mm must contain finite nonnegative values."
            )

        distances = distances.copy()
        distances.setflags(write=False)

        object.__setattr__(
            self,
            "distances_mm",
            distances,
        )

        for field_name in (
            "mean_distance_mm",
            "max_distance_mm",
        ):
            value = float(
                getattr(self, field_name)
            )

            if (
                not np.isfinite(value)
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


class AtlasCanonicalHeadMetricPointToSurfaceDistance:
    @classmethod
    def evaluate(
        cls,
        *,
        source_points: object,
        target_vertices: object,
        target_faces: object,
    ) -> AtlasCanonicalHeadMetricPointToSurfaceDistanceResult:
        points = cls._normalize_points(
            source_points,
            name="source_points",
        )
        vertices = cls._normalize_points(
            target_vertices,
            name="target_vertices",
        )
        faces = cls._normalize_faces(
            target_faces,
            vertex_count=vertices.shape[0],
        )

        triangles = vertices[faces]

        distances = np.asarray(
            [
                min(
                    cls._point_to_triangle_distance(
                        point,
                        triangle[0],
                        triangle[1],
                        triangle[2],
                    )
                    for triangle in triangles
                )
                for point in points
            ],
            dtype=np.float64,
        )

        return AtlasCanonicalHeadMetricPointToSurfaceDistanceResult(
            distances_mm=distances,
            mean_distance_mm=float(
                np.mean(distances)
            ),
            max_distance_mm=float(
                np.max(distances)
            ),
        )

    @staticmethod
    def _point_to_triangle_distance(
        point: np.ndarray,
        a: np.ndarray,
        b: np.ndarray,
        c: np.ndarray,
    ) -> float:
        ab = b - a
        ac = c - a
        ap = point - a

        d1 = np.dot(ab, ap)
        d2 = np.dot(ac, ap)

        if d1 <= 0.0 and d2 <= 0.0:
            return float(
                np.linalg.norm(ap)
            )

        bp = point - b
        d3 = np.dot(ab, bp)
        d4 = np.dot(ac, bp)

        if d3 >= 0.0 and d4 <= d3:
            return float(
                np.linalg.norm(bp)
            )

        vc = d1 * d4 - d3 * d2

        if (
            vc <= 0.0
            and d1 >= 0.0
            and d3 <= 0.0
        ):
            v = d1 / (d1 - d3)
            projection = a + v * ab
            return float(
                np.linalg.norm(
                    point - projection
                )
            )

        cp = point - c
        d5 = np.dot(ab, cp)
        d6 = np.dot(ac, cp)

        if d6 >= 0.0 and d5 <= d6:
            return float(
                np.linalg.norm(cp)
            )

        vb = d5 * d2 - d1 * d6

        if (
            vb <= 0.0
            and d2 >= 0.0
            and d6 <= 0.0
        ):
            w = d2 / (d2 - d6)
            projection = a + w * ac
            return float(
                np.linalg.norm(
                    point - projection
                )
            )

        va = d3 * d6 - d5 * d4

        if (
            va <= 0.0
            and (d4 - d3) >= 0.0
            and (d5 - d6) >= 0.0
        ):
            edge = c - b
            w = (
                (d4 - d3)
                / (
                    (d4 - d3)
                    + (d5 - d6)
                )
            )
            projection = b + w * edge
            return float(
                np.linalg.norm(
                    point - projection
                )
            )

        denominator = (
            va + vb + vc
        )

        if abs(denominator) <= 1e-15:
            return min(
                AtlasCanonicalHeadMetricPointToSurfaceDistance
                ._point_to_segment_distance(point, a, b),
                AtlasCanonicalHeadMetricPointToSurfaceDistance
                ._point_to_segment_distance(point, b, c),
                AtlasCanonicalHeadMetricPointToSurfaceDistance
                ._point_to_segment_distance(point, c, a),
            )

        inverse = 1.0 / denominator
        v = vb * inverse
        w = vc * inverse
        projection = (
            a
            + ab * v
            + ac * w
        )

        return float(
            np.linalg.norm(
                point - projection
            )
        )

    @staticmethod
    def _point_to_segment_distance(
        point: np.ndarray,
        a: np.ndarray,
        b: np.ndarray,
    ) -> float:
        segment = b - a
        denominator = float(
            np.dot(segment, segment)
        )

        if denominator <= 1e-30:
            return float(
                np.linalg.norm(point - a)
            )

        t = float(
            np.dot(
                point - a,
                segment,
            )
            / denominator
        )
        t = min(
            1.0,
            max(
                0.0,
                t,
            ),
        )

        projection = (
            a
            + t * segment
        )

        return float(
            np.linalg.norm(
                point - projection
            )
        )

    @staticmethod
    def _normalize_points(
        value: object,
        *,
        name: str,
    ) -> np.ndarray:
        points = np.asarray(
            value,
            dtype=np.float64,
        )

        if (
            points.ndim != 2
            or points.shape[1] != 3
            or points.shape[0] == 0
        ):
            raise ValueError(
                f"{name} must have shape (N, 3)."
            )

        if not np.all(
            np.isfinite(points)
        ):
            raise ValueError(
                f"{name} must contain only finite values."
            )

        return points.copy()

    @staticmethod
    def _normalize_faces(
        value: object,
        *,
        vertex_count: int,
    ) -> np.ndarray:
        try:
            faces = np.asarray(
                value,
                dtype=np.int64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "target_faces must contain triangular integer indices."
            ) from exc

        if (
            faces.ndim != 2
            or faces.shape[1] != 3
            or faces.shape[0] == 0
        ):
            raise ValueError(
                "target_faces must have shape (F, 3)."
            )

        if (
            np.any(faces < 0)
            or np.any(faces >= vertex_count)
        ):
            raise ValueError(
                "target_faces indices must be inside vertex bounds."
            )

        return faces
