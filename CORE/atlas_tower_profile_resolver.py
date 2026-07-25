class AtlasTowerProfileResolver:
    @staticmethod
    def resolve(tags):
        tags = tags or {}

        if tags.get("tower:type") == "observation":
            return "observation"

        return "generic"
