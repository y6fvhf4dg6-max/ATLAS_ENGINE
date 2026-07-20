import numpy as np
import pytest

from CORE.atlas_neutral_parametric_face_surface_builder import (
    AtlasNeutralParametricFaceSurfaceBuilder,
)
from CORE.atlas_parametric_face_depth_deformer import (
    AtlasParametricFaceDepthDeformer,
)
from CORE.atlas_parametric_face_depth_profile import (
    AtlasParametricFaceDepthProfile,
)
from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)


def _zero_profile() -> AtlasParametricFaceDepthProfile:
    return AtlasParametricFaceDepthProfile(
        name="zero-depth",
        brow_projection=0.0,
        eye_socket_depth=0.0,
        cheek_projection=0.0,
        nose_bridge_projection=0.0,
        nose_tip_projection=0.0,
        nose_wing_projection=0.0,
        upper_lip_projection=0.0,
        lower_lip_projection=0.0,
        philtrum_depth=0.0,
        labiomental_fold_depth=0.0,
        chin_projection=0.0,
    )


def test_deformer_returns_parametric_face_surface():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=9,
        column_count=11,
    )

    result = AtlasParametricFaceDepthDeformer.deform(
        source,
        depth_profile=_zero_profile(),
    )

    assert isinstance(
        result,
        AtlasParametricFaceSurface,
    )


def test_zero_profile_preserves_all_coordinates():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=9,
        column_count=11,
    )

    result = AtlasParametricFaceDepthDeformer.deform(
        source,
        depth_profile=_zero_profile(),
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


def test_deformer_preserves_xy_coordinates():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=17,
        column_count=19,
    )

    profile = AtlasParametricFaceDepthProfile(
        name="nose-tip-only",
        brow_projection=0.0,
        eye_socket_depth=0.0,
        cheek_projection=0.0,
        nose_bridge_projection=0.0,
        nose_tip_projection=0.10,
        nose_wing_projection=0.0,
        upper_lip_projection=0.0,
        lower_lip_projection=0.0,
        philtrum_depth=0.0,
        labiomental_fold_depth=0.0,
        chin_projection=0.0,
    )

    result = AtlasParametricFaceDepthDeformer.deform(
        source,
        depth_profile=profile,
    )

    assert result.x_coordinates == pytest.approx(
        source.x_coordinates,
    )
    assert result.y_coordinates == pytest.approx(
        source.y_coordinates,
    )


def test_deformer_does_not_mutate_source_surface():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=9,
        column_count=11,
    )

    original_x = source.x_coordinates.copy()
    original_y = source.y_coordinates.copy()
    original_z = source.z_coordinates.copy()

    AtlasParametricFaceDepthDeformer.deform(
        source,
        depth_profile=_zero_profile(),
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


def test_deformer_returns_new_surface_instance():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=9,
        column_count=11,
    )

    result = AtlasParametricFaceDepthDeformer.deform(
        source,
        depth_profile=_zero_profile(),
    )

    assert result is not source
    assert result.x_coordinates is not source.x_coordinates
    assert result.y_coordinates is not source.y_coordinates
    assert result.z_coordinates is not source.z_coordinates


def test_deformer_is_deterministic():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=13,
        column_count=15,
    )
    profile = _zero_profile()

    first = AtlasParametricFaceDepthDeformer.deform(
        source,
        depth_profile=profile,
    )
    second = AtlasParametricFaceDepthDeformer.deform(
        source,
        depth_profile=profile,
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


def test_deformer_rejects_invalid_surface():
    with pytest.raises(
        TypeError,
        match="surface must be an AtlasParametricFaceSurface",
    ):
        AtlasParametricFaceDepthDeformer.deform(
            np.zeros(
                (
                    3,
                    3,
                ),
                dtype=np.float64,
            ),
            depth_profile=_zero_profile(),
        )


def test_deformer_rejects_invalid_depth_profile():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=9,
        column_count=11,
    )

    with pytest.raises(
        TypeError,
        match=(
            "depth_profile must be an "
            "AtlasParametricFaceDepthProfile"
        ),
    ):
        AtlasParametricFaceDepthDeformer.deform(
            source,
            depth_profile=None,
        )


