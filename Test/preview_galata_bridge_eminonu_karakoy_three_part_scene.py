import math
from pathlib import Path

from CORE.atlas_bridge_landmark_deduplicator import (
    AtlasBridgeLandmarkDeduplicator,
)
from CORE.atlas_coordinate_engine import AtlasCoordinateEngine
from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)
from CORE.atlas_galata_bridge_three_part_builder import (
    AtlasGalataBridgeThreePartBuilder,
)
from CORE.atlas_local_osm_reader import AtlasLocalOSMReader
from EXPORT.atlas_stl_writer import AtlasSTLWriter


PBF_PATH = "Data/OSM/galata-bridge-test.osm.pbf"

BASE_OUTPUT_PATH = (
    "OUTPUT/STL/"
    "galata_bridge_eminonu_karakoy_base_1_5500.stl"
)

OUTPUT_PATH = (
    "OUTPUT/STL/"
    "galata_bridge_eminonu_karakoy_three_part_1_5500.stl"
)

BBOX = (
    41.01476522,
    28.96589663,
    41.02563478,
    28.98030337,
)

SCALE_RATIO = 5500.0
PRODUCT_SIZE_MM = 220.0
GALATA_WIKIDATA = "Q81523"


def resolve_bridge_frame(footprint):
    center_x = (
        sum(x for x, _ in footprint)
        / len(footprint)
    )
    center_y = (
        sum(y for _, y in footprint)
        / len(footprint)
    )

    covariance_xx = sum(
        (x - center_x) ** 2
        for x, _ in footprint
    )
    covariance_yy = sum(
        (y - center_y) ** 2
        for _, y in footprint
    )
    covariance_xy = sum(
        (x - center_x) * (y - center_y)
        for x, y in footprint
    )

    angle = 0.5 * math.atan2(
        2.0 * covariance_xy,
        covariance_xx - covariance_yy,
    )

    axis = (
        math.cos(angle),
        math.sin(angle),
    )
    normal = (
        -axis[1],
        axis[0],
    )

    longitudinal_values = tuple(
        (
            (x - center_x) * axis[0]
            + (y - center_y) * axis[1]
        )
        for x, y in footprint
    )

    lateral_values = sorted(
        abs(
            (x - center_x) * normal[0]
            + (y - center_y) * normal[1]
        )
        for x, y in footprint
    )

    total_span_mm = (
        max(longitudinal_values)
        - min(longitudinal_values)
    )

    median_lateral = lateral_values[
        len(lateral_values) // 2
    ]

    core_values = [
        value
        for value in lateral_values
        if value <= median_lateral
    ]

    deck_width_mm = (
        2.0
        * sum(core_values)
        / len(core_values)
    )

    return {
        "center": (
            center_x,
            center_y,
        ),
        "axis": axis,
        "total_span_mm": total_span_mm,
        "deck_width_mm": deck_width_mm,
    }


result = AtlasFoundationFirstEngine.generate_city_stl(
    pbf_path=PBF_PATH,
    bbox=BBOX,
    output_path=BASE_OUTPUT_PATH,
    target_size_mm=PRODUCT_SIZE_MM,
    bed_width_mm=256,
    bed_depth_mm=256,
    margin_mm=15,
    max_buildings=None,
    min_points=4,
    max_points=300,
    z_scale=SCALE_RATIO,
    terrain_provider_name="srtm",
    terrain_smoothing_passes=0,
    water_surface_texture_amplitude_mm=0.10,
    water_surface_texture_wavelength_x_mm=9.0,
    water_surface_texture_wavelength_y_mm=13.0,
    water_surface_texture_edge_fade_mm=1.5,
    water_surface_texture_maximum_edge_length_mm=3.0,
    strict_input_quality=False,
    nature_provider_names=(),
    fixed_xy_scale=SCALE_RATIO,
    use_fixed_xy_scale=True,
    debug=False,
)

groups = result["mesh_groups"]

old_galata_meshes = [
    mesh
    for mesh in groups.get("landmarks", ())
    if (
        (mesh.get("tags", {}) or {}).get(
            "wikidata"
        )
        == GALATA_WIKIDATA
    )
]

if len(old_galata_meshes) != 1:
    raise RuntimeError(
        "Expected exactly one generated Galata Bridge mesh, "
        f"found {len(old_galata_meshes)}"
    )

old_galata_mesh = old_galata_meshes[0]
foundation_z = float(
    old_galata_mesh["foundation_z"]
)

data = AtlasLocalOSMReader.read(
    PBF_PATH,
    BBOX,
)

landmarks = (
    AtlasBridgeLandmarkDeduplicator
    .filter_landmarks(
        data["landmarks"]
    )
)

source = next(
    landmark
    for landmark in landmarks
    if (
        (landmark.get("tags", {}) or {}).get(
            "wikidata"
        )
        == GALATA_WIKIDATA
        and (landmark.get("tags", {}) or {}).get(
            "man_made"
        )
        == "bridge"
    )
)

working_bbox = result["working_bbox"]

coordinate_engine = AtlasCoordinateEngine(
    origin_lat=working_bbox[0],
    origin_lon=working_bbox[1],
    xy_scale=SCALE_RATIO,
    z_scale=SCALE_RATIO,
)

