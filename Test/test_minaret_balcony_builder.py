from CORE.atlas_mesh_validator import AtlasMeshValidator
from CORE.atlas_minaret_balcony_builder import (
    AtlasMinaretBalconyBuilder,
)


def _closed_box(
    min_x,
    min_y,
    max_x,
    max_y,
    bottom_z,
    top_z,
):
    bottom = [
        (min_x, min_y, bottom_z),
        (max_x, min_y, bottom_z),
        (max_x, max_y, bottom_z),
        (min_x, max_y, bottom_z),
    ]

    top = [
        (min_x, min_y, top_z),
        (max_x, min_y, top_z),
        (max_x, max_y, top_z),
        (min_x, max_y, top_z),
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

    walls = [
        (
            bottom[index],
            bottom[(index + 1) % 4],
            top[(index + 1) % 4],
            top[index],
        )
        for index in range(4)
    ]

    return {
        "type": "building",
        "bottom": bottom,
        "top": top,
        "walls": walls,
        "triangles": triangles,
        "bottom_z": bottom_z,
        "top_z": top_z,
    }


def test_closed_balcony_component_is_attached_to_minaret_mesh():
    minaret_mesh = _closed_box(
        -0.5,
        -0.5,
        0.5,
        0.5,
        0.0,
        12.0,
    )

    minaret_mesh["source_id"] = 100
    minaret_mesh["minaret_roof_applied"] = True

    balcony_mesh = _closed_box(
        -0.8,
        -0.8,
        0.8,
        0.8,
        8.0,
        8.4,
    )

    balcony_mesh["source_id"] = 200

    result = AtlasMinaretBalconyBuilder.attach(
        minaret_mesh=minaret_mesh,
        component_meshes=[
            balcony_mesh,
        ],
    )

    assert result["source_id"] == 100
    assert result["minaret_roof_applied"] is True

    assert result["minaret_balcony_applied"] is True
    assert result["minaret_balcony_count"] == 1
    assert result["minaret_balcony_source_ids"] == [
        200,
    ]

    assert len(result["triangles"]) == 24
    assert len(result["minaret_balcony_triangles"]) == 12

    report = AtlasMeshValidator.report(result)

    assert report["valid"] is True
    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_empty_component_list_leaves_minaret_unchanged():
    minaret_mesh = _closed_box(
        -0.5,
        -0.5,
        0.5,
        0.5,
        0.0,
        12.0,
    )

    original_triangles = list(
        minaret_mesh["triangles"]
    )

    result = AtlasMinaretBalconyBuilder.attach(
        minaret_mesh=minaret_mesh,
        component_meshes=[],
    )

    assert result["triangles"] == original_triangles
    assert result.get("minaret_balcony_applied") is None


def test_invalid_component_mesh_is_ignored():
    minaret_mesh = _closed_box(
        -0.5,
        -0.5,
        0.5,
        0.5,
        0.0,
        12.0,
    )

    result = AtlasMinaretBalconyBuilder.attach(
        minaret_mesh=minaret_mesh,
        component_meshes=[
            {
                "source_id": 200,
                "triangles": [],
            },
        ],
    )

    assert result.get("minaret_balcony_applied") is None
    assert len(result["triangles"]) == 12
