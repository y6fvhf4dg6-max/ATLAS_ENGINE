import random

import pytest

from CORE.atlas_tree_foundation_builder import (
    AtlasTreeFoundationBuilder,
)


def test_worldcover_tree_selects_canonical_tree():
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

    assert result == "canonical"


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


def test_tree_kind_override_still_resolves_to_canonical_tree():
    tree = {
        "id": "formal_row_1_0",
        "lat": 50.0,
        "lon": 8.0,
        "tree_kind": "park_tree_symbol",
        "tags": {
            "source": "osm_tree_row",
        },
    }

    result = AtlasTreeFoundationBuilder._select_tree_kind(
        tree=tree,
        rng=random.Random(1234),
    )

    assert result == "canonical"


def test_all_tree_sources_resolve_to_single_canonical_tree_kind():
    sources = (
        {
            "id": "osm_tree",
            "tree_type": "tree",
            "tags": {
                "natural": "tree",
            },
        },
        {
            "id": "worldcover_tree",
            "tree_type": "tree",
            "tags": {
                "source": "worldcover",
            },
        },
        {
            "id": "conifer_tagged_tree",
            "tree_type": "tree",
            "tags": {
                "natural": "tree",
                "leaf_type": "needleleaved",
            },
        },
        {
            "id": "tree_row_member",
            "tree_type": "tree",
            "tree_kind": "park_tree_symbol",
            "tags": {
                "source": "osm_tree_row",
            },
        },
    )

    resolved = {
        AtlasTreeFoundationBuilder._select_tree_kind(
            tree=tree,
            rng=random.Random(1234),
        )
        for tree in sources
    }

    assert resolved == {"canonical"}


def test_canonical_tree_exposes_single_printable_dimension_contract():
    dimensions = (
        AtlasTreeFoundationBuilder
        ._canonical_tree_dimensions()
    )

    assert dimensions["total_height_mm"] > 0.0
    assert dimensions["trunk_height_mm"] > 0.0
    assert dimensions["trunk_diameter_mm"] > 0.0
    assert dimensions["crown_height_mm"] > 0.0
    assert dimensions["crown_diameter_mm"] > 0.0

    assert (
        dimensions["trunk_height_mm"]
        + dimensions["crown_height_mm"]
        == pytest.approx(
            dimensions["total_height_mm"]
        )
    )

    assert (
        dimensions["trunk_diameter_mm"]
        < dimensions["crown_diameter_mm"]
    )


def test_canonical_tree_meets_physical_v1_print_minimums():
    dimensions = (
        AtlasTreeFoundationBuilder
        ._canonical_tree_dimensions()
    )

    assert dimensions["trunk_diameter_mm"] >= 1.50
    assert dimensions["root_collar_diameter_mm"] == pytest.approx(2.20)
    assert dimensions["root_collar_height_mm"] == pytest.approx(0.80)
    assert dimensions["terrain_embed_depth_mm"] == pytest.approx(0.60)
    assert dimensions["crown_diameter_mm"] >= 3.5
    assert dimensions["total_height_mm"] >= 5.0


def test_worldcover_tree_physical_scale_variant_is_deterministic():
    tree = {
        "id": "worldcover_product_123",
        "tags": {
            "source": "worldcover",
        },
    }

    first = (
        AtlasTreeFoundationBuilder
        ._resolve_physical_tree_scale(tree)
    )
    second = (
        AtlasTreeFoundationBuilder
        ._resolve_physical_tree_scale(tree)
    )

    assert first == second
    assert first in {0.95, 1.0, 1.05}


def test_non_worldcover_tree_keeps_canonical_physical_scale():
    tree = {
        "id": "osm_tree_123",
        "tags": {
            "source": "osm",
            "natural": "tree",
        },
    }

    assert (
        AtlasTreeFoundationBuilder
        ._resolve_physical_tree_scale(tree)
        == 1.0
    )


