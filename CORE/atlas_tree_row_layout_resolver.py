import math


class AtlasTreeRowLayoutResolver:
    @staticmethod
    def _distance(a, b):
        return math.hypot(
            float(b[0]) - float(a[0]),
            float(b[1]) - float(a[1]),
        )

    @classmethod
    def _interpolate_polyline(
        cls,
        geometry,
        count,
    ):
        geometry = tuple(geometry or ())

        if count < 2:
            raise ValueError("count must be at least 2")

        if len(geometry) < 2:
            raise ValueError(
                "source_geometry must contain at least two points"
            )

        segment_lengths = [
            cls._distance(start, end)
            for start, end in zip(
                geometry,
                geometry[1:],
            )
        ]

        total_length = sum(segment_lengths)

        if total_length <= 0.0:
            return tuple(
                geometry[0]
                for _ in range(count)
            )

        targets = [
            total_length * index / (count - 1)
            for index in range(count)
        ]

        points = []
        segment_index = 0
        segment_start_distance = 0.0

        for target in targets:
            while (
                segment_index < len(segment_lengths) - 1
                and target
                > segment_start_distance
                + segment_lengths[segment_index]
            ):
                segment_start_distance += (
                    segment_lengths[segment_index]
                )
                segment_index += 1

            start = geometry[segment_index]
            end = geometry[segment_index + 1]
            segment_length = segment_lengths[segment_index]

            if segment_length <= 0.0:
                ratio = 0.0
            else:
                ratio = (
                    target - segment_start_distance
                ) / segment_length

            ratio = max(0.0, min(1.0, ratio))

            points.append(
                (
                    float(start[0])
                    + (
                        float(end[0]) - float(start[0])
                    )
                    * ratio,
                    float(start[1])
                    + (
                        float(end[1]) - float(start[1])
                    )
                    * ratio,
                )
            )

        points[0] = tuple(geometry[0])
        points[-1] = tuple(geometry[-1])

        return tuple(points)

    @classmethod
    def _interpolate_polyline_with_segments(
        cls,
        geometry,
        count,
        *,
        source_segment_offset=0,
    ):
        geometry = tuple(geometry or ())

        if count < 2:
            raise ValueError("count must be at least 2")

        if len(geometry) < 2:
            raise ValueError(
                "source_geometry must contain at least two points"
            )

        segment_lengths = [
            cls._distance(start, end)
            for start, end in zip(
                geometry,
                geometry[1:],
            )
        ]

        total_length = sum(segment_lengths)

        if total_length <= 0.0:
            return (
                tuple(
                    geometry[0]
                    for _ in range(count)
                ),
                tuple(
                    source_segment_offset
                    for _ in range(count)
                ),
            )

        targets = [
            total_length * index / (count - 1)
            for index in range(count)
        ]

        points = []
        source_segments = []
        segment_index = 0
        segment_start_distance = 0.0

        for target in targets:
            while (
                segment_index < len(segment_lengths) - 1
                and target
                > segment_start_distance
                + segment_lengths[segment_index]
            ):
                segment_start_distance += (
                    segment_lengths[segment_index]
                )
                segment_index += 1

            start = geometry[segment_index]
            end = geometry[segment_index + 1]
            segment_length = segment_lengths[segment_index]

            if segment_length <= 0.0:
                ratio = 0.0
            else:
                ratio = (
                    target - segment_start_distance
                ) / segment_length

            ratio = max(0.0, min(1.0, ratio))

            points.append(
                (
                    float(start[0])
                    + (
                        float(end[0]) - float(start[0])
                    )
                    * ratio,
                    float(start[1])
                    + (
                        float(end[1]) - float(start[1])
                    )
                    * ratio,
                )
            )

            source_segments.append(
                source_segment_offset + segment_index
            )

        points[0] = tuple(geometry[0])
        points[-1] = tuple(geometry[-1])

        return (
            tuple(points),
            tuple(source_segments),
        )

    @staticmethod
    def resolve(
        *,
        row_profile,
        scale_ratio,
    ):
        if not isinstance(row_profile, dict):
            raise TypeError("row_profile must be a mapping")

        scale_ratio = float(scale_ratio)

        if scale_ratio <= 0.0:
            raise ValueError(
                "scale_ratio must be positive"
            )

        source_geometry = tuple(
            row_profile.get(
                "source_geometry",
                (),
            )
        )

        if row_profile.get("evidence_quality") != "strong":
            return {
                "source_id": row_profile.get("source_id"),
                "status": "skipped",
                "reason": "weak_evidence",
                "tree_count": 0,
                "resolved_spacing_mm": 0.0,
                "source_geometry": source_geometry,
            }

        product_spacing = row_profile.get(
            "product_spacing"
        )

        if not product_spacing:
            return {
                "source_id": row_profile.get("source_id"),
                "status": "skipped",
                "reason": "missing_spacing_evidence",
                "tree_count": 0,
                "resolved_spacing_mm": 0.0,
                "source_geometry": source_geometry,
            }

        action = product_spacing.get("action")

        if action == "omit":
            return {
                "source_id": row_profile.get("source_id"),
                "status": "skipped",
                "reason": "spacing_omitted",
                "tree_count": 0,
                "resolved_spacing_mm": 0.0,
                "source_geometry": source_geometry,
            }

        resolved_spacing_mm = float(
            product_spacing["resolved_spacing_mm"]
        )

        if resolved_spacing_mm <= 0.0:
            return {
                "source_id": row_profile.get("source_id"),
                "status": "skipped",
                "reason": "invalid_resolved_spacing",
                "tree_count": 0,
                "resolved_spacing_mm": 0.0,
                "source_geometry": source_geometry,
            }

        length_m = float(
            row_profile.get(
                "length_m",
                0.0,
            )
        )

        if length_m <= 0.0:
            return {
                "source_id": row_profile.get("source_id"),
                "status": "skipped",
                "reason": "invalid_length",
                "tree_count": 0,
                "resolved_spacing_mm": resolved_spacing_mm,
                "source_geometry": source_geometry,
            }

        length_mm = (
            length_m
            * 1000.0
            / scale_ratio
        )

        tree_count = max(
            2,
            int(
                math.floor(
                    length_mm
                    / resolved_spacing_mm
                )
            )
            + 1,
        )

        source_gaps = row_profile.get(
            "source_gaps"
        ) or {}

        gap_segment_indexes = tuple(
            sorted(
                set(
                    source_gaps.get(
                        "segment_indexes",
                        (),
                    )
                )
            )
        )

        if not gap_segment_indexes:
            placement_points = (
                AtlasTreeRowLayoutResolver
                ._interpolate_polyline(
                    source_geometry,
                    tree_count,
                )
            )

            member_source_segments = tuple(
                range(
                    max(
                        0,
                        len(source_geometry) - 1,
                    )
                )
            )

            return {
                "source_id": row_profile.get("source_id"),
                "status": "resolved",
                "reason": None,
                "tree_count": tree_count,
                "length_mm": length_mm,
                "resolved_spacing_mm": resolved_spacing_mm,
                "source_geometry": source_geometry,
                "placement_points": placement_points,
                "preserved_gap_segment_indexes": (),
                "member_source_segments": (
                    member_source_segments
                ),
            }

        segment_lengths_m = tuple(
            row_profile.get(
                "segment_lengths_m",
                (),
            )
        )

        geometry_segment_lengths = tuple(
            AtlasTreeRowLayoutResolver._distance(
                start,
                end,
            )
            for start, end in zip(
                source_geometry,
                source_geometry[1:],
            )
        )

        total_geometry_length = sum(
            geometry_segment_lengths
        )

        placement_points = []
        member_source_segments = []

        run_start = 0
        segment_count = len(source_geometry) - 1

        run_ranges = []

        for gap_index in gap_segment_indexes:
            if gap_index > run_start:
                run_ranges.append(
                    (
                        run_start,
                        gap_index - 1,
                    )
                )

            run_start = gap_index + 1

        if run_start < segment_count:
            run_ranges.append(
                (
                    run_start,
                    segment_count - 1,
                )
            )

        for first_segment, last_segment in run_ranges:
            run_geometry = source_geometry[
                first_segment:last_segment + 2
            ]

            if (
                len(segment_lengths_m)
                == segment_count
            ):
                run_length_m = sum(
                    segment_lengths_m[
                        first_segment:last_segment + 1
                    ]
                )
            else:
                run_geometry_length = sum(
                    geometry_segment_lengths[
                        first_segment:last_segment + 1
                    ]
                )

                run_length_m = (
                    0.0
                    if total_geometry_length <= 0.0
                    else (
                        length_m
                        * run_geometry_length
                        / total_geometry_length
                    )
                )

            if run_length_m <= 0.0:
                continue

            run_length_mm = (
                run_length_m
                * 1000.0
                / scale_ratio
            )

            run_tree_count = max(
                2,
                int(
                    math.floor(
                        run_length_mm
                        / resolved_spacing_mm
                    )
                )
                + 1,
            )

            (
                run_points,
                run_source_segments,
            ) = (
                AtlasTreeRowLayoutResolver
                ._interpolate_polyline_with_segments(
                    run_geometry,
                    run_tree_count,
                    source_segment_offset=first_segment,
                )
            )

            placement_points.extend(run_points)
            member_source_segments.extend(
                run_source_segments
            )

        return {
            "source_id": row_profile.get("source_id"),
            "status": "resolved",
            "reason": None,
            "tree_count": len(placement_points),
            "length_mm": length_mm,
            "resolved_spacing_mm": resolved_spacing_mm,
            "source_geometry": source_geometry,
            "placement_points": tuple(
                placement_points
            ),
            "preserved_gap_segment_indexes": (
                gap_segment_indexes
            ),
            "member_source_segments": tuple(
                member_source_segments
            ),
        }
