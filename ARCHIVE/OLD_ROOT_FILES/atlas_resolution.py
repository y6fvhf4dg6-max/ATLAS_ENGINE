def get_resolution_profile(quality):
    profiles = {
        "draft": {
            "grid_size": 16,
            "model_size": 100,
            "base_thickness": 3,
            "terrain_height": 18,
        },
        "standard": {
            "grid_size": 64,
            "model_size": 100,
            "base_thickness": 3,
            "terrain_height": 18,
        },
        "premium": {
            "grid_size": 128,
            "model_size": 100,
            "base_thickness": 3,
            "terrain_height": 18,
        },
        "ultra": {
            "grid_size": 256,
            "model_size": 100,
            "base_thickness": 3,
            "terrain_height": 18,
        },
    }

    if quality not in profiles:
        raise ValueError("Geçersiz kalite seviyesi.")

    return profiles[quality]


if __name__ == "__main__":
    profile = get_resolution_profile("draft")
    print(profile)