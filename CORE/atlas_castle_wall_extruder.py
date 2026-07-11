# CORE/atlas_castle_wall_extruder.py

import math

from CORE.atlas_foundation_sampler import AtlasFoundationSampler
from CORE.atlas_castle_wall_profile import AtlasCastleWallProfile


class AtlasCastleWallExtruder:
    """
    ATLAS Castle Wall Extruder v0.1

    Amaç:
    - Polyline boyunca sürekli bir duvar şeridi üretmek
    - Her segmenti ayrı prizma hâline getirmemek
    - Köşe birleşimlerinde miter yaklaşımı kullanmak
    - Kapalı halkaları düzgün kapatmak
    - Terrain yüksekliğini her sınır noktasında örneklemek
    - Baskıya uygun kapalı mesh üretmek

    Bu sürüm yalnızca ana sur gövdesini üretir.
    Mazgal, burç ve kule sistemi sonraki aşamalardır.
    """

    MITER_LIMIT = 4.0
    EPSILON = 1e-9

    @staticmethod
    def build_wall(
        points,
        terrain_mesh,
        width_mm,
        height_mm,
        closed=False,
    ):
        clean_points = AtlasCastleWallExtruder._clean_points(
            points=points,
            closed=closed,
        )

        if closed:
            if len(clean_points) < 3:
                return None
        elif len(clean_points) < 2:
            return None

        offset_result = AtlasCastleWallExtruder._build_offset_lines(
            points=clean_points,
            half_width=width_mm / 2.0,
            closed=closed,
        )

        if offset_result is None:
            return None

        left_points, right_points = offset_result
        # Kule profili geçici olarak kapalı.
        # Relation outer/inner sınırları birlikte analiz edilmeden
        # ayrı ayrı yükseklik verilmemelidir.
        height_multipliers = [1.0] * len(clean_points)

        if len(left_points) != len(clean_points):
            return None

        if len(right_points) != len(clean_points):
            return None

        bottom_left = []
        bottom_right = []
        top_left = []
        top_right = []

        for index, (left, right) in enumerate(zip(left_points, right_points)):
            left_z = AtlasFoundationSampler.terrain_z_at_xy(
                terrain_mesh=terrain_mesh,
                x=left[0],
                y=left[1],
            )

            right_z = AtlasFoundationSampler.terrain_z_at_xy(
                terrain_mesh=terrain_mesh,
                x=right[0],
                y=right[1],
            )

            bottom_left.append(
                (
                    left[0],
                    left[1],
                    left_z,
                )
            )

            bottom_right.append(
                (
                    right[0],
                    right[1],
                    right_z,
                )
            )

            profile_height_mm = height_mm * height_multipliers[index]

            top_left.append(
                (
                    left[0],
                    left[1],
                    left_z + profile_height_mm,
                )
            )

            top_right.append(
                (
                    right[0],
                    right[1],
                    right_z + profile_height_mm,
                )
            )

        triangles = []
        walls = []

        segment_count = len(clean_points) if closed else len(clean_points) - 1

        for index in range(segment_count):
            next_index = (index + 1) % len(clean_points)

            bl1 = bottom_left[index]
            bl2 = bottom_left[next_index]

            br1 = bottom_right[index]
            br2 = bottom_right[next_index]

            tl1 = top_left[index]
            tl2 = top_left[next_index]

            tr1 = top_right[index]
            tr2 = top_right[next_index]

            # Alt yüzey
            triangles.append((bl1, br2, br1))
            triangles.append((bl1, bl2, br2))

            # Üst yüzey
            triangles.append((tl1, tr1, tr2))
            triangles.append((tl1, tr2, tl2))

            # Sol dış duvar
            triangles.append((bl1, tl1, tl2))
            triangles.append((bl1, tl2, bl2))

            # Sağ dış duvar
            triangles.append((br1, br2, tr2))
            triangles.append((br1, tr2, tr1))

            walls.append(
                (
                    bl1,
                    bl2,
                    tl2,
                    tl1,
                )
            )

            walls.append(
                (
                    br1,
                    tr1,
                    tr2,
                    br2,
                )
            )

        if not closed:
            AtlasCastleWallExtruder._add_end_cap(
                triangles=triangles,
                bottom_left=bottom_left[0],
                bottom_right=bottom_right[0],
                top_left=top_left[0],
                top_right=top_right[0],
                reverse=True,
            )

            AtlasCastleWallExtruder._add_end_cap(
                triangles=triangles,
                bottom_left=bottom_left[-1],
                bottom_right=bottom_right[-1],
                top_left=top_left[-1],
                top_right=top_right[-1],
                reverse=False,
            )

        return {
            "type": "castle_wall_strip",
            "bottom": bottom_left + bottom_right,
            "top": top_left + top_right,
            "walls": walls,
            "triangles": triangles,
            "closed": closed,
            "wall_width_mm": width_mm,
            "wall_height_mm": height_mm,
            "left_points": left_points,
            "right_points": right_points,
        }

    @staticmethod
    def _build_offset_lines(
        points,
        half_width,
        closed,
    ):
        segment_normals = []

        segment_count = len(points) if closed else len(points) - 1

        for index in range(segment_count):
            next_index = (index + 1) % len(points)

            normal = AtlasCastleWallExtruder._segment_normal(
                points[index],
                points[next_index],
            )

            if normal is None:
                return None

            segment_normals.append(normal)

        left_points = []
        right_points = []

        for index, point in enumerate(points):
            offset = AtlasCastleWallExtruder._vertex_offset(
                index=index,
                points=points,
                segment_normals=segment_normals,
                half_width=half_width,
                closed=closed,
            )

            if offset is None:
                return None

            ox, oy = offset
            x, y = point

            left_points.append(
                (
                    x + ox,
                    y + oy,
                )
            )

            right_points.append(
                (
                    x - ox,
                    y - oy,
                )
            )

        return left_points, right_points

    @staticmethod
    def _vertex_offset(
        index,
        points,
        segment_normals,
        half_width,
        closed,
    ):
        point_count = len(points)

        if not closed and index == 0:
            nx, ny = segment_normals[0]
            return (
                nx * half_width,
                ny * half_width,
            )

        if not closed and index == point_count - 1:
            nx, ny = segment_normals[-1]
            return (
                nx * half_width,
                ny * half_width,
            )

        previous_segment_index = index - 1 if index > 0 else len(segment_normals) - 1

        next_segment_index = index if index < len(segment_normals) else 0

        n1 = segment_normals[previous_segment_index]
        n2 = segment_normals[next_segment_index]

        mx = n1[0] + n2[0]
        my = n1[1] + n2[1]

        miter_length = math.sqrt(mx * mx + my * my)

        if miter_length <= AtlasCastleWallExtruder.EPSILON:
            return (
                n2[0] * half_width,
                n2[1] * half_width,
            )

        mx /= miter_length
        my /= miter_length

        denominator = mx * n2[0] + my * n2[1]

        if abs(denominator) <= AtlasCastleWallExtruder.EPSILON:
            return (
                n2[0] * half_width,
                n2[1] * half_width,
            )

        scale = half_width / denominator
        max_scale = half_width * AtlasCastleWallExtruder.MITER_LIMIT

        if scale > max_scale:
            scale = max_scale
        elif scale < -max_scale:
            scale = -max_scale

        return (
            mx * scale,
            my * scale,
        )

    @staticmethod
    def _segment_normal(p1, p2):
        x1, y1 = p1
        x2, y2 = p2

        dx = x2 - x1
        dy = y2 - y1

        length = math.sqrt(dx * dx + dy * dy)

        if length <= AtlasCastleWallExtruder.EPSILON:
            return None

        return (
            -dy / length,
            dx / length,
        )

    @staticmethod
    def _clean_points(points, closed):
        clean = []

        for point in points:
            if point is None or len(point) < 2:
                continue

            x = float(point[0])
            y = float(point[1])

            if clean:
                previous = clean[-1]

                if (
                    abs(previous[0] - x) <= AtlasCastleWallExtruder.EPSILON
                    and abs(previous[1] - y) <= AtlasCastleWallExtruder.EPSILON
                ):
                    continue

            clean.append((x, y))

        if (
            closed
            and len(clean) >= 2
            and AtlasCastleWallExtruder._same_point(
                clean[0],
                clean[-1],
            )
        ):
            clean.pop()

        return clean

    @staticmethod
    def _same_point(p1, p2):
        return (
            abs(p1[0] - p2[0]) <= AtlasCastleWallExtruder.EPSILON
            and abs(p1[1] - p2[1]) <= AtlasCastleWallExtruder.EPSILON
        )

    @staticmethod
    def _add_end_cap(
        triangles,
        bottom_left,
        bottom_right,
        top_left,
        top_right,
        reverse,
    ):
        if reverse:
            triangles.append(
                (
                    bottom_left,
                    top_right,
                    bottom_right,
                )
            )

            triangles.append(
                (
                    bottom_left,
                    top_left,
                    top_right,
                )
            )
        else:
            triangles.append(
                (
                    bottom_left,
                    bottom_right,
                    top_right,
                )
            )

            triangles.append(
                (
                    bottom_left,
                    top_right,
                    top_left,
                )
            )
