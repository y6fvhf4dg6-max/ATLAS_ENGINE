from __future__ import annotations

import math


class AtlasFacadeArchBandMesher:
    @staticmethod
    def _positive(value, *, name):
        numeric = float(value)

        if not math.isfinite(numeric) or numeric <= 0.0:
            raise ValueError(
                f"{name} must be finite and greater than zero"
            )

        return numeric

    @classmethod
    def build(
        cls,
        *,
        center_x_mm,
        bottom_z_mm,
        outer_width_mm,
        outer_height_mm,
        band_width_mm,
        depth_mm,
        front_y_mm=0.0,
        arch_segments=16,
        arch_height_ratio=0.55,
        metadata=None,
    ):
        center_x_mm = float(center_x_mm)
        bottom_z_mm = float(bottom_z_mm)
        front_y_mm = float(front_y_mm)

        outer_width_mm = cls._positive(
            outer_width_mm,
            name="outer_width_mm",
        )
        outer_height_mm = cls._positive(
            outer_height_mm,
            name="outer_height_mm",
        )
        band_width_mm = cls._positive(
            band_width_mm,
            name="band_width_mm",
        )
        depth_mm = cls._positive(
            depth_mm,
            name="depth_mm",
        )
        arch_height_ratio = cls._positive(
            arch_height_ratio,
            name="arch_height_ratio",
        )

        arch_segments = int(
            arch_segments
        )

        if arch_segments < 4:
            raise ValueError(
                "arch_segments must be at least four"
            )

        if band_width_mm * 2.0 >= outer_width_mm:
            raise ValueError(
                "band_width_mm is too large for outer_width_mm"
            )

        if band_width_mm * 2.0 >= outer_height_mm:
            raise ValueError(
                "band_width_mm is too large for outer_height_mm"
            )

        outer_half_width = (
            outer_width_mm / 2.0
        )

        outer_arch_rise = min(
            outer_height_mm - band_width_mm,
            outer_half_width * arch_height_ratio,
        )

        outer_spring_z = (
            bottom_z_mm
            + outer_height_mm
            - outer_arch_rise
        )

        outer_top_z = (
            bottom_z_mm
            + outer_height_mm
        )

        inner_half_width = (
            outer_half_width
            - band_width_mm
        )

        inner_bottom_z = (
            bottom_z_mm
            + band_width_mm
        )

        inner_top_z = (
            outer_top_z
            - band_width_mm
        )

        inner_arch_rise = max(
            band_width_mm,
            outer_arch_rise - band_width_mm,
        )

        inner_spring_z = (
            inner_top_z
            - inner_arch_rise
        )

        def contour(
            *,
            half_width,
            bottom_z,
            spring_z,
            top_z,
        ):
            points = [
                (
                    center_x_mm - half_width,
                    bottom_z,
                ),
                (
                    center_x_mm - half_width,
                    spring_z,
                ),
            ]

            rise = (
                top_z - spring_z
            )

            for index in range(
                1,
                arch_segments,
            ):
                fraction = (
                    index / arch_segments
                )

                angle = (
                    math.pi
                    - fraction * math.pi
                )

                x = (
                    center_x_mm
                    + half_width
                    * math.cos(angle)
                )

                z = (
                    spring_z
                    + rise
                    * math.sin(angle)
                )

                points.append(
                    (x, z)
                )

            points.extend(
                (
                    (
                        center_x_mm + half_width,
                        spring_z,
                    ),
                    (
                        center_x_mm + half_width,
                        bottom_z,
                    ),
                )
            )

            return tuple(
                points
            )

        outer = contour(
            half_width=outer_half_width,
            bottom_z=bottom_z_mm,
            spring_z=outer_spring_z,
            top_z=outer_top_z,
        )

        inner = contour(
            half_width=inner_half_width,
            bottom_z=inner_bottom_z,
            spring_z=inner_spring_z,
            top_z=inner_top_z,
        )

        if len(outer) != len(inner):
            raise RuntimeError(
                "outer and inner contours must have matching vertices"
            )

        back_y_mm = (
            front_y_mm - depth_mm
        )

        triangles = []

        count = len(
            outer
        )

        for index in range(count):
            next_index = (
                (index + 1) % count
            )

            ox0, oz0 = outer[index]
            ox1, oz1 = outer[next_index]

            ix0, iz0 = inner[index]
            ix1, iz1 = inner[next_index]

            of0 = (
                ox0,
                front_y_mm,
                oz0,
            )
            of1 = (
                ox1,
                front_y_mm,
                oz1,
            )
            inf0 = (
                ix0,
                front_y_mm,
                iz0,
            )
            inf1 = (
                ix1,
                front_y_mm,
                iz1,
            )

            ob0 = (
                ox0,
                back_y_mm,
                oz0,
            )
            ob1 = (
                ox1,
                back_y_mm,
                oz1,
            )
            inb0 = (
                ix0,
                back_y_mm,
                iz0,
            )
            inb1 = (
                ix1,
                back_y_mm,
                iz1,
            )

            # Front annular strip.
            triangles.extend(
                (
                    (
                        of0,
                        of1,
                        inf1,
                    ),
                    (
                        of0,
                        inf1,
                        inf0,
                    ),
                )
            )

            # Back annular strip.
            triangles.extend(
                (
                    (
                        ob0,
                        inb1,
                        ob1,
                    ),
                    (
                        ob0,
                        inb0,
                        inb1,
                    ),
                )
            )

            # Outer perimeter wall.
            triangles.extend(
                (
                    (
                        of0,
                        ob1,
                        of1,
                    ),
                    (
                        of0,
                        ob0,
                        ob1,
                    ),
                )
            )

            # Inner perimeter wall.
            triangles.extend(
                (
                    (
                        inf0,
                        inf1,
                        inb1,
                    ),
                    (
                        inf0,
                        inb1,
                        inb0,
                    ),
                )
            )

        result = {
            "type": "facade_arch_band_mesh",
            "component_type": "facade_arch_band",
            "source_system": "facade_arch_band_mesher",
            "triangles": triangles,
            "outer_width_mm": outer_width_mm,
            "outer_height_mm": outer_height_mm,
            "band_width_mm": band_width_mm,
            "depth_mm": depth_mm,
            "arch_segments": arch_segments,
            "arch_height_ratio": arch_height_ratio,
        }

        if metadata:
            result.update(
                dict(metadata)
            )

        return result
