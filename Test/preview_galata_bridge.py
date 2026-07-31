from collections import Counter
from pathlib import Path

from CORE.atlas_bridge_landmark_deduplicator import (
    AtlasBridgeLandmarkDeduplicator,
)
from CORE.atlas_coordinate_engine import AtlasCoordinateEngine
from CORE.atlas_landmark_foundation_builder import (
    AtlasLandmarkFoundationBuilder,
)
from CORE.atlas_local_osm_reader import AtlasLocalOSMReader
from EXPORT.atlas_stl_writer import AtlasSTLWriter


PBF_PATH = "Data/OSM/galata-bridge-test.osm.pbf"
OUTPUT_PATH = "OUTPUT/STL/galata_bridge_isolated_1_5500.stl"

BBOX = (
    41.01476522,
    28.96589663,
    41.02563478,
    28.98030337,
)

XY_SCALE = 5500.0
Z_SCALE = 5500.0
GALATA_WIKIDATA = "Q81523"


def point_key(point):
    return tuple(round(float(value), 9) for value in point)


data = AtlasLocalOSMReader.read(PBF_PATH, BBOX)

landmarks = AtlasBridgeLandmarkDeduplicator.filter_landmarks(
    data["landmarks"]
)

galata = next(
    item
    for item in landmarks
    if (
        (item.get("tags", {}) or {}).get("wikidata")
        == GALATA_WIKIDATA
        and (item.get("tags", {}) or {}).get("man_made")
        == "bridge"
    )
)

south, west, _north, _east = BBOX

coordinate_engine = AtlasCoordinateEngine(
    origin_lat=south,
    origin_lon=west,
    xy_scale=XY_SCALE,
    z_scale=Z_SCALE,
)

mesh = AtlasLandmarkFoundationBuilder._build_landmark_mesh(
    source=galata,
    coordinate_engine=coordinate_engine,
    terrain_mesh=None,
)

if mesh is None:
    raise RuntimeError("Galata Bridge mesh could not be built")

triangles = tuple(mesh.get("triangles", ()))

all_points = [
    point
    for triangle in triangles
    for point in triangle
]

min_x = min(point[0] for point in all_points)
max_x = max(point[0] for point in all_points)
min_y = min(point[1] for point in all_points)
max_y = max(point[1] for point in all_points)
min_z = min(point[2] for point in all_points)
max_z = max(point[2] for point in all_points)

translated_triangles = [
    tuple(
        (
            float(x) - min_x,
            float(y) - min_y,
            float(z) - min_z,
        )
        for x, y, z in triangle
    )
    for triangle in triangles
]

translated_mesh = {
    **mesh,
    "triangles": translated_triangles,
}

edge_counts = Counter()

for triangle in translated_triangles:
    points = [point_key(point) for point in triangle]

    for a, b in (
        (points[0], points[1]),
        (points[1], points[2]),
        (points[2], points[0]),
    ):
        edge_counts[tuple(sorted((a, b)))] += 1

open_edges = sum(
    1
    for count in edge_counts.values()
    if count == 1
)

non_manifold_edges = sum(
    1
    for count in edge_counts.values()
    if count > 2
)

Path(OUTPUT_PATH).parent.mkdir(
    parents=True,
    exist_ok=True,
)

AtlasSTLWriter.write(
    [translated_mesh],
    OUTPUT_PATH,
    solid_name="ATLAS_GALATA_BRIDGE",
)

print()
print("=" * 70)
print("GALATA BRIDGE ISOLATED PREVIEW")
print("=" * 70)
print("Landmark ID       :", galata["id"])
print("Name              :", galata["tags"].get("name"))
print("Wikidata          :", galata["tags"].get("wikidata"))
print("Input points      :", len(galata["geometry"]))
print("Triangles         :", len(translated_triangles))
print("Width X           :", f"{max_x - min_x:.6f} mm")
print("Depth Y           :", f"{max_y - min_y:.6f} mm")
print("Height Z          :", f"{max_z - min_z:.6f} mm")
print("Open edges        :", open_edges)
print("Non-manifold      :", non_manifold_edges)
print("Output            :", OUTPUT_PATH)
print("=" * 70)
