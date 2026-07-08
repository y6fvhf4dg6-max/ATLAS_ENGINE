"""
ATLAS Engine

Atlas Object Policy v1.0
Decides how analyzed buildings should be handled.
"""


class AtlasObjectPolicy:
    @staticmethod
    def decide(analysis, mode="city"):
        category = analysis.get("category")
        area = analysis.get("area_m2", 0)
        ratio = analysis.get("aspect_ratio", 0)
        score = analysis.get("print_score", 0)
        btype = analysis.get("type")

        if mode == "technical":
            return "keep"

        if mode == "landmark":
            return "keep"

        if mode == "city":
            if score < 30:
                return "skip"

            if category == "too_small":
                return "skip"

            if category == "too_long" and area < 300:
                return "skip"

            if area > 8000 and btype not in ("office", "commercial"):
                return "simplify"

            return "keep"

        if mode == "gift":
            if score < 50:
                return "skip"

            if category in ("too_small", "too_long"):
                return "skip"

            if area > 5000:
                return "simplify"

            return "keep"

        return "keep"
