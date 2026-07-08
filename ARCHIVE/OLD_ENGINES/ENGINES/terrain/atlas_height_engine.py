"""
ATLAS Engine

Module : Height Engine
Version: 0.2
Status : Development

Purpose:
Calculates real-world building height from OpenStreetMap tags,
converts it into model height in millimeters,
then applies ATLAS visual optimization rules.

Principles:
- XY scale stays geographically accurate.
- Z scale is configurable through ATLAS Vertical Scale.
- Very small heights can be increased for printability.
"""


DEFAULT_HEIGHT_M = 10.0
LEVEL_HEIGHT_M = 3.0

VERTICAL_SCALE = 1.35
MIN_PRINTABLE_HEIGHT_MM = 1.5
MAX_REASONABLE_HEIGHT_MM = 60.0


BUILDING_TYPE_HEIGHTS_M = {
    "garage": 3.0,
    "garages": 3.0,
    "shed": 3.0,
    "hut": 3.0,

    "house": 7.0,
    "detached": 7.0,
    "residential": 10.0,
    "apartments": 15.0,

    "commercial": 15.0,
    "retail": 12.0,
    "office": 20.0,
    "industrial": 12.0,
    "warehouse": 10.0,

    "church": 25.0,
    "cathedral": 45.0,
    "mosque": 25.0,
    "synagogue": 20.0,

    "school": 12.0,
    "hospital": 18.0,
    "government": 18.0,
    "public": 15.0,

    "yes": DEFAULT_HEIGHT_M,
}


def clean_number(value):
    if value is None:
        return None

    text = str(value).lower()
    text = text.replace("meters", "")
    text = text.replace("metres", "")
    text = text.replace("meter", "")
    text = text.replace("metre", "")
    text = text.replace("m", "")
    text = text.replace(",", ".")
    text = text.strip()

    try:
        return float(text)
    except ValueError:
        return None


def get_real_height_m(tags):
    if "height" in tags:
        height = clean_number(tags["height"])
        if height and height > 0:
            return height

    if "building:height" in tags:
        height = clean_number(tags["building:height"])
        if height and height > 0:
            return height

    if "building:levels" in tags:
        levels = clean_number(tags["building:levels"])
        if levels and levels > 0:
            return levels * LEVEL_HEIGHT_M

    building_type = tags.get("building", "yes")

    return BUILDING_TYPE_HEIGHTS_M.get(
        building_type,
        DEFAULT_HEIGHT_M
    )


def real_height_to_model_mm(real_height_m, real_size_m, model_size_mm):
    scale = model_size_mm / real_size_m
    return real_height_m * scale


def optimize_model_height_mm(model_height_mm):
    optimized_height = model_height_mm * VERTICAL_SCALE

    if optimized_height < MIN_PRINTABLE_HEIGHT_MM:
        optimized_height = MIN_PRINTABLE_HEIGHT_MM

    if optimized_height > MAX_REASONABLE_HEIGHT_MM:
        optimized_height = MAX_REASONABLE_HEIGHT_MM

    return optimized_height


def get_final_model_height_mm(tags, real_size_m, model_size_mm):
    real_height_m = get_real_height_m(tags)

    raw_model_height_mm = real_height_to_model_mm(
        real_height_m,
        real_size_m,
        model_size_mm
    )

    final_model_height_mm = optimize_model_height_mm(
        raw_model_height_mm
    )

    return {
        "real_height_m": real_height_m,
        "raw_model_height_mm": raw_model_height_mm,
        "final_model_height_mm": final_model_height_mm,
        "vertical_scale": VERTICAL_SCALE,
        "min_printable_height_mm": MIN_PRINTABLE_HEIGHT_MM,
    }


if __name__ == "__main__":
    samples = [
        {"building": "house"},
        {"building": "apartments", "building:levels": "6"},
        {"building": "office", "height": "28"},
        {"building": "church"},
        {"building": "garage"},
        {"building": "yes"},
    ]

    for tags in samples:
        result = get_final_model_height_mm(
            tags,
            real_size_m=1000,
            model_size_mm=200
        )

        print("--------------------------------")
        print("Tags:", tags)
        print("Gerçek yükseklik:", result["real_height_m"], "m")
        print("Ham model yüksekliği:", round(result["raw_model_height_mm"], 2), "mm")
        print("Final model yüksekliği:", round(result["final_model_height_mm"], 2), "mm")
        print("Vertical Scale:", result["vertical_scale"])
        print("Minimum:", result["min_printable_height_mm"], "mm")