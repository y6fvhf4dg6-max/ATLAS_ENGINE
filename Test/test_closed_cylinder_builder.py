import pytest

from CORE.atlas_closed_cylinder_builder import (
    AtlasClosedCylinderBuilder,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


def test_closed_cylinder_is_manifold():
    mesh = AtlasClosedCylinderBuilder.build(
        center_x=10.0,
        center_y=20.0,
        base_z=3.0,
        radius=1.0,
        height=5.0,
        segments=12,
    )

    report = (
        AtlasMeshValidator
        ._topology_report(mesh)
    )

    assert report["open_edge_count"] == 0
    assert (
        report["non_manifold_edge_count"]
        == 0
    )


def test_closed_cylinder_triangle_counts():
    segments = 12

    mesh = AtlasClosedCylinderBuilder.build(
        center_x=0.0,
        center_y=0.0,
        base_z=0.0,
        radius=1.0,
        height=2.0,
        segments=segments,
    )

    assert len(mesh["walls"]) == (
        segments * 2
    )
    assert len(mesh["bottom"]) == segments
    assert len(mesh["top"]) == segments
    assert len(mesh["triangles"]) == (
        segments * 4
    )
    assert mesh["triangle_count"] == (
        segments * 4
    )


def test_closed_cylinder_dimensions():
    mesh = AtlasClosedCylinderBuilder.build(
        center_x=4.0,
        center_y=7.0,
        base_z=2.5,
        radius=0.8,
        height=3.4,
        segments=8,
    )

    assert mesh["center"] == (
        4.0,
        7.0,
    )
    assert mesh["base_z"] == 2.5
    assert mesh["top_z"] == pytest.approx(
        5.9
    )
    assert mesh["radius"] == 0.8
    assert mesh["height"] == 3.4
    assert mesh["segments"] == 8


def test_closed_cylinder_preserves_metadata():
    mesh = AtlasClosedCylinderBuilder.build(
        center_x=0.0,
        center_y=0.0,
        base_z=0.0,
        radius=1.0,
        height=2.0,
        metadata={
            "component_type": (
                "classical_column"
            ),
            "source_system": (
                "classical_colonnade"
            ),
        },
    )

    assert (
        mesh["component_type"]
        == "classical_column"
    )
    assert (
        mesh["source_system"]
        == "classical_colonnade"
    )


@pytest.mark.parametrize(
    "radius",
    [
        0.0,
        -1.0,
    ],
)
def test_closed_cylinder_rejects_invalid_radius(
    radius,
):
    with pytest.raises(
        ValueError,
        match="radius",
    ):
        AtlasClosedCylinderBuilder.build(
            center_x=0.0,
            center_y=0.0,
            base_z=0.0,
            radius=radius,
            height=2.0,
        )


@pytest.mark.parametrize(
    "height",
    [
        0.0,
        -1.0,
    ],
)
def test_closed_cylinder_rejects_invalid_height(
    height,
):
    with pytest.raises(
        ValueError,
        match="height",
    ):
        AtlasClosedCylinderBuilder.build(
            center_x=0.0,
            center_y=0.0,
            base_z=0.0,
            radius=1.0,
            height=height,
        )


def test_closed_cylinder_rejects_too_few_segments():
    with pytest.raises(
        ValueError,
        match="segments",
    ):
        AtlasClosedCylinderBuilder.build(
            center_x=0.0,
            center_y=0.0,
            base_z=0.0,
            radius=1.0,
            height=2.0,
            segments=5,
        )
