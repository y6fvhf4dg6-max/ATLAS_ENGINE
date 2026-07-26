from dataclasses import dataclass
import math


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

        footprint = geometry
        span_m = AtlasBridgeBuilder.DEFAULT_SPAN_M

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

        return AtlasBridgeGeometry(
            footprint=footprint,
            height_m=height_m,
            landmark_kind="bridge",
            metadata={
                "bridge_span_m": span_m,
                "bridge_width_m": width_m,
                "bridge_deck_thickness_m": deck_thickness_m,
            },
        )
