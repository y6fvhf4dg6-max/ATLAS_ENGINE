# CORE/atlas_castle_wall_profile.py

import math


class AtlasCastleWallProfile:
    """
    ATLAS Castle Wall Profile v0.3

    Rumeli Hisarı gibi yapılardaki yuvarlak burçları algılar.

    v0.3 yaklaşımı:
    - Keskin tekil köşeleri kule saymaz
    - Aynı yönde devam eden küçük dönüşleri izler
    - Uzun ve yumuşak yayları burç/kule olarak işaretler
    - Düz sur bölümlerini normal yükseklikte bırakır
    """

    DEFAULT_HEIGHT_MULTIPLIER = 1.0
    TOWER_HEIGHT_MULTIPLIER = 1.85

    WINDOW_RADIUS = 7

    MIN_GENTLE_TURN_RAD = math.radians(0.35)
    MAX_GENTLE_TURN_RAD = math.radians(14.0)
    SHARP_TURN_RAD = math.radians(24.0)

    MIN_ACTIVE_TURNS = 5
    MIN_TOTAL_ARC_TURN_RAD = math.radians(28.0)
    MIN_DIRECTION_RATIO = 0.72

    MIN_RUN_LENGTH = 4
    FLAG_EXPANSION_RADIUS = 2

    EPSILON = 1e-9

    @staticmethod
    def build_height_multipliers(
        points,
        closed=False,
    ):
        point_count = len(points)

        if point_count < 7:
            return [AtlasCastleWallProfile.DEFAULT_HEIGHT_MULTIPLIER for _ in points]

        signed_turns = AtlasCastleWallProfile._calculate_signed_turns(
            points=points,
            closed=closed,
        )

        flags = [False] * point_count

        for index in range(point_count):
            indices = AtlasCastleWallProfile._window_indices(
                index=index,
                point_count=point_count,
                closed=closed,
            )

            window_turns = [signed_turns[item_index] for item_index in indices]

            if AtlasCastleWallProfile._is_gentle_arc(window_turns):
                flags[index] = True

        flags = AtlasCastleWallProfile._remove_short_runs(
            flags=flags,
            closed=closed,
            minimum_length=AtlasCastleWallProfile.MIN_RUN_LENGTH,
        )

        flags = AtlasCastleWallProfile._expand_flags(
            flags=flags,
            closed=closed,
            radius=AtlasCastleWallProfile.FLAG_EXPANSION_RADIUS,
        )

        return [
            (
                AtlasCastleWallProfile.TOWER_HEIGHT_MULTIPLIER
                if flag
                else AtlasCastleWallProfile.DEFAULT_HEIGHT_MULTIPLIER
            )
            for flag in flags
        ]

    @staticmethod
    def _is_gentle_arc(turns):
        gentle_turns = [
            turn
            for turn in turns
            if (
                AtlasCastleWallProfile.MIN_GENTLE_TURN_RAD
                <= abs(turn)
                <= AtlasCastleWallProfile.MAX_GENTLE_TURN_RAD
            )
        ]

        if len(gentle_turns) < AtlasCastleWallProfile.MIN_ACTIVE_TURNS:
            return False

        if any(abs(turn) >= AtlasCastleWallProfile.SHARP_TURN_RAD for turn in turns):
            return False

        positive_count = sum(1 for turn in gentle_turns if turn > 0)

        negative_count = sum(1 for turn in gentle_turns if turn < 0)

        dominant_count = max(
            positive_count,
            negative_count,
        )

        direction_ratio = dominant_count / len(gentle_turns)

        if direction_ratio < AtlasCastleWallProfile.MIN_DIRECTION_RATIO:
            return False

        dominant_sign = 1.0 if positive_count >= negative_count else -1.0

        total_dominant_turn = sum(
            abs(turn) for turn in gentle_turns if turn * dominant_sign > 0
        )

        return total_dominant_turn >= AtlasCastleWallProfile.MIN_TOTAL_ARC_TURN_RAD

    @staticmethod
    def _calculate_signed_turns(
        points,
        closed,
    ):
        point_count = len(points)
        turns = [0.0] * point_count

        for index in range(point_count):
            if not closed and index in {0, point_count - 1}:
                continue

            previous_index = index - 1 if index > 0 else point_count - 1

            next_index = index + 1 if index < point_count - 1 else 0

            turns[index] = AtlasCastleWallProfile._signed_turn_angle(
                previous_point=points[previous_index],
                current_point=points[index],
                next_point=points[next_index],
            )

        return turns

    @staticmethod
    def _signed_turn_angle(
        previous_point,
        current_point,
        next_point,
    ):
        ax = current_point[0] - previous_point[0]
        ay = current_point[1] - previous_point[1]

        bx = next_point[0] - current_point[0]
        by = next_point[1] - current_point[1]

        length_a = math.sqrt(ax * ax + ay * ay)
        length_b = math.sqrt(bx * bx + by * by)

        if (
            length_a <= AtlasCastleWallProfile.EPSILON
            or length_b <= AtlasCastleWallProfile.EPSILON
        ):
            return 0.0

        ax /= length_a
        ay /= length_a
        bx /= length_b
        by /= length_b

        cross = ax * by - ay * bx
        dot = ax * bx + ay * by

        dot = max(-1.0, min(1.0, dot))

        return math.atan2(
            cross,
            dot,
        )

    @staticmethod
    def _window_indices(
        index,
        point_count,
        closed,
    ):
        indices = []

        for offset in range(
            -AtlasCastleWallProfile.WINDOW_RADIUS,
            AtlasCastleWallProfile.WINDOW_RADIUS + 1,
        ):
            candidate = index + offset

            if closed:
                candidate %= point_count
            elif candidate < 0 or candidate >= point_count:
                continue

            indices.append(candidate)

        return indices

    @staticmethod
    def _remove_short_runs(
        flags,
        closed,
        minimum_length,
    ):
        point_count = len(flags)

        if point_count == 0:
            return []

        if closed:
            if all(flags):
                return list(flags)

            start_false = next(index for index, flag in enumerate(flags) if not flag)

            rotated = flags[start_false + 1 :] + flags[: start_false + 1]

            cleaned_rotated = AtlasCastleWallProfile._remove_short_runs(
                flags=rotated,
                closed=False,
                minimum_length=minimum_length,
            )

            split = point_count - start_false - 1

            return cleaned_rotated[split:] + cleaned_rotated[:split]

        cleaned = [False] * point_count
        start = None

        for index, flag in enumerate(flags + [False]):
            if flag and start is None:
                start = index

            if not flag and start is not None:
                if index - start >= minimum_length:
                    for run_index in range(start, index):
                        cleaned[run_index] = True

                start = None

        return cleaned

    @staticmethod
    def _expand_flags(
        flags,
        closed,
        radius,
    ):
        expanded = list(flags)
        point_count = len(flags)

        for index, flag in enumerate(flags):
            if not flag:
                continue

            for offset in range(-radius, radius + 1):
                candidate = index + offset

                if closed:
                    candidate %= point_count
                elif candidate < 0 or candidate >= point_count:
                    continue

                expanded[candidate] = True

        return expanded
