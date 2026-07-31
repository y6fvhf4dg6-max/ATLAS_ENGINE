import pytest

from CORE.atlas_label_birthday_cake_mesher import (
    AtlasLabelBirthdayCakeMesher,
)


def test_birthday_cake_mesher_builds_closed_centered_printable_symbol():
    mesh = AtlasLabelBirthdayCakeMesher.build(
        width_mm=8.0,
        height_mm=7.0,
        depth_mm=0.6,
    )

    assert mesh["type"] == "label_birthday_cake"
    assert mesh["width_mm"] == pytest.approx(8.0)
    assert mesh["height_mm"] == pytest.approx(7.0)
    assert mesh["depth_mm"] == pytest.approx(0.6)
    assert mesh["triangles"]

    xs = [
        coordinate
        for triangle in mesh["triangles"]
        for vertex in triangle
        for coordinate in (vertex[0],)
    ]
    ys = [
        coordinate
        for triangle in mesh["triangles"]
        for vertex in triangle
        for coordinate in (vertex[1],)
    ]
    zs = [
        coordinate
        for triangle in mesh["triangles"]
        for vertex in triangle
        for coordinate in (vertex[2],)
    ]

    assert min(xs) == pytest.approx(-4.0)
    assert max(xs) == pytest.approx(4.0)
    assert min(ys) == pytest.approx(-3.5)
    assert max(ys) == pytest.approx(3.5)
    assert min(zs) == pytest.approx(0.0)
    assert max(zs) == pytest.approx(0.6)


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("width_mm", 0.0),
        ("width_mm", -1.0),
        ("height_mm", 0.0),
        ("height_mm", -1.0),
        ("depth_mm", 0.0),
        ("depth_mm", -1.0),
    ),
)
def test_birthday_cake_mesher_rejects_non_positive_dimensions(
    field_name,
    value,
):
    values = {
        "width_mm": 8.0,
        "height_mm": 7.0,
        "depth_mm": 0.6,
    }
    values[field_name] = value

    with pytest.raises(
        ValueError,
        match=f"{field_name} must be positive",
    ):
        AtlasLabelBirthdayCakeMesher.build(**values)
