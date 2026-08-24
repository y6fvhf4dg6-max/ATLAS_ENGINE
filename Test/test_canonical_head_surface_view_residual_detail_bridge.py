import numpy as np
import pytest

from CORE.atlas_canonical_head_residual_detail_observation import (
    AtlasCanonicalHeadResidualDetailObservation,
)
from CORE.atlas_canonical_head_surface_correspondence import (
    AtlasCanonicalHeadSurfaceCorrespondence,
)
from CORE.atlas_canonical_head_surface_view_residual_detail_bridge import (
    AtlasCanonicalHeadSurfaceViewResidualDetailBridge,
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


def _observation():
    return AtlasCanonicalHeadResidualDetailObservation(
        observation_id="surface-view-detail",
        source_view_id="view-a",
        image_width=640,
        image_height=480,
        sample_indices=(10, 20),
        sample_coordinates_normalized=np.array(
            [
                [0.25, 0.30],
                [0.75, 0.60],
            ],
            dtype=np.float64,
        ),
        scalar_detail=np.array(
            [
                0.40,
                -0.20,
            ],
            dtype=np.float64,
        ),
        confidence=np.array(
            [
                0.80,
                0.50,
            ],
            dtype=np.float64,
        ),
    )


def _correspondence():
    return AtlasCanonicalHeadSurfaceCorrespondence(
        correspondence_id="surface-view-correspondence",
        topology=_topology(),
        observed_sample_to_canonical_surface={
            10: (0, (0.5, 0.5, 0.0)),
            20: (1, (0.0, 0.5, 0.5)),
        },
    )


def test_bridges_surface_observation_through_surface_amplitude_and_policy():
    result = (
        AtlasCanonicalHeadSurfaceViewResidualDetailBridge
        .resolve(
            observation=_observation(),
            correspondence=_correspondence(),
            maximum_absolute_amplitude=0.15,
        )
    )

    assert result.observation_id == "surface-view-detail"
    assert result.source_view_id == "view-a"

    assert result.canonical_scalar_detail.shape == (5,)
    assert result.canonical_confidence.shape == (5,)
    assert result.weighted_amplitude.shape == (5,)
    assert result.bounded_amplitude.shape == (5,)

    assert np.all(
        np.abs(
            result.bounded_amplitude
        )
        <= 0.15 + 1e-12
    )

    assert result.mapped_vertex_count == 4

    assert (
        result.connectivity_signature
        == _correspondence().connectivity_signature
    )


def test_preserves_confidence_weighting_as_policy_owned_behavior():
    result = (
        AtlasCanonicalHeadSurfaceViewResidualDetailBridge
        .resolve(
            observation=_observation(),
            correspondence=_correspondence(),
            maximum_absolute_amplitude=1.0,
        )
    )

    np.testing.assert_allclose(
        result.weighted_amplitude,
        (
            result.canonical_scalar_detail
            * result.canonical_confidence
        ),
    )


def test_rejects_non_surface_correspondence():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadSurfaceCorrespondence",
    ):
        (
            AtlasCanonicalHeadSurfaceViewResidualDetailBridge
            .resolve(
                observation=_observation(),
                correspondence={},
                maximum_absolute_amplitude=0.15,
            )
        )


def test_bridge_does_not_claim_projection_visibility_or_geometry():
    result = (
        AtlasCanonicalHeadSurfaceViewResidualDetailBridge
        .resolve(
            observation=_observation(),
            correspondence=_correspondence(),
            maximum_absolute_amplitude=0.15,
        )
    )

    for forbidden_attribute in (
        "camera",
        "pose",
        "visibility",
        "occlusion",
        "projected_normal",
        "normal_direction",
        "displacement",
        "geometry",
        "provider_id",
        "identity_score",
        "phase_9_authorized",
    ):
        assert not hasattr(
            result,
            forbidden_attribute,
        )
