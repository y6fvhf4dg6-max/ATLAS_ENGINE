from pathlib import Path


def _source():
    return Path(
        "CORE/atlas_foundation_first_engine.py"
    ).read_text()


def test_generate_city_builds_city_composition_scene():
    source = _source()

    assert (
        "AtlasCityCompositionSceneAdapter"
        in source
    )

    assert (
        "city_composition_scene"
        in source
    )


def test_generate_city_resolves_city_composition_lod():
    source = _source()

    assert (
        "AtlasCityCompositionLoDResolver"
        in source
    )

    assert (
        "city_composition_lod"
        in source
    )


def test_generate_city_exposes_city_composition_context():
    source = _source()

    assert (
        "city_composition_lod_level="
        in source
    )

    assert (
        "scene_morphology="
        in source
    )


def test_generate_city_returns_city_composition_lod_metadata():
    source = _source()

    assert (
        '"city_composition_lod"'
        in source
    )

    assert (
        '"city_composition_scene"'
        in source
    )


def test_generate_city_applies_city_composition_before_final_stl():
    source = _source()

    assert (
        "AtlasCityCompositionMeshFilter"
        in source
    )

    assert (
        "city_composition_mesh_filter_result"
        in source
    )

    assert (
        '"city_composition_suppressed_meshes"'
        in source
    )


def test_generate_city_runtime_suppresses_minor_path_before_stl(
    monkeypatch,
):
    from CORE.atlas_foundation_first_engine import (
        AtlasFoundationFirstEngine,
    )

    fake_data = {
        "buildings": [],
        "landmarks": [],
        "trees": [],
        "tree_rows": [],
        "roads": [],
        "pedestrian_paths": [
            {
                "id": 9001,
                "road_type": "pedestrian",
                "geometry": (
                    (50.0000, 8.0000),
                    (50.0001, 8.0001),
                ),
                "tags": {
                    "highway": "pedestrian",
                },
            },
        ],
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
                "size_mm": 100.0,
                "size_x_mm": 100.0,
                "size_y_mm": 100.0,
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
                    (100.0, 0.0, 0.8),
                ],
                [
                    (0.0, 100.0, 0.8),
                    (100.0, 100.0, 0.8),
                ],
            ],
            "bottom_points": [],
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
        "AtlasWaterFoundationBuilder."
        "build_coastline_water_meshes",
        lambda **kwargs: [],
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_engine."
        "AtlasWaterFoundationBuilder."
        "build_inland_water_meshes",
        lambda **kwargs: [],
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_engine."
        "AtlasRoadFoundationBuilder.build_roads",
        lambda **kwargs: [
            {
                "source_id": 9001,
                "road_type": "pedestrian",
                "type": "road_foundation",
                "triangles": [
                    (
                        (0.0, 0.0, 1.0),
                        (1.0, 0.0, 1.0),
                        (0.0, 1.0, 1.0),
                    ),
                ],
            },
        ],
    )

    written = {}

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_engine."
        "AtlasSTLWriter.write",
        lambda meshes, output_path: (
            written.update(
                {
                    "meshes": list(meshes),
                    "output_path": output_path,
                }
            )
        ),
    )

    result = AtlasFoundationFirstEngine.generate_city_stl(
        pbf_path="dummy.osm.pbf",
        bbox=(
            50.0,
            8.0,
            50.1,
            8.1,
        ),
        output_path="/tmp/dummy_city_lod_814.stl",
        target_size_mm=100.0,
        z_scale=5500.0,
        nature_provider_names=(),
        city_composition_lod_level=1,
        scene_morphology="dense_urban",
        debug=False,
    )

    assert (
        result["city_composition_lod"][
            "decisions"
        ]["road_9001"]["retain"]
        is False
    )

    assert result[
        "city_composition_suppressed_meshes"
    ] == 1

    assert result["mesh_groups"]["roads"] == []

    assert all(
        mesh.get("source_id") != 9001
        for mesh in written["meshes"]
        if isinstance(mesh, dict)
    )
