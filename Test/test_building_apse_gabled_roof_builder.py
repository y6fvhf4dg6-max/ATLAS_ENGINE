import pytest

from CORE.atlas_building_apse_gabled_roof_builder import (
    AtlasBuildingApseGabledRoofBuilder,
)
from CORE.atlas_mesh_validator import AtlasMeshValidator
from CORE.atlas_polygon_triangulator import (
    AtlasPolygonTriangulator,
)


class DummyCoordinateEngine:
    scale_ratio = 3000.0

    @staticmethod
    def height_to_stl_mm(height_m):
        return float(height_m) * 1000.0 / 3000.0


def build_apse_building_mesh():
    footprint = [
        (0.0, -3.0),
        (6.0, -3.0),
        (7.5, -2.4),
        (8.5, -1.4),
        (9.0, 0.0),
        (8.5, 1.4),
        (7.5, 2.4),
        (6.0, 3.0),
        (0.0, 3.0),
    ]

    bottom = [
        (x, y, 0.0)
        for x, y in footprint
    ]
    top = [
        (x, y, 6.0)
        for x, y in footprint
    ]

    surface_triangles = (
        AtlasPolygonTriangulator.triangulate(
            footprint
        )
    )

    bottom_triangles = [
        (
            (triangle[0][0], triangle[0][1], 0.0),
            (triangle[2][0], triangle[2][1], 0.0),
            (triangle[1][0], triangle[1][1], 0.0),
        )
        for triangle in surface_triangles
    ]

    top_triangles = [
        (
            (triangle[0][0], triangle[0][1], 6.0),
            (triangle[1][0], triangle[1][1], 6.0),
            (triangle[2][0], triangle[2][1], 6.0),
        )
        for triangle in surface_triangles
    ]

    walls = []
    wall_triangles = []

    for index, bottom_a in enumerate(bottom):
        next_index = (index + 1) % len(bottom)

        bottom_b = bottom[next_index]
        top_a = top[index]
        top_b = top[next_index]

        walls.append(
            (
                bottom_a,
                bottom_b,
                top_b,
                top_a,
            )
        )

        wall_triangles.extend(
            [
                (
                    bottom_a,
                    bottom_b,
                    top_b,
                ),
                (
                    bottom_a,
                    top_b,
                    top_a,
                ),
            ]
        )

    return {
        "bottom": bottom,
        "top": top,
        "walls": walls,
        "triangles": [
            *bottom_triangles,
            *top_triangles,
            *wall_triangles,
        ],
        "bottom_z": 0.0,
        "top_z": 6.0,
        "building_roof_profile": "apse_gabled",
        "is_castle_building": False,
    }


def test_apse_gabled_roof_uses_osm_height_and_remains_manifold():
    mesh = build_apse_building_mesh()

    result = AtlasBuildingApseGabledRoofBuilder.apply(
        mesh=mesh,
        roof_height_m="3",
        coordinate_engine=DummyCoordinateEngine(),
    )

    expected_roof_height_mm = 3_000.0 / 3000.0

    assert result["building_apse_gabled_roof_applied"] is True
    assert result["roof_geometry"] == "apse_gabled"
    assert result["body_top_z"] == pytest.approx(6.0)
    assert result["roof_height_mm"] == pytest.approx(
        expected_roof_height_mm
    )
    assert result["roof_top_z"] == pytest.approx(
        6.0 + expected_roof_height_mm
    )
    assert result["top_z"] == pytest.approx(
        6.0 + expected_roof_height_mm
    )

    ridge_start = result["roof_ridge_start"]
    ridge_end = result["roof_ridge_end"]

    assert ridge_start[0] < ridge_end[0]
    assert ridge_start[2] == pytest.approx(7.0)
    assert ridge_end[2] == pytest.approx(7.0)

    assert (
        result["building_apse_gabled_removed_top_triangles"]
        > 0
    )
    assert result["building_apse_gabled_roof_triangles"]

    report = AtlasMeshValidator.report(result)

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0
    assert report["valid"] is True


def test_apse_gabled_roof_uses_adjacent_footprints_to_resolve_ridge():
    mesh = build_apse_building_mesh()

    adjacent_footprints = [
        [
            (-5.0, -3.0),
            (0.0, -3.0),
            (0.0, 3.0),
            (-5.0, 3.0),
        ],
    ]

    result = AtlasBuildingApseGabledRoofBuilder.apply(
        mesh=mesh,
        roof_height_m="3",
        coordinate_engine=DummyCoordinateEngine(),
        adjacent_footprints=adjacent_footprints,
    )

    assert result["apse_connection_edge_indices"] == [8]
    assert result["apse_connection_start"] == pytest.approx(
        (0.0, 3.0)
    )
    assert result["apse_connection_end"] == pytest.approx(
        (0.0, -3.0)
    )
    assert result["apse_tip"] == pytest.approx(
        (9.0, 0.0)
    )

    ridge_start = result["roof_ridge_start"]
    ridge_end = result["roof_ridge_end"]

    from shapely.geometry import Polygon

    architectural_centroid = Polygon(
        result["apse_architectural_ring"]
    ).centroid

    assert ridge_start[:2] == pytest.approx(
        (
            architectural_centroid.x,
            architectural_centroid.y,
        )
    )
    assert ridge_end[:2] == pytest.approx(
        (9.0, 0.0)
    )
    assert ridge_start[2] == pytest.approx(7.0)
    assert ridge_end[2] == pytest.approx(7.0)

    report = AtlasMeshValidator.report(result)

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0
    assert report["valid"] is True


def test_ridge_connection_midpoint_follows_multi_edge_contact_chain():
    footprint = [
        (0.0, -3.0),
        (6.0, -3.0),
        (7.5, -2.4),
        (8.5, -1.4),
        (9.0, 0.0),
        (8.5, 1.4),
        (7.5, 2.4),
        (6.0, 3.0),
        (0.0, 3.0),
    ]

    adjacent_footprints = [
        [
            (-5.0, -4.0),
            (6.1, -4.0),
            (6.1, 4.0),
            (-5.0, 4.0),
        ],
    ]

    context = (
        AtlasBuildingApseGabledRoofBuilder
        ._resolve_ridge_context(
            footprint=footprint,
            adjacent_footprints=adjacent_footprints,
        )
    )

    assert context["connection_edge_indices"] == [
        7,
        8,
        0,
    ]

    assert context["connection_midpoint"] == pytest.approx(
        (0.0, 0.0)
    )

    assert context["apse_tip"] == pytest.approx(
        (9.0, 0.0)
    )


def test_apse_architectural_ring_regularizes_dense_outline_to_polygon():
    dense_footprint = [
        (0.0, -3.0),
        (2.0, -3.0),
        (4.0, -2.9),
        (6.0, -2.5),
        (7.5, -1.8),
        (8.5, -0.9),
        (9.0, 0.0),
        (8.5, 0.9),
        (7.5, 1.8),
        (6.0, 2.5),
        (4.0, 2.9),
        (2.0, 3.0),
        (0.0, 3.0),
        (0.0, 1.0),
        (0.0, -1.0),
    ]

    result = (
        AtlasBuildingApseGabledRoofBuilder
        ._regularize_architectural_polygon(
            footprint=dense_footprint,
            connection_edge_indices=[12, 13, 14],
        )
    )

    assert result is not None
    assert len(result["architectural_ring"]) >= 5
    assert (
        len(result["exposed_eave_points"])
        == len(result["architectural_ring"]) - 1
    )
    assert result["connection_start"] == pytest.approx(
        (0.0, 3.0)
    )
    assert result["connection_end"] == pytest.approx(
        (0.0, -3.0)
    )
