"""
ATLAS Castle Wall Physical State Classifier v0.1

Tarihsel kimlik ile güncel fiziksel varlığı ayırır.

Durumlar:
- CURRENT_PHYSICAL
- RUIN_OR_REMAINS
- HISTORICAL_ONLY
- UNCERTAIN
"""

import re


class AtlasCastleWallPhysicalStateClassifier:
    CURRENT_PHYSICAL = "CURRENT_PHYSICAL"
    RUIN_OR_REMAINS = "RUIN_OR_REMAINS"
    HISTORICAL_ONLY = "HISTORICAL_ONLY"
    UNCERTAIN = "UNCERTAIN"

    REMOVED_PREFIXES = {
        "demolished",
        "removed",
        "razed",
    }

    INACTIVE_PREFIXES = {
        "abandoned",
        "disused",
    }

    PHYSICAL_BARRIER_VALUES = {
        "wall",
        "city_wall",
        "retaining_wall",
    }

    RUIN_VALUES = {
        "yes",
        "ruins",
        "remains",
    }

    @staticmethod
    def classify(tags):
        tags = tags or {}

        height_data = (
            AtlasCastleWallPhysicalStateClassifier._parse_height(
                tags.get("height")
            )
        )

        if AtlasCastleWallPhysicalStateClassifier._is_removed(tags):
            return AtlasCastleWallPhysicalStateClassifier._result(
                state=(
                    AtlasCastleWallPhysicalStateClassifier.HISTORICAL_ONLY
                ),
                allow_full_wall=False,
                allow_low_remains=False,
                allow_crenellations=False,
                height_data=height_data,
                reason="removed_or_demolished",
            )

        if AtlasCastleWallPhysicalStateClassifier._is_relation_boundary_only(
            tags
        ):
            return AtlasCastleWallPhysicalStateClassifier._result(
                state=(
                    AtlasCastleWallPhysicalStateClassifier.HISTORICAL_ONLY
                ),
                allow_full_wall=False,
                allow_low_remains=False,
                allow_crenellations=False,
                height_data=height_data,
                reason="relation_boundary_without_wall_evidence",
            )

        if AtlasCastleWallPhysicalStateClassifier._is_ruin(tags):
            return AtlasCastleWallPhysicalStateClassifier._result(
                state=(
                    AtlasCastleWallPhysicalStateClassifier.RUIN_OR_REMAINS
                ),
                allow_full_wall=False,
                allow_low_remains=True,
                allow_crenellations=False,
                height_data=height_data,
                reason="ruin_or_remains_tags",
            )

        if AtlasCastleWallPhysicalStateClassifier._is_current_physical(tags):
            return AtlasCastleWallPhysicalStateClassifier._result(
                state=(
                    AtlasCastleWallPhysicalStateClassifier.CURRENT_PHYSICAL
                ),
                allow_full_wall=True,
                allow_low_remains=False,
                allow_crenellations=(
                    AtlasCastleWallPhysicalStateClassifier
                    ._supports_crenellations(tags)
                ),
                height_data=height_data,
                reason="current_physical_evidence",
            )

        if AtlasCastleWallPhysicalStateClassifier._is_historic_wall(tags):
            return AtlasCastleWallPhysicalStateClassifier._result(
                state=AtlasCastleWallPhysicalStateClassifier.UNCERTAIN,
                allow_full_wall=False,
                allow_low_remains=True,
                allow_crenellations=False,
                height_data=height_data,
                reason="historic_identity_without_physical_evidence",
            )

        if AtlasCastleWallPhysicalStateClassifier._is_inactive(tags):
            return AtlasCastleWallPhysicalStateClassifier._result(
                state=(
                    AtlasCastleWallPhysicalStateClassifier.RUIN_OR_REMAINS
                ),
                allow_full_wall=False,
                allow_low_remains=True,
                allow_crenellations=False,
                height_data=height_data,
                reason="abandoned_or_disused",
            )

        return AtlasCastleWallPhysicalStateClassifier._result(
            state=AtlasCastleWallPhysicalStateClassifier.UNCERTAIN,
            allow_full_wall=False,
            allow_low_remains=True,
            allow_crenellations=False,
            height_data=height_data,
            reason="insufficient_evidence",
        )

    @staticmethod
    def _result(
        state,
        allow_full_wall,
        allow_low_remains,
        allow_crenellations,
        height_data,
        reason,
    ):
        return {
            "state": state,
            "allow_full_wall": allow_full_wall,
            "allow_low_remains": allow_low_remains,
            "allow_crenellations": allow_crenellations,
            "height_min_m": height_data["height_min_m"],
            "height_max_m": height_data["height_max_m"],
            "height_representative_m": (
                height_data["height_representative_m"]
            ),
            "reason": reason,
        }

    @staticmethod
    def _is_removed(tags):
        for prefix in (
            AtlasCastleWallPhysicalStateClassifier.REMOVED_PREFIXES
        ):
            if AtlasCastleWallPhysicalStateClassifier._truthy(
                tags.get(prefix)
            ):
                return True

            for key in tags:
                if key.startswith(f"{prefix}:"):
                    return True

        return False

    @staticmethod
    def _is_inactive(tags):
        for prefix in (
            AtlasCastleWallPhysicalStateClassifier.INACTIVE_PREFIXES
        ):
            if AtlasCastleWallPhysicalStateClassifier._truthy(
                tags.get(prefix)
            ):
                return True

            for key in tags:
                if key.startswith(f"{prefix}:"):
                    return True

        return False

    @staticmethod
    def _is_ruin(tags):
        ruins = str(tags.get("ruins", "")).strip().lower()
        historic = str(tags.get("historic", "")).strip().lower()
        building = str(tags.get("building", "")).strip().lower()

        if ruins in AtlasCastleWallPhysicalStateClassifier.RUIN_VALUES:
            return True

        if historic in {"ruins", "archaeological_site"}:
            return True

        if building in {"ruins", "collapsed"}:
            return True

        for key in tags:
            if key.startswith("ruins:"):
                return True

        return False

    @staticmethod
    def _is_current_physical(tags):
        barrier = str(tags.get("barrier", "")).strip().lower()

        if (
            barrier
            in AtlasCastleWallPhysicalStateClassifier.PHYSICAL_BARRIER_VALUES
        ):
            return True

        if tags.get("wall"):
            return True

        if tags.get("height"):
            return True

        if tags.get("width"):
            return True

        if tags.get("man_made") in {"wall", "embankment"}:
            return True

        return False

    @staticmethod
    def _is_historic_wall(tags):
        historic = str(tags.get("historic", "")).strip().lower()

        return historic in {
            "castle_wall",
            "citywalls",
            "city_wall",
        }

    @staticmethod
    def _is_relation_boundary_only(tags):
        if tags.get("source") != "castle_relation":
            return False

        has_physical_evidence = (
            AtlasCastleWallPhysicalStateClassifier._is_current_physical(tags)
        )

        return not has_physical_evidence

    @staticmethod
    def _supports_crenellations(tags):
        barrier = str(tags.get("barrier", "")).strip().lower()
        historic = str(tags.get("historic", "")).strip().lower()

        return (
            barrier == "city_wall"
            or historic in {"castle_wall", "citywalls", "city_wall"}
        )

    @staticmethod
    def _parse_height(value):
        result = {
            "height_min_m": None,
            "height_max_m": None,
            "height_representative_m": None,
        }

        if value is None:
            return result

        text = str(value).strip().lower().replace(",", ".")

        numbers = [
            float(number)
            for number in re.findall(
                r"(?<!\d)(\d+(?:\.\d+)?)",
                text,
            )
        ]

        positive_numbers = [
            number
            for number in numbers
            if number > 0
        ]

        if not positive_numbers:
            return result

        height_min_m = min(positive_numbers)
        height_max_m = max(positive_numbers)

        result["height_min_m"] = height_min_m
        result["height_max_m"] = height_max_m
        result["height_representative_m"] = (
            height_min_m + height_max_m
        ) / 2.0

        return result

    @staticmethod
    def _truthy(value):
        if value is None:
            return False

        return str(value).strip().lower() not in {
            "",
            "no",
            "false",
            "0",
            "none",
        }
