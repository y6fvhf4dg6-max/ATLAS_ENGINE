"""
ATLAS Minaret Balcony Builder v0.1

Minare gövde meshine, önceden kapalı olarak üretilmiş
şerefe/balkon component meshlerini ekler.

Bu sınıf boolean union yapmaz.
Her kapalı component'i aynı sahne mesh sözlüğünde
ayrı kapalı triangle shell olarak korur.
"""


class AtlasMinaretBalconyBuilder:
    @staticmethod
    def attach(
        minaret_mesh,
        component_meshes,
    ):
        if not minaret_mesh:
            return minaret_mesh

        valid_components = []

        for component_mesh in component_meshes or []:
            triangles = component_mesh.get(
                "triangles",
                [],
            )

            if not triangles:
                continue

            valid_components.append(
                component_mesh
            )

        if not valid_components:
            return minaret_mesh

        balcony_triangles = []
        balcony_walls = []
        balcony_bottom = []
        balcony_top = []
        source_ids = []

        for component_mesh in valid_components:
            balcony_triangles.extend(
                component_mesh.get(
                    "triangles",
                    [],
                )
            )

            balcony_walls.extend(
                component_mesh.get(
                    "walls",
                    [],
                )
            )

            balcony_bottom.extend(
                component_mesh.get(
                    "bottom",
                    [],
                )
            )

            balcony_top.extend(
                component_mesh.get(
                    "top",
                    [],
                )
            )

            source_id = component_mesh.get(
                "source_id"
            )

            if source_id is not None:
                source_ids.append(source_id)

        minaret_mesh["triangles"] = [
            *minaret_mesh.get(
                "triangles",
                [],
            ),
            *balcony_triangles,
        ]

        minaret_mesh["walls"] = [
            *minaret_mesh.get(
                "walls",
                [],
            ),
            *balcony_walls,
        ]

        minaret_mesh["bottom"] = [
            *minaret_mesh.get(
                "bottom",
                [],
            ),
            *balcony_bottom,
        ]

        minaret_mesh["top"] = [
            *minaret_mesh.get(
                "top",
                [],
            ),
            *balcony_top,
        ]

        minaret_mesh[
            "minaret_balcony_triangles"
        ] = balcony_triangles

        minaret_mesh[
            "minaret_balcony_walls"
        ] = balcony_walls

        minaret_mesh[
            "minaret_balcony_bottom"
        ] = balcony_bottom

        minaret_mesh[
            "minaret_balcony_top"
        ] = balcony_top

        minaret_mesh[
            "minaret_balcony_component_meshes"
        ] = valid_components

        minaret_mesh[
            "minaret_balcony_source_ids"
        ] = source_ids

        minaret_mesh[
            "minaret_balcony_count"
        ] = len(valid_components)

        minaret_mesh[
            "minaret_balcony_applied"
        ] = True

        return minaret_mesh
