from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.atlas_neutral_parametric_face_surface_builder import (
    AtlasNeutralParametricFaceSurfaceBuilder,
)
from CORE.atlas_parametric_face_parameters import (
    AtlasParametricFaceParameters,
)
from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)
from CORE.atlas_parametric_face_surface_comparison_result import (
    AtlasParametricFaceSurfaceComparisonResult,
)


def _surface(
    *,
    row_count: int = 11,
    column_count: int = 13,
) -> AtlasParametricFaceSurface:
    return AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=row_count,
        column_count=column_count,
    )


def _parameters() -> AtlasParametricFaceParameters:
    return AtlasParametricFaceParameters(
        scale=1.0,
        translation_x=0.0,
        translation_y=0.0,
        rotation_degrees=0.0,
        face_width=1.0,
        face_height=1.0,
        eye_spacing=1.0,
        eye_height=1.0,
        nose_width=1.0,
        nose_length=1.0,
        mouth_width=1.0,
        chin_width=1.0,
        chin_length=1.0,
        jaw_width=1.0,
        forehead_height=1.0,
    )


def _adapted_surface(
    source: AtlasParametricFaceSurface,
) -> AtlasParametricFaceSurface:
    return AtlasParametricFaceSurface(
        x_coordinates=(
            source.x_coordinates
            + 0.10
        ),
        y_coordinates=(
            source.y_coordinates
            - 0.05
        ),
        z_coordinates=(
            source.z_coordinates
            * 1.20
        ),
    )


def test_result_stores_surfaces_and_parameters():
    neutral = _surface()
    adapted = _adapted_surface(
        neutral,
    )
    parameters = _parameters()

    result = AtlasParametricFaceSurfaceComparisonResult(
        neutral_surface=neutral,
        adapted_surface=adapted,
        parameters=parameters,
    )

    assert result.neutral_surface is neutral
    assert result.adapted_surface is adapted
    assert result.parameters is parameters


def test_result_is_immutable():
    neutral = _surface()

    result = AtlasParametricFaceSurfaceComparisonResult(
        neutral_surface=neutral,
        adapted_surface=_adapted_surface(
            neutral,
        ),
        parameters=_parameters(),
    )

    with pytest.raises(
        FrozenInstanceError,
    ):
        result.parameters = _parameters()


def test_result_exposes_coordinate_delta_arrays():
    neutral = _surface()
    adapted = _adapted_surface(
        neutral,
    )

    result = AtlasParametricFaceSurfaceComparisonResult(
        neutral_surface=neutral,
        adapted_surface=adapted,
        parameters=_parameters(),
    )

    assert result.x_deltas == pytest.approx(
        adapted.x_coordinates
        - neutral.x_coordinates,
    )
    assert result.y_deltas == pytest.approx(
        adapted.y_coordinates
        - neutral.y_coordinates,
    )
    assert result.z_deltas == pytest.approx(
        adapted.z_coordinates
        - neutral.z_coordinates,
    )


def test_coordinate_delta_arrays_are_float64_and_read_only():
    neutral = _surface()

    result = AtlasParametricFaceSurfaceComparisonResult(
        neutral_surface=neutral,
        adapted_surface=_adapted_surface(
            neutral,
        ),
        parameters=_parameters(),
    )

    for values in (
        result.x_deltas,
        result.y_deltas,
        result.z_deltas,
    ):
        assert values.dtype == np.float64
        assert not values.flags.writeable


def test_result_reports_maximum_absolute_coordinate_deltas():
    neutral = _surface()
    adapted = _adapted_surface(
        neutral,
    )

    result = AtlasParametricFaceSurfaceComparisonResult(
        neutral_surface=neutral,
        adapted_surface=adapted,
        parameters=_parameters(),
    )

    assert result.maximum_absolute_x_delta == pytest.approx(
        0.10,
    )
    assert result.maximum_absolute_y_delta == pytest.approx(
        0.05,
    )
    assert result.maximum_absolute_z_delta == pytest.approx(
        np.max(
            np.abs(
                adapted.z_coordinates
                - neutral.z_coordinates
            )
        ),
    )


def test_result_reports_coordinate_change():
    neutral = _surface()

    changed = AtlasParametricFaceSurfaceComparisonResult(
        neutral_surface=neutral,
        adapted_surface=_adapted_surface(
            neutral,
        ),
        parameters=_parameters(),
    )

    unchanged = AtlasParametricFaceSurfaceComparisonResult(
        neutral_surface=neutral,
        adapted_surface=neutral,
        parameters=_parameters(),
    )

    assert changed.has_coordinate_change
    assert not unchanged.has_coordinate_change


def test_result_rejects_wrong_neutral_surface_type():
    with pytest.raises(
        TypeError,
        match="neutral_surface",
    ):
        AtlasParametricFaceSurfaceComparisonResult(
            neutral_surface=object(),
            adapted_surface=_surface(),
            parameters=_parameters(),
        )


def test_result_rejects_wrong_adapted_surface_type():
    with pytest.raises(
        TypeError,
        match="adapted_surface",
    ):
        AtlasParametricFaceSurfaceComparisonResult(
            neutral_surface=_surface(),
            adapted_surface=object(),
            parameters=_parameters(),
        )


def test_result_rejects_wrong_parameters_type():
    neutral = _surface()

    with pytest.raises(
        TypeError,
        match="parameters",
    ):
        AtlasParametricFaceSurfaceComparisonResult(
            neutral_surface=neutral,
            adapted_surface=neutral,
            parameters=object(),
        )


def test_result_rejects_surface_shape_mismatch():
    with pytest.raises(
        ValueError,
        match="same shape",
    ):
        AtlasParametricFaceSurfaceComparisonResult(
            neutral_surface=_surface(
                row_count=11,
                column_count=13,
            ),
            adapted_surface=_surface(
                row_count=9,
                column_count=13,
            ),
            parameters=_parameters(),
        )


def test_result_does_not_modify_source_surfaces():
    neutral = _surface()
    adapted = _adapted_surface(
        neutral,
    )

    neutral_x = neutral.x_coordinates.copy()
    neutral_y = neutral.y_coordinates.copy()
    neutral_z = neutral.z_coordinates.copy()

    adapted_x = adapted.x_coordinates.copy()
    adapted_y = adapted.y_coordinates.copy()
    adapted_z = adapted.z_coordinates.copy()

    AtlasParametricFaceSurfaceComparisonResult(
        neutral_surface=neutral,
        adapted_surface=adapted,
        parameters=_parameters(),
    )

    assert neutral.x_coordinates == pytest.approx(
        neutral_x,
    )
    assert neutral.y_coordinates == pytest.approx(
        neutral_y,
    )
    assert neutral.z_coordinates == pytest.approx(
        neutral_z,
    )

    assert adapted.x_coordinates == pytest.approx(
        adapted_x,
    )
    assert adapted.y_coordinates == pytest.approx(
        adapted_y,
    )
    assert adapted.z_coordinates == pytest.approx(
        adapted_z,
    )
