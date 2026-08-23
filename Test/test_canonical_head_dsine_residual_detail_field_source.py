import numpy as np
import pytest

from CORE.atlas_canonical_head_dsine_residual_detail_field_source import (
    AtlasCanonicalHeadDsineResidualDetailFieldSource,
)


def _normalize(normals):
    lengths = np.linalg.norm(
        normals,
        axis=2,
        keepdims=True,
    )
    return normals / np.maximum(
        lengths,
        1e-12,
    )


def _synthetic_normals():
    rows = 21
    columns = 25

    y, x = np.mgrid[
        -1.0:1.0:complex(rows),
        -1.0:1.0:complex(columns),
    ]

    broad_height = (
        0.20 * x
        + 0.10 * y
    )

    detail_height = (
        0.03
        * np.sin(
            6.0 * np.pi * x
        )
        * np.cos(
            4.0 * np.pi * y
        )
    )

    height = (
        broad_height
        + detail_height
    )

    dz_dy, dz_dx = np.gradient(
        height
    )

    normals = np.stack(
        (
            -dz_dx,
            -dz_dy,
            np.ones_like(
                height
            ),
        ),
        axis=2,
    )

    return _normalize(
        normals
    )


def test_builds_residual_scalar_and_confidence_fields():
    confidence = np.full(
        (21, 25),
        0.75,
        dtype=np.float64,
    )

    result = (
        AtlasCanonicalHeadDsineResidualDetailFieldSource
        .build(
            normals=_synthetic_normals(),
            confidence_field=confidence,
            structure_radius=3,
        )
    )

    assert result.scalar_detail_field.shape == (
        21,
        25,
    )
    assert result.confidence_field.shape == (
        21,
        25,
    )

    assert result.scalar_detail_field.dtype == np.float64
    assert result.confidence_field.dtype == np.float64

    assert np.all(
        np.isfinite(
            result.scalar_detail_field
        )
    )
    assert np.all(
        np.isfinite(
            result.confidence_field
        )
    )


def test_preserves_explicit_confidence_without_applying_it():
    confidence = np.linspace(
        0.0,
        1.0,
        21 * 25,
        dtype=np.float64,
    ).reshape(
        21,
        25,
    )

    result = (
        AtlasCanonicalHeadDsineResidualDetailFieldSource
        .build(
            normals=_synthetic_normals(),
            confidence_field=confidence,
            structure_radius=3,
        )
    )

    assert np.array_equal(
        result.confidence_field,
        confidence,
    )

    assert not hasattr(
        result,
        "weighted_scalar_detail_field",
    )


def test_scalar_field_is_independent_of_confidence_values():
    normals = _synthetic_normals()

    full = (
        AtlasCanonicalHeadDsineResidualDetailFieldSource
        .build(
            normals=normals,
            confidence_field=np.ones(
                normals.shape[:2],
                dtype=np.float64,
            ),
            structure_radius=3,
        )
    )

    zero = (
        AtlasCanonicalHeadDsineResidualDetailFieldSource
        .build(
            normals=normals,
            confidence_field=np.zeros(
                normals.shape[:2],
                dtype=np.float64,
            ),
            structure_radius=3,
        )
    )

    assert np.allclose(
        full.scalar_detail_field,
        zero.scalar_detail_field,
        atol=1e-12,
    )


def test_flat_normals_produce_flat_residual_scalar_field():
    normals = np.zeros(
        (12, 16, 3),
        dtype=np.float64,
    )
    normals[..., 2] = 1.0

    result = (
        AtlasCanonicalHeadDsineResidualDetailFieldSource
        .build(
            normals=normals,
            confidence_field=np.ones(
                (12, 16),
                dtype=np.float64,
            ),
            structure_radius=3,
        )
    )

    assert np.ptp(
        result.scalar_detail_field
    ) == pytest.approx(
        0.0,
        abs=1e-10,
    )


def test_residual_scalar_field_is_zero_centered():
    result = (
        AtlasCanonicalHeadDsineResidualDetailFieldSource
        .build(
            normals=_synthetic_normals(),
            confidence_field=np.ones(
                (21, 25),
                dtype=np.float64,
            ),
            structure_radius=3,
        )
    )

    assert float(
        np.mean(
            result.scalar_detail_field
        )
    ) == pytest.approx(
        0.0,
        abs=1e-10,
    )


def test_result_arrays_are_immutable_snapshots():
    normals = _synthetic_normals()

    confidence = np.full(
        normals.shape[:2],
        0.5,
        dtype=np.float64,
    )

    result = (
        AtlasCanonicalHeadDsineResidualDetailFieldSource
        .build(
            normals=normals,
            confidence_field=confidence,
            structure_radius=3,
        )
    )

    confidence[:] = 1.0

    assert result.scalar_detail_field.flags.writeable is False
    assert result.confidence_field.flags.writeable is False

    assert np.allclose(
        result.confidence_field,
        0.5,
    )

    with pytest.raises(ValueError):
        result.scalar_detail_field[0, 0] = 1.0


