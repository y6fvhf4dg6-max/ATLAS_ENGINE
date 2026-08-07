import pytest

from CORE.atlas_linear_infrastructure_solid_builder import (
    AtlasLinearInfrastructureSolidBuilder,
)


class _TerrainMesh:
    pass


class _Sampler:
    @staticmethod
    def terrain_z_at_xy(*, terrain_mesh, x, y):
        return x + y


def test_build_terrain_following_polygon_solid(monkeypatch):
    monkeypatch.setattr(
        "CORE.atlas_linear_infrastructure_solid_builder."
        "AtlasFoundationSampler",
        _Sampler,
    )

    mesh = (
        AtlasLinearInfrastructureSolidBuilder
        .build_polygon_solid(
            points=[
                (0.0, 0.0),
                (10.0, 0.0),
                (10.0, 5.0),
                (0.0, 5.0),
                (0.0, 0.0),
            ],
            terrain_mesh=_TerrainMesh(),
            height_mm=0.4,
        )
    )

    assert mesh is not None
    assert mesh["type"] == "linear_infrastructure_solid"
    assert len(mesh["bottom"]) == 4
    assert len(mesh["top"]) == 4
    assert len(mesh["walls"]) == 4

    assert mesh["bottom"][0] == pytest.approx(
        (0.0, 0.0, 0.0)
    )
    assert mesh["top"][0] == pytest.approx(
        (0.0, 0.0, 0.4)
    )

    assert mesh["bottom"][2] == pytest.approx(
        (10.0, 5.0, 15.0)
    )
    assert mesh["top"][2] == pytest.approx(
        (10.0, 5.0, 15.4)
    )

    assert len(mesh["triangles"]) == 12


def test_build_polygon_solid_rejects_nonpositive_height(monkeypatch):
    monkeypatch.setattr(
        "CORE.atlas_linear_infrastructure_solid_builder."
        "AtlasFoundationSampler",
        _Sampler,
    )

    with pytest.raises(ValueError):
        AtlasLinearInfrastructureSolidBuilder.build_polygon_solid(
            points=[
                (0.0, 0.0),
                (1.0, 0.0),
                (1.0, 1.0),
                (0.0, 0.0),
            ],
            terrain_mesh=_TerrainMesh(),
            height_mm=0.0,
        )


def test_build_polygon_solid_rejects_insufficient_geometry(monkeypatch):
    monkeypatch.setattr(
        "CORE.atlas_linear_infrastructure_solid_builder."
        "AtlasFoundationSampler",
        _Sampler,
    )

    assert (
        AtlasLinearInfrastructureSolidBuilder
        .build_polygon_solid(
            points=[
                (0.0, 0.0),
                (1.0, 0.0),
            ],
            terrain_mesh=_TerrainMesh(),
            height_mm=0.4,
        )
        is None
    )


class _CoordinateEngine:
    def geometry_to_stl_mm(self, geometry):
        return [
            (lon * 10.0, lat * 10.0)
            for lat, lon in geometry
        ]


class _Profile:
    physical_width_mm = 2.0


def test_build_product_solid_builds_linear_corridor(monkeypatch):
    monkeypatch.setattr(
        "CORE.atlas_linear_infrastructure_solid_builder."
        "AtlasFoundationSampler",
        _Sampler,
    )

    mesh = AtlasLinearInfrastructureSolidBuilder.build_product_solid(
        item={
            "geometry": [
                (1.0, 2.0),
                (1.0, 3.0),
            ],
            "tags": {
                "railway": "tram",
            },
        },
        coordinate_engine=_CoordinateEngine(),
        profile=_Profile(),
        terrain_mesh=_TerrainMesh(),
        height_mm=0.4,
    )

    assert mesh is not None
    assert mesh["type"] == "linear_infrastructure_solid"
    assert len(mesh["walls"]) == 4


def test_build_product_solid_builds_area_corridor(monkeypatch):
    monkeypatch.setattr(
        "CORE.atlas_linear_infrastructure_solid_builder."
        "AtlasFoundationSampler",
        _Sampler,
    )

    mesh = AtlasLinearInfrastructureSolidBuilder.build_product_solid(
        item={
            "geometry": [
                (1.0, 2.0),
                (1.0, 3.0),
                (2.0, 3.0),
                (2.0, 2.0),
                (1.0, 2.0),
            ],
            "tags": {
                "landuse": "railway",
            },
        },
        coordinate_engine=_CoordinateEngine(),
        profile=_Profile(),
        terrain_mesh=_TerrainMesh(),
        height_mm=0.4,
    )

    assert mesh is not None
    assert mesh["type"] == "linear_infrastructure_solid"
    assert len(mesh["walls"]) == 4
