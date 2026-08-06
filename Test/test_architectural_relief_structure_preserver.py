from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.atlas_architectural_relief_structure_preserver import (
    AtlasArchitecturalReliefStructurePreserver,
    AtlasArchitecturalReliefStructureProfile,
)


def test_builds_feature_protection_map_with_maximum_union():
    edge_mask = np.array(
        [
            [0.0, 1.0, 0.0],
            [0.0, 0.5, 0.0],
        ],
        dtype=np.float64,
    )
    portal_mask = np.array(
        [
            [0.0, 0.6, 0.0],
            [1.0, 0.0, 0.0],
        ],
        dtype=np.float64,
    )

    result = (
        AtlasArchitecturalReliefStructurePreserver
        .build_protection_map(
            feature_masks={
                "architectural_edge": edge_mask,
                "portal": portal_mask,
            },
            feature_weights={
                "architectural_edge": 0.8,
                "portal": 0.5,
            },
        )
    )

    np.testing.assert_allclose(
        result,
        np.array(
            [
                [0.0, 0.8, 0.0],
                [0.5, 0.4, 0.0],
            ],
            dtype=np.float64,
        ),
    )


def test_preserves_structure_with_bounded_correction():
    candidate = np.array(
        [
            [0.20, 0.30, 0.40],
            [0.50, 0.60, 0.70],
        ],
        dtype=np.float64,
    )
    reference = np.array(
        [
            [0.20, 0.50, 0.20],
            [0.90, 0.10, 0.70],
        ],
        dtype=np.float64,
    )
    protection = np.array(
        [
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
        ],
        dtype=np.float64,
    )

    result = (
        AtlasArchitecturalReliefStructurePreserver
        .preserve(
            depth_candidate=candidate,
            structure_reference=reference,
            protection_map=protection,
            profile=(
                AtlasArchitecturalReliefStructureProfile(
                    strength=0.5,
                    max_correction=0.10,
                )
            ),
        )
    )

    np.testing.assert_allclose(
        result["preserved_depth"],
        np.array(
            [
                [0.20, 0.35, 0.40],
                [0.55, 0.60, 0.70],
            ],
            dtype=np.float64,
        ),
    )

    np.testing.assert_allclose(
        result["applied_correction"],
        np.array(
            [
                [0.0, 0.05, 0.0],
                [0.05, 0.0, 0.0],
            ],
            dtype=np.float64,
        ),
    )

    assert result["type"] == (
        "architectural_relief_structure_preservation"
    )


def test_soft_protection_map_scales_local_correction():
    candidate = np.zeros(
        (1, 3),
        dtype=np.float64,
    )
    reference = np.ones_like(
        candidate
    )

    result = (
        AtlasArchitecturalReliefStructurePreserver
        .preserve(
            depth_candidate=candidate,
            structure_reference=reference,
            protection_map=np.array(
                [[0.0, 0.5, 1.0]],
                dtype=np.float64,
            ),
            profile=(
                AtlasArchitecturalReliefStructureProfile(
                    strength=1.0,
                    max_correction=0.20,
                )
            ),
        )
    )

    np.testing.assert_allclose(
        result["preserved_depth"],
        [[0.0, 0.10, 0.20]],
    )


def test_zero_protection_preserves_candidate_exactly():
    candidate = np.array(
        [
            [0.15, 0.35],
            [0.55, 0.75],
        ],
        dtype=np.float64,
    )

    result = (
        AtlasArchitecturalReliefStructurePreserver
        .preserve(
            depth_candidate=candidate,
            structure_reference=np.ones_like(
                candidate
            ),
            protection_map=np.zeros_like(
                candidate
            ),
            profile=(
                AtlasArchitecturalReliefStructureProfile()
            ),
        )
    )

    np.testing.assert_array_equal(
        result["preserved_depth"],
        candidate,
    )


def test_output_can_be_clamped_to_unit_interval():
    result = (
        AtlasArchitecturalReliefStructurePreserver
        .preserve(
            depth_candidate=np.array(
                [[0.98]],
                dtype=np.float64,
            ),
            structure_reference=np.array(
                [[1.50]],
                dtype=np.float64,
            ),
            protection_map=np.array(
                [[1.0]],
                dtype=np.float64,
            ),
            profile=(
                AtlasArchitecturalReliefStructureProfile(
                    strength=1.0,
                    max_correction=0.20,
                )
            ),
            clamp_output=True,
        )
    )

    assert result["preserved_depth"][0, 0] == 1.0


def test_rejects_shape_mismatch():
    with pytest.raises(
        ValueError,
        match="shape",
    ):
        AtlasArchitecturalReliefStructurePreserver.preserve(
            depth_candidate=np.zeros(
                (2, 2),
                dtype=np.float64,
            ),
            structure_reference=np.zeros(
                (2, 3),
                dtype=np.float64,
            ),
            protection_map=np.zeros(
                (2, 2),
                dtype=np.float64,
            ),
            profile=(
                AtlasArchitecturalReliefStructureProfile()
            ),
        )


def test_rejects_weight_for_unknown_feature():
    with pytest.raises(
        ValueError,
        match="unknown feature",
    ):
        AtlasArchitecturalReliefStructurePreserver.build_protection_map(
            feature_masks={
                "portal": np.ones(
                    (2, 2),
                    dtype=np.float64,
                ),
            },
            feature_weights={
                "cornice": 0.8,
            },
        )


def test_profile_is_immutable():
    profile = (
        AtlasArchitecturalReliefStructureProfile()
    )

    with pytest.raises(FrozenInstanceError):
        profile.strength = 0.2


@pytest.mark.parametrize(
    "field,value",
    [
        ("strength", -0.1),
        ("strength", 1.1),
        ("strength", float("nan")),
        ("max_correction", 0.0),
        ("max_correction", -0.1),
        ("max_correction", float("inf")),
    ],
)
def test_profile_rejects_invalid_values(
    field,
    value,
):
    kwargs = {
        "strength": 1.0,
        "max_correction": 0.05,
    }
    kwargs[field] = value

    with pytest.raises(
        ValueError,
        match=field,
    ):
        AtlasArchitecturalReliefStructureProfile(
            **kwargs
        )


def test_preserve_does_not_mutate_inputs():
    candidate = np.full(
        (2, 3),
        0.4,
        dtype=np.float64,
    )
    reference = np.full(
        (2, 3),
        0.8,
        dtype=np.float64,
    )
    protection = np.full(
        (2, 3),
        0.5,
        dtype=np.float64,
    )

    originals = (
        candidate.copy(),
        reference.copy(),
        protection.copy(),
    )

    AtlasArchitecturalReliefStructurePreserver.preserve(
        depth_candidate=candidate,
        structure_reference=reference,
        protection_map=protection,
        profile=(
            AtlasArchitecturalReliefStructureProfile()
        ),
    )

    np.testing.assert_array_equal(
        candidate,
        originals[0],
    )
    np.testing.assert_array_equal(
        reference,
        originals[1],
    )
    np.testing.assert_array_equal(
        protection,
        originals[2],
    )
