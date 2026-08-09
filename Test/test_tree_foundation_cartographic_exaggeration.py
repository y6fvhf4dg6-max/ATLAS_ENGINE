import random

import pytest

from CORE.atlas_lod_level_catalog import (
    AtlasLoDLevelCatalog,
)
from CORE.atlas_tree_foundation_builder import (
    AtlasTreeFoundationBuilder,
)


def test_park_tree_symbol_can_use_explicit_source_diameter_for_cartographic_exaggeration():
    result = (
        AtlasTreeFoundationBuilder
        ._resolve_park_tree_symbol_diameter_mm(
            source_diameter_m=1.0,
            scale_ratio=5500.0,
            product_size_mm=150.0,
            nozzle_diameter_mm=0.60,
            minimum_printable_width_mm=(
                AtlasTreeFoundationBuilder
                .PARK_TREE_SYMBOL_MIN_DIAMETER_MM
            ),
            lod_level=(
                AtlasLoDLevelCatalog.resolve(2)
            ),
        )
    )

    assert result.physical_width_mm == pytest.approx(
        0.60
    )
    assert result.strict_scale_width_mm == pytest.approx(
        1.0 * 1000.0 / 5500.0
    )
    assert result.exaggerated is True
    assert result.semantic_class == (
        "vegetation_element"
    )


def test_park_tree_symbol_preserves_readable_explicit_source_diameter():
    result = (
        AtlasTreeFoundationBuilder
        ._resolve_park_tree_symbol_diameter_mm(
            source_diameter_m=8.0,
            scale_ratio=5500.0,
            product_size_mm=150.0,
            nozzle_diameter_mm=0.40,
            minimum_printable_width_mm=(
                AtlasTreeFoundationBuilder
                .PARK_TREE_SYMBOL_MIN_DIAMETER_MM
            ),
            lod_level=(
                AtlasLoDLevelCatalog.resolve(2)
            ),
        )
    )

    assert result.strict_scale_width_mm == pytest.approx(
        8.0 * 1000.0 / 5500.0
    )
    assert result.physical_width_mm == pytest.approx(
        8.0 * 1000.0 / 5500.0
    )
    assert result.exaggerated is False


def test_park_tree_symbol_keeps_legacy_dimensions_without_source_diameter():
    rng = random.Random(1234)

    dimensions = (
        AtlasTreeFoundationBuilder
        ._park_tree_symbol_dimensions(
            rng
        )
    )

    assert (
        AtlasTreeFoundationBuilder
        .PARK_TREE_SYMBOL_MIN_DIAMETER_MM
        <= dimensions["diameter_mm"]
        <= AtlasTreeFoundationBuilder
        .PARK_TREE_SYMBOL_MAX_DIAMETER_MM
    )
    assert (
        AtlasTreeFoundationBuilder
        .PARK_TREE_SYMBOL_MIN_HEIGHT_MM
        <= dimensions["height_mm"]
        <= AtlasTreeFoundationBuilder
        .PARK_TREE_SYMBOL_MAX_HEIGHT_MM
    )


def test_park_tree_symbol_uses_osm_crown_diameter_when_cartographic_context_exists(
    monkeypatch,
):
    captured = {}

    class FakeResult:
        physical_width_mm = 0.75

    monkeypatch.setattr(
        AtlasTreeFoundationBuilder,
        "_resolve_park_tree_symbol_diameter_mm",
        staticmethod(
            lambda **kwargs: (
                captured.update(kwargs)
                or FakeResult()
            )
        ),
    )

    rng = random.Random(1234)

    dimensions = (
        AtlasTreeFoundationBuilder
        ._park_tree_symbol_dimensions(
            rng,
            tree={
                "tags": {
                    "natural": "tree",
                    "diameter_crown": "1.5",
                },
            },
            scale_ratio=5500.0,
            product_size_mm=150.0,
            nozzle_diameter_mm=0.60,
            lod_level=(
                AtlasLoDLevelCatalog.resolve(2)
            ),
        )
    )

    assert captured["source_diameter_m"] == pytest.approx(
        1.5
    )
    assert dimensions["diameter_mm"] == pytest.approx(
        0.75
    )


def test_park_tree_symbol_without_crown_diameter_keeps_legacy_dimension_path(
    monkeypatch,
):
    called = []

    monkeypatch.setattr(
        AtlasTreeFoundationBuilder,
        "_resolve_park_tree_symbol_diameter_mm",
        staticmethod(
            lambda **kwargs: called.append(kwargs)
        ),
    )

    rng = random.Random(1234)

    dimensions = (
        AtlasTreeFoundationBuilder
        ._park_tree_symbol_dimensions(
            rng,
            tree={
                "tags": {
                    "natural": "tree",
                },
            },
            scale_ratio=5500.0,
            product_size_mm=150.0,
            nozzle_diameter_mm=0.60,
            lod_level=(
                AtlasLoDLevelCatalog.resolve(2)
            ),
        )
    )

    assert called == []
    assert (
        AtlasTreeFoundationBuilder
        .PARK_TREE_SYMBOL_MIN_DIAMETER_MM
        <= dimensions["diameter_mm"]
        <= AtlasTreeFoundationBuilder
        .PARK_TREE_SYMBOL_MAX_DIAMETER_MM
    )


