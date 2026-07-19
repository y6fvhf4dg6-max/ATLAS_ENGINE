# CORE/atlas_mesh_validator.py


class AtlasMeshValidator:
    """
    ATLAS Mesh Validator v2.0

    Hem temel mesh yapısını kontrol eder,
    hem triangle edge topolojisini sayar.
    """

    @staticmethod
    def validate(mesh):
        report = AtlasMeshValidator.report(mesh)
        return report["valid"]

    @staticmethod
    def report(mesh):
        if mesh is None:
            return {
                "valid": False,
                "reason": "mesh_is_none",
            }

        structure_report = AtlasMeshValidator._structure_report(mesh)

        if not structure_report["structure_valid"]:
            return {
                "valid": False,
                **structure_report,
            }

        topology_report = AtlasMeshValidator._topology_report(mesh)

        return {
            "valid": (
                structure_report["structure_valid"]
                and topology_report["open_edge_count"] == 0
                and topology_report["non_manifold_edge_count"] == 0
            ),
            **structure_report,
            **topology_report,
        }

    @staticmethod
    def _structure_report(mesh):
        if mesh.get("type") == "castle_wall_crenellations":
            triangles = mesh.get("triangles")

            if triangles is None:
                return {
                    "structure_valid": False,
                    "reason": "missing_key_triangles",
                }

            if len(triangles) < 4:
                return {
                    "structure_valid": False,
                    "reason": "triangles_too_small",
                }

            for triangle in triangles:
                if triangle is None or len(triangle) != 3:
                    return {
                        "structure_valid": False,
                        "reason": "bad_triangle_size",
                    }

                for point in triangle:
                    if point is None or len(point) != 3:
                        return {
                            "structure_valid": False,
                            "reason": "bad_point_size",
                        }

                    if any(value is None for value in point):
                        return {
                            "structure_valid": False,
                            "reason": "point_has_none",
                        }

            return {
                "structure_valid": True,
                "triangles": len(triangles),
            }

        required_keys = ("bottom", "top", "walls", "triangles")

        for key in required_keys:
            if key not in mesh:
                return {
                    "structure_valid": False,
                    "reason": f"missing_key_{key}",
                }

        bottom = mesh["bottom"]
        top = mesh["top"]
        walls = mesh["walls"]
        triangles = mesh["triangles"]

        if len(bottom) < 3:
            return {"structure_valid": False, "reason": "bottom_too_small"}

        if len(top) < 3:
            return {"structure_valid": False, "reason": "top_too_small"}

        if len(bottom) != len(top):
            return {"structure_valid": False, "reason": "bottom_top_mismatch"}

        mesh_type = mesh.get(
            "type",
        )

        if (
            mesh_type != "road_foundation"
            and len(walls) != len(bottom)
        ):
            return {
                "structure_valid": False,
                "reason": "wall_count_mismatch",
            }

        if (
            mesh_type == "road_foundation"
            and len(walls) < 4
        ):
            return {
                "structure_valid": False,
                "reason": "road_wall_count_too_small",
            }

        if len(triangles) < 4:
            return {"structure_valid": False, "reason": "triangles_too_small"}

        for triangle in triangles:
            if triangle is None:
                return {
                    "structure_valid": False,
                    "reason": "bad_triangle_size",
                }

            try:
                triangle_size = len(triangle)
            except TypeError:
                return {
                    "structure_valid": False,
                    "reason": "bad_triangle_size",
                }

            if triangle_size != 3:
                return {
                    "structure_valid": False,
                    "reason": "bad_triangle_size",
                }

            for point in triangle:
                if point is None:
                    return {
                        "structure_valid": False,
                        "reason": "bad_point_size",
                    }

                try:
                    point_size = len(point)
                except TypeError:
                    return {
                        "structure_valid": False,
                        "reason": "bad_point_size",
                    }

                if point_size != 3:
                    return {
                        "structure_valid": False,
                        "reason": "bad_point_size",
                    }

                if any(value is None for value in point):
                    return {
                        "structure_valid": False,
                        "reason": "point_has_none",
                    }

        for point in bottom + top:
            if len(point) != 3:
                return {"structure_valid": False, "reason": "bad_point_size"}

            x, y, z = point

            if x is None or y is None or z is None:
                return {"structure_valid": False, "reason": "point_has_none"}

        return {
            "structure_valid": True,
            "bottom_points": len(bottom),
            "top_points": len(top),
            "walls": len(walls),
            "triangles": len(triangles),
        }

    @staticmethod
    def _topology_report(mesh):
        triangles = mesh.get("triangles", [])
        edge_counts = {}

        for tri in triangles:
            p1, p2, p3 = tri

            edges = [
                AtlasMeshValidator._edge_key(p1, p2),
                AtlasMeshValidator._edge_key(p2, p3),
                AtlasMeshValidator._edge_key(p3, p1),
            ]

            for edge in edges:
                edge_counts[edge] = edge_counts.get(edge, 0) + 1

        open_edges = []
        non_manifold_edges = []

        for edge, count in edge_counts.items():
            if count == 1:
                open_edges.append(edge)
            elif count > 2:
                non_manifold_edges.append((edge, count))

        return {
            "edge_count": len(edge_counts),
            "open_edge_count": len(open_edges),
            "non_manifold_edge_count": len(non_manifold_edges),
            "sample_open_edges": open_edges[:10],
            "sample_non_manifold_edges": non_manifold_edges[:10],
        }

    @staticmethod
    def _edge_key(p1, p2):
        a = AtlasMeshValidator._point_key(p1)
        b = AtlasMeshValidator._point_key(p2)

        if a <= b:
            return (a, b)

        return (b, a)

    @staticmethod
    def _point_key(point):
        return (
            round(point[0], 6),
            round(point[1], 6),
            round(point[2], 6),
        )
