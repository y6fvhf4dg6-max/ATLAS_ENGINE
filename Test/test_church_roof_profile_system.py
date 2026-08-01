import pytest

from CORE.atlas_church_roof_profile_system import (
    AtlasChurchRoofProfileSystem,
)


def test_roof_system_defines_required_architectural_layers():
    profile = AtlasChurchRoofProfileSystem.resolve(
        longitudinal_span=60.0,
        lateral_span=30.0,
        wall_height=20.0,
    )

    assert tuple(
        section.section_type
        for section in profile.sections
    ) == (
        "outer_aisle_left",
        "outer_aisle_right",
        "main_nave",
        "transept",
        "apse",
    )


def test_outer_aisle_roofs_are_lower_than_main_nave_roof():
    profile = AtlasChurchRoofProfileSystem.resolve(
        longitudinal_span=60.0,
        lateral_span=30.0,
        wall_height=20.0,
    )

    left_aisle = profile.section(
        "outer_aisle_left"
    )
    right_aisle = profile.section(
        "outer_aisle_right"
    )
    main_nave = profile.section(
        "main_nave"
    )

    assert left_aisle.eave_z < main_nave.eave_z
    assert right_aisle.eave_z < main_nave.eave_z

    assert left_aisle.ridge_z < main_nave.ridge_z
    assert right_aisle.ridge_z < main_nave.ridge_z


def test_main_nave_uses_long_gable_roof():
    profile = AtlasChurchRoofProfileSystem.resolve(
        longitudinal_span=60.0,
        lateral_span=30.0,
        wall_height=20.0,
    )

    main_nave = profile.section(
        "main_nave"
    )

    assert main_nave.roof_shape == "gable"
    assert main_nave.longitudinal_ratio >= 0.70
    assert main_nave.lateral_ratio < 1.0
    assert main_nave.ridge_z > main_nave.eave_z


def test_transept_uses_independent_gable_roof():
    profile = AtlasChurchRoofProfileSystem.resolve(
        longitudinal_span=60.0,
        lateral_span=30.0,
        wall_height=20.0,
    )

    transept = profile.section(
        "transept"
    )

    assert transept.roof_shape == "gable"
    assert transept.orientation == "lateral"
    assert transept.ridge_z > transept.eave_z


def test_apse_uses_polygon_pyramid_roof():
    profile = AtlasChurchRoofProfileSystem.resolve(
        longitudinal_span=60.0,
        lateral_span=30.0,
        wall_height=20.0,
    )

    apse = profile.section(
        "apse"
    )

    assert apse.roof_shape == "polygon_pyramid"
    assert apse.polygon_sides >= 5
    assert apse.ridge_z > apse.eave_z


def test_roof_layers_have_independent_eave_and_ridge_levels():
    profile = AtlasChurchRoofProfileSystem.resolve(
        longitudinal_span=60.0,
        lateral_span=30.0,
        wall_height=20.0,
    )

    levels = {
        (
            section.eave_z,
            section.ridge_z,
        )
        for section in profile.sections
    }

    assert len(levels) >= 3


@pytest.mark.parametrize(
    "longitudinal_span,lateral_span,wall_height",
    [
        (0.0, 30.0, 20.0),
        (60.0, 0.0, 20.0),
        (60.0, 30.0, 0.0),
        (-1.0, 30.0, 20.0),
        (60.0, -1.0, 20.0),
        (60.0, 30.0, -1.0),
    ],
)
def test_roof_system_rejects_non_positive_dimensions(
    longitudinal_span,
    lateral_span,
    wall_height,
):
    with pytest.raises(ValueError):
        AtlasChurchRoofProfileSystem.resolve(
            longitudinal_span=longitudinal_span,
            lateral_span=lateral_span,
            wall_height=wall_height,
        )
