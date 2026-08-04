from __future__ import annotations

import math


class AtlasGalataBridgeCenterSectionBuilder:
    SUPPORT_LONGITUDINAL_POSITIONS = (
        0.12,
        0.88,
    )

    SUPPORT_DECK_EMBED_MM = 0.15
    FLARED_SUPPORT_WIDTH_RATIO = 1.35
    FLARED_SUPPORT_DEPTH_MM = 4.0
    FLARED_SUPPORT_CORE_WIDTH_RATIO = 0.88

    @staticmethod
    def _normalize_axis(axis):
        axis_x = float(axis[0])
        axis_y = float(axis[1])

        length = math.hypot(
            axis_x,
            axis_y,
        )

        if length <= 1e-12:
            raise ValueError(
                "axis must have non-zero length"
            )

        return (
            axis_x / length,
            axis_y / length,
        )

    @staticmethod
    def _oriented_box(
        *,
        center,
        axis,
        length_mm,
        width_mm,
        bottom_z,
        top_z,
        mesh_type,
        **metadata,
    ):
        center_x = float(center[0])
        center_y = float(center[1])

        axis_x, axis_y = axis
        normal_x = -axis_y
        normal_y = axis_x

        half_length = float(length_mm) * 0.5
        half_width = float(width_mm) * 0.5

        footprint = (
            (
                center_x
                - axis_x * half_length
                - normal_x * half_width,
                center_y
                - axis_y * half_length
                - normal_y * half_width,
            ),
            (
                center_x
                + axis_x * half_length
                - normal_x * half_width,
                center_y
                + axis_y * half_length
                - normal_y * half_width,
            ),
            (
                center_x
                + axis_x * half_length
                + normal_x * half_width,
                center_y
                + axis_y * half_length
                + normal_y * half_width,
            ),
            (
                center_x
                - axis_x * half_length
                + normal_x * half_width,
                center_y
                - axis_y * half_length
                + normal_y * half_width,
            ),
        )

        bottom = tuple(
            (
                float(x),
                float(y),
                float(bottom_z),
            )
            for x, y in footprint
        )

        top = tuple(
            (
                float(x),
                float(y),
                float(top_z),
            )
            for x, y in footprint
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
            "footprint": footprint,
            "bottom": bottom,
            "top": top,
            "triangles": triangles,
            "length_mm": float(length_mm),
            "width_mm": float(width_mm),
            "bottom_z": float(bottom_z),
            "top_z": float(top_z),
            **metadata,
        }

    @classmethod
    def _flared_support(
        cls,
        *,
        center,
        axis,
        width_mm,
        depth_mm,
        bottom_z,
        top_z,
        longitudinal_position,
    ):
        center_x = float(center[0])
        center_y = float(center[1])

        axis_x, axis_y = axis
        normal_x = -axis_y
        normal_y = axis_x

        half_depth = float(depth_mm) * 0.5
        outer_half_width = float(width_mm) * 0.5
        core_half_width = (
            outer_half_width
            * cls.FLARED_SUPPORT_CORE_WIDTH_RATIO
        )

        # Köprü ekseni boyunca ince; enine yönde iki yana
        # açılan ve uçlarda üçgenleşen taşıyıcı platform.
        local_points = (
            (-half_depth, -core_half_width),
            (0.0, -outer_half_width),
            (half_depth, -core_half_width),
            (half_depth, core_half_width),
            (0.0, outer_half_width),
            (-half_depth, core_half_width),
        )

        footprint = tuple(
            (
                center_x
                + axis_x * longitudinal
                + normal_x * lateral,
                center_y
                + axis_y * longitudinal
                + normal_y * lateral,
            )
            for longitudinal, lateral in local_points
        )

        bottom = tuple(
            (x, y, float(bottom_z))
            for x, y in footprint
        )
        top = tuple(
            (x, y, float(top_z))
            for x, y in footprint
        )

        triangles = []
        point_count = len(footprint)

        for index in range(1, point_count - 1):
            triangles.append(
                (
                    bottom[0],
                    bottom[index + 1],
                    bottom[index],
                )
            )
            triangles.append(
                (
                    top[0],
                    top[index],
                    top[index + 1],
                )
            )

        for index in range(point_count):
            next_index = (
                index + 1
            ) % point_count

            triangles.extend(
                (
                    (
                        bottom[index],
                        bottom[next_index],
                        top[next_index],
                    ),
                    (
                        bottom[index],
                        top[next_index],
                        top[index],
                    ),
                )
            )

        return {
            "type": "galata_bridge_flared_support",
            "footprint": footprint,
            "bottom": bottom,
            "top": top,
            "triangles": tuple(triangles),
            "length_mm": float(depth_mm),
            "width_mm": float(width_mm),
            "bottom_z": float(bottom_z),
            "top_z": float(top_z),
            "longitudinal_position": float(
                longitudinal_position
            ),
            "lateral_offset_mm": 0.0,
            "extends_beyond_deck": True,
            "footprint_shape": (
                "double_wedge_flared_platform"
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
        deck_bottom_z,
        deck_thickness_mm,
    ):
        normalized_axis = cls._normalize_axis(
            axis
        )

        total_span_mm = float(
            total_span_mm
        )
        deck_width_mm = float(
            deck_width_mm
        )
        center_section_ratio = float(
            center_section_ratio
        )
        foundation_z = float(
            foundation_z
        )
        deck_bottom_z = float(
            deck_bottom_z
        )
        deck_thickness_mm = float(
            deck_thickness_mm
        )

        if total_span_mm <= 0.0:
            raise ValueError(
                "total_span_mm must be positive"
            )

        if deck_width_mm <= 0.0:
            raise ValueError(
                "deck_width_mm must be positive"
            )

        if not 0.0 < center_section_ratio < 1.0:
            raise ValueError(
                "center_section_ratio must be inside 0..1"
            )

        if deck_bottom_z <= foundation_z:
            raise ValueError(
                "deck_bottom_z must be above foundation_z"
            )

        if deck_thickness_mm <= 0.0:
            raise ValueError(
                "deck_thickness_mm must be positive"
            )

        center_x = float(center[0])
        center_y = float(center[1])

        axis_x, axis_y = normalized_axis
        normal_x = -axis_y
        normal_y = axis_x

        section_length_mm = (
            total_span_mm
            * center_section_ratio
        )

        deck_top_z = (
            deck_bottom_z
            + deck_thickness_mm
        )

        deck = cls._oriented_box(
            center=(center_x, center_y),
            axis=normalized_axis,
            length_mm=section_length_mm,
            width_mm=deck_width_mm,
            bottom_z=deck_bottom_z,
            top_z=deck_top_z,
            mesh_type=(
                "galata_bridge_center_deck"
            ),
        )

        support_top_z = (
            deck_bottom_z
            + cls.SUPPORT_DECK_EMBED_MM
        )

        flared_support_width = (
            deck_width_mm
            * cls.FLARED_SUPPORT_WIDTH_RATIO
        )

        supports = []

        for position in (
            cls.SUPPORT_LONGITUDINAL_POSITIONS
        ):
            longitudinal_offset = (
                (position - 0.5)
                * section_length_mm
            )

            support_center = (
                center_x
                + axis_x * longitudinal_offset,
                center_y
                + axis_y * longitudinal_offset,
            )

            supports.append(
                cls._flared_support(
                    center=support_center,
                    axis=normalized_axis,
                    width_mm=flared_support_width,
                    depth_mm=(
                        cls.FLARED_SUPPORT_DEPTH_MM
                    ),
                    bottom_z=foundation_z,
                    top_z=support_top_z,
                    longitudinal_position=position,
                )
            )

        half_length = (
            section_length_mm * 0.5
        )
        half_width = (
            deck_width_mm * 0.5
        )

        def connection_edge(
            longitudinal_sign,
        ):
            longitudinal = (
                half_length
                * longitudinal_sign
            )

            return (
                (
                    center_x
                    + axis_x * longitudinal
                    - normal_x * half_width,
                    center_y
                    + axis_y * longitudinal
                    - normal_y * half_width,
                    deck_top_z,
                ),
                (
                    center_x
                    + axis_x * longitudinal
                    + normal_x * half_width,
                    center_y
                    + axis_y * longitudinal
                    + normal_y * half_width,
                    deck_top_z,
                ),
            )

        return {
            "type": (
                "galata_bridge_center_section"
            ),
            "deck": deck,
            "supports": tuple(supports),
            "storey_count": 1,
            "has_lower_storey": False,
            "clearance_bottom_z": foundation_z,
            "clearance_top_z": deck_bottom_z,
            "clearance_height_mm": (
                deck_bottom_z
                - foundation_z
            ),
            "left_connection_edge": (
                connection_edge(-1.0)
            ),
            "right_connection_edge": (
                connection_edge(1.0)
            ),
            "axis": normalized_axis,
            "center": (
                center_x,
                center_y,
            ),
            "length_mm": section_length_mm,
            "width_mm": deck_width_mm,
        }
