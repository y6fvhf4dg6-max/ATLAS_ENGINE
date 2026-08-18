from CORE.atlas_facade_bay_analyzer import (
    AtlasFacadeBayAnalyzer,
)
from CORE.atlas_facade_opening_layout import (
    AtlasFacadeOpeningLayout,
)
from CORE.atlas_facade_portal_surround_mesher import (
    AtlasFacadePortalSurroundMesher,
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


def _portal_layout():
    region_analysis = AtlasFacadeRegionAnalyzer.analyze(
        tags={
            "building:levels": "1",
        },
        total_height_m=7.0,
    )

    bay_analysis = AtlasFacadeBayAnalyzer.analyze(
        region_analysis=region_analysis,
        bay_count=1,
    )

    return AtlasFacadeOpeningLayout.create_uniform(
        bay_analysis=bay_analysis,
        opening_kind="portal",
        horizontal_margin_ratio=0.30,
        vertical_margin_ratio=0.10,
    )


def test_portal_surround_builds_two_jambs_and_one_lintel():
    result = AtlasFacadePortalSurroundMesher.build(
        wall_quad=WALL_QUAD,
        opening_analysis=_portal_layout(),
        surround_width_ratio=0.12,
        depth_mm=0.24,
        embed_mm=0.04,
    )

    assert result["portal_count"] == 1
    assert len(result["component_meshes"]) == 3
    assert tuple(
        component["surround_part"]
        for component in result["component_meshes"]
    ) == (
        "left_jamb",
        "right_jamb",
        "lintel",
    )


def test_portal_surround_components_are_closed_and_manifold():
    result = AtlasFacadePortalSurroundMesher.build(
        wall_quad=WALL_QUAD,
        opening_analysis=_portal_layout(),
        surround_width_ratio=0.12,
    )

    for component in result["component_meshes"]:
        report = AtlasMeshValidator._topology_report(
            component
        )

        assert report["open_edge_count"] == 0
        assert report["non_manifold_edge_count"] == 0


def test_portal_surround_preserves_opening_identity():
    opening_analysis = _portal_layout()

    result = AtlasFacadePortalSurroundMesher.build(
        wall_quad=WALL_QUAD,
        opening_analysis=opening_analysis,
        surround_width_ratio=0.12,
    )

    first = result["component_meshes"][0]
    source_opening = opening_analysis.openings[0]

    assert first["component_type"] == "facade_portal_surround"
    assert first["opening_kind"] == source_opening.opening_kind
    assert first["level_index"] == source_opening.level_index
    assert first["bay_index"] == source_opening.bay_index
    assert first["opening_index"] == source_opening.opening_index
    assert first["region_name"] == source_opening.region_name
    assert first["source_system"] == "facade_portal_surround_mesher"
