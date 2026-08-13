from types import SimpleNamespace

from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)


def test_foundation_first_builds_surface_railway_meshes(
    monkeypatch,
):
    railway = {
        "id": 94247467,
        "geometry": (
            (50.1530, 8.6530),
            (50.1550, 8.6530),
        ),
        "tags": {
            "railway": "rail",
        },
        "semantic_class": "railway",
        "operational_state": "active",
        "surface_visible": True,
    }

    profile = SimpleNamespace(
        semantic_class="railway",
        physical_width_mm=0.8,
        vertical_treatment="surface",
    )

    railway_mesh = {
        "type": "linear_infrastructure_solid",
        "triangles": [
            (
                (1.0, 1.0, 1.0),
                (2.0, 1.0, 1.0),
                (1.0, 2.0, 1.0),
            ),
        ],
    }

    captured = {}

    monkeypatch.setattr(
        "CORE.atlas_linear_infrastructure_resolver."
        "AtlasLinearInfrastructureResolver.resolve_profile",
        lambda **kwargs: profile,
    )

    def fake_build_product_solid(**kwargs):
        captured.update(kwargs)
        return railway_mesh

    monkeypatch.setattr(
        "CORE.atlas_linear_infrastructure_solid_builder."
        "AtlasLinearInfrastructureSolidBuilder.build_product_solid",
        fake_build_product_solid,
    )

    result = (
        AtlasFoundationFirstEngine
        ._build_linear_infrastructure_meshes(
            linear_infrastructure=(railway,),
            coordinate_engine=object(),
            terrain_mesh={},
            scale_ratio=3000.0,
            minimum_printable_width_mm=0.8,
            line_width_mm=0.4,
            minimum_gap_mm=0.4,
            cartographic_product_size_mm=200.0,
            cartographic_nozzle_diameter_mm=0.4,
            cartographic_lod_level=None,
        )
    )

    assert result == [railway_mesh]
    assert captured["item"] is railway
    assert captured["profile"] is profile


def test_foundation_first_clips_surface_railway_to_product_bounds(
    monkeypatch,
):
    railway = {
        "id": 94247467,
        "geometry": (
            (50.0, 8.0),
            (50.0, 8.1),
        ),
        "tags": {
            "railway": "rail",
        },
        "surface_visible": True,
    }

    profile = SimpleNamespace(
        semantic_class="railway",
        physical_width_mm=0.8,
        vertical_treatment="surface",
    )

    class CoordinateEngine:
        @staticmethod
        def geometry_to_stl_mm(geometry):
            return [
                (-20.0, 100.0),
                (220.0, 100.0),
            ]

    monkeypatch.setattr(
        "CORE.atlas_linear_infrastructure_resolver."
        "AtlasLinearInfrastructureResolver.resolve_profile",
        lambda **kwargs: profile,
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_sampler."
        "AtlasFoundationSampler.terrain_z_at_xy",
        lambda **kwargs: 0.0,
    )

    result = (
        AtlasFoundationFirstEngine
        ._build_linear_infrastructure_meshes(
            linear_infrastructure=(railway,),
            coordinate_engine=CoordinateEngine(),
            terrain_mesh={},
            scale_ratio=3000.0,
            minimum_printable_width_mm=0.8,
            line_width_mm=0.4,
            minimum_gap_mm=0.2,
            cartographic_product_size_mm=200.0,
            cartographic_nozzle_diameter_mm=0.4,
            cartographic_lod_level=None,
            clip_bounds=(
                0.0,
                200.0,
                0.0,
                200.0,
            ),
        )
    )

    assert len(result) == 1

    for triangle in result[0]["triangles"]:
        for x, y, _z in triangle:
            assert 0.0 <= x <= 200.0
            assert 0.0 <= y <= 200.0

