from __future__ import annotations

import pytest

from CORE.atlas_surface_projection_engine import (
    AtlasSurfaceProjectionEngine,
)
from CORE.atlas_surface_target import AtlasSurfaceTarget


def test_flat_plane_projection_maps_local_xyz_to_uv_and_outward_normal():
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

    source_mesh = {
        "type": "synthetic_relief",
        "triangles": [
            (
                (1.0, 2.0, 0.0),
                (3.0, 2.0, 0.0),
                (1.0, 4.0, 1.0),
            ),
        ],
    }

    result = AtlasSurfaceProjectionEngine.project(
        mesh=source_mesh,
        target=target,
    )

    assert result["projection_mode"] == "flat_plane"
    assert result["surface_id"] == "main_nave_front"
    assert result["source_component_id"] == "portal_arch"
    assert result["target_component_id"] == "main_nave"

    triangle = result["mesh"]["triangles"][0]

    assert triangle[0] == pytest.approx((11.0, 20.0, 7.0))
    assert triangle[1] == pytest.approx((13.0, 20.0, 7.0))
    assert triangle[2] == pytest.approx((11.0, 19.0, 9.0))

    assert result["winding_preserved"] is True
    assert result["clipped_triangle_count"] == 0
    assert result["depth_envelope_violation_count"] == 0


