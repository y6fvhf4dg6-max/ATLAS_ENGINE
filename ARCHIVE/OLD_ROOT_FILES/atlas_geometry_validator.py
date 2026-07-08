"""
============================================================
ATLAS GEOMETRY VALIDATOR
Version : 1.0
Purpose : Validate source geometries before mesh generation
============================================================
"""

from shapely.geometry import LineString, Polygon
from shapely.validation import explain_validity


class AtlasGeometryValidator:

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_line(self, line, name="Line"):
        error_count_before = len(self.errors)
        if line is None:
            self.errors.append(f"{name}: Geometry is None")
            return False

        if line.is_empty:
            self.errors.append(f"{name}: Empty geometry")

        if not line.is_valid:
            self.errors.append(
                f"{name}: Invalid geometry ({explain_validity(line)})"
            )

        if line.length == 0:
            self.errors.append(f"{name}: Zero length")

        coords = list(line.coords)

        for i in range(len(coords) - 1):

            if coords[i] == coords[i + 1]:
                self.errors.append(
                    f"{name}: Duplicate vertex at segment {i}"
                )

        return len(self.errors) == error_count_before

    def validate_polygon(self, polygon, name="Polygon"):
        error_count_before = len(self.errors)
        if polygon is None:
            self.errors.append(f"{name}: Polygon is None")
            return False

        if polygon.is_empty:
            self.errors.append(f"{name}: Empty polygon")

        if not polygon.is_valid:
            self.errors.append(
                f"{name}: Invalid polygon ({explain_validity(polygon)})"
            )

        if polygon.area == 0:
            self.errors.append(f"{name}: Zero area polygon")

        return len(self.errors) == error_count_before

    def report(self):

        print()
        print("=" * 60)
        print("ATLAS GEOMETRY VALIDATOR")
        print("=" * 60)

        print("Errors  :", len(self.errors))
        print("Warnings:", len(self.warnings))

        if self.errors:

            print()
            print("ERROR LIST")

            for item in self.errors:
                print("-", item)

        if self.warnings:

            print()
            print("WARNING LIST")

            for item in self.warnings:
                print("-", item)

        if not self.errors:
            print()
            print("Geometry OK")