def test_worldcover_physical_scale_variants_preserve_print_minimums():
    base = (
        AtlasTreeFoundationBuilder
        ._canonical_tree_dimensions()
    )

    for scale in (0.95, 1.0, 1.05):
        assert base["trunk_diameter_mm"] * scale >= 1.40
        assert base["crown_diameter_mm"] * scale >= 3.5
        assert base["total_height_mm"] * scale >= 5.0


def test_canonical_tree_has_visible_trunk_and_crown_above_ground():
    base_z = 3.0

    result = (
        AtlasTreeFoundationBuilder
        ._build_canonical_tree(
            x=10.0,
            y=20.0,
            base_z=base_z,
        )
    )

    assert result["triangles"]

    dimensions = result["dimensions"]

    assert result["trunk_bottom_z"] == pytest.approx(
        base_z - dimensions["terrain_embed_depth_mm"]
    )
    assert result["root_collar_bottom_z"] == pytest.approx(
        result["trunk_bottom_z"]
    )
    assert result["root_collar_top_z"] == pytest.approx(
        result["trunk_bottom_z"]
        + dimensions["root_collar_height_mm"]
    )
    assert (
        result["trunk_top_z"]
        == base_z + dimensions["trunk_height_mm"]
    )
    assert result["crown_bottom_z"] >= result["trunk_top_z"]
    assert result["crown_bottom_z"] > base_z
    assert (
        result["top_z"]
        == base_z + dimensions["total_height_mm"]
    )


def test_canonical_tree_geometry_is_deterministic():
    first = (
        AtlasTreeFoundationBuilder
        ._build_canonical_tree(
            x=10.0,
            y=20.0,
            base_z=3.0,
        )
    )

    second = (
        AtlasTreeFoundationBuilder
        ._build_canonical_tree(
            x=10.0,
            y=20.0,
            base_z=3.0,
        )
    )

    assert first == second


def test_build_tree_mesh_applies_worldcover_physical_scale_variant(monkeypatch):
    class CoordinateEngineStub:
        xy_scale = 3000.0

        @staticmethod
        def latlon_to_stl_mm(lat, lon):
            return 75.0, 75.0

    terrain_mesh = {
        "triangles": [
            (
                (0.0, 0.0, 1.0),
                (150.0, 0.0, 1.0),
                (150.0, 150.0, 1.0),
            ),
            (
                (0.0, 0.0, 1.0),
                (150.0, 150.0, 1.0),
                (0.0, 150.0, 1.0),
            ),
        ],
    }

    captured = {}

    monkeypatch.setattr(
        AtlasTreeFoundationBuilder,
        "_resolve_physical_tree_scale",
        staticmethod(lambda tree: 1.05),
    )

    monkeypatch.setattr(
        "CORE.atlas_tree_foundation_builder."
        "AtlasFoundationSampler.terrain_z_at_xy",
        lambda **kwargs: 1.0,
    )

    original = (
        AtlasTreeFoundationBuilder
        ._build_canonical_tree
    )

    def capture_build_canonical_tree(**kwargs):
        captured["physical_scale"] = kwargs.get(
            "physical_scale"
        )
        return original(**kwargs)

    monkeypatch.setattr(
        AtlasTreeFoundationBuilder,
        "_build_canonical_tree",
        staticmethod(capture_build_canonical_tree),
    )

    mesh = AtlasTreeFoundationBuilder._build_tree_mesh(
        tree={
            "id": "worldcover_product_42",
            "lat": 50.0,
            "lon": 7.0,
            "tags": {
                "source": "worldcover",
            },
        },
        index=0,
        coordinate_engine=CoordinateEngineStub(),
        terrain_mesh=terrain_mesh,
    )

    assert mesh is not None
    assert captured["physical_scale"] == pytest.approx(1.05)


