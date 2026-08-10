from pathlib import Path


def _source():
    return Path(
        "CORE/atlas_foundation_first_engine.py"
    ).read_text()


def test_generate_city_imports_scene_morphology_components():
    source = _source()

    assert (
        "AtlasSceneMorphologyEvidenceResolver"
        in source
    )

    assert (
        "AtlasSceneMorphologyClassifier"
        in source
    )

    assert (
        "AtlasSceneMorphologyMeshAreaResolver"
        in source
    )


def test_generate_city_resolves_scene_morphology_evidence():
    source = _source()

    assert (
        "scene_morphology_evidence"
        in source
    )

    assert (
        "building_footprint_area_mm2"
        in source
    )

    assert (
        "road_surface_area_mm2"
        in source
    )

    assert (
        "water_area_mm2"
        in source
    )


def test_generate_city_resolves_scene_morphology_classification():
    source = _source()

    assert (
        "resolved_scene_morphology"
        in source
    )

    assert (
        "AtlasSceneMorphologyClassifier.resolve"
        in source
    )


def test_generate_city_returns_scene_morphology_metadata():
    source = _source()

    assert (
        '"scene_morphology_evidence"'
        in source
    )

    assert (
        '"resolved_scene_morphology"'
        in source
    )


def test_scene_morphology_selection_uses_classifier_when_explicit_value_missing():
    from CORE.atlas_foundation_first_engine import (
        AtlasFoundationFirstEngine,
    )

    assert (
        AtlasFoundationFirstEngine
        ._select_scene_morphology(
            explicit_scene_morphology=None,
            classified_scene_morphology="dense_urban",
        )
        == "dense_urban"
    )


def test_scene_morphology_selection_preserves_explicit_override():
    from CORE.atlas_foundation_first_engine import (
        AtlasFoundationFirstEngine,
    )

    assert (
        AtlasFoundationFirstEngine
        ._select_scene_morphology(
            explicit_scene_morphology="historic_core",
            classified_scene_morphology="dense_urban",
        )
        == "historic_core"
    )


def test_city_composition_uses_effective_scene_morphology():
    source = _source()

    assert (
        "effective_scene_morphology"
        in source
    )

    assert (
        "scene_morphology=("
        in source
    )

    assert (
        "effective_scene_morphology"
        in source[
            source.index(
                "AtlasCityCompositionLoDResolver"
            ):
        ]
    )


def test_generate_city_runtime_uses_classified_morphology_when_explicit_missing(
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
            "top_points": [],
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
        "AtlasSceneMorphologyClassifier.resolve",
        lambda **kwargs: {
            "morphology": "river_city",
            "confidence": 0.91,
            "scores": {},
            "evidence": kwargs,
        },
    )

    captured = {}

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_engine."
        "AtlasCityCompositionLoDResolver."
        "resolve_urban_fabric_scene",
        lambda **kwargs: (
            captured.update(kwargs)
            or {
                "decisions": {},
                "scene_morphology": (
                    kwargs["scene_morphology"]
                ),
            }
        ),
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_engine."
        "AtlasSTLWriter.write",
        lambda meshes, output_path: None,
    )

    result = AtlasFoundationFirstEngine.generate_city_stl(
        pbf_path="dummy.osm.pbf",
        bbox=(
            50.0,
            8.0,
            50.1,
            8.1,
        ),
        output_path="/tmp/dummy_morphology_815.stl",
        target_size_mm=100.0,
        z_scale=5500.0,
        nature_provider_names=(),
        city_composition_lod_level=1,
        scene_morphology=None,
        debug=False,
    )

    assert result[
        "resolved_scene_morphology"
    ] == "river_city"

    assert result[
        "effective_scene_morphology"
    ] == "river_city"

    assert captured[
        "scene_morphology"
    ] == "river_city"
