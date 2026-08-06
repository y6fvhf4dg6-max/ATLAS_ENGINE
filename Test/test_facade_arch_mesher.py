from CORE.atlas_facade_arch_mesher import (
    AtlasFacadeArchMesher,
)
from CORE.atlas_facade_bay_analyzer import (
    AtlasFacadeBayAnalyzer,
)
from CORE.atlas_facade_opening_layout import (
    AtlasFacadeOpeningLayout,
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


def _arch_layout():
    region_analysis = AtlasFacadeRegionAnalyzer.analyze(
        tags={
            "building:levels": "2",
        },
        total_height_m=7.0,
    )

    bay_analysis = AtlasFacadeBayAnalyzer.analyze(
        region_analysis=region_analysis,
        bay_count=3,
    )

    return AtlasFacadeOpeningLayout.create_uniform(
        bay_analysis=bay_analysis,
        opening_kind="arch",
        horizontal_margin_ratio=0.20,
        vertical_margin_ratio=0.20,
    )


def test_arches_follow_real_bay_and_floor_regions():
    result = AtlasFacadeArchMesher.build(
        wall_quad=WALL_QUAD,
        opening_analysis=_arch_layout(),
        arch_segments=8,
    )

    assert result["arch_count"] == 6
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
        (0.8, 3.2, 0.7, 2.8),
        (4.8, 7.2, 0.7, 2.8),
        (8.8, 11.2, 0.7, 2.8),
        (0.8, 3.2, 4.2, 6.3),
        (4.8, 7.2, 4.2, 6.3),
        (8.8, 11.2, 4.2, 6.3),
    )


def test_each_arch_component_is_closed_and_manifold():
    result = AtlasFacadeArchMesher.build(
        wall_quad=WALL_QUAD,
        opening_analysis=_arch_layout(),
        arch_segments=8,
    )

    for component in result[
        "component_meshes"
    ]:
        report = AtlasMeshValidator._topology_report(
            component
        )

        assert report["open_edge_count"] == 0
        assert report["non_manifold_edge_count"] == 0


def test_arch_identity_and_region_metadata_are_preserved():
    result = AtlasFacadeArchMesher.build(
        wall_quad=WALL_QUAD,
        opening_analysis=_arch_layout(),
        arch_segments=8,
    )

    first = result["component_meshes"][0]

    assert first["component_type"] == "facade_arch"
    assert first["opening_kind"] == "arch"
    assert first["level_index"] == 0
    assert first["bay_index"] == 0
    assert first["opening_index"] == 0
    assert first["region_name"] == "ground_floor"
