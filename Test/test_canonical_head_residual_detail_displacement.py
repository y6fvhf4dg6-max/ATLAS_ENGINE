from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.atlas_canonical_head_residual_detail_displacement import (
    AtlasCanonicalHeadResidualDetailDisplacement,
)
from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)


def _topology():
    return AtlasCanonicalHeadTopology(
        topology_id="fixture-head-v1",
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


def test_preserves_residual_detail_identity_and_topology():
    topology = _topology()

    detail = AtlasCanonicalHeadResidualDetailDisplacement(
        detail_id="  Person A Micro Detail  ",
        topology=topology,
        displacement=np.array(
            [
                [0.0, 0.0, 0.010],
                [0.0, 0.0, -0.005],
                [0.0, 0.0, 0.004],
                [0.0, 0.0, 0.000],
            ],
            dtype=np.float64,
        ),
    )

    assert detail.detail_id == "person_a_micro_detail"
    assert detail.topology is topology
    assert detail.displacement.shape == (4, 3)
    assert detail.displacement.dtype == np.float64
    assert (
        detail.connectivity_signature
        == topology.connectivity_signature
    )


def test_displacement_is_immutable_snapshot():
    topology = _topology()

    source = np.full(
        (4, 3),
        0.01,
        dtype=np.float64,
    )

    detail = AtlasCanonicalHeadResidualDetailDisplacement(
        detail_id="detail",
        topology=topology,
        displacement=source,
    )

    source[0, 0] = 99.0

    assert detail.displacement[0, 0] == pytest.approx(
        0.01
    )
    assert detail.displacement.flags.writeable is False

    with pytest.raises(ValueError):
        detail.displacement[0, 0] = 1.0

    with pytest.raises(FrozenInstanceError):
        detail.detail_id = "changed"


def test_rejects_blank_detail_id():
    with pytest.raises(
        ValueError,
        match="detail_id",
    ):
        AtlasCanonicalHeadResidualDetailDisplacement(
            detail_id="   ",
            topology=_topology(),
            displacement=np.zeros(
                (4, 3),
                dtype=np.float64,
            ),
        )


def test_rejects_noncanonical_topology():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadTopology",
    ):
        AtlasCanonicalHeadResidualDetailDisplacement(
            detail_id="detail",
            topology={},
            displacement=np.zeros(
                (4, 3),
                dtype=np.float64,
            ),
        )


@pytest.mark.parametrize(
    "displacement",
    (
        np.zeros((4, 2), dtype=np.float64),
        np.zeros((3, 3), dtype=np.float64),
    ),
)
def test_rejects_wrong_displacement_shape(
    displacement,
):
    with pytest.raises(
        ValueError,
        match="displacement.*shape",
    ):
        AtlasCanonicalHeadResidualDetailDisplacement(
            detail_id="detail",
            topology=_topology(),
            displacement=displacement,
        )


def test_rejects_nonfinite_displacement():
    displacement = np.zeros(
        (4, 3),
        dtype=np.float64,
    )
    displacement[1, 2] = np.nan

    with pytest.raises(
        ValueError,
        match="finite",
    ):
        AtlasCanonicalHeadResidualDetailDisplacement(
            detail_id="detail",
            topology=_topology(),
            displacement=displacement,
        )


def test_contract_does_not_claim_identity_expression_pose_provider_or_confidence():
    detail = AtlasCanonicalHeadResidualDetailDisplacement(
        detail_id="detail",
        topology=_topology(),
        displacement=np.zeros(
            (4, 3),
            dtype=np.float64,
        ),
    )

    assert not hasattr(detail, "identity_shape")
    assert not hasattr(detail, "expression")
    assert not hasattr(detail, "pose")
    assert not hasattr(detail, "camera")
    assert not hasattr(detail, "provider_id")
    assert not hasattr(detail, "confidence")
    assert not hasattr(detail, "likeness_score")
    assert not hasattr(detail, "phase_9_authorized")
