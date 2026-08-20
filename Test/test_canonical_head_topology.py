from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)


def _topology(**overrides):
    values = {
        "topology_id": "fixture-head-v1",
        "vertex_count": 6,
        "faces": (
            (0, 1, 2),
            (0, 2, 3),
            (0, 3, 4),
            (0, 4, 5),
        ),
        "semantic_vertex_regions": {
            "face": (0, 1, 2, 3, 4, 5),
            "nose": (0, 2, 3),
            "left_eye": (1, 2),
            "right_eye": (4, 5),
        },
    }
    values.update(overrides)
    return AtlasCanonicalHeadTopology(**values)


def test_normalizes_provider_independent_canonical_topology():
    topology = _topology(
        topology_id="  Fixture Head V1  ",
        semantic_vertex_regions={
            " Face ": (0, 1, 2, 3, 4, 5),
            "Nose": (0, 2, 3),
        },
    )

    assert topology.topology_id == "fixture_head_v1"
    assert topology.vertex_count == 6
    assert topology.faces == (
        (0, 1, 2),
        (0, 2, 3),
        (0, 3, 4),
        (0, 4, 5),
    )
    assert topology.semantic_vertex_regions == {
        "face": (0, 1, 2, 3, 4, 5),
        "nose": (0, 2, 3),
    }


def test_exposes_deterministic_connectivity_signature():
    first = _topology()
    second = _topology(
        topology_id="different-provider-label",
    )

    assert first.connectivity_signature == second.connectivity_signature
    assert len(first.connectivity_signature) == 64


def test_connectivity_signature_changes_when_faces_change():
    first = _topology()
    second = _topology(
        faces=(
            (0, 1, 2),
            (0, 2, 4),
            (0, 4, 5),
        )
    )

    assert (
        first.connectivity_signature
        != second.connectivity_signature
    )


def test_topology_is_immutable_snapshot():
    faces = [
        [0, 1, 2],
        [0, 2, 3],
    ]
    regions = {
        "face": [0, 1, 2, 3],
    }

    topology = _topology(
        vertex_count=4,
        faces=faces,
        semantic_vertex_regions=regions,
    )

    faces[0][0] = 3
    regions["face"].append(99)

    assert topology.faces == (
        (0, 1, 2),
        (0, 2, 3),
    )
    assert topology.semantic_vertex_regions == {
        "face": (0, 1, 2, 3),
    }

    with pytest.raises(FrozenInstanceError):
        topology.vertex_count = 99

    with pytest.raises(TypeError):
        topology.semantic_vertex_regions["face"] = (0,)


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"topology_id": "   "}, "topology_id"),
        ({"vertex_count": 0}, "vertex_count"),
        ({"faces": ()}, "faces"),
        ({"faces": ((0, 1),)}, "exactly three"),
        ({"faces": ((0, 1, 6),)}, "vertex index"),
        ({"faces": ((0, 0, 1),)}, "distinct"),
        (
            {
                "faces": (
                    (0, 1, 2),
                    (0, 1, 2),
                )
            },
            "unique",
        ),
        (
            {
                "semantic_vertex_regions": {
                    "nose": (),
                }
            },
            "must not be empty",
        ),
        (
            {
                "semantic_vertex_regions": {
                    "nose": (0, 6),
                }
            },
            "vertex index",
        ),
        (
            {
                "semantic_vertex_regions": {},
            },
            "must not be empty",
        ),
    ],
)
def test_rejects_invalid_topology(overrides, message):
    with pytest.raises(
        (TypeError, ValueError),
        match=message,
    ):
        _topology(**overrides)


def test_contract_does_not_claim_instance_geometry_or_provider():
    topology = _topology()

    assert not hasattr(topology, "vertices")
    assert not hasattr(topology, "identity_shape")
    assert not hasattr(topology, "expression")
    assert not hasattr(topology, "provider_id")
    assert not hasattr(topology, "confidence")
