import math
import statistics

from CORE.atlas_tree_row_spacing_resolver import (
    AtlasTreeRowSpacingResolver,
)


class AtlasTreeRowResolver:
    @staticmethod
    def resolve(
        source,
        *,
        scale_ratio=None,
        nozzle_diameter_mm=None,
    ):
        if not isinstance(source, dict):
            raise TypeError("source must be a mapping")

        if source.get("tree_type") != "tree_row":
            raise ValueError(
                "source tree_type must be tree_row"
            )

        geometry = AtlasTreeRowResolver._normalize_geometry(
            source.get("geometry")
        )

        if len(geometry) < 2:
            raise ValueError(
                "tree_row geometry must contain at least two points"
            )

        segment_lengths = []

        for start, end in zip(
            geometry,
            geometry[1:],
        ):
            segment_lengths.append(
                AtlasTreeRowResolver._distance_meters(
                    start,
                    end,
                )
            )

        first = geometry[0]
        last = geometry[-1]

        east_m, north_m = (
            AtlasTreeRowResolver._local_vector_meters(
                first,
                last,
            )
        )

        minimum_m = min(segment_lengths)
        maximum_m = max(segment_lengths)
        mean_m = (
            sum(segment_lengths)
            / len(segment_lengths)
        )

        regularity_ratio = (
            1.0
            if maximum_m <= 0.0
            else minimum_m / maximum_m
        )

        direction_consistency_ratio = (
            AtlasTreeRowResolver
            ._direction_consistency_ratio(
                geometry
            )
        )

        median_segment_length_m = statistics.median(
            segment_lengths
        )

        gap_threshold_m = (
            median_segment_length_m * 2.5
        )

        gap_segment_indexes = tuple(
            index
            for index, length_m in enumerate(
                segment_lengths
            )
            if (
                median_segment_length_m > 0.0
                and length_m > gap_threshold_m
            )
        )

        gap_lengths_m = tuple(
            segment_lengths[index]
            for index in gap_segment_indexes
        )

        evidence_quality = (
            "strong"
            if (
                len(segment_lengths) >= 1
                and direction_consistency_ratio >= 0.90
            )
            else "weak"
        )

        product_spacing = None
        explicit_spacing_m = source.get("tree_spacing_m")

        if explicit_spacing_m is not None:
            if scale_ratio is None or nozzle_diameter_mm is None:
                raise ValueError(
                    "scale_ratio and nozzle_diameter_mm are required "
                    "for explicit tree spacing resolution"
                )

            spacing_result = AtlasTreeRowSpacingResolver.resolve(
                source_spacing_m=explicit_spacing_m,
                scale_ratio=scale_ratio,
                nozzle_diameter_mm=nozzle_diameter_mm,
            )

            product_spacing = {
                **spacing_result,
                "evidence_source": "explicit_tree_spacing",
            }

        elif (
            evidence_quality == "strong"
            and scale_ratio is not None
            and nozzle_diameter_mm is not None
        ):
            product_spacing = (
                AtlasTreeRowSpacingResolver
                .resolve_fallback(
                    nozzle_diameter_mm=nozzle_diameter_mm,
                )
            )

        return {
            "source_id": source.get("id"),
            "semantic_role": "tree_row",
            "representation_mode": "ordered_row",
            "source_geometry": tuple(geometry),
            "segment_count": len(segment_lengths),
            "segment_lengths_m": tuple(segment_lengths),
            "length_m": sum(segment_lengths),
            "source_segment_spacing": {
                "count": len(segment_lengths),
                "minimum_m": minimum_m,
                "maximum_m": maximum_m,
                "mean_m": mean_m,
                "regularity_ratio": regularity_ratio,
            },
            "direction_consistency_ratio": (
                direction_consistency_ratio
            ),
            "source_gaps": {
                "count": len(gap_segment_indexes),
                "segment_indexes": gap_segment_indexes,
                "maximum_gap_m": (
                    max(gap_lengths_m)
                    if gap_lengths_m
                    else 0.0
                ),
                "median_segment_length_m": (
                    median_segment_length_m
                ),
                "threshold_m": gap_threshold_m,
            },
            "evidence_quality": evidence_quality,
            "product_spacing": product_spacing,
            "direction": {
                "east_m": east_m,
                "north_m": north_m,
            },
        }

    @staticmethod
    def _normalize_geometry(geometry):
        points = []

        for point in geometry or ():
            if not isinstance(point, (tuple, list)):
                continue

            if len(point) < 2:
                continue

            try:
                lat = float(point[0])
                lon = float(point[1])
            except (TypeError, ValueError):
                continue

            if not (
                math.isfinite(lat)
                and math.isfinite(lon)
            ):
                continue

            points.append((lat, lon))

        return points

    @staticmethod
    def _local_vector_meters(start, end):
        lat1, lon1 = start
        lat2, lon2 = end

        mean_lat = math.radians(
            (lat1 + lat2) / 2.0
        )

        meters_per_degree_lat = 111_320.0
        meters_per_degree_lon = (
            111_320.0 * math.cos(mean_lat)
        )

        east_m = (
            (lon2 - lon1)
            * meters_per_degree_lon
        )
        north_m = (
            (lat2 - lat1)
            * meters_per_degree_lat
        )

        return east_m, north_m

    @staticmethod
    def _direction_consistency_ratio(geometry):
        start = geometry[0]
        end = geometry[-1]

        main_east, main_north = (
            AtlasTreeRowResolver
            ._local_vector_meters(
                start,
                end,
            )
        )

        main_length = math.hypot(
            main_east,
            main_north,
        )

        if main_length <= 0.0:
            return 0.0

        similarities = []

        for segment_start, segment_end in zip(
            geometry,
            geometry[1:],
        ):
            east_m, north_m = (
                AtlasTreeRowResolver
                ._local_vector_meters(
                    segment_start,
                    segment_end,
                )
            )

            segment_length = math.hypot(
                east_m,
                north_m,
            )

            if segment_length <= 0.0:
                continue

            cosine = (
                east_m * main_east
                + north_m * main_north
            ) / (
                segment_length
                * main_length
            )

            similarities.append(
                max(-1.0, min(1.0, cosine))
            )

        if not similarities:
            return 0.0

        return sum(similarities) / len(similarities)

    @staticmethod
    def _distance_meters(start, end):
        east_m, north_m = (
            AtlasTreeRowResolver._local_vector_meters(
                start,
                end,
            )
        )

        return math.hypot(
            east_m,
            north_m,
        )
