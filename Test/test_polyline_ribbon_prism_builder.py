import pytest

from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)
from CORE.atlas_polyline_ribbon_prism_builder import (
    AtlasPolylineRibbonPrismBuilder,
)


def test_ribbon_prism_is_closed_and_manifold():
    mesh = (
        AtlasPolylineRibbonPrismBuilder
        .build(
            inner_path=[
                (0.0, 0.0),
                (5.0, 0.0),
                (10.0, 0.0),
            ],
            outer_path=[
                (0.0, 1.0),
                (5.0, 1.0),
                (10.0, 1.0),
            ],
            base_z=2.0,
            height=0.6,
        )
    )

    report = (
        AtlasMeshValidator
        ._topology_report(mesh)
    )

    assert report["open_edge_count"] == 0
    assert (
        report["non_manifold_edge_count"]
        == 0
    )


def test_ribbon_prism_triangle_count():
    mesh = (
        AtlasPolylineRibbonPrismBuilder
        .build(
            inner_path=[
                (0.0, 0.0),
                (5.0, 0.0),
                (10.0, 0.0),
            ],
            outer_path=[
                (0.0, 1.0),
                (5.0, 1.0),
                (10.0, 1.0),
            ],
            base_z=0.0,
            height=1.0,
        )
    )

    assert len(mesh["top_triangles"]) == 4
    assert len(mesh["bottom_triangles"]) == 4
    assert len(mesh["inner_wall_triangles"]) == 4
    assert len(mesh["outer_wall_triangles"]) == 4
    assert len(mesh["end_triangles"]) == 4
    assert len(mesh["triangles"]) == 20


def test_ribbon_prism_preserves_dimensions():
    mesh = (
        AtlasPolylineRibbonPrismBuilder
        .build(
            inner_path=[
                (0.0, 0.0),
                (5.0, 0.0),
            ],
            outer_path=[
                (0.0, 1.0),
                (5.0, 1.0),
            ],
            base_z=3.0,
            height=0.75,
        )
    )

    assert mesh["base_z"] == 3.0
    assert mesh["top_z"] == pytest.approx(
        3.75
    )
    assert mesh["height"] == 0.75
    assert mesh["point_count"] == 2


def test_ribbon_prism_preserves_metadata():
    mesh = (
        AtlasPolylineRibbonPrismBuilder
        .build(
            inner_path=[
                (0.0, 0.0),
                (5.0, 0.0),
            ],
            outer_path=[
                (0.0, 1.0),
                (5.0, 1.0),
            ],
            base_z=0.0,
            height=1.0,
            metadata={
                "architectural_role": (
                    "gallery_cap"
                ),
            },
        )
    )

    assert (
        mesh["architectural_role"]
        == "gallery_cap"
    )


def test_ribbon_prism_rejects_mismatched_paths():
    with pytest.raises(
        ValueError,
        match="matching point counts",
    ):
        (
            AtlasPolylineRibbonPrismBuilder
            .build(
                inner_path=[
                    (0.0, 0.0),
                    (5.0, 0.0),
                ],
                outer_path=[
                    (0.0, 1.0),
                    (5.0, 1.0),
                    (10.0, 1.0),
                ],
                base_z=0.0,
                height=1.0,
            )
        )


def test_ribbon_prism_rejects_invalid_height():
    with pytest.raises(
        ValueError,
        match="height",
    ):
        (
            AtlasPolylineRibbonPrismBuilder
            .build(
                inner_path=[
                    (0.0, 0.0),
                    (5.0, 0.0),
                ],
                outer_path=[
                    (0.0, 1.0),
                    (5.0, 1.0),
                ],
                base_z=0.0,
                height=0.0,
            )
        )
