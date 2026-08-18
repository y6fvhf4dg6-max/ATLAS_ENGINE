from __future__ import annotations

from copy import deepcopy
import math

from CORE.atlas_surface_target import (
    AtlasSurfaceTarget,
)


def _point3(value, *, field_name):
    if isinstance(value, (str, bytes)):
        raise ValueError(
            f"{field_name} must contain exactly three numeric values"
        )

    try:
        point = tuple(value)
    except TypeError as exc:
        raise ValueError(
            f"{field_name} must contain exactly three numeric values"
        ) from exc

    if len(point) != 3:
        raise ValueError(
            f"{field_name} must contain exactly three numeric values"
        )

    normalized = []

    for coordinate in point:
        if isinstance(coordinate, bool):
            raise ValueError(
                f"{field_name} coordinates must be numeric"
            )

        try:
            numeric = float(coordinate)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{field_name} coordinates must be numeric"
            ) from exc

        if not math.isfinite(numeric):
            raise ValueError(
                f"{field_name} coordinates must be finite"
            )

        normalized.append(numeric)

    return tuple(normalized)


def _point_in_polygon_2d(point, polygon):
    x, y = point
    inside = False
    count = len(polygon)

    for index in range(count):
        x1, y1 = polygon[index]
        x2, y2 = polygon[(index + 1) % count]

        if (
            min(y1, y2) <= y <= max(y1, y2)
            and abs(y2 - y1) <= 1e-12
            and min(x1, x2) <= x <= max(x1, x2)
        ):
            return True

        if (
            min(x1, x2) <= x <= max(x1, x2)
            and abs(x2 - x1) <= 1e-12
            and min(y1, y2) <= y <= max(y1, y2)
        ):
            return True

        intersects = (
            (y1 > y) != (y2 > y)
        )

        if intersects:
            crossing_x = (
                (x2 - x1)
                * (y - y1)
                / (y2 - y1)
                + x1
            )

            if abs(crossing_x - x) <= 1e-12:
                return True

            if crossing_x > x:
                inside = not inside

    return inside


def _barycentric_weights_2d(point, a, b, c):
    px, py = point
    ax, ay = a
    bx, by = b
    cx, cy = c

    denominator = (
        (by - cy) * (ax - cx)
        + (cx - bx) * (ay - cy)
    )

    if abs(denominator) <= 1e-12:
        return None

    wa = (
        (by - cy) * (px - cx)
        + (cx - bx) * (py - cy)
    ) / denominator

    wb = (
        (cy - ay) * (px - cx)
        + (ax - cx) * (py - cy)
    ) / denominator

    wc = 1.0 - wa - wb

    tolerance = 1e-9
    if (
        wa < -tolerance
        or wb < -tolerance
        or wc < -tolerance
    ):
        return None

    return (wa, wb, wc)


def _normalized_triangle_normal(a, b, c):
    ab = (
        b[0] - a[0],
        b[1] - a[1],
        b[2] - a[2],
    )
    ac = (
        c[0] - a[0],
        c[1] - a[1],
        c[2] - a[2],
    )

    normal = (
        ab[1] * ac[2] - ab[2] * ac[1],
        ab[2] * ac[0] - ab[0] * ac[2],
        ab[0] * ac[1] - ab[1] * ac[0],
    )

    length = math.sqrt(
        sum(value * value for value in normal)
    )

    if length <= 1e-12:
        raise ValueError(
            "indexed mesh surface face is degenerate"
        )

    return tuple(
        value / length
        for value in normal
    )


def _uv_winding_sign(triangle):
    a, b, c = triangle
    signed_area_twice = (
        (b[0] - a[0]) * (c[1] - a[1])
        - (b[1] - a[1]) * (c[0] - a[0])
    )

    if abs(signed_area_twice) <= 1e-12:
        return 0

    return 1 if signed_area_twice > 0.0 else -1


