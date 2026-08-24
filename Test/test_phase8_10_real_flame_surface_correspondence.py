import json
import pickle
from pathlib import Path

import numpy as np
import pytest

from CORE.atlas_canonical_head_residual_detail_observation import (
    AtlasCanonicalHeadResidualDetailObservation,
)
from CORE.atlas_canonical_head_surface_correspondence import (
    AtlasCanonicalHeadSurfaceCorrespondence,
)
from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)


ROOT = Path(__file__).resolve().parents[1]

BENCHMARK_DIR = (
    ROOT
    / "Data"
    / "PORTRAIT"
    / "phase8_10_flame_multiview_benchmark"
)

FLAME_MODEL_PATH = (
    ROOT
    / "Data"
    / "MODELS"
    / "FLAME"
    / "flame2023_Open.pkl"
)

FLAME_EMBEDDING_PATH = (
    ROOT
    / "Data"
    / "MODELS"
    / "FLAME"
    / "mediapipe_landmark_embedding.npz"
)

CASES = (
    "subject_01_front",
    "subject_01_side_a",
    "subject_01_side_b",
    "subject_02_front",
    "subject_02_side_a",
    "subject_02_side_b",
)


def _load_real_flame_topology():
    with FLAME_MODEL_PATH.open("rb") as stream:
        flame = pickle.load(
            stream,
            encoding="latin1",
        )

    faces = np.asarray(
        flame["f"],
        dtype=np.int64,
    )

    vertex_count = int(
        faces.max()
    ) + 1

    return AtlasCanonicalHeadTopology(
        topology_id="flame-2023-open-real",
        vertex_count=vertex_count,
        faces=tuple(
            tuple(
                int(index)
                for index in face
            )
            for face in faces
        ),
        semantic_vertex_regions={
            "face": tuple(
                range(
                    vertex_count
                )
            ),
        },
    )


def _load_real_flame_surface_mapping():
    embedding = np.load(
        FLAME_EMBEDDING_PATH
    )

    landmark_indices = embedding[
        "landmark_indices"
    ]
    face_indices = embedding[
        "lmk_face_idx"
    ]
    barycentric = embedding[
        "lmk_b_coords"
    ]

    assert landmark_indices.shape == (105,)
    assert face_indices.shape == (105,)
    assert barycentric.shape == (105, 3)

    return {
        int(sample_index): (
            int(face_index),
            tuple(
                float(weight)
                for weight in weights
            ),
        )
        for sample_index, face_index, weights in zip(
            landmark_indices,
            face_indices,
            barycentric,
            strict=True,
        )
    }


def _load_landmark_observation(case_id):
    path = (
        BENCHMARK_DIR
        / "landmarks"
        / f"{case_id}.json"
    )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    landmarks = data["landmarks"]

    sample_indices = tuple(
        int(item["id"])
        for item in landmarks
    )

    coordinates = np.asarray(
        [
            (
                float(item["x"]),
                float(item["y"]),
            )
            for item in landmarks
        ],
        dtype=np.float64,
    )

    return AtlasCanonicalHeadResidualDetailObservation(
        observation_id=f"{case_id}-correspondence-boundary",
        source_view_id=case_id,
        image_width=int(
            data["image_width"]
        ),
        image_height=int(
            data["image_height"]
        ),
        sample_indices=sample_indices,
        sample_coordinates_normalized=coordinates,
        scalar_detail=np.zeros(
            len(sample_indices),
            dtype=np.float64,
        ),
        confidence=np.ones(
            len(sample_indices),
            dtype=np.float64,
        ),
    )


def test_real_six_view_flame_surface_correspondence_is_complete():
    topology = _load_real_flame_topology()
    mapping = _load_real_flame_surface_mapping()

    correspondence = AtlasCanonicalHeadSurfaceCorrespondence(
        correspondence_id=(
            "phase8-10-real-mediapipe-to-flame-surface"
        ),
        topology=topology,
        observed_sample_to_canonical_surface=mapping,
    )

    assert topology.vertex_count == 5023
    assert len(topology.faces) == 9976

    assert correspondence.correspondence_count == 105
    assert len(
        set(
            correspondence.observed_sample_indices
        )
    ) == 105

    for case_id in CASES:
        observation = _load_landmark_observation(
            case_id
        )

        assert observation.sample_count == 478

        missing = (
            set(
                correspondence.observed_sample_indices
            )
            - set(
                observation.sample_indices
            )
        )

        assert missing == set()

        for sample_index in (
            correspondence.observed_sample_indices
        ):
            face_index, weights = (
                correspondence.canonical_surface_location(
                    sample_index
                )
            )

            assert 0 <= face_index < len(
                topology.faces
            )
            assert sum(weights) == pytest.approx(
                1.0,
                abs=1e-12,
            )


