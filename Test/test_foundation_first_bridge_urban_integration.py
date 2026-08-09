from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)


def test_foundation_first_attaches_bridge_urban_integration_record():
    result = {}

    bridge_source = {
        "id": 100,
        "geometry_type": "way",
        "geometry": (
            (50.0000, 8.0000),
            (50.0000, 8.2000),
        ),
        "tags": {
            "man_made": "bridge",
        },
    }

    bridge_mesh = {
        "landmark_id": 100,
        "foundation_z": 0.50,
        "road_approaches": (
            {
                "road_mesh_index": 2,
                "source_distance_mm": 0.60,
                "length_mm": 1.20,
            },
            {
                "road_mesh_index": 5,
                "source_distance_mm": 0.80,
                "length_mm": 1.40,
            },
        ),
    }

    resolved = (
        AtlasFoundationFirstEngine
        .attach_bridge_urban_integration(
            result=result,
            landmarks=(bridge_source,),
            landmark_meshes=(bridge_mesh,),
        )
    )

    assert resolved is result
    assert resolved[
        "bridge_urban_integration_records"
    ] == 1

    records = resolved[
        "bridge_urban_integration"
    ]

    assert len(records) == 1

    record = records[0]

    assert record["bridge_element_id"] == "bridge_100"
    assert record["approach_road_continuity"] is True
    assert record["approach_count"] == 2
    assert record["approach_road_mesh_indices"] == (
        2,
        5,
    )
    assert record[
        "maximum_approach_source_distance_mm"
    ] == 0.80

    assert record[
        "existing_bridge_topology_preserved"
    ] is True
    assert record[
        "bridge_geometry_rewritten"
    ] is False

    assert record["foundation_z"] == 0.50


def test_foundation_first_bridge_integration_ignores_non_bridge_landmarks():
    result = {}

    resolved = (
        AtlasFoundationFirstEngine
        .attach_bridge_urban_integration(
            result=result,
            landmarks=(
                {
                    "id": 200,
                    "geometry_type": "way",
                    "geometry": (
                        (50.0, 8.0),
                        (50.1, 8.1),
                    ),
                    "tags": {
                        "man_made": "tower",
                    },
                },
            ),
            landmark_meshes=(
                {
                    "landmark_id": 200,
                    "foundation_z": 0.70,
                },
            ),
        )
    )

    assert resolved[
        "bridge_urban_integration"
    ] == ()
    assert resolved[
        "bridge_urban_integration_records"
    ] == 0


