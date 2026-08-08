class AtlasTreeRowMemberProducer:
    @staticmethod
    def build(layout):
        if not isinstance(layout, dict):
            raise TypeError("layout must be a mapping")

        if layout.get("status") != "resolved":
            return []

        source_id = layout.get("source_id")
        points = tuple(
            layout.get(
                "placement_points",
                (),
            )
        )

        result = []

        for index, point in enumerate(points):
            lat, lon = point

            result.append(
                {
                    "id": (
                        f"tree_row_{source_id}_{index}"
                    ),
                    "lat": float(lat),
                    "lon": float(lon),
                    "tree_type": "tree",
                    "tree_kind": "park_tree_symbol",
                    "tags": {
                        "source": "osm_tree_row",
                        "source_tree_row_id": source_id,
                        "tree_row_index": index,
                    },
                }
            )

        return result
