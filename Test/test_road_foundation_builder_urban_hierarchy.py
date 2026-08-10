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


def test_road_builder_clips_crossing_polyline_before_extrusion(
    monkeypatch,
):
    from CORE.atlas_foundation_sampler import (
        AtlasFoundationSampler,
    )
    from CORE.atlas_mesh_validator import (
        AtlasMeshValidator,
    )

    class CoordinateEngine:
        xy_scale = 1000.0

        @staticmethod
        def geometry_to_stl_mm(geometry):
            return [
                (
                    float(point[0]),
                    float(point[1]),
                )
                for point in geometry
            ]

        @staticmethod
        def height_to_stl_mm(value):
            return float(value)

    monkeypatch.setattr(
        AtlasFoundationSampler,
        "terrain_z_at_xy",
        staticmethod(
            lambda **kwargs: 0.0
        ),
    )

    meshes = AtlasRoadFoundationBuilder.build_roads(
        roads=[
            {
                "id": 987654,
                "road_type": "residential",
                "geometry": (
                    (-20.0, 50.0),
                    (120.0, 50.0),
                ),
                "tags": {
                    "highway": "residential",
                },
            },
        ],
        coordinate_engine=CoordinateEngine(),
        terrain_mesh=object(),
        clip_bounds=(
            0.0,
            100.0,
            0.0,
            100.0,
        ),
        debug=False,
    )

    assert len(meshes) == 1

    mesh = meshes[0]

    assert mesh["source_id"] == 987654

    vertices = [
        point
        for triangle in mesh["triangles"]
        for point in triangle
    ]

    xs = [
        float(point[0])
        for point in vertices
    ]
    ys = [
        float(point[1])
        for point in vertices
    ]

    assert min(xs) >= 0.0
    assert max(xs) <= 100.0
    assert min(ys) >= 0.0
    assert max(ys) <= 100.0

    report = AtlasMeshValidator.report(mesh)

    assert report["valid"] is True
    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0

