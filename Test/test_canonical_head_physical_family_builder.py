from __future__ import annotations

import pytest

from CORE.atlas_canonical_head_physical_family_builder import (
    AtlasCanonicalHeadPhysicalFamilyBuilder,
)


REQUIRED_FAMILIES = (
    "relief",
    "bust",
    "figurine_head",
    "story_kit_component",
)


def _closed_tetrahedron_physical_mesh():
    v0 = (0.0, 0.0, 0.0)
    v1 = (20.0, 0.0, 0.0)
    v2 = (0.0, 40.0, 0.0)
    v3 = (0.0, 0.0, 16.0)

    attachment_ring = (
        v1,
        v0,
        v3,
    )

    attachment_center = (
        sum(point[0] for point in attachment_ring) / 3.0,
        sum(point[1] for point in attachment_ring) / 3.0,
        sum(point[2] for point in attachment_ring) / 3.0,
    )

    return {
        "triangles": (
            # Open tetrahedron identity surface.
            (v0, v2, v1),
            (v1, v2, v3),
            (v2, v0, v3),

            # Adapter-style centroid-fan closure.
            (v0, v1, attachment_center),
            (v3, v0, attachment_center),
            (v1, v3, attachment_center),
        ),
        "type": "canonical_head_physical_mesh",
        "support_attachment_boundary": {
            "boundary_index": 0,
            "vertex_indices": (1, 0, 3),
            "physical_points": attachment_ring,
            "centroid": attachment_center,
        },
    }


def test_supported_families_match_locked_item11_contract():
    assert (
        AtlasCanonicalHeadPhysicalFamilyBuilder
        .SUPPORTED_REPRESENTATION_KINDS
        == REQUIRED_FAMILIES
    )


@pytest.mark.parametrize(
    "representation_kind",
    REQUIRED_FAMILIES,
)
def test_build_returns_family_scoped_physical_geometry(
    representation_kind,
):
    result = AtlasCanonicalHeadPhysicalFamilyBuilder.build(
        physical_head_mesh=(
            _closed_tetrahedron_physical_mesh()
        ),
        representation_kind=representation_kind,
        target_head_height_mm=40.0,
    )

    assert result["representation_kind"] == representation_kind
    assert result["physical_unit"] == "mm"
    assert result["family_geometry"]["triangles"]
    assert result["family_geometry_kind"]
    assert result["family_builder_provenance"]


def test_four_families_are_not_metadata_aliases_of_one_geometry():
    results = {
        representation_kind: (
            AtlasCanonicalHeadPhysicalFamilyBuilder.build(
                physical_head_mesh=(
                    _closed_tetrahedron_physical_mesh()
                ),
                representation_kind=representation_kind,
                target_head_height_mm=40.0,
            )
        )
        for representation_kind in REQUIRED_FAMILIES
    }

    geometry_kinds = {
        result["family_geometry_kind"]
        for result in results.values()
    }

    assert len(geometry_kinds) == len(REQUIRED_FAMILIES)


def test_relief_reports_explicit_depth_transfer_geometry():
    result = AtlasCanonicalHeadPhysicalFamilyBuilder.build(
        physical_head_mesh=(
            _closed_tetrahedron_physical_mesh()
        ),
        representation_kind="relief",
        target_head_height_mm=40.0,
    )

    assert result["family_geometry_kind"] == "relief"
    assert result["canonical_depth_mm"] > 0.0
    assert result["physical_depth_mm"] >= 0.0
    assert (
        result["physical_depth_mm"]
        < result["canonical_depth_mm"]
    )


def test_bust_has_integral_support_geometry():
    result = AtlasCanonicalHeadPhysicalFamilyBuilder.build(
        physical_head_mesh=(
            _closed_tetrahedron_physical_mesh()
        ),
        representation_kind="bust",
        target_head_height_mm=40.0,
    )

    assert result["family_geometry_kind"] == "bust"
    assert result["support_geometry_kind"] == "pedestal"
    assert result["family_geometry"]["triangles"]


