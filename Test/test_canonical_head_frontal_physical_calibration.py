from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_canonical_head_frontal_physical_calibration import (
    AtlasCanonicalHeadFrontalPhysicalCalibration,
)


def _non_square_image_fixture():
    """
    401x201 image:
      pixel X extent = 400
      pixel Y extent = 200

    The target points describe a square 200x200-pixel object.
    In normalized-image coordinates that square becomes:
      X span = 0.5
      Y span = 1.0

    A correct square-pixel calibration must undo that normalized
    coordinate anisotropy rather than treating those spans as
    physically comparable.
    """
    source_xy = np.asarray(
        (
            (-1.0, -1.0),
            (1.0, -1.0),
            (1.0, 1.0),
            (-1.0, 1.0),
        ),
        dtype=np.float64,
    )

    target_normalized_xy = np.asarray(
        (
            (0.25, 0.0),
            (0.75, 0.0),
            (0.75, 1.0),
            (0.25, 1.0),
        ),
        dtype=np.float64,
    )

    return source_xy, target_normalized_xy


def test_derives_square_pixel_axis_scales_from_normalized_image_targets():
    source_xy, target_normalized_xy = (
        _non_square_image_fixture()
    )

    result = (
        AtlasCanonicalHeadFrontalPhysicalCalibration
        .derive(
            source_points_xy=source_xy,
            target_points_normalized=(
                target_normalized_xy
            ),
            image_width=401,
            image_height=201,
        )
    )

    # Square-pixel conversion uses one isotropic pixel denominator:
    # max(W-1, H-1) = 400.
    #
    # Target spans therefore become:
    # X: 200 / 400 = 0.5
    # Y: 200 / 400 = 0.5
    #
    # Source spans are both 2.0, so independent axis scales
    # must be equal.
    assert result.axis_scale_x == pytest.approx(
        0.25
    )
    assert result.axis_scale_y == pytest.approx(
        0.25
    )
    assert result.horizontal_scale_factor == pytest.approx(
        1.0
    )

    assert (
        result.target_coordinate_space
        == "square_pixel_isotropic"
    )


def test_horizontal_scale_factor_is_derived_from_axis_scale_ratio():
    source_xy = np.asarray(
        (
            (-1.0, -1.0),
            (1.0, -1.0),
            (1.0, 1.0),
            (-1.0, 1.0),
        ),
        dtype=np.float64,
    )

    # In square-pixel space:
    # X span = 300 px
    # Y span = 200 px
    #
    # With max image extent 400 px this becomes:
    # X span = 0.75
    # Y span = 0.50
    #
    # Independent scales:
    # X = 0.375
    # Y = 0.250
    # => required horizontal physical gain = 1.5.
    target_normalized_xy = np.asarray(
        (
            (0.125, 0.0),
            (0.875, 0.0),
            (0.875, 1.0),
            (0.125, 1.0),
        ),
        dtype=np.float64,
    )

    result = (
        AtlasCanonicalHeadFrontalPhysicalCalibration
        .derive(
            source_points_xy=source_xy,
            target_points_normalized=(
                target_normalized_xy
            ),
            image_width=401,
            image_height=201,
        )
    )

    assert result.axis_scale_x == pytest.approx(
        0.375
    )
    assert result.axis_scale_y == pytest.approx(
        0.25
    )
    assert result.horizontal_scale_factor == pytest.approx(
        1.5
    )

    assert result.horizontal_scale_factor == pytest.approx(
        result.axis_scale_x
        / result.axis_scale_y
    )


def test_calibration_does_not_mutate_input_arrays():
    source_xy, target_normalized_xy = (
        _non_square_image_fixture()
    )

    source_before = source_xy.copy()
    target_before = target_normalized_xy.copy()

    AtlasCanonicalHeadFrontalPhysicalCalibration.derive(
        source_points_xy=source_xy,
        target_points_normalized=target_normalized_xy,
        image_width=401,
        image_height=201,
    )

    np.testing.assert_array_equal(
        source_xy,
        source_before,
    )
    np.testing.assert_array_equal(
        target_normalized_xy,
        target_before,
    )


@pytest.mark.parametrize(
    ("width", "height"),
    (
        (1, 201),
        (401, 1),
        (0, 201),
        (401, 0),
    ),
)
def test_rejects_invalid_image_dimensions(
    width,
    height,
):
    source_xy, target_normalized_xy = (
        _non_square_image_fixture()
    )

    with pytest.raises(
        ValueError,
        match="image_(width|height)",
    ):
        AtlasCanonicalHeadFrontalPhysicalCalibration.derive(
            source_points_xy=source_xy,
            target_points_normalized=(
                target_normalized_xy
            ),
            image_width=width,
            image_height=height,
        )


def test_rejects_degenerate_source_axis_spread():
    source_xy = np.asarray(
        (
            (0.0, -1.0),
            (0.0, 0.0),
            (0.0, 1.0),
        ),
        dtype=np.float64,
    )

    target_normalized_xy = np.asarray(
        (
            (0.25, 0.0),
            (0.50, 0.5),
            (0.75, 1.0),
        ),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="source.*spread",
    ):
        AtlasCanonicalHeadFrontalPhysicalCalibration.derive(
            source_points_xy=source_xy,
            target_points_normalized=(
                target_normalized_xy
            ),
            image_width=401,
            image_height=201,
        )