def _cylindrical_reference_normal(
    target,
    local_triangle,
):
    mean_angle_degrees = sum(
        point[0]
        for point in local_triangle
    ) / len(local_triangle)

    angle_radians = math.radians(
        mean_angle_degrees
    )

    axis = target.v_axis
    reference = target.u_axis

    tangent = (
        axis[1] * reference[2]
        - axis[2] * reference[1],
        axis[2] * reference[0]
        - axis[0] * reference[2],
        axis[0] * reference[1]
        - axis[1] * reference[0],
    )

    tangent_length = math.sqrt(
        sum(value * value for value in tangent)
    )

    if tangent_length <= 1e-12:
        raise ValueError(
            "cylindrical winding frame is degenerate"
        )

    tangent = tuple(
        value / tangent_length
        for value in tangent
    )

    return tuple(
        (
            math.cos(angle_radians)
            * reference[index]
            + math.sin(angle_radians)
            * tangent[index]
        )
        for index in range(3)
    )


def _dome_winding_reference_normal(
    target,
    local_triangle,
):
    mean_azimuth_degrees = sum(
        point[0]
        for point in local_triangle
    ) / len(local_triangle)
    mean_polar_degrees = sum(
        point[1]
        for point in local_triangle
    ) / len(local_triangle)

    azimuth = math.radians(
        mean_azimuth_degrees
    )
    polar = math.radians(
        mean_polar_degrees
    )

    axis = target.v_axis
    reference = target.u_axis

    tangent = (
        axis[1] * reference[2]
        - axis[2] * reference[1],
        axis[2] * reference[0]
        - axis[0] * reference[2],
        axis[0] * reference[1]
        - axis[1] * reference[0],
    )

    tangent_length = math.sqrt(
        sum(value * value for value in tangent)
    )

    if tangent_length <= 1e-12:
        raise ValueError(
            "dome winding frame is degenerate"
        )

    tangent = tuple(
        value / tangent_length
        for value in tangent
    )

    equatorial = tuple(
        (
            math.cos(azimuth) * reference[index]
            + math.sin(azimuth) * tangent[index]
        )
        for index in range(3)
    )

    d_azimuth = tuple(
        math.sin(polar)
        * (
            -math.sin(azimuth) * reference[index]
            + math.cos(azimuth) * tangent[index]
        )
        for index in range(3)
    )

    d_polar = tuple(
        (
            -math.sin(polar) * axis[index]
            + math.cos(polar) * equatorial[index]
        )
        for index in range(3)
    )

    normal = (
        d_azimuth[1] * d_polar[2]
        - d_azimuth[2] * d_polar[1],
        d_azimuth[2] * d_polar[0]
        - d_azimuth[0] * d_polar[2],
        d_azimuth[0] * d_polar[1]
        - d_azimuth[1] * d_polar[0],
    )

    length = math.sqrt(
        sum(value * value for value in normal)
    )

    if length <= 1e-12:
        raise ValueError(
            "dome winding reference is degenerate"
        )

    return tuple(
        value / length
        for value in normal
    )


def _bilinear_winding_reference_normal(
    target,
    local_triangle,
):
    mean_u = sum(
        point[0]
        for point in local_triangle
    ) / len(local_triangle)
    mean_v = sum(
        point[1]
        for point in local_triangle
    ) / len(local_triangle)

    p00, p10, p11, p01 = target.surface_points

    du = tuple(
        (
            (1.0 - mean_v) * (p10[axis] - p00[axis])
            + mean_v * (p11[axis] - p01[axis])
        )
        for axis in range(3)
    )

    dv = tuple(
        (
            (1.0 - mean_u) * (p01[axis] - p00[axis])
            + mean_u * (p11[axis] - p10[axis])
        )
        for axis in range(3)
    )

    normal = (
        du[1] * dv[2] - du[2] * dv[1],
        du[2] * dv[0] - du[0] * dv[2],
        du[0] * dv[1] - du[1] * dv[0],
    )

    length = math.sqrt(
        sum(value * value for value in normal)
    )

    if length <= 1e-12:
        raise ValueError(
            "bilinear winding reference is degenerate"
        )

    return tuple(
        value / length
        for value in normal
    )