def test_rejects_invalid_normal_shape():
    with pytest.raises(
        ValueError,
        match="normals",
    ):
        AtlasCanonicalHeadDsineResidualDetailFieldSource.build(
            normals=np.zeros(
                (12, 16),
                dtype=np.float64,
            ),
            confidence_field=np.ones(
                (12, 16),
                dtype=np.float64,
            ),
            structure_radius=3,
        )


def test_rejects_confidence_shape_mismatch():
    with pytest.raises(
        ValueError,
        match="confidence_field",
    ):
        AtlasCanonicalHeadDsineResidualDetailFieldSource.build(
            normals=_synthetic_normals(),
            confidence_field=np.ones(
                (20, 25),
                dtype=np.float64,
            ),
            structure_radius=3,
        )


@pytest.mark.parametrize(
    "invalid_value",
    (
        -0.1,
        1.1,
        np.nan,
        np.inf,
    ),
)
def test_rejects_invalid_confidence_values(
    invalid_value,
):
    confidence = np.ones(
        (21, 25),
        dtype=np.float64,
    )
    confidence[0, 0] = invalid_value

    with pytest.raises(
        ValueError,
        match="confidence_field",
    ):
        AtlasCanonicalHeadDsineResidualDetailFieldSource.build(
            normals=_synthetic_normals(),
            confidence_field=confidence,
            structure_radius=3,
        )


def test_source_does_not_claim_identity_geometry_or_downstream_policy():
    result = (
        AtlasCanonicalHeadDsineResidualDetailFieldSource
        .build(
            normals=_synthetic_normals(),
            confidence_field=np.ones(
                (21, 25),
                dtype=np.float64,
            ),
            structure_radius=3,
        )
    )

    assert not hasattr(result, "identity_shape")
    assert not hasattr(result, "canonical_geometry")
    assert not hasattr(result, "camera")
    assert not hasattr(result, "pose")
    assert not hasattr(result, "visibility")
    assert not hasattr(result, "correspondence")
    assert not hasattr(result, "bounded_amplitude")
    assert not hasattr(result, "displacement")
    assert not hasattr(result, "phase_9_authorized")


def test_explicit_face_support_mask_limits_residual_field():
    normals = _synthetic_normals()

    confidence = np.ones(
        normals.shape[:2],
        dtype=np.float64,
    )

    mask = np.zeros(
        normals.shape[:2],
        dtype=np.float64,
    )
    mask[4:17, 5:20] = 1.0

    result = (
        AtlasCanonicalHeadDsineResidualDetailFieldSource
        .build(
            normals=normals,
            confidence_field=confidence,
            mask=mask,
            structure_radius=3,
        )
    )

    outside = mask <= 0.0
    inside = mask > 0.0

    assert np.allclose(
        result.scalar_detail_field[outside],
        0.0,
        atol=1e-12,
    )

    assert np.ptp(
        result.scalar_detail_field[inside]
    ) > 0.0


def test_mask_does_not_modify_explicit_confidence_channel():
    normals = _synthetic_normals()

    confidence = np.linspace(
        0.0,
        1.0,
        normals.shape[0] * normals.shape[1],
        dtype=np.float64,
    ).reshape(
        normals.shape[:2]
    )

    mask = np.zeros(
        normals.shape[:2],
        dtype=np.float64,
    )
    mask[4:17, 5:20] = 1.0

    result = (
        AtlasCanonicalHeadDsineResidualDetailFieldSource
        .build(
            normals=normals,
            confidence_field=confidence,
            mask=mask,
            structure_radius=3,
        )
    )

    assert np.array_equal(
        result.confidence_field,
        confidence,
    )


def test_rejects_mask_shape_mismatch():
    with pytest.raises(
        ValueError,
        match="mask",
    ):
        AtlasCanonicalHeadDsineResidualDetailFieldSource.build(
            normals=_synthetic_normals(),
            confidence_field=np.ones(
                (21, 25),
                dtype=np.float64,
            ),
            mask=np.ones(
                (20, 25),
                dtype=np.float64,
            ),
            structure_radius=3,
        )


def test_rejects_nonfinite_mask():
    mask = np.ones(
        (21, 25),
        dtype=np.float64,
    )
    mask[0, 0] = np.nan

    with pytest.raises(
        ValueError,
        match="mask",
    ):
        AtlasCanonicalHeadDsineResidualDetailFieldSource.build(
            normals=_synthetic_normals(),
            confidence_field=np.ones(
                (21, 25),
                dtype=np.float64,
            ),
            mask=mask,
            structure_radius=3,
        )
