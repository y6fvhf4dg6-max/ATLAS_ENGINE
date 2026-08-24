import numpy as np
import pytest

from CORE.atlas_canonical_head_geometry import (
    AtlasCanonicalHeadGeometry,
)
from CORE.atlas_canonical_head_residual_detail_observation import (
    AtlasCanonicalHeadResidualDetailObservation,
)
from CORE.atlas_canonical_head_surface_correspondence import (
    AtlasCanonicalHeadSurfaceCorrespondence,
)
from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)

from CORE.atlas_canonical_head_correspondence_reference_span_resolver import (
    AtlasCanonicalHeadCorrespondenceReferenceSpanResolver,
)


def _topology():
    return AtlasCanonicalHeadTopology(
        topology_id="fixture-head",
        vertex_count=4,
        faces=(
            (0, 1, 2),
            (0, 2, 3),
        ),
        semantic_vertex_regions={
            "face": (0, 1, 2, 3),
        },
    )


def _geometry():
    return AtlasCanonicalHeadGeometry(
        topology=_topology(),
        vertices=np.array(
            [
                [0.0, 0.0, 0.0],
                [2.0, 0.0, 0.0],
                [2.0, 3.0, 0.0],
                [0.0, 3.0, 0.0],
            ],
            dtype=np.float64,
        ),
    )


def _observation():
    return AtlasCanonicalHeadResidualDetailObservation(
        observation_id="fixture-detail",
        source_view_id="view-a",
        image_width=401,
        image_height=301,
        sample_indices=(10, 20, 30),
        sample_coordinates_normalized=np.array(
            [
                [0.25, 0.20],
                [0.75, 0.20],
                [0.75, 0.80],
            ],
            dtype=np.float64,
        ),
        scalar_detail=np.zeros(
            3,
            dtype=np.float64,
        ),
        confidence=np.ones(
            3,
            dtype=np.float64,
        ),
    )


def _correspondence():
    return AtlasCanonicalHeadSurfaceCorrespondence(
        correspondence_id="fixture-surface",
        topology=_topology(),
        observed_sample_to_canonical_surface={
            10: (0, (1.0, 0.0, 0.0)),
            20: (0, (0.0, 1.0, 0.0)),
            30: (0, (0.0, 0.0, 1.0)),
        },
    )


def test_resolves_equivalent_image_and_canonical_reference_spans():
    result = (
        AtlasCanonicalHeadCorrespondenceReferenceSpanResolver
        .resolve(
            observation=_observation(),
            correspondence=_correspondence(),
            geometry=_geometry(),
        )
    )

    # image pixels:
    # x = 100, 300, 300
    # y = 60, 60, 240
    # bbox diagonal = sqrt(200^2 + 180^2)
    assert result.image_reference_span_px == pytest.approx(
        np.hypot(
            200.0,
            180.0,
        )
    )

    # canonical surface points:
    # (0,0,0), (2,0,0), (2,3,0)
    # bbox diagonal = sqrt(2^2 + 3^2)
    assert result.canonical_reference_span == pytest.approx(
        np.sqrt(
            13.0
        )
    )


def test_uses_only_corresponded_samples():
    observation = AtlasCanonicalHeadResidualDetailObservation(
        observation_id="extra-sample",
        source_view_id="view-a",
        image_width=401,
        image_height=301,
        sample_indices=(10, 20, 30, 999),
        sample_coordinates_normalized=np.array(
            [
                [0.25, 0.20],
                [0.75, 0.20],
                [0.75, 0.80],
                [1.00, 1.00],
            ],
            dtype=np.float64,
        ),
        scalar_detail=np.zeros(
            4,
            dtype=np.float64,
        ),
        confidence=np.ones(
            4,
            dtype=np.float64,
        ),
    )

    result = (
        AtlasCanonicalHeadCorrespondenceReferenceSpanResolver
        .resolve(
            observation=observation,
            correspondence=_correspondence(),
            geometry=_geometry(),
        )
    )

    assert result.image_reference_span_px == pytest.approx(
        np.hypot(
            200.0,
            180.0,
        )
    )


def test_rejects_geometry_with_different_connectivity():
    other_topology = AtlasCanonicalHeadTopology(
        topology_id="other-head",
        vertex_count=4,
        faces=(
            (0, 1, 3),
            (1, 2, 3),
        ),
        semantic_vertex_regions={
            "face": (0, 1, 2, 3),
        },
    )

    geometry = AtlasCanonicalHeadGeometry(
        topology=other_topology,
        vertices=np.zeros(
            (4, 3),
            dtype=np.float64,
        ),
    )

    with pytest.raises(
        ValueError,
        match="TOPOLOGY_MISMATCH",
    ):
        (
            AtlasCanonicalHeadCorrespondenceReferenceSpanResolver
            .resolve(
                observation=_observation(),
                correspondence=_correspondence(),
                geometry=geometry,
            )
        )


def test_rejects_missing_observation_sample():
    observation = AtlasCanonicalHeadResidualDetailObservation(
        observation_id="missing-sample",
        source_view_id="view-a",
        image_width=401,
        image_height=301,
        sample_indices=(10, 20),
        sample_coordinates_normalized=np.array(
            [
                [0.25, 0.20],
                [0.75, 0.20],
            ],
            dtype=np.float64,
        ),
        scalar_detail=np.zeros(
            2,
            dtype=np.float64,
        ),
        confidence=np.ones(
            2,
            dtype=np.float64,
        ),
    )

    with pytest.raises(
        ValueError,
        match="OBSERVATION_SAMPLE_MISMATCH",
    ):
        (
            AtlasCanonicalHeadCorrespondenceReferenceSpanResolver
            .resolve(
                observation=observation,
                correspondence=_correspondence(),
                geometry=_geometry(),
            )
        )