def test_real_correspondence_preserves_flame_connectivity_signature():
    topology = _load_real_flame_topology()

    correspondence = AtlasCanonicalHeadSurfaceCorrespondence(
        correspondence_id=(
            "phase8-10-real-flame-connectivity"
        ),
        topology=topology,
        observed_sample_to_canonical_surface=(
            _load_real_flame_surface_mapping()
        ),
    )

    assert (
        correspondence.connectivity_signature
        == topology.connectivity_signature
    )

from CORE.atlas_canonical_head_dsine_residual_detail_field_source import (
    AtlasCanonicalHeadDsineResidualDetailFieldSource,
)
from CORE.atlas_canonical_head_residual_detail_image_sampler import (
    AtlasCanonicalHeadResidualDetailImageSampler,
)
from CORE.atlas_relief_face_landmark_regions import (
    AtlasReliefFaceLandmarkRegions,
)
from CORE.atlas_relief_face_structure_confidence_map import (
    AtlasReliefFaceStructureConfidenceMap,
)
from CORE.atlas_relief_mediapipe_landmark_adapter import (
    AtlasReliefMediaPipeLandmarkAdapter,
)


DSINE_EVIDENCE_DIR = Path(
    "/Users/Kubi/ATLAS_HYBRID_SPIKE/EVIDENCE/"
    "phase8_10_hybrid_dsine_2026-08-23"
)


def _load_real_residual_detail_observation(case_id):
    landmark_path = (
        BENCHMARK_DIR
        / "landmarks"
        / f"{case_id}.json"
    )

    data = json.loads(
        landmark_path.read_text(
            encoding="utf-8"
        )
    )

    width = int(data["image_width"])
    height = int(data["image_height"])
    landmarks = data["landmarks"]

    normalized_xy = np.asarray(
        [
            (
                float(item["x"]),
                float(item["y"]),
            )
            for item in landmarks
        ],
        dtype=np.float64,
    )

    points_xy = normalized_xy * np.asarray(
        (
            width - 1,
            height - 1,
        ),
        dtype=np.float64,
    )

    semantic_landmarks = (
        AtlasReliefMediaPipeLandmarkAdapter.convert(
            points_xy=points_xy,
            image_shape=(height, width),
        )
    )

    regions = AtlasReliefFaceLandmarkRegions.build(
        image_shape=(height, width),
        landmarks=semantic_landmarks,
    )

    face_support = regions.masks[
        "face_interior"
    ]

    confidence_field = (
        AtlasReliefFaceStructureConfidenceMap.build(
            face_support,
            landmark_regions=regions.masks,
        )
    )

    normals = np.load(
        DSINE_EVIDENCE_DIR
        / f"{case_id}_dsine_normals.npy"
    )

    field_result = (
        AtlasCanonicalHeadDsineResidualDetailFieldSource.build(
            normals=normals,
            confidence_field=confidence_field,
            mask=face_support,
        )
    )

    sample_indices = tuple(
        int(item["id"])
        for item in landmarks
    )

    return AtlasCanonicalHeadResidualDetailImageSampler.sample(
        observation_id=f"{case_id}-real-dsine-residual-detail",
        source_view_id=case_id,
        scalar_detail_field=field_result.scalar_detail_field,
        confidence_field=field_result.confidence_field,
        sample_indices=sample_indices,
        sample_coordinates_normalized=normalized_xy,
    )


