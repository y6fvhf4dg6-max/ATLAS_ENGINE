"""
ATLAS Engine 2.0

Module : Engine Config
Version: 0.1
Status : Architecture Foundation

Purpose:
Central configuration for ATLAS product modes, finish options,
vertical scale and printability rules.
"""


PRODUCT_MODES = {
    "basic": {
        "name": "Basic",
        "vertical_scale": 1.15,
        "min_printable_height_mm": 1.2,
        "road_detail": "simple",
        "roof_detail": False,
        "memory_highlight": False,
    },

    "realistic": {
        "name": "Realistic",
        "vertical_scale": 1.30,
        "min_printable_height_mm": 1.4,
        "road_detail": "standard",
        "roof_detail": False,
        "memory_highlight": True,
    },

    "museum": {
        "name": "Museum",
        "vertical_scale": 1.45,
        "min_printable_height_mm": 1.6,
        "road_detail": "detailed",
        "roof_detail": True,
        "memory_highlight": True,
    },

    "ultra": {
        "name": "Ultra",
        "vertical_scale": 1.60,
        "min_printable_height_mm": 1.8,
        "road_detail": "maximum",
        "roof_detail": True,
        "memory_highlight": True,
    },
}


FINISH_OPTIONS = {
    "white": {
        "name": "Monochrome White",
        "colors": 1,
        "description": "Single color white model.",
    },

    "black": {
        "name": "Monochrome Black",
        "colors": 1,
        "description": "Single color black model.",
    },

    "dual": {
        "name": "Dual Color",
        "colors": 2,
        "description": "Two-color model, for example black city with white highlight.",
    },

    "full_color": {
        "name": "Full Color",
        "colors": 4,
        "description": "Multi-color print for roads, water, parks and buildings.",
    },

    "hand_painted": {
        "name": "Hand Painted",
        "colors": "manual",
        "description": "Premium post-processed painted finish.",
    },
}


DEFAULT_MODE = "realistic"
DEFAULT_FINISH = "white"


def get_mode_config(mode_name=DEFAULT_MODE):
    if mode_name not in PRODUCT_MODES:
        raise ValueError(f"Bilinmeyen ürün modu: {mode_name}")

    return PRODUCT_MODES[mode_name]


def get_finish_config(finish_name=DEFAULT_FINISH):
    if finish_name not in FINISH_OPTIONS:
        raise ValueError(f"Bilinmeyen finish seçeneği: {finish_name}")

    return FINISH_OPTIONS[finish_name]


def print_engine_config(mode_name=DEFAULT_MODE, finish_name=DEFAULT_FINISH):
    mode = get_mode_config(mode_name)
    finish = get_finish_config(finish_name)

    print()
    print("=" * 60)
    print("ATLAS ENGINE CONFIG v0.1")
    print("=" * 60)

    print("Mode   :", mode["name"])
    print("Finish :", finish["name"])
    print()

    print("Vertical Scale:", mode["vertical_scale"])
    print("Minimum Height:", mode["min_printable_height_mm"], "mm")
    print("Road Detail   :", mode["road_detail"])
    print("Roof Detail   :", mode["roof_detail"])
    print("Memory Highlight:", mode["memory_highlight"])
    print()

    print("Finish Colors:", finish["colors"])
    print("Description  :", finish["description"])

    print("=" * 60)


if __name__ == "__main__":
    print_engine_config()