from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_weak_perspective_fitting_input import (
    AtlasPortraitWeakPerspectiveFittingInput,
)


LANDMARK_NAMES = (
    "left_eye_outer",
    "left_eye_inner",
    "right_eye_inner",
    "right_eye_outer",
    "nose_root",
    "nose_bridge",
    "nose_tip",
    "nose_left",
    "nose_right",
    "mouth_left",
    "upper_lip_center",
    "lower_lip_center",
    "mouth_right",
    "left_eyebrow_outer",
    "left_eyebrow_inner",
    "right_eyebrow_inner",
    "right_eyebrow_outer",
)


def _source_points() -> np.ndarray:
    x_coordinates = np.linspace(
        -0.05,
        0.05,
        len(
            LANDMARK_NAMES,
        ),
        dtype=np.float64,
    )

    y_coordinates = np.linspace(
        0.04,
        -0.05,
        len(
            LANDMARK_NAMES,
        ),
        dtype=np.float64,
    )

    z_coordinates = np.linspace(
        0.03,
        0.08,
        len(
            LANDMARK_NAMES,
        ),
        dtype=np.float64,
    )

    return np.column_stack(
        (
            x_coordinates,
            y_coordinates,
            z_coordinates,
        )
    )


def _target_points() -> np.ndarray:
    x_coordinates = np.linspace(
        0.30,
        0.70,
        len(
            LANDMARK_NAMES,
        ),
        dtype=np.float64,
    )

    y_coordinates = np.linspace(
        0.25,
        0.50,
        len(
            LANDMARK_NAMES,
        ),
        dtype=np.float64,
    )

    return np.column_stack(
        (
            x_coordinates,
            y_coordinates,
        )
    )


def _weights() -> np.ndarray:
    return np.linspace(
        0.75,
        1.0,
        len(
            LANDMARK_NAMES,
        ),
        dtype=np.float64,
    )


def _fitting_input(
    **overrides,
) -> AtlasPortraitWeakPerspectiveFittingInput:
    values = {
        "landmark_names": LANDMARK_NAMES,
        "source_points_3d": _source_points(),
        "target_points_2d": _target_points(),
        "landmark_weights": _weights(),
        "image_width": 1122,
        "image_height": 1402,
        "metadata": {
            "correspondence_version": (
                "flame-mediapipe-ground-truth-v1"
            ),
            "embedding_name": (
                "mediapipe_landmark_embedding"
            ),
            "input_view": "front",
            "model_family": "flame",
            "portrait_fixture": (
                "portrait_graphic_v1_ground_truth"
            ),
        },
    }

    values.update(
        overrides,
    )

    return AtlasPortraitWeakPerspectiveFittingInput(
        **values,
    )


def test_contract_preserves_landmark_count():
    fitting_input = _fitting_input()

    assert fitting_input.landmark_count == 17


def test_contract_preserves_landmark_names():
    fitting_input = _fitting_input()

    assert fitting_input.landmark_names == LANDMARK_NAMES


def test_contract_preserves_source_points():
    fitting_input = _fitting_input()

    assert fitting_input.source_points_3d.shape == (
        17,
        3,
    )

    assert fitting_input.source_points_3d.dtype == (
        np.float64
    )

    assert np.array_equal(
        fitting_input.source_points_3d,
        _source_points(),
    )


def test_contract_preserves_target_points():
    fitting_input = _fitting_input()

    assert fitting_input.target_points_2d.shape == (
        17,
        2,
    )

    assert fitting_input.target_points_2d.dtype == (
        np.float64
    )

    assert np.array_equal(
        fitting_input.target_points_2d,
        _target_points(),
    )


def test_contract_preserves_landmark_weights():
    fitting_input = _fitting_input()

    assert fitting_input.landmark_weights.shape == (
        17,
    )

    assert fitting_input.landmark_weights.dtype == (
        np.float64
    )

    assert np.array_equal(
        fitting_input.landmark_weights,
        _weights(),
    )


def test_contract_preserves_image_dimensions():
    fitting_input = _fitting_input()

    assert fitting_input.image_width == 1122
    assert fitting_input.image_height == 1402


def test_contract_arrays_are_read_only():
    fitting_input = _fitting_input()

    for array in (
        fitting_input.source_points_3d,
        fitting_input.target_points_2d,
        fitting_input.landmark_weights,
    ):
        assert array.flags.writeable is False

        with pytest.raises(
            ValueError,
        ):
            array.flat[
                0
            ] = 99.0


def test_contract_copies_input_arrays():
    source_points = _source_points()
    target_points = _target_points()
    weights = _weights()

    fitting_input = _fitting_input(
        source_points_3d=source_points,
        target_points_2d=target_points,
        landmark_weights=weights,
    )

    source_points[
        0,
        0,
    ] = 99.0

    target_points[
        0,
        0,
    ] = 99.0

    weights[
        0
    ] = 0.1

    assert fitting_input.source_points_3d[
        0,
        0,
    ] != 99.0

    assert fitting_input.target_points_2d[
        0,
        0,
    ] != 99.0

    assert fitting_input.landmark_weights[
        0
    ] != 0.1


