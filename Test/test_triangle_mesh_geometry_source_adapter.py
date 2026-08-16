import pytest

from CORE.atlas_geometry_source_result import (
    AtlasGeometrySourceResult,
)
from CORE.atlas_triangle_mesh_geometry_source_adapter import (
    AtlasTriangleMeshGeometrySourceAdapter,
)


def test_triangle_mesh_adapter_returns_canonical_geometry_source_result():
    triangles = [
        (
            (1, 2, 3),
            (5, 2, 3),
            (1, 6, 3),
        ),
        (
            (5, 2, 3),
            (5, 6, 7),
            (1, 6, 3),
        ),
    ]

    source = {
        "triangles": triangles,
        "anchors": {
            " Origin ": (1, 2, 3),
            "Top Center": (3, 4, 7),
        },
        "confidence": 0.90,
        "provenance": " Existing Mesh Fixture ",
        "supported_projection_modes": (
            " Flat Plane ",
            "Arbitrary Mesh Surface",
        ),
    }

    result = AtlasTriangleMeshGeometrySourceAdapter().adapt(
        source
    )

    assert isinstance(
        result,
        AtlasGeometrySourceResult,
    )

    assert result.normalized_geometry == {
        "geometry_kind": "triangle_mesh",
        "triangles": (
            (
                (1.0, 2.0, 3.0),
                (5.0, 2.0, 3.0),
                (1.0, 6.0, 3.0),
            ),
            (
                (5.0, 2.0, 3.0),
                (5.0, 6.0, 7.0),
                (1.0, 6.0, 3.0),
            ),
        ),
        "triangle_count": 2,
    }

    assert result.local_bounds == (
        (1.0, 2.0, 3.0),
        (5.0, 6.0, 7.0),
    )

    assert dict(result.anchors) == {
        "origin": (1.0, 2.0, 3.0),
        "top_center": (3.0, 4.0, 7.0),
    }

    assert result.confidence == 0.90
    assert result.provenance == (
        "Existing Mesh Fixture"
    )
    assert result.supported_projection_modes == (
        "flat_plane",
        "arbitrary_mesh_surface",
    )


def test_triangle_mesh_adapter_does_not_mutate_or_share_source_triangles():
    triangles = [
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ]
    ]

    source = {
        "triangles": triangles,
        "anchors": {
            "origin": (0, 0, 0),
        },
        "confidence": 1.0,
        "provenance": "fixture",
        "supported_projection_modes": (
            "flat_plane",
        ),
    }

    result = AtlasTriangleMeshGeometrySourceAdapter().adapt(
        source
    )

    triangles[0][0][0] = 99.0
    triangles.append(
        [
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ]
    )

    assert result.normalized_geometry["triangles"] == (
        (
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
        ),
    )
    assert result.normalized_geometry[
        "triangle_count"
    ] == 1


@pytest.mark.parametrize(
    "triangles",
    (
        (),
        [],
        [
            (
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
            ),
        ],
        [
            (
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (0.0, 1.0),
            ),
        ],
        [
            (
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (0.0, 1.0, float("nan")),
            ),
        ],
        [
            (
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (0.0, 1.0, float("inf")),
            ),
        ],
        [
            (
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (0.0, True, 0.0),
            ),
        ],
    ),
)
def test_triangle_mesh_adapter_rejects_invalid_triangles(
    triangles,
):
    source = {
        "triangles": triangles,
        "anchors": {
            "origin": (0.0, 0.0, 0.0),
        },
        "confidence": 1.0,
        "provenance": "fixture",
        "supported_projection_modes": (
            "flat_plane",
        ),
    }

    with pytest.raises(ValueError):
        AtlasTriangleMeshGeometrySourceAdapter().adapt(
            source
        )


def test_triangle_mesh_adapter_requires_complete_mapping_source():
    adapter = AtlasTriangleMeshGeometrySourceAdapter()

    with pytest.raises(
        TypeError,
        match="source must be a mapping",
    ):
        adapter.adapt(
            [
                (
                    (0.0, 0.0, 0.0),
                    (1.0, 0.0, 0.0),
                    (0.0, 1.0, 0.0),
                )
            ]
        )

    with pytest.raises(
        ValueError,
        match="missing required fields",
    ):
        adapter.adapt(
            {
                "triangles": [
                    (
                        (0.0, 0.0, 0.0),
                        (1.0, 0.0, 0.0),
                        (0.0, 1.0, 0.0),
                    )
                ],
            }
        )


def test_triangle_mesh_adapter_bounds_are_deterministic_for_negative_coordinates():
    source = {
        "triangles": (
            (
                (-5.0, 2.0, -1.0),
                (3.0, -4.0, 8.0),
                (1.0, 7.0, 2.0),
            ),
        ),
        "anchors": {
            "origin": (0.0, 0.0, 0.0),
        },
        "confidence": 1.0,
        "provenance": "fixture",
        "supported_projection_modes": (
            "flat_plane",
        ),
    }

    result = AtlasTriangleMeshGeometrySourceAdapter().adapt(
        source
    )

    assert result.local_bounds == (
        (-5.0, -4.0, -1.0),
        (3.0, 7.0, 8.0),
    )
