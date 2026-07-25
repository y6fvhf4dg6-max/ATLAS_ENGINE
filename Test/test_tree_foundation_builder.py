import random

from CORE.atlas_tree_foundation_builder import (
    AtlasTreeFoundationBuilder,
)


def test_round_tree_builds_closed_printable_mesh():
    triangles = AtlasTreeFoundationBuilder._build_round_tree(
        x=10.0,
        y=20.0,
        base_z=3.0,
        rng=random.Random(1234),
    )

    assert triangles
    assert len(triangles) > 0

    z_values = [
        point[2]
        for triangle in triangles
        for point in triangle
    ]

    assert min(z_values) == 3.0
    assert max(z_values) > 3.0


def test_round_tree_is_deterministic_for_same_seed():
    first = AtlasTreeFoundationBuilder._build_round_tree(
        x=10.0,
        y=20.0,
        base_z=3.0,
        rng=random.Random(1234),
    )

    second = AtlasTreeFoundationBuilder._build_round_tree(
        x=10.0,
        y=20.0,
        base_z=3.0,
        rng=random.Random(1234),
    )

    assert first == second


def test_round_crown_profile_has_natural_tapered_silhouette():
    profile = (
        AtlasTreeFoundationBuilder
        ._round_crown_profile(
            crown_radius=1.0,
            crown_height=2.0,
        )
    )

    assert profile == [
        (0.00, 0.28),
        (0.16, 0.68),
        (0.38, 1.00),
        (0.64, 0.82),
        (0.84, 0.46),
        (1.00, 0.00),
    ]


def test_round_crown_profile_is_monotonic_in_height():
    profile = (
        AtlasTreeFoundationBuilder
        ._round_crown_profile(
            crown_radius=1.5,
            crown_height=3.0,
        )
    )

    heights = [height for height, _radius in profile]

    assert heights == sorted(heights)
    assert heights[0] == 0.0
    assert heights[-1] == 1.0


def test_round_tree_crown_uses_deterministic_asymmetric_lobes():
    lobes = AtlasTreeFoundationBuilder._round_crown_lobes(
        rng=random.Random(1234),
    )

    assert len(lobes) == 4

    assert lobes == (
        AtlasTreeFoundationBuilder._round_crown_lobes(
            rng=random.Random(1234),
        )
    )

    assert any(
        abs(lobe["offset_x"]) > 0.0
        or abs(lobe["offset_y"]) > 0.0
        for lobe in lobes
    )

    assert len({
        round(lobe["radius_scale"], 6)
        for lobe in lobes
    }) > 1


def test_park_tree_symbol_profile_is_compact_and_grounded():
    profile = (
        AtlasTreeFoundationBuilder
        ._park_tree_symbol_profile()
    )

    assert profile == [
        (0.00, 0.52),
        (0.22, 0.78),
        (0.52, 1.00),
        (0.78, 0.64),
        (1.00, 0.00),
    ]


def test_park_tree_symbol_uses_printable_dimensions():
    dimensions = (
        AtlasTreeFoundationBuilder
        ._park_tree_symbol_dimensions(
            rng=random.Random(1234),
        )
    )

    assert 1.0 <= dimensions["height_mm"] <= 1.4
    assert 0.60 <= dimensions["diameter_mm"] <= 1.10


def test_worldcover_tree_selects_park_tree_symbol():
    tree = {
        "id": "worldcover_1",
        "lat": 50.0,
        "lon": 8.0,
        "tags": {
            "source": "worldcover",
        },
    }

    result = AtlasTreeFoundationBuilder._select_tree_kind(
        tree=tree,
        rng=random.Random(1234),
    )

    assert result == "park_tree_symbol"


def test_park_tree_symbol_builds_grounded_single_piece_mesh():
    triangles = (
        AtlasTreeFoundationBuilder
        ._build_park_tree_symbol(
            x=10.0,
            y=20.0,
            base_z=3.0,
            rng=random.Random(1234),
        )
    )

    assert triangles

    z_values = [
        point[2]
        for triangle in triangles
        for point in triangle
    ]

    assert min(z_values) == 3.0
    assert 4.0 <= max(z_values) <= 4.4


def test_park_tree_symbol_is_deterministic():
    first = AtlasTreeFoundationBuilder._build_park_tree_symbol(
        x=10.0,
        y=20.0,
        base_z=3.0,
        rng=random.Random(1234),
    )

    second = AtlasTreeFoundationBuilder._build_park_tree_symbol(
        x=10.0,
        y=20.0,
        base_z=3.0,
        rng=random.Random(1234),
    )

    assert first == second


def test_tree_mesh_preserves_source_metadata():
    class CoordinateEngineStub:
        @staticmethod
        def latlon_to_stl_mm(lat, lon):
            return 10.0, 20.0

    tree = {
        "id": "green_fill_1",
        "lat": 50.0,
        "lon": 8.0,
        "tree_type": "tree",
        "tags": {
            "source": "osm_green_area_fill",
            "park_id": 101,
            "park_type": "landuse:forest",
        },
    }

    terrain_mesh = {
        "triangles": [
            (
                (0.0, 0.0, 1.0),
                (200.0, 0.0, 1.0),
                (0.0, 200.0, 1.0),
            ),
            (
                (200.0, 0.0, 1.0),
                (200.0, 200.0, 1.0),
                (0.0, 200.0, 1.0),
            ),
        ],
    }

    result = AtlasTreeFoundationBuilder._build_tree_mesh(
        tree=tree,
        index=0,
        coordinate_engine=CoordinateEngineStub(),
        terrain_mesh=terrain_mesh,
    )

    assert result["tree_id"] == "green_fill_1"
    assert result["source"] == "osm_green_area_fill"
    assert result["tags"] == tree["tags"]
    assert result["tags"] is not tree["tags"]


def test_osm_source_tag_url_is_not_used_as_provider_source():
    tree = {
        "id": 123,
        "lat": 50.0,
        "lon": 8.0,
        "tags": {
            "source": "https://www.mapillary.com/example",
        },
    }

    source = AtlasTreeFoundationBuilder._resolve_source(tree)

    assert source == "osm"


def test_known_generated_tree_source_is_preserved():
    tree = {
        "id": "fill_1",
        "lat": 50.0,
        "lon": 8.0,
        "tags": {
            "source": "osm_green_area_fill",
        },
    }

    source = AtlasTreeFoundationBuilder._resolve_source(tree)

    assert source == "osm_green_area_fill"
