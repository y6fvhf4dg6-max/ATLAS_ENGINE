from CORE.atlas_elevated_area_foundation_builder import (
    AtlasElevatedAreaFoundationBuilder,
)
from CORE.atlas_mesh_validator import AtlasMeshValidator


class FakeCoordinateEngine:
    @staticmethod
    def geometry_to_stl_mm(geometry):
        return [
            (float(x), float(y))
            for x, y in geometry
        ]

    @staticmethod
    def height_to_stl_mm(height_m):
        return float(height_m) * 0.20


def _terrain_mesh():
    return {
        "top_points": [
            [
                (0.0, 0.0, 1.0),
                (5.0, 0.0, 1.2),
                (10.0, 0.0, 1.4),
            ],
            [
                (0.0, 5.0, 1.2),
                (5.0, 5.0, 1.4),
                (10.0, 5.0, 1.6),
            ],
            [
                (0.0, 10.0, 1.4),
                (5.0, 10.0, 1.6),
                (10.0, 10.0, 1.8),
            ],
        ],
        "metadata": {
            "size_x_mm": 10.0,
            "size_y_mm": 10.0,
        },
    }


def _area():
    return {
        "id": 1001,
        "geometry": [
            (2.0, 2.0),
            (8.0, 2.0),
            (8.0, 8.0),
            (2.0, 8.0),
        ],
        "height_m": 4.0,
        "tags": {
            "highway": "pedestrian",
            "area": "yes",
            "height": "4.0",
        },
        "area_type": "elevated_pedestrian_area",
    }


def test_builds_closed_elevated_area_mesh():
    meshes = AtlasElevatedAreaFoundationBuilder.build_areas(
        areas=[_area()],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_terrain_mesh(),
        debug=False,
    )

    assert len(meshes) == 1

    mesh = meshes[0]
    report = AtlasMeshValidator.report(mesh)

    assert report["valid"]
    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_top_surface_is_flat_and_bottom_follows_terrain():
    mesh = AtlasElevatedAreaFoundationBuilder.build_areas(
        areas=[_area()],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_terrain_mesh(),
        debug=False,
    )[0]

    bottom_z_values = {
        round(point[2], 6)
        for point in mesh["bottom"]
    }

    top_z_values = {
        round(point[2], 6)
        for point in mesh["top"]
    }

    assert len(bottom_z_values) > 1
    assert len(top_z_values) == 1


def test_preserves_source_and_height_metadata():
    mesh = AtlasElevatedAreaFoundationBuilder.build_areas(
        areas=[_area()],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_terrain_mesh(),
        debug=False,
    )[0]

    assert mesh["type"] == "elevated_area_foundation"
    assert mesh["source_id"] == 1001
    assert mesh["height_m"] == 4.0
    assert mesh["height_mm"] == 0.8
    assert mesh["placement_mode"] == "foundation_first"


def test_nested_step_starts_at_parent_top_instead_of_terrain():
    parent = {
        "id": 2001,
        "geometry": [
            (1.0, 1.0),
            (9.0, 1.0),
            (9.0, 9.0),
            (1.0, 9.0),
        ],
        "height_m": 1.0,
        "tags": {
            "highway": "pedestrian",
            "area": "yes",
            "height": "1.0",
        },
        "area_type": "elevated_pedestrian_area",
    }

    child = {
        "id": 2002,
        "geometry": [
            (3.0, 3.0),
            (7.0, 3.0),
            (7.0, 7.0),
            (3.0, 7.0),
        ],
        "height_m": 2.0,
        "tags": {
            "highway": "pedestrian",
            "area": "yes",
            "height": "2.0",
        },
        "area_type": "elevated_pedestrian_area",
    }

    meshes = AtlasElevatedAreaFoundationBuilder.build_areas(
        areas=[parent, child],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_terrain_mesh(),
        debug=False,
    )

    assert len(meshes) == 2

    by_id = {
        mesh["source_id"]: mesh
        for mesh in meshes
    }

    parent_mesh = by_id[2001]
    child_mesh = by_id[2002]

    assert child_mesh["parent_source_id"] == 2001
    assert child_mesh["base_mode"] == "parent_top"

    assert {
        round(point[2], 6)
        for point in child_mesh["bottom"]
    } == {
        round(parent_mesh["top_z"], 6)
    }

    assert child_mesh["top_z"] > parent_mesh["top_z"]