def _nose_tip_profile(
    projection: float,
) -> AtlasParametricFaceDepthProfile:
    return AtlasParametricFaceDepthProfile(
        name="nose-tip-test",
        brow_projection=0.0,
        eye_socket_depth=0.0,
        cheek_projection=0.0,
        nose_bridge_projection=0.0,
        nose_tip_projection=projection,
        nose_wing_projection=0.0,
        upper_lip_projection=0.0,
        lower_lip_projection=0.0,
        philtrum_depth=0.0,
        labiomental_fold_depth=0.0,
        chin_projection=0.0,
    )


def test_nose_tip_projection_increases_depth_at_nose_tip_center():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=101,
        column_count=101,
    )

    result = AtlasParametricFaceDepthDeformer.deform(
        source,
        depth_profile=_nose_tip_profile(
            0.10,
        ),
    )

    center_row = int(
        np.argmin(
            np.abs(
                source.y_coordinates[:, 0]
                - (-0.12)
            )
        )
    )
    center_column = int(
        np.argmin(
            np.abs(
                source.x_coordinates[0, :]
            )
        )
    )

    assert (
        result.z_coordinates[
            center_row,
            center_column,
        ]
        - source.z_coordinates[
            center_row,
            center_column,
        ]
    ) == pytest.approx(
        0.10,
        abs=1.0e-12,
    )


def test_nose_tip_projection_is_horizontally_symmetric():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=101,
        column_count=101,
    )

    result = AtlasParametricFaceDepthDeformer.deform(
        source,
        depth_profile=_nose_tip_profile(
            0.10,
        ),
    )

    depth_delta = (
        result.z_coordinates
        - source.z_coordinates
    )

    assert depth_delta == pytest.approx(
        np.fliplr(
            depth_delta,
        ),
    )


def test_nose_tip_projection_has_compact_local_support():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=101,
        column_count=101,
    )

    result = AtlasParametricFaceDepthDeformer.deform(
        source,
        depth_profile=_nose_tip_profile(
            0.10,
        ),
    )

    far_region = (
        (
            np.abs(
                source.x_coordinates,
            )
            >= 0.30
        )
        |
        (
            np.abs(
                source.y_coordinates
                - (-0.12)
            )
            >= 0.32
        )
    )

    assert result.z_coordinates[
        far_region
    ] == pytest.approx(
        source.z_coordinates[
            far_region
        ],
    )


def test_larger_nose_tip_projection_produces_larger_center_depth():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=101,
        column_count=101,
    )

    smaller = AtlasParametricFaceDepthDeformer.deform(
        source,
        depth_profile=_nose_tip_profile(
            0.05,
        ),
    )
    larger = AtlasParametricFaceDepthDeformer.deform(
        source,
        depth_profile=_nose_tip_profile(
            0.12,
        ),
    )

    center_row = int(
        np.argmin(
            np.abs(
                source.y_coordinates[:, 0]
                - (-0.12)
            )
        )
    )
    center_column = int(
        np.argmin(
            np.abs(
                source.x_coordinates[0, :]
            )
        )
    )

    smaller_delta = (
        smaller.z_coordinates[
            center_row,
            center_column,
        ]
        - source.z_coordinates[
            center_row,
            center_column,
        ]
    )
    larger_delta = (
        larger.z_coordinates[
            center_row,
            center_column,
        ]
        - source.z_coordinates[
            center_row,
            center_column,
        ]
    )

    assert larger_delta > smaller_delta
    assert smaller_delta == pytest.approx(
        0.05,
        abs=1.0e-12,
    )
    assert larger_delta == pytest.approx(
        0.12,
        abs=1.0e-12,
    )


def test_nose_tip_projection_changes_only_z_coordinates():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=101,
        column_count=101,
    )

    result = AtlasParametricFaceDepthDeformer.deform(
        source,
        depth_profile=_nose_tip_profile(
            0.10,
        ),
    )

    assert result.x_coordinates == pytest.approx(
        source.x_coordinates,
    )
    assert result.y_coordinates == pytest.approx(
        source.y_coordinates,
    )
    assert not np.allclose(
        result.z_coordinates,
        source.z_coordinates,
    )