def test_generate_city_result_exposes_bridge_urban_integration(
    monkeypatch,
):
    class StopAfterBridgeIntegration(Exception):
        pass

    fake_data = {
        "buildings": [],
        "landmarks": [
            {
                "id": 100,
                "geometry_type": "way",
                "geometry": (
                    (50.0000, 8.0000),
                    (50.0000, 8.2000),
                ),
                "tags": {
                    "man_made": "bridge",
                },
            },
        ],
        "trees": [],
        "tree_rows": [],
        "roads": [],
        "pedestrian_paths": [],
        "linear_infrastructure": [],
        "elevated_areas": [],
        "artworks": [],
        "parks": [],
        "waters": [],
        "coastlines": [],
        "waterfront_structures": [],
        "castles": [],
        "castle_metadata": [],
        "castle_walls": [],
        "defensive_towers": [],
    }

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_engine."
        "AtlasLocalOSMReader.read",
        lambda *args, **kwargs: fake_data,
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_engine."
        "AtlasNaturePipeline.fetch",
        lambda **kwargs: {},
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_engine."
        "AtlasCastleGeometryClassifier.classify",
        lambda **kwargs: {
            "shell_castles": [],
            "independent_castle_walls": [],
            "relation_castle_walls": [],
            "inferred_perimeter_walls": [],
            "unknown_castles": [],
        },
    )

    monkeypatch.setattr(
        AtlasFoundationFirstEngine,
        "_resolve_scene_scale",
        staticmethod(
            lambda **kwargs: {
                "xy_scale": 5500.0,
            }
        ),
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_engine."
        "AtlasTerrainPipeline.build_terrain_slab",
        lambda **kwargs: {
            "type": "terrain_closed_slab",
            "triangles": [],
            "metadata": {
                "grid_size": 2,
                "size_mm": 150.0,
                "size_x_mm": 150.0,
                "size_y_mm": 150.0,
                "min_height_m": 100.0,
                "max_height_m": 100.0,
                "delta_height_m": 0.0,
                "smoothing_passes": 0,
            },
            "grid": {
                "heights": [
                    [100.0, 100.0],
                    [100.0, 100.0],
                ],
                "min_height_m": 100.0,
                "max_height_m": 100.0,
                "delta_height_m": 0.0,
            },
            "top_points": [
                [
                    (0.0, 0.0, 0.8),
                    (150.0, 0.0, 0.8),
                ],
                [
                    (0.0, 150.0, 0.8),
                    (150.0, 150.0, 0.8),
                ],
            ],
            "bottom_points": [
                [
                    (0.0, 0.0, 0.0),
                    (150.0, 0.0, 0.0),
                ],
                [
                    (0.0, 150.0, 0.0),
                    (150.0, 150.0, 0.0),
                ],
            ],
        },
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_engine."
        "AtlasInputQualityReport.build",
        lambda **kwargs: {},
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_engine."
        "AtlasInputQualityReport.evaluate_policy",
        lambda report: {},
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_engine."
        "AtlasInputQualityReport.enforce_policy",
        lambda **kwargs: None,
    )

    monkeypatch.setattr(
        AtlasFoundationFirstEngine,
        "_build_water_polygon_groups",
        staticmethod(
            lambda **kwargs: {
                "coastline": [],
                "inland": [],
            }
        ),
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_engine."
        "AtlasWaterFoundationBuilder.build_coastline_water_meshes",
        lambda **kwargs: [],
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_engine."
        "AtlasWaterFoundationBuilder.build_inland_water_meshes",
        lambda **kwargs: [],
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_engine."
        "AtlasLandmarkFoundationBuilder.build_landmarks",
        lambda **kwargs: [
            {
                "landmark_id": 100,
                "foundation_z": 0.50,
                "road_approaches": (),
                "triangles": [
                    (
                        (10.0, 10.0, 0.50),
                        (11.0, 10.0, 0.50),
                        (10.0, 11.0, 0.50),
                    ),
                ],
            },
        ],
    )

    original_attach = (
        AtlasFoundationFirstEngine
        .attach_bridge_urban_integration
    )

    captured = {}

    def capture_attachment(**kwargs):
        result = original_attach(**kwargs)
        captured.update(result)
        raise StopAfterBridgeIntegration

    monkeypatch.setattr(
        AtlasFoundationFirstEngine,
        "attach_bridge_urban_integration",
        staticmethod(capture_attachment),
    )

    try:
        AtlasFoundationFirstEngine.generate_city_stl(
            pbf_path="dummy.osm.pbf",
            bbox=(
                50.0,
                8.0,
                50.1,
                8.1,
            ),
            output_path="/tmp/dummy_bridge_811.stl",
            target_size_mm=150.0,
            z_scale=5500.0,
            nature_provider_names=(),
            debug=False,
        )
    except StopAfterBridgeIntegration:
        pass
    else:
        raise AssertionError(
            "Bridge urban integration attachment was not reached"
        )

    assert captured[
        "bridge_urban_integration_records"
    ] == 1

    record = captured[
        "bridge_urban_integration"
    ][0]

    assert record["bridge_element_id"] == "bridge_100"
    assert record["foundation_z"] == 0.50
    assert record["existing_bridge_topology_preserved"] is True
    assert record["bridge_geometry_rewritten"] is False
