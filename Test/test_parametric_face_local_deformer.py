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


def test_increased_eye_spacing_moves_eye_regions_outward():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            eye_spacing=1.30,
        ),
    )

    eye_region = (
        (np.abs(source.x_coordinates) >= 0.20)
        & (np.abs(source.x_coordinates) <= 0.55)
        & (source.y_coordinates >= 0.05)
        & (source.y_coordinates <= 0.40)
    )

    assert np.mean(
        np.abs(
            result.x_coordinates[eye_region]
        )
    ) > np.mean(
        np.abs(
            source.x_coordinates[eye_region]
        )
    )


def test_reduced_eye_spacing_moves_eye_regions_inward():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            eye_spacing=0.75,
        ),
    )

    eye_region = (
        (np.abs(source.x_coordinates) >= 0.20)
        & (np.abs(source.x_coordinates) <= 0.55)
        & (source.y_coordinates >= 0.05)
        & (source.y_coordinates <= 0.40)
    )

    assert np.mean(
        np.abs(
            result.x_coordinates[eye_region]
        )
    ) < np.mean(
        np.abs(
            source.x_coordinates[eye_region]
        )
    )


def test_increased_eye_height_expands_eye_regions_vertically():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            eye_height=1.35,
        ),
    )

    eye_region = (
        (np.abs(source.x_coordinates) >= 0.20)
        & (np.abs(source.x_coordinates) <= 0.55)
        & (source.y_coordinates >= 0.05)
        & (source.y_coordinates <= 0.40)
    )

    eye_center_y = 0.22

    assert np.mean(
        np.abs(
            result.y_coordinates[eye_region]
            - eye_center_y
        )
    ) > np.mean(
        np.abs(
            source.y_coordinates[eye_region]
            - eye_center_y
        )
    )


def test_reduced_eye_height_compresses_eye_regions_vertically():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            eye_height=0.70,
        ),
    )

    eye_region = (
        (np.abs(source.x_coordinates) >= 0.20)
        & (np.abs(source.x_coordinates) <= 0.55)
        & (source.y_coordinates >= 0.05)
        & (source.y_coordinates <= 0.40)
    )

    eye_center_y = 0.22

    assert np.mean(
        np.abs(
            result.y_coordinates[eye_region]
            - eye_center_y
        )
    ) < np.mean(
        np.abs(
            source.y_coordinates[eye_region]
            - eye_center_y
        )
    )


def test_eye_deformation_preserves_horizontal_symmetry():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            eye_spacing=1.20,
            eye_height=1.15,
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


def test_eye_deformation_preserves_lower_face_and_far_edges():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            eye_spacing=1.30,
            eye_height=1.25,
        ),
    )

    protected_region = (
        (source.y_coordinates <= -0.20)
        | (np.abs(source.x_coordinates) >= 0.75)
    )

    assert result.x_coordinates[
        protected_region
    ] == pytest.approx(
        source.x_coordinates[
            protected_region
        ],
    )
    assert result.y_coordinates[
        protected_region
    ] == pytest.approx(
        source.y_coordinates[
            protected_region
        ],
    )
    assert result.z_coordinates[
        protected_region
    ] == pytest.approx(
        source.z_coordinates[
            protected_region
        ],
    )


def test_increased_mouth_width_expands_mouth_region():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            mouth_width=1.35,
        ),
    )

    mouth_region = (
        (np.abs(source.x_coordinates) <= 0.45)
        & (source.y_coordinates >= -0.55)
        & (source.y_coordinates <= -0.22)
    )

    assert np.mean(
        np.abs(
            result.x_coordinates[mouth_region]
        )
    ) > np.mean(
        np.abs(
            source.x_coordinates[mouth_region]
        )
    )


def test_reduced_mouth_width_compresses_mouth_region():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            mouth_width=0.70,
        ),
    )

    mouth_region = (
        (np.abs(source.x_coordinates) <= 0.45)
        & (source.y_coordinates >= -0.55)
        & (source.y_coordinates <= -0.22)
    )

    assert np.mean(
        np.abs(
            result.x_coordinates[mouth_region]
        )
    ) < np.mean(
        np.abs(
            source.x_coordinates[mouth_region]
        )
    )


def test_mouth_deformation_preserves_horizontal_symmetry():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            mouth_width=1.30,
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


def test_mouth_deformation_preserves_upper_face_chin_and_far_edges():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            mouth_width=1.35,
        ),
    )

    protected_region = (
        (source.y_coordinates >= 0.0)
        | (source.y_coordinates <= -0.72)
        | (np.abs(source.x_coordinates) >= 0.75)
    )

    assert result.x_coordinates[
        protected_region
    ] == pytest.approx(
        source.x_coordinates[
            protected_region
        ],
    )
    assert result.y_coordinates[
        protected_region
    ] == pytest.approx(
        source.y_coordinates[
            protected_region
        ],
    )
    assert result.z_coordinates[
        protected_region
    ] == pytest.approx(
        source.z_coordinates[
            protected_region
        ],
    )


