from __future__ import annotations

import numpy as np

from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)
from CORE.atlas_portrait_contact_plane_projection_result import (
    AtlasPortraitContactPlaneProjectionResult,
)


class AtlasPortraitContactPlaneProjector:
    """
    Projects a regular-grid frontal face surface onto a
    contact-plane distance representation.

    The frontal contact plane is placed at the maximum
    surface Z coordinate. Every grid point stores its
    nonnegative distance behind that plane.

    When multiple points share the maximum Z value, the
    first point in row-major order is selected as the
    deterministic contact index.

    It performs no reconstruction, relief compression,
    rendering, triangulation, repair, or mesh generation.
    """

    PROJECTION_METADATA = {
        "projection_mode": "frontal_contact_plane",
        "contact_policy": "first_maximum_z_row_major",
        "distance_direction": (
            "contact_plane_z_minus_surface_z"
        ),
    }

    @classmethod
    def project(
        cls,
        surface: AtlasParametricFaceSurface,
    ) -> AtlasPortraitContactPlaneProjectionResult:
        if not isinstance(
            surface,
            AtlasParametricFaceSurface,
        ):
            raise TypeError(
                "surface must be an "
                "AtlasParametricFaceSurface instance."
            )

        z_coordinates = surface.z_coordinates

        contact_flat_index = int(
            np.argmax(
                z_coordinates,
            )
        )

        contact_row, contact_column = np.unravel_index(
            contact_flat_index,
            surface.shape,
        )

        contact_plane_z = float(
            z_coordinates[
                contact_row,
                contact_column,
            ]
        )

        distance_to_plane = (
            contact_plane_z
            - z_coordinates
        ).astype(
            np.float64,
            copy=True,
        )

        distance_to_plane = np.maximum(
            distance_to_plane,
            0.0,
        )

        maximum_distance = float(
            np.max(
                distance_to_plane,
            )
        )

        return AtlasPortraitContactPlaneProjectionResult(
            distance_to_plane=distance_to_plane,
            contact_plane_z=contact_plane_z,
            contact_row=int(
                contact_row,
            ),
            contact_column=int(
                contact_column,
            ),
            maximum_distance=maximum_distance,
            source_shape=surface.shape,
            metadata=cls.PROJECTION_METADATA,
        )
