"""
ATLAS Engine 2.0
Module : Config
Version: 1.1
"""


def make_profile(name, model_size_mm, real_size_m):
    scale = round((real_size_m * 1000) / model_size_mm)

    return {
        "name": name,
        "model_size_mm": model_size_mm,
        "real_size_m": real_size_m,
        "scale": scale,
        "base_thickness_mm": 3,
        "terrain_height_mm": 18,
    }


PRODUCT_PROFILES = {
    "historic_20": make_profile(
        name="Historic Center 20", model_size_mm=200, real_size_m=300
    ),
    "detail_20": make_profile(
        name="City Detail 20", model_size_mm=200, real_size_m=500
    ),
    "signature_20": make_profile(
        name="Signature 20", model_size_mm=200, real_size_m=1000
    ),
    "premium_25": make_profile(name="Premium 25", model_size_mm=250, real_size_m=1000),
}


DEFAULT_PRODUCT = "historic_20"

# ============================================================
# ATLAS WORLD ACTIVE LOCATION
# ============================================================

ACTIVE_CONTINENT = "Europe"
ACTIVE_COUNTRY = "Turkey"
ACTIVE_CITY = "Ankara"
ACTIVE_ADDRESS = "Ankara, Turkey"


def print_active_product():
    product = PRODUCT_PROFILES[DEFAULT_PRODUCT]

    print("Aktif ürün:", product["name"])
    print("Model:", product["model_size_mm"], "mm x", product["model_size_mm"], "mm")
    print("Gerçek alan:", product["real_size_m"], "m x", product["real_size_m"], "m")
    print("Ölçek: 1:", product["scale"])
