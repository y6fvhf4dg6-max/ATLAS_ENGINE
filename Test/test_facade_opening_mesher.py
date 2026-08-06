from CORE.atlas_facade_bay_analyzer import (
    AtlasFacadeBayAnalyzer,
)
from CORE.atlas_facade_opening_layout import (
    AtlasFacadeOpeningLayout,
)
from CORE.atlas_facade_opening_mesher import (
    AtlasFacadeOpeningMesher,
)
from CORE.atlas_facade_region_analyzer import (
    AtlasFacadeRegionAnalyzer,
)


WALL_QUAD = (
    (0.0, 0.0, 0.0),
    (12.0, 0.0, 0.0),
    (12.0, 0.0, 7.0),
    (0.0, 0.0, 7.0),
)


def _opening_layout(
    opening_kind,
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

    return AtlasFacadeOpeningLayout.create_uniform(
        bay_analysis=bay_analysis,
        opening_kind=opening_kind,
        horizontal_margin_ratio=0.20,
        vertical_margin_ratio=0.25,
    )


def test_rectangular_window_openings_create_closed_prisms():
    result = AtlasFacadeOpeningMesher.build(
        wall_quad=WALL_QUAD,
        opening_analysis=_opening_layout(
            "window"
        ),
        depth_mm=0.24,
        embed_mm=0.05,
    )

    assert result["opening_count"] == 6
    assert len(result["component_meshes"]) == 6
    assert len(result["triangles"]) == 72

    first = result["component_meshes"][0]

    assert first["component_type"] == "facade_opening"
    assert first["opening_kind"] == "window"
    assert first["level_index"] == 0
    assert first["bay_index"] == 0
    assert first["opening_index"] == 0
    assert first["depth_mm"] == 0.24
    assert first["embed_mm"] == 0.05
    assert len(first["triangles"]) == 12


def test_door_and_portal_kinds_are_preserved_in_mesh_metadata():
    for opening_kind in (
        "door",
        "portal",
    ):
        result = AtlasFacadeOpeningMesher.build(
            wall_quad=WALL_QUAD,
            opening_analysis=_opening_layout(
                opening_kind
            ),
        )

        assert all(
            component["opening_kind"]
            == opening_kind
            for component in result[
                "component_meshes"
            ]
        )


def test_opening_meshes_preserve_layout_identity_and_region():
    result = AtlasFacadeOpeningMesher.build(
        wall_quad=WALL_QUAD,
        opening_analysis=_opening_layout(
            "window"
        ),
    )

    identities = tuple(
        (
            component["level_index"],
            component["bay_index"],
            component["opening_index"],
            component["region_name"],
        )
        for component in result[
            "component_meshes"
        ]
    )

    assert identities == (
        (0, 0, 0, "ground_floor"),
        (0, 1, 0, "ground_floor"),
        (0, 2, 0, "ground_floor"),
        (1, 0, 0, "top_floor"),
        (1, 1, 0, "top_floor"),
        (1, 2, 0, "top_floor"),
    )


def test_invalid_wall_quad_is_rejected():
    try:
        AtlasFacadeOpeningMesher.build(
            wall_quad=(
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (1.0, 0.0, 1.0),
            ),
            opening_analysis=_opening_layout(
                "window"
            ),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "invalid wall_quad was accepted"
        )


def test_opening_analysis_type_is_required():
    try:
        AtlasFacadeOpeningMesher.build(
            wall_quad=WALL_QUAD,
            opening_analysis={},
        )
    except TypeError:
        pass
    else:
        raise AssertionError(
            "invalid opening_analysis was accepted"
        )


def test_invalid_depth_and_embed_values_are_rejected():
    opening_analysis = _opening_layout(
        "window"
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
            AtlasFacadeOpeningMesher.build(
                wall_quad=WALL_QUAD,
                opening_analysis=opening_analysis,
                **arguments,
            )
        except ValueError:
            pass
        else:
            raise AssertionError(
                f"invalid geometry values were accepted: "
                f"{arguments!r}"
            )


def test_custom_metadata_is_added_to_every_opening_mesh():
    result = AtlasFacadeOpeningMesher.build(
        wall_quad=WALL_QUAD,
        opening_analysis=_opening_layout(
            "portal"
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

