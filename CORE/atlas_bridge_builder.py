from dataclasses import dataclass
import math

from CORE.atlas_master_landmark_catalog import (
    AtlasMasterLandmarkCatalog,
)


@dataclass(frozen=True, slots=True)
class AtlasBridgeGeometry:
    footprint: tuple
    height_m: float
    landmark_kind: str
    metadata: dict


class AtlasBridgeBuilder:
    """OSM bridge geometrisini köprü sözleşmesine dönüştürür."""

    DEFAULT_WIDTH_M = 10.0
    DEFAULT_SPAN_M = 50.0
    DEFAULT_HEIGHT_M = 8.0
    DEFAULT_DECK_THICKNESS_M = 1.0
    DEFAULT_PIER_WIDTH_M = 2.0
    DEFAULT_PIER_DEPTH_M = 1.0

    @staticmethod
    def _try_float(value):
        try:
            if isinstance(value, str):
                value = value.replace("m", "").strip()
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def build(landmark) -> AtlasBridgeGeometry:
        tags = getattr(landmark, "tags", {}) or {}
        geometry = tuple(landmark.geometry)

        height_m = AtlasBridgeBuilder._try_float(
            tags.get("height")
        )
        if height_m is None:
            height_m = AtlasBridgeBuilder.DEFAULT_HEIGHT_M

        width_m = AtlasBridgeBuilder._try_float(
            tags.get("width")
        )
        if width_m is None:
            width_m = AtlasBridgeBuilder.DEFAULT_WIDTH_M

        deck_thickness_m = AtlasBridgeBuilder._try_float(
            tags.get("bridge:deck_thickness")
        )
        if deck_thickness_m is None:
            deck_thickness_m = AtlasBridgeBuilder.DEFAULT_DECK_THICKNESS_M

        pier_width_m = AtlasBridgeBuilder._try_float(
            tags.get("bridge:pier_width")
        )
        if pier_width_m is None or pier_width_m <= 0.0:
            pier_width_m = AtlasBridgeBuilder.DEFAULT_PIER_WIDTH_M

        pier_depth_m = AtlasBridgeBuilder._try_float(
            tags.get("bridge:pier_depth")
        )
        if pier_depth_m is None or pier_depth_m <= 0.0:
            pier_depth_m = AtlasBridgeBuilder.DEFAULT_PIER_DEPTH_M

        pier_base_m = 0.0
        pier_top_m = max(0.0, height_m - deck_thickness_m)
        pier_height_m = max(0.0, pier_top_m - pier_base_m)

        catalog_entry = (
            AtlasMasterLandmarkCatalog.resolve(
                wikidata_id=tags.get("wikidata"),
                osm_id=getattr(
                    landmark,
                    "id",
                    None,
                ),
            )
        )

        is_galata_bridge = (
            catalog_entry is not None
            and catalog_entry.landmark_family
            == "bridge"
            and catalog_entry.profile_name
            == "galata"
        )

        approach_profile = False
        segmented_deck = False
        full_span_convex = is_galata_bridge
        shore_top_m = 6.0 if is_galata_bridge else height_m
        approach_ratio = 0.20

        footprint = geometry
        span_m = AtlasBridgeBuilder.DEFAULT_SPAN_M
        pier_count = 0
        pier_positions = ()

        pier_count_value = AtlasBridgeBuilder._try_float(
            tags.get("bridge:pier_count")
        )
        if (
            pier_count_value is not None
            and pier_count_value >= 1
            and pier_count_value.is_integer()
        ):
            pier_count = int(pier_count_value)

        if len(geometry) == 2:
            (x1, y1), (x2, y2) = geometry
            dx = float(x2) - float(x1)
            dy = float(y2) - float(y1)
            span_m = math.hypot(dx, dy)

            if span_m > 0.0:
                half_width = width_m / 2.0
                offset_x = -dy / span_m * half_width
                offset_y = dx / span_m * half_width

                footprint = (
                    (float(x1) - offset_x, float(y1) - offset_y),
                    (float(x2) - offset_x, float(y2) - offset_y),
                    (float(x2) + offset_x, float(y2) + offset_y),
                    (float(x1) + offset_x, float(y1) + offset_y),
                )

                if pier_count > 0:
                    pier_positions = tuple(
                        (
                            float(x1) + dx * index / (pier_count + 1),
                            float(y1) + dy * index / (pier_count + 1),
                        )
                        for index in range(1, pier_count + 1)
                    )

        return AtlasBridgeGeometry(
            footprint=footprint,
            height_m=height_m,
            landmark_kind="bridge",
            metadata={
                "bridge_span_m": span_m,
                "bridge_width_m": width_m,
                "bridge_deck_thickness_m": deck_thickness_m,
                "bridge_pier_count": pier_count,
                "bridge_pier_positions": pier_positions,
                "bridge_pier_width_m": pier_width_m,
                "bridge_pier_depth_m": pier_depth_m,
                "bridge_pier_base_m": pier_base_m,
                "bridge_pier_top_m": pier_top_m,
                "bridge_pier_height_m": pier_height_m,
                "bridge_approach_profile": approach_profile,
                "bridge_segmented_deck": segmented_deck,
                "bridge_full_span_convex": full_span_convex,
                "bridge_shore_top_m": shore_top_m,
                "bridge_approach_ratio": approach_ratio,
            },
        )
