class AtlasTowerProfileResolver:
    @staticmethod
    def resolve(tags):
        tags = tags or {}

        if tags.get("wikidata") == "Q91274":
            return "galata"

        if tags.get("tower:type") == "observation":
            return "observation"

        if (
            tags.get("amenity") == "clock"
            and tags.get("man_made") == "tower"
        ):
            return "clock"

        return "generic"