def _indexed_mesh_winding_reference_normal(
    target,
    local_triangle,
):
    centroid_uv = (
        sum(point[0] for point in local_triangle) / len(local_triangle),
        sum(point[1] for point in local_triangle) / len(local_triangle),
    )

    for face in target.surface_faces:
        uv_a = target.vertex_uvs[face[0]]
        uv_b = target.vertex_uvs[face[1]]
        uv_c = target.vertex_uvs[face[2]]

        weights = _barycentric_weights_2d(
            centroid_uv,
            uv_a,
            uv_b,
            uv_c,
        )

        if weights is None:
            continue

        a = target.surface_points[face[0]]
        b = target.surface_points[face[1]]
        c = target.surface_points[face[2]]

        return _normalized_triangle_normal(
            a,
            b,
            c,
        )

    raise ValueError(
        "indexed mesh winding centroid lies outside UV surface"
    )


def _projected_winding_sign(
    triangle,
    *,
    reference_normal,
):
    a, b, c = triangle

    ab = (
        b[0] - a[0],
        b[1] - a[1],
        b[2] - a[2],
    )
    ac = (
        c[0] - a[0],
        c[1] - a[1],
        c[2] - a[2],
    )

    normal = (
        ab[1] * ac[2] - ab[2] * ac[1],
        ab[2] * ac[0] - ab[0] * ac[2],
        ab[0] * ac[1] - ab[1] * ac[0],
    )

    orientation = sum(
        value * reference
        for value, reference in zip(
            normal,
            reference_normal,
            strict=True,
        )
    )

    if abs(orientation) <= 1e-12:
        return 0

    return 1 if orientation > 0.0 else -1


