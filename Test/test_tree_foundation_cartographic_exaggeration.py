import random

import pytest

from CORE.atlas_lod_level_catalog import (
    AtlasLoDLevelCatalog,
)
from CORE.atlas_tree_foundation_builder import (
    AtlasTreeFoundationBuilder,
)


def test_canonical_tree_can_use_explicit_source_diameter_for_cartographic_exaggeration():
    result = (
        AtlasTreeFoundationBuilder
        ._resolve_canonical_tree_diameter_mm(
            source_diameter_m=1.0,
            scale_ratio=5500.0,
            product_size_mm=150.0,
            nozzle_diameter_mm=0.60,
            minimum_printable_width_mm=(
                AtlasTreeFoundationBuilder
                .CANONICAL_TREE_MIN_CROWN_DIAMETER_MM
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


def test_canonical_tree_preserves_readable_explicit_source_diameter():
    result = (
        AtlasTreeFoundationBuilder
        ._resolve_canonical_tree_diameter_mm(
            source_diameter_m=8.0,
            scale_ratio=5500.0,
            product_size_mm=150.0,
            nozzle_diameter_mm=0.40,
            minimum_printable_width_mm=(
                AtlasTreeFoundationBuilder
                .CANONICAL_TREE_MIN_CROWN_DIAMETER_MM
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


def test_build_tree_mesh_propagates_cartographic_context_to_canonical_tree(
    monkeypatch,
):
    captured = {}

    def fake_build_canonical_tree(
        *,
        x,
        y,
        base_z,
        **kwargs,
    ):
        captured.update(kwargs)

        return {
            "triangles": [],
        }

    monkeypatch.setattr(
        AtlasTreeFoundationBuilder,
        "_build_canonical_tree",
        staticmethod(fake_build_canonical_tree),
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
            "tags": {
                "natural": "tree",
                "diameter_crown": "1.5",
            },
        },
        index=0,
        coordinate_engine=coordinate_engine,
        terrain_mesh={
            "triangles": [
                (
                    (0.0, 0.0, 0.0),
                    (150.0, 0.0, 0.0),
                    (150.0, 150.0, 0.0),
                ),
                (
                    (0.0, 0.0, 0.0),
                    (150.0, 150.0, 0.0),
                    (0.0, 150.0, 0.0),
                ),
            ],
        },
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
        "_build_canonical_tree",
        staticmethod(
            lambda **kwargs: {
                "triangles": [],
            }
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
            terrain_mesh={
            "triangles": [
                (
                    (0.0, 0.0, 0.0),
                    (150.0, 0.0, 0.0),
                    (150.0, 150.0, 0.0),
                ),
                (
                    (0.0, 0.0, 0.0),
                    (150.0, 150.0, 0.0),
                    (0.0, 150.0, 0.0),
                ),
            ],
        },
        )
    )

    assert mesh is not None


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
