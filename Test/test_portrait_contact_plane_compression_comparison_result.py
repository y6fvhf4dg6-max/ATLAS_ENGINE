from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.atlas_portrait_contact_plane_compression_comparison_result import (
    AtlasPortraitContactPlaneCompressionComparisonResult,
)


def _result(
    *,
    source_height=None,
    compressed_height=None,
    source_maximum_height=0.8,
    target_maximum_height=0.2,
    compression_ratio=0.25,
    contact_row=1,
    contact_column=1,
    maximum_absolute_height_error=0.6,
    mean_absolute_height_error=0.225,
    preview_mean_absolute_error=12.5,
    preview_maximum_absolute_error=34,
    contact_point_preserved=True,
    source_surface_safe=True,
    compressed_surface_safe=True,
    metadata=None,
):
    if source_height is None:
        source_height = np.array(
            [
                [0.0, 0.4, 0.0],
                [0.1, 0.8, 0.1],
            ],
            dtype=np.float64,
        )

    if compressed_height is None:
        compressed_height = np.array(
            [
                [0.000, 0.100, 0.000],
                [0.025, 0.200, 0.025],
            ],
            dtype=np.float64,
        )

    if metadata is None:
        metadata = {
            "compression_mode": (
                "linear_target_maximum_height"
            ),
        }

    return AtlasPortraitContactPlaneCompressionComparisonResult(
        source_height=source_height,
        compressed_height=compressed_height,
        source_maximum_height=source_maximum_height,
        target_maximum_height=target_maximum_height,
        compression_ratio=compression_ratio,
        contact_row=contact_row,
        contact_column=contact_column,
        maximum_absolute_height_error=(
            maximum_absolute_height_error
        ),
        mean_absolute_height_error=(
            mean_absolute_height_error
        ),
        preview_mean_absolute_error=(
            preview_mean_absolute_error
        ),
        preview_maximum_absolute_error=(
            preview_maximum_absolute_error
        ),
        contact_point_preserved=contact_point_preserved,
        source_surface_safe=source_surface_safe,
        compressed_surface_safe=compressed_surface_safe,
        metadata=metadata,
    )


def test_result_normalizes_height_grids():
    result = _result(
        source_height=[
            [0.0, 0.4],
            [0.1, 0.8],
        ],
        compressed_height=[
            [0.0, 0.1],
            [0.025, 0.2],
        ],
        contact_row=1,
        contact_column=1,
    )

    assert result.source_height.dtype == np.float64
    assert result.compressed_height.dtype == np.float64
    assert result.shape == (2, 2)


def test_result_copies_height_grids():
    source = np.array(
        [
            [0.0, 0.4],
            [0.1, 0.8],
        ],
        dtype=np.float64,
    )
    compressed = source * 0.25

    result = _result(
        source_height=source,
        compressed_height=compressed,
        contact_row=1,
        contact_column=1,
    )

    source[0, 0] = 99.0
    compressed[0, 0] = 99.0

    assert result.source_height[0, 0] == pytest.approx(
        0.0,
    )
    assert result.compressed_height[0, 0] == pytest.approx(
        0.0,
    )


def test_result_height_grids_are_read_only():
    result = _result()

    assert not result.source_height.flags.writeable
    assert not result.compressed_height.flags.writeable

    with pytest.raises(
        ValueError,
    ):
        result.source_height[0, 0] = 1.0

    with pytest.raises(
        ValueError,
    ):
        result.compressed_height[0, 0] = 1.0


def test_result_is_frozen():
    result = _result()

    with pytest.raises(
        FrozenInstanceError,
    ):
        result.compression_ratio = 0.5


def test_result_reports_dimensions():
    result = _result()

    assert result.row_count == 2
    assert result.column_count == 3
    assert result.contact_index == (1, 1)


def test_result_reports_height_delta_grid():
    result = _result()

    expected = (
        result.compressed_height
        - result.source_height
    )

    assert result.height_deltas == pytest.approx(
        expected,
    )
    assert result.height_deltas.dtype == np.float64
    assert not result.height_deltas.flags.writeable


