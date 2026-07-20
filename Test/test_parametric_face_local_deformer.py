import numpy as np
import pytest

from CORE.atlas_neutral_parametric_face_surface_builder import (
    AtlasNeutralParametricFaceSurfaceBuilder,
)
from CORE.atlas_parametric_face_local_deformer import (
    AtlasParametricFaceLocalDeformer,
)
from CORE.atlas_parametric_face_parameters import (
    AtlasParametricFaceParameters,
)
from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)


def _surface() -> AtlasParametricFaceSurface:
    return AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=41,
        column_count=41,
    )


def _parameters(
    **overrides,
) -> AtlasParametricFaceParameters:
    values = {
        "scale": 1.0,
        "translation_x": 0.0,
        "translation_y": 0.0,
        "rotation_degrees": 0.0,
        "face_width": 1.0,
        "face_height": 1.0,
        "eye_spacing": 1.0,
        "eye_height": 1.0,
        "nose_width": 1.0,
        "nose_length": 1.0,
        "mouth_width": 1.0,
        "chin_width": 1.0,
        "chin_length": 1.0,
        "jaw_width": 1.0,
        "forehead_height": 1.0,
    }

    values.update(
        overrides,
    )

    return AtlasParametricFaceParameters(
        **values,
    )


def test_local_deformer_returns_parametric_face_surface():
    result = AtlasParametricFaceLocalDeformer.deform(
        _surface(),
        parameters=_parameters(),
    )

    assert isinstance(
        result,
        AtlasParametricFaceSurface,
    )


def test_identity_parameters_preserve_surface():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(),
    )

    assert result.x_coordinates == pytest.approx(
        source.x_coordinates,
    )
    assert result.y_coordinates == pytest.approx(
        source.y_coordinates,
    )
    assert result.z_coordinates == pytest.approx(
        source.z_coordinates,
    )


def test_wider_nose_increases_horizontal_nose_extent():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            nose_width=1.40,
        ),
    )

    nose_region = (
        (np.abs(source.x_coordinates) <= 0.30)
        & (source.y_coordinates >= -0.35)
        & (source.y_coordinates <= 0.45)
    )

    assert np.max(
        np.abs(
            result.x_coordinates[nose_region]
        )
    ) > np.max(
        np.abs(
            source.x_coordinates[nose_region]
        )
    )


def test_narrower_nose_reduces_horizontal_nose_extent():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            nose_width=0.70,
        ),
    )

    nose_region = (
        (np.abs(source.x_coordinates) <= 0.30)
        & (source.y_coordinates >= -0.35)
        & (source.y_coordinates <= 0.45)
    )

    assert np.max(
        np.abs(
            result.x_coordinates[nose_region]
        )
    ) < np.max(
        np.abs(
            source.x_coordinates[nose_region]
        )
    )


def test_longer_nose_increases_vertical_nose_extent():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            nose_length=1.35,
        ),
    )

    nose_region = (
        (np.abs(source.x_coordinates) <= 0.22)
        & (source.y_coordinates >= -0.35)
        & (source.y_coordinates <= 0.45)
    )

    source_extent = (
        source.y_coordinates[nose_region].max()
        - source.y_coordinates[nose_region].min()
    )
    result_extent = (
        result.y_coordinates[nose_region].max()
        - result.y_coordinates[nose_region].min()
    )

    assert result_extent > source_extent


def test_shorter_nose_reduces_vertical_nose_extent():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            nose_length=0.75,
        ),
    )

    nose_region = (
        (np.abs(source.x_coordinates) <= 0.22)
        & (source.y_coordinates >= -0.35)
        & (source.y_coordinates <= 0.45)
    )

    source_extent = (
        source.y_coordinates[nose_region].max()
        - source.y_coordinates[nose_region].min()
    )
    result_extent = (
        result.y_coordinates[nose_region].max()
        - result.y_coordinates[nose_region].min()
    )

    assert result_extent < source_extent


def test_nose_deformation_preserves_horizontal_symmetry():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            nose_width=1.30,
            nose_length=1.20,
        ),
    )

    assert result.x_coordinates == pytest.approx(
        -np.fliplr(
            result.x_coordinates,
        ),
        abs=1e-12,
    )
    assert result.y_coordinates == pytest.approx(
        np.fliplr(
            result.y_coordinates,
        ),
        abs=1e-12,
    )
    assert result.z_coordinates == pytest.approx(
        np.fliplr(
            result.z_coordinates,
        ),
        abs=1e-12,
    )


def test_far_face_edges_remain_unchanged():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            nose_width=1.40,
            nose_length=1.35,
        ),
    )

    far_region = np.abs(
        source.x_coordinates,
    ) >= 0.70

    assert result.x_coordinates[far_region] == pytest.approx(
        source.x_coordinates[far_region],
    )
    assert result.y_coordinates[far_region] == pytest.approx(
        source.y_coordinates[far_region],
    )
    assert result.z_coordinates[far_region] == pytest.approx(
        source.z_coordinates[far_region],
    )


def test_local_deformer_does_not_modify_source():
    source = _surface()

    original_x = source.x_coordinates.copy()
    original_y = source.y_coordinates.copy()
    original_z = source.z_coordinates.copy()

    AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            nose_width=1.20,
            nose_length=0.85,
        ),
    )

    assert source.x_coordinates == pytest.approx(
        original_x,
    )
    assert source.y_coordinates == pytest.approx(
        original_y,
    )
    assert source.z_coordinates == pytest.approx(
        original_z,
    )


def test_local_deformer_is_deterministic():
    source = _surface()
    parameters = _parameters(
        nose_width=1.15,
        nose_length=1.10,
    )

    first = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=parameters,
    )
    second = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=parameters,
    )

    assert first.x_coordinates == pytest.approx(
        second.x_coordinates,
    )
    assert first.y_coordinates == pytest.approx(
        second.y_coordinates,
    )
    assert first.z_coordinates == pytest.approx(
        second.z_coordinates,
    )


def test_local_deformer_rejects_wrong_surface_type():
    with pytest.raises(
        TypeError,
        match="AtlasParametricFaceSurface",
    ):
        AtlasParametricFaceLocalDeformer.deform(
            object(),
            parameters=_parameters(),
        )


def test_local_deformer_rejects_wrong_parameters_type():
    with pytest.raises(
        TypeError,
        match="AtlasParametricFaceParameters",
    ):
        AtlasParametricFaceLocalDeformer.deform(
            _surface(),
            parameters=object(),
        )
