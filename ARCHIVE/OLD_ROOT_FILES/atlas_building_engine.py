"""
ATLAS Engine 2.0

Module : Building Engine
Version: 2.0

Purpose:
Create building meshes from OSM building data.
Includes Landmark awareness through Tag Analyzer.
"""

from atlas_roof_engine import generate_roof_geometry
from atlas_extrusion import extrude_mesh
from atlas_geometry import resolve_node_coordinates
from atlas_mesh_builder import triangulate_polygon
from atlas_landmark_geometry import generate_landmark_geometry
from atlas_model_space import coordinates_to_model_points
from atlas_tag_analyzer import (
    get_landmark_score,
    is_landmark,
    landmark_category,
)


MAX_BUILDINGS = 150

DEFAULT_HEIGHT_M = 9.0
MIN_MODEL_HEIGHT_MM = 1.5

LANDMARK_HEIGHT_MULTIPLIER = 1.6
LANDMARK_MIN_HEIGHT_M = 22.0


BUILDING_HEIGHTS_M = {
    "cathedral": 35.0,
    "church": 24.0,
    "chapel": 14.0,
    "mosque": 26.0,
    "synagogue": 20.0,
    "monastery": 20.0,
    "castle": 24.0,
    "palace": 22.0,
    "townhall": 18.0,
    "museum": 16.0,
    "university": 16.0,
    "hospital": 18.0,
    "office": 18.0,
    "commercial": 16.0,
    "retail": 12.0,
    "apartments": 13.5,
    "house": 9.0,
    "residential": 10.5,
    "garage": 3.0,
    "parking": 3.0,
    "yes": DEFAULT_HEIGHT_M,
}


