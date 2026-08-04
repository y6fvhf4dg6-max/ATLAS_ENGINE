from CORE.atlas_product_color_preview_obj_exporter import (
    AtlasProductColorPreviewOBJExporter,
)
from Test import (
    preview_galata_bridge_eminonu_karakoy_multicolor_1_5500
    as source,
)


OUTPUT_PATH = (
    "OUTPUT/PREVIEW/"
    "galata_bridge_eminonu_karakoy_color_1_5500.obj"
)


result = AtlasProductColorPreviewOBJExporter.export(
    scene=source.color_scene,
    output_path=OUTPUT_PATH,
)

print()
print("=" * 88)
print("GALATA BRIDGE — COLOR OBJ 1:5500")
print("=" * 88)
print("Profile            :", result["profile_name"])
print("Triangles          :", result["triangle_count"])
print("OBJ geometry       :", result["obj_path"])
print("MTL colors         :", result["mtl_path"])
print("=" * 88)
