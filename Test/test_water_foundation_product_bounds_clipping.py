from CORE.atlas_water_foundation_builder import (
    AtlasWaterFoundationBuilder,
)


class _CoordinateEngine:
    @staticmethod
    def geometry_to_stl_mm(geometry):
        return [
            (-20.0, 100.0),
            (220.0, 100.0),
        ]


def test_narrow_waterway_is_clipped_before_closed_solid_build(
    monkeypatch,
):
    monkeypatch.setattr(
        "CORE.atlas_foundation_sampler."
        "AtlasFoundationSampler.terrain_z_at_xy",
        lambda **kwargs: 0.0,
    )

    mesh = (
        AtlasWaterFoundationBuilder
        ._build_narrow_waterway_mesh(
            geometry=(
                (50.0, 8.0),
                (50.0, 8.1),
            ),
            coordinate_engine=_CoordinateEngine(),
            terrain_mesh={},
            width_mm=0.80,
            waterway_type="river",
            source_id=251248199,
            clip_bounds=(
                0.0,
                200.0,
                0.0,
                200.0,
            ),
        )
    )

    assert mesh is not None

    vertices = [
        point
        for triangle in mesh["triangles"]
        for point in triangle
    ]

    assert all(
        -1e-9 <= x <= 200.0 + 1e-9
        and -1e-9 <= y <= 200.0 + 1e-9
        for x, y, _z in vertices
    )


def test_build_narrow_waterway_meshes_forwards_product_clip_bounds(
    monkeypatch,
):
    captured = {}

    def _fake_build(**kwargs):
        captured.update(kwargs)
        return {
            "type": "narrow_waterway_foundation",
            "triangles": (),
        }

    monkeypatch.setattr(
        AtlasWaterFoundationBuilder,
        "_build_narrow_waterway_mesh",
        staticmethod(_fake_build),
    )

    waters = [
        {
            "id": 251248199,
            "tags": {
                "waterway": "river",
            },
            "geometry": (
                (50.0, 8.0),
                (50.0, 8.1),
            ),
        },
    ]

    AtlasWaterFoundationBuilder.build_narrow_waterway_meshes(
        waters=waters,
        coordinate_engine=_CoordinateEngine(),
        terrain_mesh={},
        minimum_printable_width_mm=0.80,
        cartographic_product_size_mm=200.0,
        cartographic_nozzle_diameter_mm=0.40,
        cartographic_lod_level=2,
        debug=False,
        clip_bounds=(0.0, 200.0, 0.0, 200.0),
    )

    assert captured["clip_bounds"] == (
        0.0,
        200.0,
        0.0,
        200.0,
    )


def test_narrow_waterway_defaults_clip_bounds_from_product_size(
    monkeypatch,
):
    captured = {}

    def _fake_build(**kwargs):
        captured.update(kwargs)
        return {
            "type": "narrow_waterway_foundation",
            "triangles": (),
        }

    monkeypatch.setattr(
        AtlasWaterFoundationBuilder,
        "_build_narrow_waterway_mesh",
        staticmethod(_fake_build),
    )

    waters = [
        {
            "id": 251248199,
            "tags": {
                "waterway": "river",
            },
            "geometry": (
                (50.0, 8.0),
                (50.0, 8.1),
            ),
        },
    ]

    AtlasWaterFoundationBuilder.build_narrow_waterway_meshes(
        waters=waters,
        coordinate_engine=_CoordinateEngine(),
        terrain_mesh={},
        minimum_printable_width_mm=0.80,
        cartographic_product_size_mm=200.0,
        cartographic_nozzle_diameter_mm=0.40,
        cartographic_lod_level=2,
        debug=False,
    )

    assert captured["clip_bounds"] == (
        0.0,
        200.0,
        0.0,
        200.0,
    )