def _nose_bridge_profile(
    projection: float,
) -> AtlasParametricFaceDepthProfile:
    return AtlasParametricFaceDepthProfile(
        name="nose-bridge-test",
        brow_projection=0.0,
        eye_socket_depth=0.0,
        cheek_projection=0.0,
        nose_bridge_projection=projection,
        nose_tip_projection=0.0,
        nose_wing_projection=0.0,
        upper_lip_projection=0.0,
        lower_lip_projection=0.0,
        philtrum_depth=0.0,
        labiomental_fold_depth=0.0,
        chin_projection=0.0,
    )


def test_nose_bridge_projection_increases_depth_at_bridge_center():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=101,
        column_count=101,
    )

    result = AtlasParametricFaceDepthDeformer.deform(
        source,
        depth_profile=_nose_bridge_profile(
            0.08,
        ),
    )

    center_row = int(
        np.argmin(
            np.abs(
                source.y_coordinates[:, 0]
                - 0.08
            )
        )
    )
    center_column = int(
        np.argmin(
            np.abs(
                source.x_coordinates[0, :]
            )
        )
    )

    assert (
        result.z_coordinates[
            center_row,
            center_column,
        ]
        - source.z_coordinates[
            center_row,
            center_column,
        ]
    ) == pytest.approx(
        0.08,
        abs=1.0e-12,
    )


def test_nose_bridge_projection_is_horizontally_symmetric():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=101,
        column_count=101,
    )

    result = AtlasParametricFaceDepthDeformer.deform(
        source,
        depth_profile=_nose_bridge_profile(
            0.08,
        ),
    )

    depth_delta = (
        result.z_coordinates
        - source.z_coordinates
    )

    assert depth_delta == pytest.approx(
        np.fliplr(
            depth_delta,
        ),
    )


def test_nose_bridge_projection_has_compact_local_support():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=101,
        column_count=101,
    )

    result = AtlasParametricFaceDepthDeformer.deform(
        source,
        depth_profile=_nose_bridge_profile(
            0.08,
        ),
    )

    far_region = (
        (
            np.abs(
                source.x_coordinates,
            )
            >= 0.22
        )
        |
        (
            np.abs(
                source.y_coordinates
                - 0.08
            )
            >= 0.55
        )
    )

    assert result.z_coordinates[
        far_region
    ] == pytest.approx(
        source.z_coordinates[
            far_region
        ],
    )


def test_larger_nose_bridge_projection_produces_larger_center_depth():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=101,
        column_count=101,
    )

    smaller = AtlasParametricFaceDepthDeformer.deform(
        source,
        depth_profile=_nose_bridge_profile(
            0.04,
        ),
    )
    larger = AtlasParametricFaceDepthDeformer.deform(
        source,
        depth_profile=_nose_bridge_profile(
            0.10,
        ),
    )

    center_row = int(
        np.argmin(
            np.abs(
                source.y_coordinates[:, 0]
                - 0.08
            )
        )
    )
    center_column = int(
        np.argmin(
            np.abs(
                source.x_coordinates[0, :]
            )
        )
    )

    smaller_delta = (
        smaller.z_coordinates[
            center_row,
            center_column,
        ]
        - source.z_coordinates[
            center_row,
            center_column,
        ]
    )
    larger_delta = (
        larger.z_coordinates[
            center_row,
            center_column,
        ]
        - source.z_coordinates[
            center_row,
            center_column,
        ]
    )

    assert smaller_delta == pytest.approx(
        0.04,
        abs=1.0e-12,
    )
    assert larger_delta == pytest.approx(
        0.10,
        abs=1.0e-12,
    )
    assert larger_delta > smaller_delta


def test_nose_bridge_projection_changes_only_z_coordinates():
    source = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=101,
        column_count=101,
    )

    result = AtlasParametricFaceDepthDeformer.deform(
        source,
        depth_profile=_nose_bridge_profile(
            0.08,
        ),
    )

    assert result.x_coordinates == pytest.approx(
        source.x_coordinates,
    )
    assert result.y_coordinates == pytest.approx(
        source.y_coordinates,
    )
    assert not np.allclose(
        result.z_coordinates,
        source.z_coordinates,
    )
