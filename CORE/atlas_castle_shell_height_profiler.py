"""
ATLAS Castle Shell Height Profiler v0.1

Kale kabuğunun dış sınırı ile iç avlu sınırı arasındaki
yerel kalınlığı ölçerek kule ve burç bölgelerini belirler.

Temel kural:
- İnce bölgeler normal sur yüksekliğinde kalır
- Sürekli kalınlaşan bölgeler kule/burç olarak yükseltilir
- Tekil kalın noktalar elenir
"""

import math


class AtlasCastleShellHeightProfiler:
    NORMAL_HEIGHT_MULTIPLIER = 1.0
    TOWER_HEIGHT_MULTIPLIER = 1.70

    THICKNESS_PERCENTILE = 0.75
    SMOOTHING_RADIUS = 2
    MIN_RUN_LENGTH = 5
    EXPANSION_RADIUS = 2
    MIN_RUN_AVERAGE_RATIO = 1.20
    MIN_RUN_MAXIMUM_RATIO = 1.45

    EPSILON = 1e-9

    @staticmethod
    def build_profile(
        outer_ring,
        inner_rings,
    ):
        point_count = len(outer_ring)

        if point_count < 3 or not inner_rings:
            return {
                "multipliers": [1.0] * point_count,
                "tower_flags": [False] * point_count,
                "thicknesses": [0.0] * point_count,
                "smoothed_thicknesses": [0.0] * point_count,
                "threshold_mm": 0.0,
                "tower_point_count": 0,
                "tower_runs": [],
            }

        thicknesses = [
            AtlasCastleShellHeightProfiler._distance_to_rings(
                point=point,
                rings=inner_rings,
            )
            for point in outer_ring
        ]

        smoothed = AtlasCastleShellHeightProfiler._smooth_circular(
            values=thicknesses,
            radius=AtlasCastleShellHeightProfiler.SMOOTHING_RADIUS,
        )

        threshold = AtlasCastleShellHeightProfiler._percentile(
            values=smoothed,
            percentile=(AtlasCastleShellHeightProfiler.THICKNESS_PERCENTILE),
        )

        flags = [value >= threshold for value in smoothed]

        flags = AtlasCastleShellHeightProfiler._remove_short_runs(
            flags=flags,
            minimum_length=(AtlasCastleShellHeightProfiler.MIN_RUN_LENGTH),
        )

        flags = AtlasCastleShellHeightProfiler._expand_flags(
            flags=flags,
            radius=(AtlasCastleShellHeightProfiler.EXPANSION_RADIUS),
        )

        runs = AtlasCastleShellHeightProfiler._find_circular_runs(flags)

        flags = AtlasCastleShellHeightProfiler._filter_weak_runs(
            flags=flags,
            values=smoothed,
            threshold=threshold,
            runs=runs,
        )

        runs = AtlasCastleShellHeightProfiler._find_circular_runs(flags)

        multipliers = [
            (
                AtlasCastleShellHeightProfiler.TOWER_HEIGHT_MULTIPLIER
                if flag
                else AtlasCastleShellHeightProfiler.NORMAL_HEIGHT_MULTIPLIER
            )
            for flag in flags
        ]

        return {
            "multipliers": multipliers,
            "tower_flags": flags,
            "thicknesses": thicknesses,
            "smoothed_thicknesses": smoothed,
            "threshold_mm": threshold,
            "tower_point_count": sum(flags),
            "tower_runs": runs,
        }

    @staticmethod
    def _distance_to_rings(
        point,
        rings,
    ):
        minimum = float("inf")

        for ring in rings:
            if len(ring) < 2:
                continue

            for index in range(len(ring)):
                next_index = (index + 1) % len(ring)

                distance = AtlasCastleShellHeightProfiler._point_to_segment_distance(
                    point=point,
                    start=ring[index],
                    end=ring[next_index],
                )

                minimum = min(
                    minimum,
                    distance,
                )

        if math.isinf(minimum):
            return 0.0

        return minimum

    @staticmethod
    def _point_to_segment_distance(
        point,
        start,
        end,
    ):
        px, py = point
        x1, y1 = start
        x2, y2 = end

        dx = x2 - x1
        dy = y2 - y1

        length_squared = dx * dx + dy * dy

        if length_squared <= (AtlasCastleShellHeightProfiler.EPSILON):
            return math.hypot(
                px - x1,
                py - y1,
            )

        ratio = ((px - x1) * dx + (py - y1) * dy) / length_squared

        ratio = max(
            0.0,
            min(1.0, ratio),
        )

        nearest_x = x1 + ratio * dx
        nearest_y = y1 + ratio * dy

        return math.hypot(
            px - nearest_x,
            py - nearest_y,
        )

    @staticmethod
    def _smooth_circular(
        values,
        radius,
    ):
        count = len(values)

        if count == 0:
            return []

        smoothed = []

        for index in range(count):
            window = [
                values[(index + offset) % count]
                for offset in range(
                    -radius,
                    radius + 1,
                )
            ]

            smoothed.append(sum(window) / len(window))

        return smoothed

    @staticmethod
    def _remove_short_runs(
        flags,
        minimum_length,
    ):
        count = len(flags)

        if count == 0:
            return []

        if all(flags):
            return list(flags)

        false_index = next(index for index, flag in enumerate(flags) if not flag)

        rotated = flags[false_index + 1 :] + flags[: false_index + 1]

        cleaned = [False] * count
        run_start = None

        for index, flag in enumerate(rotated + [False]):
            if flag and run_start is None:
                run_start = index

            if not flag and run_start is not None:
                run_length = index - run_start

                if run_length >= minimum_length:
                    for run_index in range(
                        run_start,
                        index,
                    ):
                        cleaned[run_index] = True

                run_start = None

        split = count - false_index - 1

        return cleaned[split:] + cleaned[:split]

    @staticmethod
    def _expand_flags(
        flags,
        radius,
    ):
        count = len(flags)
        expanded = list(flags)

        for index, flag in enumerate(flags):
            if not flag:
                continue

            for offset in range(
                -radius,
                radius + 1,
            ):
                expanded[(index + offset) % count] = True

        return expanded

    @staticmethod
    def _find_circular_runs(flags):
        count = len(flags)

        if count == 0:
            return []

        if all(flags):
            return [(0, count - 1, count)]

        false_index = next(index for index, flag in enumerate(flags) if not flag)

        ordered_indices = [
            (false_index + 1 + offset) % count for offset in range(count)
        ]

        runs = []
        current = []

        for index in ordered_indices:
            if flags[index]:
                current.append(index)
            elif current:
                runs.append(
                    (
                        current[0],
                        current[-1],
                        len(current),
                    )
                )
                current = []

        if current:
            runs.append(
                (
                    current[0],
                    current[-1],
                    len(current),
                )
            )

        return runs

    @staticmethod
    def _filter_weak_runs(
        flags,
        values,
        threshold,
        runs,
    ):
        filtered = [False] * len(flags)

        for start, end, _length in runs:
            indices = []
            current = start

            while True:
                indices.append(current)

                if current == end:
                    break

                current = (current + 1) % len(flags)

            run_values = [values[index] for index in indices]

            if not run_values:
                continue

            average_value = sum(run_values) / len(run_values)

            maximum_value = max(run_values)

            average_ok = (
                average_value
                >= threshold * AtlasCastleShellHeightProfiler.MIN_RUN_AVERAGE_RATIO
            )

            maximum_ok = (
                maximum_value
                >= threshold * AtlasCastleShellHeightProfiler.MIN_RUN_MAXIMUM_RATIO
            )

            if not average_ok and not maximum_ok:
                continue

            for index in indices:
                filtered[index] = True

        return filtered

    @staticmethod
    def _percentile(
        values,
        percentile,
    ):
        ordered = sorted(values)

        if not ordered:
            return 0.0

        position = percentile * (len(ordered) - 1)

        lower = int(math.floor(position))
        upper = int(math.ceil(position))

        if lower == upper:
            return ordered[lower]

        fraction = position - lower

        return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction
