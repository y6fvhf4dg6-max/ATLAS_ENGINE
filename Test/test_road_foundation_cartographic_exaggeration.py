import pytest

from CORE.atlas_coordinate_engine import (
    AtlasCoordinateEngine,
)
from CORE.atlas_lod_level_catalog import (
    AtlasLoDLevelCatalog,
)
from CORE.atlas_road_foundation_builder import (
    AtlasRoadFoundationBuilder,
)


def _coordinate_engine():
    return AtlasCoordinateEngine(
        origin_lat=50.0,
        origin_lon=8.0,
        xy_scale=5500.0,
        z_scale=5500.0,
    )


def test_road_foundation_can_use_cartographic_exaggeration(
    monkeypatch,
):
    captured = {}

    def fake_build_polyline_mesh(
        *,
        geometry,
        coordinate_engine,
        terrain_mesh,
        width_mm,
        road_type,
    ):
        captured["width_mm"] = width_mm

        return {
            "triangles": (),
            "road_type": road_type,
        }

    monkeypatch.setattr(
        AtlasRoadFoundationBuilder,
        "_build_polyline_mesh",
        staticmethod(fake_build_polyline_mesh),
    )

    roads = (
        {
            "id": 1,
            "geometry": (
                (50.0000, 8.0000),
                (50.0005, 8.0000),
            ),
            "road_type": "residential",
            "tags": {
                "highway": "residential",
                "width": "1.0",
            },
        },
    )

    meshes = AtlasRoadFoundationBuilder.build_roads(
        roads=roads,
        coordinate_engine=_coordinate_engine(),
        terrain_mesh=object(),
        minimum_printable_width_mm=0.40,
        cartographic_product_size_mm=150.0,
        cartographic_nozzle_diameter_mm=0.60,
        cartographic_lod_level=(
            AtlasLoDLevelCatalog.resolve(2)
        ),
        debug=False,
    )

    assert len(meshes) == 1

    strict_scale_width_mm = (
        1.0 * 1000.0 / 5500.0
    )

    assert strict_scale_width_mm < 0.60
    assert captured["width_mm"] == pytest.approx(
        0.60
    )


def test_road_foundation_preserves_strict_scale_when_readable(
    monkeypatch,
):
    captured = {}

    def fake_build_polyline_mesh(
        *,
        geometry,
        coordinate_engine,
        terrain_mesh,
        width_mm,
        road_type,
    ):
        captured["width_mm"] = width_mm

        return {
            "triangles": (),
            "road_type": road_type,
        }

    monkeypatch.setattr(
        AtlasRoadFoundationBuilder,
        "_build_polyline_mesh",
        staticmethod(fake_build_polyline_mesh),
    )

    roads = (
        {
            "id": 1,
            "geometry": (
                (50.0000, 8.0000),
                (50.0005, 8.0000),
            ),
            "road_type": "primary",
            "tags": {
                "highway": "primary",
                "width": "8.0",
            },
        },
    )

    AtlasRoadFoundationBuilder.build_roads(
        roads=roads,
        coordinate_engine=_coordinate_engine(),
        terrain_mesh=object(),
        minimum_printable_width_mm=0.40,
        cartographic_product_size_mm=150.0,
        cartographic_nozzle_diameter_mm=0.40,
        cartographic_lod_level=(
            AtlasLoDLevelCatalog.resolve(2)
        ),
        debug=False,
    )

    assert captured["width_mm"] == pytest.approx(
        8.0 * 1000.0 / 5500.0
    )


def test_road_foundation_keeps_legacy_behavior_without_8_13_context(
    monkeypatch,
):
    captured = {}

    def fake_build_polyline_mesh(
        *,
        geometry,
        coordinate_engine,
        terrain_mesh,
        width_mm,
        road_type,
    ):
        captured["width_mm"] = width_mm

        return {
            "triangles": (),
            "road_type": road_type,
        }

    monkeypatch.setattr(
        AtlasRoadFoundationBuilder,
        "_build_polyline_mesh",
        staticmethod(fake_build_polyline_mesh),
    )

    roads = (
        {
            "id": 1,
            "geometry": (
                (50.0000, 8.0000),
                (50.0005, 8.0000),
            ),
            "road_type": "residential",
            "tags": {
                "highway": "residential",
                "width": "1.0",
            },
        },
    )

    AtlasRoadFoundationBuilder.build_roads(
        roads=roads,
        coordinate_engine=_coordinate_engine(),
        terrain_mesh=object(),
        minimum_printable_width_mm=0.40,
        debug=False,
    )

    assert captured["width_mm"] == pytest.approx(
        0.40
    )
