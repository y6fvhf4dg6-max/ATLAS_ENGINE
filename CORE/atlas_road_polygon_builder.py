# CORE/atlas_road_polygon_builder.py

import math


class AtlasRoadPolygonBuilder:
    """
    ATLAS Road Polygon Builder v1.0

    Görev:
    Yol centerline verisinden tek parça yol poligonu üretmek.

    Bu ilk sürüm:
    - Segment bazlı dikdörtgen mesh üretmez.
    - Her polyline için left/right offset noktaları üretir.
    - Basit polygon candidate döndürür.
    - Henüz gelişmiş miter/round join yapmaz.
    """

    @staticmethod
    def build_road_polygons(road_footprints, debug=True, clip_bounds=None):
        polygons = []
        accepted = 0
        skipped = 0

        for footprint in road_footprints:
            polygon = AtlasRoadPolygonBuilder._build_polygon_from_footprint(footprint)

            if polygon:
                if clip_bounds:
                    polygon = AtlasRoadPolygonBuilder._clip_polygon_to_bounds(
                        polygon,
                        clip_bounds,
                    )

            if polygon and len(polygon.get("points", [])) >= 3:
                polygons.append(polygon)
                accepted += 1
            else:
                skipped += 1
        else:
            skipped += 1

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS ROAD POLYGON BUILDER REPORT")
            print("=" * 60)
            print(f"Input footprints : {len(road_footprints)}")
            print(f"Accepted polygons: {accepted}")
            print(f"Skipped polygons : {skipped}")
            print("=" * 60)
            print("")

        return polygons

    @staticmethod
    def _build_polygon_from_footprint(footprint):
        segments = footprint.get("segments", [])

        if not segments:
            return None

        centerline = AtlasRoadPolygonBuilder._extract_centerline(segments)

        if len(centerline) < 2:
            return None

        width_mm = footprint.get("width_mm")

        if not width_mm:
            return None

        polygon_points = AtlasRoadPolygonBuilder._offset_polyline_to_polygon(
            centerline=centerline,
            width_mm=width_mm,
        )

        if len(polygon_points) < 3:
            return None

        return {
            "type": "road_polygon",
            "road_type": footprint.get("road_type"),
            "width_mm": width_mm,
            "points": polygon_points,
            "centerline": centerline,
        }

    @staticmethod
    def _extract_centerline(segments):
        centerline = []

        for index, segment in enumerate(segments):
            pair = segment.get("centerline", [])

            if len(pair) != 2:
                continue

            p1, p2 = pair

            if index == 0:
                centerline.append(p1)

            centerline.append(p2)

        return centerline

    @staticmethod
    def _offset_polyline_to_polygon(centerline, width_mm):
        half_width = width_mm / 2.0

        left_points = []
        right_points = []

        for index, point in enumerate(centerline):
            normal = AtlasRoadPolygonBuilder._estimate_vertex_normal(
                centerline,
                index,
            )

            if normal is None:
                continue

            nx, ny = normal
            x, y = point

            left_points.append((x + nx * half_width, y + ny * half_width))
            right_points.append((x - nx * half_width, y - ny * half_width))

        if len(left_points) < 2 or len(right_points) < 2:
            return []

        polygon = left_points + list(reversed(right_points))

        return polygon

    @staticmethod
    def _estimate_vertex_normal(points, index):
        if len(points) < 2:
            return None

        if index == 0:
            p1 = points[0]
            p2 = points[1]
        elif index == len(points) - 1:
            p1 = points[-2]
            p2 = points[-1]
        else:
            prev_point = points[index - 1]
            next_point = points[index + 1]

            p1 = prev_point
            p2 = next_point

        x1, y1 = p1
        x2, y2 = p2

        dx = x2 - x1
        dy = y2 - y1

        length = math.sqrt((dx * dx) + (dy * dy))

        if length <= 0:
            return None

        nx = -dy / length
        ny = dx / length

        return nx, ny

    @staticmethod
    def _clip_polygon_to_bounds(polygon, bounds):
        points = polygon.get("points", [])

        if len(points) < 3:
            return None

        min_x = bounds["min_x"]
        max_x = bounds["max_x"]
        min_y = bounds["min_y"]
        max_y = bounds["max_y"]

        clipped = AtlasRoadPolygonBuilder._clip_points_against_edge(
            points,
            "left",
            min_x,
        )
        clipped = AtlasRoadPolygonBuilder._clip_points_against_edge(
            clipped,
            "right",
            max_x,
        )
        clipped = AtlasRoadPolygonBuilder._clip_points_against_edge(
            clipped,
            "bottom",
            min_y,
        )
        clipped = AtlasRoadPolygonBuilder._clip_points_against_edge(
            clipped,
            "top",
            max_y,
        )

        if len(clipped) < 3:
            return None

        new_polygon = dict(polygon)
        new_polygon["points"] = clipped
        return new_polygon

    @staticmethod
    def _clip_points_against_edge(points, edge, value):
        if not points:
            return []

        clipped = []
        previous = points[-1]

        for current in points:
            previous_inside = AtlasRoadPolygonBuilder._point_inside_edge(
                previous,
                edge,
                value,
            )
            current_inside = AtlasRoadPolygonBuilder._point_inside_edge(
                current,
                edge,
                value,
            )

            if current_inside:
                if not previous_inside:
                    clipped.append(
                        AtlasRoadPolygonBuilder._intersect_edge(
                            previous,
                            current,
                            edge,
                            value,
                        )
                    )
                clipped.append(current)
            elif previous_inside:
                clipped.append(
                    AtlasRoadPolygonBuilder._intersect_edge(
                        previous,
                        current,
                        edge,
                        value,
                    )
                )

            previous = current

        return clipped

    @staticmethod
    def _point_inside_edge(point, edge, value):
        x, y = point

        if edge == "left":
            return x >= value

        if edge == "right":
            return x <= value

        if edge == "bottom":
            return y >= value

        if edge == "top":
            return y <= value

        return True

    @staticmethod
    def _intersect_edge(p1, p2, edge, value):
        x1, y1 = p1
        x2, y2 = p2

        dx = x2 - x1
        dy = y2 - y1

        if edge in ("left", "right"):
            if dx == 0:
                return p1

            t = (value - x1) / dx
            return (value, y1 + (dy * t))

        if edge in ("bottom", "top"):
            if dy == 0:
                return p1

            t = (value - y1) / dy
            return (x1 + (dx * t), value)

        return p1