footprint = tuple(
    coordinate_engine.geometry_to_stl_mm(
        source["geometry"]
    )
)

frame = resolve_bridge_frame(
    footprint
)

prototype = AtlasGalataBridgeThreePartBuilder.build(
    center=frame["center"],
    axis=frame["axis"],
    total_span_mm=frame["total_span_mm"],
    deck_width_mm=frame["deck_width_mm"],
    center_section_ratio=0.30,
    foundation_z=foundation_z,
    center_deck_bottom_z=(
        foundation_z + 3.0
    ),
    deck_thickness_mm=0.80,
    left_extension_mm=3.561365,
    right_extension_mm=0.0,
)


def is_bridge_corridor_road(mesh):
    vertices = [
        point
        for triangle in mesh.get("triangles", ())
        for point in triangle
    ]

    if not vertices:
        return False

    center_x, center_y = frame["center"]
    axis_x, axis_y = frame["axis"]
    normal_x = -axis_y
    normal_y = axis_x

    longitudinal = [
        (
            (float(x) - center_x) * axis_x
            + (float(y) - center_y) * axis_y
        )
        for x, y, _z in vertices
    ]

    lateral = [
        (
            (float(x) - center_x) * normal_x
            + (float(y) - center_y) * normal_y
        )
        for x, y, _z in vertices
    ]

    longitudinal_span = (
        max(longitudinal) - min(longitudinal)
    )

    bridge_half_span = (
        frame["total_span_mm"] * 0.5
    )
    corridor_half_width = (
        frame["deck_width_mm"] * 0.5
        + 2.0
    )

    crosses_bridge_center = (
        min(longitudinal) < 0.0
        and max(longitudinal) > 0.0
    )

    mostly_follows_bridge = (
        longitudinal_span
        >= frame["total_span_mm"] * 0.80
    )

    enters_bridge_width = (
        min(lateral) <= corridor_half_width
        and max(lateral) >= -corridor_half_width
    )

    remains_near_bridge_ends = (
        min(longitudinal)
        <= -bridge_half_span * 0.80
        and max(longitudinal)
        >= bridge_half_span * 0.80
    )

    return (
        crosses_bridge_center
        and mostly_follows_bridge
        and enters_bridge_width
        and remains_near_bridge_ends
    )


original_road_meshes = list(
    groups.get("roads", ())
)

removed_bridge_road_meshes = [
    mesh
    for mesh in original_road_meshes
    if is_bridge_corridor_road(mesh)
]

retained_road_meshes = [
    mesh
    for mesh in original_road_meshes
    if not is_bridge_corridor_road(mesh)
]

groups["roads"] = retained_road_meshes

retained_landmarks = [
    mesh
    for mesh in groups.get("landmarks", ())
    if mesh is not old_galata_mesh
]

scene_meshes = []

group_order = (
    "terrain",
    "buildings",
    "roads",
    "parks",
    "elevated_areas",
    "artworks",
    "trees",
    "waters",
    "castle_walls",
    "castle_shells",
    "castle_tower_caps",
)

for group_name in group_order:
    scene_meshes.extend(
        groups.get(group_name, ())
    )

scene_meshes.extend(
    retained_landmarks
)
scene_meshes.extend(
    prototype["meshes"]
)

Path(OUTPUT_PATH).parent.mkdir(
    parents=True,
    exist_ok=True,
)

AtlasSTLWriter.write(
    scene_meshes,
    OUTPUT_PATH,
    solid_name=(
        "ATLAS_GALATA_EMINONU_KARAKOY"
    ),
)

prototype_triangle_count = sum(
    len(mesh["triangles"])
    for mesh in prototype["meshes"]
)

total_triangle_count = sum(
    len(mesh.get("triangles", ()))
    for mesh in scene_meshes
)

print()
print("=" * 92)
print("GALATA BRIDGE — EMINÖNÜ/KARAKÖY SCENE 1:5500")
print("=" * 92)
print(
    "Terrain size        : "
    f"{result['terrain_size_x_mm']:.3f} × "
    f"{result['terrain_size_y_mm']:.3f} mm"
)
print(f"Bridge foundation Z : {foundation_z:.3f} mm")
print(
    "Bridge axis         : "
    f"{frame['axis'][0]:.6f}, "
    f"{frame['axis'][1]:.6f}"
)
print(
    "Source bridge span  : "
    f"{frame['total_span_mm']:.3f} mm"
)
print(
    "Effective span      : "
    f"{prototype['total_span_mm']:.3f} mm"
)
print(
    "Left extension      : "
    f"{prototype['left_extension_mm']:.3f} mm"
)
print(
    "Bridge deck width   : "
    f"{frame['deck_width_mm']:.3f} mm"
)
print(
    "Prototype supports  : "
    f"{len(prototype['center']['supports'])}"
)
print(
    "Prototype triangles : "
    f"{prototype_triangle_count}"
)
print(
    "Removed bridge roads: "
    f"{len(removed_bridge_road_meshes)}"
)
print(
    "Retained road meshes: "
    f"{len(retained_road_meshes)}"
)
print(
    "Scene meshes        : "
    f"{len(scene_meshes)}"
)
print(
    "Scene triangles     : "
    f"{total_triangle_count}"
)
print(f"Output              : {OUTPUT_PATH}")
print("=" * 92)
