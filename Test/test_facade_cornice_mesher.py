from CORE.atlas_facade_cornice_layout import (
    AtlasFacadeCorniceLayout,
)
from CORE.atlas_facade_cornice_mesher import (
    AtlasFacadeCorniceMesher,
)
from CORE.atlas_facade_region_analyzer import (
    AtlasFacadeRegionAnalyzer,
)


WALL_QUAD = (
    (0.0, 0.0, 0.0),
    (12.0, 0.0, 0.0),
    (12.0, 0.0, 14.0),
    (0.0, 0.0, 14.0),
)


def _cornice_layout(
    *,
    include_top_cornice=False,
):
    region_analysis = AtlasFacadeRegionAnalyzer.analyze(
        tags={
            "building:levels": "4",
        },
        total_height_m=14.0,
    )

    return AtlasFacadeCorniceLayout.create(
        region_analysis=region_analysis,
        include_top_cornice=include_top_cornice,
    )


def test_floor_cornices_create_closed_horizontal_prisms():
    result = AtlasFacadeCorniceMesher.build(
        wall_quad=WALL_QUAD,
        cornice_analysis=_cornice_layout(),
        band_height_mm=0.40,
        depth_mm=0.28,
        embed_mm=0.05,
    )

    assert result["cornice_count"] == 3
    assert len(result["component_meshes"]) == 3
    assert len(result["triangles"]) == 36

    first = result["component_meshes"][0]

    assert first["component_type"] == "facade_cornice"
    assert first["cornice_kind"] == "floor_cornice"
    assert first["cornice_index"] == 0
    assert first["boundary_level_index"] == 1
    assert first["band_height_mm"] == 0.40
    assert first["depth_mm"] == 0.28
    assert first["embed_mm"] == 0.05
    assert len(first["triangles"]) == 12


def test_cornices_are_positioned_on_real_floor_boundaries():
    result = AtlasFacadeCorniceMesher.build(
        wall_quad=WALL_QUAD,
        cornice_analysis=_cornice_layout(),
        band_height_mm=0.40,
    )

    bounds = tuple(
        (
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
        (3.3, 3.7),
        (6.8, 7.2),
        (10.3, 10.7),
    )


def test_top_cornice_metadata_is_preserved():
    result = AtlasFacadeCorniceMesher.build(
        wall_quad=WALL_QUAD,
        cornice_analysis=_cornice_layout(
            include_top_cornice=True,
        ),
        band_height_mm=0.40,
    )

    top = result["component_meshes"][-1]

    assert top["cornice_kind"] == "top_cornice"
    assert top["boundary_level_index"] == 4
