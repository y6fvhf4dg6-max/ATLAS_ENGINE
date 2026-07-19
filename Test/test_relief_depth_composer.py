import numpy as np
import pytest

from CORE.atlas_relief_depth_composer import (
    AtlasReliefDepthComposer,
)


def test_composes_form_detail_and_micro_detail():
    form = np.full(
        (2, 2),
        0.5,
        dtype=np.float64,
    )
    detail = np.array(
        [
            [0.1, -0.1],
            [0.2, -0.2],
        ],
        dtype=np.float64,
    )
    micro_detail = np.array(
        [
            [0.05, -0.05],
            [0.10, -0.10],
        ],
        dtype=np.float64,
    )

    result = AtlasReliefDepthComposer.compose(
        form=form,
        detail=detail,
        micro_detail=micro_detail,
        form_weight=1.0,
        detail_weight=0.5,
        micro_detail_weight=0.25,
        micro_detail_limit=0.08,
    )

    expected = (
        form
        + detail * 0.5
        + np.clip(
            micro_detail,
            -0.08,
            0.08,
        ) * 0.25
    )

    assert np.allclose(
        result["depth_candidate"],
        expected,
    )


def test_micro_detail_is_limited_before_weighting():
    form = np.zeros(
        (1, 3),
        dtype=np.float64,
    )
    detail = np.zeros_like(form)
    micro_detail = np.array(
        [[-1.0, 0.0, 1.0]],
        dtype=np.float64,
    )

    result = AtlasReliefDepthComposer.compose(
        form=form,
        detail=detail,
        micro_detail=micro_detail,
        micro_detail_weight=2.0,
        micro_detail_limit=0.1,
    )

    assert np.allclose(
        result["limited_micro_detail"],
        [[-0.1, 0.0, 0.1]],
    )
    assert np.allclose(
        result["weighted_micro_detail"],
        [[-0.2, 0.0, 0.2]],
    )


def test_zero_detail_weights_preserve_form():
    form = np.array(
        [
            [0.1, 0.2],
            [0.3, 0.4],
        ],
        dtype=np.float64,
    )
    detail = np.ones_like(form)
    micro_detail = np.ones_like(form)

    result = AtlasReliefDepthComposer.compose(
        form=form,
        detail=detail,
        micro_detail=micro_detail,
        detail_weight=0.0,
        micro_detail_weight=0.0,
    )

    assert np.array_equal(
        result["depth_candidate"],
        form,
    )


def test_default_weights_favor_form_over_detail():
    form = np.ones(
        (2, 2),
        dtype=np.float64,
    )
    detail = np.ones_like(form)
    micro_detail = np.ones_like(form)

    result = AtlasReliefDepthComposer.compose(
        form=form,
        detail=detail,
        micro_detail=micro_detail,
    )

    assert result["form_weight"] > result["detail_weight"]
    assert (
        result["detail_weight"]
        > result["micro_detail_weight"]
    )


def test_rejects_shape_mismatch():
    form = np.zeros(
        (2, 2),
        dtype=np.float64,
    )
    detail = np.zeros(
        (3, 2),
        dtype=np.float64,
    )
    micro_detail = np.zeros(
        (2, 2),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="must have identical shapes",
    ):
        AtlasReliefDepthComposer.compose(
            form=form,
            detail=detail,
            micro_detail=micro_detail,
        )


@pytest.mark.parametrize(
    "name,value",
    [
        ("form_weight", -0.1),
        ("detail_weight", -0.1),
        ("micro_detail_weight", -0.1),
        ("micro_detail_limit", 0.0),
        ("micro_detail_limit", -0.1),
        ("form_weight", float("nan")),
        ("detail_weight", float("inf")),
        ("micro_detail_weight", "invalid"),
        ("micro_detail_limit", None),
    ],
)
def test_rejects_invalid_parameters(
    name,
    value,
):
    values = np.zeros(
        (2, 2),
        dtype=np.float64,
    )

    kwargs = {
        "form": values,
        "detail": values,
        "micro_detail": values,
    }
    kwargs[name] = value

    with pytest.raises(ValueError):
        AtlasReliefDepthComposer.compose(
            **kwargs,
        )


def test_result_arrays_are_independent():
    values = np.ones(
        (2, 2),
        dtype=np.float64,
    )

    first = AtlasReliefDepthComposer.compose(
        form=values,
        detail=values,
        micro_detail=values,
    )
    first["depth_candidate"][0, 0] = 99.0

    second = AtlasReliefDepthComposer.compose(
        form=values,
        detail=values,
        micro_detail=values,
    )

    assert second["depth_candidate"][0, 0] != 99.0


def test_compose_does_not_mutate_inputs():
    form = np.arange(
        4,
        dtype=np.float64,
    ).reshape(2, 2)
    detail = form.copy()
    micro_detail = form.copy()

    original_form = form.copy()
    original_detail = detail.copy()
    original_micro = micro_detail.copy()

    AtlasReliefDepthComposer.compose(
        form=form,
        detail=detail,
        micro_detail=micro_detail,
    )

    assert np.array_equal(
        form,
        original_form,
    )
    assert np.array_equal(
        detail,
        original_detail,
    )
    assert np.array_equal(
        micro_detail,
        original_micro,
    )
