from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import trimesh


import pytest

from CORE.atlas_canonical_head_physical_mesh_adapter import (
    AtlasCanonicalHeadPhysicalMeshAdapter,
)


def _open_triangle_mesh():
    return {
        "vertices": (
            (-1.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
        ),
        "faces": (
            (0, 1, 2),
        ),
        "provenance": "unit_test_open_triangle",
    }


def test_adapter_rejects_unsupported_representation_kind():
    with pytest.raises(ValueError, match="representation_kind"):
        AtlasCanonicalHeadPhysicalMeshAdapter.build(
            canonical_mesh=_open_triangle_mesh(),
            representation_kind="unknown",
            target_head_height_mm=40.0,
        )


@pytest.mark.parametrize(
    "representation_kind",
    (
        "relief",
        "bust",
        "figurine_head",
        "story_kit_component",
    ),
)
def test_adapter_accepts_all_required_representation_families(
    representation_kind,
):
    result = AtlasCanonicalHeadPhysicalMeshAdapter.build(
        canonical_mesh=_open_triangle_mesh(),
        representation_kind=representation_kind,
        target_head_height_mm=40.0,
    )

    assert result["representation_kind"] == representation_kind


def test_adapter_requires_positive_target_head_height_mm():
    with pytest.raises(ValueError, match="target_head_height_mm"):
        AtlasCanonicalHeadPhysicalMeshAdapter.build(
            canonical_mesh=_open_triangle_mesh(),
            representation_kind="bust",
            target_head_height_mm=0.0,
        )


def test_adapter_preserves_original_canonical_vertices():
    source = _open_triangle_mesh()
    original_vertices = source["vertices"]

    result = AtlasCanonicalHeadPhysicalMeshAdapter.build(
        canonical_mesh=source,
        representation_kind="bust",
        target_head_height_mm=40.0,
    )

    assert source["vertices"] == original_vertices
    assert result["canonical_vertices"] == original_vertices


def test_adapter_reports_explicit_scale_and_provenance():
    result = AtlasCanonicalHeadPhysicalMeshAdapter.build(
        canonical_mesh=_open_triangle_mesh(),
        representation_kind="bust",
        target_head_height_mm=40.0,
    )

    assert result["target_head_height_mm"] == pytest.approx(40.0)
    assert result["scale_factor"] > 0.0
    assert result["source_provenance"] == "unit_test_open_triangle"
    assert result["adapter_provenance"]


def test_adapter_returns_ready_triangle_mesh():
    result = AtlasCanonicalHeadPhysicalMeshAdapter.build(
        canonical_mesh=_open_triangle_mesh(),
        representation_kind="bust",
        target_head_height_mm=40.0,
    )

    physical_mesh = result["physical_mesh"]

    assert isinstance(physical_mesh, dict)
    assert physical_mesh["triangles"]
    assert all(
        len(triangle) == 3
        and all(len(point) == 3 for point in triangle)
        for triangle in physical_mesh["triangles"]
    )


def _open_tetrahedron():
    # Closed tetrahedron with its base face intentionally missing.
    # Boundary loop: vertices 0 -> 2 -> 1 -> 0.
    return {
        "vertices": (
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
        ),
        "faces": (
            (0, 1, 3),
            (1, 2, 3),
            (2, 0, 3),
        ),
        "provenance": "unit_test_open_tetrahedron",
    }


def _triangle_edge_counts(triangles):
    counts = {}

    for triangle in triangles:
        for p1, p2 in (
            (triangle[0], triangle[1]),
            (triangle[1], triangle[2]),
            (triangle[2], triangle[0]),
        ):
            edge = tuple(sorted((p1, p2)))
            counts[edge] = counts.get(edge, 0) + 1

    return counts


def test_boundary_closure_produces_closed_manifold_without_moving_canonical_vertices():
    source = _open_tetrahedron()
    original_vertices = source["vertices"]

    result = AtlasCanonicalHeadPhysicalMeshAdapter.build(
        canonical_mesh=source,
        representation_kind="bust",
        target_head_height_mm=40.0,
        close_boundaries=True,
    )

    assert source["vertices"] == original_vertices
    assert result["canonical_vertices"] == original_vertices

    physical_mesh = result["physical_mesh"]
    edge_counts = _triangle_edge_counts(
        physical_mesh["triangles"]
    )

    assert sum(
        count == 1
        for count in edge_counts.values()
    ) == 0

    assert sum(
        count > 2
        for count in edge_counts.values()
    ) == 0

    assert result["boundary_closure_status"] == "CLOSED"
    assert result["source_open_boundary_count"] == 1
    assert result["closed_boundary_count"] == 1
    assert result["added_closure_triangle_count"] > 0


def _open_tetrahedron_with_detached_closed_tetrahedron():
    return {
        "vertices": (
            # Main open tetrahedron: three connected faces.
            (0.0, 0.0, 0.0),
            (2.0, 0.0, 0.0),
            (0.0, 2.0, 0.0),
            (0.0, 0.0, 2.0),

            # Smaller detached component.
            (10.0, 0.0, 0.0),
            (11.0, 0.0, 0.0),
            (10.0, 1.0, 0.0),
        ),
        "faces": (
            # Main component: base intentionally open.
            (0, 1, 3),
            (1, 2, 3),
            (2, 0, 3),

            # Detached one-face component.
            (4, 6, 5),
        ),
        "provenance": "unit_test_main_head_plus_detached_component",
    }


def test_main_head_only_keeps_largest_connected_component_and_records_exclusions():
    source = _open_tetrahedron_with_detached_closed_tetrahedron()
    original_vertices = source["vertices"]
    original_faces = source["faces"]

    result = AtlasCanonicalHeadPhysicalMeshAdapter.build(
        canonical_mesh=source,
        representation_kind="bust",
        target_head_height_mm=40.0,
        close_boundaries=True,
        main_head_only=True,
    )

    assert source["vertices"] == original_vertices
    assert source["faces"] == original_faces
    assert result["canonical_vertices"] == original_vertices

    assert result["source_connected_component_count"] == 2
    assert result["selected_source_component_face_count"] == 3
    assert result["discarded_source_component_count"] == 1
    assert result["discarded_source_face_count"] == 1

    assert result["source_open_boundary_count"] == 1
    assert result["closed_boundary_count"] == 1

    assert len(
        result["physical_mesh"]["triangles"]
    ) == 6



def test_repo_local_real_flame_main_head_only_produces_single_closed_volume():
    root = Path(__file__).resolve().parents[1]

    flame_path = (
        root
        / "Data"
        / "MODELS"
        / "FLAME"
        / "flame2023_Open.pkl"
    )

    with flame_path.open("rb") as stream:
        flame = pickle.load(
            stream,
            encoding="latin1",
        )

    vertices = np.asarray(
        flame["v_template"],
        dtype=np.float64,
    )

    faces = np.asarray(
        flame["f"],
        dtype=np.int64,
    )

    source_vertices = tuple(
        tuple(float(value) for value in vertex)
        for vertex in vertices
    )

    source_faces = tuple(
        tuple(int(index) for index in face)
        for face in faces
    )

    source = {
        "vertices": source_vertices,
        "faces": source_faces,
        "provenance": (
            "repo-local:Data/MODELS/FLAME/"
            "flame2023_Open.pkl:v_template"
        ),
    }

    result = AtlasCanonicalHeadPhysicalMeshAdapter.build(
        canonical_mesh=source,
        representation_kind="bust",
        target_head_height_mm=40.0,
        close_boundaries=True,
        main_head_only=True,
    )

    triangles = np.asarray(
        result["physical_mesh"]["triangles"],
        dtype=np.float64,
    )

    mesh = trimesh.Trimesh(
        vertices=triangles.reshape(-1, 3),
        faces=np.arange(
            triangles.shape[0] * 3,
            dtype=np.int64,
        ).reshape(-1, 3),
        process=True,
        validate=False,
    )

    bodies = mesh.split(
        only_watertight=False
    )

    assert len(source_vertices) == 5023
    assert len(source_faces) == 9976

    assert (
        result["source_connected_component_count"]
        == 3
    )
    assert (
        result["selected_source_component_face_count"]
        == 7800
    )
    assert (
        result["discarded_source_component_count"]
        == 2
    )
    assert (
        result["discarded_source_face_count"]
        == 2176
    )

    assert result["source_open_boundary_count"] == 2
    assert result["closed_boundary_count"] == 2
    assert result["added_closure_triangle_count"] == 62

    assert len(triangles) == 7862
    assert len(bodies) == 1

    assert mesh.is_watertight
    assert mesh.is_winding_consistent
    assert mesh.is_volume

    assert (
        result["canonical_vertices"]
        == source_vertices
    )
    assert result["boundary_closure_status"] == "CLOSED"
    assert result["manufacturability_status"] == "UNRESOLVED"


def test_boundary_closure_rejects_non_manifold_source_edge():
    source = {
        "vertices": (
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
            (0.0, -1.0, 0.0),
        ),
        "faces": (
            # Edge (0, 1) is shared by three faces.
            (0, 1, 2),
            (1, 0, 3),
            (0, 1, 4),
        ),
        "provenance": "unit_test_non_manifold_edge",
    }

    with pytest.raises(
        ValueError,
        match="non-manifold",
    ):
        AtlasCanonicalHeadPhysicalMeshAdapter.build(
            canonical_mesh=source,
            representation_kind="bust",
            target_head_height_mm=40.0,
            close_boundaries=True,
        )


def test_boundary_closure_preserves_reversed_source_winding_consistency():
    source = _open_tetrahedron()

    reversed_faces = tuple(
        (a, c, b)
        for a, b, c in source["faces"]
    )

    result = AtlasCanonicalHeadPhysicalMeshAdapter.build(
        canonical_mesh={
            **source,
            "faces": reversed_faces,
            "provenance": "unit_test_open_tetrahedron_reversed_winding",
        },
        representation_kind="bust",
        target_head_height_mm=40.0,
        close_boundaries=True,
    )

    triangles = np.asarray(
        result["physical_mesh"]["triangles"],
        dtype=np.float64,
    )

    mesh = trimesh.Trimesh(
        vertices=triangles.reshape(-1, 3),
        faces=np.arange(
            triangles.shape[0] * 3,
            dtype=np.int64,
        ).reshape(-1, 3),
        process=True,
        validate=False,
    )

    assert mesh.is_watertight
    assert mesh.is_winding_consistent
    assert mesh.is_volume


def test_boundary_closure_exposes_explicit_physical_attachment_boundary():
    source = _open_tetrahedron()

    result = AtlasCanonicalHeadPhysicalMeshAdapter.build(
        canonical_mesh=source,
        representation_kind="bust",
        target_head_height_mm=40.0,
        close_boundaries=True,
    )

    records = result["physical_boundary_loops"]

    assert len(records) == 1

    record = records[0]

    assert record["boundary_index"] == 0
    assert len(record["vertex_indices"]) == 3
    assert len(record["physical_points"]) == 3
    assert len(record["centroid"]) == 3

    attachment = result["support_attachment_boundary"]

    assert attachment is not None
    assert (
        result["physical_mesh"][
            "support_attachment_boundary"
        ]
        == attachment
    )
    assert (
        attachment["boundary_index"]
        == record["boundary_index"]
    )
    assert (
        attachment["physical_points"]
        == record["physical_points"]
    )
    assert (
        result["support_attachment_boundary_policy"]
        == "lowest_mean_y_boundary"
    )


def test_repo_local_real_flame_exposes_bottom_boundary_without_provider_semantic_label():
    root = Path(__file__).resolve().parents[1]

    flame_path = (
        root
        / "Data"
        / "MODELS"
        / "FLAME"
        / "flame2023_Open.pkl"
    )

    with flame_path.open("rb") as stream:
        flame = pickle.load(
            stream,
            encoding="latin1",
        )

    source_vertices = tuple(
        tuple(float(value) for value in vertex)
        for vertex in np.asarray(
            flame["v_template"],
            dtype=np.float64,
        )
    )

    source_faces = tuple(
        tuple(int(index) for index in face)
        for face in np.asarray(
            flame["f"],
            dtype=np.int64,
        )
    )

    result = AtlasCanonicalHeadPhysicalMeshAdapter.build(
        canonical_mesh={
            "vertices": source_vertices,
            "faces": source_faces,
            "provenance": (
                "repo-local:Data/MODELS/FLAME/"
                "flame2023_Open.pkl:v_template"
            ),
        },
        representation_kind="bust",
        target_head_height_mm=40.0,
        close_boundaries=True,
        main_head_only=True,
    )

    records = result["physical_boundary_loops"]

    assert len(records) == 2

    attachment = result[
        "support_attachment_boundary"
    ]

    assert attachment is not None
    assert len(
        attachment["physical_points"]
    ) == 30

    attachment_mean_y = sum(
        point[1]
        for point in attachment["physical_points"]
    ) / len(
        attachment["physical_points"]
    )

    other = next(
        record
        for record in records
        if (
            record["boundary_index"]
            != attachment["boundary_index"]
        )
    )

    other_mean_y = sum(
        point[1]
        for point in other["physical_points"]
    ) / len(
        other["physical_points"]
    )

    assert attachment_mean_y < other_mean_y
    assert (
        result["support_attachment_boundary_policy"]
        == "lowest_mean_y_boundary"
    )

    # Explicitly geometry-derived only:
    # no provider semantic such as "neck" or "mouth".
    assert "semantic_region" not in attachment
