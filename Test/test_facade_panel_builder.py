import pytest

from CORE.atlas_facade_panel_builder import (
    AtlasFacadePanelBuilder,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


WALL_QUAD = (
    (0.0, 0.0, 0.0),
    (10.0, 0.0, 0.0),
    (10.0, 0.0, 6.0),
    (0.0, 0.0, 6.0),
)


def test_repeated_facade_panels_are_created():
    mesh = (
        AtlasFacadePanelBuilder
        .build_repeated_rectangles(
            wall_quad=WALL_QUAD,
            column_count=5,
            row_count=2,
        )
    )

    assert mesh["panel_count"] == 10
    assert len(
        mesh["component_meshes"]
    ) == 10
    assert len(mesh["triangles"]) == 120


def test_each_facade_panel_is_closed():
    mesh = (
        AtlasFacadePanelBuilder
        .build_repeated_rectangles(
            wall_quad=WALL_QUAD,
            column_count=4,
            row_count=3,
        )
    )

    for component in mesh[
        "component_meshes"
    ]:
        report = (
            AtlasMeshValidator
            ._topology_report(component)
        )

        assert report["open_edge_count"] == 0
        assert (
            report[
                "non_manifold_edge_count"
            ]
            == 0
        )


def test_facade_panels_preserve_grid_indices():
    mesh = (
        AtlasFacadePanelBuilder
        .build_repeated_rectangles(
            wall_quad=WALL_QUAD,
            column_count=3,
            row_count=2,
        )
    )

    indices = {
        (
            component["row_index"],
            component["column_index"],
        )
        for component in mesh[
            "component_meshes"
        ]
    }

    assert indices == {
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 1),
        (1, 2),
    }


def test_facade_panels_preserve_metadata():
    mesh = (
        AtlasFacadePanelBuilder
        .build_repeated_rectangles(
            wall_quad=WALL_QUAD,
            column_count=2,
            row_count=1,
            metadata={
                "architectural_role": (
                    "stage_facade_window"
                ),
            },
        )
    )

    assert all(
        component[
            "architectural_role"
        ]
        == "stage_facade_window"
        for component in mesh[
            "component_meshes"
        ]
    )


def test_facade_panel_depth_and_embed():
    mesh = (
        AtlasFacadePanelBuilder
        .build_repeated_rectangles(
            wall_quad=WALL_QUAD,
            column_count=2,
            row_count=1,
            depth_mm=0.30,
            embed_mm=0.08,
        )
    )

    assert mesh["depth_mm"] == 0.30
    assert mesh["embed_mm"] == 0.08

    assert all(
        component["depth_mm"] == 0.30
        and component["embed_mm"] == 0.08
        for component in mesh[
            "component_meshes"
        ]
    )


@pytest.mark.parametrize(
    "column_count,row_count",
    [
        (0, 1),
        (1, 0),
        (-1, 2),
        (2, -1),
    ],
)
def test_facade_panels_reject_invalid_grid(
    column_count,
    row_count,
):
    with pytest.raises(ValueError):
        (
            AtlasFacadePanelBuilder
            .build_repeated_rectangles(
                wall_quad=WALL_QUAD,
                column_count=column_count,
                row_count=row_count,
            )
        )


def test_facade_panels_reject_degenerate_wall():
    with pytest.raises(
        ValueError,
        match="degenerate",
    ):
        (
            AtlasFacadePanelBuilder
            .build_repeated_rectangles(
                wall_quad=(
                    (0.0, 0.0, 0.0),
                    (0.0, 0.0, 0.0),
                    (0.0, 0.0, 1.0),
                    (0.0, 0.0, 1.0),
                ),
                column_count=2,
                row_count=1,
            )
        )


def test_repeated_arched_panels_are_created():
    mesh = (
        AtlasFacadePanelBuilder
        .build_repeated_arches(
            wall_quad=WALL_QUAD,
            column_count=5,
            row_count=2,
            arch_segments=6,
        )
    )

    assert mesh["panel_count"] == 10
    assert len(
        mesh["component_meshes"]
    ) == 10
    assert mesh["arch_segments"] == 6


def test_each_arched_panel_is_closed():
    mesh = (
        AtlasFacadePanelBuilder
        .build_repeated_arches(
            wall_quad=WALL_QUAD,
            column_count=4,
            row_count=3,
            arch_segments=6,
        )
    )

    for component in mesh[
        "component_meshes"
    ]:
        report = (
            AtlasMeshValidator
            ._topology_report(component)
        )

        assert report["open_edge_count"] == 0
        assert (
            report[
                "non_manifold_edge_count"
            ]
            == 0
        )


def test_arched_panels_preserve_metadata():
    mesh = (
        AtlasFacadePanelBuilder
        .build_repeated_arches(
            wall_quad=WALL_QUAD,
            column_count=3,
            row_count=2,
            metadata={
                "architectural_role": (
                    "stage_facade_arch"
                ),
            },
        )
    )

    assert all(
        component[
            "architectural_role"
        ]
        == "stage_facade_arch"
        for component in mesh[
            "component_meshes"
        ]
    )


def test_arched_panels_reject_too_few_segments():
    with pytest.raises(
        ValueError,
        match="arch_segments",
    ):
        (
            AtlasFacadePanelBuilder
            .build_repeated_arches(
                wall_quad=WALL_QUAD,
                column_count=3,
                row_count=2,
                arch_segments=2,
            )
        )

def test_arch_height_ratio_is_measured_in_physical_wall_space():
    result = AtlasFacadePanelBuilder.build_repeated_arches(
        wall_quad=(
            (0.0, 0.0, 0.0),
            (20.0, 0.0, 0.0),
            (20.0, 0.0, 40.0),
            (0.0, 0.0, 40.0),
        ),
        column_count=1,
        row_count=1,
        panel_width_ratio=0.40,
        panel_height_ratio=0.60,
        arch_height_ratio=0.35,
        horizontal_margin_ratio=0.10,
        vertical_margin_ratio=0.10,
        arch_segments=8,
    )

    panel = result["component_meshes"][0]
    back = panel["back"]

    physical_width = (
        (
            (back[1][0] - back[0][0]) ** 2
            + (back[1][1] - back[0][1]) ** 2
            + (back[1][2] - back[0][2]) ** 2
        )
        ** 0.5
    )
    spring_height = back[2][2]
    physical_rise = (
        max(point[2] for point in back)
        - spring_height
    )

    assert abs(
        physical_rise
        - physical_width * 0.5 * 0.35
    ) < 1e-9


def test_unit_arch_height_ratio_builds_physical_semicircle():
    result = AtlasFacadePanelBuilder.build_repeated_arches(
        wall_quad=(
            (0.0, 0.0, 0.0),
            (30.0, 0.0, 0.0),
            (30.0, 0.0, 18.0),
            (0.0, 0.0, 18.0),
        ),
        column_count=1,
        row_count=1,
        panel_width_ratio=0.30,
        panel_height_ratio=0.70,
        arch_height_ratio=1.00,
        horizontal_margin_ratio=0.10,
        vertical_margin_ratio=0.10,
        arch_segments=12,
    )

    panel = result["component_meshes"][0]
    back = panel["back"]

    physical_width = (
        (
            (back[1][0] - back[0][0]) ** 2
            + (back[1][1] - back[0][1]) ** 2
            + (back[1][2] - back[0][2]) ** 2
        )
        ** 0.5
    )
    spring_height = back[2][2]
    physical_rise = (
        max(point[2] for point in back)
        - spring_height
    )

    assert abs(
        physical_rise
        - physical_width * 0.5
    ) < 1e-9