def test_contract_metadata_is_deterministic():
    fitting_input = _fitting_input()

    assert tuple(
        fitting_input.metadata,
    ) == tuple(
        sorted(
            fitting_input.metadata,
        )
    )

    assert fitting_input.metadata == {
        "correspondence_version": (
            "flame-mediapipe-ground-truth-v1"
        ),
        "embedding_name": (
            "mediapipe_landmark_embedding"
        ),
        "input_view": "front",
        "model_family": "flame",
        "portrait_fixture": (
            "portrait_graphic_v1_ground_truth"
        ),
    }


def test_contract_serialization_is_deterministic():
    first = _fitting_input()
    second = _fitting_input()

    assert first.to_dict() == second.to_dict()


def test_contract_to_dict_contains_plain_values():
    fitting_input = _fitting_input()

    assert fitting_input.to_dict() == {
        "landmark_count": 17,
        "landmark_names": list(
            LANDMARK_NAMES
        ),
        "source_points_3d": (
            _source_points().tolist()
        ),
        "target_points_2d": (
            _target_points().tolist()
        ),
        "landmark_weights": (
            _weights().tolist()
        ),
        "image_width": 1122,
        "image_height": 1402,
        "metadata": {
            "correspondence_version": (
                "flame-mediapipe-ground-truth-v1"
            ),
            "embedding_name": (
                "mediapipe_landmark_embedding"
            ),
            "input_view": "front",
            "model_family": "flame",
            "portrait_fixture": (
                "portrait_graphic_v1_ground_truth"
            ),
        },
    }


@pytest.mark.parametrize(
    "landmark_names",
    [
        (),
        None,
        "nose_tip",
        (
            "nose_tip",
            "",
        ),
        (
            "nose_tip",
            "nose_tip",
        ),
    ],
)
def test_contract_rejects_invalid_landmark_names(
    landmark_names,
):
    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
    ):
        _fitting_input(
            landmark_names=landmark_names,
        )


@pytest.mark.parametrize(
    "source_points",
    [
        np.zeros(
            (
                17,
                2,
            ),
            dtype=np.float64,
        ),
        np.zeros(
            (
                16,
                3,
            ),
            dtype=np.float64,
        ),
        np.full(
            (
                17,
                3,
            ),
            np.nan,
            dtype=np.float64,
        ),
    ],
)
def test_contract_rejects_invalid_source_points(
    source_points,
):
    with pytest.raises(
        ValueError,
        match="source_points_3d",
    ):
        _fitting_input(
            source_points_3d=source_points,
        )


@pytest.mark.parametrize(
    "target_points",
    [
        np.zeros(
            (
                17,
                3,
            ),
            dtype=np.float64,
        ),
        np.zeros(
            (
                16,
                2,
            ),
            dtype=np.float64,
        ),
        np.full(
            (
                17,
                2,
            ),
            np.inf,
            dtype=np.float64,
        ),
    ],
)
def test_contract_rejects_invalid_target_points(
    target_points,
):
    with pytest.raises(
        ValueError,
        match="target_points_2d",
    ):
        _fitting_input(
            target_points_2d=target_points,
        )


def test_contract_rejects_target_coordinates_outside_normalized_range():
    target_points = _target_points()

    target_points[
        0,
        0,
    ] = 1.01

    with pytest.raises(
        ValueError,
        match="0.0..1.0",
    ):
        _fitting_input(
            target_points_2d=target_points,
        )


@pytest.mark.parametrize(
    "weights",
    [
        np.ones(
            16,
            dtype=np.float64,
        ),
        np.zeros(
            17,
            dtype=np.float64,
        ),
        np.full(
            17,
            np.nan,
            dtype=np.float64,
        ),
    ],
)
def test_contract_rejects_invalid_weights(
    weights,
):
    with pytest.raises(
        ValueError,
        match="landmark_weights",
    ):
        _fitting_input(
            landmark_weights=weights,
        )


@pytest.mark.parametrize(
    (
        "dimension_name",
        "dimension_value",
    ),
    [
        (
            "image_width",
            0,
        ),
        (
            "image_width",
            100.5,
        ),
        (
            "image_height",
            -1,
        ),
        (
            "image_height",
            None,
        ),
    ],
)
def test_contract_rejects_invalid_dimensions(
    dimension_name,
    dimension_value,
):
    with pytest.raises(
        ValueError,
        match=dimension_name,
    ):
        _fitting_input(
            **{
                dimension_name: dimension_value,
            }
        )


def test_contract_rejects_non_mapping_metadata():
    with pytest.raises(
        TypeError,
        match="metadata",
    ):
        _fitting_input(
            metadata=[
                "invalid",
            ],
        )