class AtlasBuildingEngine:

    def __init__(self, context):
        self.context = context

    def is_building_way(self, element):
        return (
            element.get("type") == "way"
            and "tags" in element
            and "building" in element["tags"]
            and "nodes" in element
        )

    def building_type(self, element):
        return element.get("tags", {}).get("building", "yes")

    def parse_float_tag(self, tags, key):
        value = tags.get(key)

        if value is None:
            return None

        try:
            value = str(value).lower().replace("m", "").strip()
            return float(value)
        except Exception:
            return None

    def parse_levels(self, tags):
        value = tags.get("building:levels")

        if value is None:
            return None

        try:
            return float(str(value).strip())
        except Exception:
            return None

    def real_height_m(self, element):
        tags = element.get("tags", {})
        btype = self.building_type(element)

        explicit_height = self.parse_float_tag(tags, "height")
        if explicit_height is not None and explicit_height > 0:
            height = explicit_height
        else:
            levels = self.parse_levels(tags)

            if levels is not None and levels > 0:
                height = levels * 3.0
            else:
                height = BUILDING_HEIGHTS_M.get(btype, DEFAULT_HEIGHT_M)

        if is_landmark(tags):
            height = max(
                height * LANDMARK_HEIGHT_MULTIPLIER,
                LANDMARK_MIN_HEIGHT_M
            )

        return height

    def model_height_mm(self, real_height_m):
        detail_engine = getattr(self.context, "detail_engine", None)

        if detail_engine is not None:
            height_mm = detail_engine.real_m_to_model_mm(real_height_m)
        else:
            height_mm = real_height_m / 2.0

        return max(height_mm, MIN_MODEL_HEIGHT_MM)

    def element_to_model_points(self, element):
        coordinates = resolve_node_coordinates(
            element["nodes"],
            self.context.node_lookup_buildings
        )

        if len(coordinates) > 1 and coordinates[0] == coordinates[-1]:
            coordinates = coordinates[:-1]

        return coordinates_to_model_points(
            coordinates,
            self.context.bounds,
            self.context.model_size_mm
        )

    def place_mesh_on_terrain(self, points_3d):
        placed_points = []

        for x, y, z in points_3d:
            if self.context.terrain_sampler is None:
                terrain_z = 0.0
            else:
                terrain_z = self.context.terrain_sampler.get_height(x, y)

            placed_points.append((x, y, terrain_z + z))

        return placed_points
    def is_inside_landmark_zone(self, x, y):
        landmark_context = getattr(self.context, "landmark_context", None)

        if landmark_context is None:
            return False

        return landmark_context.is_point_inside_landmark_zone(x, y)   

    def is_protected_building(self, element, x, y):
        tags = element.get("tags", {})

        if is_landmark(tags):
            return True

        if self.is_inside_landmark_zone(x, y):
            return True

        return False     

    def print_building_log(
        self,
        index,
        element,
        real_height_m,
        model_height_mm,
        terrain_z,
        inside_landmark_zone,
        protected_building
    ):
        tags = element.get("tags", {})
        btype = self.building_type(element)

        score = get_landmark_score(tags)
        landmark = is_landmark(tags)
        category = landmark_category(tags)
        name = tags.get("name")

        label = "LANDMARK" if landmark else "OK"

        print(
            f"{label}: {index}",
            "| OSM:", element.get("id"),
            "| Name:", name,
            "| Type:", btype,
            "| Category:", category,
            "| Score:", score,
            "| Landmark Zone:", inside_landmark_zone,
            "| Terrain Z:", round(terrain_z, 2), "mm",
            "| Real Height:", round(real_height_m, 2), "m",
            "| Model Height:", round(model_height_mm, 2), "mm"
        )

    def build(self):
        print()
        print("=" * 60)
        print("ATLAS BUILDING ENGINE v2.0 - LANDMARK AWARE")
        print("=" * 60)

        if self.context.osm_building_data is None:
            raise ValueError("Context içinde OSM bina verisi yok.")

        if self.context.node_lookup_buildings is None:
            raise ValueError("Context içinde bina node lookup yok.")

        if self.context.scene is None:
            raise ValueError("Context içinde Scene Engine yok.")

        self.context.building_checked_count = 0
        self.context.building_valid_count = 0
        self.context.building_skipped_count = 0

        for element in self.context.osm_building_data["elements"]:

            if not self.is_building_way(element):
                continue

            self.context.building_checked_count += 1

            if self.context.building_valid_count >= MAX_BUILDINGS:
                break

            try:
                tags = element.get("tags", {})

                model_points = self.element_to_model_points(element)

                if len(model_points) < 3:
                    self.context.building_skipped_count += 1
                    continue

                polygon, vertices, triangles = triangulate_polygon(
                    model_points
                )

                if polygon is None or polygon.is_empty:
                    self.context.building_skipped_count += 1
                    continue

                if not polygon.is_valid:
                    self.context.building_skipped_count += 1
                    continue

                real_height = self.real_height_m(element)
                height_mm = self.model_height_mm(real_height)

                points_3d, faces = extrude_mesh(
                    vertices,
                    triangles,
                    height_mm
                )

                points_3d = self.place_mesh_on_terrain(points_3d)

                self.context.scene.add_mesh(
                    points_3d,
                    faces,
                    layer_name="buildings"
                )
                roof_meshes = generate_roof_geometry(
                    tags,
                    model_points,
                    height_mm
                )

                for roof_points, roof_faces in roof_meshes:

                    roof_points = self.place_mesh_on_terrain(roof_points)

                    self.context.scene.add_mesh(
                        roof_points,
                        roof_faces,
                        layer_name="roof"
                    )

                landmark_meshes = generate_landmark_geometry(
                    tags,
                    model_points,
                    height_mm
                )
                for landmark_points, landmark_faces in landmark_meshes:
                    self.context.scene.add_mesh(
                        landmark_points,
                        landmark_faces,
                        layer_name="landmark_geometry"
                    )

                self.context.building_valid_count += 1

                centroid = polygon.centroid
                if self.context.terrain_sampler is None:
                    terrain_z = 0.0
                else:
                    terrain_z = self.context.terrain_sampler.get_height(
                        centroid.x,
                        centroid.y
                    )
                inside_landmark_zone = self.is_inside_landmark_zone(
                    centroid.x,
                    centroid.y
                )    
                protected_building = self.is_protected_building(
                    element,
                    centroid.x,
                    centroid.y
                )

                self.print_building_log(
                    self.context.building_valid_count,
                    element,
                    real_height,
                    height_mm,
                    terrain_z,
                    inside_landmark_zone,
                    protected_building
                )

            except Exception as error:
                self.context.building_skipped_count += 1
                print("Atlandı:", element.get("id"), "|", error)

        print()
        print("Building Engine özeti")
        print("---------------------")
        print("Denenen bina  :", self.context.building_checked_count)
        print("Geçerli bina  :", self.context.building_valid_count)
        print("Atlanan bina  :", self.context.building_skipped_count)
        print("=" * 60)