def test_mouth_width_does_not_change_y_or_z_coordinates():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            mouth_width=1.25,
        ),
    )

    assert result.y_coordinates == pytest.approx(
        source.y_coordinates,
    )
    assert result.z_coordinates == pytest.approx(
        source.z_coordinates,
    )


def test_increased_jaw_width_expands_jaw_region():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            jaw_width=1.30,
        ),
    )

    jaw_region = (
        (np.abs(source.x_coordinates) >= 0.30)
        & (np.abs(source.x_coordinates) <= 0.70)
        & (source.y_coordinates >= -0.78)
        & (source.y_coordinates <= -0.30)
    )

    assert np.mean(
        np.abs(
            result.x_coordinates[jaw_region]
        )
    ) > np.mean(
        np.abs(
            source.x_coordinates[jaw_region]
        )
    )


def test_reduced_jaw_width_compresses_jaw_region():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            jaw_width=0.72,
        ),
    )

    jaw_region = (
        (np.abs(source.x_coordinates) >= 0.30)
        & (np.abs(source.x_coordinates) <= 0.70)
        & (source.y_coordinates >= -0.78)
        & (source.y_coordinates <= -0.30)
    )

    assert np.mean(
        np.abs(
            result.x_coordinates[jaw_region]
        )
    ) < np.mean(
        np.abs(
            source.x_coordinates[jaw_region]
        )
    )


def test_increased_chin_width_expands_chin_region():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            chin_width=1.35,
        ),
    )

    chin_region = (
        (np.abs(source.x_coordinates) <= 0.35)
        & (source.y_coordinates >= -0.92)
        & (source.y_coordinates <= -0.55)
    )

    assert np.mean(
        np.abs(
            result.x_coordinates[chin_region]
        )
    ) > np.mean(
        np.abs(
            source.x_coordinates[chin_region]
        )
    )


def test_reduced_chin_width_compresses_chin_region():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            chin_width=0.70,
        ),
    )

    chin_region = (
        (np.abs(source.x_coordinates) <= 0.35)
        & (source.y_coordinates >= -0.92)
        & (source.y_coordinates <= -0.55)
    )

    assert np.mean(
        np.abs(
            result.x_coordinates[chin_region]
        )
    ) < np.mean(
        np.abs(
            source.x_coordinates[chin_region]
        )
    )


def test_increased_chin_length_moves_chin_downward():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            chin_length=1.30,
        ),
    )

    chin_region = (
        (np.abs(source.x_coordinates) <= 0.32)
        & (source.y_coordinates >= -0.92)
        & (source.y_coordinates <= -0.58)
    )

    assert np.mean(
        result.y_coordinates[chin_region]
    ) < np.mean(
        source.y_coordinates[chin_region]
    )


def test_reduced_chin_length_moves_chin_upward():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            chin_length=0.72,
        ),
    )

    chin_region = (
        (np.abs(source.x_coordinates) <= 0.32)
        & (source.y_coordinates >= -0.92)
        & (source.y_coordinates <= -0.58)
    )

    assert np.mean(
        result.y_coordinates[chin_region]
    ) > np.mean(
        source.y_coordinates[chin_region]
    )


def test_jaw_and_chin_deformation_preserves_horizontal_symmetry():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            jaw_width=1.20,
            chin_width=1.25,
            chin_length=1.15,
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


def test_jaw_and_chin_deformation_preserves_upper_face_and_far_edges():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            jaw_width=1.30,
            chin_width=1.30,
            chin_length=1.25,
        ),
    )

    protected_region = (
        (source.y_coordinates >= -0.10)
        | (np.abs(source.x_coordinates) >= 0.78)
    )

    assert result.x_coordinates[
        protected_region
    ] == pytest.approx(
        source.x_coordinates[
            protected_region
        ],
    )
    assert result.y_coordinates[
        protected_region
    ] == pytest.approx(
        source.y_coordinates[
            protected_region
        ],
    )
    assert result.z_coordinates[
        protected_region
    ] == pytest.approx(
        source.z_coordinates[
            protected_region
        ],
    )


def test_jaw_and_chin_deformation_preserves_z_coordinates():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            jaw_width=1.20,
            chin_width=0.85,
            chin_length=1.25,
        ),
    )

    assert result.z_coordinates == pytest.approx(
        source.z_coordinates,
    )


def test_increased_forehead_height_moves_forehead_upward():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            forehead_height=1.30,
        ),
    )

    forehead_region = (
        (np.abs(source.x_coordinates) <= 0.55)
        & (source.y_coordinates >= 0.48)
        & (source.y_coordinates <= 0.92)
    )

    assert np.mean(
        result.y_coordinates[forehead_region]
    ) > np.mean(
        source.y_coordinates[forehead_region]
    )


