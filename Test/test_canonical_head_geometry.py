from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)
from CORE.atlas_canonical_head_geometry import (
    AtlasCanonicalHeadGeometry,
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
        },
    )


def _vertices(offset=0.0):
    return np.array(
        [
            [0.0, 0.0, 0.0 + offset],
            [1.0, 0.0, 0.1 + offset],
            [1.0, 1.0, 0.2 + offset],
            [0.0, 1.0, 0.1 + offset],
        ],
        dtype=np.float64,
    )


def test_preserves_topology_and_canonical_vertex_geometry():
    topology = _topology()

    geometry = AtlasCanonicalHeadGeometry(
        topology=topology,
        vertices=_vertices(),
    )

    assert geometry.topology is topology

    np.testing.assert_allclose(
        geometry.vertices,
        _vertices(),
    )

    assert geometry.vertex_count == 4
    assert geometry.face_count == 2
    assert (
        geometry.connectivity_signature
        == topology.connectivity_signature
    )


def test_different_identity_geometry_can_share_same_topology():
    topology = _topology()

    first = AtlasCanonicalHeadGeometry(
        topology=topology,
        vertices=_vertices(0.0),
    )
    second = AtlasCanonicalHeadGeometry(
        topology=topology,
        vertices=_vertices(0.5),
    )

    assert not np.array_equal(
        first.vertices,
        second.vertices,
    )

    assert (
        first.connectivity_signature
        == second.connectivity_signature
        == topology.connectivity_signature
    )


def test_vertices_are_immutable_snapshot():
    source = _vertices()

    geometry = AtlasCanonicalHeadGeometry(
        topology=_topology(),
        vertices=source,
    )

    source[0, 0] = 99.0

    assert geometry.vertices[0, 0] == 0.0
    assert geometry.vertices.flags.writeable is False

    with pytest.raises(ValueError):
        geometry.vertices[0, 0] = 1.0

    with pytest.raises(FrozenInstanceError):
        geometry.topology = _topology()


@pytest.mark.parametrize(
    "vertices",
    [
        np.zeros((3, 3), dtype=np.float64),
        np.zeros((4, 2), dtype=np.float64),
        np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [1.0, 1.0, np.nan],
                [0.0, 1.0, 0.0],
            ]
        ),
    ],
)
def test_rejects_invalid_vertex_geometry(vertices):
    with pytest.raises(
        ValueError,
        match="vertices",
    ):
        AtlasCanonicalHeadGeometry(
            topology=_topology(),
            vertices=vertices,
        )


def test_rejects_non_topology_contract():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadTopology",
    ):
        AtlasCanonicalHeadGeometry(
            topology={},
            vertices=_vertices(),
        )


def test_exposes_semantic_region_vertices_without_changing_topology():
    geometry = AtlasCanonicalHeadGeometry(
        topology=_topology(),
        vertices=_vertices(),
    )

    np.testing.assert_allclose(
        geometry.semantic_region_vertices(
            "nose"
        ),
        np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 1.0, 0.2],
            ],
            dtype=np.float64,
        ),
    )

    with pytest.raises(KeyError):
        geometry.semantic_region_vertices(
            "unknown"
        )


def test_contract_does_not_claim_pose_expression_or_provider():
    geometry = AtlasCanonicalHeadGeometry(
        topology=_topology(),
        vertices=_vertices(),
    )

    assert not hasattr(geometry, "pose")
    assert not hasattr(geometry, "expression")
    assert not hasattr(geometry, "identity_parameters")
    assert not hasattr(geometry, "provider_id")
    assert not hasattr(geometry, "confidence")
