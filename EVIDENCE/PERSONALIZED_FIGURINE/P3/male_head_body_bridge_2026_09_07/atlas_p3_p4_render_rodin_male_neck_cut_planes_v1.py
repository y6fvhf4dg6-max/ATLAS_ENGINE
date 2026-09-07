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
OUTPUT = Path("/private/tmp/atlas_p3_p4_rodin_male_neck_cut_plane_candidates_v1.png")
BLEND = Path("/private/tmp/atlas_p3_p4_rodin_male_neck_cut_plane_candidates_v1.blend")

CANDIDATES = [
    (-0.375, "LOWER / Y=-0.375", (0.95, 0.48, 0.08, 1.0)),
    (-0.350, "LEADER / Y=-0.350", (0.12, 0.90, 0.30, 1.0)),
    (-0.300, "UPPER / Y=-0.300", (0.10, 0.62, 1.00, 1.0)),
]

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

local_vertices = [vertex.co.copy() for vertex in base.data.vertices]
z_min = min(vertex.z for vertex in local_vertices)
z_max = max(vertex.z for vertex in local_vertices)
z_center = (z_min + z_max) / 2.0
vertical_extent = z_max - z_min

expected_min = -0.95448899269104
expected_max = 0.9321897029876709

print("=== AXIS MAPPING CHECK ===")
print(f"BLENDER_LOCAL_Z_MIN={z_min}")
print(f"BLENDER_LOCAL_Z_MAX={z_max}")
print(f"EXPECTED_RODIN_Y_MIN={expected_min}")
print(f"EXPECTED_RODIN_Y_MAX={expected_max}")

if abs(z_min - expected_min) > 1e-5 or abs(z_max - expected_max) > 1e-5:
    raise RuntimeError("RODIN_Y_TO_BLENDER_Z_MAPPING_NOT_VERIFIED")

bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")

body_material = bpy.data.materials.new("ATLAS_RODIN_MALE_BODY")
body_material.diffuse_color = (0.70, 0.73, 0.78, 1.0)
body_material.metallic = 0.0
body_material.roughness = 0.78
base.data.materials.clear()
base.data.materials.append(body_material)

for polygon in base.data.polygons:
    polygon.use_smooth = False

display_scale = 14.0 / vertical_extent
panels = [
    ("FRONT", -6.5, 0.0),
    ("RIGHT PROFILE", 6.5, 90.0),
]

for index, (panel_label, panel_x, angle) in enumerate(panels):
    if index == 0:
        obj = base
    else:
        obj = base.copy()
        obj.data = base.data.copy()
        bpy.context.collection.objects.link(obj)

    obj.name = f"RODIN_MALE_{panel_label.replace(' ', '_')}"
    obj.scale = (display_scale, display_scale, display_scale)
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (0.0, 0.0, math.radians(angle))
    obj.location = (panel_x, 0.0, 0.0)

    bpy.ops.object.text_add(location=(panel_x, -5.3, -8.2))
    panel_text = bpy.context.active_object
    panel_text.data.body = panel_label
    panel_text.data.align_x = "CENTER"
    panel_text.data.align_y = "CENTER"
    panel_text.data.size = 0.60
    panel_text.rotation_euler = (math.radians(90.0), 0.0, 0.0)

    panel_material = bpy.data.materials.get("ATLAS_PANEL_LABEL")
    if panel_material is None:
        panel_material = bpy.data.materials.new("ATLAS_PANEL_LABEL")
        panel_material.diffuse_color = (0.88, 0.90, 0.94, 1.0)
    panel_text.data.materials.append(panel_material)

    for candidate_y, label, color in CANDIDATES:
        marker_z = (candidate_y - z_center) * display_scale

        marker_material_name = "MARKER_" + label.split("/")[0].strip()
        marker_material = bpy.data.materials.get(marker_material_name)
        if marker_material is None:
            marker_material = bpy.data.materials.new(marker_material_name)
            marker_material.diffuse_color = color

        bpy.ops.mesh.primitive_cube_add(
            location=(panel_x, -5.0, marker_z)
        )
        marker = bpy.context.active_object
        marker.name = (
            f"CUT_PLANE_{candidate_y:+.3f}_"
            f"{panel_label.replace(' ', '_')}"
        )
        marker.scale = (5.55, 0.025, 0.035)
        marker.data.materials.append(marker_material)

        bpy.ops.object.text_add(
            location=(panel_x - 5.45, -5.3, marker_z + 0.23)
        )
        marker_text = bpy.context.active_object
        marker_text.data.body = f"{candidate_y:+.3f}"
        marker_text.data.align_x = "LEFT"
        marker_text.data.align_y = "CENTER"
        marker_text.data.size = 0.34
        marker_text.rotation_euler = (
            math.radians(90.0), 0.0, 0.0
        )
        marker_text.data.materials.append(marker_material)

bpy.ops.object.text_add(location=(0.0, -5.3, 9.2))
title = bpy.context.active_object
title.data.body = "RODIN MALE — LOWER-NECK CUT-PLANE CANDIDATES"
title.data.align_x = "CENTER"
title.data.align_y = "CENTER"
title.data.size = 0.72
title.rotation_euler = (math.radians(90.0), 0.0, 0.0)
title.data.materials.append(bpy.data.materials["ATLAS_PANEL_LABEL"])

camera_data = bpy.data.cameras.new("ATLAS_ORTHO_CAMERA")
camera = bpy.data.objects.new("ATLAS_ORTHO_CAMERA", camera_data)
bpy.context.collection.objects.link(camera)
bpy.context.scene.camera = camera
camera.location = (0.0, -38.0, 0.5)
camera.rotation_euler = (
    Vector((0.0, 0.0, 0.5)) - camera.location
).to_track_quat("-Z", "Y").to_euler()
camera.data.type = "ORTHO"
camera.data.ortho_scale = 20.5

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.background_type = "VIEWPORT"
scene.display.shading.background_color = (0.025, 0.030, 0.040)
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = "WORLD"
scene.display.shading.curvature_ridge_factor = 1.5
scene.display.shading.curvature_valley_factor = 1.2
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.filepath = str(OUTPUT)

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
bpy.ops.render.render(write_still=True)

print("\n=== VISUAL CUT-PLANE OUTPUT ===")
for candidate_y, label, _ in CANDIDATES:
    marker_z = (candidate_y - z_center) * display_scale
    print(
        f"CANDIDATE={label}|RODIN_Y={candidate_y:.3f}"
        f"|DISPLAY_Z={marker_z:.9f}"
    )
print(f"OUTPUT={OUTPUT}")
print(f"OUTPUT_EXISTS={OUTPUT.is_file()}")
print(f"OUTPUT_BYTES={OUTPUT.stat().st_size if OUTPUT.is_file() else 0}")
print("SOURCE_GEOMETRY_CHANGED=NO")
print("CUT_PERFORMED=NO")
print("STATUS=READY_FOR_HUMAN_CUT_PLANE_DECISION")
