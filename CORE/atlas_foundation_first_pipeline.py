# CORE/atlas_foundation_first_pipeline.py

from CORE.atlas_mesh_builder import AtlasMeshBuilder
from CORE.atlas_foundation_surface_builder import AtlasFoundationSurfaceBuilder
from CORE.atlas_foundation_mesh_builder import AtlasFoundationMeshBuilder
from CORE.atlas_foundation_mesh_extruder import AtlasFoundationMeshExtruder


class AtlasFoundationFirstPipeline:
    """
    ATLAS Foundation-First Pipeline v0.1
    """

    @staticmethod
    def build_building_mesh(
        building,
        coordinate_engine,
        terrain_mesh,
        sample_grid=5,
        embed_depth_mm=0.30,
        diagnostics=None,
    ):
        temporary_mesh = AtlasMeshBuilder.build_mesh(
            building,
            coordinate_engine,
            foundation_z=0.0,
            diagnostics=diagnostics,
        )

        if temporary_mesh is None:
            if diagnostics and diagnostics.get("reason"):
                return None

            return AtlasFoundationFirstPipeline._reject(
                diagnostics,
                "temporary_mesh_failed",
            )

        bounds = AtlasFoundationFirstPipeline._mesh_xy_bounds(temporary_mesh)

        if bounds is None:
            return AtlasFoundationFirstPipeline._reject(
                diagnostics,
                "temporary_mesh_bounds_missing",
            )

        foundation_surface = AtlasFoundationSurfaceBuilder.build_surface(
            terrain_mesh=terrain_mesh,
            bounds=bounds,
            sample_grid=sample_grid,
            embed_depth_mm=embed_depth_mm,
        )

        if foundation_surface is None:
            return AtlasFoundationFirstPipeline._reject(
                diagnostics,
                "foundation_surface_failed",
            )

        foundation_z = foundation_surface["foundation_z"]

        foundation_mesh = AtlasFoundationMeshBuilder.build(
            footprint_points=temporary_mesh.get("bottom", []),
            foundation_z=foundation_z,
        )

        final_mesh = AtlasFoundationMeshExtruder.extrude(
            building=building,
            coordinate_engine=coordinate_engine,
            foundation_z=foundation_z,
            diagnostics=diagnostics,
        )

        if final_mesh is not None:
            final_mesh["foundation_z"] = foundation_z
            final_mesh["foundation_surface"] = foundation_surface
            final_mesh["foundation_mesh"] = foundation_mesh
            final_mesh["placement_mode"] = "foundation_first"

        return final_mesh

    @staticmethod
    def _reject(diagnostics, reason, **details):
        if diagnostics is not None:
            diagnostics.clear()
            diagnostics.update(
                {
                    "accepted": False,
                    "reason": reason,
                }
            )
            diagnostics.update(details)

        return None

    @staticmethod
    def _mesh_xy_bounds(mesh):
        points = []

        points.extend(mesh.get("bottom", []))
        points.extend(mesh.get("top", []))

        for triangle in mesh.get("triangles", []):
            points.extend(triangle)

        if not points:
            return None

        xs = [point[0] for point in points]
        ys = [point[1] for point in points]

        return {
            "min_x": min(xs),
            "max_x": max(xs),
            "min_y": min(ys),
            "max_y": max(ys),
        }
