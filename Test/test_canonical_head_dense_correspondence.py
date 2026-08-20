from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_dense_correspondence import (
    AtlasCanonicalHeadDenseCorrespondence,
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


def test_preserves_dense_observation_to_canonical_mapping():
    topology = _topology()

    correspondence = AtlasCanonicalHeadDenseCorrespondence(
        correspondence_id="  Fixture Dense V1  ",
        topology=topology,
        observed_sample_to_canonical_vertex={
            0: 0,
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            5: 5,
        },
    )

    assert correspondence.correspondence_id == "fixture_dense_v1"
    assert correspondence.topology is topology
    assert correspondence.observed_sample_indices == (
        0,
        1,
        2,
        3,
        4,
        5,
    )
    assert correspondence.canonical_vertex_indices == (
        0,
        1,
        2,
        3,
        4,
        5,
    )
    assert correspondence.canonical_vertex_index(4) == 4
    assert correspondence.correspondence_count == 6
    assert correspondence.coverage_ratio == pytest.approx(
        6 / 8
    )
    assert (
        correspondence.connectivity_signature
        == topology.connectivity_signature
    )


def test_dense_mapping_is_immutable_snapshot():
    source = {
        0: 0,
        1: 1,
    }

    correspondence = AtlasCanonicalHeadDenseCorrespondence(
        correspondence_id="fixture",
        topology=_topology(),
        observed_sample_to_canonical_vertex=source,
    )

    source[0] = 7

    assert correspondence.canonical_vertex_index(0) == 0

    with pytest.raises(TypeError):
        correspondence.observed_sample_to_canonical_vertex[0] = 7

    with pytest.raises(FrozenInstanceError):
        correspondence.correspondence_id = "changed"


def test_full_dense_coverage_reports_one():
    topology = _topology()

    correspondence = AtlasCanonicalHeadDenseCorrespondence(
        correspondence_id="fixture-full",
        topology=topology,
        observed_sample_to_canonical_vertex={
            index: index
            for index in range(topology.vertex_count)
        },
    )

    assert correspondence.coverage_ratio == pytest.approx(1.0)


def test_rejects_blank_correspondence_id():
    with pytest.raises(
        ValueError,
        match="correspondence_id",
    ):
        AtlasCanonicalHeadDenseCorrespondence(
            correspondence_id="   ",
            topology=_topology(),
            observed_sample_to_canonical_vertex={
                0: 0,
            },
        )


def test_rejects_noncanonical_topology():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadTopology",
    ):
        AtlasCanonicalHeadDenseCorrespondence(
            correspondence_id="fixture",
            topology={},
            observed_sample_to_canonical_vertex={
                0: 0,
            },
        )


def test_rejects_empty_dense_mapping():
    with pytest.raises(
        ValueError,
        match="observed_sample_to_canonical_vertex",
    ):
        AtlasCanonicalHeadDenseCorrespondence(
            correspondence_id="fixture",
            topology=_topology(),
            observed_sample_to_canonical_vertex={},
        )


@pytest.mark.parametrize(
    "mapping",
    (
        {True: 0},
        {0.5: 0},
        {0: True},
        {0: 1.5},
        {0: -1},
        {0: 8},
    ),
)
def test_rejects_invalid_dense_indices(
    mapping,
):
    with pytest.raises(
        (TypeError, ValueError),
    ):
        AtlasCanonicalHeadDenseCorrespondence(
            correspondence_id="fixture",
            topology=_topology(),
            observed_sample_to_canonical_vertex=mapping,
        )


def test_rejects_duplicate_canonical_targets():
    with pytest.raises(
        ValueError,
        match="canonical vertex",
    ):
        AtlasCanonicalHeadDenseCorrespondence(
            correspondence_id="fixture",
            topology=_topology(),
            observed_sample_to_canonical_vertex={
                0: 2,
                1: 2,
            },
        )


def test_unknown_sample_lookup_raises_key_error():
    correspondence = AtlasCanonicalHeadDenseCorrespondence(
        correspondence_id="fixture",
        topology=_topology(),
        observed_sample_to_canonical_vertex={
            0: 0,
        },
    )

    with pytest.raises(KeyError):
        correspondence.canonical_vertex_index(
            999
        )


def test_contract_does_not_claim_fit_camera_provider_or_identity_quality():
    correspondence = AtlasCanonicalHeadDenseCorrespondence(
        correspondence_id="fixture",
        topology=_topology(),
        observed_sample_to_canonical_vertex={
            0: 0,
        },
    )

    assert not hasattr(correspondence, "provider_id")
    assert not hasattr(correspondence, "confidence")
    assert not hasattr(correspondence, "fit_error")
    assert not hasattr(correspondence, "camera")
    assert not hasattr(correspondence, "identity_shape")
    assert not hasattr(correspondence, "likeness_score")
