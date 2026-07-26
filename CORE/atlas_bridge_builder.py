from dataclasses import dataclass


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

        height_m = AtlasBridgeBuilder._try_float(
            tags.get("height")
        )

        if height_m is None:
            height_m = AtlasBridgeBuilder.DEFAULT_HEIGHT_M

        return AtlasBridgeGeometry(
            footprint=tuple(landmark.geometry),
            height_m=height_m,
            landmark_kind="bridge",
            metadata={
                "bridge_span_m": AtlasBridgeBuilder.DEFAULT_SPAN_M,
                "bridge_width_m": AtlasBridgeBuilder.DEFAULT_WIDTH_M,
            },
        )
