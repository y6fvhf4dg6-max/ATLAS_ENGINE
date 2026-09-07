import bpy
import math
from pathlib import Path
from mathutils import Vector

SOURCE = Path(
    "/Users/Kubi/ATLAS_ENGINE/"
    "EVIDENCE/PERSONALIZED_FIGURINE/P3/"
    "rodin_v2_5_synthetic_benchmark_2026_09_07/male/"
    "rodin_v2_5_minimum_50k_quad_texture_high_shaded.glb"
)
OUTPUT = Path("/private/tmp/atlas_p3_p4_rodin_male_source_four_view_v1.png")
BLEND = Path("/private/tmp/atlas_p3_p4_rodin_male_source_four_view_v1.blend")

if not SOURCE.is_file():
    raise RuntimeError(f"MISSING_SOURCE={SOURCE}")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

bpy.ops.import_scene.gltf(filepath=str(SOURCE))
mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]

if len(mesh_objects) != 1:
    raise RuntimeError(f"UNEXPECTED_MESH_OBJECT_COUNT={len(mesh_objects)}")

base = mesh_objects[0]
bpy.context.view_layer.objects.active = base
base.select_set(True)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")

material = bpy.data.materials.new("ATLAS_RODIN_MALE_GEOMETRY")
material.diffuse_color = (0.74, 0.77, 0.82, 1.0)
material.metallic = 0.0
material.roughness = 0.75
base.data.materials.clear()
base.data.materials.append(material)

for polygon in base.data.polygons:
    polygon.use_smooth = False

vertical_extent = max(float(base.dimensions.z), 1e-9)
display_scale = 14.0 / vertical_extent

placements = [
    ("0 DEG",   -8.5,  10.0,   0.0),
    ("90 DEG",   8.5,  10.0,  90.0),
    ("180 DEG", -8.5,  -9.0, 180.0),
    ("270 DEG",  8.5,  -9.0, 270.0),
]

for index, (label, x_pos, z_pos, angle) in enumerate(placements):
    if index == 0:
        obj = base
    else:
        obj = base.copy()
        obj.data = base.data.copy()
        bpy.context.collection.objects.link(obj)

    obj.name = f"RODIN_MALE_{int(angle):03d}"
    obj.scale = (display_scale, display_scale, display_scale)
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (0.0, 0.0, math.radians(angle))
    obj.location = (x_pos, 0.0, z_pos)

    bpy.ops.object.text_add(location=(x_pos, -3.5, z_pos - 8.0))
    text_obj = bpy.context.active_object
    text_obj.data.body = label
    text_obj.data.align_x = "CENTER"
    text_obj.data.align_y = "CENTER"
    text_obj.data.size = 0.75
    text_obj.rotation_euler = (math.radians(90.0), 0.0, 0.0)

    label_material = bpy.data.materials.get("ATLAS_LABEL")
    if label_material is None:
        label_material = bpy.data.materials.new("ATLAS_LABEL")
        label_material.diffuse_color = (0.86, 0.88, 0.92, 1.0)
    text_obj.data.materials.append(label_material)

bpy.ops.object.text_add(location=(0.0, -3.5, 20.5))
title = bpy.context.active_object
title.data.body = "RODIN V2.5 MALE — ORIGINAL SOURCE ENVELOPE"
title.data.align_x = "CENTER"
title.data.align_y = "CENTER"
title.data.size = 0.95
title.rotation_euler = (math.radians(90.0), 0.0, 0.0)
title.data.materials.append(bpy.data.materials["ATLAS_LABEL"])

camera_data = bpy.data.cameras.new("ATLAS_ORTHO_CAMERA")
camera = bpy.data.objects.new("ATLAS_ORTHO_CAMERA", camera_data)
bpy.context.collection.objects.link(camera)
bpy.context.scene.camera = camera
camera.location = (0.0, -52.0, 1.0)
camera.rotation_euler = (
    Vector((0.0, 0.0, 1.0)) - camera.location
).to_track_quat("-Z", "Y").to_euler()
camera.data.type = "ORTHO"
camera.data.ortho_scale = 44.0

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.background_type = "VIEWPORT"
scene.display.shading.background_color = (0.035, 0.040, 0.050)
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = "WORLD"
scene.display.shading.curvature_ridge_factor = 1.5
scene.display.shading.curvature_valley_factor = 1.2
scene.render.resolution_x = 1600
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.filepath = str(OUTPUT)

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
bpy.ops.render.render(write_still=True)

print("=== RODIN MALE VISUAL ENVELOPE ===")
print(f"SOURCE={SOURCE}")
print(f"OUTPUT={OUTPUT}")
print(f"OUTPUT_EXISTS={OUTPUT.is_file()}")
print(f"OUTPUT_BYTES={OUTPUT.stat().st_size if OUTPUT.is_file() else 0}")
print("SOURCE_GEOMETRY_CHANGED=NO")
print("MAKEHUMAN_BODY_ATTACHED=NO")
print("STATUS=READY_FOR_HEAD_NECK_SHOULDER_ENVELOPE_DECISION")
