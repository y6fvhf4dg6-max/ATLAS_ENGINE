from dataclasses import replace

from CORE.atlas_landmark_mesh_builder import AtlasLandmarkMeshBuilder
from CORE.atlas_landmark_provider_osm import AtlasLandmarkProviderOsm


class AtlasLandmarkFoundationBuilder:
    @classmethod
    def build_landmarks(
        cls,
        landmarks,
        coordinate_engine,
        terrain_mesh,
        debug=True,
    ):
        meshes = []
        skipped = 0

        for source in landmarks:
            mesh = cls._build_landmark_mesh(
                source=source,
                coordinate_engine=coordinate_engine,
                terrain_mesh=terrain_mesh,
            )

            if mesh is None:
                skipped += 1
                continue

            meshes.append(mesh)

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS LANDMARK FOUNDATION BUILDER REPORT")
            print("=" * 60)
            print(f"Input landmarks : {len(landmarks)}")
            print(f"Accepted        : {len(meshes)}")
            print(f"Skipped         : {skipped}")
            print(f"Landmark meshes : {len(meshes)}")
            print("=" * 60)
            print("")

        return meshes

    @classmethod
    def _build_landmark_mesh(
        cls,
        source,
        coordinate_engine,
        terrain_mesh,
    ):
        geometry = tuple(source.get("geometry", ()))

        if len(geometry) < 3:
            return None

        landmark = AtlasLandmarkProviderOsm.from_source(source)

        try:
            local_meter_geometry = tuple(
                coordinate_engine.latlon_to_local_meters(lat, lon)
                for lat, lon in geometry
            )

            builder = AtlasLandmarkMeshBuilder._BUILDERS.get(
                landmark.landmark_type
            )

            if builder is None:
                return None

            metric_landmark = replace(
                landmark,
                geometry=local_meter_geometry,
            )

            resolved_geometry = builder.build(metric_landmark)

            stl_footprint = tuple(
                coordinate_engine.geometry_to_stl_mm(geometry)
            )

            scaled_geometry = replace(
                resolved_geometry,
                footprint=stl_footprint,
                height_m=coordinate_engine.height_to_stl_mm(
                    resolved_geometry.height_m
                ),
            )

            mesh = AtlasLandmarkMeshBuilder.build(
                replace(
                    landmark,
                    geometry=scaled_geometry.footprint,
                    tags={
                        **dict(landmark.tags),
                        "height": str(scaled_geometry.height_m),
                    },
                ),
                terrain_mesh=terrain_mesh,
            )
        except (TypeError, ValueError, AttributeError):
            return None

        mesh["landmark_id"] = landmark.id
        mesh["source"] = landmark.source
        mesh["tags"] = dict(landmark.tags)
        mesh["placement_mode"] = "foundation_first"

        return mesh
