from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_architectural_relief_depth_composer import (
    AtlasArchitecturalReliefDepthProfile,
)
from CORE.atlas_architectural_relief_detail_scale_filter import (
    AtlasArchitecturalReliefDetailScaleProfile,
)
from CORE.atlas_architectural_relief_physical_profile import (
    AtlasArchitecturalReliefPhysicalProfile,
)
from CORE.atlas_architectural_relief_structure_preserver import (
    AtlasArchitecturalReliefStructureProfile,
)
from CORE.atlas_architectural_relief_v1_standard import (
    ARCHITECTURAL_RELIEF_V1,
    AtlasArchitecturalReliefV1Standard,
)
from CORE.atlas_relief_product_profile import (
    AtlasReliefProductProfile,
)
from CORE.atlas_relief_product_profile_catalog import (
    ROCK_CARVED_LANDMARK,
)
from CORE.atlas_relief_risk_profile import (
    AtlasReliefRiskProfile,
)


def test_architectural_relief_v1_groups_locked_profiles():
    standard = ARCHITECTURAL_RELIEF_V1

    assert isinstance(
        standard,
        AtlasArchitecturalReliefV1Standard,
    )
    assert standard.name == (
        "architectural-relief-v1"
    )
    assert standard.version == "1.0"

    assert isinstance(
        standard.product_profile,
        AtlasReliefProductProfile,
    )
    assert (
        standard.product_profile
        is ROCK_CARVED_LANDMARK
    )

    assert isinstance(
        standard.depth_profile,
        AtlasArchitecturalReliefDepthProfile,
    )
    assert isinstance(
        standard.structure_profile,
        AtlasArchitecturalReliefStructureProfile,
    )
    assert isinstance(
        standard.detail_scale_profile,
        AtlasArchitecturalReliefDetailScaleProfile,
    )
    assert isinstance(
        standard.physical_profile,
        AtlasArchitecturalReliefPhysicalProfile,
    )
    assert isinstance(
        standard.risk_profile,
        AtlasReliefRiskProfile,
    )


def test_v1_depth_profile_matches_locked_product_weights():
    standard = ARCHITECTURAL_RELIEF_V1
    product = ROCK_CARVED_LANDMARK

    assert (
        standard.depth_profile.form_weight
        == product.form_weight
    )
    assert (
        standard.depth_profile.detail_weight
        == product.detail_weight
    )
    assert (
        standard.depth_profile.micro_detail_weight
        == product.micro_detail_weight
    )
    assert (
        standard.depth_profile.micro_detail_limit
        == product.micro_detail_limit
    )


def test_v1_locks_general_architectural_processing_profiles():
    standard = ARCHITECTURAL_RELIEF_V1

    assert standard.structure_profile == (
        AtlasArchitecturalReliefStructureProfile(
            strength=1.0,
            max_correction=0.05,
        )
    )

    assert standard.detail_scale_profile == (
        AtlasArchitecturalReliefDetailScaleProfile(
            minimum_feature_mm=0.8,
            activity_threshold=0.02,
            minimum_density=0.25,
        )
    )


def test_v1_locks_general_physical_product_profile():
    physical = (
        ARCHITECTURAL_RELIEF_V1
        .physical_profile
    )

    assert physical.name == (
        "architectural-relief-v1"
    )
    assert physical.base_thickness_mm == pytest.approx(
        0.8
    )
    assert physical.relief_height_mm == pytest.approx(
        1.8
    )
    assert (
        physical.target_sample_spacing_mm
        == pytest.approx(0.25)
    )
    assert physical.total_height_mm == pytest.approx(
        2.6
    )


def test_v1_locks_named_print_risk_policy():
    risk = ARCHITECTURAL_RELIEF_V1.risk_profile

    assert risk.name == (
        "architectural-relief-v1"
    )
    assert risk.warning_slope_degrees == pytest.approx(
        55.0
    )
    assert risk.critical_slope_degrees == pytest.approx(
        75.0
    )
    assert (
        risk.warning_slope_area_percent
        == pytest.approx(0.0)
    )
    assert (
        risk.critical_slope_area_percent
        == pytest.approx(0.0)
    )


def test_v1_standard_is_immutable():
    with pytest.raises(FrozenInstanceError):
        ARCHITECTURAL_RELIEF_V1.version = "2.0"


@pytest.mark.parametrize(
    (
        "field",
        "value",
        "message",
    ),
    (
        (
            "name",
            " ",
            "name",
        ),
        (
            "version",
            "",
            "version",
        ),
        (
            "product_profile",
            object(),
            "product_profile",
        ),
        (
            "depth_profile",
            object(),
            "depth_profile",
        ),
        (
            "structure_profile",
            object(),
            "structure_profile",
        ),
        (
            "detail_scale_profile",
            object(),
            "detail_scale_profile",
        ),
        (
            "physical_profile",
            object(),
            "physical_profile",
        ),
        (
            "risk_profile",
            object(),
            "risk_profile",
        ),
    ),
)
def test_v1_standard_rejects_invalid_contract_fields(
    field,
    value,
    message,
):
    values = {
        "name": "architectural-relief-v1",
        "version": "1.0",
        "product_profile": ROCK_CARVED_LANDMARK,
        "depth_profile": (
            AtlasArchitecturalReliefDepthProfile()
        ),
        "structure_profile": (
            AtlasArchitecturalReliefStructureProfile()
        ),
        "detail_scale_profile": (
            AtlasArchitecturalReliefDetailScaleProfile()
        ),
        "physical_profile": (
            AtlasArchitecturalReliefPhysicalProfile(
                name="architectural-relief-v1",
                base_thickness_mm=0.8,
                relief_height_mm=1.8,
                target_sample_spacing_mm=0.25,
            )
        ),
        "risk_profile": (
            AtlasReliefRiskProfile(
                name="architectural-relief-v1",
            )
        ),
    }

    values[field] = value

    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match=message,
    ):
        AtlasArchitecturalReliefV1Standard(
            **values
        )
