from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any


class AtlasCanonicalHeadPhysicalMeshAdapter:
    """
    Converts one canonical-head triangle topology into
    representation-scoped physical-coordinate triangles.

    Optional boundary closure is topology-changing and
    limited to deterministic centroid-fan closure of simple,
    consistently oriented boundary loops. Family-specific carrier
    geometry and manufacturability are not claimed here.
    """

    SUPPORTED_REPRESENTATION_KINDS = (
        "relief",
        "bust",
        "figurine_head",
        "story_kit_component",
    )

    ADAPTER_PROVENANCE = (
        "atlas_canonical_head_physical_mesh_adapter:v1"
    )

    @classmethod
    def build(
        cls,
        *,
        canonical_mesh: Mapping[str, Any],
        representation_kind: str,
        target_head_height_mm: float,
        close_boundaries: bool = False,
        main_head_only: bool = False,
    ) -> dict[str, Any]:
        if not isinstance(canonical_mesh, Mapping):
            raise TypeError(
                "canonical_mesh must be a mapping"
            )

        resolved_kind = cls._representation_kind(
            representation_kind
        )

        resolved_height = cls._positive_finite_float(
            target_head_height_mm,
            field_name="target_head_height_mm",
        )

        canonical_vertices = cls._vertices(
            canonical_mesh.get("vertices")
        )
        faces = cls._faces(
            canonical_mesh.get("faces"),
            vertex_count=len(canonical_vertices),
        )

        source_height = cls._head_height(
            canonical_vertices
        )

        scale_factor = (
            resolved_height / source_height
        )

        physical_vertices = tuple(
            (
                point[0] * scale_factor,
                point[1] * scale_factor,
                point[2] * scale_factor,
            )
            for point in canonical_vertices
        )

        source_components = cls._face_connected_components(
            faces
        )

        if main_head_only:
            selected_faces = (
                max(
                    source_components,
                    key=lambda component: len(component),
                )
                if source_components
                else ()
            )
        else:
            selected_faces = faces

        selected_face_count = len(selected_faces)

        discarded_source_component_count = (
            len(source_components) - 1
            if main_head_only and source_components
            else 0
        )

        discarded_source_face_count = (
            len(faces) - selected_face_count
            if main_head_only
            else 0
        )

        physical_triangles = tuple(
            (
                physical_vertices[a],
                physical_vertices[b],
                physical_vertices[c],
            )
            for a, b, c in selected_faces
        )

        boundary_loops = cls._boundary_loops(
            selected_faces
        )

        physical_boundary_loops = tuple(
            {
                "boundary_index": boundary_index,
                "vertex_indices": tuple(loop),
                "physical_points": tuple(
                    physical_vertices[index]
                    for index in loop
                ),
                "centroid": (
                    sum(
                        physical_vertices[index][0]
                        for index in loop
                    )
                    / len(loop),
                    sum(
                        physical_vertices[index][1]
                        for index in loop
                    )
                    / len(loop),
                    sum(
                        physical_vertices[index][2]
                        for index in loop
                    )
                    / len(loop),
                ),
            }
            for boundary_index, loop in enumerate(
                boundary_loops
            )
        )

        support_attachment_boundary = (
            min(
                physical_boundary_loops,
                key=lambda record: (
                    record["centroid"][1],
                    record["boundary_index"],
                ),
            )
            if physical_boundary_loops
            else None
        )

        closure_triangles = ()

        if close_boundaries:
            closure_triangles = cls._closure_triangles(
                boundary_loops=boundary_loops,
                physical_vertices=physical_vertices,
            )

        ready_triangles = (
            *physical_triangles,
            *closure_triangles,
        )

        ready_triangles = (
            cls._normalize_closed_mesh_orientation(
                ready_triangles
            )
        )

        source_provenance = str(
            canonical_mesh.get(
                "provenance",
                "unspecified",
            )
        ).strip()

        if not source_provenance:
            source_provenance = "unspecified"

        return {
            "representation_kind": resolved_kind,
            "target_head_height_mm": resolved_height,
            "source_head_height": source_height,
            "scale_factor": scale_factor,
            "canonical_vertices": canonical_vertices,
            "physical_vertices": physical_vertices,
            "faces": faces,
            "physical_mesh": {
                "triangles": ready_triangles,
                "type": "canonical_head_physical_mesh",
                "representation_kind": resolved_kind,
                "support_attachment_boundary": (
                    support_attachment_boundary
                ),
                "support_attachment_boundary_policy": (
                    "lowest_mean_y_boundary"
                ),
            },
            "source_provenance": source_provenance,
            "adapter_provenance": cls.ADAPTER_PROVENANCE,
            "boundary_closure_status": (
                "CLOSED"
                if close_boundaries
                else "UNRESOLVED"
            ),
            "source_connected_component_count": len(
                source_components
            ),
            "selected_source_component_face_count": (
                selected_face_count
            ),
            "discarded_source_component_count": (
                discarded_source_component_count
            ),
            "discarded_source_face_count": (
                discarded_source_face_count
            ),
            "source_open_boundary_count": len(
                boundary_loops
            ),
            "physical_boundary_loops": (
                physical_boundary_loops
            ),
            "support_attachment_boundary": (
                support_attachment_boundary
            ),
            "support_attachment_boundary_policy": (
                "lowest_mean_y_boundary"
            ),
            "closed_boundary_count": (
                len(boundary_loops)
                if close_boundaries
                else 0
            ),
            "added_closure_triangle_count": len(
                closure_triangles
            ),
            "manufacturability_status": "UNRESOLVED",
        }

    @staticmethod
    def _face_connected_components(
        faces: Sequence[tuple[int, int, int]],
    ) -> tuple[
        tuple[tuple[int, int, int], ...],
        ...,
    ]:
        if not faces:
            return ()

        vertex_to_face_ids: dict[
            int,
            list[int],
        ] = {}

        for face_id, face in enumerate(faces):
            for vertex_id in face:
                vertex_to_face_ids.setdefault(
                    vertex_id,
                    [],
                ).append(face_id)

        face_neighbors: list[set[int]] = [
            set()
            for _ in faces
        ]

        for incident_face_ids in (
            vertex_to_face_ids.values()
        ):
            for face_id in incident_face_ids:
                face_neighbors[face_id].update(
                    other_face_id
                    for other_face_id in incident_face_ids
                    if other_face_id != face_id
                )

        remaining = set(range(len(faces)))
        components = []

        while remaining:
            start = min(remaining)
            stack = [start]
            component_face_ids = []

            while stack:
                face_id = stack.pop()

                if face_id not in remaining:
                    continue

                remaining.remove(face_id)
                component_face_ids.append(face_id)

                stack.extend(
                    sorted(
                        face_neighbors[face_id]
                        & remaining,
                        reverse=True,
                    )
                )

            component_face_ids.sort()

            components.append(
                tuple(
                    faces[face_id]
                    for face_id in component_face_ids
                )
            )

        components.sort(
            key=lambda component: (
                -len(component),
                component,
            )
        )

        return tuple(components)

    @staticmethod
    def _boundary_loops(
        faces: Sequence[tuple[int, int, int]],
    ) -> tuple[tuple[int, ...], ...]:
        edge_counts: dict[
            tuple[int, int],
            int,
        ] = {}

        directed_boundary_candidates: dict[
            tuple[int, int],
            tuple[int, int],
        ] = {}

        for a, b, c in faces:
            for u, v in (
                (a, b),
                (b, c),
                (c, a),
            ):
                key = (
                    (u, v)
                    if u < v
                    else (v, u)
                )

                edge_counts[key] = (
                    edge_counts.get(key, 0)
                    + 1
                )

                directed_boundary_candidates[
                    key
                ] = (u, v)

        non_manifold_edges = tuple(
            key
            for key, count in edge_counts.items()
            if count > 2
        )

        if non_manifold_edges:
            raise ValueError(
                "canonical_mesh contains non-manifold "
                "edges shared by more than two faces"
            )

        boundary_directed = tuple(
            directed_boundary_candidates[key]
            for key, count in edge_counts.items()
            if count == 1
        )

        if not boundary_directed:
            return ()

        outgoing: dict[int, list[int]] = {}
        incoming: dict[int, list[int]] = {}

        for u, v in boundary_directed:
            outgoing.setdefault(u, []).append(v)
            incoming.setdefault(v, []).append(u)

        boundary_vertices = set(
            vertex
            for edge in boundary_directed
            for vertex in edge
        )

        for vertex in boundary_vertices:
            outgoing_vertices = outgoing.get(
                vertex,
                [],
            )
            incoming_vertices = incoming.get(
                vertex,
                [],
            )

            if (
                len(outgoing_vertices) != 1
                or len(incoming_vertices) != 1
            ):
                raise ValueError(
                    "canonical_mesh open boundary must "
                    "form consistently oriented simple "
                    "closed loops"
                )

        loops = []
        unused = set(boundary_vertices)

        while unused:
            start = min(unused)
            loop = []
            current = start

            while True:
                if current in loop:
                    if current != start:
                        raise ValueError(
                            "canonical_mesh open boundary "
                            "contains a self-intersection"
                        )
                    break

                loop.append(current)

                next_vertex = outgoing[current][0]

                if next_vertex == start:
                    break

                if next_vertex not in unused:
                    raise ValueError(
                        "canonical_mesh open boundary "
                        "loop traversal failed"
                    )

                current = next_vertex

            if len(loop) < 3:
                raise ValueError(
                    "canonical_mesh open boundary must "
                    "contain at least three vertices"
                )

            unused.difference_update(loop)

            loops.append(
                tuple(loop)
            )

        return tuple(
            sorted(
                loops,
                key=lambda loop: min(loop),
            )
        )

    @staticmethod
    def _closure_triangles(
        *,
        boundary_loops: Sequence[
            tuple[int, ...]
        ],
        physical_vertices: Sequence[
            tuple[float, float, float]
        ],
    ) -> tuple[
        tuple[
            tuple[float, float, float],
            tuple[float, float, float],
            tuple[float, float, float],
        ],
        ...,
    ]:
        triangles = []

        for loop in boundary_loops:
            if len(loop) < 3:
                raise ValueError(
                    "canonical_mesh open boundary must "
                    "contain at least three vertices"
                )

            points = tuple(
                physical_vertices[index]
                for index in loop
            )

            count = float(len(points))

            center = (
                sum(point[0] for point in points)
                / count,
                sum(point[1] for point in points)
                / count,
                sum(point[2] for point in points)
                / count,
            )

            for index, current_id in enumerate(
                loop
            ):
                next_id = loop[
                    (index + 1) % len(loop)
                ]

                triangles.append(
                    (
                        physical_vertices[
                            next_id
                        ],
                        physical_vertices[
                            current_id
                        ],
                        center,
                    )
                )

        return tuple(triangles)

    @staticmethod
    def _normalize_closed_mesh_orientation(
        triangles: Sequence[
            tuple[
                tuple[float, float, float],
                tuple[float, float, float],
                tuple[float, float, float],
            ]
        ],
    ) -> tuple[
        tuple[
            tuple[float, float, float],
            tuple[float, float, float],
            tuple[float, float, float],
        ],
        ...,
    ]:
        resolved = tuple(triangles)

        if not resolved:
            return resolved

        edge_counts: dict[
            tuple[
                tuple[float, float, float],
                tuple[float, float, float],
            ],
            int,
        ] = {}

        signed_volume = 0.0

        for p1, p2, p3 in resolved:
            keys = tuple(
                tuple(
                    round(float(value), 9)
                    for value in point
                )
                for point in (p1, p2, p3)
            )

            for start, end in (
                (keys[0], keys[1]),
                (keys[1], keys[2]),
                (keys[2], keys[0]),
            ):
                edge = tuple(
                    sorted(
                        (start, end)
                    )
                )

                edge_counts[edge] = (
                    edge_counts.get(edge, 0)
                    + 1
                )

            signed_volume += (
                p1[0] * (
                    p2[1] * p3[2]
                    - p2[2] * p3[1]
                )
                - p1[1] * (
                    p2[0] * p3[2]
                    - p2[2] * p3[0]
                )
                + p1[2] * (
                    p2[0] * p3[1]
                    - p2[1] * p3[0]
                )
            ) / 6.0

        is_closed_manifold = (
            bool(edge_counts)
            and all(
                count == 2
                for count in edge_counts.values()
            )
        )

        if (
            is_closed_manifold
            and signed_volume < 0.0
        ):
            return tuple(
                (p1, p3, p2)
                for p1, p2, p3 in resolved
            )

        return resolved

    @classmethod
    def _representation_kind(
        cls,
        value: Any,
    ) -> str:
        normalized = "_".join(
            str(value).strip().lower().split()
        )

        if normalized not in (
            cls.SUPPORTED_REPRESENTATION_KINDS
        ):
            raise ValueError(
                "representation_kind must be one of: "
                + ", ".join(
                    cls.SUPPORTED_REPRESENTATION_KINDS
                )
            )

        return normalized

    @staticmethod
    def _positive_finite_float(
        value: Any,
        *,
        field_name: str,
    ) -> float:
        if isinstance(value, bool):
            raise ValueError(
                f"{field_name} must be a positive finite number"
            )

        try:
            resolved = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{field_name} must be a positive finite number"
            ) from exc

        if (
            not math.isfinite(resolved)
            or resolved <= 0.0
        ):
            raise ValueError(
                f"{field_name} must be a positive finite number"
            )

        return resolved

    @classmethod
    def _vertices(
        cls,
        value: Any,
    ) -> tuple[tuple[float, float, float], ...]:
        if isinstance(value, (str, bytes)):
            raise ValueError(
                "canonical_mesh vertices must be a "
                "non-empty sequence"
            )

        try:
            items = tuple(value)
        except TypeError as exc:
            raise ValueError(
                "canonical_mesh vertices must be a "
                "non-empty sequence"
            ) from exc

        if not items:
            raise ValueError(
                "canonical_mesh vertices must be non-empty"
            )

        vertices = []

        for point in items:
            try:
                coordinates = tuple(point)
            except TypeError as exc:
                raise ValueError(
                    "each canonical vertex must contain "
                    "exactly three coordinates"
                ) from exc

            if len(coordinates) != 3:
                raise ValueError(
                    "each canonical vertex must contain "
                    "exactly three coordinates"
                )

            normalized = tuple(
                cls._finite_coordinate(coordinate)
                for coordinate in coordinates
            )

            vertices.append(normalized)

        return tuple(vertices)

    @classmethod
    def _faces(
        cls,
        value: Any,
        *,
        vertex_count: int,
    ) -> tuple[tuple[int, int, int], ...]:
        if isinstance(value, (str, bytes)):
            raise ValueError(
                "canonical_mesh faces must be a "
                "non-empty sequence"
            )

        try:
            items = tuple(value)
        except TypeError as exc:
            raise ValueError(
                "canonical_mesh faces must be a "
                "non-empty sequence"
            ) from exc

        if not items:
            raise ValueError(
                "canonical_mesh faces must be non-empty"
            )

        faces = []

        for face in items:
            try:
                indices = tuple(face)
            except TypeError as exc:
                raise ValueError(
                    "each canonical face must contain "
                    "exactly three vertex indices"
                ) from exc

            if len(indices) != 3:
                raise ValueError(
                    "each canonical face must contain "
                    "exactly three vertex indices"
                )

            normalized = []

            for index in indices:
                if isinstance(index, bool) or not isinstance(
                    index,
                    int,
                ):
                    raise ValueError(
                        "canonical face indices must be integers"
                    )

                if index < 0 or index >= vertex_count:
                    raise ValueError(
                        "canonical face index out of range"
                    )

                normalized.append(index)

            if len(set(normalized)) != 3:
                raise ValueError(
                    "canonical face must reference "
                    "three distinct vertices"
                )

            faces.append(tuple(normalized))

        return tuple(faces)

    @staticmethod
    def _finite_coordinate(
        value: Any,
    ) -> float:
        if isinstance(value, bool):
            raise ValueError(
                "canonical vertex coordinates must be finite"
            )

        try:
            coordinate = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "canonical vertex coordinates must be finite"
            ) from exc

        if not math.isfinite(coordinate):
            raise ValueError(
                "canonical vertex coordinates must be finite"
            )

        return coordinate

    @staticmethod
    def _head_height(
        vertices: Sequence[
            tuple[float, float, float]
        ],
    ) -> float:
        # FLAME canonical vertical axis is Y in the
        # currently qualified Phase-8 evidence path.
        y_values = tuple(
            point[1]
            for point in vertices
        )

        height = max(y_values) - min(y_values)

        if not math.isfinite(height) or height <= 0.0:
            raise ValueError(
                "canonical_mesh must have positive "
                "head height on the Y axis"
            )

        return height
