import math

from CORE.atlas_building_hipped_roof_builder import (
    AtlasBuildingHippedRoofBuilder,
)


def _rectangular_mesh():
    bottom = [
        (0.0, 0.0, 1.0),
        (8.0, 0.0, 1.0),
        (8.0, 5.0, 1.0),
        (0.0, 5.0, 1.0),
    ]

    top = [
        (0.0, 0.0, 5.0),
        (8.0, 0.0, 5.0),
        (8.0, 5.0, 5.0),
        (0.0, 5.0, 5.0),
    ]

    triangles = [
        # Alt kapak
        (bottom[0], bottom[2], bottom[1]),
        (bottom[0], bottom[3], bottom[2]),
        # Üst kapak
        (top[0], top[1], top[2]),
        (top[0], top[2], top[3]),
        # Duvarlar
        (bottom[0], bottom[1], top[1]),
        (bottom[0], top[1], top[0]),
        (bottom[1], bottom[2], top[2]),
        (bottom[1], top[2], top[1]),
        (bottom[2], bottom[3], top[3]),
        (bottom[2], top[3], top[2]),
        (bottom[3], bottom[0], top[0]),
        (bottom[3], top[0], top[3]),
    ]

    return {
        "bottom": bottom,
        "top": top,
        "walls": [
            (bottom[0], bottom[1], top[1], top[0]),
            (bottom[1], bottom[2], top[2], top[1]),
            (bottom[2], bottom[3], top[3], top[2]),
            (bottom[3], bottom[0], top[0], top[3]),
        ],
        "triangles": triangles,
        "foundation_z": 1.0,
        "building_roof_profile": "hipped",
    }


def test_hipped_roof_replaces_flat_top_with_four_slopes():
    mesh = _rectangular_mesh()
    original_triangles = list(mesh["triangles"])

    result = AtlasBuildingHippedRoofBuilder.apply(mesh)

    assert result["building_hipped_roof_applied"] is True
    assert result["roof_geometry"] == "hipped"

    assert result["body_top_z"] == 5.0
    assert result["roof_top_z"] > 5.0
    assert result["top_z"] == result["roof_top_z"]

    assert result["building_hipped_removed_top_triangles"] == 2
    assert len(result["building_hipped_roof_triangles"]) == 4

    # 12 başlangıç - 2 düz üst kapak + 4 eğimli yüz
    assert len(result["triangles"]) == 14

    for top_triangle in original_triangles[2:4]:
        assert top_triangle not in result["triangles"]


def test_hipped_roof_apex_is_centered_over_footprint():
    mesh = _rectangular_mesh()

    result = AtlasBuildingHippedRoofBuilder.apply(mesh)

    apex = result["roof_apex"]

    assert math.isclose(apex[0], 4.0)
    assert math.isclose(apex[1], 2.5)
    assert apex[2] > 5.0


def test_non_hipped_profile_is_unchanged():
    mesh = _rectangular_mesh()
    mesh["building_roof_profile"] = "flat"

    original_triangles = list(mesh["triangles"])

    result = AtlasBuildingHippedRoofBuilder.apply(mesh)

    assert result is mesh
    assert result["triangles"] == original_triangles
    assert "building_hipped_roof_applied" not in result


def _concave_l_shaped_mesh():
    bottom = [
        (0.0, 0.0, 1.0),
        (6.0, 0.0, 1.0),
        (6.0, 1.0, 1.0),
        (1.0, 1.0, 1.0),
        (1.0, 6.0, 1.0),
        (0.0, 6.0, 1.0),
    ]

    top = [
        (0.0, 0.0, 5.0),
        (6.0, 0.0, 5.0),
        (6.0, 1.0, 5.0),
        (1.0, 1.0, 5.0),
        (1.0, 6.0, 5.0),
        (0.0, 6.0, 5.0),
    ]

    triangles = [
        # Alt kapak
        (bottom[0], bottom[3], bottom[1]),
        (bottom[1], bottom[3], bottom[2]),
        (bottom[0], bottom[5], bottom[3]),
        (bottom[3], bottom[5], bottom[4]),
        # Üst kapak
        (top[0], top[1], top[3]),
        (top[1], top[2], top[3]),
        (top[0], top[3], top[5]),
        (top[3], top[4], top[5]),
    ]

    for index, bottom_1 in enumerate(bottom):
        next_index = (index + 1) % len(bottom)

        bottom_2 = bottom[next_index]
        top_1 = top[index]
        top_2 = top[next_index]

        triangles.extend(
            [
                (bottom_1, bottom_2, top_2),
                (bottom_1, top_2, top_1),
            ]
        )

    walls = []

    for index, bottom_1 in enumerate(bottom):
        next_index = (index + 1) % len(bottom)

        walls.append(
            (
                bottom_1,
                bottom[next_index],
                top[next_index],
                top[index],
            )
        )

    return {
        "bottom": bottom,
        "top": top,
        "walls": walls,
        "triangles": triangles,
        "foundation_z": 1.0,
        "building_roof_profile": "hipped",
    }


def test_hipped_roof_apex_stays_inside_concave_footprint():
    from shapely.geometry import Point
    from shapely.geometry import Polygon

    mesh = _concave_l_shaped_mesh()

    footprint = Polygon(
        [
            (point[0], point[1])
            for point in mesh["top"]
        ]
    )

    arithmetic_center = Point(
        sum(point[0] for point in mesh["top"])
        / len(mesh["top"]),
        sum(point[1] for point in mesh["top"])
        / len(mesh["top"]),
    )

    assert not footprint.covers(arithmetic_center)

    result = AtlasBuildingHippedRoofBuilder.apply(mesh)

    apex = result["roof_apex"]

    assert footprint.covers(
        Point(apex[0], apex[1])
    )


