from __future__ import annotations

import math

from CORE.atlas_galata_bridge_center_section_builder import (
    AtlasGalataBridgeCenterSectionBuilder,
)


class AtlasGalataBridgeThreePartBuilder:
    LOWER_STOREY_TOP_RATIO = 0.55

    @staticmethod
    def _normalize_axis(axis):
        axis_x = float(axis[0])
        axis_y = float(axis[1])

        length = math.hypot(axis_x, axis_y)

        if length <= 1e-12:
            raise ValueError(
                "axis must have non-zero length"
            )

        return (
            axis_x / length,
            axis_y / length,
        )

    @staticmethod
    def _build_sloped_prism(
        *,
        outer_edge,
        inner_edge,
        outer_bottom_z,
        outer_top_z,
        inner_bottom_z,
        inner_top_z,
        mesh_type,
        **metadata,
    ):
        outer_left, outer_right = outer_edge
        inner_left, inner_right = inner_edge

        bottom = (
            (
                float(outer_left[0]),
                float(outer_left[1]),
                float(outer_bottom_z),
            ),
            (
                float(inner_left[0]),
                float(inner_left[1]),
                float(inner_bottom_z),
            ),
            (
                float(inner_right[0]),
                float(inner_right[1]),
                float(inner_bottom_z),
            ),
            (
                float(outer_right[0]),
                float(outer_right[1]),
                float(outer_bottom_z),
            ),
        )

        top = (
            (
                float(outer_left[0]),
                float(outer_left[1]),
                float(outer_top_z),
            ),
            (
                float(inner_left[0]),
                float(inner_left[1]),
                float(inner_top_z),
            ),
            (
                float(inner_right[0]),
                float(inner_right[1]),
                float(inner_top_z),
            ),
            (
                float(outer_right[0]),
                float(outer_right[1]),
                float(outer_top_z),
            ),
        )

        triangles = (
            (bottom[0], bottom[2], bottom[1]),
            (bottom[0], bottom[3], bottom[2]),
            (top[0], top[1], top[2]),
            (top[0], top[2], top[3]),
            (bottom[0], bottom[1], top[1]),
            (bottom[0], top[1], top[0]),
            (bottom[1], bottom[2], top[2]),
            (bottom[1], top[2], top[1]),
            (bottom[2], bottom[3], top[3]),
            (bottom[2], top[3], top[2]),
            (bottom[3], bottom[0], top[0]),
            (bottom[3], top[0], top[3]),
        )

        return {
            "type": mesh_type,
            "bottom": bottom,
            "top": top,
            "triangles": triangles,
            **metadata,
        }

    @classmethod
    def _build_side_section(
        cls,
        *,
        side,
        center,
        axis,
        normal,
        side_length_mm,
        deck_width_mm,
        center_half_length_mm,
        foundation_z,
        center_deck_bottom_z,
        deck_thickness_mm,
        left_extension_mm=0.0,
        right_extension_mm=0.0,
    ):
        center_x, center_y = center
        axis_x, axis_y = axis
        normal_x, normal_y = normal

        direction = -1.0 if side == "left" else 1.0

        inner_longitudinal = (
            direction * center_half_length_mm
        )
        outer_longitudinal = (
            direction
            * (
                center_half_length_mm
                + side_length_mm
            )
        )

        half_width = deck_width_mm * 0.5

        def edge(longitudinal):
            return (
                (
                    center_x
                    + axis_x * longitudinal
                    - normal_x * half_width,
                    center_y
                    + axis_y * longitudinal
                    - normal_y * half_width,
                ),
                (
                    center_x
                    + axis_x * longitudinal
                    + normal_x * half_width,
                    center_y
                    + axis_y * longitudinal
                    + normal_y * half_width,
                ),
            )

        inner_edge = edge(inner_longitudinal)
        outer_edge = edge(outer_longitudinal)

        if side == "right":
            outer_edge = (
                outer_edge[1],
                outer_edge[0],
            )
            inner_edge = (
                inner_edge[1],
                inner_edge[0],
            )

        inner_bottom_z = float(
            center_deck_bottom_z
        )
        inner_top_z = (
            inner_bottom_z
            + float(deck_thickness_mm)
        )

        outer_bottom_z = float(foundation_z)
        outer_top_z = (
            outer_bottom_z
            + float(deck_thickness_mm)
        )

        lower_outer_top_z = (
            foundation_z
            + deck_thickness_mm
        )

        upper_deck = cls._build_sloped_prism(
            outer_edge=outer_edge,
            inner_edge=inner_edge,
            outer_bottom_z=lower_outer_top_z,
            outer_top_z=(
                lower_outer_top_z
                + deck_thickness_mm
            ),
            inner_bottom_z=inner_bottom_z,
            inner_top_z=inner_top_z,
            mesh_type=(
                f"galata_bridge_{side}_upper_deck"
            ),
        )

        lower_inner_top_z = (
            foundation_z
            + (
                center_deck_bottom_z
                - foundation_z
            )
            * cls.LOWER_STOREY_TOP_RATIO
        )

        lower_storey = cls._build_sloped_prism(
            outer_edge=outer_edge,
            inner_edge=inner_edge,
            outer_bottom_z=foundation_z,
            outer_top_z=(
                foundation_z
                + deck_thickness_mm
            ),
            inner_bottom_z=foundation_z,
            inner_top_z=lower_inner_top_z,
            mesh_type=(
                f"galata_bridge_{side}_lower_storey"
            ),
        )

        return {
            "type": (
                f"galata_bridge_{side}_section"
            ),
            "side": side,
            "length_mm": float(side_length_mm),
            "width_mm": float(deck_width_mm),
            "storey_count": 2,
            "has_lower_storey": True,
            "lower_storey": lower_storey,
            "upper_deck": upper_deck,
            "outer_bottom_z": outer_bottom_z,
            "outer_top_z": outer_top_z,
            "inner_bottom_z": inner_bottom_z,
            "inner_top_z": inner_top_z,
            "outer_touches_foundation": True,
            "outer_edge": outer_edge,
            "inner_edge": inner_edge,
            "meshes": (
                lower_storey,
                upper_deck,
            ),
        }

    @classmethod
    def build(
        cls,
        *,
        center,
        axis,
        total_span_mm,
        deck_width_mm,
        center_section_ratio,
        foundation_z,
        center_deck_bottom_z,
        deck_thickness_mm,
        left_extension_mm=0.0,
        right_extension_mm=0.0,
    ):
        axis = cls._normalize_axis(axis)

        total_span_mm = float(total_span_mm)
        deck_width_mm = float(deck_width_mm)
        center_section_ratio = float(
            center_section_ratio
        )
        left_extension_mm = float(
            left_extension_mm
        )
        right_extension_mm = float(
            right_extension_mm
        )

        if total_span_mm <= 0.0:
            raise ValueError(
                "total_span_mm must be positive"
            )

        if not 0.0 < center_section_ratio < 1.0:
            raise ValueError(
                "center_section_ratio must be inside 0..1"
            )

        if left_extension_mm < 0.0:
            raise ValueError(
                "left_extension_mm must not be negative"
            )

        if right_extension_mm < 0.0:
            raise ValueError(
                "right_extension_mm must not be negative"
            )

        normal = (
            -axis[1],
            axis[0],
        )

        center_section = (
            AtlasGalataBridgeCenterSectionBuilder
            .build(
                center=center,
                axis=axis,
                total_span_mm=total_span_mm,
                deck_width_mm=deck_width_mm,
                center_section_ratio=(
                    center_section_ratio
                ),
                foundation_z=foundation_z,
                deck_bottom_z=(
                    center_deck_bottom_z
                ),
                deck_thickness_mm=(
                    deck_thickness_mm
                ),
            )
        )

        center_length_mm = (
            total_span_mm
            * center_section_ratio
        )

        base_side_length_mm = (
            total_span_mm
            - center_length_mm
        ) * 0.5

        left_side_length_mm = (
            base_side_length_mm
            + left_extension_mm
        )

        right_side_length_mm = (
            base_side_length_mm
            + right_extension_mm
        )

        effective_total_span_mm = (
            total_span_mm
            + left_extension_mm
            + right_extension_mm
        )

        center_half_length_mm = (
            center_length_mm * 0.5
        )

        left = cls._build_side_section(
            side="left",
            center=center,
            axis=axis,
            normal=normal,
            side_length_mm=left_side_length_mm,
            deck_width_mm=deck_width_mm,
            center_half_length_mm=(
                center_half_length_mm
            ),
            foundation_z=foundation_z,
            center_deck_bottom_z=(
                center_deck_bottom_z
            ),
            deck_thickness_mm=(
                deck_thickness_mm
            ),
        )

        right = cls._build_side_section(
            side="right",
            center=center,
            axis=axis,
            normal=normal,
            side_length_mm=right_side_length_mm,
            deck_width_mm=deck_width_mm,
            center_half_length_mm=(
                center_half_length_mm
            ),
            foundation_z=foundation_z,
            center_deck_bottom_z=(
                center_deck_bottom_z
            ),
            deck_thickness_mm=(
                deck_thickness_mm
            ),
        )

        center_meshes = (
            center_section["deck"],
            *center_section["supports"],
        )

        meshes = (
            *left["meshes"],
            *center_meshes,
            *right["meshes"],
        )

        return {
            "type": (
                "galata_bridge_three_part"
            ),
            "sections": {
                "left": left,
                "center": center_section,
                "right": right,
            },
            "left": left,
            "center": center_section,
            "right": right,
            "total_span_mm": effective_total_span_mm,
            "source_span_mm": total_span_mm,
            "left_extension_mm": left_extension_mm,
            "right_extension_mm": right_extension_mm,
            "deck_width_mm": deck_width_mm,
            "center_section_ratio": (
                center_section_ratio
            ),
            "meshes": meshes,
        }
