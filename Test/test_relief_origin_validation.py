import numpy as np
import pytest

from CORE.atlas_relief_mesh_builder import (
    AtlasReliefMeshBuilder,
)


@pytest.mark.parametrize(
    "parameter",
    [
        "origin_x",
        "origin_y",
        "origin_z",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        np.nan,
        np.inf,
        -np.inf,
    ],
)
def test_rejects_non_finite_origin_values(
    parameter,
    value,
):
    arguments = {
        "height_map": [
            [0.0, 0.5],
            [1.0, 0.25],
        ],
        "width_mm": 8.0,
        "depth_mm": 6.0,
        "origin_x": 0.0,
        "origin_y": 0.0,
        "origin_z": 0.0,
    }

    arguments[parameter] = value

    with pytest.raises(
        ValueError,
        match=rf"{parameter} must be finite",
    ):
        AtlasReliefMeshBuilder.build(
            **arguments
        )


@pytest.mark.parametrize(
    "origin",
    [
        (-1_000_000.0, 2_000_000.0, -50_000.0),
        (1e-9, -1e-9, 1e-12),
        (-125.5, 80.25, 3.75),
    ],
)
def test_accepts_finite_origin_values(
    origin,
):
    mesh = AtlasReliefMeshBuilder.build(
        [
            [0.0, 0.5],
            [1.0, 0.25],
        ],
        width_mm=8.0,
        depth_mm=6.0,
        origin_x=origin[0],
        origin_y=origin[1],
        origin_z=origin[2],
    )

    assert mesh["origin"] == origin

    assert mesh["bottom_grid"][0][0] == (
        origin[0],
        origin[1],
        origin[2],
    )

    assert np.all(
        np.isfinite(
            np.asarray(
                mesh["triangles"],
                dtype=np.float64,
            )
        )
    )
