"""
============================================================
ATLAS ENGINE
Data Manager
Version : 1.0
============================================================
"""

from DATA_CONNECTORS.Microsoft.microsoft_connector import MicrosoftConnector
from DATA_CONNECTORS.Overture.overture_connector import OvertureConnector
from DATA_CONNECTORS.OpenBuildingMap.openbuilding_connector import OpenBuildingConnector
from DATA_CONNECTORS.OSM.osm_connector import OSMConnector


class AtlasDataManager:

    def __init__(self):
        self.providers = {}

        self.provider_priority = {
            "OSM": 100,
            "Microsoft": 90,
            "Overture": 80,
            "OpenBuildingMap": 70,
        }

        self.provider_quality = {
            "OSM": 0.90,
            "Microsoft": 0.85,
            "Overture": 0.80,
            "OpenBuildingMap": 0.70,
        }

    def register_default_providers(self):
        self.providers["OSM"] = OSMConnector()
        self.providers["Microsoft"] = MicrosoftConnector()
        self.providers["Overture"] = OvertureConnector()
        self.providers["OpenBuildingMap"] = OpenBuildingConnector()

    def get_provider_names(self):
        return list(self.providers.keys())

    def is_provider_available(self, provider_name):
        if provider_name == "OSM":
            return True

        provider = self.providers.get(provider_name)

        if provider is None:
            return False

        if hasattr(provider, "is_available"):
            return provider.is_available()

        return True

    def get_provider_info(self, provider_name):
        provider = self.providers.get(provider_name)

        if provider is None:
            return None

        if hasattr(provider, "provider_info"):
            return provider.provider_info()

        return None

    def get_provider_score(self, provider_name):
        info = self.get_provider_info(provider_name)

        if info is None:
            return 0

        if not info.get("available", False):
            return 0

        priority = info.get("priority", 0)
        quality = info.get("quality", 0)

        return priority * quality

    def create_candidate_from_report(self, provider_name, report):
        return {
            "count": report["building_ways"],
            "has_height": report["height_count"] > 0,
            "has_roof": report["roof_count"] > 0,
            "footprint_quality": 1.0 if report["building_ways"] > 0 else 0.0,
            "freshness": 0.90,
        }

    def select_best_building_source(self, candidates):
        best_provider = None
        best_score = -1
        score_details = {}

        for provider_name, data in candidates.items():
            if not self.is_provider_available(provider_name):
                continue

            base_score = self.get_provider_score(provider_name)

            building_count = data.get("count", 0)
            has_height = data.get("has_height", False)
            has_roof = data.get("has_roof", False)
            footprint_quality = data.get("footprint_quality", 0.5)
            freshness = data.get("freshness", 0.5)

            score = base_score
            score += building_count * 0.05

            if has_height:
                score += 10

            if has_roof:
                score += 8

            score += footprint_quality * 20
            score += freshness * 10

            score_details[provider_name] = {
                "base_score": round(base_score, 2),
                "building_count": building_count,
                "has_height": has_height,
                "has_roof": has_roof,
                "footprint_quality": footprint_quality,
                "freshness": freshness,
                "final_score": round(score, 2),
            }

            if score > best_score:
                best_score = score
                best_provider = provider_name

        return {
            "provider": best_provider,
            "score": round(best_score, 2),
            "details": score_details,
        }

    def status(self):
        print("=" * 60)
        print("ATLAS DATA MANAGER v1.0")
        print("=" * 60)
        print()
        print("Provider scores:")

        for provider_name in ["OSM"] + self.get_provider_names():
            print(
                "-",
                provider_name,
                "| available:",
                self.is_provider_available(provider_name),
                "| priority:",
                self.provider_priority.get(provider_name),
                "| quality:",
                self.provider_quality.get(provider_name),
                "| score:",
                self.get_provider_score(provider_name),
            )


def main():
    manager = AtlasDataManager()
    manager.register_default_providers()
    manager.status()

    print()
    print("Best source test:")

    candidates = {
        "OSM": {
            "count": 90,
            "has_height": True,
            "has_roof": True,
            "footprint_quality": 0.75,
            "freshness": 0.80,
        },
        "Microsoft": {
            "count": 140,
            "has_height": False,
            "has_roof": False,
            "footprint_quality": 0.95,
            "freshness": 0.90,
        },
        "Overture": {
            "count": 120,
            "has_height": True,
            "has_roof": True,
            "footprint_quality": 0.85,
            "freshness": 0.85,
        },
        "OpenBuildingMap": {
            "count": 60,
            "has_height": True,
            "has_roof": False,
            "footprint_quality": 0.80,
            "freshness": 0.70,
        },
    }

    result = manager.select_best_building_source(candidates)

    print()
    print("=" * 60)
    print("ATLAS BUILDING SOURCE REPORT")
    print("=" * 60)

    for provider, info in result["details"].items():
        print()
        print(provider)
        print("-" * len(provider))
        print(f"Base Score        : {info['base_score']}")
        print(f"Buildings         : {info['building_count']}")
        print(f"Height            : {info['has_height']}")
        print(f"Roof              : {info['has_roof']}")
        print(f"Footprint Quality : {info['footprint_quality']}")
        print(f"Freshness         : {info['freshness']}")
        print(f"Final Score       : {info['final_score']}")

    print()
    print("=" * 60)
    print("BEST PROVIDER")
    print("=" * 60)
    print(result["provider"])
    print(f"Score : {result['score']}")


if __name__ == "__main__":
    main()
