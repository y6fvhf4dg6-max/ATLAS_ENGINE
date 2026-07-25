class AtlasLandmarkHeightResolver:
    DEFAULT_FLOOR_HEIGHT_M = 3.5

    @staticmethod
    def _try_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def resolve(
        cls,
        tags,
        *,
        default_height_m,
        floor_height_m=None,
    ):
        tags = tags or {}

        height_m = cls._try_float(tags.get("height"))
        if height_m is not None:
            return height_m

        levels = cls._try_float(tags.get("building:levels"))
        if levels is not None:
            resolved_floor_height = (
                cls.DEFAULT_FLOOR_HEIGHT_M
                if floor_height_m is None
                else float(floor_height_m)
            )
            return levels * resolved_floor_height

        min_height_m = cls._try_float(tags.get("min_height"))
        if min_height_m is not None:
            return min_height_m

        return float(default_height_m)
