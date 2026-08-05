from CORE.atlas_building_part_hierarchy_profiler import (
    AtlasBuildingPartHierarchyProfiler,
)
from CORE.atlas_foundation_scene_builder import (
    AtlasFoundationSceneBuilder,
)
from CORE.atlas_foundation_first_pipeline import (
    AtlasFoundationFirstPipeline,
)


def test_scene_uses_separate_pre_dedup_records_for_part_hierarchy(
    monkeypatch,
):
    landmark_parent = {
        "id": 112526702,
        "geometry": [
            (50.7333, 7.0995),
            (50.7333, 7.1002),
            (50.7341, 7.1002),
            (50.7341, 7.0995),
        ],
        "tags": {
            "building": "cathedral",
            "name": "Bonner Münster",
        },
    }

    building_part = {
        "id": 321760757,
        "geometry": [
            (50.7334, 7.0996),
            (50.7334, 7.0998),
            (50.7336, 7.0998),
            (50.7336, 7.0996),
        ],
        "tags": {
            "building:part": "yes",
            "height": "27",
            "roof:height": "7",
            "roof:shape": "apse_gabled",
        },
    }

    captured = {}

    def fake_analyze(records):
        captured["records"] = list(records)

        return {
            "main_buildings": [landmark_parent],
            "building_parts": [building_part],
            "mesh_buildings": [building_part],
            "parent_metrics": {},
            "suppressed_parent_ids": [],
            "residual_replacement_parent_ids": [],
            "residual_parent_records": [],
            "parents": {
                112526702: {
                    "parent": landmark_parent,
                    "parts": [building_part],
                    "part_ids": [321760757],
                },
            },
            "part_to_parent": {
                321760757: 112526702,
            },
            "unassigned_part_ids": [],
            "minaret_component_to_minaret": {},
            "minaret_components_by_minaret": {},
            "summary": {
                "main_building_count": 1,
                "building_part_count": 1,
                "parent_with_parts_count": 1,
                "assigned_building_part_count": 1,
                "unassigned_building_part_count": 0,
                "parent_part_counts": {
                    112526702: 1,
                },
                "suppressed_parent_count": 0,
                "mesh_building_count": 1,
            },
        }

    monkeypatch.setattr(
        AtlasBuildingPartHierarchyProfiler,
        "analyze",
        staticmethod(fake_analyze),
    )

    monkeypatch.setattr(
        AtlasFoundationFirstPipeline,
        "build_building_mesh",
        staticmethod(
            lambda **kwargs: {
                "foundation_z": 0.0,
                "triangles": [],
            }
        ),
    )

    AtlasFoundationSceneBuilder.build_scene(
        raw_buildings=[],
        hierarchy_raw_buildings=[
            landmark_parent,
            building_part,
        ],
        coordinate_engine=object(),
        terrain_mesh=object(),
        castles=[],
        max_buildings=0,
        debug=False,
    )

    assert captured["records"] == [
        landmark_parent,
        building_part,
    ]


class DummyCoordinateEngine:
    @staticmethod
    def geometry_to_stl_mm(geometry):
        return [
            (float(lon) * 10.0, float(lat) * 10.0)
            for lat, lon in geometry
        ]


def test_resolves_adjacent_sibling_footprints_for_building_part():
    target = {
        "id": 20,
        "geometry": [
            (1.0, 1.0),
            (1.0, 2.0),
            (2.0, 2.0),
            (2.0, 1.0),
        ],
        "tags": {
            "building:part": "yes",
            "roof:shape": "apse_gabled",
        },
    }

    sibling_a = {
        "id": 21,
        "geometry": [
            (1.0, 0.0),
            (1.0, 1.0),
            (2.0, 1.0),
            (2.0, 0.0),
        ],
        "tags": {
            "building:part": "yes",
        },
    }

    sibling_b = {
        "id": 22,
        "geometry": [
            (2.0, 1.0),
            (2.0, 2.0),
            (3.0, 2.0),
            (3.0, 1.0),
        ],
        "tags": {
            "building:part": "yes",
        },
    }

    parent_data = {
        "parts": [
            target,
            sibling_a,
            sibling_b,
        ],
    }

    result = (
        AtlasFoundationSceneBuilder
        ._building_part_adjacent_footprints(
            raw_building=target,
            parent_data=parent_data,
            coordinate_engine=DummyCoordinateEngine(),
        )
    )

    assert result == [
        [
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 20.0),
            (0.0, 20.0),
        ],
        [
            (10.0, 20.0),
            (20.0, 20.0),
            (20.0, 30.0),
            (10.0, 30.0),
        ],
    ]

def test_scene_exposes_single_computed_building_part_hierarchy(
    monkeypatch,
):
    expected_hierarchy = {
        "main_buildings": [],
        "building_parts": [],
        "mesh_buildings": [],
        "parent_metrics": {},
        "suppressed_parent_ids": [],
        "residual_replacement_parent_ids": [],
        "residual_parent_records": [],
        "attached_minaret_component_ids": [],
        "minaret_component_to_minaret": {},
        "minaret_components_by_minaret": {},
        "parents": {},
        "part_to_parent": {},
        "unassigned_part_ids": [],
        "summary": {
            "main_building_count": 0,
            "building_part_count": 0,
            "parent_with_parts_count": 0,
            "assigned_building_part_count": 0,
            "unassigned_building_part_count": 0,
            "parent_part_counts": {},
            "suppressed_parent_count": 0,
            "mesh_building_count": 0,
        },
    }

    monkeypatch.setattr(
        AtlasBuildingPartHierarchyProfiler,
        "analyze",
        staticmethod(
            lambda records: expected_hierarchy
        ),
    )

    scene = AtlasFoundationSceneBuilder.build_scene(
        raw_buildings=[],
        hierarchy_raw_buildings=[],
        coordinate_engine=object(),
        terrain_mesh=object(),
        castles=[],
        max_buildings=0,
        debug=False,
    )

    assert (
        scene.metadata["building_part_hierarchy"]
        is expected_hierarchy
    )
