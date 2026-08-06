from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.atlas_architectural_relief_depth_composer import (
    AtlasArchitecturalReliefDepthComposer,
    AtlasArchitecturalReliefDepthProfile,
)


def _bands():
    form = np.full(
        (2, 3),
        0.50,
        dtype=np.float64,
    )
    detail = np.array(
        [
            [0.10, 0.20, -0.10],
            [0.30, -0.20, 0.40],
        ],
        dtype=np.float64,
    )
    micro_detail = np.array(
        [
            [0.20, 0.20, -0.20],
            [0.20, -0.20, 0.20],
        ],
        dtype=np.float64,
    )

    return form, detail, micro_detail


def _material_map():
    return np.array(
        [
            [0, 1, 2],
            [0, 1, 2],
        ],
        dtype=np.uint8,
    )


def test_composes_depth_with_material_specific_profiles():
    form, detail, micro_detail = _bands()

    result = (
        AtlasArchitecturalReliefDepthComposer
        .compose(
            form=form,
            detail=detail,
            micro_detail=micro_detail,
            material_id_map=_material_map(),
            material_names=(
                "rock",
                "vegetation",
                "tomb_facade",
            ),
            default_profile=(
                AtlasArchitecturalReliefDepthProfile(
                    form_weight=1.0,
                    detail_weight=0.5,
                    micro_detail_weight=0.25,
                    micro_detail_limit=0.10,
                )
            ),
            material_profiles={
                "vegetation": (
                    AtlasArchitecturalReliefDepthProfile(
                        form_weight=0.8,
                        detail_weight=0.2,
                        micro_detail_weight=0.0,
                        micro_detail_limit=0.05,
                    )
                ),
                "tomb_facade": (
                    AtlasArchitecturalReliefDepthProfile(
                        form_weight=1.2,
                        detail_weight=0.8,
                        micro_detail_weight=0.4,
                        micro_detail_limit=0.15,
                    )
                ),
            },
        )
    )

    expected = np.array(
        [
            [
                0.575,
                0.44,
                0.46,
            ],
            [
                0.675,
                0.36,
                0.98,
            ],
        ],
        dtype=np.float64,
    )

    np.testing.assert_allclose(
        result["depth_candidate"],
        expected,
    )

    assert result["type"] == (
        "architectural_relief_depth_composition"
    )
    assert result["material_names"] == (
        "rock",
        "vegetation",
        "tomb_facade",
    )


def test_unconfigured_material_uses_default_profile():
    values = np.ones(
        (1, 2),
        dtype=np.float64,
    )

    result = (
        AtlasArchitecturalReliefDepthComposer
        .compose(
            form=values,
            detail=values,
            micro_detail=values,
            material_id_map=np.array(
                [[0, 1]],
                dtype=np.uint8,
            ),
            material_names=(
                "rock",
                "portal",
            ),
            default_profile=(
                AtlasArchitecturalReliefDepthProfile(
                    form_weight=1.0,
                    detail_weight=0.5,
                    micro_detail_weight=0.25,
                    micro_detail_limit=0.10,
                )
            ),
            material_profiles={},
        )
    )

    np.testing.assert_allclose(
        result["depth_candidate"],
        [[1.525, 1.525]],
    )


def test_reports_resolved_profile_for_each_material():
    values = np.zeros(
        (1, 2),
        dtype=np.float64,
    )
    portal_profile = (
        AtlasArchitecturalReliefDepthProfile(
            form_weight=1.2,
            detail_weight=0.7,
            micro_detail_weight=0.2,
            micro_detail_limit=0.04,
        )
    )

    result = (
        AtlasArchitecturalReliefDepthComposer
        .compose(
            form=values,
            detail=values,
            micro_detail=values,
            material_id_map=np.array(
                [[0, 1]],
                dtype=np.uint8,
            ),
            material_names=(
                "rock",
                "portal",
            ),
            default_profile=(
                AtlasArchitecturalReliefDepthProfile()
            ),
            material_profiles={
                "portal": portal_profile,
            },
        )
    )

    assert (
        result["resolved_profiles"]["portal"]
        == portal_profile
    )
    assert (
        result["resolved_profiles"]["rock"]
        == AtlasArchitecturalReliefDepthProfile()
    )


def test_rejects_profile_for_unknown_material():
    values = np.zeros(
        (1, 1),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="unknown material",
    ):
        AtlasArchitecturalReliefDepthComposer.compose(
            form=values,
            detail=values,
            micro_detail=values,
            material_id_map=np.zeros(
                (1, 1),
                dtype=np.uint8,
            ),
            material_names=("rock",),
            default_profile=(
                AtlasArchitecturalReliefDepthProfile()
            ),
            material_profiles={
                "portal": (
                    AtlasArchitecturalReliefDepthProfile()
                ),
            },
        )


def test_rejects_shape_mismatch():
    with pytest.raises(
        ValueError,
        match="shape",
    ):
        AtlasArchitecturalReliefDepthComposer.compose(
            form=np.zeros((2, 2)),
            detail=np.zeros((2, 2)),
            micro_detail=np.zeros((2, 2)),
            material_id_map=np.zeros(
                (3, 2),
                dtype=np.uint8,
            ),
            material_names=("rock",),
            default_profile=(
                AtlasArchitecturalReliefDepthProfile()
            ),
            material_profiles={},
        )


def test_profile_is_immutable():
    profile = AtlasArchitecturalReliefDepthProfile()

    with pytest.raises(FrozenInstanceError):
        profile.form_weight = 2.0


@pytest.mark.parametrize(
    "field,value",
    [
        ("form_weight", -0.1),
        ("detail_weight", -0.1),
        ("micro_detail_weight", -0.1),
        ("micro_detail_limit", 0.0),
        ("micro_detail_limit", float("nan")),
    ],
)
def test_profile_rejects_invalid_values(
    field,
    value,
):
    kwargs = {
        "form_weight": 1.0,
        "detail_weight": 0.35,
        "micro_detail_weight": 0.10,
        "micro_detail_limit": 0.05,
    }
    kwargs[field] = value

    with pytest.raises(
        ValueError,
        match=field,
    ):
        AtlasArchitecturalReliefDepthProfile(
            **kwargs
        )


def test_compose_does_not_mutate_inputs():
    form, detail, micro_detail = _bands()
    material_map = _material_map()

    originals = (
        form.copy(),
        detail.copy(),
        micro_detail.copy(),
        material_map.copy(),
    )

    AtlasArchitecturalReliefDepthComposer.compose(
        form=form,
        detail=detail,
        micro_detail=micro_detail,
        material_id_map=material_map,
        material_names=(
            "rock",
            "vegetation",
            "tomb_facade",
        ),
        default_profile=(
            AtlasArchitecturalReliefDepthProfile()
        ),
        material_profiles={},
    )

    np.testing.assert_array_equal(
        form,
        originals[0],
    )
    np.testing.assert_array_equal(
        detail,
        originals[1],
    )
    np.testing.assert_array_equal(
        micro_detail,
        originals[2],
    )
    np.testing.assert_array_equal(
        material_map,
        originals[3],
    )
