import math


class AtlasTerrainContourBandBuilder:

    @staticmethod
    def build_band(polyline, half_width_mm):
        half_width_mm = float(half_width_mm)

        if half_width_mm <= 0.0:
            raise ValueError("half_width_mm must be positive")

        if len(polyline) < 2:
            return []

        points = []
        for point in polyline:
            if not points or point != points[-1]:
                points.append(point)

        if len(points) < 2:
            return []

        closed = (
            len(points) >= 3
            and points[0] == points[-1]
        )

        if closed:
            points = points[:-1]

        left = []
        right = []

        count = len(points)

        for i in range(count):
            if closed:
                p0 = points[i]
                p1 = points[(i + 1) % count]
            else:
                if i == count - 1:
                    p0 = points[i - 1]
                    p1 = points[i]
                else:
                    p0 = points[i]
                    p1 = points[i + 1]

            dx = p1[0] - p0[0]
            dy = p1[1] - p0[1]

            length = math.hypot(dx, dy)

            if length == 0.0:
                continue

            nx = -dy / length
            ny = dx / length

            x, y = points[i]

            left.append(
                (
                    x + nx * half_width_mm,
                    y + ny * half_width_mm,
                )
            )

            right.append(
                (
                    x - nx * half_width_mm,
                    y - ny * half_width_mm,
                )
            )

        if closed:
            left.append(left[0])
            right.append(right[0])

        return left + list(reversed(right))
