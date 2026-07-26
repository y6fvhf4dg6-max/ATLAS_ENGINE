from CORE.atlas_bridge_builder import AtlasBridgeBuilder
from CORE.atlas_landmark_geometry_mesher import (
    AtlasLandmarkGeometryMesher,
)
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_lighthouse_builder import AtlasLighthouseBuilder
from CORE.atlas_tower_builder import AtlasTowerBuilder


class AtlasLandmarkMeshBuilder:
    _BUILDERS = {
        AtlasLandmarkType.BRIDGE: AtlasBridgeBuilder,
        AtlasLandmarkType.LIGHTHOUSE: AtlasLighthouseBuilder,
        AtlasLandmarkType.TOWER: AtlasTowerBuilder,
    }

    @classmethod
    def build(cls, landmark, *, terrain_mesh=None):
        builder = cls._BUILDERS.get(landmark.landmark_type)

        if builder is None:
            raise ValueError(
                f"Unsupported landmark type: {landmark.landmark_type}"
            )

        geometry = builder.build(landmark)
        mesh = AtlasLandmarkGeometryMesher.build(geometry)

        if terrain_mesh is None:
            return mesh

        mesh["triangles"] = [
            tuple(
                (
                    x,
                    y,
                    z + float(terrain_mesh.sample_height(x, y)),
                )
                for x, y, z in triangle
            )
            for triangle in mesh["triangles"]
        ]

        for key in ("bottom", "top"):
            if key in mesh:
                mesh[key] = tuple(
                    (
                        x,
                        y,
                        z + float(terrain_mesh.sample_height(x, y)),
                    )
                    for x, y, z in mesh[key]
                )

        if "rings" in mesh:
            mesh["rings"] = tuple(
                tuple(
                    (
                        x,
                        y,
                        z + float(terrain_mesh.sample_height(x, y)),
                    )
                    for x, y, z in ring
                )
                for ring in mesh["rings"]
            )

        return mesh