def test_tree_outside_actual_terrain_bounds_is_rejected(monkeypatch):
    class CoordinateEngineStub:
        xy_scale = 3000.0

        @staticmethod
        def latlon_to_stl_mm(lat, lon):
            return 160.0, 75.0

    terrain_mesh = {
        "triangles": [
            (
                (0.0, 0.0, 1.0),
                (150.0, 0.0, 1.0),
                (150.0, 150.0, 1.0),
            ),
            (
                (0.0, 0.0, 1.0),
                (150.0, 150.0, 1.0),
                (0.0, 150.0, 1.0),
            ),
        ],
    }

    monkeypatch.setattr(
        "CORE.atlas_tree_foundation_builder."
        "AtlasFoundationSampler.terrain_z_at_xy",
        lambda **kwargs: 1.0,
    )

    result = AtlasTreeFoundationBuilder._build_tree_mesh(
        tree={
            "id": "outside_terrain",
            "lat": 50.0,
            "lon": 7.0,
            "tags": {
                "natural": "tree",
            },
        },
        index=0,
        coordinate_engine=CoordinateEngineStub(),
        terrain_mesh=terrain_mesh,
    )

    assert result is None


def test_tree_crown_must_fit_inside_actual_terrain_bounds(monkeypatch):
    class CoordinateEngineStub:
        xy_scale = 3000.0

        @staticmethod
        def latlon_to_stl_mm(lat, lon):
            return 149.5, 75.0

    terrain_mesh = {
        "triangles": [
            (
                (0.0, 0.0, 1.0),
                (150.0, 0.0, 1.0),
                (150.0, 150.0, 1.0),
            ),
            (
                (0.0, 0.0, 1.0),
                (150.0, 150.0, 1.0),
                (0.0, 150.0, 1.0),
            ),
        ],
    }

    monkeypatch.setattr(
        "CORE.atlas_tree_foundation_builder."
        "AtlasFoundationSampler.terrain_z_at_xy",
        lambda **kwargs: 1.0,
    )

    result = AtlasTreeFoundationBuilder._build_tree_mesh(
        tree={
            "id": "crown_over_edge",
            "lat": 50.0,
            "lon": 7.0,
            "tags": {
                "natural": "tree",
            },
        },
        index=0,
        coordinate_engine=CoordinateEngineStub(),
        terrain_mesh=terrain_mesh,
    )

    assert result is None

def test_canonical_tree_root_collar_strengthens_terrain_connection():
    base_z = 3.0
    result = AtlasTreeFoundationBuilder._build_canonical_tree(
        x=10.0,
        y=20.0,
        base_z=base_z,
    )
    dimensions = result["dimensions"]

    assert dimensions["root_collar_diameter_mm"] > (
        dimensions["trunk_diameter_mm"]
    )
    assert result["trunk_bottom_z"] < base_z
    assert result["root_collar_bottom_z"] < base_z
    assert result["root_collar_top_z"] > base_z

    vertices = [
        point
        for triangle in result["triangles"]
        for point in triangle
    ]
    collar_radius = dimensions["root_collar_diameter_mm"] / 2.0

    assert any(
        abs(z - result["root_collar_bottom_z"]) < 1e-9
        and abs(((x - 10.0) ** 2 + (y - 20.0) ** 2) ** 0.5 - collar_radius)
        < 1e-6
        for x, y, z in vertices
    )


def test_strengthened_tree_preserves_visible_product_height():
    base_z = 3.0
    result = AtlasTreeFoundationBuilder._build_canonical_tree(
        x=10.0,
        y=20.0,
        base_z=base_z,
    )

    assert result["top_z"] == pytest.approx(
        base_z + result["dimensions"]["total_height_mm"]
    )

def test_strengthened_canonical_tree_is_closed_and_manifold():
    from CORE.atlas_mesh_validator import AtlasMeshValidator

    mesh = AtlasTreeFoundationBuilder._build_canonical_tree(
        x=10.0,
        y=20.0,
        base_z=3.0,
    )
    report = AtlasMeshValidator._topology_report(mesh)

    assert report["edge_count"] > 0
    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0
