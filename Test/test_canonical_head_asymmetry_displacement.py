from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.atlas_canonical_head_asymmetry_displacement import (
    AtlasCanonicalHeadAsymmetryDisplacement,
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


def _asymmetry_displacement():
    return np.array(
        [
            [-0.02, 0.00, 0.01],
            [-0.01, 0.01, 0.00],
            [0.03, 0.00, -0.01],
            [0.00, -0.01, 0.02],
        ],
        dtype=np.float64,
    )


def test_normalizes_asymmetry_id_and_preserves_canonical_topology():
    topology = _topology()

    asymmetry = AtlasCanonicalHeadAsymmetryDisplacement(
        asymmetry_id="  Person A Natural Asymmetry  ",
        topology=topology,
        displacement=_asymmetry_displacement(),
    )

    assert (
        asymmetry.asymmetry_id
        == "person_a_natural_asymmetry"
    )
    assert asymmetry.topology is topology
    assert (
        asymmetry.connectivity_signature
        == topology.connectivity_signature
    )


def test_preserves_asymmetry_as_immutable_snapshot():
    source = _asymmetry_displacement()

    asymmetry = AtlasCanonicalHeadAsymmetryDisplacement(
        asymmetry_id="person-a",
        topology=_topology(),
        displacement=source,
    )

    source[0, 0] = 99.0

    assert asymmetry.displacement[0, 0] == pytest.approx(-0.02)
    assert asymmetry.displacement.flags.writeable is False

    with pytest.raises(ValueError):
        asymmetry.displacement[0, 0] = 1.0

    with pytest.raises(FrozenInstanceError):
        asymmetry.asymmetry_id = "changed"


def test_zero_displacement_represents_no_preserved_asymmetry():
    asymmetry = AtlasCanonicalHeadAsymmetryDisplacement(
        asymmetry_id="symmetric-baseline",
        topology=_topology(),
        displacement=np.zeros((4, 3), dtype=np.float64),
    )

    assert asymmetry.has_preserved_asymmetry is False


def test_nonzero_displacement_preserves_real_asymmetry():
    asymmetry = AtlasCanonicalHeadAsymmetryDisplacement(
        asymmetry_id="person-a",
        topology=_topology(),
        displacement=_asymmetry_displacement(),
    )

    assert asymmetry.has_preserved_asymmetry is True


@pytest.mark.parametrize(
    "displacement",
    [
        np.zeros((3, 3), dtype=np.float64),
        np.zeros((4, 2), dtype=np.float64),
        np.array(
            [
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, np.nan, 0.0],
                [0.0, 0.0, 0.0],
            ],
            dtype=np.float64,
        ),
    ],
)
def test_rejects_invalid_asymmetry_displacement(displacement):
    with pytest.raises(
        ValueError,
        match="displacement",
    ):
        AtlasCanonicalHeadAsymmetryDisplacement(
            asymmetry_id="person-a",
            topology=_topology(),
            displacement=displacement,
        )


def test_rejects_blank_asymmetry_id():
    with pytest.raises(
        ValueError,
        match="asymmetry_id",
    ):
        AtlasCanonicalHeadAsymmetryDisplacement(
            asymmetry_id="   ",
            topology=_topology(),
            displacement=_asymmetry_displacement(),
        )


def test_rejects_noncanonical_topology():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadTopology",
    ):
        AtlasCanonicalHeadAsymmetryDisplacement(
            asymmetry_id="person-a",
            topology={},
            displacement=_asymmetry_displacement(),
        )


def test_contract_does_not_mix_expression_pose_camera_or_provider_state():
    asymmetry = AtlasCanonicalHeadAsymmetryDisplacement(
        asymmetry_id="person-a",
        topology=_topology(),
        displacement=_asymmetry_displacement(),
    )

    assert not hasattr(asymmetry, "identity_shape")
    assert not hasattr(asymmetry, "expression")
    assert not hasattr(asymmetry, "pose")
    assert not hasattr(asymmetry, "camera")
    assert not hasattr(asymmetry, "provider_id")
    assert not hasattr(asymmetry, "confidence")
    assert not hasattr(asymmetry, "likeness_score")
