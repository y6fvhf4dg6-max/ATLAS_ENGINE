from types import SimpleNamespace

import pytest

from CORE.atlas_lod_level_catalog import (
    AtlasLoDLevelCatalog,
)
from CORE.atlas_water_foundation_builder import (
    AtlasWaterFoundationBuilder,
)


def test_widthless_river_uses_minimum_printable_width(
    monkeypatch,
):
    captured = {}

    def fake_build(**kwargs):
        captured.update(kwargs)
        return {
            "type": "narrow_waterway_foundation",
            "triangles": (),
        }

    monkeypatch.setattr(
        AtlasWaterFoundationBuilder,
        "_build_narrow_waterway_mesh",
        staticmethod(fake_build),
    )

    meshes = (
        AtlasWaterFoundationBuilder
        .build_narrow_waterway_meshes(
            waters=(
                {
                    "id": 251248199,
                    "geometry": (
                        (50.1540, 8.6460),
                        (50.1550, 8.6462),
                    ),
                    "tags": {
                        "name": "Nidda",
                        "waterway": "river",
                    },
                },
            ),
            coordinate_engine=SimpleNamespace(
                xy_scale=3000.0,
            ),
            terrain_mesh=object(),
            minimum_printable_width_mm=0.80,
            cartographic_product_size_mm=200.0,
            cartographic_nozzle_diameter_mm=0.40,
            cartographic_lod_level=(
                AtlasLoDLevelCatalog.resolve(2)
            ),
            debug=False,
        )
    )

    assert len(meshes) == 1
    assert captured["width_mm"] == pytest.approx(0.80)
    assert captured["waterway_type"] == "river"
    assert captured["source_id"] == 251248199
