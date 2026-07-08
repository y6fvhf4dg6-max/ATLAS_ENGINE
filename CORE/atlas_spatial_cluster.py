# CORE/atlas_spatial_cluster.py

import math


class AtlasSpatialCluster:
    """
    ATLAS Spatial Cluster v1.0

    Görev:
    Bina listesinden fiziksel olarak birbirine yakın olan en iyi kümeyi seçmek.

    Bu modül kalite filtresi değildir.
    Bu modül önce mekânsal yakınlığı çözer.

    Kullanım:
        clustered_buildings = AtlasSpatialCluster.select_dense_cluster(
            buildings,
            limit=100,
            radius_m=120,
            debug=True,
        )
    """

    @staticmethod
    def select_dense_cluster(
        buildings,
        limit=100,
        radius_m=120,
        debug=True,
    ):
        items = []

        for building in buildings:
            geometry = AtlasSpatialCluster._extract_geometry(building)

            if not geometry:
                continue

            centroid = AtlasSpatialCluster._centroid(geometry)

            if centroid is None:
                continue

            items.append(
                {
                    "building": building,
                    "building_id": AtlasSpatialCluster._extract_id(building),
                    "centroid": centroid,
                    "geometry": geometry,
                }
            )

        if not items:
            if debug:
                print("AtlasSpatialCluster: no valid buildings.")
            return []

        best_cluster = None
        best_score = -1

        for center_item in items:
            center = center_item["centroid"]

            cluster = []

            for item in items:
                distance_m = AtlasSpatialCluster._distance_meters(
                    center,
                    item["centroid"],
                )

                if distance_m <= radius_m:
                    cluster.append(
                        {
                            **item,
                            "distance_m": distance_m,
                        }
                    )

            score = AtlasSpatialCluster._cluster_score(cluster)

            if score > best_score:
                best_score = score
                best_cluster = cluster

        if best_cluster is None:
            return []

        best_cluster.sort(key=lambda item: item["distance_m"])

        selected = best_cluster[:limit]
        selected_buildings = [item["building"] for item in selected]

        if debug:
            AtlasSpatialCluster._print_report(
                total=len(buildings),
                valid=len(items),
                radius_m=radius_m,
                selected=selected,
            )

        return selected_buildings

    @staticmethod
    def _cluster_score(cluster):
        if not cluster:
            return 0

        count_score = len(cluster) * 1000

        average_distance = sum(item["distance_m"] for item in cluster) / len(cluster)

        compactness_penalty = average_distance * 2

        return count_score - compactness_penalty

    @staticmethod
    def _extract_geometry(building):
        if building is None:
            return []

        if isinstance(building, dict):
            return building.get("geometry") or building.get("points") or []

        if hasattr(building, "geometry"):
            return building.geometry

        if hasattr(building, "points"):
            return building.points

        return []

    @staticmethod
    def _extract_id(building):
        if building is None:
            return "unknown"

        if isinstance(building, dict):
            return building.get("id") or building.get("building_id") or "unknown"

        if hasattr(building, "building_id"):
            return building.building_id

        if hasattr(building, "id"):
            return building.id

        return "unknown"

    @staticmethod
    def _centroid(points):
        if not points:
            return None

        clean_points = points[:]

        if len(clean_points) > 1 and clean_points[0] == clean_points[-1]:
            clean_points = clean_points[:-1]

        if not clean_points:
            return None

        lat_sum = 0.0
        lon_sum = 0.0

        for lat, lon in clean_points:
            lat_sum += lat
            lon_sum += lon

        return (
            lat_sum / len(clean_points),
            lon_sum / len(clean_points),
        )

    @staticmethod
    def _distance_meters(a, b):
        lat1, lon1 = a
        lat2, lon2 = b

        mean_lat = math.radians((lat1 + lat2) / 2.0)

        meters_per_degree_lat = 111_320
        meters_per_degree_lon = 111_320 * math.cos(mean_lat)

        dx = (lon2 - lon1) * meters_per_degree_lon
        dy = (lat2 - lat1) * meters_per_degree_lat

        return math.sqrt((dx * dx) + (dy * dy))

    @staticmethod
    def _print_report(total, valid, radius_m, selected):
        print("")
        print("=" * 60)
        print("ATLAS SPATIAL CLUSTER REPORT")
        print("=" * 60)
        print(f"Candidate buildings : {total}")
        print(f"Valid centroids     : {valid}")
        print(f"Cluster radius      : {radius_m} m")
        print(f"Selected buildings  : {len(selected)}")
        print("-" * 60)

        for item in selected[:30]:
            print(
                f"CLUSTERED | ID: {item['building_id']} | "
                f"Distance: {item['distance_m']:.2f} m"
            )

        print("=" * 60)
        print("")
