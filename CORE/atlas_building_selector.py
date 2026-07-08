# CORE/atlas_building_selector.py

import math


class AtlasBuildingSelector:
    """
    ATLAS Building Selector v2.0

    Görev:
    - Temiz bina seçmek
    - Çok karmaşık / bozuk footprint'leri elemek
    - Seçilen binaların aynı sahne içinde birbirine yakın olmasını sağlamak
    """

    DEFAULT_MIN_POINTS = 4
    DEFAULT_MAX_POINTS = 10
    DEFAULT_MAX_ASPECT_RATIO = 8.0

    @staticmethod
    def select_clean_buildings(
        buildings,
        limit=20,
        min_points=4,
        max_points=10,
        max_aspect_ratio=8.0,
        debug=True,
    ):
        evaluated = []

        for building in buildings:
            result = AtlasBuildingSelector._evaluate_building(
                building=building,
                min_points=min_points,
                max_points=max_points,
                max_aspect_ratio=max_aspect_ratio,
            )

            if result["accepted"]:
                evaluated.append(result)

        if not evaluated:
            if debug:
                print("No acceptable buildings found.")
            return []

        best_cluster = AtlasBuildingSelector._find_best_cluster(
            evaluated,
            limit=limit,
        )

        selected = [item["building"] for item in best_cluster]

        if debug:
            AtlasBuildingSelector._print_report(
                total=len(buildings),
                accepted=len(evaluated),
                selected=best_cluster,
            )

        return selected

    @staticmethod
    def _evaluate_building(building, min_points, max_points, max_aspect_ratio):
        building_id = AtlasBuildingSelector._extract_id(building)
        geometry = AtlasBuildingSelector._extract_geometry(building)

        reasons = []

        if not geometry:
            reasons.append("no_geometry")

        clean_geometry = AtlasBuildingSelector._remove_closing_point(geometry)

        point_count = len(clean_geometry)

        if point_count < min_points:
            reasons.append("too_few_points")

        if point_count > max_points:
            reasons.append("too_many_points")

        if AtlasBuildingSelector._has_duplicate_points(clean_geometry):
            reasons.append("duplicate_points")

        area = abs(AtlasBuildingSelector._polygon_area(clean_geometry))

        if area <= 0:
            reasons.append("zero_area")

        aspect_ratio = AtlasBuildingSelector._aspect_ratio(clean_geometry)

        if aspect_ratio > max_aspect_ratio:
            reasons.append("bad_aspect_ratio")

        centroid = AtlasBuildingSelector._centroid(clean_geometry)

        if centroid is None:
            reasons.append("no_centroid")

        accepted = len(reasons) == 0

        score = AtlasBuildingSelector._score(
            point_count=point_count,
            aspect_ratio=aspect_ratio,
            area=area,
        )

        return {
            "accepted": accepted,
            "building": building,
            "building_id": building_id,
            "geometry": clean_geometry,
            "point_count": point_count,
            "area": area,
            "aspect_ratio": aspect_ratio,
            "centroid": centroid,
            "score": score,
            "reasons": reasons,
        }

    @staticmethod
    def _find_best_cluster(items, limit):
        """
        En iyi kümeyi bulur.

        Mantık:
        Her kabul edilmiş binayı merkez kabul eder.
        Ona en yakın binaları seçer.
        Kümeyi kalite + yakınlık açısından puanlar.
        En iyi kümeyi döndürür.
        """

        if len(items) <= limit:
            return sorted(items, key=lambda item: item["score"], reverse=True)

        best_cluster = None
        best_cluster_score = -999999

        for center_item in items:
            center = center_item["centroid"]

            candidates = []

            for item in items:
                distance = AtlasBuildingSelector._distance(
                    center,
                    item["centroid"],
                )

                cluster_score = item["score"] - (distance * 100000)

                candidates.append(
                    {
                        **item,
                        "distance_to_center": distance,
                        "cluster_score": cluster_score,
                    }
                )

            candidates.sort(key=lambda item: item["distance_to_center"])

            cluster = candidates[:limit]

            total_score = sum(item["cluster_score"] for item in cluster)
            max_distance = max(item["distance_to_center"] for item in cluster)

            compactness_bonus = 1 / (max_distance + 0.000000001)

            final_score = total_score + compactness_bonus

            if final_score > best_cluster_score:
                best_cluster_score = final_score
                best_cluster = cluster

        return sorted(best_cluster, key=lambda item: item["distance_to_center"])

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
    def _remove_closing_point(points):
        if len(points) > 1 and points[0] == points[-1]:
            return points[:-1]

        return points[:]

    @staticmethod
    def _has_duplicate_points(points):
        return len(points) != len(set(points))

    @staticmethod
    def _polygon_area(points):
        if len(points) < 3:
            return 0.0

        area = 0.0

        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]

            area += x1 * y2
            area -= x2 * y1

        return area / 2.0

    @staticmethod
    def _aspect_ratio(points):
        if len(points) < 2:
            return 999999

        xs = [p[1] for p in points]
        ys = [p[0] for p in points]

        width = max(xs) - min(xs)
        height = max(ys) - min(ys)

        small = min(width, height)
        large = max(width, height)

        if small <= 0:
            return 999999

        return large / small

    @staticmethod
    def _centroid(points):
        if not points:
            return None

        lat_sum = 0.0
        lon_sum = 0.0

        for lat, lon in points:
            lat_sum += lat
            lon_sum += lon

        return (
            lat_sum / len(points),
            lon_sum / len(points),
        )

    @staticmethod
    def _distance(a, b):
        if a is None or b is None:
            return 999999

        lat1, lon1 = a
        lat2, lon2 = b

        d_lat = lat1 - lat2
        d_lon = lon1 - lon2

        return math.sqrt((d_lat * d_lat) + (d_lon * d_lon))

    @staticmethod
    def _score(point_count, aspect_ratio, area):
        score = 100.0

        score -= abs(point_count - 4) * 5.0
        score -= max(0.0, aspect_ratio - 1.5) * 8.0

        if area <= 0:
            score -= 50.0

        return max(score, 1.0)

    @staticmethod
    def _print_report(total, accepted, selected):
        print("")
        print("=" * 60)
        print("ATLAS BUILDING SELECTOR REPORT")
        print("=" * 60)
        print(f"Candidate buildings : {total}")
        print(f"Accepted buildings  : {accepted}")
        print(f"Selected buildings  : {len(selected)}")
        print("-" * 60)

        for item in selected:
            distance = item.get("distance_to_center", 0)

            print(
                f"SELECTED | ID: {item['building_id']} | "
                f"Points: {item['point_count']} | "
                f"Aspect: {item['aspect_ratio']:.2f} | "
                f"Distance: {distance:.8f} | "
                f"Score: {item['score']:.2f}"
            )

        print("=" * 60)
        print("")
