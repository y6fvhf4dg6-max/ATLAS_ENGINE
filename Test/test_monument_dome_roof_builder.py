import pytest

from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)
from CORE.atlas_monument_dome_roof_builder import (
    AtlasMonumentDomeRoofBuilder,
)


def build_round_building_mesh():
    bottom = [
        (-1.0, -1.0, 0.0),
        (1.0, -1.0, 0.0),
        (1.0, 1.0, 0.0),
        (-1.0, 1.0, 0.0),
    ]

    top = [
        (-1.0, -1.0, 2.0),
        (1.0, -1.0, 2.0),
        (1.0, 1.0, 2.0),
        (-1.0, 1.0, 2.0),
    ]

    bottom_triangles = [
        (
            bottom[0],
            bottom[2],
            bottom[1],
        ),
        (
            bottom[0],
            bottom[3],
            bottom[2],
        ),
    ]

    top_triangles = [
        (
            top[0],
            top[1],
            top[2],
        ),
        (
            top[0],
            top[2],
            top[3],
        ),
    ]

    walls = []
    wall_triangles = []

    for index in range(len(bottom)):
        next_index = (index + 1) % len(bottom)

        b1 = bottom[index]
        b2 = bottom[next_index]
        t1 = top[index]
        t2 = top[next_index]

        walls.append(
            (
                b1,
                b2,
                t2,
                t1,
            )
        )

        wall_triangles.extend(
            [
                (
                    b1,
                    b2,
                    t2,
                ),
                (
                    b1,
                    t2,
                    t1,
                ),
            ]
        )

    return {
        "type": "building",
        "bottom": bottom,
        "top": top,
        "walls": walls,
        "triangles": [
            *bottom_triangles,
            *top_triangles,
            *wall_triangles,
        ],
        "bottom_z": 0.0,
        "top_z": 2.0,
        "foundation_z": 0.0,
    }


def test_dome_roof_replaces_flat_top_and_remains_manifold():
    mesh = build_round_building_mesh()

    before_report = AtlasMeshValidator.report(mesh)

    assert before_report["open_edge_count"] == 0
    assert before_report["non_manifold_edge_count"] == 0

    result = AtlasMonumentDomeRoofBuilder.apply(
        mesh=mesh,
        roof_shape="dome",
        roof_height_m=6.0,
        coordinate_engine=None,
    )

    assert result["monument_dome_applied"] is True
    assert result["roof_geometry"] == "dome"
    assert result["roof_top_z"] > 2.0
    assert result["roof_height_mm"] > 0.0
    assert len(result["roof_triangles"]) > 4

    after_report = AtlasMeshValidator.report(result)

    assert after_report["open_edge_count"] == 0
    assert after_report["non_manifold_edge_count"] == 0
    assert after_report["valid"] is True


def test_non_dome_roof_shape_is_ignored():
    mesh = build_round_building_mesh()

    result = AtlasMonumentDomeRoofBuilder.apply(
        mesh=mesh,
        roof_shape="flat",
        roof_height_m=None,
        coordinate_engine=None,
    )

    assert result.get("monument_dome_applied") is not True
    assert result["top_z"] == 2.0


def test_missing_mesh_is_ignored():
    assert (
        AtlasMonumentDomeRoofBuilder.apply(
            mesh=None,
            roof_shape="dome",
            roof_height_m=None,
            coordinate_engine=None,
        )
        is None
    )


class FakeCoordinateEngine:
    @staticmethod
    def height_to_stl_mm(height_m):
        return float(height_m) * 1000.0 / 5500.0


def test_default_dome_height_uses_short_footprint_axis():
    base_ring = [
        (0.0, 0.0, 2.0),
        (10.0, 0.0, 2.0),
        (10.0, 4.0, 2.0),
        (0.0, 4.0, 2.0),
    ]

    result = AtlasMonumentDomeRoofBuilder._calculate_roof_height_mm(
        base_ring=base_ring,
        roof_height_m=None,
        coordinate_engine=None,
    )

    assert result == pytest.approx(
        4.0
        * AtlasMonumentDomeRoofBuilder
        .DEFAULT_WIDTH_HEIGHT_RATIO
    )


def test_default_dome_ratio_is_shallow_cap_range():
    assert (
        0.25
        <= AtlasMonumentDomeRoofBuilder.DEFAULT_WIDTH_HEIGHT_RATIO
        <= 0.33
    )


def test_small_dome_is_not_forced_to_six_tenths_mm():
    base_ring = [
        (0.0, 0.0, 2.0),
        (1.0, 0.0, 2.0),
        (1.0, 1.0, 2.0),
        (0.0, 1.0, 2.0),
    ]

    result = AtlasMonumentDomeRoofBuilder._calculate_roof_height_mm(
        base_ring=base_ring,
        roof_height_m=None,
        coordinate_engine=None,
    )

    assert result < 0.60
    assert result >= (
        AtlasMonumentDomeRoofBuilder.MIN_ROOF_HEIGHT_MM
    )


def test_explicit_roof_height_uses_coordinate_scale():
    base_ring = [
        (0.0, 0.0, 2.0),
        (10.0, 0.0, 2.0),
        (10.0, 10.0, 2.0),
        (0.0, 10.0, 2.0),
    ]

    result = AtlasMonumentDomeRoofBuilder._calculate_roof_height_mm(
        base_ring=base_ring,
        roof_height_m="5 m",
        coordinate_engine=FakeCoordinateEngine(),
    )

    assert result == pytest.approx(
        5.0 * 1000.0 / 5500.0
    )


def test_dome_uses_existing_extruded_height_interval_without_double_counting():
    mesh = build_round_building_mesh()

    # Extruder min_height değerini zaten bottom_z konumuna uygular.
    # Bu örnekte kubbe parçası 1–2 mm aralığında hazırdır.
    def shift_bottom_vertex(point):
        z = 1.0 if point[2] == 0.0 else point[2]

        return (
            point[0],
            point[1],
            z,
        )

    mesh["bottom"] = [
        shift_bottom_vertex(point)
        for point in mesh["bottom"]
    ]

    mesh["walls"] = [
        tuple(
            shift_bottom_vertex(point)
            for point in wall
        )
        for wall in mesh["walls"]
    ]

    mesh["triangles"] = [
        tuple(
            shift_bottom_vertex(point)
            for point in triangle
        )
        for triangle in mesh["triangles"]
    ]

    mesh["bottom_z"] = 1.0
    mesh["foundation_z"] = 0.0

    result = AtlasMonumentDomeRoofBuilder.apply(
        mesh=mesh,
        roof_shape="dome",
        roof_height_m=None,
        coordinate_engine=None,
        total_height_m=11.0,
        min_height_m=5.5,
    )

    assert result["monument_dome_applied"] is True
    assert result["roof_semantic_mode"] == "height_interval"

    # Mevcut extruded parça aralığı doğrudan kubbe aralığıdır.
    assert result["body_top_z"] == pytest.approx(1.0)
    assert result["roof_base_z"] == pytest.approx(1.0)
    assert result["roof_top_z"] == pytest.approx(2.0)
    assert result["top_z"] == pytest.approx(2.0)
    assert result["roof_height_mm"] == pytest.approx(1.0)

    report = AtlasMeshValidator.report(result)

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0
    assert report["valid"] is True