def test_figurine_head_has_attachment_interface_not_pedestal():
    result = AtlasCanonicalHeadPhysicalFamilyBuilder.build(
        physical_head_mesh=(
            _closed_tetrahedron_physical_mesh()
        ),
        representation_kind="figurine_head",
        target_head_height_mm=40.0,
    )

    assert result["family_geometry_kind"] == "figurine_head"
    assert result["support_geometry_kind"] == "attachment_interface"
    assert result["support_geometry_kind"] != "pedestal"


def test_story_kit_component_has_distinct_mounting_carrier():
    result = AtlasCanonicalHeadPhysicalFamilyBuilder.build(
        physical_head_mesh=(
            _closed_tetrahedron_physical_mesh()
        ),
        representation_kind="story_kit_component",
        target_head_height_mm=40.0,
    )

    assert (
        result["family_geometry_kind"]
        == "story_kit_component"
    )
    assert result["support_geometry_kind"] == "kit_mount"


@pytest.mark.parametrize(
    "representation_kind",
    (
        "bust",
        "figurine_head",
        "story_kit_component",
    ),
)
def test_three_dimensional_family_geometry_is_one_integral_closed_body(
    representation_kind,
):
    import numpy as np
    import trimesh

    result = AtlasCanonicalHeadPhysicalFamilyBuilder.build(
        physical_head_mesh=(
            _closed_tetrahedron_physical_mesh()
        ),
        representation_kind=representation_kind,
        target_head_height_mm=40.0,
    )

    triangles = np.asarray(
        result["family_geometry"]["triangles"],
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

    parts = mesh.split(
        only_watertight=False
    )

    assert len(parts) == 1
    assert mesh.is_watertight
    assert mesh.is_winding_consistent
    assert mesh.is_volume
    assert float(mesh.volume) > 0.0


def test_repo_local_real_flame_produces_four_single_volume_family_geometries():
    from pathlib import Path
    import pickle

    import numpy as np
    import trimesh

    from CORE.atlas_canonical_head_physical_mesh_adapter import (
        AtlasCanonicalHeadPhysicalMeshAdapter,
    )

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

    adapter_result = (
        AtlasCanonicalHeadPhysicalMeshAdapter.build(
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
    )

    physical_head_mesh = adapter_result[
        "physical_mesh"
    ]

    attachment = physical_head_mesh[
        "support_attachment_boundary"
    ]

    assert attachment is not None
    assert len(
        attachment["physical_points"]
    ) == 30

    expected = {
        "relief": {
            "geometry_kind": "relief",
            "support_kind": "planar_backing",
            "triangle_count": 7862,
        },
        "bust": {
            "geometry_kind": "bust",
            "support_kind": "pedestal",
            "triangle_count": 7922,
        },
        "figurine_head": {
            "geometry_kind": "figurine_head",
            "support_kind": "attachment_interface",
            "triangle_count": 7922,
        },
        "story_kit_component": {
            "geometry_kind": "story_kit_component",
            "support_kind": "kit_mount",
            "triangle_count": 7922,
        },
    }

    for representation_kind, contract in expected.items():
        result = (
            AtlasCanonicalHeadPhysicalFamilyBuilder.build(
                physical_head_mesh=physical_head_mesh,
                representation_kind=representation_kind,
                target_head_height_mm=40.0,
            )
        )

        triangles = np.asarray(
            result["family_geometry"]["triangles"],
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

        assert (
            result["family_geometry_kind"]
            == contract["geometry_kind"]
        )
        assert (
            result["support_geometry_kind"]
            == contract["support_kind"]
        )
        assert (
            len(triangles)
            == contract["triangle_count"]
        )

        assert len(bodies) == 1
        assert mesh.is_watertight
        assert mesh.is_winding_consistent
        assert mesh.is_volume
        assert float(mesh.volume) > 0.0

        assert (
            result["manufacturability_status"]
            == "UNRESOLVED"
        )

        if representation_kind == "relief":
            vertices = np.asarray(
                mesh.vertices,
                dtype=np.float64,
            )
            faces = np.asarray(
                mesh.faces,
                dtype=np.int64,
            )

            z_min = float(
                vertices[:, 2].min()
            )

            face_z = vertices[
                faces,
                2,
            ]

            planar_back_faces = np.all(
                np.isclose(
                    face_z,
                    z_min,
                    atol=1e-6,
                    rtol=0.0,
                ),
                axis=1,
            )

            planar_back_area = float(
                mesh.area_faces[
                    planar_back_faces
                ].sum()
            )

            xy_bounding_area = float(
                mesh.extents[0]
                * mesh.extents[1]
            )

            assert int(
                planar_back_faces.sum()
            ) > 0

            assert planar_back_area > 0.0

            assert (
                planar_back_area
                / xy_bounding_area
                >= 0.50
            )

    relief = AtlasCanonicalHeadPhysicalFamilyBuilder.build(
        physical_head_mesh=physical_head_mesh,
        representation_kind="relief",
        target_head_height_mm=40.0,
    )

    assert relief["physical_depth_mm"] == pytest.approx(
        relief["canonical_depth_mm"]
        * AtlasCanonicalHeadPhysicalFamilyBuilder.RELIEF_DEPTH_RATIO
    )
    assert (
        relief["physical_depth_mm"]
        < relief["canonical_depth_mm"]
    )


def test_relief_has_integral_planar_backing_surface():
    import numpy as np
    import trimesh

    source = _closed_tetrahedron_physical_mesh()

    def shear_point(point):
        x, y, z = point
        return (
            x,
            y,
            z + 0.10 * x + 0.05 * y,
        )

    sheared_triangles = tuple(
        tuple(
            shear_point(point)
            for point in triangle
        )
        for triangle in source["triangles"]
    )

    source_attachment = source[
        "support_attachment_boundary"
    ]

    sheared_ring = tuple(
        shear_point(point)
        for point in source_attachment[
            "physical_points"
        ]
    )

    sheared_centroid = tuple(
        sum(point[axis] for point in sheared_ring)
        / len(sheared_ring)
        for axis in range(3)
    )

    sheared_source = {
        **source,
        "triangles": sheared_triangles,
        "support_attachment_boundary": {
            **source_attachment,
            "physical_points": sheared_ring,
            "centroid": sheared_centroid,
        },
    }

    result = AtlasCanonicalHeadPhysicalFamilyBuilder.build(
        physical_head_mesh=sheared_source,
        representation_kind="relief",
        target_head_height_mm=40.0,
    )

    triangles = np.asarray(
        result["family_geometry"]["triangles"],
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

    assert len(
        mesh.split(
            only_watertight=False
        )
    ) == 1
    assert mesh.is_watertight
    assert mesh.is_winding_consistent
    assert mesh.is_volume
    assert float(mesh.volume) > 0.0

    vertices = np.asarray(
        mesh.vertices,
        dtype=np.float64,
    )
    faces = np.asarray(
        mesh.faces,
        dtype=np.int64,
    )

    z_min = float(
        vertices[:, 2].min()
    )

    face_z = vertices[
        faces,
        2,
    ]

    planar_back_faces = np.all(
        np.isclose(
            face_z,
            z_min,
            atol=1e-6,
            rtol=0.0,
        ),
        axis=1,
    )

    planar_back_area = float(
        mesh.area_faces[
            planar_back_faces
        ].sum()
    )

    xy_bounding_area = float(
        mesh.extents[0]
        * mesh.extents[1]
    )

    assert int(
        planar_back_faces.sum()
    ) > 0

    assert planar_back_area > 0.0

    assert (
        planar_back_area
        / xy_bounding_area
        >= 0.50
    )

    assert (
        result["support_geometry_kind"]
        == "planar_backing"
    )

    assert (
        result["manufacturability_status"]
        == "UNRESOLVED"
    )
