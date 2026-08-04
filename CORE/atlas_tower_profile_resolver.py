from CORE.atlas_master_landmark_catalog import (
    AtlasMasterLandmarkCatalog,
)


class AtlasTowerProfileResolver:
    @staticmethod
    def resolve(tags):
        tags = tags or {}

        catalog_entry = (
            AtlasMasterLandmarkCatalog.resolve(
                wikidata_id=tags.get("wikidata"),
            )
        )

        if (
            catalog_entry is not None
            and catalog_entry.landmark_family
            == "tower"
            and catalog_entry.profile_name
            is not None
        ):
            return catalog_entry.profile_name

        if tags.get("tower:type") == "observation":
            return "observation"

        if (
            tags.get("amenity") == "clock"
            and tags.get("man_made") == "tower"
        ):
            return "clock"

        return "generic"