def test_build_tree_mesh_propagates_cartographic_context_to_park_tree_symbol(
    monkeypatch,
):
    captured = {}

    monkeypatch.setattr(
        AtlasTreeFoundationBuilder,
        "_select_tree_kind",
        staticmethod(
            lambda tree, rng: "park_tree_symbol"
        ),
    )

    def fake_build_symbol(
        x,
        y,
        base_z,
        rng,
        **kwargs,
    ):
        captured.update(kwargs)
        return []

    monkeypatch.setattr(
        AtlasTreeFoundationBuilder,
        "_build_park_tree_symbol",
        staticmethod(fake_build_symbol),
    )

    monkeypatch.setattr(
        "CORE.atlas_tree_foundation_builder."
        "AtlasFoundationSampler.terrain_z_at_xy",
        lambda **kwargs: 0.0,
    )

    coordinate_engine = type(
        "CoordinateEngine",
        (),
        {
            "xy_scale": 5500.0,
            "latlon_to_stl_mm": staticmethod(
                lambda lat, lon: (10.0, 10.0)
            ),
        },
    )()

    AtlasTreeFoundationBuilder._build_tree_mesh(
        tree={
            "id": 100,
            "lat": 50.0,
            "lon": 8.0,
            "tree_kind": "park_tree_symbol",
            "tags": {
                "natural": "tree",
                "diameter_crown": "1.5",
            },
        },
        index=0,
        coordinate_engine=coordinate_engine,
        terrain_mesh=object(),
        cartographic_product_size_mm=150.0,
        cartographic_nozzle_diameter_mm=0.60,
        cartographic_lod_level=(
            AtlasLoDLevelCatalog.resolve(2)
        ),
    )

    assert captured["tree"]["id"] == 100
    assert captured["scale_ratio"] == pytest.approx(
        5500.0
    )
    assert captured["product_size_mm"] == pytest.approx(
        150.0
    )
    assert captured["nozzle_diameter_mm"] == pytest.approx(
        0.60
    )
    assert captured["lod_level"].level == 2


def test_build_tree_mesh_keeps_cartographic_context_optional(
    monkeypatch,
):
    monkeypatch.setattr(
        AtlasTreeFoundationBuilder,
        "_select_tree_kind",
        staticmethod(
            lambda tree, rng: "park_tree_symbol"
        ),
    )

    monkeypatch.setattr(
        AtlasTreeFoundationBuilder,
        "_build_park_tree_symbol",
        staticmethod(
            lambda x, y, base_z, rng: []
        ),
    )

    monkeypatch.setattr(
        "CORE.atlas_tree_foundation_builder."
        "AtlasFoundationSampler.terrain_z_at_xy",
        lambda **kwargs: 0.0,
    )

    coordinate_engine = type(
        "CoordinateEngine",
        (),
        {
            "xy_scale": 5500.0,
            "latlon_to_stl_mm": staticmethod(
                lambda lat, lon: (10.0, 10.0)
            ),
        },
    )()

    mesh = (
        AtlasTreeFoundationBuilder
        ._build_tree_mesh(
            tree={
                "id": 101,
                "lat": 50.0,
                "lon": 8.0,
                "tree_kind": "park_tree_symbol",
                "tags": {
                    "natural": "tree",
                },
            },
            index=0,
            coordinate_engine=coordinate_engine,
            terrain_mesh=object(),
        )
    )

    assert mesh is not None


def test_build_park_tree_symbol_uses_cartographic_resolved_diameter(
    monkeypatch,
):
    captured = {}

    monkeypatch.setattr(
        AtlasTreeFoundationBuilder,
        "_park_tree_symbol_dimensions",
        staticmethod(
            lambda rng, **kwargs: (
                captured.update(kwargs)
                or {
                    "height_mm": 1.20,
                    "diameter_mm": 0.80,
                }
            )
        ),
    )

    triangles = (
        AtlasTreeFoundationBuilder
        ._build_park_tree_symbol(
            x=10.0,
            y=20.0,
            base_z=2.0,
            rng=random.Random(1234),
            tree={
                "id": 100,
                "tags": {
                    "natural": "tree",
                    "diameter_crown": "1.5",
                },
            },
            scale_ratio=5500.0,
            product_size_mm=150.0,
            nozzle_diameter_mm=0.60,
            lod_level=(
                AtlasLoDLevelCatalog.resolve(2)
            ),
        )
    )

    assert captured["tree"]["id"] == 100
    assert captured["scale_ratio"] == pytest.approx(
        5500.0
    )
    assert captured["product_size_mm"] == pytest.approx(
        150.0
    )
    assert captured["nozzle_diameter_mm"] == pytest.approx(
        0.60
    )
    assert captured["lod_level"].level == 2
    assert triangles


def test_build_park_tree_symbol_keeps_legacy_signature():
    triangles = (
        AtlasTreeFoundationBuilder
        ._build_park_tree_symbol(
            x=10.0,
            y=20.0,
            base_z=2.0,
            rng=random.Random(1234),
        )
    )

    assert triangles


def test_build_trees_propagates_cartographic_context_to_each_tree(
    monkeypatch,
):
    captured = []

    monkeypatch.setattr(
        AtlasTreeFoundationBuilder,
        "_build_tree_mesh",
        staticmethod(
            lambda **kwargs: (
                captured.append(kwargs)
                or {
                    "triangles": (),
                }
            )
        ),
    )

    lod_level = AtlasLoDLevelCatalog.resolve(2)

    meshes = AtlasTreeFoundationBuilder.build_trees(
        trees=[
            {
                "id": 100,
                "lat": 50.0,
                "lon": 8.0,
            },
        ],
        coordinate_engine=object(),
        terrain_mesh=object(),
        cartographic_product_size_mm=150.0,
        cartographic_nozzle_diameter_mm=0.60,
        cartographic_lod_level=lod_level,
        debug=False,
    )

    assert len(meshes) == 1
    assert len(captured) == 1

    assert captured[0][
        "cartographic_product_size_mm"
    ] == pytest.approx(150.0)

    assert captured[0][
        "cartographic_nozzle_diameter_mm"
    ] == pytest.approx(0.60)

    assert (
        captured[0]["cartographic_lod_level"]
        is lod_level
    )
