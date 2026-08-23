import numpy as np
import pytest

from CORE.atlas_canonical_head_geometry import (
    AtlasCanonicalHeadGeometry,
)
from CORE.atlas_canonical_head_normal_residual_detail_projector import (
    AtlasCanonicalHeadNormalResidualDetailProjector,
)
from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)


def _geometry():
    topology = AtlasCanonicalHeadTopology(
        topology_id="fixture-head",
        vertex_count=4,
        faces=(
            (0, 1, 2),
            (0, 2, 3),
        ),
        semantic_vertex_regions={
            "face": (0, 1, 2, 3),
            "nose": (0, 2),
            "left_eye": (0, 1),
            "right_eye": (2, 3),
        },
    )

    return AtlasCanonicalHeadGeometry(
        topology=topology,
        vertices=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [1.0, 1.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=np.float64,
        ),
    )


def test_projects_scalar_amplitudes_along_canonical_vertex_normals():
    geometry = _geometry()

    amplitudes = np.array(
        [
            0.01,
            -0.02,
            0.03,
            0.00,
        ],
        dtype=np.float64,
    )

    displacement = (
        AtlasCanonicalHeadNormalResidualDetailProjector
        .project(
            geometry,
            amplitudes=amplitudes,
        )
    )

    assert displacement.shape == (4, 3)
    assert displacement.dtype == np.float64

    assert np.allclose(
        displacement[:, 0],
        0.0,
        atol=1e-12,
    )
    assert np.allclose(
        displacement[:, 1],
        0.0,
        atol=1e-12,
    )
    assert np.allclose(
        displacement[:, 2],
        amplitudes,
        atol=1e-12,
    )


def test_zero_amplitudes_produce_zero_displacement():
    displacement = (
        AtlasCanonicalHeadNormalResidualDetailProjector
        .project(
            _geometry(),
            amplitudes=np.zeros(
                4,
                dtype=np.float64,
            ),
        )
    )

    assert np.count_nonzero(
        displacement
    ) == 0


def test_returns_immutable_snapshot():
    displacement = (
        AtlasCanonicalHeadNormalResidualDetailProjector
        .project(
            _geometry(),
            amplitudes=np.ones(
                4,
                dtype=np.float64,
            ),
        )
    )

    assert displacement.flags.writeable is False

    with pytest.raises(ValueError):
        displacement[0, 0] = 1.0


def test_rejects_noncanonical_geometry():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadGeometry",
    ):
        AtlasCanonicalHeadNormalResidualDetailProjector.project(
            {},
            amplitudes=np.zeros(
                4,
                dtype=np.float64,
            ),
        )


@pytest.mark.parametrize(
    "amplitudes",
    (
        np.zeros((4, 1), dtype=np.float64),
        np.zeros(3, dtype=np.float64),
    ),
)
def test_rejects_wrong_amplitude_shape(
    amplitudes,
):
    with pytest.raises(
        ValueError,
        match="amplitudes.*shape",
    ):
        AtlasCanonicalHeadNormalResidualDetailProjector.project(
            _geometry(),
            amplitudes=amplitudes,
        )


def test_rejects_nonfinite_amplitudes():
    amplitudes = np.zeros(
        4,
        dtype=np.float64,
    )
    amplitudes[1] = np.nan

    with pytest.raises(
        ValueError,
        match="finite",
    ):
        AtlasCanonicalHeadNormalResidualDetailProjector.project(
            _geometry(),
            amplitudes=amplitudes,
        )


def test_projector_does_not_claim_provider_camera_pose_or_identity_quality():
    projector = AtlasCanonicalHeadNormalResidualDetailProjector

    assert not hasattr(projector, "provider_id")
    assert not hasattr(projector, "camera")
    assert not hasattr(projector, "pose")
    assert not hasattr(projector, "confidence")
    assert not hasattr(projector, "likeness_score")
    assert not hasattr(projector, "phase_9_authorized")
