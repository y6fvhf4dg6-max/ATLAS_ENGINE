import pytest

from CORE.atlas_classical_colonnade_builder import (
    AtlasClassicalColonnadeBuilder,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


def test_linear_colonnade_builds_closed_columns():
    mesh = AtlasClassicalColonnadeBuilder.build_along_polyline(
        path_points=[
            (0.0, 0.0),
            (10.0, 0.0),
        ],
        base_z=2.0,
        column_radius_mm=0.5,
        column_height_mm=3.0,
        target_spacing_mm=2.5,
        column_segments=8,
    )

    assert mesh["column_count"] == 5
    assert len(mesh["component_meshes"]) == 5
    assert mesh["base_z"] == 2.0
    assert mesh["top_z"] == 5.0

    for component in mesh["component_meshes"]:
        report = (
            AtlasMeshValidator
            ._topology_report(component)
        )

        assert report["open_edge_count"] == 0
        assert (
            report["non_manifold_edge_count"]
            == 0
        )


def test_colonnade_preserves_endpoints():
    mesh = AtlasClassicalColonnadeBuilder.build_along_polyline(
        path_points=[
            (1.0, 2.0),
            (9.0, 2.0),
        ],
        base_z=0.0,
        target_spacing_mm=2.0,
        include_endpoints=True,
    )

    assert mesh["column_centers"][0] == (
        1.0,
        2.0,
    )
    assert mesh["column_centers"][-1] == (
        9.0,
        2.0,
    )


def test_colonnade_works_on_curved_polyline():
    mesh = AtlasClassicalColonnadeBuilder.build_along_polyline(
        path_points=[
            (-4.0, 0.0),
            (-3.0, 2.0),
            (0.0, 4.0),
            (3.0, 2.0),
            (4.0, 0.0),
        ],
        base_z=1.0,
        column_radius_mm=0.4,
        column_height_mm=2.5,
        target_spacing_mm=1.8,
        column_segments=10,
    )

    assert mesh["column_count"] >= 6
    assert (
        mesh["actual_spacing_min_mm"]
        > 0.0
    )
    assert (
        mesh["actual_spacing_max_mm"]
        <= 2.2
    )


def test_colonnade_triangle_count_matches_components():
    mesh = AtlasClassicalColonnadeBuilder.build_along_polyline(
        path_points=[
            (0.0, 0.0),
            (6.0, 0.0),
        ],
        base_z=0.0,
        column_segments=10,
        target_spacing_mm=2.0,
    )

    expected = sum(
        len(component["triangles"])
        for component in mesh[
            "component_meshes"
        ]
    )

    assert len(mesh["triangles"]) == expected


def test_colonnade_preserves_metadata():
    mesh = AtlasClassicalColonnadeBuilder.build_along_polyline(
        path_points=[
            (0.0, 0.0),
            (5.0, 0.0),
        ],
        base_z=0.0,
        metadata={
            "architectural_role": (
                "upper_gallery"
            ),
        },
    )

    assert (
        mesh["architectural_role"]
        == "upper_gallery"
    )

    assert all(
        component["architectural_role"]
        == "upper_gallery"
        for component in mesh[
            "component_meshes"
        ]
    )


def test_colonnade_rejects_short_path():
    with pytest.raises(
        ValueError,
        match="two distinct points",
    ):
        AtlasClassicalColonnadeBuilder.build_along_polyline(
            path_points=[
                (0.0, 0.0),
            ],
            base_z=0.0,
        )


def test_colonnade_rejects_invalid_spacing():
    with pytest.raises(
        ValueError,
        match="target_spacing_mm",
    ):
        AtlasClassicalColonnadeBuilder.build_along_polyline(
            path_points=[
                (0.0, 0.0),
                (5.0, 0.0),
            ],
            base_z=0.0,
            target_spacing_mm=0.0,
        )