class AtlasSurfaceProjectionEngine:
    @classmethod
    def project(
        cls,
        *,
        mesh,
        target,
    ):
        if not isinstance(
            target,
            AtlasSurfaceTarget,
        ):
            raise TypeError(
                "target must be an AtlasSurfaceTarget"
            )

        if target.projection_mode not in {
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
            "cylindrical_surface",
            "dome_surface",
            "vault_surface",
            "indexed_mesh_surface",
        }:
            raise NotImplementedError(
                "projection mode is not implemented: "
                f"{target.projection_mode}"
            )

        if not isinstance(mesh, dict):
            raise TypeError(
                "mesh must be a dictionary"
            )

        if "triangles" not in mesh:
            raise ValueError(
                "mesh must contain triangles"
            )

        projected = deepcopy(mesh)
        projected_triangles = []
        attachment_found = False
        seen_triangle_keys = set()
        winding_violation_count = 0
        winding_audited = target.projection_mode in {
            "flat_plane",
            "oriented_planar",
            "cylindrical_surface",
            "vault_surface",
            "dome_surface",
            "bilinear_surface",
            "indexed_mesh_surface",
        }

        if target.relief_polarity == "outward":
            depth_sign = 1.0
        elif target.relief_polarity == "inward":
            depth_sign = -1.0
        else:
            raise ValueError(
                "unsupported relief polarity: "
                f"{target.relief_polarity}"
            )

        for triangle in mesh["triangles"]:
            try:
                triangle = tuple(triangle)
            except TypeError as exc:
                raise ValueError(
                    "each triangle must contain exactly three points"
                ) from exc

            if len(triangle) != 3:
                raise ValueError(
                    "each triangle must contain exactly three points"
                )

            local_points = tuple(
                _point3(
                    raw_point,
                    field_name="triangle point",
                )
                for raw_point in triangle
            )

            triangle_key = tuple(
                sorted(local_points)
            )

            if triangle_key in seen_triangle_keys:
                raise ValueError(
                    "mesh contains overlapping duplicate triangles"
                )

            seen_triangle_keys.add(
                triangle_key
            )

            if any(
                not _point_in_polygon_2d(
                    (point[0], point[1]),
                    target.clipping_boundary_uv,
                )
                for point in local_points
            ):
                raise ValueError(
                    "triangle lies outside target clipping boundary"
                )

            if any(
                point[2] < target.minimum_depth_mm
                or point[2] > target.maximum_depth_mm
                for point in local_points
            ):
                raise ValueError(
                    "triangle violates target depth envelope"
                )

            if any(
                abs(
                    point[2]
                    - target.minimum_depth_mm
                ) <= 1e-9
                for point in local_points
            ):
                attachment_found = True

            projected_triangle = []

            for raw_point in local_points:
                local_x, local_y, local_z = raw_point

                if target.projection_mode == "indexed_mesh_surface":
                    containing_face = None
                    barycentric_weights = None

                    for face in target.surface_faces:
                        uv_a = target.vertex_uvs[face[0]]
                        uv_b = target.vertex_uvs[face[1]]
                        uv_c = target.vertex_uvs[face[2]]

                        weights = _barycentric_weights_2d(
                            (local_x, local_y),
                            uv_a,
                            uv_b,
                            uv_c,
                        )

                        if weights is not None:
                            containing_face = face
                            barycentric_weights = weights
                            break

                    if containing_face is None:
                        raise ValueError(
                            "point lies outside indexed mesh UV surface"
                        )

                    a = target.surface_points[
                        containing_face[0]
                    ]
                    b = target.surface_points[
                        containing_face[1]
                    ]
                    c = target.surface_points[
                        containing_face[2]
                    ]

                    wa, wb, wc = barycentric_weights

                    surface_point = tuple(
                        (
                            wa * a[axis_index]
                            + wb * b[axis_index]
                            + wc * c[axis_index]
                        )
                        for axis_index in range(3)
                    )

                    normal = _normalized_triangle_normal(
                        a,
                        b,
                        c,
                    )

                    world_point = tuple(
                        (
                            surface_point[axis_index]
                            + depth_sign * local_z * normal[axis_index]
                        )
                        for axis_index in range(3)
                    )

                elif target.projection_mode == "dome_surface":
                    azimuth_radians = math.radians(local_x)
                    polar_radians = math.radians(local_y)

                    axis = target.v_axis
                    reference = target.u_axis

                    tangent = (
                        axis[1] * reference[2]
                        - axis[2] * reference[1],
                        axis[2] * reference[0]
                        - axis[0] * reference[2],
                        axis[0] * reference[1]
                        - axis[1] * reference[0],
                    )
                    tangent_length = math.sqrt(
                        sum(value * value for value in tangent)
                    )

                    if tangent_length <= 1e-12:
                        raise ValueError(
                            "dome surface frame is degenerate"
                        )

                    tangent = tuple(
                        value / tangent_length
                        for value in tangent
                    )

                    equatorial_direction = tuple(
                        (
                            math.cos(azimuth_radians)
                            * reference[axis_index]
                            + math.sin(azimuth_radians)
                            * tangent[axis_index]
                        )
                        for axis_index in range(3)
                    )

                    radial_direction = tuple(
                        (
                            math.cos(polar_radians)
                            * axis[axis_index]
                            + math.sin(polar_radians)
                            * equatorial_direction[axis_index]
                        )
                        for axis_index in range(3)
                    )

                    radial_distance = (
                        target.radius_mm
                        + depth_sign * local_z
                    )

                    world_point = tuple(
                        (
                            target.origin[axis_index]
                            + radial_distance
                            * radial_direction[axis_index]
                        )
                        for axis_index in range(3)
                    )

                elif target.projection_mode in {
                    "cylindrical_surface",
                    "vault_surface",
                }:
                    angle_radians = math.radians(local_x)

                    axis = target.v_axis
                    reference = target.u_axis

                    tangent = (
                        axis[1] * reference[2]
                        - axis[2] * reference[1],
                        axis[2] * reference[0]
                        - axis[0] * reference[2],
                        axis[0] * reference[1]
                        - axis[1] * reference[0],
                    )
                    tangent_length = math.sqrt(
                        sum(value * value for value in tangent)
                    )

                    if tangent_length <= 1e-12:
                        raise ValueError(
                            "cylindrical surface frame is degenerate"
                        )

                    tangent = tuple(
                        value / tangent_length
                        for value in tangent
                    )

                    radial_direction = tuple(
                        (
                            math.cos(angle_radians) * reference[axis_index]
                            + math.sin(angle_radians) * tangent[axis_index]
                        )
                        for axis_index in range(3)
                    )

                    radial_distance = (
                        target.radius_mm
                        + depth_sign * local_z
                    )

                    world_point = tuple(
                        (
                            target.origin[axis_index]
                            + local_y * axis[axis_index]
                            + radial_distance
                            * radial_direction[axis_index]
                        )
                        for axis_index in range(3)
                    )

                elif target.projection_mode == "bilinear_surface":
                    p00, p10, p11, p01 = target.surface_points
                    u = local_x
                    v = local_y

                    surface_point = tuple(
                        (
                            (1.0 - u) * (1.0 - v) * p00[axis]
                            + u * (1.0 - v) * p10[axis]
                            + u * v * p11[axis]
                            + (1.0 - u) * v * p01[axis]
                        )
                        for axis in range(3)
                    )

                    du = tuple(
                        (
                            (1.0 - v) * (p10[axis] - p00[axis])
                            + v * (p11[axis] - p01[axis])
                        )
                        for axis in range(3)
                    )
                    dv = tuple(
                        (
                            (1.0 - u) * (p01[axis] - p00[axis])
                            + u * (p11[axis] - p10[axis])
                        )
                        for axis in range(3)
                    )

                    normal = _point3(
                        (
                            du[1] * dv[2] - du[2] * dv[1],
                            du[2] * dv[0] - du[0] * dv[2],
                            du[0] * dv[1] - du[1] * dv[0],
                        ),
                        field_name="bilinear surface normal",
                    )
                    normal_length = math.sqrt(
                        sum(value * value for value in normal)
                    )

                    if normal_length <= 1e-12:
                        raise ValueError(
                            "bilinear surface normal is degenerate"
                        )

                    normal = tuple(
                        value / normal_length
                        for value in normal
                    )

                    world_point = tuple(
                        surface_point[axis]
                        + depth_sign * local_z * normal[axis]
                        for axis in range(3)
                    )
                else:
                    world_point = (
                        target.origin[0]
                        + local_x * target.u_axis[0]
                        + local_y * target.v_axis[0]
                        + depth_sign * local_z * target.outward_normal[0],
                        target.origin[1]
                        + local_x * target.u_axis[1]
                        + local_y * target.v_axis[1]
                        + depth_sign * local_z * target.outward_normal[1],
                        target.origin[2]
                        + local_x * target.u_axis[2]
                        + local_y * target.v_axis[2]
                        + depth_sign * local_z * target.outward_normal[2],
                    )

                projected_triangle.append(
                    world_point
                )

            projected_triangle = tuple(
                projected_triangle
            )

            if winding_audited:
                source_winding = _uv_winding_sign(
                    local_points
                )
                if target.projection_mode in {
                    "cylindrical_surface",
                    "vault_surface",
                }:
                    reference_normal = _cylindrical_reference_normal(
                        target,
                        local_points,
                    )
                elif target.projection_mode == "dome_surface":
                    reference_normal = _dome_winding_reference_normal(
                        target,
                        local_points,
                    )
                elif target.projection_mode == "bilinear_surface":
                    reference_normal = _bilinear_winding_reference_normal(
                        target,
                        local_points,
                    )
                elif target.projection_mode == "indexed_mesh_surface":
                    reference_normal = _indexed_mesh_winding_reference_normal(
                        target,
                        local_points,
                    )
                else:
                    reference_normal = target.outward_normal

                projected_winding = _projected_winding_sign(
                    projected_triangle,
                    reference_normal=reference_normal,
                )

                if (
                    source_winding != projected_winding
                ):
                    winding_violation_count += 1

            projected_triangles.append(
                projected_triangle
            )

        if (
            target.attachment_policy == "must_attach"
            and not attachment_found
        ):
            raise ValueError(
                "mesh violates target attachment policy"
            )

        projected["triangles"] = projected_triangles

        return {
            "type": "surface_projection_result",
            "projection_mode": target.projection_mode,
            "surface_id": target.surface_id,
            "source_component_id": target.source_component_id,
            "target_component_id": target.target_component_id,
            "mesh": projected,
            "winding_preserved": (
                winding_violation_count == 0
                if winding_audited
                else True
            ),
            "winding_audited": winding_audited,
            "winding_violation_count": winding_violation_count,
            "clipped_triangle_count": 0,
            "depth_envelope_violation_count": 0,
        }
