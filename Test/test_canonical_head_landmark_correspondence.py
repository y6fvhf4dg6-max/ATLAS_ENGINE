from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_landmark_correspondence import (
    AtlasCanonicalHeadLandmarkCorrespondence,
)
from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)


def _topology():
    return AtlasCanonicalHeadTopology(
        topology_id="fixture-head-v1",
        vertex_count=8,
        faces=(
            (0, 1, 2),
            (0, 2, 3),
            (0, 3, 4),
            (0, 4, 5),
            (0, 5, 6),
            (0, 6, 7),
        ),
        semantic_vertex_regions={
            "face": tuple(range(8)),
            "nose": (0, 3, 4),
            "left_eye": (1, 2),
            "right_eye": (5, 6),
        },
    )


def test_preserves_observed_to_canonical_vertex_mapping():
    topology = _topology()

    correspondence = AtlasCanonicalHeadLandmarkCorrespondence(
        correspondence_id="  Fixture Sparse V1  ",
        topology=topology,
        observed_to_canonical_vertex={
            4: 3,
            33: 1,
            133: 2,
            263: 6,
        },
    )

    assert correspondence.correspondence_id == "fixture_sparse_v1"
    assert correspondence.topology is topology
    assert correspondence.observed_landmark_ids == (
        4,
        33,
        133,
        263,
    )
    assert correspondence.canonical_vertex_indices == (
        3,
        1,
        2,
        6,
    )
    assert correspondence.canonical_vertex_index(133) == 2
    assert correspondence.correspondence_count == 4
    assert (
        correspondence.connectivity_signature
        == topology.connectivity_signature
    )


def test_mapping_is_immutable_snapshot():
    source = {
        4: 3,
        33: 1,
    }

    correspondence = AtlasCanonicalHeadLandmarkCorrespondence(
        correspondence_id="fixture",
        topology=_topology(),
        observed_to_canonical_vertex=source,
    )

    source[4] = 7

    assert correspondence.canonical_vertex_index(4) == 3

    with pytest.raises(TypeError):
        correspondence.observed_to_canonical_vertex[4] = 7

    with pytest.raises(FrozenInstanceError):
        correspondence.correspondence_id = "changed"


def test_rejects_blank_correspondence_id():
    with pytest.raises(
        ValueError,
        match="correspondence_id",
    ):
        AtlasCanonicalHeadLandmarkCorrespondence(
            correspondence_id="   ",
            topology=_topology(),
            observed_to_canonical_vertex={
                4: 3,
            },
        )


def test_rejects_noncanonical_topology():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadTopology",
    ):
        AtlasCanonicalHeadLandmarkCorrespondence(
            correspondence_id="fixture",
            topology={},
            observed_to_canonical_vertex={
                4: 3,
            },
        )


def test_rejects_empty_correspondence_mapping():
    with pytest.raises(
        ValueError,
        match="observed_to_canonical_vertex",
    ):
        AtlasCanonicalHeadLandmarkCorrespondence(
            correspondence_id="fixture",
            topology=_topology(),
            observed_to_canonical_vertex={},
        )


@pytest.mark.parametrize(
    "mapping",
    (
        {True: 1},
        {4.5: 1},
        {4: True},
        {4: 2.5},
        {4: -1},
        {4: 8},
    ),
)
def test_rejects_invalid_observed_or_canonical_indices(
    mapping,
):
    with pytest.raises(
        (TypeError, ValueError),
    ):
        AtlasCanonicalHeadLandmarkCorrespondence(
            correspondence_id="fixture",
            topology=_topology(),
            observed_to_canonical_vertex=mapping,
        )


def test_rejects_duplicate_canonical_vertex_targets():
    with pytest.raises(
        ValueError,
        match="canonical vertex",
    ):
        AtlasCanonicalHeadLandmarkCorrespondence(
            correspondence_id="fixture",
            topology=_topology(),
            observed_to_canonical_vertex={
                33: 2,
                133: 2,
            },
        )


def test_unknown_observed_landmark_lookup_raises_key_error():
    correspondence = AtlasCanonicalHeadLandmarkCorrespondence(
        correspondence_id="fixture",
        topology=_topology(),
        observed_to_canonical_vertex={
            4: 3,
        },
    )

    with pytest.raises(KeyError):
        correspondence.canonical_vertex_index(
            999
        )


def test_contract_is_provider_independent_and_does_not_claim_fit_quality():
    correspondence = AtlasCanonicalHeadLandmarkCorrespondence(
        correspondence_id="fixture",
        topology=_topology(),
        observed_to_canonical_vertex={
            4: 3,
        },
    )

    assert not hasattr(correspondence, "provider_id")
    assert not hasattr(correspondence, "confidence")
    assert not hasattr(correspondence, "fit_error")
    assert not hasattr(correspondence, "camera")
    assert not hasattr(correspondence, "identity_shape")
    assert not hasattr(correspondence, "dense_correspondence")
