import pytest

from CORE.atlas_coordinate_engine import (
    AtlasCoordinateEngine,
)
from CORE.atlas_lod_level_catalog import (
    AtlasLoDLevelCatalog,
)
from CORE.atlas_water_foundation_builder import (
    AtlasWaterFoundationBuilder,
)


def _coordinate_engine():
    return AtlasCoordinateEngine(
        origin_lat=50.0,
        origin_lon=8.0,
        xy_scale=5500.0,
        z_scale=5500.0,
    )


def test_narrow_waterway_foundation_can_use_cartographic_exaggeration(
    monkeypatch,
):
    captured = {}

    def fake_build(
        *,
        geometry,
        coordinate_engine,
        terrain_mesh,
        width_mm,
        waterway_type,
        source_id,
        clip_bounds=None,
    ):
        captured["width_mm"] = width_mm
        captured["waterway_type"] = waterway_type
        captured["source_id"] = source_id

        return {
            "triangles": (),
            "type": "narrow_waterway_foundation",
        }

    monkeypatch.setattr(
        AtlasWaterFoundationBuilder,
        "_build_narrow_waterway_mesh",
        staticmethod(fake_build),
        raising=False,
    )

    meshes = (
        AtlasWaterFoundationBuilder
        .build_narrow_waterway_meshes(
            waters=(
                {
                    "id": 100,
                    "geometry": (
                        (50.0000, 8.0000),
                        (50.0005, 8.0000),
                        (50.0010, 8.0000),
                    ),
                    "tags": {
                        "waterway": "stream",
                        "width": "1.0",
                    },
                },
            ),
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
    )

    assert len(meshes) == 1

    assert captured["width_mm"] == pytest.approx(
        0.60
    )
    assert captured["waterway_type"] == "stream"
    assert captured["source_id"] == 100


def test_readable_narrow_waterway_preserves_strict_scale_width(
    monkeypatch,
):
    captured = {}

    def fake_build(**kwargs):
        captured.update(kwargs)

        return {
            "triangles": (),
            "type": "narrow_waterway_foundation",
        }

    monkeypatch.setattr(
        AtlasWaterFoundationBuilder,
        "_build_narrow_waterway_mesh",
        staticmethod(fake_build),
        raising=False,
    )

    AtlasWaterFoundationBuilder.build_narrow_waterway_meshes(
        waters=(
            {
                "id": 101,
                "geometry": (
                    (50.0000, 8.0000),
                    (50.0005, 8.0000),
                    (50.0010, 8.0000),
                ),
                "tags": {
                    "waterway": "canal",
                    "width": "8.0",
                },
            },
        ),
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


def test_narrow_waterway_builder_ignores_surface_water_polygons(
    monkeypatch,
):
    called = []

    monkeypatch.setattr(
        AtlasWaterFoundationBuilder,
        "_build_narrow_waterway_mesh",
        staticmethod(
            lambda **kwargs: called.append(kwargs)
        ),
        raising=False,
    )

    meshes = (
        AtlasWaterFoundationBuilder
        .build_narrow_waterway_meshes(
            waters=(
                {
                    "id": 102,
                    "geometry": (
                        (50.0000, 8.0000),
                        (50.0000, 8.0010),
                        (50.0010, 8.0010),
                        (50.0010, 8.0000),
                    ),
                    "tags": {
                        "natural": "water",
                        "water": "lake",
                    },
                },
            ),
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
    )

    assert meshes == []
    assert called == []


def test_narrow_waterway_mesh_is_terrain_following_closed_solid(
    monkeypatch,
):
    from CORE.atlas_mesh_validator import (
        AtlasMeshValidator,
    )

    terrain_mesh = {
        "top_points": [
            [
                (0.0, 0.0, 1.0),
                (20.0, 0.0, 1.5),
            ],
            [
                (0.0, 20.0, 2.0),
                (20.0, 20.0, 2.5),
            ],
        ],
    }

    coordinate_engine = _coordinate_engine()

    mesh = (
        AtlasWaterFoundationBuilder
        ._build_narrow_waterway_mesh(
            geometry=(
                (50.00010, 8.00010),
                (50.00020, 8.00010),
                (50.00030, 8.00010),
            ),
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_mesh,
            width_mm=0.80,
            waterway_type="stream",
            source_id=700,
        )
    )

    assert mesh is not None
    assert (
        mesh["type"]
        == "narrow_waterway_foundation"
    )
    assert mesh["waterway_type"] == "stream"
    assert mesh["source_id"] == 700
    assert mesh["physical_width_mm"] == pytest.approx(
        0.80
    )
    assert (
        mesh["placement_mode"]
        == "terrain_following"
    )

    bottom_z_values = {
        round(point[2], 9)
        for point in mesh["bottom"]
    }

    assert len(bottom_z_values) > 1

    report = AtlasMeshValidator._topology_report(
        mesh
    )

    assert report["open_edge_count"] == 0
    assert (
        report["non_manifold_edge_count"]
        == 0
    )


def test_narrow_waterway_mesh_reuses_general_band_and_solid_builders(
    monkeypatch,
):
    captured = {}

    monkeypatch.setattr(
        "CORE.atlas_water_foundation_builder."
        "AtlasTerrainContourBandBuilder.build_band",
        lambda **kwargs: [
            (0.0, 0.0),
            (0.0, 1.0),
            (5.0, 1.0),
            (5.0, 0.0),
        ],
    )

    def fake_solid(**kwargs):
        captured.update(kwargs)

        return {
            "triangles": (),
            "bottom": (),
            "top": (),
            "walls": (),
        }

    monkeypatch.setattr(
        "CORE.atlas_water_foundation_builder."
        "AtlasLinearInfrastructureSolidBuilder."
        "build_polygon_solid",
        fake_solid,
    )

    mesh = (
        AtlasWaterFoundationBuilder
        ._build_narrow_waterway_mesh(
            geometry=(
                (50.00010, 8.00010),
                (50.00020, 8.00010),
            ),
            coordinate_engine=_coordinate_engine(),
            terrain_mesh=object(),
            width_mm=0.80,
            waterway_type="canal",
            source_id=701,
        )
    )

    assert captured["height_mm"] == pytest.approx(
        AtlasWaterFoundationBuilder.WATER_HEIGHT_MM
    )

    assert mesh["type"] == (
        "narrow_waterway_foundation"
    )
    assert mesh["source_id"] == 701
    assert mesh["waterway_type"] == "canal"
    assert mesh["physical_width_mm"] == pytest.approx(
        0.80
    )

