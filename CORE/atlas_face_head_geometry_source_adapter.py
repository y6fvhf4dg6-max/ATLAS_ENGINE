from __future__ import annotations

from typing import Any

from CORE.atlas_geometry_source_adapter import (
    AtlasGeometrySourceAdapter,
)
from CORE.atlas_geometry_source_result import (
    AtlasGeometrySourceResult,
)
from CORE.atlas_portrait_landmark_result import (
    AtlasPortraitLandmarkResult,
)


class AtlasFaceHeadGeometrySourceAdapter(
    AtlasGeometrySourceAdapter,
):
    def adapt(
        self,
        source: Any,
    ) -> AtlasGeometrySourceResult:
        if not isinstance(
            source,
            AtlasPortraitLandmarkResult,
        ):
            raise TypeError(
                "source must be an "
                "AtlasPortraitLandmarkResult"
            )

        landmarks = {
            "_".join(
                str(name).strip().lower().split()
            ): (
                float(coordinates[0]),
                float(coordinates[1]),
            )
            for name, coordinates
            in source.landmarks.items()
        }

        points = tuple(
            (
                coordinates[0],
                coordinates[1],
                0.0,
            )
            for coordinates in landmarks.values()
        )

        local_bounds = (
            (
                min(point[0] for point in points),
                min(point[1] for point in points),
                0.0,
            ),
            (
                max(point[0] for point in points),
                max(point[1] for point in points),
                0.0,
            ),
        )

        anchors = {
            name: (
                coordinates[0],
                coordinates[1],
                0.0,
            )
            for name, coordinates
            in landmarks.items()
        }

        result = AtlasGeometrySourceResult(
            normalized_geometry={
                "geometry_kind": (
                    "face_head_landmarks"
                ),
                "coordinate_space": (
                    "normalized_image_2d"
                ),
                "image_width": (
                    source.image_width
                ),
                "image_height": (
                    source.image_height
                ),
                "landmarks": landmarks,
                "provider_id": (
                    source.provider_id
                ),
            },
            local_bounds=local_bounds,
            anchors=anchors,
            confidence=source.confidence,
            provenance=(
                "portrait_landmark_provider:"
                f"{source.provider_id}"
            ),
            supported_projection_modes=(
                "flat_plane",
            ),
        )

        return self.validate_result(
            result
        )
