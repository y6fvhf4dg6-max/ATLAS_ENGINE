from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.atlas_canonical_head_geometry import (
    AtlasCanonicalHeadGeometry,
)
from CORE.atlas_canonical_head_identity_shape import (
    AtlasCanonicalHeadIdentityShape,
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


def _reference_geometry():
    return AtlasCanonicalHeadGeometry(
        topology=_topology(),
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


def _identity_displacement():
    return np.array(
        [
            [0.00, 0.00, 0.10],
            [0.05, 0.00, 0.15],
            [0.05, 0.00, 0.20],
            [0.00, 0.00, 0.10],
        ],
        dtype=np.float64,
    )


def test_normalizes_identity_shape_id_and_preserves_reference_geometry():
    reference = _reference_geometry()

    shape = AtlasCanonicalHeadIdentityShape(
        identity_shape_id="  Fixture Person A  ",
        reference_geometry=reference,
        identity_displacement=_identity_displacement(),
    )

    assert shape.identity_shape_id == "fixture_person_a"
    assert shape.reference_geometry is reference
    assert (
        shape.connectivity_signature
        == reference.connectivity_signature
    )


def test_resolved_geometry_is_reference_plus_identity_displacement():
    reference = _reference_geometry()
    displacement = _identity_displacement()

    shape = AtlasCanonicalHeadIdentityShape(
        identity_shape_id="person-a",
        reference_geometry=reference,
        identity_displacement=displacement,
    )

    resolved = shape.resolved_geometry

    assert isinstance(
        resolved,
        AtlasCanonicalHeadGeometry,
    )
    assert resolved.topology is reference.topology

    np.testing.assert_allclose(
        resolved.vertices,
        reference.vertices + displacement,
    )


def test_different_identity_shapes_preserve_same_canonical_topology():
    reference = _reference_geometry()

    first = AtlasCanonicalHeadIdentityShape(
        identity_shape_id="person-a",
        reference_geometry=reference,
        identity_displacement=_identity_displacement(),
    )
    second = AtlasCanonicalHeadIdentityShape(
        identity_shape_id="person-b",
        reference_geometry=reference,
        identity_displacement=_identity_displacement() * 2.0,
    )

    assert not np.array_equal(
        first.resolved_geometry.vertices,
        second.resolved_geometry.vertices,
    )

    assert (
        first.connectivity_signature
        == second.connectivity_signature
        == reference.connectivity_signature
    )


def test_identity_displacement_is_immutable_snapshot():
    source = _identity_displacement()

    shape = AtlasCanonicalHeadIdentityShape(
        identity_shape_id="person-a",
        reference_geometry=_reference_geometry(),
        identity_displacement=source,
    )

    source[0, 2] = 99.0

    assert shape.identity_displacement[0, 2] == 0.10
    assert shape.identity_displacement.flags.writeable is False

    with pytest.raises(ValueError):
        shape.identity_displacement[0, 2] = 2.0

    with pytest.raises(FrozenInstanceError):
        shape.identity_shape_id = "changed"


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
def test_rejects_invalid_identity_displacement(
    displacement,
):
    with pytest.raises(
        ValueError,
        match="identity_displacement",
    ):
        AtlasCanonicalHeadIdentityShape(
            identity_shape_id="person-a",
            reference_geometry=_reference_geometry(),
            identity_displacement=displacement,
        )


def test_rejects_blank_identity_shape_id():
    with pytest.raises(
        ValueError,
        match="identity_shape_id",
    ):
        AtlasCanonicalHeadIdentityShape(
            identity_shape_id="   ",
            reference_geometry=_reference_geometry(),
            identity_displacement=_identity_displacement(),
        )


def test_rejects_noncanonical_reference_geometry():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadGeometry",
    ):
        AtlasCanonicalHeadIdentityShape(
            identity_shape_id="person-a",
            reference_geometry={},
            identity_displacement=_identity_displacement(),
        )


def test_contract_does_not_mix_expression_pose_or_residual_detail():
    shape = AtlasCanonicalHeadIdentityShape(
        identity_shape_id="person-a",
        reference_geometry=_reference_geometry(),
        identity_displacement=_identity_displacement(),
    )

    assert not hasattr(shape, "expression")
    assert not hasattr(shape, "pose")
    assert not hasattr(shape, "expression_displacement")
    assert not hasattr(shape, "residual_detail")
    assert not hasattr(shape, "provider_id")
    assert not hasattr(shape, "confidence")
    assert not hasattr(shape, "likeness_score")