def test_nested_steps_preserve_scaled_height_difference():
    parent = {
        "id": 3001,
        "geometry": [
            (1.0, 1.0),
            (9.0, 1.0),
            (9.0, 9.0),
            (1.0, 9.0),
        ],
        "height_m": 7.00,
        "tags": {
            "highway": "pedestrian",
            "area": "yes",
            "height": "7.00",
        },
        "area_type": "elevated_pedestrian_area",
    }

    child = {
        "id": 3002,
        "geometry": [
            (2.0, 2.0),
            (8.0, 2.0),
            (8.0, 8.0),
            (2.0, 8.0),
        ],
        "height_m": 7.25,
        "tags": {
            "highway": "pedestrian",
            "area": "yes",
            "height": "7.25",
        },
        "area_type": "elevated_pedestrian_area",
    }

    meshes = AtlasElevatedAreaFoundationBuilder.build_areas(
        areas=[parent, child],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_terrain_mesh(),
        debug=False,
    )

    by_id = {
        mesh["source_id"]: mesh
        for mesh in meshes
    }

    parent_mesh = by_id[3001]
    child_mesh = by_id[3002]

    expected_increment_mm = (
        FakeCoordinateEngine.height_to_stl_mm(7.25)
        - FakeCoordinateEngine.height_to_stl_mm(7.00)
    )

    actual_increment_mm = (
        child_mesh["top_z"]
        - parent_mesh["top_z"]
    )

    assert abs(
        actual_increment_mm - expected_increment_mm
    ) < 1e-9
    assert actual_increment_mm < (
        AtlasElevatedAreaFoundationBuilder
        .MIN_PRINTABLE_THICKNESS_MM
    )


def test_root_area_uses_median_terrain_reference_and_clamps_high_points():
    low_area = {
        "id": 4001,
        "geometry": [
            (0.0, 0.0),
            (10.0, 0.0),
            (10.0, 10.0),
            (0.0, 10.0),
        ],
        "height_m": 0.10,
        "tags": {
            "highway": "pedestrian",
            "area": "yes",
            "height": "0.10",
        },
        "area_type": "elevated_pedestrian_area",
    }

    mesh = AtlasElevatedAreaFoundationBuilder.build_areas(
        areas=[low_area],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_terrain_mesh(),
        debug=False,
    )[0]

    expected_reference_z = 1.4
    expected_top_z = (
        expected_reference_z
        + AtlasElevatedAreaFoundationBuilder
        .MIN_PRINTABLE_THICKNESS_MM
    )

    assert mesh["base_mode"] == "terrain"
    assert mesh["terrain_reference_mode"] == "median"

    assert abs(
        mesh["terrain_reference_z"]
        - expected_reference_z
    ) < 1e-9

    assert abs(
        mesh["top_z"]
        - expected_top_z
    ) < 1e-9

    maximum_bottom_z = max(
        point[2]
        for point in mesh["bottom"]
    )

    assert maximum_bottom_z <= (
        mesh["top_z"]
        - AtlasElevatedAreaFoundationBuilder
        .MIN_PRINTABLE_THICKNESS_MM
        + 1e-9
    )

    assert mesh["top_z"] < (
        mesh["highest_terrain_z"]
        + AtlasElevatedAreaFoundationBuilder
        .MIN_PRINTABLE_THICKNESS_MM
    )

    report = AtlasMeshValidator.report(mesh)

    assert report["valid"]
    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_nested_area_identifies_edges_shared_with_parent():
    parent = {
        "id": 5001,
        "geometry": [
            (1.0, 1.0),
            (9.0, 1.0),
            (9.0, 9.0),
            (1.0, 9.0),
        ],
        "height_m": 1.0,
        "tags": {
            "highway": "pedestrian",
            "area": "yes",
            "height": "1.0",
        },
        "area_type": "elevated_pedestrian_area",
    }

    child = {
        "id": 5002,
        "geometry": [
            (1.0, 1.0),
            (9.0, 1.0),
            (9.0, 8.0),
            (1.0, 8.0),
        ],
        "height_m": 1.25,
        "tags": {
            "highway": "pedestrian",
            "area": "yes",
            "height": "1.25",
        },
        "area_type": "elevated_pedestrian_area",
    }

    meshes = AtlasElevatedAreaFoundationBuilder.build_areas(
        areas=[parent, child],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=_terrain_mesh(),
        debug=False,
    )

    by_id = {
        mesh["source_id"]: mesh
        for mesh in meshes
    }

    child_mesh = by_id[5002]

    assert child_mesh["parent_source_id"] == 5001
    assert child_mesh["shared_parent_edge_count"] == 3
    assert child_mesh["new_step_edge_count"] == 1

    assert len(
        child_mesh["shared_parent_edge_indices"]
    ) == 3

    assert len(
        child_mesh["new_step_edge_indices"]
    ) == 1
