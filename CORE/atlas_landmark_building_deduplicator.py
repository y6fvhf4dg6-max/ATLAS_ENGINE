class AtlasLandmarkBuildingDeduplicator:
    BUILDING_OWNED_TOWER_TYPES = {
        "minaret",
        "bell_tower",
        "staircase",
        "office",
    }

    @classmethod
    def filter_landmarks(
        cls,
        *,
        landmarks,
        raw_buildings,
    ):
        detailed_parent_ids = {
            building.get("parent_building_id")
            for building in raw_buildings
            if (
                building.get("parent_building_id")
                is not None
                and (
                    building.get("tags", {})
                    or {}
                ).get("building:part") == "yes"
            )
        }

        return [
            landmark
            for landmark in landmarks
            if landmark.get("id") not in detailed_parent_ids
        ]

    @classmethod
    def filter_buildings(
        cls,
        *,
        raw_buildings,
        landmarks,
    ):
        landmark_ids = {
            landmark.get("id")
            for landmark in landmarks
        }

        filtered = []

        for building in raw_buildings:
            object_id = building.get("id")

            if object_id not in landmark_ids:
                filtered.append(building)
                continue

            tags = building.get("tags", {}) or {}
            tower_type = tags.get("tower:type")

            if tower_type in cls.BUILDING_OWNED_TOWER_TYPES:
                filtered.append(building)

        return filtered
