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
            "triangle_count": None,
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
        if contract["triangle_count"] is None:
            assert len(triangles) > 0
        else:
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
        AtlasCanonicalHeadPhysicalFamilyBuilder.RELIEF_HEIGHT_MM
    )
    assert relief["physical_depth_mm"] == pytest.approx(
        2.0
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


def test_relief_depends_on_frontal_visible_surface_not_rear_head_depth():
    """
    Relief semantics are frontal-visible-surface based.

    Changing geometry hidden behind the same frontal surface
    must not change the produced relief. Relief excursion is
    independently bounded to the physical relief-height
    contract rather than derived as a fraction of full
    canonical head depth.
    """

    def physical_head_mesh(rear_z):
        front_z = 10.0

        return {
            "triangles": (
                # Identical frontal visible surface.
                (
                    (-10.0, 0.0, front_z),
                    (10.0, 0.0, front_z),
                    (0.0, 40.0, front_z),
                ),
                # Fully hidden rear surface. Only its depth
                # changes between the two fixtures.
                (
                    (-10.0, 0.0, rear_z),
                    (0.0, 40.0, rear_z),
                    (10.0, 0.0, rear_z),
                ),
            ),
        }

    near_rear = (
        AtlasCanonicalHeadPhysicalFamilyBuilder.build(
            physical_head_mesh=physical_head_mesh(-10.0),
            representation_kind="relief",
            target_head_height_mm=40.0,
        )
    )

    far_rear = (
        AtlasCanonicalHeadPhysicalFamilyBuilder.build(
            physical_head_mesh=physical_head_mesh(-30.0),
            representation_kind="relief",
            target_head_height_mm=40.0,
        )
    )

    assert (
        near_rear["family_geometry"]["triangles"]
        == far_rear["family_geometry"]["triangles"]
    )

    assert near_rear["physical_depth_mm"] == 2.0
    assert far_rear["physical_depth_mm"] == 2.0


def test_relief_uses_frontal_projection_triangles_when_available():
    """
    Relief generation must use the adapter-provided frontal
    projection payload when present rather than limiting the
    visible-surface raster to the primary physical body.
    """

    primary_triangles = (
        (
            (-10.0, 0.0, 0.0),
            (10.0, 0.0, 0.0),
            (0.0, 40.0, 1.0),
        ),
    )

    frontal_component = (
        (
            (-2.0, 18.0, 5.0),
            (2.0, 18.0, 5.0),
            (0.0, 22.0, 5.0),
        ),
    )

    primary_only = {
        "triangles": primary_triangles,
    }

    with_projection_payload = {
        "triangles": primary_triangles,
        "frontal_projection_triangles": (
            *primary_triangles,
            *frontal_component,
        ),
        "frontal_projection_source_policy": (
            "full_source_without_boundary_closure"
        ),
    }

    baseline = AtlasCanonicalHeadPhysicalFamilyBuilder.build(
        physical_head_mesh=primary_only,
        representation_kind="relief",
        target_head_height_mm=40.0,
    )

    projected = AtlasCanonicalHeadPhysicalFamilyBuilder.build(
        physical_head_mesh=with_projection_payload,
        representation_kind="relief",
        target_head_height_mm=40.0,
    )

    assert (
        baseline["family_geometry"]["triangles"]
        != projected["family_geometry"]["triangles"]
    )

    assert (
        projected["physical_depth_mm"]
        == pytest.approx(2.0)
    )


def _region_aware_relief_fixture():
    import numpy as np

    # 20 x 40 mm frontal surface. With the locked 0.25 mm
    # sample pitch this resolves to 161 x 81 raster samples.
    v00 = (-10.0, 0.0, 0.0)
    v10 = (10.0, 0.0, 1.0)
    v01 = (-10.0, 40.0, 2.0)
    v11 = (10.0, 40.0, 3.0)

    mesh = {
        "triangles": (
            (v00, v10, v11),
            (v00, v11, v01),
        ),
    }

    shape = (161, 81)

    zero = np.zeros(
        shape,
        dtype=np.float64,
    )
    one = np.ones(
        shape,
        dtype=np.float64,
    )

    regions = {
        "eye_glasses": zero.copy(),
        "nose_bridge": zero.copy(),
        "nose_body": zero.copy(),
        "nose_base": zero.copy(),
        "philtrum": zero.copy(),
        "upper_lip": zero.copy(),
        "lower_lip": zero.copy(),
        "left_cheek": zero.copy(),
        "right_cheek": zero.copy(),
        "chin": zero.copy(),
        "face_interior": one,
        "face_boundary_falloff": zero.copy(),
    }

    regions["nose_body"][55:90, 34:47] = 1.0
    regions["nose_base"][88:101, 35:46] = 1.0
    regions["upper_lip"][101:116, 32:49] = 1.0
    regions["lower_lip"][114:128, 31:50] = 1.0
    regions["philtrum"][94:106, 36:45] = 1.0
    regions["chin"][127:148, 29:52] = 1.0

    return mesh, regions


def test_relief_accepts_explicit_raster_region_masks_for_region_aware_depth():
    mesh, regions = _region_aware_relief_fixture()

    result = AtlasCanonicalHeadPhysicalFamilyBuilder.build(
        physical_head_mesh=mesh,
        representation_kind="relief",
        target_head_height_mm=40.0,
        relief_region_masks=regions,
        minimum_printable_separation_mm=0.20,
    )

    assert (
        result["relief_depth_transfer_kind"]
        == "region_aware_bounded_local_depth_allocation"
    )
    assert (
        result["relief_semantic_support"]
        == "raster_region_masks"
    )
    assert (
        result["relief_depth_policy_provenance"]
        == "atlas_canonical_head_region_aware_relief_depth_policy:v1"
    )


def test_region_aware_relief_changes_depth_surface_when_masks_are_supplied():
    mesh, regions = _region_aware_relief_fixture()

    baseline = AtlasCanonicalHeadPhysicalFamilyBuilder.build(
        physical_head_mesh=mesh,
        representation_kind="relief",
        target_head_height_mm=40.0,
    )

    adjusted = AtlasCanonicalHeadPhysicalFamilyBuilder.build(
        physical_head_mesh=mesh,
        representation_kind="relief",
        target_head_height_mm=40.0,
        relief_region_masks=regions,
        minimum_printable_separation_mm=0.20,
    )

    assert (
        adjusted["family_geometry"]["triangles"]
        != baseline["family_geometry"]["triangles"]
    )


def test_region_aware_relief_rejects_masks_not_matching_builder_raster_shape():
    import numpy as np

    mesh, regions = _region_aware_relief_fixture()

    bad_regions = dict(regions)
    bad_regions["nose_body"] = np.zeros(
        (160, 81),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="region|shape|raster",
    ):
        AtlasCanonicalHeadPhysicalFamilyBuilder.build(
            physical_head_mesh=mesh,
            representation_kind="relief",
            target_head_height_mm=40.0,
            relief_region_masks=bad_regions,
            minimum_printable_separation_mm=0.20,
        )


def test_non_relief_families_reject_region_aware_relief_inputs():
    _, regions = _region_aware_relief_fixture()

    with pytest.raises(
        ValueError,
        match="relief",
    ):
        AtlasCanonicalHeadPhysicalFamilyBuilder.build(
            physical_head_mesh=_closed_tetrahedron_physical_mesh(),
            representation_kind="bust",
            target_head_height_mm=40.0,
            relief_region_masks=regions,
            minimum_printable_separation_mm=0.20,
        )


def test_relief_without_region_masks_preserves_existing_depth_path():
    mesh, _ = _region_aware_relief_fixture()

    result = AtlasCanonicalHeadPhysicalFamilyBuilder.build(
        physical_head_mesh=mesh,
        representation_kind="relief",
        target_head_height_mm=40.0,
    )

    assert (
        result["relief_depth_transfer_kind"]
        == "covered_global_linear"
    )
    assert (
        result["relief_semantic_support"]
        == "not_used"
    )

def test_relief_consumes_indexed_projection_surface():
    mesh = _closed_tetrahedron_physical_mesh()

    projection_triangles = mesh["triangles"]
    vertices = tuple(
        point
        for triangle in projection_triangles
        for point in triangle
    )
    faces = tuple(
        (index, index + 1, index + 2)
        for index in range(0, len(vertices), 3)
    )

    mesh = dict(mesh)
    mesh["frontal_projection_triangles"] = (
        projection_triangles
    )
    mesh["frontal_projection_vertices"] = vertices
    mesh["frontal_projection_faces"] = faces

    result = AtlasCanonicalHeadPhysicalFamilyBuilder.build(
        physical_head_mesh=mesh,
        representation_kind="relief",
        target_head_height_mm=40.0,
    )

    assert (
        result["relief_projection_correspondence"]
        == "indexed_visible_surface"
    )
