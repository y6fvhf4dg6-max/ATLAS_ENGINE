from __future__ import annotations

import pytest

from CORE.atlas_surface_target import AtlasSurfaceTarget


def test_flat_plane_target_preserves_canonical_surface_contract():
    target = AtlasSurfaceTarget.flat_plane(
        surface_id="main_nave_front",
        source_component_id="portal_arch",
        target_component_id="main_nave",
        origin=(10.0, 20.0, 5.0),
        u_axis=(1.0, 0.0, 0.0),
        v_axis=(0.0, 0.0, 1.0),
        clipping_boundary_uv=(
            (0.0, 0.0),
            (8.0, 0.0),
            (8.0, 12.0),
            (0.0, 12.0),
        ),
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=2.5,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    assert target.surface_id == "main_nave_front"
    assert target.surface_kind == "flat_plane"
    assert target.projection_mode == "flat_plane"

    assert target.source_component_id == "portal_arch"
    assert target.target_component_id == "main_nave"

    assert target.origin == pytest.approx((10.0, 20.0, 5.0))
    assert target.u_axis == pytest.approx((1.0, 0.0, 0.0))
    assert target.v_axis == pytest.approx((0.0, 0.0, 1.0))
    assert target.outward_normal == pytest.approx((0.0, -1.0, 0.0))

    assert target.clipping_boundary_uv == (
        (0.0, 0.0),
        (8.0, 0.0),
        (8.0, 12.0),
        (0.0, 12.0),
    )

    assert target.relief_polarity == "outward"
    assert target.minimum_depth_mm == pytest.approx(0.0)
    assert target.maximum_depth_mm == pytest.approx(2.5)
    assert target.attachment_policy == "must_attach"
    assert target.intersection_policy == "reject"


def test_oriented_planar_quad_derives_stable_local_frame_and_boundary():
    target = AtlasSurfaceTarget.oriented_planar_quad(
        surface_id="apse_front",
        source_component_id="inscription",
        target_component_id="apse_wall",
        quad=(
            (2.0, 3.0, 1.0),
            (8.0, 3.0, 1.0),
            (8.0, 3.0, 9.0),
            (2.0, 3.0, 9.0),
        ),
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=1.8,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    assert target.surface_kind == "oriented_planar_quad"
    assert target.projection_mode == "oriented_planar"
    assert target.origin == pytest.approx((2.0, 3.0, 1.0))
    assert target.u_axis == pytest.approx((1.0, 0.0, 0.0))
    assert target.v_axis == pytest.approx((0.0, 0.0, 1.0))
    assert target.outward_normal == pytest.approx((0.0, -1.0, 0.0))
    assert target.clipping_boundary_uv == (
        (0.0, 0.0),
        (6.0, 0.0),
        (6.0, 8.0),
        (0.0, 8.0),
    )


def test_bilinear_quad_target_preserves_four_corner_surface_definition():
    target = AtlasSurfaceTarget.bilinear_quad(
        surface_id="warped_facade_panel",
        source_component_id="rosette",
        target_component_id="facade_shell",
        quad=(
            (0.0, 0.0, 0.0),
            (8.0, 0.0, 0.5),
            (8.0, 1.0, 10.0),
            (0.0, 0.0, 9.0),
        ),
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=1.2,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    assert target.surface_kind == "bilinear_quad"
    assert target.projection_mode == "bilinear_surface"
    assert target.surface_points == (
        (0.0, 0.0, 0.0),
        (8.0, 0.0, 0.5),
        (8.0, 1.0, 10.0),
        (0.0, 0.0, 9.0),
    )
    assert target.origin == pytest.approx((0.0, 0.0, 0.0))
    assert target.clipping_boundary_uv == (
        (0.0, 0.0),
        (1.0, 0.0),
        (1.0, 1.0),
        (0.0, 1.0),
    )


def test_cylindrical_surface_target_preserves_axis_radius_and_angular_clip():
    target = AtlasSurfaceTarget.cylindrical_surface(
        surface_id="tower_gallery_outer",
        source_component_id="arch_niche",
        target_component_id="tower_gallery",
        axis_origin=(0.0, 0.0, 2.0),
        axis_direction=(0.0, 0.0, 1.0),
        reference_direction=(1.0, 0.0, 0.0),
        radius_mm=6.0,
        minimum_angle_degrees=-45.0,
        maximum_angle_degrees=45.0,
        minimum_axis_mm=0.0,
        maximum_axis_mm=8.0,
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=1.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    assert target.surface_kind == "cylindrical_surface"
    assert target.projection_mode == "cylindrical_surface"
    assert target.origin == pytest.approx((0.0, 0.0, 2.0))
    assert target.u_axis == pytest.approx((1.0, 0.0, 0.0))
    assert target.v_axis == pytest.approx((0.0, 0.0, 1.0))
    assert target.radius_mm == pytest.approx(6.0)
    assert target.minimum_angle_degrees == pytest.approx(-45.0)
    assert target.maximum_angle_degrees == pytest.approx(45.0)
    assert target.minimum_axis_mm == pytest.approx(0.0)
    assert target.maximum_axis_mm == pytest.approx(8.0)


def test_dome_surface_target_preserves_center_radius_cap_and_frame():
    target = AtlasSurfaceTarget.dome_surface(
        surface_id="main_dome_outer",
        source_component_id="medallion",
        target_component_id="main_dome",
        center=(0.0, 0.0, 10.0),
        axis_direction=(0.0, 0.0, 1.0),
        reference_direction=(1.0, 0.0, 0.0),
        radius_mm=8.0,
        minimum_polar_degrees=0.0,
        maximum_polar_degrees=60.0,
        minimum_azimuth_degrees=-90.0,
        maximum_azimuth_degrees=90.0,
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=1.2,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    assert target.surface_kind == "dome_surface"
    assert target.projection_mode == "dome_surface"
    assert target.origin == pytest.approx((0.0, 0.0, 10.0))
    assert target.u_axis == pytest.approx((1.0, 0.0, 0.0))
    assert target.v_axis == pytest.approx((0.0, 0.0, 1.0))
    assert target.radius_mm == pytest.approx(8.0)
    assert target.minimum_polar_degrees == pytest.approx(0.0)
    assert target.maximum_polar_degrees == pytest.approx(60.0)
    assert target.minimum_azimuth_degrees == pytest.approx(-90.0)
    assert target.maximum_azimuth_degrees == pytest.approx(90.0)


def test_vault_surface_target_preserves_axis_radius_span_and_clip():
    target = AtlasSurfaceTarget.vault_surface(
        surface_id="nave_vault_inner",
        source_component_id="ceiling_ornament",
        target_component_id="nave_vault",
        axis_origin=(0.0, 0.0, 6.0),
        axis_direction=(0.0, 1.0, 0.0),
        reference_direction=(1.0, 0.0, 0.0),
        radius_mm=5.0,
        minimum_angle_degrees=0.0,
        maximum_angle_degrees=180.0,
        minimum_axis_mm=0.0,
        maximum_axis_mm=12.0,
        relief_polarity="inward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=1.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    assert target.surface_kind == "vault_surface"
    assert target.projection_mode == "vault_surface"
    assert target.origin == pytest.approx((0.0, 0.0, 6.0))
    assert target.u_axis == pytest.approx((1.0, 0.0, 0.0))
    assert target.v_axis == pytest.approx((0.0, 1.0, 0.0))
    assert target.radius_mm == pytest.approx(5.0)
    assert target.minimum_angle_degrees == pytest.approx(0.0)
    assert target.maximum_angle_degrees == pytest.approx(180.0)
    assert target.minimum_axis_mm == pytest.approx(0.0)
    assert target.maximum_axis_mm == pytest.approx(12.0)
    assert target.relief_polarity == "inward"


def test_indexed_mesh_surface_target_preserves_vertices_faces_and_boundary():
    target = AtlasSurfaceTarget.indexed_mesh_surface(
        surface_id="sculpted_wall_patch",
        source_component_id="figurative_plaque",
        target_component_id="historic_wall",
        vertices=(
            (0.0, 0.0, 0.0),
            (4.0, 0.0, 0.2),
            (4.0, 3.0, 0.5),
            (0.0, 3.0, 0.1),
        ),
        faces=(
            (0, 1, 2),
            (0, 2, 3),
        ),
        clipping_vertex_indices=(0, 1, 2, 3),
        vertex_uvs=(
            (0.0, 0.0),
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0),
        ),
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=1.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    assert target.surface_kind == "indexed_mesh_surface"
    assert target.projection_mode == "indexed_mesh_surface"
    assert target.surface_points == (
        (0.0, 0.0, 0.0),
        (4.0, 0.0, 0.2),
        (4.0, 3.0, 0.5),
        (0.0, 3.0, 0.1),
    )
    assert target.surface_faces == (
        (0, 1, 2),
        (0, 2, 3),
    )
    assert target.clipping_vertex_indices == (0, 1, 2, 3)
    assert target.vertex_uvs == (
        (0.0, 0.0),
        (1.0, 0.0),
        (1.0, 1.0),
        (0.0, 1.0),
    )


def test_indexed_mesh_surface_requires_explicit_vertex_uvs():
    with pytest.raises(
        TypeError,
        match="vertex_uvs",
    ):
        AtlasSurfaceTarget.indexed_mesh_surface(
            surface_id="irregular_shell",
            source_component_id="ornament_patch",
            target_component_id="shell",
            vertices=(
                (0.0, 0.0, 0.0),
                (10.0, 0.0, 0.0),
                (10.0, 10.0, 1.0),
                (0.0, 10.0, 0.0),
            ),
            faces=(
                (0, 1, 2),
                (0, 2, 3),
            ),
            clipping_vertex_indices=(0, 1, 2, 3),
            relief_polarity="outward",
            minimum_depth_mm=0.0,
            maximum_depth_mm=2.0,
            attachment_policy="must_attach",
            intersection_policy="reject",
        )
