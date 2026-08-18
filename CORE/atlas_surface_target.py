from __future__ import annotations

from dataclasses import dataclass
import math


def _identifier(value, *, field_name):
    normalized = "_".join(
        str(value).strip().lower().split()
    )
    if not normalized:
        raise ValueError(
            f"{field_name} must not be blank"
        )
    return normalized


def _point3(value, *, field_name):
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


def _point2(value, *, field_name):
    try:
        point = tuple(value)
    except TypeError as exc:
        raise ValueError(
            f"{field_name} must contain exactly two numeric values"
        ) from exc

    if len(point) != 2:
        raise ValueError(
            f"{field_name} must contain exactly two numeric values"
        )

    normalized = []
    for coordinate in point:
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


def _normalize_vector(value, *, field_name):
    x, y, z = _point3(
        value,
        field_name=field_name,
    )
    length = math.sqrt(
        x * x + y * y + z * z
    )

    if length <= 0.0:
        raise ValueError(
            f"{field_name} must not be zero length"
        )

    return (
        x / length,
        y / length,
        z / length,
    )


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _finite_non_negative(value, *, field_name):
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{field_name} must be numeric"
        ) from exc

    if not math.isfinite(numeric) or numeric < 0.0:
        raise ValueError(
            f"{field_name} must be finite and non-negative"
        )

    return numeric


