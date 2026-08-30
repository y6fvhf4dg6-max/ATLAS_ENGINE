from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_canonical_head_region_aware_relief_depth_policy import (
    AtlasCanonicalHeadRegionAwareReliefDepthPolicy,
)


def _fixture():
    """
    Small synthetic visible-face depth field.

    The source intentionally contains globally large depth range
    while central facial distinctions are compact. This models the
    failure observed in the real candidate, where a global transfer
    consumes the physical depth budget before nose/lip detail becomes
    printable.
    """

    source = np.asarray(
        (
            (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
            (0.0, 3.0, 3.1, 3.2, 3.0, 0.0),
            (0.0, 4.0, 6.00, 6.10, 4.0, 0.0),
            (0.0, 4.1, 6.05, 6.12, 4.1, 0.0),
            (0.0, 2.0, 5.85, 5.90, 2.0, 0.0),
            (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        ),
        dtype=np.float64,
    )

    coverage = np.asarray(
        (
            (False, False, False, False, False, False),
            (False, True,  True,  True,  True,  False),
            (False, True,  True,  True,  True,  False),
            (False, True,  True,  True,  True,  False),
            (False, True,  True,  True,  True,  False),
            (False, False, False, False, False, False),
        ),
        dtype=np.bool_,
    )

    zero = np.zeros_like(source)
    face = coverage.astype(np.float64)

    nose_body = zero.copy()
    nose_body[2:4, 2:4] = 1.0

    nose_base = zero.copy()
    nose_base[3, 2:4] = 1.0

    philtrum = zero.copy()
    philtrum[4, 2:4] = 1.0

    upper_lip = zero.copy()
    upper_lip[4, 2:4] = 1.0

    left_cheek = zero.copy()
    left_cheek[2:4, 1] = 1.0

    right_cheek = zero.copy()
    right_cheek[2:4, 4] = 1.0

    eye_glasses = zero.copy()
    eye_glasses[1, 1:5] = 1.0

    lower_lip = zero.copy()
    lower_lip[4, 1:5] = 0.5

    chin = zero.copy()
    chin[4, 1:5] = 0.25

    masks = {
        "eye_glasses": eye_glasses,
        "nose_bridge": nose_body * 0.5,
        "nose_body": nose_body,
        "nose_base": nose_base,
        "philtrum": philtrum,
        "upper_lip": upper_lip,
        "lower_lip": lower_lip,
        "left_cheek": left_cheek,
        "right_cheek": right_cheek,
        "chin": chin,
        "face_interior": face,
        "face_boundary_falloff": zero,
    }

    return source, coverage, masks


def _transfer():
    source, coverage, masks = _fixture()

    return (
        AtlasCanonicalHeadRegionAwareReliefDepthPolicy.transfer(
            source_depth_map=source,
            coverage_map=coverage,
            region_masks=masks,
            relief_height_mm=2.0,
            minimum_printable_separation_mm=0.20,
        )
    )


def test_transfer_returns_bounded_float64_depth_map():
    result = _transfer()

    depth = np.asarray(
        result.depth_map_mm,
        dtype=np.float64,
    )

    assert depth.shape == (6, 6)
    assert depth.dtype == np.float64
    assert np.all(np.isfinite(depth))
    assert float(depth.min()) >= 0.0
    assert float(depth.max()) <= 2.0


def test_transfer_preserves_coverage_contract():
    source, coverage, masks = _fixture()

    result = (
        AtlasCanonicalHeadRegionAwareReliefDepthPolicy.transfer(
            source_depth_map=source,
            coverage_map=coverage,
            region_masks=masks,
            relief_height_mm=2.0,
            minimum_printable_separation_mm=0.20,
        )
    )

    assert np.array_equal(
        result.coverage_map,
        coverage,
    )

    assert np.allclose(
        result.depth_map_mm[~coverage],
        0.0,
        atol=1.0e-12,
    )


def test_transfer_preserves_local_source_order_for_distinct_depths():
    result = _transfer()
    depth = result.depth_map_mm

    # Within the nose-body support the source increases from
    # row 2 to row 3. Region-aware enhancement may enlarge the
    # distinction but must not reverse its physical ordering.
    assert depth[3, 2] >= depth[2, 2]
    assert depth[3, 3] >= depth[2, 3]


def test_region_policy_materially_improves_nose_to_upper_lip_separation():
    source, coverage, masks = _fixture()

    result = (
        AtlasCanonicalHeadRegionAwareReliefDepthPolicy.transfer(
            source_depth_map=source,
            coverage_map=coverage,
            region_masks=masks,
            relief_height_mm=2.0,
            minimum_printable_separation_mm=0.20,
        )
    )

    nose_support = masks["nose_body"] >= 0.50
    lip_support = masks["upper_lip"] >= 0.50

    mapped_nose = float(
        np.mean(result.depth_map_mm[nose_support])
    )
    mapped_lip = float(
        np.mean(result.depth_map_mm[lip_support])
    )

    source_covered = source[coverage]
    baseline = np.zeros_like(source)

    baseline[coverage] = (
        (
            source_covered
            - float(source_covered.min())
        )
        / (
            float(source_covered.max())
            - float(source_covered.min())
        )
        * 2.0
    )

    baseline_separation = abs(
        float(np.mean(baseline[nose_support]))
        - float(np.mean(baseline[lip_support]))
    )

    mapped_separation = abs(
        mapped_nose - mapped_lip
    )

    assert mapped_separation > baseline_separation
    assert mapped_separation >= 0.18


def test_region_policy_does_not_require_dense_canonical_semantics():
    source, coverage, masks = _fixture()

    # Contract uses only raster-space region masks. It does not
    # require FLAME vertex semantic IDs or a dense canonical
    # semantic mapping.
    result = (
        AtlasCanonicalHeadRegionAwareReliefDepthPolicy.transfer(
            source_depth_map=source,
            coverage_map=coverage,
            region_masks=masks,
            relief_height_mm=2.0,
            minimum_printable_separation_mm=0.20,
        )
    )

    assert (
        result.metadata["semantic_support"]
        == "raster_region_masks"
    )


def test_result_reports_explicit_policy_provenance():
    result = _transfer()

    assert (
        result.metadata["transfer_kind"]
        == "region_aware_bounded_local_depth_allocation"
    )

    assert (
        result.metadata["policy_provenance"]
        == "atlas_canonical_head_region_aware_relief_depth_policy:v1"
    )

    assert (
        result.metadata[
            "minimum_printable_separation_mm"
        ]
        == pytest.approx(0.20)
    )


@pytest.mark.parametrize(
    "relief_height_mm",
    (
        0.0,
        -1.0,
        float("nan"),
        float("inf"),
    ),
)
def test_transfer_rejects_invalid_relief_height(
    relief_height_mm,
):
    source, coverage, masks = _fixture()

    with pytest.raises(
        ValueError,
        match="relief_height_mm",
    ):
        AtlasCanonicalHeadRegionAwareReliefDepthPolicy.transfer(
            source_depth_map=source,
            coverage_map=coverage,
            region_masks=masks,
            relief_height_mm=relief_height_mm,
            minimum_printable_separation_mm=0.20,
        )


@pytest.mark.parametrize(
    "minimum_separation",
    (
        0.0,
        -0.1,
        float("nan"),
        float("inf"),
        2.1,
    ),
)
def test_transfer_rejects_invalid_minimum_printable_separation(
    minimum_separation,
):
    source, coverage, masks = _fixture()

    with pytest.raises(
        ValueError,
        match="minimum_printable_separation_mm",
    ):
        AtlasCanonicalHeadRegionAwareReliefDepthPolicy.transfer(
            source_depth_map=source,
            coverage_map=coverage,
            region_masks=masks,
            relief_height_mm=2.0,
            minimum_printable_separation_mm=minimum_separation,
        )


def test_transfer_rejects_region_mask_shape_mismatch():
    source, coverage, masks = _fixture()
    masks = dict(masks)
    masks["nose_body"] = np.zeros(
        (3, 3),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="nose_body|shape",
    ):
        AtlasCanonicalHeadRegionAwareReliefDepthPolicy.transfer(
            source_depth_map=source,
            coverage_map=coverage,
            region_masks=masks,
            relief_height_mm=2.0,
            minimum_printable_separation_mm=0.20,
        )


def test_transfer_rejects_missing_required_region():
    source, coverage, masks = _fixture()
    masks = dict(masks)
    del masks["nose_base"]

    with pytest.raises(
        ValueError,
        match="nose_base",
    ):
        AtlasCanonicalHeadRegionAwareReliefDepthPolicy.transfer(
            source_depth_map=source,
            coverage_map=coverage,
            region_masks=masks,
            relief_height_mm=2.0,
            minimum_printable_separation_mm=0.20,
        )


def test_policy_reports_robust_macro_base_contract():
    result = _transfer()

    assert (
        result.metadata["base_transfer"]
        == "covered_robust_percentile_linear"
    )
    assert (
        result.metadata["base_low_percentile"]
        == pytest.approx(0.25)
    )
    assert (
        result.metadata["base_high_percentile"]
        == pytest.approx(99.75)
    )


def test_policy_derives_empirical_allocations_from_printable_separation():
    result = _transfer()

    assert (
        result.metadata["nose_positive_allocation_mm"]
        == pytest.approx(0.22)
    )
    assert (
        result.metadata["lower_face_negative_allocation_mm"]
        == pytest.approx(0.15)
    )
    assert (
        result.metadata["nose_allocation_factor"]
        == pytest.approx(1.10)
    )
    assert (
        result.metadata["lower_face_allocation_factor"]
        == pytest.approx(0.75)
    )


def test_policy_uses_coherent_lower_face_support():
    result = _transfer()

    assert (
        result.metadata["local_allocation"]
        == "nose_positive_coherent_lower_face_negative"
    )

    assert result.metadata["lower_face_regions"] == (
        "upper_lip",
        "lower_lip",
        "philtrum",
        "chin",
    )


def test_robust_macro_base_limits_extreme_source_outlier_consumption():
    # Percentile clipping needs enough covered samples for P0.25 to
    # represent a non-zero population fraction. The normal 6x6 fixture
    # contains only 16 covered samples, so one isolated minimum still
    # dominates the interpolated 0.25th percentile.
    rows = 50
    columns = 50

    source = np.linspace(
        0.0,
        10.0,
        rows * columns,
        dtype=np.float64,
    ).reshape(rows, columns)

    coverage = np.ones(
        (rows, columns),
        dtype=np.bool_,
    )

    source[0, 0] = -1000.0

    zero = np.zeros_like(source)
    face = np.ones_like(source)

    nose_body = zero.copy()
    nose_body[20:30, 20:30] = 1.0

    masks = {
        "eye_glasses": zero.copy(),
        "nose_bridge": zero.copy(),
        "nose_body": nose_body,
        "nose_base": zero.copy(),
        "philtrum": zero.copy(),
        "upper_lip": zero.copy(),
        "lower_lip": zero.copy(),
        "left_cheek": zero.copy(),
        "right_cheek": zero.copy(),
        "chin": zero.copy(),
        "face_interior": face,
        "face_boundary_falloff": zero.copy(),
    }

    result = (
        AtlasCanonicalHeadRegionAwareReliefDepthPolicy.transfer(
            source_depth_map=source,
            coverage_map=coverage,
            region_masks=masks,
            relief_height_mm=2.0,
            minimum_printable_separation_mm=0.20,
        )
    )

    central = result.depth_map_mm[
        masks["nose_body"] >= 0.50
    ]

    # The single -1000 outlier must not collapse ordinary central-face
    # variation to a saturated constant.
    assert float(np.ptp(central)) > 0.01
    assert np.unique(
        np.round(central, decimals=8)
    ).size > 2


def test_lower_face_allocation_is_not_upper_lip_only():
    source, coverage, masks = _fixture()

    result = (
        AtlasCanonicalHeadRegionAwareReliefDepthPolicy.transfer(
            source_depth_map=source,
            coverage_map=coverage,
            region_masks=masks,
            relief_height_mm=2.0,
            minimum_printable_separation_mm=0.20,
        )
    )

    # Explicit metadata prevents silently returning to the earlier
    # upper-lip-only opposing field that degraded lower-face structure.
    assert (
        result.metadata["lower_face_region_weights"]
        == {
            "upper_lip": pytest.approx(1.00),
            "lower_lip": pytest.approx(0.80),
            "philtrum": pytest.approx(0.65),
            "chin": pytest.approx(0.70),
        }
    )
