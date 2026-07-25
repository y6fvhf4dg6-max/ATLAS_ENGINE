import math

import pytest

from CORE.atlas_landmark_geometry_mesher import (
    AtlasLandmarkGeometryMesher,
)
from CORE.atlas_lighthouse_builder import (
    AtlasLighthouseGeometry,
)


def test_lighthouse_uses_regular_radial_rings_from_irregular_footprint():
    geometry = AtlasLighthouseGeometry(
        footprint=(
            (0.0, 0.0),
            (8.0, 0.0),
            (8.0, 3.0),
            (5.0, 3.0),
            (5.0, 6.0),
            (0.0, 6.0),
        ),
        height_m=35.0,
    )

    mesh = AtlasLandmarkGeometryMesher.build(
        geometry
    )

    rings = mesh["rings"]

    assert len(rings) >= 5

    point_counts = {
        len(ring)
        for ring in rings
    }

    assert point_counts == {16}

    for ring in rings:
        center_x = sum(point[0] for point in ring) / len(ring)
        center_y = sum(point[1] for point in ring) / len(ring)

        radii = [
            math.hypot(
                point[0] - center_x,
                point[1] - center_y,
            )
            for point in ring
        ]

        assert max(radii) - min(radii) == pytest.approx(
            0.0,
            abs=1e-6,
        )
