from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


class AtlasProductColorPreviewPNGRenderer:
    @staticmethod
    def _collect_triangles(scene: dict):
        collected = []

        for batch_name, batch in scene["material_batches"].items():
            rgb = tuple(channel / 255.0 for channel in batch["rgb"])

            for mesh in batch["meshes"]:
                for triangle in mesh.get("triangles", []):
                    collected.append(
                        {
                            "batch_name": batch_name,
                            "rgb": rgb,
                            "triangle": tuple(
                                tuple(float(value) for value in vertex)
                                for vertex in triangle
                            ),
                        }
                    )

        return collected

    @classmethod
    def render(
        cls,
        *,
        scene: dict,
        output_path,
        image_width_px: int = 1200,
        image_height_px: int = 1200,
    ) -> dict:
        if image_width_px <= 0 or image_height_px <= 0:
            raise ValueError("image dimensions must be positive")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        triangles = cls._collect_triangles(scene)

        figure = plt.figure(
            figsize=(
                image_width_px / 100.0,
                image_height_px / 100.0,
            ),
            dpi=100,
        )
        axis = figure.add_subplot(111, projection="3d")

        for item in triangles:
            polygon = Poly3DCollection(
                [item["triangle"]],
                facecolors=[item["rgb"]],
                edgecolors="none",
                linewidths=0.0,
            )
            axis.add_collection3d(polygon)

        outer_width_mm = float(scene["outer_width_mm"])
        outer_height_mm = float(scene["outer_height_mm"])

        half_width = outer_width_mm / 2.0
        half_height = outer_height_mm / 2.0

        axis.set_xlim(-half_width, half_width)
        axis.set_ylim(-half_height, half_height)

        if triangles:
            z_values = [
                vertex[2]
                for item in triangles
                for vertex in item["triangle"]
            ]
            minimum_z = min(z_values)
            maximum_z = max(z_values)
        else:
            minimum_z = 0.0
            maximum_z = 1.0

        z_span = max(maximum_z - minimum_z, 1.0)
        axis.set_zlim(
            minimum_z - (z_span * 0.05),
            maximum_z + (z_span * 0.15),
        )

        axis.set_box_aspect(
            (
                outer_width_mm,
                outer_height_mm,
                max(z_span * 8.0, outer_width_mm * 0.18),
            )
        )

        axis.view_init(
            elev=58.0,
            azim=-58.0,
        )

        axis.set_axis_off()
        figure.subplots_adjust(
            left=0.0,
            right=1.0,
            bottom=0.0,
            top=1.0,
        )

        figure.savefig(
            output_path,
            format="png",
            dpi=100,
            transparent=False,
            facecolor=(0.96, 0.96, 0.94),
            bbox_inches=None,
            pad_inches=0.0,
        )
        plt.close(figure)

        return {
            "type": "product_color_preview_png",
            "profile_name": scene["profile_name"],
            "output_path": output_path,
            "image_width_px": int(image_width_px),
            "image_height_px": int(image_height_px),
            "triangle_count": len(triangles),
            "camera": {
                "elevation_deg": 58.0,
                "azimuth_deg": -58.0,
            },
            "framing": {
                "outer_width_mm": outer_width_mm,
                "outer_height_mm": outer_height_mm,
                "x_min_mm": -half_width,
                "x_max_mm": half_width,
                "y_min_mm": -half_height,
                "y_max_mm": half_height,
            },
        }
