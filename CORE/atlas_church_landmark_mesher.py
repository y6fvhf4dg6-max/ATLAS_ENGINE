from __future__ import annotations

from shapely.geometry import Polygon

from CORE.atlas_church_body_profile_system import (
    AtlasChurchBodyProfileSystem,
)
from CORE.atlas_church_footprint_resolver import (
    AtlasChurchFootprintResolver,
)
from CORE.atlas_polygon_triangulator import (
    AtlasPolygonTriangulator,
)
from CORE.atlas_church_landmark_builder import (
    AtlasChurchLandmarkGeometry,
)
from CORE.atlas_church_roof_mesher import (
    AtlasChurchRoofMesher,
)
from CORE.atlas_church_roof_profile_system import (
    AtlasChurchRoofProfileSystem,
)
from CORE.atlas_church_semantic_profile_system import (
    AtlasChurchSemanticProfileSystem,
)
from CORE.atlas_church_tower_mesher import (
    AtlasChurchTowerMesher,
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

    @staticmethod
    def _signed_area(
        footprint,
    ):
        return sum(
            (
                footprint[index][0]
                * footprint[(index + 1) % len(footprint)][1]
                - footprint[(index + 1) % len(footprint)][0]
                * footprint[index][1]
            )
            for index in range(len(footprint))
        ) / 2.0

    @classmethod
    def _extrude_real_footprint(
        cls,
        *,
        footprint,
        min_z,
        max_z,
        mesh_type,
        **metadata,
    ):
        footprint = tuple(
            (
                float(x),
                float(y),
            )
            for x, y in footprint
        )

        if (
            len(footprint) > 1
            and footprint[0] == footprint[-1]
        ):
            footprint = footprint[:-1]

        polygon = Polygon(footprint)

        if (
            polygon.is_empty
            or not polygon.is_valid
            or polygon.area <= 1e-12
        ):
            raise ValueError(
                "Church footprint must define a valid polygon"
            )

        minimum_x = min(
            x
            for x, _ in footprint
        )
        minimum_y = min(
            y
            for _, y in footprint
        )

        span_x = (
            max(x for x, _ in footprint)
            - minimum_x
        )
        span_y = (
            max(y for _, y in footprint)
            - minimum_y
        )

        normalization_scale = max(
            span_x,
            span_y,
        )

        if normalization_scale <= 1e-15:
            raise ValueError(
                "Church footprint has no triangulatable span"
            )

        normalized_footprint = tuple(
            (
                (x - minimum_x)
                / normalization_scale,
                (y - minimum_y)
                / normalization_scale,
            )
            for x, y in footprint
        )

        normalized_triangles = (
            AtlasPolygonTriangulator.triangulate(
                normalized_footprint
            )
        )

        surface_triangles = tuple(
            tuple(
                (
                    minimum_x
                    + normalized_x
                    * normalization_scale,
                    minimum_y
                    + normalized_y
                    * normalization_scale,
                )
                for normalized_x, normalized_y
                in triangle
            )
            for triangle in normalized_triangles
        )

        if not surface_triangles:
            raise ValueError(
                "Church footprint triangulation produced no surface"
            )

        triangles = []

        for coordinates in surface_triangles:
            bottom = tuple(
                (
                    float(x),
                    float(y),
                    float(min_z),
                )
                for x, y in coordinates
            )
            top = tuple(
                (
                    float(x),
                    float(y),
                    float(max_z),
                )
                for x, y in coordinates
            )

            triangles.append(
                (
                    bottom[0],
                    bottom[2],
                    bottom[1],
                )
            )
            triangles.append(
                (
                    top[0],
                    top[1],
                    top[2],
                )
            )

        counterclockwise = (
            cls._signed_area(footprint) > 0.0
        )

        for index in range(len(footprint)):
            first = footprint[index]
            second = footprint[
                (index + 1) % len(footprint)
            ]

            first_bottom = (
                first[0],
                first[1],
                float(min_z),
            )
            second_bottom = (
                second[0],
                second[1],
                float(min_z),
            )
            first_top = (
                first[0],
                first[1],
                float(max_z),
            )
            second_top = (
                second[0],
                second[1],
                float(max_z),
            )

            if counterclockwise:
                triangles.extend(
                    (
                        (
                            first_bottom,
                            second_bottom,
                            second_top,
                        ),
                        (
                            first_bottom,
                            second_top,
                            first_top,
                        ),
                    )
                )
            else:
                triangles.extend(
                    (
                        (
                            first_bottom,
                            second_top,
                            second_bottom,
                        ),
                        (
                            first_bottom,
                            first_top,
                            second_top,
                        ),
                    )
                )

        return {
            "type": mesh_type,
            "triangles": triangles,
            "uses_real_footprint": True,
            "footprint": footprint,
            "min_z": float(min_z),
            "max_z": float(max_z),
            "top_z": float(max_z),
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

        semantic_profile = (
            AtlasChurchSemanticProfileSystem.resolve(
                geometry.profile.profile_name
            )
        )
        body_profile = (
            AtlasChurchBodyProfileSystem.resolve(
                semantic_profile.plan_type
            )
        )

        half_depth = depth / 2.0
        half_width = width / 2.0

        nave_width = (
            width
            * body_profile.nave_width_ratio
        )
        nave_depth = (
            depth
            * body_profile.nave_depth_ratio
        )

        outer_aisle_height = (
            body_height
            * body_profile.outer_aisle_height_ratio
        )
        main_nave_height = body_height

        nave_meshes = [
            cls._extrude_real_footprint(
                footprint=geometry.footprint,
                min_z=0.0,
                max_z=outer_aisle_height,
                mesh_type="church_outer_body",
                section_type="outer_aisle_shell",
            )
        ]

        main_nave_body_meshes = [
            cls._oriented_box(
                frame=frame,
                min_longitudinal=-nave_depth / 2.0,
                max_longitudinal=nave_depth / 2.0,
                min_lateral=-nave_width / 2.0,
                max_lateral=nave_width / 2.0,
                min_z=0.0,
                max_z=main_nave_height,
                mesh_type="church_main_nave_body",
                section_type="main_nave",
                top_z=main_nave_height,
            )
        ]

        architectural_body_system = {
            "type": "church_stepped_body",
            "sections": (
                {
                    "section_type": "outer_aisle_left",
                    "top_z": outer_aisle_height,
                    "mesh": nave_meshes[0],
                },
                {
                    "section_type": "outer_aisle_right",
                    "top_z": outer_aisle_height,
                    "mesh": nave_meshes[0],
                },
                {
                    "section_type": "main_nave",
                    "top_z": main_nave_height,
                    "mesh": main_nave_body_meshes[0],
                },
            ),
        }

        transept_depth = (
            depth
            * body_profile.transept_depth_ratio
        )
        transept_width = (
            width
            * body_profile.transept_width_ratio
        )

        transept_meshes = [
            cls._oriented_box(
                frame=frame,
                min_longitudinal=-transept_depth / 2.0,
                max_longitudinal=transept_depth / 2.0,
                min_lateral=-transept_width / 2.0,
                max_lateral=transept_width / 2.0,
                min_z=0.0,
                max_z=(
                    body_height
                    * body_profile.transept_height_ratio
                ),
                mesh_type="church_transept",
            )
        ]

        apse_depth = (
            depth
            * body_profile.apse_depth_ratio
        )
        apse_width = (
            nave_width
            * body_profile.apse_width_ratio
        )
        apse_center_longitudinal = (
            half_depth
            - apse_depth / 2.0
        )

        suppress_front_apse = (
            not geometry.profile.has_apse
        )

        apse_meshes = (
            []
            if suppress_front_apse
            else [
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
                    max_z=(
                        body_height
                        * body_profile.apse_height_ratio
                    ),
                    mesh_type="church_apse",
                )
            ]
        )

        architectural_tower_system = (
            AtlasChurchTowerMesher.build(
                frame=frame,
                profile=geometry.tower_profile,
                building_height=geometry.height_m,
            )
        )

        tower_meshes = list(
            architectural_tower_system["towers"]
        )
        spire_meshes = []

        roof_profile = (
            AtlasChurchRoofProfileSystem.resolve(
                longitudinal_span=depth,
                lateral_span=width,
                wall_height=body_height,
                roof_character=(
                    semantic_profile.roof_character
                ),
            )
        )

        architectural_roof_system = (
            AtlasChurchRoofMesher.build(
                frame=frame,
                profile=roof_profile,
            )
        )

        roof_meshes = [
            roof
            for roof in architectural_roof_system["sections"]
            if (
                not suppress_front_apse
                or roof["section_type"] != "apse"
            )
        ]

        component_meshes = (
            nave_meshes
            + main_nave_body_meshes
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
            "main_nave_body_meshes": main_nave_body_meshes,
            "architectural_body_system": (
                architectural_body_system
            ),
            "transept_meshes": transept_meshes,
            "apse_meshes": apse_meshes,
            "tower_meshes": tower_meshes,
            "spire_meshes": spire_meshes,
            "architectural_tower_system": (
                architectural_tower_system
            ),
            "roof_meshes": roof_meshes,
            "architectural_roof_system": (
                architectural_roof_system
            ),
        }
