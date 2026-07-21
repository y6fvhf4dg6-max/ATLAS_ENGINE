from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.atlas_portrait_contact_plane_projection_result import (
    AtlasPortraitContactPlaneProjectionResult,
)


def _result(
    *,
    distance_to_plane=None,
    contact_plane_z=0.8,
    contact_row=1,
    contact_column=1,
    maximum_distance=0.8,
    source_shape=(2, 3),
    metadata=None,
):
    if distance_to_plane is None:
        distance_to_plane = np.array(
            [
                [0.8, 0.4, 0.8],
                [0.7, 0.0, 0.7],
            ],
            dtype=np.float64,
        )

    if metadata is None:
        metadata = {
            "projection_mode": "contact_plane",
        }

    return AtlasPortraitContactPlaneProjectionResult(
        distance_to_plane=distance_to_plane,
        contact_plane_z=contact_plane_z,
        contact_row=contact_row,
        contact_column=contact_column,
        maximum_distance=maximum_distance,
        source_shape=source_shape,
        metadata=metadata,
    )


def test_result_normalizes_distance_grid():
    result = _result(
        distance_to_plane=[
            [0, 0.4, 0.8],
            [0.7, 0.0, 0.7],
        ],
    )

    assert result.distance_to_plane.dtype == np.float64
    assert result.distance_to_plane.shape == (2, 3)


def test_result_copies_distance_grid():
    values = np.array(
        [
            [0.8, 0.4, 0.8],
            [0.7, 0.0, 0.7],
        ],
        dtype=np.float64,
    )

    result = _result(
        distance_to_plane=values,
    )

    values[0, 0] = 99.0

    assert result.distance_to_plane[0, 0] == pytest.approx(
        0.8,
    )


def test_result_distance_grid_is_read_only():
    result = _result()

    assert not result.distance_to_plane.flags.writeable

    with pytest.raises(
        ValueError,
    ):
        result.distance_to_plane[0, 0] = 1.0


def test_result_is_frozen():
    result = _result()

    with pytest.raises(
        FrozenInstanceError,
    ):
        result.contact_plane_z = 1.0


def test_result_reports_shape_and_dimensions():
    result = _result()

    assert result.shape == (2, 3)
    assert result.row_count == 2
    assert result.column_count == 3


def test_result_preserves_contact_location():
    result = _result(
        contact_row=1,
        contact_column=1,
    )

    assert result.contact_index == (1, 1)
    assert result.distance_to_plane[
        result.contact_index
    ] == pytest.approx(
        0.0,
    )


def test_result_reports_distance_range():
    result = _result()

    assert result.minimum_distance == pytest.approx(
        0.0,
    )
    assert result.maximum_distance == pytest.approx(
        0.8,
    )


def test_result_preserves_projection_metadata():
    result = _result(
        contact_plane_z=0.8,
        source_shape=(2, 3),
        metadata={
            "projection_mode": "contact_plane",
            "source": "synthetic",
        },
    )

    assert result.contact_plane_z == pytest.approx(
        0.8,
    )
    assert result.source_shape == (2, 3)
    assert result.metadata == {
        "projection_mode": "contact_plane",
        "source": "synthetic",
    }


def test_result_copies_metadata():
    metadata = {
        "projection_mode": "contact_plane",
    }

    result = _result(
        metadata=metadata,
    )

    metadata["projection_mode"] = "changed"

    assert result.metadata == {
        "projection_mode": "contact_plane",
    }


def test_result_rejects_non_two_dimensional_distance_grid():
    with pytest.raises(
        ValueError,
        match="two-dimensional",
    ):
        _result(
            distance_to_plane=np.zeros(
                (
                    2,
                    2,
                    2,
                ),
                dtype=np.float64,
            ),
        )


def test_result_rejects_too_small_distance_grid():
    with pytest.raises(
        ValueError,
        match="at least two rows and two columns",
    ):
        _result(
            distance_to_plane=np.zeros(
                (
                    1,
                    3,
                ),
                dtype=np.float64,
            ),
            source_shape=(1, 3),
        )


def test_result_rejects_non_finite_distance_values():
    values = np.zeros(
        (
            2,
            3,
        ),
        dtype=np.float64,
    )
    values[0, 0] = np.nan

    with pytest.raises(
        ValueError,
        match="non-finite",
    ):
        _result(
            distance_to_plane=values,
        )


def test_result_rejects_negative_distance_values():
    values = np.zeros(
        (
            2,
            3,
        ),
        dtype=np.float64,
    )
    values[0, 0] = -0.01

    with pytest.raises(
        ValueError,
        match="must not contain negative",
    ):
        _result(
            distance_to_plane=values,
        )


def test_result_rejects_source_shape_mismatch():
    with pytest.raises(
        ValueError,
        match="source_shape",
    ):
        _result(
            source_shape=(3, 2),
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
def test_result_rejects_out_of_range_contact_index(
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


def test_result_requires_zero_distance_at_contact_point():
    with pytest.raises(
        ValueError,
        match="contact point",
    ):
        _result(
            contact_row=0,
            contact_column=0,
        )


def test_result_requires_maximum_distance_to_match_grid():
    with pytest.raises(
        ValueError,
        match="maximum_distance",
    ):
        _result(
            maximum_distance=0.7,
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
