import pytest

from CORE.atlas_mesh_validator import AtlasMeshValidator
from CORE.atlas_minaret_roof_builder import (
    AtlasMinaretRoofBuilder,
)


class DummyCoordinateEngine:
    @staticmethod
    def height_to_stl_mm(height_m):
        return float(height_m)


def _make_prism_mesh():
    bottom = [
        (-0.5, -0.5, 0.0),
        (0.5, -0.5, 0.0),
        (0.5, 0.5, 0.0),
        (-0.5, 0.5, 0.0),
    ]

    top = [
        (-0.5, -0.5, 12.0),
        (0.5, -0.5, 12.0),
        (0.5, 0.5, 12.0),
        (-0.5, 0.5, 12.0),
    ]

    triangles = [
        # Bottom
        (bottom[0], bottom[2], bottom[1]),
        (bottom[0], bottom[3], bottom[2]),

        # Top
        (top[0], top[1], top[2]),
        (top[0], top[2], top[3]),

        # Walls
        (bottom[0], bottom[1], top[1]),
        (bottom[0], top[1], top[0]),

        (bottom[1], bottom[2], top[2]),
        (bottom[1], top[2], top[1]),

        (bottom[2], bottom[3], top[3]),
        (bottom[2], top[3], top[2]),

        (bottom[3], bottom[0], top[0]),
        (bottom[3], top[0], top[3]),
    ]

    return {
        "type": "building",
        "bottom": bottom,
        "top": top,
        "walls": [
            (
                bottom[index],
                bottom[(index + 1) % 4],
                top[(index + 1) % 4],
                top[index],
            )
            for index in range(4)
        ],
        "triangles": triangles,
        "foundation_z": 0.0,
        "base_offset_mm": 0.0,
        "bottom_z": 0.0,
        "top_z": 12.0,
    }


def test_pyramidal_minaret_roof_replaces_flat_top():
    mesh = _make_prism_mesh()

    result = AtlasMinaretRoofBuilder.apply(
        mesh=mesh,
        tower_type="minaret",
        roof_shape="pyramidal",
        roof_height_m="2",
        coordinate_engine=DummyCoordinateEngine(),
    )

    assert result["minaret_roof_applied"] is True
    assert result["roof_geometry"] == "minaret_pyramidal"

    assert result["body_top_z"] == pytest.approx(10.0)
    assert result["roof_base_z"] == pytest.approx(10.0)
    assert result["roof_top_z"] == pytest.approx(12.0)
    assert result["top_z"] == pytest.approx(12.0)

    assert result["roof_apex"] == pytest.approx(
        (0.0, 0.0, 12.0)
    )

    assert len(result["roof_triangles"]) == 4
    assert result["removed_top_triangle_count"] == 2

    report = AtlasMeshValidator.report(result)

    assert report["valid"] is True
    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_non_minaret_mesh_is_unchanged():
    mesh = _make_prism_mesh()

    original_triangles = list(mesh["triangles"])

    result = AtlasMinaretRoofBuilder.apply(
        mesh=mesh,
        tower_type=None,
        roof_shape="pyramidal",
        roof_height_m="2",
        coordinate_engine=DummyCoordinateEngine(),
    )

    assert result["triangles"] == original_triangles
    assert result.get("minaret_roof_applied") is None


def test_unsupported_minaret_roof_shape_is_unchanged():
    mesh = _make_prism_mesh()

    original_triangles = list(mesh["triangles"])

    result = AtlasMinaretRoofBuilder.apply(
        mesh=mesh,
        tower_type="minaret",
        roof_shape="flat",
        roof_height_m="2",
        coordinate_engine=DummyCoordinateEngine(),
    )

    assert result["triangles"] == original_triangles
    assert result.get("minaret_roof_applied") is None
