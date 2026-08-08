from CORE.atlas_park_foundation_builder import (
    AtlasParkFoundationBuilder,
)


class AtlasForestCanopyFoundationBuilder:
    @staticmethod
    def build(
        *,
        surfaces,
        coordinate_engine,
        terrain_mesh,
        debug=True,
    ):
        meshes = []

        for surface in surfaces or ():
            base_mesh = AtlasParkFoundationBuilder._build_park_mesh(
                park=surface,
                coordinate_engine=coordinate_engine,
                terrain_mesh=terrain_mesh,
            )

            if base_mesh is None:
                continue

            meshes.append(
                {
                    **base_mesh,
                    "type": "forest_canopy_foundation",
                    "semantic_role": "forest_canopy",
                    "surface_id": surface.get("id"),
                    "source": surface.get("source"),
                    "cell_count": surface.get("cell_count"),
                }
            )

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS FOREST CANOPY FOUNDATION BUILDER REPORT")
            print("=" * 60)
            print(f"Input surfaces    : {len(surfaces or ())}")
            print(f"Canopy meshes     : {len(meshes)}")
            print("=" * 60)
            print("")

        return meshes
