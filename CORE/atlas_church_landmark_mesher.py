from __future__ import annotations

from CORE.atlas_church_footprint_resolver import (
    AtlasChurchFootprintResolver,
)
from CORE.atlas_church_landmark_builder import (
    AtlasChurchLandmarkGeometry,
)


class AtlasChurchLandmarkMesher:
    @staticmethod
    def _world_vertex(
        *,
        frame,
        longitudinal,
        lateral,
        z,
    ):
        x, y = frame.to_world(
            longitudinal=longitudinal,
            lateral=lateral,
        )

        return (
            float(x),
            float(y),
            float(z),
        )

    @classmethod
    def _oriented_box(
        cls,
        *,
        frame,
        min_longitudinal,
        max_longitudinal,
        min_lateral,
        max_lateral,
        min_z,
        max_z,
        mesh_type,
        **metadata,
    ):
        v000 = cls._world_vertex(
            frame=frame,
            longitudinal=min_longitudinal,
            lateral=min_lateral,
            z=min_z,
        )
        v100 = cls._world_vertex(
            frame=frame,
            longitudinal=max_longitudinal,
            lateral=min_lateral,
            z=min_z,
        )
        v110 = cls._world_vertex(
            frame=frame,
            longitudinal=max_longitudinal,
            lateral=max_lateral,
            z=min_z,
        )
        v010 = cls._world_vertex(
            frame=frame,
            longitudinal=min_longitudinal,
            lateral=max_lateral,
            z=min_z,
        )

        v001 = cls._world_vertex(
            frame=frame,
            longitudinal=min_longitudinal,
            lateral=min_lateral,
            z=max_z,
        )
        v101 = cls._world_vertex(
            frame=frame,
            longitudinal=max_longitudinal,
            lateral=min_lateral,
            z=max_z,
        )
        v111 = cls._world_vertex(
            frame=frame,
            longitudinal=max_longitudinal,
            lateral=max_lateral,
            z=max_z,
        )
        v011 = cls._world_vertex(
            frame=frame,
            longitudinal=min_longitudinal,
            lateral=max_lateral,
            z=max_z,
        )

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

    @classmethod
    def _oriented_spire(
        cls,
        *,
        frame,
        center_longitudinal,
        center_lateral,
        half_width,
        base_z,
        top_z,
        index,
    ):
        base = (
            cls._world_vertex(
                frame=frame,
                longitudinal=(
                    center_longitudinal
                    - half_width
                ),
                lateral=(
                    center_lateral
                    - half_width
                ),
                z=base_z,
            ),
            cls._world_vertex(
                frame=frame,
                longitudinal=(
                    center_longitudinal
                    + half_width
                ),
                lateral=(
                    center_lateral
                    - half_width
                ),
                z=base_z,
            ),
            cls._world_vertex(
                frame=frame,
                longitudinal=(
                    center_longitudinal
                    + half_width
                ),
                lateral=(
                    center_lateral
                    + half_width
                ),
                z=base_z,
            ),
            cls._world_vertex(
                frame=frame,
                longitudinal=(
                    center_longitudinal
                    - half_width
                ),
                lateral=(
                    center_lateral
                    + half_width
                ),
                z=base_z,
            ),
        )

        apex = cls._world_vertex(
            frame=frame,
            longitudinal=center_longitudinal,
            lateral=center_lateral,
            z=top_z,
        )

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

        frame = AtlasChurchFootprintResolver.resolve(
            geometry.footprint
        )

        depth = frame.longitudinal_span
        width = frame.lateral_span

        if width <= 0.0 or depth <= 0.0:
            raise ValueError(
                "Church footprint must have positive area"
            )

        body_height = geometry.height_m * 0.62
        tower_height = geometry.height_m * 0.82
        spire_top = geometry.height_m

        half_depth = depth / 2.0
        half_width = width / 2.0

        nave_width = width * 0.52
        nave_depth = depth * 0.78

        nave_meshes = [
            cls._oriented_box(
                frame=frame,
                min_longitudinal=-nave_depth / 2.0,
                max_longitudinal=nave_depth / 2.0,
                min_lateral=-nave_width / 2.0,
                max_lateral=nave_width / 2.0,
                min_z=0.0,
                max_z=body_height,
                mesh_type="church_nave",
            )
        ]

        transept_depth = depth * 0.22
        transept_width = width * 0.84

        transept_meshes = [
            cls._oriented_box(
                frame=frame,
                min_longitudinal=-transept_depth / 2.0,
                max_longitudinal=transept_depth / 2.0,
                min_lateral=-transept_width / 2.0,
                max_lateral=transept_width / 2.0,
                min_z=0.0,
                max_z=body_height * 0.92,
                mesh_type="church_transept",
            )
        ]

        apse_depth = depth * 0.14
        apse_width = nave_width * 0.78
        apse_center_longitudinal = (
            half_depth
            - apse_depth / 2.0
        )

        apse_meshes = [
            cls._oriented_box(
                frame=frame,
                min_longitudinal=(
                    apse_center_longitudinal
                    - apse_depth / 2.0
                ),
                max_longitudinal=(
                    apse_center_longitudinal
                    + apse_depth / 2.0
                ),
                min_lateral=-apse_width / 2.0,
                max_lateral=apse_width / 2.0,
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
        tower_center_longitudinal = (
            -half_depth
            + tower_depth / 2.0
        )

        if tower_count == 1:
            tower_centers_lateral = (0.0,)
        elif tower_count == 2:
            offset = width * 0.24
            tower_centers_lateral = (
                -offset,
                offset,
            )
        else:
            tower_centers_lateral = ()

        for index, tower_center_lateral in enumerate(
            tower_centers_lateral
        ):
            tower_meshes.append(
                cls._oriented_box(
                    frame=frame,
                    min_longitudinal=(
                        tower_center_longitudinal
                        - tower_depth / 2.0
                    ),
                    max_longitudinal=(
                        tower_center_longitudinal
                        + tower_depth / 2.0
                    ),
                    min_lateral=(
                        tower_center_lateral
                        - tower_width / 2.0
                    ),
                    max_lateral=(
                        tower_center_lateral
                        + tower_width / 2.0
                    ),
                    min_z=0.0,
                    max_z=tower_height,
                    mesh_type="church_tower",
                    index=index,
                )
            )

            if geometry.profile.has_spires:
                spire_meshes.append(
                    cls._oriented_spire(
                        frame=frame,
                        center_longitudinal=(
                            tower_center_longitudinal
                        ),
                        center_lateral=(
                            tower_center_lateral
                        ),
                        half_width=(
                            tower_width * 0.52
                        ),
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
                    -nave_depth / 2.0,
                    nave_depth / 2.0,
                    -nave_width / 2.0,
                    nave_width / 2.0,
                    body_height,
                    (
                        body_height
                        + geometry.height_m * 0.08
                    ),
                )
            elif section_name == "transept":
                roof_bounds = (
                    -transept_depth / 2.0,
                    transept_depth / 2.0,
                    -transept_width / 2.0,
                    transept_width / 2.0,
                    body_height * 0.92,
                    body_height,
                )
            elif section_name == "apse":
                roof_bounds = (
                    (
                        apse_center_longitudinal
                        - apse_depth / 2.0
                    ),
                    (
                        apse_center_longitudinal
                        + apse_depth / 2.0
                    ),
                    -apse_width / 2.0,
                    apse_width / 2.0,
                    body_height * 0.82,
                    body_height * 0.90,
                )
            else:
                roof_bounds = (
                    (
                        tower_center_longitudinal
                        - tower_depth / 2.0
                    ),
                    (
                        tower_center_longitudinal
                        + tower_depth / 2.0
                    ),
                    -tower_width / 2.0,
                    tower_width / 2.0,
                    tower_height,
                    (
                        tower_height
                        + geometry.height_m * 0.04
                    ),
                )

            roof_depth = (
                roof_bounds[1]
                - roof_bounds[0]
            )
            roof_width = (
                roof_bounds[3]
                - roof_bounds[2]
            )

            roof_inset = min(
                roof_depth,
                roof_width,
            ) * 0.02

            roof_meshes.append(
                cls._oriented_box(
                    frame=frame,
                    min_longitudinal=(
                        roof_bounds[0]
                        + roof_inset
                    ),
                    max_longitudinal=(
                        roof_bounds[1]
                        - roof_inset
                    ),
                    min_lateral=(
                        roof_bounds[2]
                        + roof_inset
                    ),
                    max_lateral=(
                        roof_bounds[3]
                        - roof_inset
                    ),
                    min_z=roof_bounds[4],
                    max_z=roof_bounds[5],
                    mesh_type=(
                        "church_roof_section"
                    ),
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
            "footprint_frame": frame,
            "triangles": triangles,
            "nave_meshes": nave_meshes,
            "transept_meshes": transept_meshes,
            "apse_meshes": apse_meshes,
            "tower_meshes": tower_meshes,
            "spire_meshes": spire_meshes,
            "roof_meshes": roof_meshes,
        }
