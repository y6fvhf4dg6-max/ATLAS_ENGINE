import inspect

from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)


def test_foundation_first_engine_exposes_optional_road_print_minimum():
    signature = inspect.signature(
        AtlasFoundationFirstEngine.generate_city_stl
    )

    parameter = signature.parameters[
        "road_minimum_printable_width_mm"
    ]

    assert parameter.default is None


def test_foundation_first_engine_exposes_tree_row_nozzle_diameter():
    signature = inspect.signature(
        AtlasFoundationFirstEngine.generate_city_stl
    )

    parameter = signature.parameters[
        "tree_row_nozzle_diameter_mm"
    ]

    assert parameter.default == 0.4


def test_foundation_first_engine_exposes_terrain_grid_size():
    signature = inspect.signature(
        AtlasFoundationFirstEngine.generate_city_stl
    )

    parameter = signature.parameters[
        "terrain_grid_size"
    ]

    assert parameter.default == 25


def test_foundation_first_engine_forwards_terrain_grid_size(
    monkeypatch,
):
    captured = {}

    class TerrainCallReached(Exception):
        pass

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_engine."
        "AtlasLocalOSMReader.read",
        lambda *args, **kwargs: {},
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

    def fake_build_terrain_slab(**kwargs):
        captured.update(kwargs)
        raise TerrainCallReached

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_engine."
        "AtlasTerrainPipeline.build_terrain_slab",
        fake_build_terrain_slab,
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
            output_path="/tmp/dummy.stl",
            target_size_mm=150.0,
            z_scale=5500.0,
            terrain_grid_size=97,
            nature_provider_names=(),
            debug=False,
        )
    except TerrainCallReached:
        pass
    else:
        raise AssertionError(
            "Terrain pipeline call was not reached"
        )

    assert captured["grid_size"] == 97


def test_foundation_first_engine_exposes_presentation_regularization():
    signature = inspect.signature(
        AtlasFoundationFirstEngine.generate_city_stl
    )

    assert (
        signature.parameters[
            "terrain_presentation_regularization_passes"
        ].default
        == 0
    )

    assert (
        signature.parameters[
            "terrain_presentation_regularization_strength"
        ].default
        == 0.50
    )
