"""
ATLAS Engine

Atlas Nature Engine v1.0
Creates simple nature objects for STL city models.
"""


class AtlasNatureEngine:
    @staticmethod
    def create_tree(x, y, trunk_height=4.0, crown_height=6.0):
        return {
            "type": "tree",
            "x": x,
            "y": y,
            "trunk_height": trunk_height,
            "crown_height": crown_height,
        }

    @staticmethod
    def create_shrub(x, y, height=2.0):
        return {
            "type": "shrub",
            "x": x,
            "y": y,
            "height": height,
        }

    @staticmethod
    def create_grass_area(points, height=0.4):
        return {
            "type": "grass",
            "points": points,
            "height": height,
        }