def test_real_six_view_dsine_observations_bind_to_flame_surface():
    topology = _load_real_flame_topology()

    correspondence = AtlasCanonicalHeadSurfaceCorrespondence(
        correspondence_id=(
            "phase8-10-real-dsine-to-flame-surface"
        ),
        topology=topology,
        observed_sample_to_canonical_surface=(
            _load_real_flame_surface_mapping()
        ),
    )

    for case_id in CASES:
        observation = (
            _load_real_residual_detail_observation(
                case_id
            )
        )

        assert observation.sample_count == 478
        assert np.all(
            np.isfinite(
                observation.scalar_detail
            )
        )
        assert np.all(
            np.isfinite(
                observation.confidence
            )
        )

        required = (
            correspondence.observed_sample_indices
        )

        assert set(required).issubset(
            observation.sample_indices
        )

        real_detail = np.asarray(
            [
                observation.scalar_detail_for_sample(
                    sample_index
                )
                for sample_index in required
            ],
            dtype=np.float64,
        )

        real_confidence = np.asarray(
            [
                observation.confidence_for_sample(
                    sample_index
                )
                for sample_index in required
            ],
            dtype=np.float64,
        )

        assert real_detail.shape == (105,)
        assert real_confidence.shape == (105,)
        assert np.all(np.isfinite(real_detail))
        assert np.all(np.isfinite(real_confidence))
        assert np.all(real_confidence >= 0.0)
        assert np.all(real_confidence <= 1.0)

        for sample_index in required:
            face_index, weights = (
                correspondence.canonical_surface_location(
                    sample_index
                )
            )

            assert 0 <= face_index < len(
                topology.faces
            )
            assert sum(weights) == pytest.approx(
                1.0,
                abs=1e-12,
            )

from CORE.atlas_canonical_head_correspondence_reference_span_resolver import (
    AtlasCanonicalHeadCorrespondenceReferenceSpanResolver,
)
from CORE.atlas_canonical_head_geometry import (
    AtlasCanonicalHeadGeometry,
)
from CORE.atlas_canonical_head_residual_detail_scale_normalizer import (
    AtlasCanonicalHeadResidualDetailScaleNormalizer,
)
from CORE.atlas_canonical_head_surface_residual_detail_amplitude_resolver import (
    AtlasCanonicalHeadSurfaceResidualDetailAmplitudeResolver,
)


def _load_real_flame_reference_geometry():
    with FLAME_MODEL_PATH.open("rb") as stream:
        flame = pickle.load(
            stream,
            encoding="latin1",
        )

    topology = _load_real_flame_topology()

    vertices = np.asarray(
        flame["v_template"],
        dtype=np.float64,
    )

    assert vertices.shape == (
        topology.vertex_count,
        3,
    )

    return AtlasCanonicalHeadGeometry(
        topology=topology,
        vertices=vertices,
    )


def test_real_six_view_normalized_detail_runs_canonical_amplitude_resolver():
    geometry = _load_real_flame_reference_geometry()

    correspondence = AtlasCanonicalHeadSurfaceCorrespondence(
        correspondence_id=(
            "phase8-10-real-normalized-dsine-to-flame-surface"
        ),
        topology=geometry.topology,
        observed_sample_to_canonical_surface=(
            _load_real_flame_surface_mapping()
        ),
    )

    expected_supported_vertices = {
        vertex_index
        for sample_index in correspondence.observed_sample_indices
        for vertex_index, weight in zip(
            geometry.topology.faces[
                correspondence.canonical_surface_location(
                    sample_index
                )[0]
            ],
            correspondence.canonical_surface_location(
                sample_index
            )[1],
            strict=True,
        )
        if weight > 0.0
    }

    assert expected_supported_vertices

    for case_id in CASES:
        observation = (
            _load_real_residual_detail_observation(
                case_id
            )
        )

        spans = (
            AtlasCanonicalHeadCorrespondenceReferenceSpanResolver
            .resolve(
                observation=observation,
                correspondence=correspondence,
                geometry=geometry,
            )
        )

        assert spans.image_reference_span_px > 0.0
        assert spans.canonical_reference_span > 0.0

        normalized = (
            AtlasCanonicalHeadResidualDetailScaleNormalizer
            .normalize(
                observation=observation,
                image_reference_span_px=(
                    spans.image_reference_span_px
                ),
                canonical_reference_span=(
                    spans.canonical_reference_span
                ),
            )
        )

        amplitude = (
            AtlasCanonicalHeadSurfaceResidualDetailAmplitudeResolver
            .resolve(
                observation=normalized.observation,
                correspondence=correspondence,
            )
        )

        assert normalized.scale_factor > 0.0

        assert amplitude.mapped_vertex_count == len(
            expected_supported_vertices
        )

        assert amplitude.canonical_scalar_detail.shape == (
            geometry.vertex_count,
        )
        assert amplitude.canonical_confidence.shape == (
            geometry.vertex_count,
        )

        assert np.all(
            np.isfinite(
                amplitude.canonical_scalar_detail
            )
        )
        assert np.all(
            np.isfinite(
                amplitude.canonical_confidence
            )
        )

        assert np.all(
            amplitude.canonical_confidence >= 0.0
        )
        assert np.all(
            amplitude.canonical_confidence <= 1.0
        )

        assert np.any(
            np.abs(
                amplitude.canonical_scalar_detail
            ) > 0.0
        )

        assert (
            amplitude.connectivity_signature
            == geometry.connectivity_signature
            == correspondence.connectivity_signature
        )

        unsupported = np.ones(
            geometry.vertex_count,
            dtype=bool,
        )
        unsupported[
            np.asarray(
                sorted(
                    expected_supported_vertices
                ),
                dtype=np.int64,
            )
        ] = False

        assert np.all(
            amplitude.canonical_scalar_detail[
                unsupported
            ]
            == 0.0
        )
        assert np.all(
            amplitude.canonical_confidence[
                unsupported
            ]
            == 0.0
        )

