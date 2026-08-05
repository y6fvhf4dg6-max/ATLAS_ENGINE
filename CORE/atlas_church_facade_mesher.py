from __future__ import annotations

from CORE.atlas_church_body_profile_system import (
    AtlasChurchBodyProfile,
)
from CORE.atlas_church_facade_profile_system import (
    AtlasChurchFacadeProfile,
)
from CORE.atlas_church_footprint_resolver import (
    AtlasChurchFootprintFrame,
)
from CORE.atlas_facade_circular_panel_builder import (
    AtlasFacadeCircularPanelBuilder,
)
from CORE.atlas_facade_panel_builder import (
    AtlasFacadePanelBuilder,
)
from CORE.atlas_physical_detail_resolver import (
    AtlasPhysicalDetailResolver,
)


class AtlasChurchFacadeMesher:
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
    def _side_wall_quad(
        cls,
        *,
        frame,
        facade_side,
        wall_height,
        main_nave_depth,
        main_nave_width,
        min_z=0.0,
    ):
        half_depth = (
            float(main_nave_depth) / 2.0
        )
        half_width = (
            float(main_nave_width) / 2.0
        )

        if facade_side == "left":
            lateral = -half_width
            longitudinal_start = half_depth
            longitudinal_end = -half_depth
        elif facade_side == "right":
            lateral = half_width
            longitudinal_start = -half_depth
            longitudinal_end = half_depth
        else:
            raise ValueError(
                "facade_side must be left or right"
            )

        return (
            cls._world_vertex(
                frame=frame,
                longitudinal=longitudinal_start,
                lateral=lateral,
                z=min_z,
            ),
            cls._world_vertex(
                frame=frame,
                longitudinal=longitudinal_end,
                lateral=lateral,
                z=min_z,
            ),
            cls._world_vertex(
                frame=frame,
                longitudinal=longitudinal_end,
                lateral=lateral,
                z=wall_height,
            ),
            cls._world_vertex(
                frame=frame,
                longitudinal=longitudinal_start,
                lateral=lateral,
                z=wall_height,
            ),
        )

    @classmethod
    def _end_wall_quad(
        cls,
        *,
        frame,
        facade_side,
        wall_height,
        main_nave_depth,
        main_nave_width,
    ):
        half_depth = (
            float(main_nave_depth) / 2.0
        )
        half_width = (
            float(main_nave_width) / 2.0
        )

        if facade_side == "front":
            longitudinal = -half_depth
            lateral_start = half_width
            lateral_end = -half_width
        elif facade_side == "rear":
            longitudinal = half_depth
            lateral_start = -half_width
            lateral_end = half_width
        else:
            raise ValueError(
                "facade_side must be front or rear"
            )

        return (
            cls._world_vertex(
                frame=frame,
                longitudinal=longitudinal,
                lateral=lateral_start,
                z=0.0,
            ),
            cls._world_vertex(
                frame=frame,
                longitudinal=longitudinal,
                lateral=lateral_end,
                z=0.0,
            ),
            cls._world_vertex(
                frame=frame,
                longitudinal=longitudinal,
                lateral=lateral_end,
                z=wall_height,
            ),
            cls._world_vertex(
                frame=frame,
                longitudinal=longitudinal,
                lateral=lateral_start,
                z=wall_height,
            ),
        )

    @staticmethod
    def _column_count(
        facade_profile,
    ):
        return max(
            1,
            round(
                1.0
                / facade_profile.bay_spacing_ratio
            ),
        )

    @classmethod
    def build(
        cls,
        *,
        frame,
        wall_height,
        facade_profile,
        body_profile,
        scale_ratio,
        nozzle_diameter_mm,
        window_action=None,
        window_resolved_size_mm=None,
        side_wall_min_z=0.0,
        front_wall_quad=None,
        front_surface_target="main_nave_front",
        rear_wall_quad=None,
        rear_surface_target="main_nave_rear",
    ):
        if not isinstance(
            frame,
            AtlasChurchFootprintFrame,
        ):
            raise TypeError(
                "frame must be AtlasChurchFootprintFrame"
            )

        if not isinstance(
            facade_profile,
            AtlasChurchFacadeProfile,
        ):
            raise TypeError(
                "facade_profile must be AtlasChurchFacadeProfile"
            )

        if not isinstance(
            body_profile,
            AtlasChurchBodyProfile,
        ):
            raise TypeError(
                "body_profile must be AtlasChurchBodyProfile"
            )

        wall_height = float(
            wall_height
        )
        scale_ratio = float(
            scale_ratio
        )
        nozzle_diameter_mm = float(
            nozzle_diameter_mm
        )
        side_wall_min_z = float(
            side_wall_min_z
        )
        front_surface_target = "_".join(
            str(
                front_surface_target
            ).strip().lower().split()
        )

        if not front_surface_target:
            raise ValueError(
                "front_surface_target must not be blank"
            )

        if front_wall_quad is not None:
            front_wall_quad = tuple(
                tuple(
                    float(coordinate)
                    for coordinate in point
                )
                for point in front_wall_quad
            )

            if (
                len(front_wall_quad) != 4
                or any(
                    len(point) != 3
                    for point in front_wall_quad
                )
            ):
                raise ValueError(
                    "front_wall_quad must contain "
                    "four 3D points"
                )

        rear_surface_target = "_".join(
            str(
                rear_surface_target
            ).strip().lower().split()
        )

        if not rear_surface_target:
            raise ValueError(
                "rear_surface_target must not be blank"
            )

        if rear_wall_quad is not None:
            rear_wall_quad = tuple(
                tuple(
                    float(coordinate)
                    for coordinate in point
                )
                for point in rear_wall_quad
            )

            if (
                len(rear_wall_quad) != 4
                or any(
                    len(point) != 3
                    for point in rear_wall_quad
                )
            ):
                raise ValueError(
                    "rear_wall_quad must contain "
                    "four 3D points"
                )

        if window_action is not None:
            window_action = str(
                window_action
            ).strip().lower()

            if window_action not in {
                "preserve",
                "enlarge",
                "omit",
            }:
                raise ValueError(
                    "window_action must be preserve, "
                    "enlarge, omit, or None"
                )

            if window_resolved_size_mm is None:
                raise ValueError(
                    "window_resolved_size_mm is required "
                    "when window_action is provided"
                )

            window_resolved_size_mm = float(
                window_resolved_size_mm
            )

            if window_resolved_size_mm < 0.0:
                raise ValueError(
                    "window_resolved_size_mm must be "
                    "non-negative"
                )

            if (
                window_action == "omit"
                and window_resolved_size_mm != 0.0
            ):
                raise ValueError(
                    "omit requires "
                    "window_resolved_size_mm=0"
                )

            if (
                window_action != "omit"
                and window_resolved_size_mm <= 0.0
            ):
                raise ValueError(
                    "preserve and enlarge require a "
                    "positive window_resolved_size_mm"
                )

        if wall_height <= 0.0:
            raise ValueError(
                "wall_height must be greater than zero"
            )

        if side_wall_min_z < 0.0:
            raise ValueError(
                "side_wall_min_z must be non-negative"
            )

        if side_wall_min_z >= wall_height:
            raise ValueError(
                "side_wall_min_z must be below wall_height"
            )

        if scale_ratio <= 0.0:
            raise ValueError(
                "scale_ratio must be greater than zero"
            )

        if nozzle_diameter_mm <= 0.0:
            raise ValueError(
                "nozzle_diameter_mm must be greater than zero"
            )

        main_nave_width = (
            frame.lateral_span
            * body_profile.nave_width_ratio
        )
        main_nave_depth = (
            frame.longitudinal_span
            * body_profile.nave_depth_ratio
        )

        nominal_depth_m = (
            min(
                main_nave_depth,
                main_nave_width,
            )
            * facade_profile.recess_depth_ratio
        )

        depth_decision = AtlasPhysicalDetailResolver.resolve(
            real_size_m=nominal_depth_m,
            scale_ratio=scale_ratio,
            nozzle_diameter_mm=nozzle_diameter_mm,
            detail_type="church_facade_recess",
        )

        physical_depth_mm = max(
            depth_decision.resolved_size_mm,
            nozzle_diameter_mm,
        )

        resolved_window_action = (
            "preserve"
            if window_action is None
            else window_action
        )
        resolved_window_size_mm = (
            physical_depth_mm
            if window_resolved_size_mm is None
            else window_resolved_size_mm
        )

        model_depth_m = (
            physical_depth_mm
            * scale_ratio
            / 1000.0
        )
        model_embed_m = (
            model_depth_m * 0.20
        )

        column_count = cls._column_count(
            facade_profile
        )
        arch_segments = (
            8
            if facade_profile.arch_shape
            == "round_arch"
            else 4
        )

        side_facades = []
        end_facades = []
        oculus_meshes = []
        component_meshes = []
        triangles = []

        if resolved_window_action == "omit":
            return {
                "type": "church_facade_system",
                "facade_rhythm": (
                    facade_profile.facade_rhythm
                ),
                "arch_shape": (
                    facade_profile.arch_shape
                ),
                "front_composition": (
                    facade_profile.front_composition
                ),
                "rear_composition": (
                    facade_profile.rear_composition
                ),
                "column_count_per_side": column_count,
                "row_count": 1,
                "main_nave_width": main_nave_width,
                "main_nave_depth": main_nave_depth,
                "panel_count": 0,
                "physical_depth_mm": 0.0,
                "model_depth_m": 0.0,
                "window_action": (
                    resolved_window_action
                ),
                "window_resolved_size_mm": (
                    resolved_window_size_mm
                ),
                "side_wall_min_z": side_wall_min_z,
                "side_wall_max_z": wall_height,
                "side_surface_target": (
                    "visible_clerestory_band"
                ),
                "front_surface_target": (
                    front_surface_target
                ),
                "rear_surface_target": (
                    rear_surface_target
                ),
                "side_facades": [],
                "end_facades": [],
                "oculus_meshes": [],
                "component_meshes": [],
                "triangles": [],
            }

        for facade_side in (
            "left",
            "right",
        ):
            facade = (
                AtlasFacadePanelBuilder
                .build_repeated_arches(
                    wall_quad=cls._side_wall_quad(
                        frame=frame,
                        facade_side=facade_side,
                        wall_height=wall_height,
                        main_nave_depth=main_nave_depth,
                        main_nave_width=main_nave_width,
                        min_z=side_wall_min_z,
                    ),
                    column_count=column_count,
                    row_count=1,
                    panel_width_ratio=(
                        facade_profile.opening_width_ratio
                    ),
                    panel_height_ratio=(
                        facade_profile.opening_height_ratio
                    ),
                    arch_height_ratio=0.50,
                    horizontal_margin_ratio=0.06,
                    vertical_margin_ratio=0.18,
                    depth_mm=model_depth_m,
                    embed_mm=model_embed_m,
                    arch_segments=arch_segments,
                    metadata={
                        "architectural_role": (
                            "church_main_nave_facade_bay"
                        ),
                        "surface_target": (
                            "visible_clerestory_band"
                        ),
                        "facade_side": facade_side,
                        "facade_rhythm": (
                            facade_profile.facade_rhythm
                        ),
                        "arch_shape": (
                            facade_profile.arch_shape
                        ),
                        "physical_action": (
                            resolved_window_action
                        ),
                        "resolved_size_mm": (
                            resolved_window_size_mm
                        ),
                    },
                )
            )

            side_facades.append(
                {
                    **facade,
                    "facade_side": facade_side,
                }
            )
            component_meshes.extend(
                facade["component_meshes"]
            )
            triangles.extend(
                facade["triangles"]
            )

        for facade_side in (
            "front",
            "rear",
        ):
            architectural_role = (
                "church_front_facade_opening"
                if facade_side == "front"
                else "church_rear_facade_opening"
            )
            facade_composition = (
                facade_profile.front_composition
                if facade_side == "front"
                else facade_profile.rear_composition
            )
            panel_width_ratio = (
                facade_profile.opening_width_ratio
            )
            panel_height_ratio = (
                facade_profile.opening_height_ratio
            )
            arch_height_ratio = 0.50

            if facade_side == "front":
                if (
                    facade_composition
                    == "portal_with_oculus"
                ):
                    panel_width_ratio = 0.34
                    panel_height_ratio = 0.42
                    arch_height_ratio = 1.00
                else:
                    panel_width_ratio = 0.28
                    panel_height_ratio = 0.34
                    arch_height_ratio = 0.50
            else:
                arch_height_ratio = (
                    1.00
                    if facade_composition
                    == "round_arch_opening"
                    else 0.35
                )

            if (
                facade_side == "front"
                and front_wall_quad is not None
            ):
                target_wall_quad = (
                    front_wall_quad
                )
            elif (
                facade_side == "rear"
                and rear_wall_quad is not None
            ):
                target_wall_quad = (
                    rear_wall_quad
                )
            else:
                target_wall_quad = (
                    cls._end_wall_quad(
                        frame=frame,
                        facade_side=facade_side,
                        wall_height=wall_height,
                        main_nave_depth=main_nave_depth,
                        main_nave_width=main_nave_width,
                    )
                )

            surface_target = (
                front_surface_target
                if facade_side == "front"
                else rear_surface_target
            )

            facade = (
                AtlasFacadePanelBuilder
                .build_repeated_arches(
                    wall_quad=target_wall_quad,
                    column_count=1,
                    row_count=1,
                    panel_width_ratio=(
                        panel_width_ratio
                    ),
                    panel_height_ratio=(
                        panel_height_ratio
                    ),
                    arch_height_ratio=(
                        arch_height_ratio
                    ),
                    horizontal_margin_ratio=0.18,
                    vertical_margin_ratio=0.18,
                    vertical_alignment=(
                        "bottom"
                        if facade_side == "front"
                        else "center"
                    ),
                    depth_mm=model_depth_m,
                    embed_mm=model_embed_m,
                    arch_segments=arch_segments,
                    metadata={
                        "architectural_role": (
                            architectural_role
                        ),
                        "facade_side": facade_side,
                        "surface_target": (
                            surface_target
                        ),
                        "facade_composition": (
                            facade_composition
                        ),
                        "facade_rhythm": (
                            facade_profile.facade_rhythm
                        ),
                        "arch_shape": (
                            facade_profile.arch_shape
                        ),
                        "physical_action": (
                            resolved_window_action
                        ),
                        "resolved_size_mm": (
                            resolved_window_size_mm
                        ),
                    },
                )
            )

            end_facades.append(
                {
                    **facade,
                    "facade_side": facade_side,
                    "surface_target": (
                        surface_target
                    ),
                    "facade_composition": (
                        facade_composition
                    ),
                    "arch_height_ratio": (
                        arch_height_ratio
                    ),
                    "panel_width_ratio": (
                        panel_width_ratio
                    ),
                    "panel_height_ratio": (
                        panel_height_ratio
                    ),
                }
            )
            component_meshes.extend(
                facade["component_meshes"]
            )
            triangles.extend(
                facade["triangles"]
            )

        if (
            facade_profile.front_composition
            == "portal_with_oculus"
        ):
            oculus = (
                AtlasFacadeCircularPanelBuilder.build(
                    wall_quad=(
                        front_wall_quad
                        if front_wall_quad is not None
                        else cls._end_wall_quad(
                            frame=frame,
                            facade_side="front",
                            wall_height=wall_height,
                            main_nave_depth=main_nave_depth,
                            main_nave_width=main_nave_width,
                        )
                    ),
                    center_u=0.50,
                    center_v=0.72,
                    diameter_ratio=0.22,
                    depth_mm=model_depth_m,
                    embed_mm=model_embed_m,
                    segments=16,
                    metadata={
                        "architectural_role": (
                            "church_front_facade_oculus"
                        ),
                        "facade_side": "front",
                        "surface_target": (
                            front_surface_target
                        ),
                        "facade_composition": (
                            facade_profile.front_composition
                        ),
                        "facade_rhythm": (
                            facade_profile.facade_rhythm
                        ),
                        "physical_action": (
                            resolved_window_action
                        ),
                        "resolved_size_mm": (
                            resolved_window_size_mm
                        ),
                    },
                )
            )

            oculus_meshes.append(
                oculus
            )
            component_meshes.append(
                oculus
            )
            triangles.extend(
                oculus["triangles"]
            )

        return {
            "type": "church_facade_system",
            "facade_rhythm": (
                facade_profile.facade_rhythm
            ),
            "arch_shape": facade_profile.arch_shape,
            "front_composition": (
                facade_profile.front_composition
            ),
            "rear_composition": (
                facade_profile.rear_composition
            ),
            "column_count_per_side": column_count,
            "row_count": 1,
            "main_nave_width": main_nave_width,
            "main_nave_depth": main_nave_depth,
            "panel_count": len(component_meshes),
            "physical_depth_mm": physical_depth_mm,
            "model_depth_m": model_depth_m,
            "window_action": resolved_window_action,
            "window_resolved_size_mm": (
                resolved_window_size_mm
            ),
            "side_wall_min_z": side_wall_min_z,
            "side_wall_max_z": wall_height,
            "side_surface_target": (
                "visible_clerestory_band"
            ),
            "front_surface_target": (
                front_surface_target
            ),
            "rear_surface_target": (
                rear_surface_target
            ),
            "side_facades": side_facades,
            "end_facades": end_facades,
            "oculus_meshes": oculus_meshes,
            "component_meshes": component_meshes,
            "triangles": triangles,
        }