def test_reduced_forehead_height_moves_forehead_downward():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            forehead_height=0.72,
        ),
    )

    forehead_region = (
        (np.abs(source.x_coordinates) <= 0.55)
        & (source.y_coordinates >= 0.48)
        & (source.y_coordinates <= 0.92)
    )

    assert np.mean(
        result.y_coordinates[forehead_region]
    ) < np.mean(
        source.y_coordinates[forehead_region]
    )


def test_forehead_deformation_preserves_horizontal_symmetry():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            forehead_height=1.25,
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


def test_forehead_deformation_preserves_lower_face_and_far_edges():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            forehead_height=1.30,
        ),
    )

    protected_region = (
        (source.y_coordinates <= 0.20)
        | (np.abs(source.x_coordinates) >= 0.78)
    )

    assert result.x_coordinates[
        protected_region
    ] == pytest.approx(
        source.x_coordinates[
            protected_region
        ],
    )
    assert result.y_coordinates[
        protected_region
    ] == pytest.approx(
        source.y_coordinates[
            protected_region
        ],
    )
    assert result.z_coordinates[
        protected_region
    ] == pytest.approx(
        source.z_coordinates[
            protected_region
        ],
    )


def test_forehead_height_does_not_change_x_or_z_coordinates():
    source = _surface()

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            forehead_height=1.25,
        ),
    )

    assert result.x_coordinates == pytest.approx(
        source.x_coordinates,
    )
    assert result.z_coordinates == pytest.approx(
        source.z_coordinates,
    )


def test_real_portrait_jaw_width_preserves_horizontal_order():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=401,
        column_count=401,
    )

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            jaw_width=1.551649849,
        ),
    )

    horizontal_steps = np.diff(
        result.x_coordinates,
        axis=1,
    )

    jaw_rows = (
        (source.y_coordinates[:, 0] >= -0.78)
        & (source.y_coordinates[:, 0] <= -0.30)
    )

    assert np.all(
        horizontal_steps[
            jaw_rows,
            :,
        ] > 0.0
    )


def test_real_portrait_jaw_width_has_no_surface_foldover():
    from CORE.atlas_parametric_face_surface_validity_analyzer import (
        AtlasParametricFaceSurfaceValidityAnalyzer,
    )

    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=401,
        column_count=401,
    )

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            jaw_width=1.551649849,
        ),
    )

    validity = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            result,
        )
    )

    assert validity.folded_cell_count == 0
    assert validity.inverted_normal_count == 0
    assert validity.minimum_signed_cell_area > 0.0
    assert validity.is_safe


def test_real_portrait_eye_spacing_preserves_horizontal_order():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=401,
        column_count=401,
    )

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            eye_spacing=1.402815658,
        ),
    )

    horizontal_steps = np.diff(
        result.x_coordinates,
        axis=1,
    )

    eye_rows = (
        (source.y_coordinates[:, 0] >= 0.05)
        & (source.y_coordinates[:, 0] <= 0.40)
    )

    assert np.all(
        horizontal_steps[
            eye_rows,
            :,
        ] > 0.0
    )


def test_real_portrait_eye_spacing_has_no_surface_foldover():
    from CORE.atlas_parametric_face_surface_validity_analyzer import (
        AtlasParametricFaceSurfaceValidityAnalyzer,
    )

    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=401,
        column_count=401,
    )

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            eye_spacing=1.402815658,
        ),
    )

    validity = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            result,
        )
    )

    assert validity.folded_cell_count == 0
    assert validity.inverted_normal_count == 0
    assert validity.minimum_signed_cell_area > 0.0
    assert validity.is_safe


def test_real_portrait_mouth_width_preserves_horizontal_order():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=401,
        column_count=401,
    )

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            mouth_width=1.537264377,
        ),
    )

    horizontal_steps = np.diff(
        result.x_coordinates,
        axis=1,
    )

    mouth_rows = (
        (source.y_coordinates[:, 0] >= -0.55)
        & (source.y_coordinates[:, 0] <= -0.22)
    )

    assert np.all(
        horizontal_steps[
            mouth_rows,
            :,
        ] > 0.0
    )


def test_real_portrait_mouth_width_has_no_surface_foldover():
    from CORE.atlas_parametric_face_surface_validity_analyzer import (
        AtlasParametricFaceSurfaceValidityAnalyzer,
    )

    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=401,
        column_count=401,
    )

    result = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=_parameters(
            mouth_width=1.537264377,
        ),
    )

    validity = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            result,
        )
    )

    assert validity.folded_cell_count == 0
    assert validity.inverted_normal_count == 0
    assert validity.minimum_signed_cell_area > 0.0
    assert validity.is_safe
