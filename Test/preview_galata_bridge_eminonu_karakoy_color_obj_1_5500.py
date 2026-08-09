from CORE.atlas_product_color_preview_obj_exporter import (
    AtlasProductColorPreviewOBJExporter,
)
from Test import (
    preview_galata_bridge_eminonu_karakoy_three_part_scene
    as source,
)


OUTPUT_PATH = (
    "OUTPUT/PREVIEW/"
    "galata_bridge_eminonu_karakoy_8_10_acceptance.obj"
)


def _meshes(group_name):
    return list(
        source.groups.get(
            group_name,
            (),
        )
    )


scene = {
    "profile_name": "GALATA_8_10_WATER_SHORELINE_ACCEPTANCE",
    "material_batches": {
        "terrain": {
            "rgb": (225, 220, 205),
            "meshes": _meshes("terrain"),
        },
        "buildings": {
            "rgb": (205, 190, 165),
            "meshes": _meshes("buildings"),
        },
        "roads": {
            "rgb": (105, 105, 105),
            "meshes": _meshes("roads"),
        },
        "parks": {
            "rgb": (105, 155, 95),
            "meshes": _meshes("parks"),
        },
        "trees": {
            "rgb": (55, 115, 65),
            "meshes": _meshes("trees"),
        },
        "water": {
            "rgb": (70, 145, 205),
            "meshes": _meshes("waters"),
        },
        "other_landmarks": {
            "rgb": (185, 120, 80),
            "meshes": list(
                source.retained_landmarks
            ),
        },
        "galata_bridge": {
            "rgb": (205, 55, 45),
            "meshes": list(
                source.prototype["meshes"]
            ),
        },
        "elevated_areas": {
            "rgb": (145, 135, 125),
            "meshes": _meshes("elevated_areas"),
        },
        "artworks": {
            "rgb": (175, 145, 65),
            "meshes": _meshes("artworks"),
        },
    },
}


result = AtlasProductColorPreviewOBJExporter.export(
    scene=scene,
    output_path=OUTPUT_PATH,
)


print()
print("=" * 88)
print("GALATA BRIDGE — 8.10 WATER/SHORELINE ACCEPTANCE OBJ")
print("=" * 88)
print("Profile            :", result["profile_name"])
print("Triangles          :", result["triangle_count"])
print("OBJ geometry       :", result["obj_path"])
print("MTL colors         :", result["mtl_path"])

for name, batch in scene["material_batches"].items():
    triangle_count = sum(
        len(mesh.get("triangles", ()))
        for mesh in batch["meshes"]
    )
    print(
        f"{name:19}: "
        f"{len(batch['meshes']):4d} meshes / "
        f"{triangle_count:6d} triangles"
    )

print("=" * 88)
