from CORE.atlas_city_composition_mesh_filter import (
    AtlasCityCompositionMeshFilter,
)


def test_city_composition_mesh_filter_suppresses_source_meshes():
    mesh_groups = {
        "roads": [
            {
                "source_id": 10,
                "type": "road_foundation",
                "triangles": [("road_10",)],
            },
            {
                "source_id": 11,
                "type": "road_foundation",
                "triangles": [("road_11",)],
            },
        ],
        "parks": [
            {
                "source_id": 20,
                "type": "park_foundation",
                "triangles": [("park_20",)],
            },
        ],
    }

    decisions = {
        "road_10": {
            "retain": True,
            "simplify": False,
            "representation_mode": "source_detail",
        },
        "road_11": {
            "retain": False,
            "simplify": False,
            "representation_mode": "suppressed",
        },
        "park_20": {
            "retain": True,
            "simplify": False,
            "representation_mode": "source_detail",
        },
    }

    result = AtlasCityCompositionMeshFilter.filter(
        mesh_groups=mesh_groups,
        decisions=decisions,
    )

    assert [
        mesh["source_id"]
        for mesh in result["mesh_groups"]["roads"]
    ] == [10]

    assert [
        mesh["source_id"]
        for mesh in result["mesh_groups"]["parks"]
    ] == [20]

    assert result["suppressed_mesh_count"] == 1


def test_city_composition_mesh_filter_preserves_unmapped_groups():
    mesh_groups = {
        "terrain": [
            {
                "type": "terrain_closed_slab",
                "triangles": [("terrain",)],
            },
        ],
        "castle_shells": [
            {
                "type": "castle_shell",
                "triangles": [("castle",)],
            },
        ],
    }

    result = AtlasCityCompositionMeshFilter.filter(
        mesh_groups=mesh_groups,
        decisions={},
    )

    assert result["mesh_groups"] == mesh_groups
    assert result["suppressed_mesh_count"] == 0
