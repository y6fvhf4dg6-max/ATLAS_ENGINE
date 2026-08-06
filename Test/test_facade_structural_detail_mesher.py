from CORE.atlas_facade_bay_analyzer import (
    AtlasFacadeBayAnalyzer,
)
from CORE.atlas_facade_region_analyzer import (
    AtlasFacadeRegionAnalyzer,
)
from CORE.atlas_facade_structural_detail_layout import (
    AtlasFacadeStructuralDetailLayout,
)
from CORE.atlas_facade_structural_detail_mesher import (
    AtlasFacadeStructuralDetailMesher,
)
from CORE.atlas_physical_detail_resolver import (
    AtlasPhysicalDetailResolver,
)


WALL_QUAD = (
    (0.0, 0.0, 0.0),
    (12.0, 0.0, 0.0),
    (12.0, 0.0, 7.0),
    (0.0, 0.0, 7.0),
)


def _layout(
    detail_kind,
    *,
    real_size_m=1.20,
    scale_ratio=3000.0,
):
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

    decision = AtlasPhysicalDetailResolver.resolve(
        real_size_m=real_size_m,
        scale_ratio=scale_ratio,
        nozzle_diameter_mm=0.4,
        detail_type=detail_kind,
    )

    return AtlasFacadeStructuralDetailLayout.create(
        bay_analysis=bay_analysis,
        detail_kind=detail_kind,
        physical_decision=decision,
    )


def test_columns_create_closed_facade_prisms():
    result = AtlasFacadeStructuralDetailMesher.build(
        wall_quad=WALL_QUAD,
        detail_analysis=_layout(
            "column"
        ),
        depth_mm=0.30,
        embed_mm=0.05,
    )

    assert result["detail_kind"] == "column"
    assert result["detail_count"] == 4
    assert len(result["component_meshes"]) == 4
    assert len(result["triangles"]) == 48

    first = result["component_meshes"][0]

    assert first["component_type"] == "facade_structural_detail"
    assert first["detail_kind"] == "column"
    assert first["detail_index"] == 0
    assert first["depth_mm"] == 0.30
    assert first["embed_mm"] == 0.05
    assert len(first["triangles"]) == 12


def test_buttress_geometry_preserves_physical_resolution_metadata():
    result = AtlasFacadeStructuralDetailMesher.build(
        wall_quad=WALL_QUAD,
        detail_analysis=_layout(
            "buttress",
            real_size_m=1.0,
            scale_ratio=5500.0,
        ),
    )

    assert result["detail_kind"] == "buttress"
    assert result["detail_count"] == 4

    assert all(
        component["action"] == "enlarge"
        and component["resolved_size_mm"] == 0.4
        for component in result[
            "component_meshes"
        ]
    )


def test_omitted_detail_layout_creates_no_geometry():
    result = AtlasFacadeStructuralDetailMesher.build(
        wall_quad=WALL_QUAD,
        detail_analysis=_layout(
            "buttress",
            real_size_m=0.10,
            scale_ratio=5500.0,
        ),
    )

    assert result["detail_count"] == 0
    assert result["component_meshes"] == []
    assert result["triangles"] == []


def test_invalid_structural_detail_wall_is_rejected():
    try:
        AtlasFacadeStructuralDetailMesher.build(
            wall_quad=(
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (1.0, 0.0, 1.0),
            ),
            detail_analysis=_layout(
                "column"
            ),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "invalid wall_quad was accepted"
        )


def test_structural_detail_analysis_type_is_required():
    try:
        AtlasFacadeStructuralDetailMesher.build(
            wall_quad=WALL_QUAD,
            detail_analysis={},
        )
    except TypeError:
        pass
    else:
        raise AssertionError(
            "invalid detail_analysis was accepted"
        )


def test_invalid_structural_depth_and_embed_are_rejected():
    detail_analysis = _layout(
        "buttress"
    )

    for arguments in (
        {
            "depth_mm": 0.0,
        },
        {
            "depth_mm": -0.1,
        },
        {
            "embed_mm": -0.01,
        },
    ):
        try:
            AtlasFacadeStructuralDetailMesher.build(
                wall_quad=WALL_QUAD,
                detail_analysis=detail_analysis,
                **arguments,
            )
        except ValueError:
            pass
        else:
            raise AssertionError(
                f"invalid geometry values were accepted: "
                f"{arguments!r}"
            )


def test_structural_detail_metadata_is_added_to_every_mesh():
    result = AtlasFacadeStructuralDetailMesher.build(
        wall_quad=WALL_QUAD,
        detail_analysis=_layout(
            "column"
        ),
        metadata={
            "facade_role": "main_front",
            "profile_name": "generic_classical",
        },
    )

    assert all(
        component["facade_role"]
        == "main_front"
        and component["profile_name"]
        == "generic_classical"
        for component in result[
            "component_meshes"
        ]
    )


def test_column_and_buttress_components_remain_closed_prisms():
    for detail_kind in (
        "column",
        "buttress",
    ):
        result = AtlasFacadeStructuralDetailMesher.build(
            wall_quad=WALL_QUAD,
            detail_analysis=_layout(
                detail_kind
            ),
        )

        assert result["detail_count"] == 4
        assert all(
            len(component["triangles"]) == 12
            and len(component["back"]) == 4
            and len(component["front"]) == 4
            for component in result[
                "component_meshes"
            ]
        )

