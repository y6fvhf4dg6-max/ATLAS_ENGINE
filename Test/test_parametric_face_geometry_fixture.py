import numpy as np
import pytest

from CORE.atlas_parametric_face_geometry import (
    AtlasParametricFaceGeometry,
)
from Test.fixtures.portrait.parametric_face_geometry_fixture import (
    fixture_landmark_names,
    fixture_semantic_region_names,
    load_parametric_face_geometry_fixture,
)


EXPECTED_LANDMARK_NAMES = (
    "chin_tip",
    "left_brow_center",
    "left_eye_center",
    "left_eye_inner",
    "left_eye_outer",
    "left_mouth_corner",
    "nose_bridge",
    "nose_tip",
    "right_brow_center",
    "right_eye_center",
    "right_eye_inner",
    "right_eye_outer",
    "right_mouth_corner",
)

EXPECTED_SEMANTIC_REGION_NAMES = (
    "chin",
    "columella",
    "forehead",
    "jaw",
    "left_ala",
    "left_brow",
    "left_cheek",
    "left_eye_socket",
    "lower_lip",
    "nose_bridge",
    "nose_tip",
    "philtrum",
    "right_ala",
    "right_brow",
    "right_cheek",
    "right_eye_socket",
    "upper_lip",
)


def test_fixture_returns_canonical_geometry():
    geometry = load_parametric_face_geometry_fixture()

    assert isinstance(
        geometry,
        AtlasParametricFaceGeometry,
    )


def test_fixture_has_deterministic_mesh_size():
    geometry = load_parametric_face_geometry_fixture()

    assert geometry.vertex_count == 25
    assert geometry.triangle_count == 32


def test_fixture_vertices_form_three_dimensional_face():
    geometry = load_parametric_face_geometry_fixture()

    assert geometry.vertices.shape == (25, 3)
    assert np.ptp(
        geometry.vertices[:, 0]
    ) > 0.0
    assert np.ptp(
        geometry.vertices[:, 1]
    ) > 0.0
    assert np.ptp(
        geometry.vertices[:, 2]
    ) > 0.0

    nose_tip_index = geometry.landmark_vertex_map[
        "nose_tip"
    ]

    assert geometry.vertices[
        nose_tip_index,
        2,
    ] == pytest.approx(
        geometry.vertices[:, 2].max()
    )


def test_fixture_triangle_indices_are_valid():
    geometry = load_parametric_face_geometry_fixture()

    assert int(
        geometry.triangle_faces.min()
    ) == 0

    assert int(
        geometry.triangle_faces.max()
    ) == geometry.vertex_count - 1


def test_fixture_has_no_duplicate_triangles():
    geometry = load_parametric_face_geometry_fixture()

    normalized_faces = np.sort(
        geometry.triangle_faces,
        axis=1,
    )

    unique_faces = np.unique(
        normalized_faces,
        axis=0,
    )

    assert len(
        unique_faces
    ) == geometry.triangle_count


def test_fixture_has_no_degenerate_triangles():
    geometry = load_parametric_face_geometry_fixture()

    triangle_vertices = geometry.vertices[
        geometry.triangle_faces
    ]

    edge_a = (
        triangle_vertices[:, 1]
        - triangle_vertices[:, 0]
    )

    edge_b = (
        triangle_vertices[:, 2]
        - triangle_vertices[:, 0]
    )

    double_areas = np.linalg.norm(
        np.cross(
            edge_a,
            edge_b,
        ),
        axis=1,
    )

    assert np.all(
        double_areas > 1e-12
    )


def test_fixture_normals_are_unit_length():
    geometry = load_parametric_face_geometry_fixture()

    lengths = np.linalg.norm(
        geometry.surface_normals,
        axis=1,
    )

    assert np.allclose(
        lengths,
        1.0,
    )


def test_fixture_uv_coordinates_are_normalized():
    geometry = load_parametric_face_geometry_fixture()

    assert np.all(
        geometry.uv_coordinates >= 0.0
    )
    assert np.all(
        geometry.uv_coordinates <= 1.0
    )


def test_fixture_semantic_region_names_are_complete():
    assert fixture_semantic_region_names() == (
        EXPECTED_SEMANTIC_REGION_NAMES
    )


def test_fixture_landmark_names_are_complete():
    assert fixture_landmark_names() == (
        EXPECTED_LANDMARK_NAMES
    )


def test_fixture_semantic_regions_are_nonempty():
    geometry = load_parametric_face_geometry_fixture()

    for region_name in (
        EXPECTED_SEMANTIC_REGION_NAMES
    ):
        assert geometry.semantic_vertex_regions[
            region_name
        ]


def test_fixture_preserves_semantic_overlap():
    geometry = load_parametric_face_geometry_fixture()

    nose_tip_index = geometry.landmark_vertex_map[
        "nose_tip"
    ]

    assert nose_tip_index in (
        geometry.semantic_vertex_regions[
            "nose_tip"
        ]
    )

    assert nose_tip_index in (
        geometry.semantic_vertex_regions[
            "columella"
        ]
    )


def test_fixture_landmarks_reference_valid_vertices():
    geometry = load_parametric_face_geometry_fixture()

    for vertex_index in (
        geometry.landmark_vertex_map.values()
    ):
        assert (
            0
            <= vertex_index
            < geometry.vertex_count
        )


def test_fixture_parameter_vectors_are_separated():
    geometry = load_parametric_face_geometry_fixture()

    assert geometry.identity_parameter_count == 4
    assert geometry.expression_parameter_count == 3
    assert geometry.pose_parameter_count == 3

    assert not np.shares_memory(
        geometry.identity_parameters,
        geometry.expression_parameters,
    )

    assert not np.shares_memory(
        geometry.identity_parameters,
        geometry.pose_parameters,
    )


def test_fixture_confidence_and_visibility_are_complete():
    geometry = load_parametric_face_geometry_fixture()

    assert geometry.confidence.shape == (
        geometry.vertex_count,
    )

    assert geometry.visibility.shape == (
        geometry.vertex_count,
    )

    assert np.allclose(
        geometry.confidence,
        1.0,
    )

    assert np.all(
        geometry.visibility
    )


def test_fixture_metadata_is_deterministic():
    geometry = load_parametric_face_geometry_fixture()

    assert geometry.metadata == {
        "coordinate_system": (
            "canonical_frontal_xyz"
        ),
        "fixture_name": (
            "synthetic_parametric_face_geometry_v1"
        ),
        "model_family": "synthetic",
        "provider_id": (
            "atlas-synthetic-canonical-fixture"
        ),
        "synthetic": True,
        "topology": "fixed",
        "view_type": "front",
    }


def test_fixture_returns_independent_results():
    first = load_parametric_face_geometry_fixture()
    second = load_parametric_face_geometry_fixture()

    assert first is not second
    assert not np.shares_memory(
        first.vertices,
        second.vertices,
    )
    assert first.to_dict() == second.to_dict()


def test_fixture_serialization_is_deterministic():
    first = load_parametric_face_geometry_fixture()
    second = load_parametric_face_geometry_fixture()

    assert first.to_dict() == second.to_dict()
