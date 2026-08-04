from CORE.atlas_bridge_builder import AtlasBridgeBuilder
from CORE.atlas_church_landmark_builder import (
    AtlasChurchLandmarkBuilder,
)
from CORE.atlas_church_landmark_mesher import (
    AtlasChurchLandmarkMesher,
)
from CORE.atlas_church_landmark_profile import (
    AtlasChurchLandmarkProfile,
)
from CORE.atlas_foundation_sampler import AtlasFoundationSampler
from CORE.atlas_foundation_surface_builder import (
    AtlasFoundationSurfaceBuilder,
)
from CORE.atlas_landmark_geometry_mesher import (
    AtlasLandmarkGeometryMesher,
)
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_worship_landmark_fallback_mesher import (
    AtlasWorshipLandmarkFallbackMesher,
)
from CORE.atlas_lighthouse_builder import AtlasLighthouseBuilder
from CORE.atlas_rock_cut_tomb_builder import AtlasRockCutTombBuilder
from CORE.atlas_tower_builder import AtlasTowerBuilder


class AtlasLandmarkMeshBuilder:
    _BUILDERS = {
        AtlasLandmarkType.BRIDGE: AtlasBridgeBuilder,
        AtlasLandmarkType.LIGHTHOUSE: AtlasLighthouseBuilder,
        AtlasLandmarkType.ROCK_CUT_TOMB: AtlasRockCutTombBuilder,
        AtlasLandmarkType.TOWER: AtlasTowerBuilder,
    }

    @classmethod
    def build(cls, landmark, *, terrain_mesh=None):
        foundation_footprint = None

        if landmark.landmark_type in {
            AtlasLandmarkType.CHURCH,
            AtlasLandmarkType.CATHEDRAL,
        }:
            landmark_class = (
                "cathedral"
                if landmark.landmark_type
                is AtlasLandmarkType.CATHEDRAL
                else "church"
            )

            profile = AtlasChurchLandmarkProfile(
                landmark_class=landmark_class,
                tower_count=(
                    2
                    if landmark_class == "cathedral"
                    else 1
                ),
            )

            geometry = AtlasChurchLandmarkBuilder.build(
                landmark=landmark,
                profile=profile,
            )
            mesh = AtlasChurchLandmarkMesher.build(
                geometry
            )
            foundation_footprint = geometry.footprint
        elif landmark.landmark_type in {
            AtlasLandmarkType.MOSQUE,
            AtlasLandmarkType.SYNAGOGUE,
        }:
            mesh = (
                AtlasWorshipLandmarkFallbackMesher.build(
                    landmark
                )
            )
            foundation_footprint = mesh["footprint"]
        else:
            builder = cls._BUILDERS.get(
                landmark.landmark_type
            )

            if builder is None:
                raise ValueError(
                    f"Unsupported landmark type: "
                    f"{landmark.landmark_type}"
                )

            geometry = builder.build(landmark)
            mesh = AtlasLandmarkGeometryMesher.build(
                geometry
            )
            foundation_footprint = geometry.footprint

        if terrain_mesh is None:
            return mesh

        if foundation_footprint is None:
            raise RuntimeError(
                "landmark builder did not resolve a foundation footprint"
            )

        foundation_z = cls._resolve_foundation_z(
            terrain_mesh=terrain_mesh,
            footprint=foundation_footprint,
        )

        mesh["triangles"] = [
            tuple(
                (
                    x,
                    y,
                    z + foundation_z,
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
                        z + foundation_z,
                    )
                    for x, y, z in mesh[key]
                )

        if "rings" in mesh:
            mesh["rings"] = tuple(
                tuple(
                    (
                        x,
                        y,
                        z + foundation_z,
                    )
                    for x, y, z in ring
                )
                for ring in mesh["rings"]
            )

        mesh["foundation_z"] = foundation_z

        return mesh

    @classmethod
    def _resolve_foundation_z(
        cls,
        *,
        terrain_mesh,
        footprint,
    ):
        footprint = tuple(
            (float(x), float(y))
            for x, y in footprint
        )

        if not footprint:
            return 0.0

        if isinstance(terrain_mesh, dict):
            xs = tuple(x for x, _ in footprint)
            ys = tuple(y for _, y in footprint)

            surface = AtlasFoundationSurfaceBuilder.build_surface(
                terrain_mesh=terrain_mesh,
                bounds={
                    "min_x": min(xs),
                    "max_x": max(xs),
                    "min_y": min(ys),
                    "max_y": max(ys),
                },
                footprint_points=footprint,
            )

            if surface is None:
                return 0.0

            return float(surface["foundation_z"])

        sample_height = getattr(
            terrain_mesh,
            "sample_height",
            None,
        )

        if callable(sample_height):
            center_x = (
                sum(x for x, _ in footprint)
                / len(footprint)
            )
            center_y = (
                sum(y for _, y in footprint)
                / len(footprint)
            )

            return float(
                sample_height(center_x, center_y)
            )

        raise TypeError(
            "terrain_mesh must provide sample_height(x, y) "
            "or be a foundation terrain slab dictionary"
        )

    @staticmethod
    def _sample_terrain_height(
        *,
        terrain_mesh,
        x,
        y,
    ):
        sample_height = getattr(
            terrain_mesh,
            "sample_height",
            None,
        )

        if callable(sample_height):
            return float(sample_height(x, y))

        if isinstance(terrain_mesh, dict):
            return float(
                AtlasFoundationSampler.terrain_z_at_xy(
                    terrain_mesh=terrain_mesh,
                    x=x,
                    y=y,
                )
            )

        raise TypeError(
            "terrain_mesh must provide sample_height(x, y) "
            "or be a foundation terrain slab dictionary"
        )
