import numpy as np
import pytest

from CORE.atlas_portrait_flame_barycentric_landmark_evaluator import (
    AtlasPortraitFlameBarycentricEmbedding,
    AtlasPortraitFlameBarycentricLandmarkEvaluator,
)


def _mesh():
    vertices = np.array(
        [
            [0.0, 0.0, 0.0],
            [2.0, 0.0, 0.0],
            [0.0, 2.0, 0.0],
            [0.0, 0.0, 2.0],
        ],
        dtype=np.float64,
    )

    faces = np.array(
        [
            [0, 1, 2],
            [0, 1, 3],
        ],
        dtype=np.int64,
    )

    return vertices, faces


def test_barycentric_evaluator_returns_expected_surface_points():
    vertices, faces = _mesh()

    embedding = AtlasPortraitFlameBarycentricEmbedding(
        landmark_indices=np.array([33, 263]),
        face_indices=np.array([0, 1]),
        barycentric_coordinates=np.array(
            [
                [0.5, 0.25, 0.25],
                [0.25, 0.25, 0.5],
            ]
        ),
    )

    points = AtlasPortraitFlameBarycentricLandmarkEvaluator.evaluate(
        vertices=vertices,
        faces=faces,
        embedding=embedding,
    )

    np.testing.assert_allclose(
        points,
        np.array(
            [
                [0.5, 0.5, 0.0],
                [0.5, 0.0, 1.0],
            ]
        ),
    )


def test_embedding_from_npz_style_mapping():
    mapping = {
        "landmark_indices": np.array([1, 2]),
        "lmk_face_idx": np.array([0, 1]),
        "lmk_b_coords": np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ]
        ),
    }

    embedding = (
        AtlasPortraitFlameBarycentricEmbedding.from_npz_mapping(
            mapping
        )
    )

    assert embedding.landmark_count == 2
    np.testing.assert_array_equal(
        embedding.landmark_indices,
        np.array([1, 2]),
    )


def test_embedding_arrays_are_read_only():
    embedding = AtlasPortraitFlameBarycentricEmbedding(
        landmark_indices=np.array([1]),
        face_indices=np.array([0]),
        barycentric_coordinates=np.array(
            [[1.0, 0.0, 0.0]]
        ),
    )

    assert embedding.landmark_indices.flags.writeable is False
    assert embedding.face_indices.flags.writeable is False
    assert embedding.barycentric_coordinates.flags.writeable is False


def test_surface_points_are_read_only():
    vertices, faces = _mesh()

    embedding = AtlasPortraitFlameBarycentricEmbedding(
        landmark_indices=np.array([1]),
        face_indices=np.array([0]),
        barycentric_coordinates=np.array(
            [[1.0, 0.0, 0.0]]
        ),
    )

    points = AtlasPortraitFlameBarycentricLandmarkEvaluator.evaluate(
        vertices=vertices,
        faces=faces,
        embedding=embedding,
    )

    assert points.flags.writeable is False


def test_duplicate_landmark_ids_are_rejected():
    with pytest.raises(
        ValueError,
        match="must be unique",
    ):
        AtlasPortraitFlameBarycentricEmbedding(
            landmark_indices=np.array([1, 1]),
            face_indices=np.array([0, 0]),
            barycentric_coordinates=np.array(
                [
                    [1.0, 0.0, 0.0],
                    [1.0, 0.0, 0.0],
                ]
            ),
        )


def test_barycentric_rows_must_sum_to_one():
    with pytest.raises(
        ValueError,
        match="must sum to 1",
    ):
        AtlasPortraitFlameBarycentricEmbedding(
            landmark_indices=np.array([1]),
            face_indices=np.array([0]),
            barycentric_coordinates=np.array(
                [[0.2, 0.2, 0.2]]
            ),
        )


def test_out_of_range_embedding_face_is_rejected():
    vertices, faces = _mesh()

    embedding = AtlasPortraitFlameBarycentricEmbedding(
        landmark_indices=np.array([1]),
        face_indices=np.array([99]),
        barycentric_coordinates=np.array(
            [[1.0, 0.0, 0.0]]
        ),
    )

    with pytest.raises(
        ValueError,
        match="outside mesh topology",
    ):
        AtlasPortraitFlameBarycentricLandmarkEvaluator.evaluate(
            vertices=vertices,
            faces=faces,
            embedding=embedding,
        )


def test_real_repo_embedding_contract_is_105_unique_landmarks():
    path = (
        "Data/MODELS/FLAME/"
        "mediapipe_landmark_embedding.npz"
    )

    with np.load(path) as mapping:
        embedding = (
            AtlasPortraitFlameBarycentricEmbedding.from_npz_mapping(
                mapping
            )
        )

    assert embedding.landmark_count == 105
    assert len(
        np.unique(embedding.landmark_indices)
    ) == 105


def test_real_repo_flame_template_evaluates_all_105_surface_points():
    import pickle

    with open(
        "Data/MODELS/FLAME/flame2023_Open.pkl",
        "rb",
    ) as stream:
        flame = pickle.load(
            stream,
            encoding="latin1",
        )

    with np.load(
        "Data/MODELS/FLAME/"
        "mediapipe_landmark_embedding.npz"
    ) as mapping:
        embedding = (
            AtlasPortraitFlameBarycentricEmbedding.from_npz_mapping(
                mapping
            )
        )

    points = AtlasPortraitFlameBarycentricLandmarkEvaluator.evaluate(
        vertices=np.asarray(
            flame["v_template"],
            dtype=np.float64,
        ),
        faces=np.asarray(
            flame["f"],
            dtype=np.int64,
        ),
        embedding=embedding,
    )

    assert points.shape == (105, 3)
    assert np.all(np.isfinite(points))
