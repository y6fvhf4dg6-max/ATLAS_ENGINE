from CORE.atlas_facade_bay_analyzer import (
    AtlasFacadeBayAnalyzer,
)
from CORE.atlas_facade_panel_layout_mesher import (
    AtlasFacadePanelLayoutMesher,
)
from CORE.atlas_facade_region_analyzer import (
    AtlasFacadeRegionAnalyzer,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


WALL_QUAD = (
    (0.0, 0.0, 0.0),
    (12.0, 0.0, 0.0),
    (12.0, 0.0, 7.0),
    (0.0, 0.0, 7.0),
)


def _two_by_three_bay_analysis():
    region_analysis = AtlasFacadeRegionAnalyzer.analyze(
        tags={
            "building:levels": "2",
        },
        total_height_m=7.0,
    )

    return AtlasFacadeBayAnalyzer.analyze(
        region_analysis=region_analysis,
        bay_count=3,
    )


def test_panels_are_created_for_real_bay_and_floor_cells():
    result = AtlasFacadePanelLayoutMesher.build(
        wall_quad=WALL_QUAD,
        bay_analysis=_two_by_three_bay_analysis(),
        horizontal_margin_ratio=0.20,
        vertical_margin_ratio=0.25,
    )

    assert result["panel_count"] == 6
    assert len(result["component_meshes"]) == 6

    bounds = tuple(
        (
            round(
                min(point[0] for point in component["back"]),
                6,
            ),
            round(
                max(point[0] for point in component["back"]),
                6,
            ),
            round(
                min(point[2] for point in component["back"]),
                6,
            ),
            round(
                max(point[2] for point in component["back"]),
                6,
            ),
        )
        for component in result[
            "component_meshes"
        ]
    )

    assert bounds == (
        (0.8, 3.2, 0.875, 2.625),
        (4.8, 7.2, 0.875, 2.625),
        (8.8, 11.2, 0.875, 2.625),
        (0.8, 3.2, 4.375, 6.125),
        (4.8, 7.2, 4.375, 6.125),
        (8.8, 11.2, 4.375, 6.125),
    )


def test_panel_identity_and_region_metadata_are_preserved():
    result = AtlasFacadePanelLayoutMesher.build(
        wall_quad=WALL_QUAD,
        bay_analysis=_two_by_three_bay_analysis(),
    )

    identities = tuple(
        (
            component["level_index"],
            component["bay_index"],
            component["region_name"],
        )
        for component in result[
            "component_meshes"
        ]
    )

    assert identities == (
        (0, 0, "ground_floor"),
        (0, 1, "ground_floor"),
        (0, 2, "ground_floor"),
        (1, 0, "top_floor"),
        (1, 1, "top_floor"),
        (1, 2, "top_floor"),
    )


def test_each_facade_panel_is_closed_and_manifold():
    result = AtlasFacadePanelLayoutMesher.build(
        wall_quad=WALL_QUAD,
        bay_analysis=_two_by_three_bay_analysis(),
    )

    for component in result[
        "component_meshes"
    ]:
        report = AtlasMeshValidator._topology_report(
            component
        )

        assert report["open_edge_count"] == 0
        assert report["non_manifold_edge_count"] == 0
