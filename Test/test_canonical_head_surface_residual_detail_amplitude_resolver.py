import numpy as np
import pytest

from CORE.atlas_canonical_head_residual_detail_observation import (
    AtlasCanonicalHeadResidualDetailObservation,
)
from CORE.atlas_canonical_head_surface_correspondence import (
    AtlasCanonicalHeadSurfaceCorrespondence,
)
from CORE.atlas_canonical_head_surface_residual_detail_amplitude_resolver import (
    AtlasCanonicalHeadSurfaceResidualDetailAmplitudeResolver,
)
from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)


def _topology():
    return AtlasCanonicalHeadTopology(
        topology_id="fixture-head",
        vertex_count=5,
        faces=(
            (0, 1, 2),
            (1, 2, 3),
        ),
        semantic_vertex_regions={
            "face": (0, 1, 2, 3, 4),
        },
    )


def _observation(
    sample_indices=(10,),
    scalar_detail=(0.6,),
    confidence=(0.8,),
):
    count = len(sample_indices)

    return AtlasCanonicalHeadResidualDetailObservation(
        observation_id="surface-detail",
        source_view_id="view-a",
        image_width=640,
        image_height=480,
        sample_indices=sample_indices,
        sample_coordinates_normalized=np.zeros(
            (count, 2),
            dtype=np.float64,
        ),
        scalar_detail=np.asarray(
            scalar_detail,
            dtype=np.float64,
        ),
        confidence=np.asarray(
            confidence,
            dtype=np.float64,
        ),
    )


def _correspondence(mapping):
    return AtlasCanonicalHeadSurfaceCorrespondence(
        correspondence_id="surface-correspondence",
        topology=_topology(),
        observed_sample_to_canonical_surface=mapping,
    )


def test_single_vertex_surface_sample_matches_direct_vertex_semantics():
    result = AtlasCanonicalHeadSurfaceResidualDetailAmplitudeResolver.resolve(
        observation=_observation(),
        correspondence=_correspondence({
            10: (0, (1.0, 0.0, 0.0)),
        }),
    )

    assert result.canonical_scalar_detail == pytest.approx(
        (0.6, 0.0, 0.0, 0.0, 0.0)
    )
    assert result.canonical_confidence == pytest.approx(
        (0.8, 0.0, 0.0, 0.0, 0.0)
    )
    assert result.mapped_vertex_count == 1


def test_interior_surface_sample_is_reconstructed_by_barycentric_constraint():
    weights = np.array(
        (0.2, 0.3, 0.5),
        dtype=np.float64,
    )

    result = AtlasCanonicalHeadSurfaceResidualDetailAmplitudeResolver.resolve(
        observation=_observation(
            scalar_detail=(0.7,),
            confidence=(0.9,),
        ),
        correspondence=_correspondence({
            10: (0, tuple(weights)),
        }),
    )

    reconstructed_detail = float(
        np.dot(
            weights,
            result.canonical_scalar_detail[:3],
        )
    )

    reconstructed_confidence = float(
        np.dot(
            weights,
            result.canonical_confidence[:3],
        )
    )

    assert reconstructed_detail == pytest.approx(
        0.7,
        abs=1e-12,
    )
    assert reconstructed_confidence == pytest.approx(
        0.9,
        abs=1e-12,
    )
    assert result.canonical_scalar_detail[4] == 0.0
    assert result.canonical_confidence[4] == 0.0
    assert result.mapped_vertex_count == 3


def test_multiple_surface_samples_are_solved_together_deterministically():
    observation = _observation(
        sample_indices=(10, 20),
        scalar_detail=(0.4, -0.2),
        confidence=(0.8, 0.6),
    )
    correspondence = _correspondence({
        10: (0, (0.5, 0.5, 0.0)),
        20: (1, (0.0, 0.5, 0.5)),
    })

    first = AtlasCanonicalHeadSurfaceResidualDetailAmplitudeResolver.resolve(
        observation=observation,
        correspondence=correspondence,
    )
    second = AtlasCanonicalHeadSurfaceResidualDetailAmplitudeResolver.resolve(
        observation=observation,
        correspondence=correspondence,
    )

    assert np.array_equal(
        first.canonical_scalar_detail,
        second.canonical_scalar_detail,
    )
    assert np.array_equal(
        first.canonical_confidence,
        second.canonical_confidence,
    )

    assert (
        0.5 * first.canonical_scalar_detail[0]
        + 0.5 * first.canonical_scalar_detail[1]
    ) == pytest.approx(0.4)

    assert (
        0.5 * first.canonical_scalar_detail[2]
        + 0.5 * first.canonical_scalar_detail[3]
    ) == pytest.approx(-0.2)


def test_confidence_remains_separate_from_raw_scalar_detail():
    result = AtlasCanonicalHeadSurfaceResidualDetailAmplitudeResolver.resolve(
        observation=_observation(
            scalar_detail=(1.0,),
            confidence=(0.25,),
        ),
        correspondence=_correspondence({
            10: (0, (1.0, 0.0, 0.0)),
        }),
    )

    assert result.canonical_scalar_detail[0] == pytest.approx(1.0)
    assert result.canonical_confidence[0] == pytest.approx(0.25)


def test_blocks_unknown_observation_sample():
    with pytest.raises(
        ValueError,
        match="OBSERVATION_SAMPLE_MISMATCH",
    ):
        AtlasCanonicalHeadSurfaceResidualDetailAmplitudeResolver.resolve(
            observation=_observation(),
            correspondence=_correspondence({
                999: (0, (1.0, 0.0, 0.0)),
            }),
        )


def test_result_preserves_topology_signature_and_is_immutable():
    correspondence = _correspondence({
        10: (0, (1.0, 0.0, 0.0)),
    })

    result = AtlasCanonicalHeadSurfaceResidualDetailAmplitudeResolver.resolve(
        observation=_observation(),
        correspondence=correspondence,
    )

    assert (
        result.connectivity_signature
        == correspondence.connectivity_signature
    )
    assert result.canonical_scalar_detail.flags.writeable is False
    assert result.canonical_confidence.flags.writeable is False


def test_rejects_wrong_boundary_types():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadResidualDetailObservation",
    ):
        AtlasCanonicalHeadSurfaceResidualDetailAmplitudeResolver.resolve(
            observation={},
            correspondence=_correspondence({
                10: (0, (1.0, 0.0, 0.0)),
            }),
        )

    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadSurfaceCorrespondence",
    ):
        AtlasCanonicalHeadSurfaceResidualDetailAmplitudeResolver.resolve(
            observation=_observation(),
            correspondence={},
        )
