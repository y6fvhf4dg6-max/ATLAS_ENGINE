import pytest

from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


def _valid_mesh():
    bottom = [
        (0.0, 0.0, 0.0),
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
    ]

    top = [
        (0.0, 0.0, 1.0),
        (1.0, 0.0, 1.0),
        (0.0, 1.0, 1.0),
    ]

    triangles = [
        (bottom[0], bottom[2], bottom[1]),
        (top[0], top[1], top[2]),
        (bottom[0], bottom[1], top[1]),
        (bottom[0], top[1], top[0]),
        (bottom[1], bottom[2], top[2]),
        (bottom[1], top[2], top[1]),
        (bottom[2], bottom[0], top[0]),
        (bottom[2], top[0], top[2]),
    ]

    return {
        "type": "test_prism",
        "bottom": bottom,
        "top": top,
        "walls": [0, 1, 2],
        "triangles": triangles,
    }


@pytest.mark.parametrize(
    "triangle,expected_reason",
    [
        (None, "bad_triangle_size"),
        ((), "bad_triangle_size"),
        (
            (
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
            ),
            "bad_triangle_size",
        ),
        (
            (
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (0.0, 1.0, 0.0),
                (1.0, 1.0, 0.0),
            ),
            "bad_triangle_size",
        ),
    ],
)
def test_report_rejects_bad_triangle_size(
    triangle,
    expected_reason,
):
    mesh = _valid_mesh()
    mesh["triangles"][0] = triangle

    report = AtlasMeshValidator.report(mesh)

    assert report["valid"] is False
    assert report["structure_valid"] is False
    assert report["reason"] == expected_reason


@pytest.mark.parametrize(
    "point",
    [
        None,
        (),
        (0.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    ],
)
def test_report_rejects_bad_triangle_point_size(
    point,
):
    mesh = _valid_mesh()

    mesh["triangles"][0] = (
        point,
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
    )

    report = AtlasMeshValidator.report(mesh)

    assert report["valid"] is False
    assert report["structure_valid"] is False
    assert report["reason"] == "bad_point_size"


@pytest.mark.parametrize(
    "point",
    [
        (None, 0.0, 0.0),
        (0.0, None, 0.0),
        (0.0, 0.0, None),
    ],
)
def test_report_rejects_none_triangle_coordinates(
    point,
):
    mesh = _valid_mesh()

    mesh["triangles"][0] = (
        point,
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
    )

    report = AtlasMeshValidator.report(mesh)

    assert report["valid"] is False
    assert report["structure_valid"] is False
    assert report["reason"] == "point_has_none"


def test_valid_triangle_structure_reaches_topology_report():
    report = AtlasMeshValidator.report(
        _valid_mesh()
    )

    assert report["structure_valid"] is True
    assert "open_edge_count" in report
    assert "non_manifold_edge_count" in report