def test_result_preserves_numeric_metrics():
    result = _result()

    assert result.source_maximum_height == pytest.approx(
        0.8,
    )
    assert result.target_maximum_height == pytest.approx(
        0.2,
    )
    assert result.compression_ratio == pytest.approx(
        0.25,
    )
    assert (
        result.maximum_absolute_height_error
        == pytest.approx(
            0.6,
        )
    )
    assert (
        result.mean_absolute_height_error
        == pytest.approx(
            0.225,
        )
    )
    assert (
        result.preview_mean_absolute_error
        == pytest.approx(
            12.5,
        )
    )
    assert (
        result.preview_maximum_absolute_error
        == pytest.approx(
            34.0,
        )
    )


def test_result_preserves_boolean_metrics():
    result = _result()

    assert result.contact_point_preserved
    assert result.source_surface_safe
    assert result.compressed_surface_safe


def test_result_copies_metadata():
    metadata = {
        "compression_mode": (
            "linear_target_maximum_height"
        ),
    }

    result = _result(
        metadata=metadata,
    )

    metadata["compression_mode"] = "changed"

    assert result.metadata == {
        "compression_mode": (
            "linear_target_maximum_height"
        ),
    }


def test_result_rejects_height_shape_mismatch():
    with pytest.raises(
        ValueError,
        match="identical shapes",
    ):
        _result(
            compressed_height=np.zeros(
                (
                    3,
                    2,
                ),
                dtype=np.float64,
            ),
        )


def test_result_rejects_non_two_dimensional_height_grid():
    with pytest.raises(
        ValueError,
        match="two-dimensional",
    ):
        _result(
            source_height=np.zeros(
                (
                    2,
                    2,
                    2,
                ),
                dtype=np.float64,
            ),
        )


def test_result_rejects_non_finite_height_grid():
    source = np.zeros(
        (
            2,
            3,
        ),
        dtype=np.float64,
    )
    source[0, 0] = np.nan

    with pytest.raises(
        ValueError,
        match="non-finite",
    ):
        _result(
            source_height=source,
        )


def test_result_rejects_negative_height_grid():
    compressed = np.zeros(
        (
            2,
            3,
        ),
        dtype=np.float64,
    )
    compressed[0, 0] = -0.01

    with pytest.raises(
        ValueError,
        match="negative",
    ):
        _result(
            compressed_height=compressed,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "contact_row",
        "contact_column",
    ],
)
def test_result_rejects_non_integer_contact_indices(
    field_name,
):
    values = {
        "contact_row": 1,
        "contact_column": 1,
    }
    values[field_name] = 1.5

    with pytest.raises(
        TypeError,
        match=field_name,
    ):
        _result(
            **values,
        )


@pytest.mark.parametrize(
    (
        "contact_row",
        "contact_column",
    ),
    [
        (-1, 1),
        (2, 1),
        (1, -1),
        (1, 3),
    ],
)
def test_result_rejects_out_of_range_contact_indices(
    contact_row,
    contact_column,
):
    with pytest.raises(
        ValueError,
        match="contact",
    ):
        _result(
            contact_row=contact_row,
            contact_column=contact_column,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "source_maximum_height",
        "target_maximum_height",
        "compression_ratio",
        "maximum_absolute_height_error",
        "mean_absolute_height_error",
        "preview_mean_absolute_error",
        "preview_maximum_absolute_error",
    ],
)
@pytest.mark.parametrize(
    "invalid_value",
    [
        np.nan,
        np.inf,
        "invalid",
        None,
    ],
)
def test_result_rejects_invalid_numeric_metrics(
    field_name,
    invalid_value,
):
    values = {
        field_name: invalid_value,
    }

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _result(
            **values,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "source_maximum_height",
        "target_maximum_height",
        "compression_ratio",
        "maximum_absolute_height_error",
        "mean_absolute_height_error",
        "preview_mean_absolute_error",
        "preview_maximum_absolute_error",
    ],
)
def test_result_rejects_negative_numeric_metrics(
    field_name,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _result(
            **{
                field_name: -0.01,
            },
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "contact_point_preserved",
        "source_surface_safe",
        "compressed_surface_safe",
    ],
)
def test_result_rejects_non_boolean_flags(
    field_name,
):
    with pytest.raises(
        TypeError,
        match=field_name,
    ):
        _result(
            **{
                field_name: 1,
            },
        )


def test_result_rejects_invalid_metadata_type():
    with pytest.raises(
        TypeError,
        match="metadata",
    ):
        _result(
            metadata=[
                "invalid",
            ],
        )
