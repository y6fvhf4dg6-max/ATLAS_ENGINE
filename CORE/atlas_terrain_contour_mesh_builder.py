class AtlasTerrainContourMeshBuilder:

    @staticmethod
    def build(contour_bands):
        triangles = []

        for band in contour_bands:
            if len(band) < 4:
                continue

            p0 = band[0]
            p1 = band[1]
            p2 = band[2]
            p3 = band[3]

            triangles.append((p0, p1, p2))
            triangles.append((p0, p2, p3))

        return triangles