def test_result_contains_explicit_bounded_provenance_not_likeness_claims():
    source_xy, target_normalized_xy = (
        _non_square_image_fixture()
    )

    result = (
        AtlasCanonicalHeadFrontalPhysicalCalibration
        .derive(
            source_points_xy=source_xy,
            target_points_normalized=(
                target_normalized_xy
            ),
            image_width=401,
            image_height=201,
        )
    )

    assert result.source_point_count == 4
    assert result.calibration_provenance
    assert result.calibration_kind == (
        "frontal_square_pixel_axis_scale"
    )

    # Calibration is geometric evidence only.
    assert not hasattr(result, "likeness_score")
    assert not hasattr(result, "identity_preserved")
    assert not hasattr(result, "production_ready")
    assert not hasattr(result, "phase_9_authorized")


def test_applies_horizontal_calibration_to_canonical_mesh_without_changing_y_z_or_faces():
    canonical_mesh = {
        "vertices": (
            (-2.0, -3.0, 4.0),
            (2.0, -3.0, 5.0),
            (1.0, 3.0, 6.0),
        ),
        "faces": (
            (0, 1, 2),
        ),
        "provenance": "fixture-canonical",
    }

    calibrated = (
        AtlasCanonicalHeadFrontalPhysicalCalibration
        .apply_to_canonical_mesh(
            canonical_mesh=canonical_mesh,
            horizontal_scale_factor=1.5,
            calibration_provenance="fixture-calibration",
        )
    )

    np.testing.assert_allclose(
        np.asarray(
            calibrated["vertices"],
            dtype=np.float64,
        ),
        np.asarray(
            (
                (-3.0, -3.0, 4.0),
                (3.0, -3.0, 5.0),
                (1.5, 3.0, 6.0),
            ),
            dtype=np.float64,
        ),
    )

    assert calibrated["faces"] == canonical_mesh["faces"]

    assert calibrated[
        "frontal_physical_calibration"
    ] == {
        "horizontal_scale_factor": pytest.approx(1.5),
        "axis_policy": "x_only_about_origin",
        "calibration_provenance": "fixture-calibration",
    }


def test_mesh_transform_does_not_mutate_canonical_mesh():
    canonical_mesh = {
        "vertices": (
            (-1.0, -2.0, 3.0),
            (1.0, -2.0, 4.0),
            (0.0, 2.0, 5.0),
        ),
        "faces": (
            (0, 1, 2),
        ),
        "provenance": "fixture",
    }

    original_vertices = canonical_mesh["vertices"]
    original_faces = canonical_mesh["faces"]

    AtlasCanonicalHeadFrontalPhysicalCalibration.apply_to_canonical_mesh(
        canonical_mesh=canonical_mesh,
        horizontal_scale_factor=1.25,
        calibration_provenance="fixture",
    )

    assert canonical_mesh["vertices"] == original_vertices
    assert canonical_mesh["faces"] == original_faces


def test_mesh_transform_preserves_vertex_and_face_counts():
    canonical_mesh = {
        "vertices": (
            (-1.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 2.0, 1.0),
            (0.0, 0.0, -1.0),
        ),
        "faces": (
            (0, 1, 2),
            (0, 3, 1),
            (0, 2, 3),
            (1, 3, 2),
        ),
    }

    calibrated = (
        AtlasCanonicalHeadFrontalPhysicalCalibration
        .apply_to_canonical_mesh(
            canonical_mesh=canonical_mesh,
            horizontal_scale_factor=1.2,
            calibration_provenance="fixture",
        )
    )

    assert len(calibrated["vertices"]) == 4
    assert len(calibrated["faces"]) == 4


@pytest.mark.parametrize(
    "factor",
    (
        0.0,
        -1.0,
        float("nan"),
        float("inf"),
    ),
)
def test_mesh_transform_rejects_invalid_horizontal_scale_factor(
    factor,
):
    with pytest.raises(
        ValueError,
        match="horizontal_scale_factor",
    ):
        AtlasCanonicalHeadFrontalPhysicalCalibration.apply_to_canonical_mesh(
            canonical_mesh={
                "vertices": (
                    (-1.0, 0.0, 0.0),
                    (1.0, 0.0, 0.0),
                    (0.0, 1.0, 1.0),
                ),
                "faces": (
                    (0, 1, 2),
                ),
            },
            horizontal_scale_factor=factor,
            calibration_provenance="fixture",
        )


def test_mesh_transform_requires_explicit_calibration_provenance():
    with pytest.raises(
        ValueError,
        match="calibration_provenance",
    ):
        AtlasCanonicalHeadFrontalPhysicalCalibration.apply_to_canonical_mesh(
            canonical_mesh={
                "vertices": (
                    (-1.0, 0.0, 0.0),
                    (1.0, 0.0, 0.0),
                    (0.0, 1.0, 1.0),
                ),
                "faces": (
                    (0, 1, 2),
                ),
            },
            horizontal_scale_factor=1.2,
            calibration_provenance="",
        )
