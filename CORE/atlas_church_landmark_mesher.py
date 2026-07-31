from __future__ import annotations

from math import sqrt

from CORE.atlas_church_landmark_builder import (
    AtlasChurchLandmarkGeometry,
)


class AtlasChurchLandmarkMesher:
    @staticmethod
    def _bounds(footprint):
        xs = tuple(point[0] for point in footprint)
        ys = tuple(point[1] for point in footprint)

        return {
            "min_x": min(xs),
            "max_x": max(xs),
            "min_y": min(ys),
            "max_y": max(ys),
        }

    @staticmethod
    def _box(
        *,
        min_x,
        max_x,
        min_y,
        max_y,
        min_z,
        max_z,
        mesh_type,
        **metadata,
    ):
        v000 = (min_x, min_y, min_z)
        v100 = (max_x, min_y, min_z)
        v110 = (max_x, max_y, min_z)
        v010 = (min_x, max_y, min_z)

        v001 = (min_x, min_y, max_z)
        v101 = (max_x, min_y, max_z)
        v111 = (max_x, max_y, max_z)
        v011 = (min_x, max_y, max_z)

        triangles = [
            (v000, v110, v100),
            (v000, v010, v110),
            (v001, v101, v111),
            (v001, v111, v011),
            (v000, v100, v101),
            (v000, v101, v001),
            (v100, v110, v111),
            (v100, v111, v101),
            (v110, v010, v011),
            (v110, v011, v111),
            (v010, v000, v001),
            (v010, v001, v011),
        ]

        return {
            "type": mesh_type,
            "triangles": triangles,
            **metadata,
        }

    @staticmethod
    def _spire(
        *,
        center_x,
        center_y,
        half_width,
        base_z,
        top_z,
        index,
    ):
        base = (
            (center_x - half_width, center_y - half_width, base_z),
            (center_x + half_width, center_y - half_width, base_z),
            (center_x + half_width, center_y + half_width, base_z),
            (center_x - half_width, center_y + half_width, base_z),
        )
        apex = (center_x, center_y, top_z)

        triangles = [
            (base[0], base[2], base[1]),
            (base[0], base[3], base[2]),
            (base[0], base[1], apex),
            (base[1], base[2], apex),
            (base[2], base[3], apex),
            (base[3], base[0], apex),
        ]

        return {
            "type": "church_spire",
            "index": index,
            "triangles": triangles,
        }

    @classmethod
    def build(
        cls,
        geometry,
    ):
        if not isinstance(
            geometry,
            AtlasChurchLandmarkGeometry,
        ):
            raise TypeError(
                "geometry must be AtlasChurchLandmarkGeometry"
            )

        bounds = cls._bounds(
            geometry.footprint
        )

        width = (
            bounds["max_x"]
            - bounds["min_x"]
        )
        depth = (
            bounds["max_y"]
            - bounds["min_y"]
        )

        if width <= 0.0 or depth <= 0.0:
            raise ValueError(
                "Church footprint must have positive area"
            )

        center_x = (
            bounds["min_x"]
            + bounds["max_x"]
        ) / 2.0
        center_y = (
            bounds["min_y"]
            + bounds["max_y"]
        ) / 2.0

        body_height = geometry.height_m * 0.62
        tower_height = geometry.height_m * 0.82
        spire_top = geometry.height_m

        nave_width = width * 0.52
        nave_depth = depth * 0.78

        nave_meshes = [
            cls._box(
                min_x=center_x - nave_width / 2.0,
                max_x=center_x + nave_width / 2.0,
                min_y=center_y - nave_depth / 2.0,
                max_y=center_y + nave_depth / 2.0,
                min_z=0.0,
                max_z=body_height,
                mesh_type="church_nave",
            )
        ]

        transept_depth = depth * 0.22
        transept_meshes = [
            cls._box(
                min_x=bounds["min_x"] + width * 0.08,
                max_x=bounds["max_x"] - width * 0.08,
                min_y=center_y - transept_depth / 2.0,
                max_y=center_y + transept_depth / 2.0,
                min_z=0.0,
                max_z=body_height * 0.92,
                mesh_type="church_transept",
            )
        ]

        apse_depth = depth * 0.14
        apse_width = nave_width * 0.78
        apse_meshes = [
            cls._box(
                min_x=center_x - apse_width / 2.0,
                max_x=center_x + apse_width / 2.0,
                min_y=bounds["max_y"] - apse_depth,
                max_y=bounds["max_y"],
                min_z=0.0,
                max_z=body_height * 0.82,
                mesh_type="church_apse",
            )
        ]

        tower_meshes = []
        spire_meshes = []

        tower_count = geometry.profile.tower_count
        tower_width = max(
            width * 0.18,
            min(width, depth) * 0.12,
        )
        tower_depth = depth * 0.16
        tower_center_y = (
            bounds["min_y"]
            + tower_depth / 2.0
        )

        if tower_count == 1:
            tower_centers = (center_x,)
        elif tower_count == 2:
            offset = width * 0.24
            tower_centers = (
                center_x - offset,
                center_x + offset,
            )
        else:
            tower_centers = ()

        for index, tower_center_x in enumerate(
            tower_centers
        ):
            tower_meshes.append(
                cls._box(
                    min_x=tower_center_x - tower_width / 2.0,
                    max_x=tower_center_x + tower_width / 2.0,
                    min_y=tower_center_y - tower_depth / 2.0,
                    max_y=tower_center_y + tower_depth / 2.0,
                    min_z=0.0,
                    max_z=tower_height,
                    mesh_type="church_tower",
                    index=index,
                )
            )

            if geometry.profile.has_spires:
                spire_meshes.append(
                    cls._spire(
                        center_x=tower_center_x,
                        center_y=tower_center_y,
                        half_width=tower_width * 0.52,
                        base_z=tower_height,
                        top_z=spire_top,
                        index=index,
                    )
                )

        roof_meshes = []

        for index, section_name in enumerate(
            geometry.profile.roof_sections
        ):
            if section_name == "nave":
                roof_bounds = (
                    center_x - nave_width / 2.0,
                    center_x + nave_width / 2.0,
                    center_y - nave_depth / 2.0,
                    center_y + nave_depth / 2.0,
                    body_height,
                    body_height + geometry.height_m * 0.08,
                )
            elif section_name == "transept":
                roof_bounds = (
                    bounds["min_x"] + width * 0.08,
                    bounds["max_x"] - width * 0.08,
                    center_y - transept_depth / 2.0,
                    center_y + transept_depth / 2.0,
                    body_height * 0.92,
                    body_height,
                )
            elif section_name == "apse":
                roof_bounds = (
                    center_x - apse_width / 2.0,
                    center_x + apse_width / 2.0,
                    bounds["max_y"] - apse_depth,
                    bounds["max_y"],
                    body_height * 0.82,
                    body_height * 0.90,
                )
            else:
                roof_bounds = (
                    center_x - tower_width / 2.0,
                    center_x + tower_width / 2.0,
                    bounds["min_y"],
                    bounds["min_y"] + tower_depth,
                    tower_height,
                    tower_height + geometry.height_m * 0.04,
                )

            roof_width = (
                roof_bounds[1]
                - roof_bounds[0]
            )
            roof_depth = (
                roof_bounds[3]
                - roof_bounds[2]
            )

            roof_inset = min(
                roof_width,
                roof_depth,
            ) * 0.02

            roof_meshes.append(
                cls._box(
                    min_x=roof_bounds[0] + roof_inset,
                    max_x=roof_bounds[1] - roof_inset,
                    min_y=roof_bounds[2] + roof_inset,
                    max_y=roof_bounds[3] - roof_inset,
                    min_z=roof_bounds[4],
                    max_z=roof_bounds[5],
                    mesh_type="church_roof_section",
                    index=index,
                    section_name=section_name,
                )
            )

        component_meshes = (
            nave_meshes
            + transept_meshes
            + apse_meshes
            + tower_meshes
            + spire_meshes
            + roof_meshes
        )

        triangles = [
            triangle
            for mesh in component_meshes
            for triangle in mesh["triangles"]
        ]

        return {
            "type": "church_landmark",
            "landmark_id": geometry.landmark_id,
            "landmark_class": geometry.landmark_class,
            "triangles": triangles,
            "nave_meshes": nave_meshes,
            "transept_meshes": transept_meshes,
            "apse_meshes": apse_meshes,
            "tower_meshes": tower_meshes,
            "spire_meshes": spire_meshes,
            "roof_meshes": roof_meshes,
        }
