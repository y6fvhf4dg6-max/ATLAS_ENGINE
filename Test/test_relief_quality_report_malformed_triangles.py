import pytest

from CORE.atlas_relief_mesh_builder import (
    AtlasReliefMeshBuilder,
)
from CORE.atlas_relief_quality_report import (
    AtlasReliefQualityReport,
)


def _valid_relief():
    return AtlasReliefMeshBuilder.build(
        [
            [0.0, 0.5],
            [1.0, 0.25],
        ],
        width_mm=8.0,
        depth_mm=6.0,
    )


@pytest.mark.parametrize(
    "triangle",
    [
        [],
        [
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
        ],
        [
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (1.0, 1.0, 0.0),
        ],
        None,
        42,
    ],
)
def test_rejects_malformed_triangle_structure(
    triangle,
):
    relief = _valid_relief()
    relief["triangles"][0] = triangle

    with pytest.raises(
        ValueError,
        match=(
            "Relief geometry contains malformed "
            "triangles"
        ),
    ):
        AtlasReliefQualityReport.build(relief)


@pytest.mark.parametrize(
    "point",
    [
        None,
        42,
        "vertex",
    ],
)
def test_rejects_non_sequence_triangle_vertex(
    point,
):
    relief = _valid_relief()
    original_triangle = relief["triangles"][0]
    relief["triangles"][0] = (
        point,
        original_triangle[1],
        original_triangle[2],
    )

    with pytest.raises(
        ValueError,
        match=(
            "Relief geometry contains invalid "
            "vertex coordinates"
        ),
    ):
        AtlasReliefQualityReport.build(relief)