def test_concave_hipped_roof_triangles_stay_inside_footprint():
    from shapely.geometry import Polygon

    mesh = _concave_l_shaped_mesh()

    footprint = Polygon(
        [
            (point[0], point[1])
            for point in mesh["top"]
        ]
    )

    result = AtlasBuildingHippedRoofBuilder.apply(mesh)

    roof_triangles = result[
        "building_hipped_roof_triangles"
    ]

    assert len(roof_triangles) == 6

    for triangle in roof_triangles:
        projected_triangle = Polygon(
            [
                (point[0], point[1])
                for point in triangle
            ]
        )

        assert footprint.covers(projected_triangle)


def test_concave_apex_selector_returns_fan_visible_point():
    from shapely.geometry import Polygon

    mesh = _concave_l_shaped_mesh()

    ring = mesh["top"]
    footprint = Polygon(
        [
            (point[0], point[1])
            for point in ring
        ]
    )

    apex_xy = (
        AtlasBuildingHippedRoofBuilder
        ._select_apex_xy(ring)
    )

    assert apex_xy is not None

    for index, point_1 in enumerate(ring):
        point_2 = ring[(index + 1) % len(ring)]

        fan_triangle = Polygon(
            [
                (point_1[0], point_1[1]),
                (point_2[0], point_2[1]),
                apex_xy,
            ]
        )

        assert footprint.covers(fan_triangle)


def _signed_volume(mesh):
    volume_times_six = 0.0

    for point_1, point_2, point_3 in mesh["triangles"]:
        volume_times_six += (
            point_1[0]
            * (
                point_2[1] * point_3[2]
                - point_2[2] * point_3[1]
            )
            - point_1[1]
            * (
                point_2[0] * point_3[2]
                - point_2[2] * point_3[0]
            )
            + point_1[2]
            * (
                point_2[0] * point_3[1]
                - point_2[1] * point_3[0]
            )
        )

    return volume_times_six / 6.0


def test_rectangular_hipped_roof_remains_closed_and_manifold():
    from CORE.atlas_mesh_validator import AtlasMeshValidator

    mesh = _rectangular_mesh()

    before_report = AtlasMeshValidator.report(mesh)

    assert before_report["valid"] is True
    assert before_report["open_edge_count"] == 0
    assert before_report["non_manifold_edge_count"] == 0

    result = AtlasBuildingHippedRoofBuilder.apply(mesh)

    after_report = AtlasMeshValidator.report(result)

    assert after_report["valid"] is True
    assert after_report["open_edge_count"] == 0
    assert after_report["non_manifold_edge_count"] == 0


def test_concave_hipped_roof_remains_closed_and_manifold():
    from CORE.atlas_mesh_validator import AtlasMeshValidator

    mesh = _concave_l_shaped_mesh()

    before_report = AtlasMeshValidator.report(mesh)

    assert before_report["valid"] is True
    assert before_report["open_edge_count"] == 0
    assert before_report["non_manifold_edge_count"] == 0

    result = AtlasBuildingHippedRoofBuilder.apply(mesh)

    after_report = AtlasMeshValidator.report(result)

    assert after_report["valid"] is True
    assert after_report["open_edge_count"] == 0
    assert after_report["non_manifold_edge_count"] == 0


def test_rectangular_hipped_roof_preserves_outward_winding():
    mesh = _rectangular_mesh()

    assert _signed_volume(mesh) > 0.0

    result = AtlasBuildingHippedRoofBuilder.apply(mesh)

    assert _signed_volume(result) > 0.0


def test_concave_hipped_roof_preserves_outward_winding():
    mesh = _concave_l_shaped_mesh()

    assert _signed_volume(mesh) > 0.0

    result = AtlasBuildingHippedRoofBuilder.apply(mesh)

    assert _signed_volume(result) > 0.0


def test_hipped_roof_leaves_mesh_unchanged_when_kernel_is_empty():
    mesh = _rectangular_mesh()

    original_triangles = list(mesh["triangles"])

    original_selector = (
        AtlasBuildingHippedRoofBuilder
        ._select_apex_xy
    )

    try:
        AtlasBuildingHippedRoofBuilder._select_apex_xy = (
            staticmethod(lambda ring: None)
        )

        result = AtlasBuildingHippedRoofBuilder.apply(mesh)
    finally:
        AtlasBuildingHippedRoofBuilder._select_apex_xy = (
            original_selector
        )

    assert result is mesh
    assert result["triangles"] == original_triangles
    assert "building_hipped_roof_applied" not in result
    assert "roof_geometry" not in result


def test_non_star_shaped_footprint_has_no_visibility_kernel():
    ring = [
        (0.0, 0.0, 5.0),
        (6.0, 0.0, 5.0),
        (6.0, 6.0, 5.0),
        (4.0, 6.0, 5.0),
        (4.0, 2.0, 5.0),
        (2.0, 2.0, 5.0),
        (2.0, 6.0, 5.0),
        (0.0, 6.0, 5.0),
    ]

    apex_xy = (
        AtlasBuildingHippedRoofBuilder
        ._select_apex_xy(ring)
    )

    assert apex_xy is None
