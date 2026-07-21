from __future__ import annotations

import pytest

from CORE.providers.portrait.atlas_flame_mediapipe_landmark_correspondence import (
    AtlasFlameMediaPipeLandmarkCorrespondence,
)


EXPECTED_MAPPING = {
    "left_eye_outer": 263,
    "left_eye_inner": 362,
    "right_eye_inner": 133,
    "right_eye_outer": 33,
    "left_eyebrow_outer": 300,
    "left_eyebrow_inner": 336,
    "right_eyebrow_inner": 107,
    "right_eyebrow_outer": 70,
    "nose_root": 168,
    "nose_bridge": 197,
    "nose_tip": 4,
    "nose_left": 327,
    "nose_right": 98,
    "mouth_left": 291,
    "upper_lip_center": 0,
    "lower_lip_center": 17,
    "mouth_right": 61,
}

UNSUPPORTED_GROUND_TRUTH_NAMES = (
    "chin_tip",
    "hairline_center",
    "left_face_edge",
    "left_jaw",
    "right_face_edge",
    "right_jaw",
)


def test_correspondence_exposes_expected_version():
    assert (
        AtlasFlameMediaPipeLandmarkCorrespondence.VERSION
        == "flame-mediapipe-ground-truth-v1"
    )


def test_correspondence_exposes_exact_mapping():
    assert (
        AtlasFlameMediaPipeLandmarkCorrespondence.mapping()
        == EXPECTED_MAPPING
    )


def test_correspondence_has_seventeen_landmarks():
    correspondence = (
        AtlasFlameMediaPipeLandmarkCorrespondence
    )

    assert correspondence.landmark_count() == 17


def test_landmark_names_are_sorted_and_deterministic():
    correspondence = (
        AtlasFlameMediaPipeLandmarkCorrespondence
    )

    assert correspondence.landmark_names() == tuple(
        sorted(
            EXPECTED_MAPPING,
        )
    )


def test_mediapipe_ids_follow_landmark_name_order():
    correspondence = (
        AtlasFlameMediaPipeLandmarkCorrespondence
    )

    assert correspondence.mediapipe_ids() == tuple(
        EXPECTED_MAPPING[name]
        for name in sorted(
            EXPECTED_MAPPING,
        )
    )


@pytest.mark.parametrize(
    (
        "landmark_name",
        "expected_media_pipe_id",
    ),
    sorted(
        EXPECTED_MAPPING.items(),
    ),
)
def test_resolve_returns_expected_media_pipe_id(
    landmark_name,
    expected_media_pipe_id,
):
    correspondence = (
        AtlasFlameMediaPipeLandmarkCorrespondence
    )

    assert correspondence.resolve(
        landmark_name,
    ) == expected_media_pipe_id


@pytest.mark.parametrize(
    "landmark_name",
    UNSUPPORTED_GROUND_TRUTH_NAMES,
)
def test_unsupported_ground_truth_landmarks_are_explicit(
    landmark_name,
):
    correspondence = (
        AtlasFlameMediaPipeLandmarkCorrespondence
    )

    assert correspondence.is_supported(
        landmark_name,
    ) is False

    with pytest.raises(
        KeyError,
        match=landmark_name,
    ):
        correspondence.resolve(
            landmark_name,
        )


@pytest.mark.parametrize(
    "landmark_name",
    EXPECTED_MAPPING,
)
def test_supported_landmarks_are_reported(
    landmark_name,
):
    assert (
        AtlasFlameMediaPipeLandmarkCorrespondence.is_supported(
            landmark_name,
        )
        is True
    )


@pytest.mark.parametrize(
    "invalid_name",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_resolve_rejects_invalid_landmark_name(
    invalid_name,
):
    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
    ):
        AtlasFlameMediaPipeLandmarkCorrespondence.resolve(
            invalid_name,
        )


def test_mapping_result_is_independent():
    correspondence = (
        AtlasFlameMediaPipeLandmarkCorrespondence
    )

    first = correspondence.mapping()
    second = correspondence.mapping()

    assert first == second
    assert first is not second

    first[
        "nose_tip"
    ] = 999

    assert correspondence.resolve(
        "nose_tip",
    ) == 4


def test_all_mediapipe_ids_are_unique():
    media_pipe_ids = (
        AtlasFlameMediaPipeLandmarkCorrespondence
        .mediapipe_ids()
    )

    assert len(
        media_pipe_ids,
    ) == len(
        set(
            media_pipe_ids,
        )
    )


def test_validate_embedding_indices_accepts_complete_embedding():
    correspondence = (
        AtlasFlameMediaPipeLandmarkCorrespondence
    )

    embedding_indices = set(
        correspondence.mediapipe_ids(),
    )

    embedding_indices.update(
        {
            2,
            5,
            6,
            13,
            14,
            55,
            63,
            97,
            285,
            293,
            326,
        }
    )

    assert correspondence.validate_embedding_indices(
        embedding_indices,
    ) == correspondence.mediapipe_ids()


def test_validate_embedding_indices_rejects_missing_required_id():
    correspondence = (
        AtlasFlameMediaPipeLandmarkCorrespondence
    )

    embedding_indices = set(
        correspondence.mediapipe_ids(),
    )

    embedding_indices.remove(
        197,
    )

    with pytest.raises(
        ValueError,
        match="197",
    ):
        correspondence.validate_embedding_indices(
            embedding_indices,
        )


@pytest.mark.parametrize(
    "embedding_indices",
    [
        None,
        "0, 4, 17",
        123,
    ],
)
def test_validate_embedding_indices_rejects_non_iterable_or_text(
    embedding_indices,
):
    with pytest.raises(
        TypeError,
    ):
        AtlasFlameMediaPipeLandmarkCorrespondence.validate_embedding_indices(
            embedding_indices,
        )


def test_correspondence_metadata_is_deterministic():
    correspondence = (
        AtlasFlameMediaPipeLandmarkCorrespondence
    )

    assert correspondence.metadata() == {
        "correspondence_version": (
            "flame-mediapipe-ground-truth-v1"
        ),
        "landmark_count": 17,
        "model_family": "flame",
        "source_embedding": (
            "mediapipe_landmark_embedding"
        ),
        "unsupported_ground_truth_landmarks": list(
            UNSUPPORTED_GROUND_TRUTH_NAMES
        ),
    }


def test_validate_embedding_indices_accepts_numpy_integer_values():
    import numpy as np

    correspondence = (
        AtlasFlameMediaPipeLandmarkCorrespondence
    )

    embedding_indices = np.asarray(
        correspondence.mediapipe_ids(),
        dtype=np.int64,
    )

    assert correspondence.validate_embedding_indices(
        embedding_indices,
    ) == correspondence.mediapipe_ids()
