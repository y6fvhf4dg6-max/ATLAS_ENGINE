def classify_building(building_type):
    landmark_religious = [
        "cathedral",
        "church",
        "mosque",
        "synagogue",
        "temple",
        "chapel",
    ]

    landmark_civic = [
        "castle",
        "stadium",
        "train_station",
        "transportation",
        "public",
    ]

    commercial = [
        "office",
        "commercial",
        "retail",
        "hotel",
    ]

    residential = [
        "house",
        "apartments",
        "residential",
        "detached",
        "terrace",
    ]

    if building_type in landmark_religious:
        return "landmark_religious"

    if building_type in landmark_civic:
        return "landmark_civic"

    if building_type in commercial:
        return "building_commercial"

    if building_type in residential:
        return "building_residential"

    return "building_generic"


if __name__ == "__main__":
    test_types = [
        "cathedral",
        "church",
        "office",
        "apartments",
        "yes",
    ]

    for building_type in test_types:
        print(building_type, "→", classify_building(building_type))