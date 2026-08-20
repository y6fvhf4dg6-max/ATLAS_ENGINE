from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.atlas_canonical_head_expression_displacement import (
    AtlasCanonicalHeadExpressionDisplacement,
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


def _expression_displacement():
    return np.array(
        [
            [0.00, 0.00, 0.00],
            [0.00, -0.02, 0.01],
            [0.00, -0.03, 0.02],
            [0.00, 0.00, 0.00],
        ],
        dtype=np.float64,
    )


def test_normalizes_expression_id_and_preserves_canonical_topology():
    topology = _topology()

    expression = AtlasCanonicalHeadExpressionDisplacement(
        expression_id="  Smile Open  ",
        topology=topology,
        displacement=_expression_displacement(),
    )

    assert expression.expression_id == "smile_open"
    assert expression.topology is topology
    assert (
        expression.connectivity_signature
        == topology.connectivity_signature
    )


def test_preserves_expression_displacement_as_immutable_snapshot():
    source = _expression_displacement()

    expression = AtlasCanonicalHeadExpressionDisplacement(
        expression_id="smile",
        topology=_topology(),
        displacement=source,
    )

    source[1, 1] = 99.0

    assert expression.displacement[1, 1] == pytest.approx(-0.02)
    assert expression.displacement.flags.writeable is False

    with pytest.raises(ValueError):
        expression.displacement[1, 1] = 2.0

    with pytest.raises(FrozenInstanceError):
        expression.expression_id = "changed"


def test_zero_displacement_represents_neutral_expression():
    expression = AtlasCanonicalHeadExpressionDisplacement(
        expression_id="neutral",
        topology=_topology(),
        displacement=np.zeros((4, 3), dtype=np.float64),
    )

    assert expression.is_neutral is True


def test_nonzero_displacement_is_not_neutral():
    expression = AtlasCanonicalHeadExpressionDisplacement(
        expression_id="smile",
        topology=_topology(),
        displacement=_expression_displacement(),
    )

    assert expression.is_neutral is False


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
def test_rejects_invalid_expression_displacement(displacement):
    with pytest.raises(
        ValueError,
        match="displacement",
    ):
        AtlasCanonicalHeadExpressionDisplacement(
            expression_id="smile",
            topology=_topology(),
            displacement=displacement,
        )


def test_rejects_blank_expression_id():
    with pytest.raises(
        ValueError,
        match="expression_id",
    ):
        AtlasCanonicalHeadExpressionDisplacement(
            expression_id="   ",
            topology=_topology(),
            displacement=_expression_displacement(),
        )


def test_rejects_noncanonical_topology():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadTopology",
    ):
        AtlasCanonicalHeadExpressionDisplacement(
            expression_id="smile",
            topology={},
            displacement=_expression_displacement(),
        )


def test_contract_does_not_mix_identity_pose_camera_or_provider_state():
    expression = AtlasCanonicalHeadExpressionDisplacement(
        expression_id="smile",
        topology=_topology(),
        displacement=_expression_displacement(),
    )

    assert not hasattr(expression, "identity_shape")
    assert not hasattr(expression, "identity_displacement")
    assert not hasattr(expression, "pose")
    assert not hasattr(expression, "camera")
    assert not hasattr(expression, "provider_id")
    assert not hasattr(expression, "confidence")
    assert not hasattr(expression, "likeness_score")