from CORE.atlas_canonical_head_residual_detail_amplitude_policy import (
    AtlasCanonicalHeadResidualDetailAmplitudePolicy,
)


PHASE8_10_HYBRID_MAXIMUM_AMPLITUDE_FRACTION = 0.01


def test_real_six_view_bounded_amplitude_policy_uses_one_percent_canonical_span():
    geometry = _load_real_flame_reference_geometry()

    correspondence = AtlasCanonicalHeadSurfaceCorrespondence(
        correspondence_id=(
            "phase8-10-real-bounded-dsine-to-flame-surface"
        ),
        topology=geometry.topology,
        observed_sample_to_canonical_surface=(
            _load_real_flame_surface_mapping()
        ),
    )

    expected_clipped_by_case = {
        "subject_01_front": 0,
        "subject_01_side_a": 0,
        "subject_01_side_b": 0,
        "subject_02_front": 0,
        "subject_02_side_a": 1,
        "subject_02_side_b": 0,
    }

    aggregate_active = 0
    aggregate_clipped = 0

    for case_id in CASES:
        observation = (
            _load_real_residual_detail_observation(
                case_id
            )
        )

        spans = (
            AtlasCanonicalHeadCorrespondenceReferenceSpanResolver
            .resolve(
                observation=observation,
                correspondence=correspondence,
                geometry=geometry,
            )
        )

        normalized = (
            AtlasCanonicalHeadResidualDetailScaleNormalizer
            .normalize(
                observation=observation,
                image_reference_span_px=(
                    spans.image_reference_span_px
                ),
                canonical_reference_span=(
                    spans.canonical_reference_span
                ),
            )
        )

        amplitude = (
            AtlasCanonicalHeadSurfaceResidualDetailAmplitudeResolver
            .resolve(
                observation=normalized.observation,
                correspondence=correspondence,
            )
        )

        maximum = (
            spans.canonical_reference_span
            * PHASE8_10_HYBRID_MAXIMUM_AMPLITUDE_FRACTION
        )

        policy = (
            AtlasCanonicalHeadResidualDetailAmplitudePolicy
            .apply(
                amplitude_result=amplitude,
                maximum_absolute_amplitude=maximum,
            )
        )

        active_mask = (
            amplitude.canonical_confidence > 0.0
        )

        active_count = int(
            np.count_nonzero(
                active_mask
            )
        )

        clipped_mask = (
            np.abs(
                policy.weighted_amplitude
            )
            > maximum + 1e-15
        ) & active_mask

        clipped_count = int(
            np.count_nonzero(
                clipped_mask
            )
        )

        assert clipped_count == (
            expected_clipped_by_case[
                case_id
            ]
        )

        assert float(
            np.max(
                np.abs(
                    policy.bounded_amplitude
                )
            )
        ) <= maximum + 1e-12

        np.testing.assert_allclose(
            policy.weighted_amplitude,
            (
                amplitude.canonical_scalar_detail
                * amplitude.canonical_confidence
            ),
        )

        assert (
            policy.maximum_absolute_amplitude
            == pytest.approx(
                maximum
            )
        )

        assert (
            policy.mapped_vertex_count
            == amplitude.mapped_vertex_count
        )

        assert (
            policy.connectivity_signature
            == amplitude.connectivity_signature
        )

        aggregate_active += active_count
        aggregate_clipped += clipped_count

    assert aggregate_active == 1268
    assert aggregate_clipped == 1

    assert (
        100.0
        * aggregate_clipped
        / aggregate_active
    ) == pytest.approx(
        0.07886435331230283
    )
