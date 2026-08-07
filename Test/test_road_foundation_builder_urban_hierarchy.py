import pytest

from CORE.atlas_road_foundation_builder import (
    AtlasRoadFoundationBuilder,
)


class _CoordinateEngine:
    xy_scale = 4000.0

    def height_to_stl_mm(self, value):
        return float(value) * 1000.0 / self.xy_scale


def test_road_builder_uses_semantic_width_resolution(
    monkeypatch,
):
    captured = []

    def fake_build_polyline_mesh(
        *,
        geometry,
        coordinate_engine,
        terrain_mesh,
        width_mm,
        road_type,
    ):
        captured.append(
            (road_type, width_mm)
        )
        return {
            "triangles": [(0, 1, 2)],
            "road_type": road_type,
        }

    monkeypatch.setattr(
        AtlasRoadFoundationBuilder,
        "_build_polyline_mesh",
        staticmethod(fake_build_polyline_mesh),
    )

    roads = [
        {
            "road_type": "primary",
            "geometry": [(0.0, 0.0), (1.0, 1.0)],
            "tags": {
                "highway": "primary",
                "width": "8 m",
            },
        },
        {
            "road_type": "footway",
            "geometry": [(0.0, 0.0), (1.0, 1.0)],
            "tags": {
                "highway": "footway",
            },
        },
    ]

    meshes = AtlasRoadFoundationBuilder.build_roads(
        roads=roads,
        coordinate_engine=_CoordinateEngine(),
        terrain_mesh=None,
        minimum_printable_width_mm=0.8,
        debug=False,
    )

    assert len(meshes) == 2
    assert captured == [
        ("primary", pytest.approx(2.0)),
        ("footway", pytest.approx(0.8)),
    ]


def test_road_builder_preserves_legacy_behavior_without_semantic_minimum(
    monkeypatch,
):
    captured = []

    def fake_build_polyline_mesh(
        *,
        geometry,
        coordinate_engine,
        terrain_mesh,
        width_mm,
        road_type,
    ):
        captured.append(
            (road_type, width_mm)
        )
        return {
            "triangles": [(0, 1, 2)],
            "road_type": road_type,
        }

    monkeypatch.setattr(
        AtlasRoadFoundationBuilder,
        "_build_polyline_mesh",
        staticmethod(fake_build_polyline_mesh),
    )

    roads = [
        {
            "road_type": "residential",
            "geometry": [(0.0, 0.0), (1.0, 1.0)],
            "tags": {
                "highway": "residential",
            },
        },
        {
            "road_type": "footway",
            "geometry": [(0.0, 0.0), (1.0, 1.0)],
            "tags": {
                "highway": "footway",
            },
        },
    ]

    meshes = AtlasRoadFoundationBuilder.build_roads(
        roads=roads,
        coordinate_engine=_CoordinateEngine(),
        terrain_mesh=None,
        debug=False,
    )

    assert len(meshes) == 1
    assert captured == [
        ("residential", pytest.approx(1.25)),
    ]