@dataclass(frozen=True, slots=True)
class AtlasSurfaceTarget:
    surface_id: str
    surface_kind: str
    projection_mode: str
    source_component_id: str
    target_component_id: str
    origin: tuple[float, float, float]
    u_axis: tuple[float, float, float]
    v_axis: tuple[float, float, float]
    outward_normal: tuple[float, float, float]
    clipping_boundary_uv: tuple[tuple[float, float], ...]
    relief_polarity: str
    minimum_depth_mm: float
    maximum_depth_mm: float
    attachment_policy: str
    intersection_policy: str
    surface_points: tuple[tuple[float, float, float], ...] = ()
    radius_mm: float | None = None
    minimum_angle_degrees: float | None = None
    maximum_angle_degrees: float | None = None
    minimum_axis_mm: float | None = None
    maximum_axis_mm: float | None = None
    minimum_polar_degrees: float | None = None
    maximum_polar_degrees: float | None = None
    minimum_azimuth_degrees: float | None = None
    maximum_azimuth_degrees: float | None = None
    surface_faces: tuple[tuple[int, int, int], ...] = ()
    clipping_vertex_indices: tuple[int, ...] = ()
    vertex_uvs: tuple[tuple[float, float], ...] = ()

    @classmethod
    def indexed_mesh_surface(
        cls,
        *,
        surface_id,
        source_component_id,
        target_component_id,
        vertices,
        faces,
        clipping_vertex_indices,
        vertex_uvs,
        relief_polarity,
        minimum_depth_mm,
        maximum_depth_mm,
        attachment_policy,
        intersection_policy,
    ):
        try:
            vertices = tuple(
                _point3(
                    vertex,
                    field_name="vertex",
                )
                for vertex in vertices
            )
        except TypeError as exc:
            raise ValueError(
                "vertices must be an iterable of 3D points"
            ) from exc

        if len(vertices) < 3:
            raise ValueError(
                "vertices must contain at least three points"
            )

        try:
            vertex_uvs = tuple(
                _point2(
                    uv,
                    field_name="vertex_uv",
                )
                for uv in vertex_uvs
            )
        except TypeError as exc:
            raise ValueError(
                "vertex_uvs must be an iterable of 2D points"
            ) from exc

        if len(vertex_uvs) != len(vertices):
            raise ValueError(
                "vertex_uvs must contain exactly one UV per vertex"
            )

        try:
            faces = tuple(
                tuple(face)
                for face in faces
            )
        except TypeError as exc:
            raise ValueError(
                "faces must be an iterable of triangle indices"
            ) from exc

        normalized_faces = []
        for face in faces:
            if len(face) != 3:
                raise ValueError(
                    "each face must contain exactly three indices"
                )

            normalized_face = []

            for index in face:
                if isinstance(index, bool) or not isinstance(index, int):
                    raise ValueError(
                        "face indices must be integers"
                    )
                if index < 0 or index >= len(vertices):
                    raise ValueError(
                        "face index out of range"
                    )
                normalized_face.append(index)

            if len(set(normalized_face)) != 3:
                raise ValueError(
                    "face indices must be unique"
                )

            normalized_faces.append(
                tuple(normalized_face)
            )

        if not normalized_faces:
            raise ValueError(
                "faces must contain at least one triangle"
            )

        try:
            clipping_vertex_indices = tuple(
                clipping_vertex_indices
            )
        except TypeError as exc:
            raise ValueError(
                "clipping_vertex_indices must be iterable"
            ) from exc

        if len(clipping_vertex_indices) < 3:
            raise ValueError(
                "clipping_vertex_indices must contain "
                "at least three indices"
            )

        normalized_boundary = []
        for index in clipping_vertex_indices:
            if isinstance(index, bool) or not isinstance(index, int):
                raise ValueError(
                    "clipping vertex indices must be integers"
                )
            if index < 0 or index >= len(vertices):
                raise ValueError(
                    "clipping vertex index out of range"
                )
            normalized_boundary.append(index)

        if len(normalized_boundary) != len(set(normalized_boundary)):
            raise ValueError(
                "clipping vertex indices must be unique"
            )

        p0 = vertices[normalized_boundary[0]]
        p1 = vertices[normalized_boundary[1]]
        p_last = vertices[normalized_boundary[-1]]

        u_vector = (
            p1[0] - p0[0],
            p1[1] - p0[1],
            p1[2] - p0[2],
        )
        v_vector = (
            p_last[0] - p0[0],
            p_last[1] - p0[1],
            p_last[2] - p0[2],
        )

        u_axis = _normalize_vector(
            u_vector,
            field_name="u_axis",
        )
        v_axis = _normalize_vector(
            v_vector,
            field_name="v_axis",
        )
        outward_normal = _normalize_vector(
            _cross(u_axis, v_axis),
            field_name="outward_normal",
        )

        minimum_depth_mm = _finite_non_negative(
            minimum_depth_mm,
            field_name="minimum_depth_mm",
        )
        maximum_depth_mm = _finite_non_negative(
            maximum_depth_mm,
            field_name="maximum_depth_mm",
        )

        if maximum_depth_mm < minimum_depth_mm:
            raise ValueError(
                "maximum_depth_mm must not be below minimum_depth_mm"
            )

        return cls(
            surface_id=_identifier(
                surface_id,
                field_name="surface_id",
            ),
            surface_kind="indexed_mesh_surface",
            projection_mode="indexed_mesh_surface",
            source_component_id=_identifier(
                source_component_id,
                field_name="source_component_id",
            ),
            target_component_id=_identifier(
                target_component_id,
                field_name="target_component_id",
            ),
            origin=p0,
            u_axis=u_axis,
            v_axis=v_axis,
            outward_normal=outward_normal,
            clipping_boundary_uv=tuple(
                vertex_uvs[index]
                for index in normalized_boundary
            ),
            relief_polarity=_identifier(
                relief_polarity,
                field_name="relief_polarity",
            ),
            minimum_depth_mm=minimum_depth_mm,
            maximum_depth_mm=maximum_depth_mm,
            attachment_policy=_identifier(
                attachment_policy,
                field_name="attachment_policy",
            ),
            intersection_policy=_identifier(
                intersection_policy,
                field_name="intersection_policy",
            ),
            surface_points=vertices,
            surface_faces=tuple(normalized_faces),
            clipping_vertex_indices=tuple(normalized_boundary),
            vertex_uvs=vertex_uvs,
        )

    @classmethod
    def vault_surface(
        cls,
        *,
        surface_id,
        source_component_id,
        target_component_id,
        axis_origin,
        axis_direction,
        reference_direction,
        radius_mm,
        minimum_angle_degrees,
        maximum_angle_degrees,
        minimum_axis_mm,
        maximum_axis_mm,
        relief_polarity,
        minimum_depth_mm,
        maximum_depth_mm,
        attachment_policy,
        intersection_policy,
    ):
        origin = _point3(
            axis_origin,
            field_name="axis_origin",
        )
        v_axis = _normalize_vector(
            axis_direction,
            field_name="axis_direction",
        )
        u_axis = _normalize_vector(
            reference_direction,
            field_name="reference_direction",
        )

        dot = sum(
            a * b
            for a, b in zip(
                u_axis,
                v_axis,
                strict=True,
            )
        )

        if abs(dot) > 1e-9:
            raise ValueError(
                "reference_direction must be perpendicular "
                "to axis_direction"
            )

        try:
            radius_mm = float(radius_mm)
            minimum_angle_degrees = float(
                minimum_angle_degrees
            )
            maximum_angle_degrees = float(
                maximum_angle_degrees
            )
            minimum_axis_mm = float(minimum_axis_mm)
            maximum_axis_mm = float(maximum_axis_mm)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "vault surface dimensions must be numeric"
            ) from exc

        values = (
            radius_mm,
            minimum_angle_degrees,
            maximum_angle_degrees,
            minimum_axis_mm,
            maximum_axis_mm,
        )

        if any(
            not math.isfinite(value)
            for value in values
        ):
            raise ValueError(
                "vault surface dimensions must be finite"
            )

        if radius_mm <= 0.0:
            raise ValueError(
                "radius_mm must be positive"
            )

        if maximum_angle_degrees <= minimum_angle_degrees:
            raise ValueError(
                "maximum_angle_degrees must exceed "
                "minimum_angle_degrees"
            )

        if maximum_axis_mm <= minimum_axis_mm:
            raise ValueError(
                "maximum_axis_mm must exceed minimum_axis_mm"
            )

        minimum_depth_mm = _finite_non_negative(
            minimum_depth_mm,
            field_name="minimum_depth_mm",
        )
        maximum_depth_mm = _finite_non_negative(
            maximum_depth_mm,
            field_name="maximum_depth_mm",
        )

        if maximum_depth_mm < minimum_depth_mm:
            raise ValueError(
                "maximum_depth_mm must not be below minimum_depth_mm"
            )

        return cls(
            surface_id=_identifier(
                surface_id,
                field_name="surface_id",
            ),
            surface_kind="vault_surface",
            projection_mode="vault_surface",
            source_component_id=_identifier(
                source_component_id,
                field_name="source_component_id",
            ),
            target_component_id=_identifier(
                target_component_id,
                field_name="target_component_id",
            ),
            origin=origin,
            u_axis=u_axis,
            v_axis=v_axis,
            outward_normal=_normalize_vector(
                u_axis,
                field_name="outward_normal",
            ),
            clipping_boundary_uv=(
                (
                    minimum_angle_degrees,
                    minimum_axis_mm,
                ),
                (
                    maximum_angle_degrees,
                    minimum_axis_mm,
                ),
                (
                    maximum_angle_degrees,
                    maximum_axis_mm,
                ),
                (
                    minimum_angle_degrees,
                    maximum_axis_mm,
                ),
            ),
            relief_polarity=_identifier(
                relief_polarity,
                field_name="relief_polarity",
            ),
            minimum_depth_mm=minimum_depth_mm,
            maximum_depth_mm=maximum_depth_mm,
            attachment_policy=_identifier(
                attachment_policy,
                field_name="attachment_policy",
            ),
            intersection_policy=_identifier(
                intersection_policy,
                field_name="intersection_policy",
            ),
            radius_mm=radius_mm,
            minimum_angle_degrees=minimum_angle_degrees,
            maximum_angle_degrees=maximum_angle_degrees,
            minimum_axis_mm=minimum_axis_mm,
            maximum_axis_mm=maximum_axis_mm,
        )

    @classmethod
    def dome_surface(
        cls,
        *,
        surface_id,
        source_component_id,
        target_component_id,
        center,
        axis_direction,
        reference_direction,
        radius_mm,
        minimum_polar_degrees,
        maximum_polar_degrees,
        minimum_azimuth_degrees,
        maximum_azimuth_degrees,
        relief_polarity,
        minimum_depth_mm,
        maximum_depth_mm,
        attachment_policy,
        intersection_policy,
    ):
        origin = _point3(
            center,
            field_name="center",
        )
        v_axis = _normalize_vector(
            axis_direction,
            field_name="axis_direction",
        )
        u_axis = _normalize_vector(
            reference_direction,
            field_name="reference_direction",
        )

        dot = sum(
            a * b
            for a, b in zip(
                u_axis,
                v_axis,
                strict=True,
            )
        )

        if abs(dot) > 1e-9:
            raise ValueError(
                "reference_direction must be perpendicular "
                "to axis_direction"
            )

        try:
            radius_mm = float(radius_mm)
            minimum_polar_degrees = float(
                minimum_polar_degrees
            )
            maximum_polar_degrees = float(
                maximum_polar_degrees
            )
            minimum_azimuth_degrees = float(
                minimum_azimuth_degrees
            )
            maximum_azimuth_degrees = float(
                maximum_azimuth_degrees
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "dome surface dimensions must be numeric"
            ) from exc

        values = (
            radius_mm,
            minimum_polar_degrees,
            maximum_polar_degrees,
            minimum_azimuth_degrees,
            maximum_azimuth_degrees,
        )

        if any(
            not math.isfinite(value)
            for value in values
        ):
            raise ValueError(
                "dome surface dimensions must be finite"
            )

        if radius_mm <= 0.0:
            raise ValueError(
                "radius_mm must be positive"
            )

        if (
            minimum_polar_degrees < 0.0
            or maximum_polar_degrees > 180.0
            or maximum_polar_degrees
            <= minimum_polar_degrees
        ):
            raise ValueError(
                "polar angle range must be ordered "
                "within 0..180 degrees"
            )

        if (
            minimum_azimuth_degrees < -180.0
            or maximum_azimuth_degrees > 180.0
            or maximum_azimuth_degrees
            <= minimum_azimuth_degrees
        ):
            raise ValueError(
                "azimuth angle range must be ordered "
                "within -180..180 degrees"
            )

        minimum_depth_mm = _finite_non_negative(
            minimum_depth_mm,
            field_name="minimum_depth_mm",
        )
        maximum_depth_mm = _finite_non_negative(
            maximum_depth_mm,
            field_name="maximum_depth_mm",
        )

        if maximum_depth_mm < minimum_depth_mm:
            raise ValueError(
                "maximum_depth_mm must not be below minimum_depth_mm"
            )

        outward_normal = v_axis

        return cls(
            surface_id=_identifier(
                surface_id,
                field_name="surface_id",
            ),
            surface_kind="dome_surface",
            projection_mode="dome_surface",
            source_component_id=_identifier(
                source_component_id,
                field_name="source_component_id",
            ),
            target_component_id=_identifier(
                target_component_id,
                field_name="target_component_id",
            ),
            origin=origin,
            u_axis=u_axis,
            v_axis=v_axis,
            outward_normal=outward_normal,
            clipping_boundary_uv=(
                (
                    minimum_azimuth_degrees,
                    minimum_polar_degrees,
                ),
                (
                    maximum_azimuth_degrees,
                    minimum_polar_degrees,
                ),
                (
                    maximum_azimuth_degrees,
                    maximum_polar_degrees,
                ),
                (
                    minimum_azimuth_degrees,
                    maximum_polar_degrees,
                ),
            ),
            relief_polarity=_identifier(
                relief_polarity,
                field_name="relief_polarity",
            ),
            minimum_depth_mm=minimum_depth_mm,
            maximum_depth_mm=maximum_depth_mm,
            attachment_policy=_identifier(
                attachment_policy,
                field_name="attachment_policy",
            ),
            intersection_policy=_identifier(
                intersection_policy,
                field_name="intersection_policy",
            ),
            radius_mm=radius_mm,
            minimum_polar_degrees=minimum_polar_degrees,
            maximum_polar_degrees=maximum_polar_degrees,
            minimum_azimuth_degrees=minimum_azimuth_degrees,
            maximum_azimuth_degrees=maximum_azimuth_degrees,
        )

    @classmethod
    def cylindrical_surface(
        cls,
        *,
        surface_id,
        source_component_id,
        target_component_id,
        axis_origin,
        axis_direction,
        reference_direction,
        radius_mm,
        minimum_angle_degrees,
        maximum_angle_degrees,
        minimum_axis_mm,
        maximum_axis_mm,
        relief_polarity,
        minimum_depth_mm,
        maximum_depth_mm,
        attachment_policy,
        intersection_policy,
    ):
        origin = _point3(
            axis_origin,
            field_name="axis_origin",
        )
        v_axis = _normalize_vector(
            axis_direction,
            field_name="axis_direction",
        )
        u_axis = _normalize_vector(
            reference_direction,
            field_name="reference_direction",
        )

        dot = sum(
            a * b
            for a, b in zip(
                u_axis,
                v_axis,
                strict=True,
            )
        )

        if abs(dot) > 1e-9:
            raise ValueError(
                "reference_direction must be perpendicular "
                "to axis_direction"
            )

        try:
            radius_mm = float(radius_mm)
            minimum_angle_degrees = float(
                minimum_angle_degrees
            )
            maximum_angle_degrees = float(
                maximum_angle_degrees
            )
            minimum_axis_mm = float(minimum_axis_mm)
            maximum_axis_mm = float(maximum_axis_mm)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "cylindrical surface dimensions must be numeric"
            ) from exc

        values = (
            radius_mm,
            minimum_angle_degrees,
            maximum_angle_degrees,
            minimum_axis_mm,
            maximum_axis_mm,
        )
        if any(
            not math.isfinite(value)
            for value in values
        ):
            raise ValueError(
                "cylindrical surface dimensions must be finite"
            )

        if radius_mm <= 0.0:
            raise ValueError(
                "radius_mm must be positive"
            )

        if maximum_angle_degrees <= minimum_angle_degrees:
            raise ValueError(
                "maximum_angle_degrees must exceed "
                "minimum_angle_degrees"
            )

        if maximum_axis_mm <= minimum_axis_mm:
            raise ValueError(
                "maximum_axis_mm must exceed minimum_axis_mm"
            )

        minimum_depth_mm = _finite_non_negative(
            minimum_depth_mm,
            field_name="minimum_depth_mm",
        )
        maximum_depth_mm = _finite_non_negative(
            maximum_depth_mm,
            field_name="maximum_depth_mm",
        )

        if maximum_depth_mm < minimum_depth_mm:
            raise ValueError(
                "maximum_depth_mm must not be below minimum_depth_mm"
            )

        outward_normal = _normalize_vector(
            u_axis,
            field_name="outward_normal",
        )

        return cls(
            surface_id=_identifier(
                surface_id,
                field_name="surface_id",
            ),
            surface_kind="cylindrical_surface",
            projection_mode="cylindrical_surface",
            source_component_id=_identifier(
                source_component_id,
                field_name="source_component_id",
            ),
            target_component_id=_identifier(
                target_component_id,
                field_name="target_component_id",
            ),
            origin=origin,
            u_axis=u_axis,
            v_axis=v_axis,
            outward_normal=outward_normal,
            clipping_boundary_uv=(
                (
                    minimum_angle_degrees,
                    minimum_axis_mm,
                ),
                (
                    maximum_angle_degrees,
                    minimum_axis_mm,
                ),
                (
                    maximum_angle_degrees,
                    maximum_axis_mm,
                ),
                (
                    minimum_angle_degrees,
                    maximum_axis_mm,
                ),
            ),
            relief_polarity=_identifier(
                relief_polarity,
                field_name="relief_polarity",
            ),
            minimum_depth_mm=minimum_depth_mm,
            maximum_depth_mm=maximum_depth_mm,
            attachment_policy=_identifier(
                attachment_policy,
                field_name="attachment_policy",
            ),
            intersection_policy=_identifier(
                intersection_policy,
                field_name="intersection_policy",
            ),
            radius_mm=radius_mm,
            minimum_angle_degrees=minimum_angle_degrees,
            maximum_angle_degrees=maximum_angle_degrees,
            minimum_axis_mm=minimum_axis_mm,
            maximum_axis_mm=maximum_axis_mm,
        )

    @classmethod
    def bilinear_quad(
        cls,
        *,
        surface_id,
        source_component_id,
        target_component_id,
        quad,
        relief_polarity,
        minimum_depth_mm,
        maximum_depth_mm,
        attachment_policy,
        intersection_policy,
    ):
        try:
            quad = tuple(
                _point3(
                    point,
                    field_name="quad point",
                )
                for point in quad
            )
        except TypeError as exc:
            raise ValueError(
                "quad must contain exactly four 3D points"
            ) from exc

        if len(quad) != 4:
            raise ValueError(
                "quad must contain exactly four 3D points"
            )

        p0, p1, p2, p3 = quad

        u_vector = (
            p1[0] - p0[0],
            p1[1] - p0[1],
            p1[2] - p0[2],
        )
        v_vector = (
            p3[0] - p0[0],
            p3[1] - p0[1],
            p3[2] - p0[2],
        )

        u_axis = _normalize_vector(
            u_vector,
            field_name="u_axis",
        )
        v_axis = _normalize_vector(
            v_vector,
            field_name="v_axis",
        )
        outward_normal = _normalize_vector(
            _cross(u_axis, v_axis),
            field_name="outward_normal",
        )

        minimum_depth_mm = _finite_non_negative(
            minimum_depth_mm,
            field_name="minimum_depth_mm",
        )
        maximum_depth_mm = _finite_non_negative(
            maximum_depth_mm,
            field_name="maximum_depth_mm",
        )

        if maximum_depth_mm < minimum_depth_mm:
            raise ValueError(
                "maximum_depth_mm must not be below minimum_depth_mm"
            )

        return cls(
            surface_id=_identifier(
                surface_id,
                field_name="surface_id",
            ),
            surface_kind="bilinear_quad",
            projection_mode="bilinear_surface",
            source_component_id=_identifier(
                source_component_id,
                field_name="source_component_id",
            ),
            target_component_id=_identifier(
                target_component_id,
                field_name="target_component_id",
            ),
            origin=p0,
            u_axis=u_axis,
            v_axis=v_axis,
            outward_normal=outward_normal,
            clipping_boundary_uv=(
                (0.0, 0.0),
                (1.0, 0.0),
                (1.0, 1.0),
                (0.0, 1.0),
            ),
            relief_polarity=_identifier(
                relief_polarity,
                field_name="relief_polarity",
            ),
            minimum_depth_mm=minimum_depth_mm,
            maximum_depth_mm=maximum_depth_mm,
            attachment_policy=_identifier(
                attachment_policy,
                field_name="attachment_policy",
            ),
            intersection_policy=_identifier(
                intersection_policy,
                field_name="intersection_policy",
            ),
            surface_points=quad,
        )

    @classmethod
    def oriented_planar_quad(
        cls,
        *,
        surface_id,
        source_component_id,
        target_component_id,
        quad,
        relief_polarity,
        minimum_depth_mm,
        maximum_depth_mm,
        attachment_policy,
        intersection_policy,
    ):
        try:
            quad = tuple(
                _point3(
                    point,
                    field_name="quad point",
                )
                for point in quad
            )
        except TypeError as exc:
            raise ValueError(
                "quad must contain exactly four 3D points"
            ) from exc

        if len(quad) != 4:
            raise ValueError(
                "quad must contain exactly four 3D points"
            )

        p0, p1, p2, p3 = quad

        u_vector = (
            p1[0] - p0[0],
            p1[1] - p0[1],
            p1[2] - p0[2],
        )
        v_vector = (
            p3[0] - p0[0],
            p3[1] - p0[1],
            p3[2] - p0[2],
        )

        u_length = math.sqrt(
            sum(value * value for value in u_vector)
        )
        v_length = math.sqrt(
            sum(value * value for value in v_vector)
        )

        if u_length <= 0.0 or v_length <= 0.0:
            raise ValueError(
                "quad edges must have positive length"
            )

        u_axis = _normalize_vector(
            u_vector,
            field_name="u_axis",
        )
        v_axis = _normalize_vector(
            v_vector,
            field_name="v_axis",
        )
        outward_normal = _normalize_vector(
            _cross(u_axis, v_axis),
            field_name="outward_normal",
        )

        minimum_depth_mm = _finite_non_negative(
            minimum_depth_mm,
            field_name="minimum_depth_mm",
        )
        maximum_depth_mm = _finite_non_negative(
            maximum_depth_mm,
            field_name="maximum_depth_mm",
        )

        if maximum_depth_mm < minimum_depth_mm:
            raise ValueError(
                "maximum_depth_mm must not be below minimum_depth_mm"
            )

        return cls(
            surface_id=_identifier(
                surface_id,
                field_name="surface_id",
            ),
            surface_kind="oriented_planar_quad",
            projection_mode="oriented_planar",
            source_component_id=_identifier(
                source_component_id,
                field_name="source_component_id",
            ),
            target_component_id=_identifier(
                target_component_id,
                field_name="target_component_id",
            ),
            origin=p0,
            u_axis=u_axis,
            v_axis=v_axis,
            outward_normal=outward_normal,
            clipping_boundary_uv=(
                (0.0, 0.0),
                (u_length, 0.0),
                (u_length, v_length),
                (0.0, v_length),
            ),
            relief_polarity=_identifier(
                relief_polarity,
                field_name="relief_polarity",
            ),
            minimum_depth_mm=minimum_depth_mm,
            maximum_depth_mm=maximum_depth_mm,
            attachment_policy=_identifier(
                attachment_policy,
                field_name="attachment_policy",
            ),
            intersection_policy=_identifier(
                intersection_policy,
                field_name="intersection_policy",
            ),
        )

    @classmethod
    def flat_plane(
        cls,
        *,
        surface_id,
        source_component_id,
        target_component_id,
        origin,
        u_axis,
        v_axis,
        clipping_boundary_uv,
        relief_polarity,
        minimum_depth_mm,
        maximum_depth_mm,
        attachment_policy,
        intersection_policy,
    ):
        origin = _point3(
            origin,
            field_name="origin",
        )
        u_axis = _normalize_vector(
            u_axis,
            field_name="u_axis",
        )
        v_axis = _normalize_vector(
            v_axis,
            field_name="v_axis",
        )

        outward_normal = _normalize_vector(
            _cross(u_axis, v_axis),
            field_name="outward_normal",
        )

        try:
            boundary = tuple(
                tuple(float(value) for value in point)
                for point in clipping_boundary_uv
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "clipping_boundary_uv must contain numeric UV points"
            ) from exc

        if (
            len(boundary) < 3
            or any(len(point) != 2 for point in boundary)
            or any(
                not math.isfinite(value)
                for point in boundary
                for value in point
            )
        ):
            raise ValueError(
                "clipping_boundary_uv must contain at least "
                "three finite 2D points"
            )

        minimum_depth_mm = _finite_non_negative(
            minimum_depth_mm,
            field_name="minimum_depth_mm",
        )
        maximum_depth_mm = _finite_non_negative(
            maximum_depth_mm,
            field_name="maximum_depth_mm",
        )

        if maximum_depth_mm < minimum_depth_mm:
            raise ValueError(
                "maximum_depth_mm must not be below minimum_depth_mm"
            )

        return cls(
            surface_id=_identifier(
                surface_id,
                field_name="surface_id",
            ),
            surface_kind="flat_plane",
            projection_mode="flat_plane",
            source_component_id=_identifier(
                source_component_id,
                field_name="source_component_id",
            ),
            target_component_id=_identifier(
                target_component_id,
                field_name="target_component_id",
            ),
            origin=origin,
            u_axis=u_axis,
            v_axis=v_axis,
            outward_normal=outward_normal,
            clipping_boundary_uv=boundary,
            relief_polarity=_identifier(
                relief_polarity,
                field_name="relief_polarity",
            ),
            minimum_depth_mm=minimum_depth_mm,
            maximum_depth_mm=maximum_depth_mm,
            attachment_policy=_identifier(
                attachment_policy,
                field_name="attachment_policy",
            ),
            intersection_policy=_identifier(
                intersection_policy,
                field_name="intersection_policy",
            ),
        )
