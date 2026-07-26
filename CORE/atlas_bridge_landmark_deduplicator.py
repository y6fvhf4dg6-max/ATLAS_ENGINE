class AtlasBridgeLandmarkDeduplicator:
    @staticmethod
    def _is_bridge(landmark):
        tags = landmark.get("tags", {}) or {}
        return (
            tags.get("man_made") == "bridge"
            or tags.get("bridge") == "yes"
        )

    @staticmethod
    def _is_bridge_area(landmark):
        tags = landmark.get("tags", {}) or {}
        return tags.get("man_made") == "bridge"

    @staticmethod
    def _normalized_name(tags):
        name = tags.get("name")
        if not isinstance(name, str):
            return None

        normalized = " ".join(
            name.strip().casefold().split()
        )
        return normalized or None

    @classmethod
    def _identity_key(cls, landmark):
        tags = landmark.get("tags", {}) or {}

        wikidata = tags.get("wikidata")
        if isinstance(wikidata, str):
            wikidata = wikidata.strip()
            if wikidata:
                return ("wikidata", wikidata.casefold())

        name = cls._normalized_name(tags)
        if name is not None:
            return ("name", name)

        return None

    @classmethod
    def filter_landmarks(cls, landmarks):
        landmarks = list(landmarks)

        preferred_bridge_ids = {}
        bridge_groups = {}

        for index, landmark in enumerate(landmarks):
            if not cls._is_bridge(landmark):
                continue

            identity = cls._identity_key(landmark)
            if identity is None:
                continue

            bridge_groups.setdefault(identity, []).append(
                (index, landmark)
            )

        for identity, entries in bridge_groups.items():
            area_entries = [
                (index, landmark)
                for index, landmark in entries
                if cls._is_bridge_area(landmark)
            ]

            if not area_entries:
                continue

            preferred_bridge_ids[identity] = id(
                area_entries[0][1]
            )

        filtered = []

        for landmark in landmarks:
            if not cls._is_bridge(landmark):
                filtered.append(landmark)
                continue

            identity = cls._identity_key(landmark)
            preferred_object_id = preferred_bridge_ids.get(
                identity
            )

            if preferred_object_id is None:
                filtered.append(landmark)
                continue

            if id(landmark) == preferred_object_id:
                filtered.append(landmark)

        return filtered
