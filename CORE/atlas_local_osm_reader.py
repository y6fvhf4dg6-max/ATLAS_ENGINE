# CORE/atlas_local_osm_reader.py

"""
ATLAS Engine

Atlas Local OSM Reader v1.2
Reads local .osm.pbf files without Overpass API.

Supported objects:
- buildings
- trees
- roads
- pedestrian paths
- parks / green areas
"""

import osmium


class AtlasLocalOSMReader(osmium.SimpleHandler):
    def __init__(self, bbox):
        super().__init__()

        self.south, self.west, self.north, self.east = bbox

        self.buildings = []
        self.trees = []
        self.roads = []
        self.pedestrian_paths = []
        self.elevated_areas = []
        self.artworks = []
        self.parks = []
        self.waters = []
        self.coastlines = []
        self.castles = []
        self.castle_metadata = []
        self.castle_walls = []
        self.defensive_towers = []

    def inside_bbox(self, lat, lon):
        return self.south <= lat <= self.north and self.west <= lon <= self.east

    def node(self, n):
        if not n.location.valid():
            return

        lat = n.location.lat
        lon = n.location.lon

        if not self.inside_bbox(lat, lon):
            return

        tags = dict(n.tags)

        if self._is_castle(tags):
            self.castle_metadata.append(
                {
                    "id": n.id,
                    "lat": lat,
                    "lon": lon,
                    "geometry_type": "node",
                    "tags": tags,
                    "castle_type": tags.get(
                        "castle_type",
                        "castle",
                    ),
                    "name": tags.get("name"),
                }
            )

        if tags.get("natural") == "tree":
            self.trees.append(
                {
                    "id": n.id,
                    "lat": lat,
                    "lon": lon,
                    "tags": tags,
                }
            )

        if self._is_artwork(tags):
            self.artworks.append(
                {
                    "id": n.id,
                    "lat": lat,
                    "lon": lon,
                    "geometry_type": "node",
                    "tags": tags,
                    "artwork_type": tags.get("artwork_type"),
                    "statue_type": tags.get("statue"),
                    "name": tags.get("name"),
                }
            )

        if self._is_defensive_tower(tags):
            self.defensive_towers.append(
                {
                    "id": n.id,
                    "lat": lat,
                    "lon": lon,
                    "geometry_type": "node",
                    "tags": tags,
                }
            )

    @staticmethod
    def _is_artwork(tags):
        if tags.get("tourism") != "artwork":
            return False

        return tags.get("artwork_type") in {
            "statue",
            "sculpture",
        }

    def way(self, w):
        tags = dict(w.tags)

        if self._is_castle(tags):
            self._read_castle(w, tags)

        if self._is_castle_wall(tags):
            self._read_castle_wall(w, tags)

            return

        if self._is_castle_wall(tags):
            self._read_castle_wall(w, tags)
            return

        if self._is_defensive_tower(tags):
            self._read_defensive_tower(w, tags)
            return

        if (
            "building" in tags
            or "building:part" in tags
        ):
            self._read_building(w, tags)
            return

        if tags.get("natural") == "coastline":
            self._read_coastline(w, tags)
            return

        if self._is_water(tags):
            self._read_water(w, tags)
            return

        if self._is_elevated_area(tags):
            self._read_elevated_area(w, tags)
            return

        if "highway" in tags:
            self._read_highway(w, tags)
            return

        if self._is_park_or_green_area(tags):
            self._read_park(w, tags)
            return

    def _read_water(self, w, tags):
        geometry = self._extract_way_geometry(w)

        if len(geometry) < 3:
            return

        if not self._any_point_inside_bbox(geometry):
            return

        if geometry[0] == geometry[-1]:
            geometry.pop()

        self.waters.append(
            {
                "id": w.id,
                "geometry": geometry,
                "tags": tags,
            }
        )

        if self._is_park_or_green_area(tags):
            self._read_park(w, tags)
            return

    def _read_coastline(self, w, tags):
        geometry = self._extract_way_geometry(w)

        if len(geometry) < 2:
            return

        if not self._any_point_inside_bbox(geometry):
            return

        self.coastlines.append(
            {
                "id": w.id,
                "geometry": geometry,
                "geometry_type": "way",
                "tags": tags,
            }
        )

    def _read_building(self, w, tags):
        geometry = self._extract_way_geometry(w)

        if len(geometry) < 4:
            return

        if not self._all_points_inside_bbox(geometry):
            return

        if geometry[0] == geometry[-1]:
            geometry.pop()

        self.buildings.append(
            {
                "id": w.id,
                "geometry": geometry,
                "tags": tags,
            }
        )

    def _read_elevated_area(self, w, tags):
        geometry = self._extract_way_geometry(w)

        if len(geometry) < 4:
            return

        if not self._any_point_inside_bbox(geometry):
            return

        if geometry[0] == geometry[-1]:
            geometry.pop()

        if len(geometry) < 3:
            return

        try:
            height_m = float(tags.get("height"))
        except (TypeError, ValueError):
            return

        if height_m <= 0.0:
            return

        self.elevated_areas.append(
            {
                "id": w.id,
                "geometry": geometry,
                "tags": tags,
                "height_m": height_m,
                "area_type": "elevated_pedestrian_area",
            }
        )

    @staticmethod
    def _is_elevated_area(tags):
        if tags.get("highway") != "pedestrian":
            return False

        if tags.get("area") != "yes":
            return False

        try:
            return float(tags.get("height")) > 0.0
        except (TypeError, ValueError):
            return False

    def _read_highway(self, w, tags):
        geometry = self._extract_way_geometry(w)

        if len(geometry) < 2:
            return

        if not self._any_point_inside_bbox(geometry):
            return

        road_type = tags.get("highway")

        item = {
            "id": w.id,
            "geometry": geometry,
            "tags": tags,
            "road_type": road_type,
        }

        if self._is_pedestrian_path(tags):
            self.pedestrian_paths.append(item)
        elif self._is_vehicle_road(tags):
            self.roads.append(item)

    def _read_water(self, w, tags):
        geometry = self._extract_way_geometry(w)

        if len(geometry) < 3:
            return

        if not self._any_point_inside_bbox(geometry):
            return

        if geometry[0] == geometry[-1]:
            geometry.pop()

        self.waters.append(
            {
                "id": w.id,
                "geometry": geometry,
                "tags": tags,
                "water_type": self._water_type(tags),
            }
        )

    @staticmethod
    def _is_water(tags):

        if tags.get("natural") == "water":
            return True

        if tags.get("water"):
            return True

        if tags.get("waterway") in {
            "river",
            "stream",
            "canal",
        }:
            return True

        if tags.get("landuse") == "reservoir":
            return True

        if tags.get("leisure") == "swimming_pool":
            return True

        if tags.get("amenity") == "fountain":
            return True

        return False

    def _read_park(self, w, tags):
        geometry = self._extract_way_geometry(w)

        if len(geometry) < 4:
            return

        if not self._any_point_inside_bbox(geometry):
            return

        if geometry[0] == geometry[-1]:
            geometry.pop()

        self.parks.append(
            {
                "id": w.id,
                "geometry": geometry,
                "tags": tags,
                "park_type": self._park_type(tags),
            }
        )

    def _extract_way_geometry(self, way):
        geometry = []

        for node in way.nodes:
            if not node.location.valid():
                continue

            lat = node.location.lat
            lon = node.location.lon

            geometry.append((lat, lon))

        return geometry

    def _all_points_inside_bbox(self, geometry):
        for lat, lon in geometry:
            if not self.inside_bbox(lat, lon):
                return False

        return True

    def _any_point_inside_bbox(self, geometry):
        for lat, lon in geometry:
            if self.inside_bbox(lat, lon):
                return True

        return False

    @staticmethod
    def _is_pedestrian_path(tags):
        highway = tags.get("highway")

        pedestrian_types = {
            "footway",
            "path",
            "pedestrian",
            "steps",
            "cycleway",
            "bridleway",
        }

        if highway in pedestrian_types:
            return True

        if tags.get("foot") in {"yes", "designated"}:
            return True

        return False

    @staticmethod
    def _is_vehicle_road(tags):
        highway = tags.get("highway")

        vehicle_types = {
            "motorway",
            "trunk",
            "primary",
            "secondary",
            "tertiary",
            "unclassified",
            "residential",
            "service",
            "living_street",
            "road",
        }

        return highway in vehicle_types

    @staticmethod
    def _is_water(tags):
        if tags.get("natural") == "water":
            return True

        if tags.get("water"):
            return True

        if tags.get("waterway") in {
            "river",
            "stream",
            "canal",
        }:
            return True

        if tags.get("landuse") == "reservoir":
            return True

        if tags.get("leisure") == "swimming_pool":
            return True

        if tags.get("amenity") == "fountain":
            return True

        return False

    @staticmethod
    def _water_type(tags):
        if tags.get("water"):
            return f"water:{tags.get('water')}"

        if tags.get("waterway"):
            return f"waterway:{tags.get('waterway')}"

        if tags.get("leisure") == "swimming_pool":
            return "leisure:swimming_pool"

        if tags.get("amenity") == "fountain":
            return "amenity:fountain"

        if tags.get("landuse") == "reservoir":
            return "landuse:reservoir"

        if tags.get("natural") == "water":
            return "natural:water"

        return "water"

    @staticmethod
    def _is_park_or_green_area(tags):
        leisure = tags.get("leisure")
        landuse = tags.get("landuse")
        natural = tags.get("natural")

        if leisure in {
            "park",
            "garden",
            "playground",
            "recreation_ground",
        }:
            return True

        if landuse in {
            "grass",
            "recreation_ground",
            "forest",
            "meadow",
            "village_green",
        }:
            return True

        if natural in {
            "wood",
            "grassland",
            "scrub",
        }:
            return True

        return False

    @staticmethod
    def _park_type(tags):
        if tags.get("leisure"):
            return f"leisure:{tags.get('leisure')}"

        if tags.get("landuse"):
            return f"landuse:{tags.get('landuse')}"

        if tags.get("natural"):
            return f"natural:{tags.get('natural')}"

        return "green_area"

    def _read_castle_wall(self, w, tags):
        geometry = self._extract_way_geometry(w)

        if len(geometry) < 2:
            return

        if not self._any_point_inside_bbox(geometry):
            return

        if geometry[0] == geometry[-1]:
            geometry.pop()

        self.castle_walls.append(
            {
                "id": w.id,
                "geometry": geometry,
                "tags": tags,
                "wall_type": "city_wall",
            }
        )

    def _read_castle(self, w, tags):
        geometry = self._extract_way_geometry(w)

        if len(geometry) < 3:
            return

        if not self._any_point_inside_bbox(geometry):
            return

        if geometry[0] == geometry[-1]:
            geometry.pop()

        self.castles.append(
            {
                "id": w.id,
                "geometry": geometry,
                "outer_geometries": [geometry],
                "inner_geometries": [],
                "geometry_type": "way",
                "tags": tags,
                "castle_type": tags.get(
                    "castle_type",
                    "castle",
                ),
            }
        )

    def _read_defensive_tower(self, w, tags):
        geometry = self._extract_way_geometry(w)

        if len(geometry) < 3:
            return

        if not self._any_point_inside_bbox(geometry):
            return

        if geometry[0] == geometry[-1]:
            geometry.pop()

        self.defensive_towers.append(
            {
                "id": w.id,
                "geometry": geometry,
                "geometry_type": "way",
                "tags": tags,
            }
        )

    @staticmethod
    def _is_castle_wall(tags):
        historic = tags.get("historic")
        barrier = tags.get("barrier")

        return (
            barrier == "city_wall"
            or historic == "citywalls"
            or historic == "castle_wall"
        )

    @staticmethod
    def _is_castle(tags):
        return tags.get("historic") == "castle" or tags.get("building") == "castle"

    @staticmethod
    def _is_defensive_tower(tags):
        return tags.get("man_made") == "tower" and tags.get("tower:type") == "defensive"

    @staticmethod
    def _is_building_relation(tags):
        if tags.get("type") != "multipolygon":
            return False

        return (
            "building" in tags
            or "building:part" in tags
        )

    @staticmethod
    def _create_building_relation_record(
        relation_id,
        tags,
        outer_geometries,
        inner_geometries,
    ):
        valid_outer_geometries = [
            list(geometry)
            for geometry in outer_geometries
            if len(geometry) >= 3
        ]

        if not valid_outer_geometries:
            return None

        valid_inner_geometries = [
            list(geometry)
            for geometry in inner_geometries
            if len(geometry) >= 3
        ]

        return {
            "id": relation_id,
            "geometry": valid_outer_geometries[0],
            "outer_geometries": valid_outer_geometries,
            "inner_geometries": valid_inner_geometries,
            "geometry_type": "relation",
            "tags": dict(tags),
        }

    @staticmethod
    def read(pbf_path, bbox):
        class BuildingRelationScanner(osmium.SimpleHandler):
            def __init__(self):
                super().__init__()

                self.building_relations = []
                self.member_way_ids = set()

            def relation(self, relation):
                tags = dict(relation.tags)

                if not AtlasLocalOSMReader._is_building_relation(tags):
                    return

                members = []

                for member in relation.members:
                    if member.type != "w":
                        continue

                    members.append(
                        {
                            "ref": member.ref,
                            "role": member.role or "",
                        }
                    )

                    self.member_way_ids.add(member.ref)

                if not members:
                    return

                self.building_relations.append(
                    {
                        "id": relation.id,
                        "tags": tags,
                        "members": members,
                    }
                )

        class CastleRelationScanner(osmium.SimpleHandler):
            def __init__(self):
                super().__init__()

                self.castle_relations = []
                self.member_way_ids = set()

            def relation(self, relation):
                tags = dict(relation.tags)

                is_castle = (
                    tags.get("historic") == "castle" or tags.get("building") == "castle"
                )

                if not is_castle:
                    return

                if tags.get("type") != "multipolygon":
                    return

                members = []

                for member in relation.members:
                    if member.type != "w":
                        continue

                    members.append(
                        {
                            "ref": member.ref,
                            "role": member.role or "",
                        }
                    )

                    self.member_way_ids.add(member.ref)

                if not members:
                    return

                self.castle_relations.append(
                    {
                        "id": relation.id,
                        "tags": tags,
                        "members": members,
                    }
                )

        building_relation_scanner = BuildingRelationScanner()

        building_relation_scanner.apply_file(
            pbf_path,
            locations=False,
        )

        relation_scanner = CastleRelationScanner()

        relation_scanner.apply_file(
            pbf_path,
            locations=False,
        )

        reader = AtlasLocalOSMReader(bbox)

        reader.apply_file(
            pbf_path,
            locations=True,
        )

        if building_relation_scanner.member_way_ids:

            class BuildingMemberWayScanner(osmium.SimpleHandler):
                def __init__(self, target_way_ids):
                    super().__init__()

                    self.target_way_ids = target_way_ids
                    self.way_geometries = {}

                def way(self, way):
                    if way.id not in self.target_way_ids:
                        return

                    geometry = []

                    for node in way.nodes:
                        if not node.location.valid():
                            continue

                        geometry.append(
                            (
                                node.location.lat,
                                node.location.lon,
                            )
                        )

                    if geometry:
                        self.way_geometries[way.id] = geometry

            building_way_scanner = BuildingMemberWayScanner(
                building_relation_scanner.member_way_ids
            )

            building_way_scanner.apply_file(
                pbf_path,
                locations=True,
            )

            existing_building_ids = {
                building.get("id")
                for building in reader.buildings
            }

            for relation in building_relation_scanner.building_relations:
                if relation["id"] in existing_building_ids:
                    continue

                outer_geometries = []
                inner_geometries = []

                for member in relation["members"]:
                    geometry = building_way_scanner.way_geometries.get(
                        member["ref"]
                    )

                    if not geometry:
                        continue

                    geometry = list(geometry)

                    if (
                        len(geometry) >= 2
                        and geometry[0] == geometry[-1]
                    ):
                        geometry.pop()

                    if len(geometry) < 3:
                        continue

                    if member["role"] == "inner":
                        inner_geometries.append(geometry)
                    else:
                        outer_geometries.append(geometry)

                if not outer_geometries:
                    continue

                if not any(
                    reader._any_point_inside_bbox(geometry)
                    for geometry in outer_geometries
                ):
                    continue

                record = AtlasLocalOSMReader._create_building_relation_record(
                    relation_id=relation["id"],
                    tags=relation["tags"],
                    outer_geometries=outer_geometries,
                    inner_geometries=inner_geometries,
                )

                if record is None:
                    continue

                reader.buildings.append(record)
                existing_building_ids.add(relation["id"])

        if relation_scanner.member_way_ids:

            class CastleMemberWayScanner(osmium.SimpleHandler):
                def __init__(self, target_way_ids):
                    super().__init__()

                    self.target_way_ids = target_way_ids
                    self.way_geometries = {}

                def way(self, way):
                    if way.id not in self.target_way_ids:
                        return

                    geometry = []

                    for node in way.nodes:
                        if not node.location.valid():
                            continue

                        geometry.append(
                            (
                                node.location.lat,
                                node.location.lon,
                            )
                        )

                    if geometry:
                        self.way_geometries[way.id] = geometry

            way_scanner = CastleMemberWayScanner(relation_scanner.member_way_ids)

            way_scanner.apply_file(
                pbf_path,
                locations=True,
            )

            for relation in relation_scanner.castle_relations:
                outer_geometries = []
                inner_geometries = []

                for member in relation["members"]:
                    geometry = way_scanner.way_geometries.get(member["ref"])

                    if not geometry:
                        continue

                    geometry = list(geometry)

                    if len(geometry) >= 2 and geometry[0] == geometry[-1]:
                        geometry.pop()

                    if len(geometry) < 3:
                        continue

                    if member["role"] == "inner":
                        inner_geometries.append(geometry)
                    else:
                        outer_geometries.append(geometry)

                if not outer_geometries:
                    continue

                if not any(
                    reader._any_point_inside_bbox(geometry)
                    for geometry in outer_geometries
                ):
                    continue

                tags = relation["tags"]

                reader.castles.append(
                    {
                        "id": relation["id"],
                        "geometry": outer_geometries[0],
                        "outer_geometries": outer_geometries,
                        "inner_geometries": inner_geometries,
                        "geometry_type": "relation",
                        "tags": tags,
                        "castle_type": tags.get(
                            "castle_type",
                            "castle",
                        ),
                    }
                )

                existing_wall_ids = {wall.get("id") for wall in reader.castle_walls}

                for member in relation["members"]:
                    geometry = way_scanner.way_geometries.get(member["ref"])

                    if not geometry:
                        continue

                    if member["ref"] in existing_wall_ids:
                        continue

                    geometry = list(geometry)

                    if len(geometry) >= 2 and geometry[0] == geometry[-1]:
                        geometry.pop()

                    if len(geometry) < 2:
                        continue

                    role = member["role"] or "outer"

                    reader.castle_walls.append(
                        {
                            "id": member["ref"],
                            "geometry": geometry,
                            "tags": {
                                **tags,
                                "relation_id": relation["id"],
                                "relation_role": role,
                                "source": "castle_relation",
                            },
                            "wall_type": (
                                "castle_relation_inner_wall"
                                if role == "inner"
                                else "castle_relation_outer_wall"
                            ),
                            "source_relation_id": relation["id"],
                            "relation_role": role,
                        }
                    )

                    existing_wall_ids.add(member["ref"])

        return {
            "buildings": reader.buildings,
            "trees": reader.trees,
            "roads": reader.roads,
            "pedestrian_paths": reader.pedestrian_paths,
            "elevated_areas": reader.elevated_areas,
            "artworks": reader.artworks,
            "parks": reader.parks,
            "waters": reader.waters,
            "coastlines": reader.coastlines,
            "castles": reader.castles,
            "castle_metadata": reader.castle_metadata,
            "castle_walls": reader.castle_walls,
            "defensive_towers": reader.defensive_towers,
        }
