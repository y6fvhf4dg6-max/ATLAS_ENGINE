from __future__ import annotations

from pathlib import Path


class AtlasProductColorPreviewOBJExporter:
    @staticmethod
    def _material_name(batch_name: str) -> str:
        return str(batch_name).strip().replace(" ", "_")

    @classmethod
    def export(
        cls,
        *,
        scene: dict,
        output_path,
    ) -> dict:
        obj_path = Path(output_path)

        if obj_path.suffix.lower() != ".obj":
            raise ValueError("output_path must use the .obj extension")

        obj_path.parent.mkdir(parents=True, exist_ok=True)
        mtl_path = obj_path.with_suffix(".mtl")

        obj_lines = [
            f"mtllib {mtl_path.name}",
            "",
        ]
        mtl_lines = []
        vertex_index = 1
        triangle_count = 0

        for batch_name, batch in scene["material_batches"].items():
            material_name = cls._material_name(batch_name)
            red, green, blue = (
                float(channel) / 255.0
                for channel in batch["rgb"]
            )

            mtl_lines.extend(
                [
                    f"newmtl {material_name}",
                    f"Kd {red:.6f} {green:.6f} {blue:.6f}",
                    "Ka 0.000000 0.000000 0.000000",
                    "Ks 0.000000 0.000000 0.000000",
                    "d 1.000000",
                    "illum 1",
                    "",
                ]
            )

            batch_has_triangles = False

            for mesh in batch["meshes"]:
                for triangle in mesh.get("triangles", []):
                    if not batch_has_triangles:
                        obj_lines.extend(
                            [
                                f"o {material_name}",
                                f"usemtl {material_name}",
                            ]
                        )
                        batch_has_triangles = True

                    for x, y, z in triangle:
                        obj_lines.append(
                            f"v {float(x):.9f} "
                            f"{float(y):.9f} "
                            f"{float(z):.9f}"
                        )

                    obj_lines.append(
                        f"f {vertex_index} "
                        f"{vertex_index + 1} "
                        f"{vertex_index + 2}"
                    )

                    vertex_index += 3
                    triangle_count += 1

            if batch_has_triangles:
                obj_lines.append("")

        obj_path.write_text(
            "\n".join(obj_lines).rstrip() + "\n",
            encoding="utf-8",
        )
        mtl_path.write_text(
            "\n".join(mtl_lines).rstrip() + "\n",
            encoding="utf-8",
        )

        return {
            "type": "product_color_preview_obj",
            "profile_name": scene["profile_name"],
            "obj_path": obj_path,
            "mtl_path": mtl_path,
            "triangle_count": triangle_count,
        }
