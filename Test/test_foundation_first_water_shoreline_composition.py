from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)


def test_foundation_first_attaches_water_shoreline_composition_records():
    result = {
        "mode": "foundation_first",
    }

    waters = [
        {
            "id": 1,
            "geometry": (
                (50.0, 8.0),
                (50.0, 8.1),
                (50.1, 8.1),
            ),
            "tags": {
                "waterway": "river",
            },
        },
    ]

    coastlines = [
        {
            "id": 2,
            "geometry": (
                (50.2, 8.0),
                (50.2, 8.1),
            ),
            "tags": {
                "natural": "coastline",
            },
        },
    ]

    waterfront_structures = [
        {
            "id": 3,
            "geometry": (
                (50.3, 8.0),
                (50.3, 8.1),
            ),
            "tags": {
                "man_made": "quay",
            },
            "waterfront_type": "quay",
        },
    ]

    resolved = (
        AtlasFoundationFirstEngine
        .attach_water_shoreline_composition(
            result=result,
            waters=waters,
            coastlines=coastlines,
            waterfront_structures=waterfront_structures,
        )
    )

    assert resolved is result
    assert result["reader_waterfront_structures"] == 1

    records = result["water_shoreline_composition"]

    assert [
        record["semantic_class"]
        for record in records
    ] == [
        "river",
        "coastline",
        "quay",
    ]

    assert result["water_shoreline_composition_records"] == 3


def test_foundation_first_water_shoreline_attachment_handles_empty_scene():
    result = {}

    resolved = (
        AtlasFoundationFirstEngine
        .attach_water_shoreline_composition(
            result=result,
            waters=(),
            coastlines=(),
            waterfront_structures=(),
        )
    )

    assert resolved["reader_waterfront_structures"] == 0
    assert resolved["water_shoreline_composition"] == ()
    assert resolved["water_shoreline_composition_records"] == 0


def test_generate_city_result_exposes_water_shoreline_composition(
    monkeypatch,
):
    class StopAfterResult(Exception):
        pass

    fake_data = {
        "buildings": [],
        "landmarks": [],
        "trees": [],
        "tree_rows": [],
        "roads": [
            {
                "id": 3,
                "geometry": (
                    (49.9500, 8.1000),
                    (50.0500, 8.1000),
                ),
                "tags": {
                    "highway": "primary",
                    "bridge": "yes",
                },
            },
        ],
        "pedestrian_paths": [],
        "linear_infrastructure": [
            {
                "id": 4,
                "geometry": (
                    (49.9500, 8.0500),
                    (50.0500, 8.0500),
                ),
                "tags": {
                    "railway": "rail",
                },
                "semantic_class": "railway",
            },
        ],
        "elevated_areas": [],
        "artworks": [],
        "parks": [],
        "waters": [
            {
                "id": 1,
                "geometry": (
                    (50.0, 8.0),
                    (50.0, 8.1),
                    (50.1, 8.1),
                ),
                "tags": {
                    "waterway": "river",
                },
            },
        ],
        "coastlines": [],
        "waterfront_structures": [
            {
                "id": 2,
                "geometry": (
                    (50.2, 8.0),
                    (50.2, 8.1),
                ),
                "tags": {
                    "man_made": "quay",
                },
                "waterfront_type": "quay",
            },
        ],
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

    original_attach = (
        AtlasFoundationFirstEngine
        .attach_water_shoreline_composition
    )

    captured = {}

    def capture_attachment(**kwargs):
        result = original_attach(**kwargs)
        captured.update(result)
        raise StopAfterResult

    monkeypatch.setattr(
        AtlasFoundationFirstEngine,
        "attach_water_shoreline_composition",
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
            output_path="/tmp/dummy.stl",
            target_size_mm=150.0,
            z_scale=5500.0,
            nature_provider_names=(),
            debug=False,
        )
    except StopAfterResult:
        pass
    else:
        raise AssertionError(
            "Water/shoreline composition attachment was not reached"
        )

    assert captured["reader_waterfront_structures"] == 1
    assert captured["water_shoreline_composition_records"] == 2

    assert [
        record["semantic_class"]
        for record in captured["water_shoreline_composition"]
    ] == [
        "river",
        "quay",
    ]

    river_record = captured[
        "water_shoreline_composition"
    ][0]

    assert river_record["bridge_interaction"] is True
    assert river_record["road_interaction"] is True
    assert river_record["rail_interaction"] is True


def test_foundation_first_resolves_real_water_interaction_scene_context():
    landmarks = [
        {
            "id": 10,
            "geometry": (
                (50.0, 8.0),
                (50.0, 8.1),
                (50.1, 8.1),
            ),
            "tags": {
                "man_made": "bridge",
            },
        },
    ]

    roads = [
        {
            "id": 20,
            "geometry": (
                (50.0, 8.0),
                (50.1, 8.0),
            ),
            "tags": {
                "highway": "primary",
                "bridge": "yes",
            },
        },
        {
            "id": 21,
            "geometry": (
                (50.2, 8.0),
                (50.3, 8.0),
            ),
            "tags": {
                "highway": "secondary",
            },
        },
    ]

    linear_infrastructure = [
        {
            "id": 30,
            "geometry": (
                (50.0, 8.2),
                (50.1, 8.2),
            ),
            "tags": {
                "railway": "rail",
            },
            "semantic_class": "railway",
        },
        {
            "id": 31,
            "geometry": (
                (50.0, 8.3),
                (50.1, 8.3),
            ),
            "tags": {
                "man_made": "embankment",
            },
            "semantic_class": "embankment",
        },
    ]

    context = (
        AtlasFoundationFirstEngine
        ._resolve_water_shoreline_interaction_context(
            landmarks=landmarks,
            roads=roads,
            linear_infrastructure=linear_infrastructure,
        )
    )

    assert [
        item["id"]
        for item in context["bridges"]
    ] == [
        10,
        20,
    ]

    assert [
        item["id"]
        for item in context["roads"]
    ] == [
        20,
        21,
    ]

    assert [
        item["id"]
        for item in context["railways"]
    ] == [
        30,
    ]


def test_foundation_first_attachment_propagates_scene_interaction_context():
    result = {}

    water = {
        "id": 50,
        "geometry": (
            (50.0000, 8.0000),
            (50.0000, 8.1000),
            (50.0000, 8.2000),
        ),
        "tags": {
            "waterway": "river",
        },
    }

    bridge = {
        "id": 51,
        "geometry": (
            (49.9500, 8.1000),
            (50.0500, 8.1000),
        ),
        "tags": {
            "bridge": "yes",
        },
    }

    road = {
        "id": 52,
        "geometry": (
            (49.9500, 8.1500),
            (50.0500, 8.1500),
        ),
        "tags": {
            "highway": "primary",
        },
    }

    railway = {
        "id": 53,
        "geometry": (
            (49.9500, 8.0500),
            (50.0500, 8.0500),
        ),
        "tags": {
            "railway": "rail",
        },
    }

    resolved = (
        AtlasFoundationFirstEngine
        .attach_water_shoreline_composition(
            result=result,
            waters=(water,),
            coastlines=(),
            waterfront_structures=(),
            bridges=(bridge,),
            roads=(road,),
            railways=(railway,),
        )
    )

    record = resolved[
        "water_shoreline_composition"
    ][0]

    assert record["bridge_interaction"] is True
    assert record["road_interaction"] is True
    assert record["rail_interaction"] is True
