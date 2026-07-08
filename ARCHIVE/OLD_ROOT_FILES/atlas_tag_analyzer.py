"""
ATLAS Engine 2.0

Module : Tag Analyzer
Version: 1.0

Purpose:
Analyze OSM tags and detect landmark / important structures.
"""


LANDMARK_RULES = {
    "building": {
        "cathedral": 100,
        "church": 90,
        "mosque": 95,
        "synagogue": 90,
        "chapel": 75,
        "monastery": 85,
        "castle": 95,
        "palace": 95,
        "museum": 80,
        "townhall": 85,
        "university": 75,
        "stadium": 80,
    },
    "amenity": {
        "place_of_worship": 90,
        "townhall": 85,
        "theatre": 75,
        "university": 75,
        "hospital": 70,
    },
    "historic": {
        "yes": 75,
        "building": 80,
        "castle": 95,
        "monument": 90,
        "memorial": 80,
        "archaeological_site": 85,
    },
    "tourism": {
        "museum": 80,
        "attraction": 75,
        "artwork": 70,
    },
    "religion": {
        "christian": 25,
        "muslim": 25,
        "jewish": 25,
    },
}


def get_landmark_score(tags):
    score = 0

    if not tags:
        return 0

    for key, value_scores in LANDMARK_RULES.items():
        value = tags.get(key)

        if value in value_scores:
            score += value_scores[value]

    if tags.get("name"):
        score += 10

    if tags.get("wikidata"):
        score += 15

    if tags.get("wikipedia"):
        score += 15

    return min(score, 100)


def is_landmark(tags):
    return get_landmark_score(tags) >= 70


def landmark_category(tags):
    if not is_landmark(tags):
        return "normal"

    if tags.get("building") in ["cathedral", "church", "chapel"]:
        return "christian_religious"

    if tags.get("building") == "mosque":
        return "mosque"

    if tags.get("building") in ["castle", "palace"]:
        return "historic_power"

    if tags.get("tourism") == "museum" or tags.get("building") == "museum":
        return "museum"

    if tags.get("amenity") == "townhall" or tags.get("building") == "townhall":
        return "civic"

    return "landmark"


def describe_tags(tags):
    return {
        "name": tags.get("name"),
        "building": tags.get("building"),
        "amenity": tags.get("amenity"),
        "historic": tags.get("historic"),
        "tourism": tags.get("tourism"),
        "religion": tags.get("religion"),
        "landmark_score": get_landmark_score(tags),
        "landmark": is_landmark(tags),
        "category": landmark_category(tags),
    }


def main():
    test_tags = {
        "building": "cathedral",
        "amenity": "place_of_worship",
        "religion": "christian",
        "name": "Fulda Cathedral",
        "wikidata": "Q123",
    }

    print("=" * 60)
    print("ATLAS TAG ANALYZER v1.0")
    print("=" * 60)
    print(describe_tags(test_tags))
    print("=" * 60)


if __name__ == "__main__":
    main()