class AtlasPlaceOfWorshipProfileResolver:
    EXPLICIT_BUILDING_PROFILES = {
        "church": (
            "church",
            "christian",
        ),
        "cathedral": (
            "cathedral",
            "christian",
        ),
        "mosque": (
            "mosque",
            "muslim",
        ),
        "synagogue": (
            "synagogue",
            "jewish",
        ),
    }

    @classmethod
    def resolve(cls, tags):
        tags = tags or {}

        building_type = str(
            tags.get("building", "")
        ).strip().lower()

        religion = str(
            tags.get("religion", "")
        ).strip().lower()

        explicit_decision = (
            cls.EXPLICIT_BUILDING_PROFILES.get(
                building_type
            )
        )

        if explicit_decision is not None:
            profile, expected_religion = (
                explicit_decision
            )

            if (
                not religion
                or religion == expected_religion
            ):
                return profile

            return "generic_place_of_worship"

        amenity = str(
            tags.get("amenity", "")
        ).strip().lower()

        if amenity != "place_of_worship":
            return None

        inferred_profiles = {
            "christian": "church",
            "muslim": "mosque",
            "jewish": "synagogue",
        }

        if building_type == "yes":
            inferred_profile = (
                inferred_profiles.get(
                    religion
                )
            )

            if inferred_profile is not None:
                return inferred_profile

        return "generic_place_of_worship"