def test_flat_plane_projection_rejects_triangle_outside_clipping_boundary():
    target = AtlasSurfaceTarget.flat_plane(
        surface_id="main_nave_front",
        source_component_id="portal_arch",
        target_component_id="main_nave",
        origin=(0.0, 0.0, 0.0),
        u_axis=(1.0, 0.0, 0.0),
        v_axis=(0.0, 1.0, 0.0),
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

    source_mesh = {
        "type": "synthetic_relief",
        "triangles": [
            (
                (7.0, 2.0, 0.5),
                (9.0, 2.0, 0.5),
                (7.0, 4.0, 0.5),
            ),
        ],
    }

    with pytest.raises(
        ValueError,
        match="outside.*clipping boundary",
    ):
        AtlasSurfaceProjectionEngine.project(
            mesh=source_mesh,
            target=target,
        )


def test_flat_plane_projection_rejects_depth_envelope_violation():
    target = AtlasSurfaceTarget.flat_plane(
        surface_id="main_nave_front",
        source_component_id="portal_arch",
        target_component_id="main_nave",
        origin=(0.0, 0.0, 0.0),
        u_axis=(1.0, 0.0, 0.0),
        v_axis=(0.0, 1.0, 0.0),
        clipping_boundary_uv=(
            (0.0, 0.0),
            (8.0, 0.0),
            (8.0, 12.0),
            (0.0, 12.0),
        ),
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=1.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    source_mesh = {
        "type": "synthetic_relief",
        "triangles": [
            (
                (1.0, 1.0, 0.0),
                (3.0, 1.0, 0.5),
                (1.0, 3.0, 1.4),
            ),
        ],
    }

    with pytest.raises(
        ValueError,
        match="depth envelope",
    ):
        AtlasSurfaceProjectionEngine.project(
            mesh=source_mesh,
            target=target,
        )


def test_flat_plane_projection_rejects_detached_mesh_when_attachment_required():
    target = AtlasSurfaceTarget.flat_plane(
        surface_id="main_nave_front",
        source_component_id="portal_arch",
        target_component_id="main_nave",
        origin=(0.0, 0.0, 0.0),
        u_axis=(1.0, 0.0, 0.0),
        v_axis=(0.0, 1.0, 0.0),
        clipping_boundary_uv=(
            (0.0, 0.0),
            (8.0, 0.0),
            (8.0, 12.0),
            (0.0, 12.0),
        ),
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=2.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    source_mesh = {
        "type": "synthetic_relief",
        "triangles": [
            (
                (1.0, 1.0, 0.5),
                (3.0, 1.0, 0.5),
                (1.0, 3.0, 1.0),
            ),
        ],
    }

    with pytest.raises(
        ValueError,
        match="attachment",
    ):
        AtlasSurfaceProjectionEngine.project(
            mesh=source_mesh,
            target=target,
        )


def test_flat_plane_projection_rejects_duplicate_overlapping_triangles():
    target = AtlasSurfaceTarget.flat_plane(
        surface_id="main_nave_front",
        source_component_id="portal_arch",
        target_component_id="main_nave",
        origin=(0.0, 0.0, 0.0),
        u_axis=(1.0, 0.0, 0.0),
        v_axis=(0.0, 1.0, 0.0),
        clipping_boundary_uv=(
            (0.0, 0.0),
            (8.0, 0.0),
            (8.0, 12.0),
            (0.0, 12.0),
        ),
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=2.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    triangle = (
        (1.0, 1.0, 0.0),
        (3.0, 1.0, 0.0),
        (1.0, 3.0, 0.5),
    )

    source_mesh = {
        "type": "synthetic_relief",
        "triangles": [
            triangle,
            triangle,
        ],
    }

    with pytest.raises(
        ValueError,
        match="self-intersection|overlapping",
    ):
        AtlasSurfaceProjectionEngine.project(
            mesh=source_mesh,
            target=target,
        )


def test_oriented_planar_projection_uses_target_local_frame():
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
        maximum_depth_mm=1.5,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    result = AtlasSurfaceProjectionEngine.project(
        mesh={
            "type": "synthetic_relief",
            "triangles": [
                (
                    (1.0, 2.0, 0.0),
                    (3.0, 2.0, 0.0),
                    (1.0, 4.0, 1.0),
                ),
            ],
        },
        target=target,
    )

    assert result["projection_mode"] == "oriented_planar"
    triangle = result["mesh"]["triangles"][0]
    assert triangle[0] == pytest.approx((3.0, 3.0, 3.0))
    assert triangle[1] == pytest.approx((5.0, 3.0, 3.0))
    assert triangle[2] == pytest.approx((3.0, 2.0, 5.0))


def test_bilinear_surface_projection_interpolates_surface_position():
    target = AtlasSurfaceTarget.bilinear_quad(
        surface_id="warped_panel",
        source_component_id="rosette",
        target_component_id="facade_shell",
        quad=(
            (0.0, 0.0, 0.0),
            (10.0, 0.0, 0.0),
            (10.0, 2.0, 10.0),
            (0.0, 0.0, 10.0),
        ),
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=1.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    result = AtlasSurfaceProjectionEngine.project(
        mesh={
            "type": "synthetic_relief",
            "triangles": [
                (
                    (0.0, 0.0, 0.0),
                    (1.0, 0.0, 0.0),
                    (0.5, 0.5, 0.0),
                ),
            ],
        },
        target=target,
    )

    triangle = result["mesh"]["triangles"][0]

    assert result["projection_mode"] == "bilinear_surface"
    assert triangle[0] == pytest.approx((0.0, 0.0, 0.0))
    assert triangle[1] == pytest.approx((10.0, 0.0, 0.0))
    assert triangle[2] == pytest.approx((5.0, 0.5, 5.0))


def test_cylindrical_surface_projection_maps_angle_axis_and_radial_depth():
    target = AtlasSurfaceTarget.cylindrical_surface(
        surface_id="tower_shell",
        source_component_id="ornament_band",
        target_component_id="tower_body",
        axis_origin=(0.0, 0.0, 0.0),
        axis_direction=(0.0, 0.0, 1.0),
        reference_direction=(1.0, 0.0, 0.0),
        radius_mm=10.0,
        minimum_angle_degrees=0.0,
        maximum_angle_degrees=90.0,
        minimum_axis_mm=0.0,
        maximum_axis_mm=20.0,
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=2.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    result = AtlasSurfaceProjectionEngine.project(
        mesh={
            "type": "synthetic_relief",
            "triangles": [
                (
                    (0.0, 2.0, 0.0),
                    (90.0, 2.0, 0.0),
                    (45.0, 4.0, 1.0),
                ),
            ],
        },
        target=target,
    )

    triangle = result["mesh"]["triangles"][0]

    assert result["projection_mode"] == "cylindrical_surface"
    assert triangle[0] == pytest.approx((10.0, 0.0, 2.0))
    assert triangle[1] == pytest.approx((0.0, 10.0, 2.0), abs=1e-9)

    radial = 11.0 / (2.0 ** 0.5)
    assert triangle[2] == pytest.approx((radial, radial, 4.0))


def test_dome_surface_projection_maps_azimuth_polar_and_radial_depth():
    target = AtlasSurfaceTarget.dome_surface(
        surface_id="central_dome",
        source_component_id="dome_ornament",
        target_component_id="dome_shell",
        center=(0.0, 0.0, 0.0),
        axis_direction=(0.0, 0.0, 1.0),
        reference_direction=(1.0, 0.0, 0.0),
        radius_mm=10.0,
        minimum_polar_degrees=0.0,
        maximum_polar_degrees=90.0,
        minimum_azimuth_degrees=0.0,
        maximum_azimuth_degrees=90.0,
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=2.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    result = AtlasSurfaceProjectionEngine.project(
        mesh={
            "type": "synthetic_relief",
            "triangles": [
                (
                    (0.0, 0.0, 0.0),
                    (0.0, 90.0, 0.0),
                    (90.0, 90.0, 1.0),
                ),
            ],
        },
        target=target,
    )

    triangle = result["mesh"]["triangles"][0]

    assert result["projection_mode"] == "dome_surface"
    assert triangle[0] == pytest.approx((0.0, 0.0, 10.0), abs=1e-9)
    assert triangle[1] == pytest.approx((10.0, 0.0, 0.0), abs=1e-9)
    assert triangle[2] == pytest.approx((0.0, 11.0, 0.0), abs=1e-9)


def test_vault_surface_projection_maps_angle_axis_and_radial_depth():
    target = AtlasSurfaceTarget.vault_surface(
        surface_id="nave_vault",
        source_component_id="vault_ornament",
        target_component_id="vault_shell",
        axis_origin=(0.0, 0.0, 0.0),
        axis_direction=(0.0, 1.0, 0.0),
        reference_direction=(1.0, 0.0, 0.0),
        radius_mm=8.0,
        minimum_angle_degrees=0.0,
        maximum_angle_degrees=180.0,
        minimum_axis_mm=0.0,
        maximum_axis_mm=20.0,
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=2.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    result = AtlasSurfaceProjectionEngine.project(
        mesh={
            "type": "synthetic_relief",
            "triangles": [
                (
                    (0.0, 2.0, 0.0),
                    (90.0, 2.0, 0.0),
                    (180.0, 4.0, 1.0),
                ),
            ],
        },
        target=target,
    )

    triangle = result["mesh"]["triangles"][0]

    assert result["projection_mode"] == "vault_surface"
    assert triangle[0] == pytest.approx((8.0, 2.0, 0.0), abs=1e-9)
    assert triangle[1] == pytest.approx((0.0, 2.0, -8.0), abs=1e-9)
    assert triangle[2] == pytest.approx((-9.0, 4.0, 0.0), abs=1e-9)


def test_indexed_mesh_surface_projection_uses_uv_barycentric_mapping():
    target = AtlasSurfaceTarget.indexed_mesh_surface(
        surface_id="irregular_shell",
        source_component_id="ornament_patch",
        target_component_id="shell",
        vertices=(
            (0.0, 0.0, 0.0),
            (10.0, 0.0, 0.0),
            (10.0, 10.0, 2.0),
            (0.0, 10.0, 0.0),
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

    result = AtlasSurfaceProjectionEngine.project(
        mesh={
            "type": "synthetic_relief",
            "triangles": [
                (
                    (0.0, 0.0, 0.0),
                    (1.0, 0.0, 0.0),
                    (0.5, 0.5, 0.0),
                ),
            ],
        },
        target=target,
    )

    triangle = result["mesh"]["triangles"][0]

    assert result["projection_mode"] == "indexed_mesh_surface"
    assert triangle[0] == pytest.approx((0.0, 0.0, 0.0))
    assert triangle[1] == pytest.approx((10.0, 0.0, 0.0))
    assert triangle[2] == pytest.approx((5.0, 5.0, 1.0))


def test_flat_plane_inward_polarity_projects_depth_against_outward_normal():
    target = AtlasSurfaceTarget.flat_plane(
        surface_id="recessed_panel",
        source_component_id="engraving",
        target_component_id="wall",
        origin=(0.0, 0.0, 0.0),
        u_axis=(1.0, 0.0, 0.0),
        v_axis=(0.0, 1.0, 0.0),
        clipping_boundary_uv=(
            (0.0, 0.0),
            (10.0, 0.0),
            (10.0, 10.0),
            (0.0, 10.0),
        ),
        relief_polarity="inward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=2.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    result = AtlasSurfaceProjectionEngine.project(
        mesh={
            "type": "synthetic_relief",
            "triangles": [
                (
                    (1.0, 1.0, 0.0),
                    (3.0, 1.0, 0.0),
                    (1.0, 3.0, 1.0),
                ),
            ],
        },
        target=target,
    )

    triangle = result["mesh"]["triangles"][0]

    assert triangle[0] == pytest.approx((1.0, 1.0, 0.0))
    assert triangle[1] == pytest.approx((3.0, 1.0, 0.0))
    assert triangle[2] == pytest.approx((1.0, 3.0, -1.0))


def test_bilinear_surface_inward_polarity_projects_against_local_normal():
    target = AtlasSurfaceTarget.bilinear_quad(
        surface_id="warped_recess",
        source_component_id="engraving",
        target_component_id="panel",
        quad=(
            (0.0, 0.0, 0.0),
            (10.0, 0.0, 0.0),
            (10.0, 0.0, 10.0),
            (0.0, 0.0, 10.0),
        ),
        relief_polarity="inward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=2.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    result = AtlasSurfaceProjectionEngine.project(
        mesh={
            "type": "synthetic_relief",
            "triangles": [
                (
                    (0.0, 0.0, 0.0),
                    (1.0, 0.0, 0.0),
                    (0.5, 0.5, 1.0),
                ),
            ],
        },
        target=target,
    )

    triangle = result["mesh"]["triangles"][0]

    assert triangle[0] == pytest.approx((0.0, 0.0, 0.0))
    assert triangle[1] == pytest.approx((10.0, 0.0, 0.0))
    assert triangle[2] == pytest.approx((5.0, 1.0, 5.0))


def test_projection_reports_audited_winding_preservation():
    target = AtlasSurfaceTarget.flat_plane(
        surface_id="winding_wall",
        source_component_id="relief",
        target_component_id="wall",
        origin=(5.0, 7.0, 2.0),
        u_axis=(1.0, 0.0, 0.0),
        v_axis=(0.0, 1.0, 0.0),
        clipping_boundary_uv=(
            (0.0, 0.0),
            (10.0, 0.0),
            (10.0, 10.0),
            (0.0, 10.0),
        ),
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=2.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    result = AtlasSurfaceProjectionEngine.project(
        mesh={
            "type": "synthetic_relief",
            "triangles": [
                (
                    (1.0, 1.0, 0.0),
                    (4.0, 1.0, 0.0),
                    (1.0, 4.0, 1.0),
                ),
            ],
        },
        target=target,
    )

    assert result["winding_preserved"] is True
    assert result["winding_audited"] is True
    assert result["winding_violation_count"] == 0


def test_cylindrical_surface_reports_audited_winding_preservation():
    target = AtlasSurfaceTarget.cylindrical_surface(
        surface_id="tower_winding",
        source_component_id="ornament",
        target_component_id="tower",
        axis_origin=(0.0, 0.0, 0.0),
        axis_direction=(0.0, 0.0, 1.0),
        reference_direction=(1.0, 0.0, 0.0),
        radius_mm=10.0,
        minimum_angle_degrees=0.0,
        maximum_angle_degrees=90.0,
        minimum_axis_mm=0.0,
        maximum_axis_mm=20.0,
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=1.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    result = AtlasSurfaceProjectionEngine.project(
        mesh={
            "type": "synthetic_relief",
            "triangles": [
                (
                    (0.0, 2.0, 0.0),
                    (30.0, 2.0, 0.0),
                    (0.0, 6.0, 0.0),
                ),
            ],
        },
        target=target,
    )

    assert result["winding_audited"] is True
    assert result["winding_preserved"] is True
    assert result["winding_violation_count"] == 0


def test_vault_surface_reports_audited_winding_preservation():
    target = AtlasSurfaceTarget.vault_surface(
        surface_id="vault_winding",
        source_component_id="ornament",
        target_component_id="vault",
        axis_origin=(0.0, 0.0, 0.0),
        axis_direction=(0.0, 1.0, 0.0),
        reference_direction=(1.0, 0.0, 0.0),
        radius_mm=8.0,
        minimum_angle_degrees=0.0,
        maximum_angle_degrees=180.0,
        minimum_axis_mm=0.0,
        maximum_axis_mm=20.0,
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=1.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    result = AtlasSurfaceProjectionEngine.project(
        mesh={
            "type": "synthetic_relief",
            "triangles": [
                (
                    (0.0, 2.0, 0.0),
                    (30.0, 2.0, 0.0),
                    (0.0, 6.0, 0.0),
                ),
            ],
        },
        target=target,
    )

    assert result["winding_audited"] is True
    assert result["winding_preserved"] is True
    assert result["winding_violation_count"] == 0


def test_dome_surface_reports_audited_winding_preservation():
    target = AtlasSurfaceTarget.dome_surface(
        surface_id="dome_winding",
        source_component_id="ornament",
        target_component_id="dome",
        center=(0.0, 0.0, 0.0),
        axis_direction=(0.0, 0.0, 1.0),
        reference_direction=(1.0, 0.0, 0.0),
        radius_mm=10.0,
        minimum_polar_degrees=0.0,
        maximum_polar_degrees=90.0,
        minimum_azimuth_degrees=0.0,
        maximum_azimuth_degrees=90.0,
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=1.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    result = AtlasSurfaceProjectionEngine.project(
        mesh={
            "type": "synthetic_relief",
            "triangles": [
                (
                    (0.0, 30.0, 0.0),
                    (30.0, 30.0, 0.0),
                    (0.0, 60.0, 0.0),
                ),
            ],
        },
        target=target,
    )

    assert result["winding_audited"] is True
    assert result["winding_preserved"] is True
    assert result["winding_violation_count"] == 0


def test_bilinear_surface_reports_audited_winding_preservation():
    target = AtlasSurfaceTarget.bilinear_quad(
        surface_id="bilinear_winding",
        source_component_id="ornament",
        target_component_id="panel",
        quad=(
            (0.0, 0.0, 0.0),
            (10.0, 0.0, 0.0),
            (10.0, 2.0, 10.0),
            (0.0, 0.0, 10.0),
        ),
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=1.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    result = AtlasSurfaceProjectionEngine.project(
        mesh={
            "type": "synthetic_relief",
            "triangles": [
                (
                    (0.1, 0.1, 0.0),
                    (0.8, 0.1, 0.0),
                    (0.1, 0.8, 0.0),
                ),
            ],
        },
        target=target,
    )

    assert result["winding_audited"] is True
    assert result["winding_preserved"] is True
    assert result["winding_violation_count"] == 0


def test_indexed_mesh_surface_reports_audited_winding_preservation():
    target = AtlasSurfaceTarget.indexed_mesh_surface(
        surface_id="indexed_winding",
        source_component_id="ornament",
        target_component_id="shell",
        vertices=(
            (0.0, 0.0, 0.0),
            (10.0, 0.0, 0.0),
            (10.0, 10.0, 2.0),
            (0.0, 10.0, 0.0),
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

    result = AtlasSurfaceProjectionEngine.project(
        mesh={
            "type": "synthetic_relief",
            "triangles": [
                (
                    (0.1, 0.1, 0.0),
                    (0.8, 0.1, 0.0),
                    (0.8, 0.8, 0.0),
                ),
            ],
        },
        target=target,
    )

    assert result["winding_audited"] is True
    assert result["winding_preserved"] is True
    assert result["winding_violation_count"] == 0


def test_oriented_planar_projection_preserves_valid_tangent_side_faces_of_closed_solid():
    target = AtlasSurfaceTarget.oriented_planar_quad(
        surface_id="closed_relief_target",
        source_component_id="closed_relief",
        target_component_id="facade",
        quad=(
            (0.0, 0.0, 0.0),
            (10.0, 0.0, 0.0),
            (10.0, 0.0, 10.0),
            (0.0, 0.0, 10.0),
        ),
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=1.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    # One valid side face of a closed relief solid.
    # Its UV projection is a line, but it has real area in UV-depth space.
    side_face = {
        "type": "closed_relief_side",
        "triangles": [
            (
                (2.0, 2.0, 0.0),
                (2.0, 2.0, 0.8),
                (2.0, 6.0, 0.8),
            ),
            (
                (2.0, 2.0, 0.0),
                (2.0, 6.0, 0.8),
                (2.0, 6.0, 0.0),
            ),
        ],
    }

    result = AtlasSurfaceProjectionEngine.project(
        mesh=side_face,
        target=target,
    )

    assert result["winding_audited"] is True
    assert result["winding_preserved"] is True
    assert result["winding_violation_count"] == 0
