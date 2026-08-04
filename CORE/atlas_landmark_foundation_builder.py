from dataclasses import dataclass, replace


from CORE.atlas_bridge_builder import AtlasBridgeGeometry
from CORE.atlas_church_landmark_builder import (
    AtlasChurchLandmarkBuilder,
)
from CORE.atlas_church_landmark_mesher import (
    AtlasChurchLandmarkMesher,
)
from CORE.atlas_church_landmark_profile_resolver import (
    AtlasChurchLandmarkProfileResolver,
)
from CORE.atlas_bridge_longitudinal_profile import (
    AtlasBridgeLongitudinalProfile,
)
from CORE.atlas_bridge_road_approach_mesher import (
    AtlasBridgeRoadApproachMesher,
)
from CORE.atlas_bridge_road_approach_profile import (
    AtlasBridgeRoadApproachProfile,
)
from CORE.atlas_bridge_road_approach_resolver import (
    AtlasBridgeRoadApproachResolver,
)
from CORE.atlas_bridge_road_approach_target_resolver import (
    AtlasBridgeRoadApproachTargetResolver,
)
from CORE.atlas_galata_bridge_parapet_mesher import (
    AtlasGalataBridgeParapetMesher,
)
from CORE.atlas_galata_bridge_support_mesher import (
    AtlasGalataBridgeSupportMesher,
)
from CORE.atlas_galata_bridge_support_resolver import (
    AtlasGalataBridgeSupportResolver,
)
from CORE.atlas_landmark_geometry_mesher import (
    AtlasLandmarkGeometryMesher,
)
from CORE.atlas_landmark_mesh_builder import AtlasLandmarkMeshBuilder
from CORE.atlas_landmark_provider_osm import AtlasLandmarkProviderOsm
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_worship_landmark_fallback_mesher import (
    AtlasWorshipLandmarkFallbackMesher,
)


@dataclass(frozen=True, slots=True)
class AtlasWorshipFallbackScaledGeometry:
    footprint: tuple
    height_m: float


class AtlasLandmarkFoundationBuilder:
    MIN_PRINTABLE_BRIDGE_DECK_THICKNESS_MM = 0.80
    GALATA_SUPPORT_DECK_EMBED_MM = 0.15
    GALATA_ROAD_APPROACH_LENGTH_MM = 3.00
    GALATA_ROAD_TOP_Z_MM = 0.80

    @staticmethod
    def _scale_bridge_metadata(
        metadata,
        coordinate_engine,
    ):
        metadata = dict(metadata)

        scalar_height_keys = (
            "bridge_deck_thickness_m",
            "bridge_pier_width_m",
            "bridge_pier_depth_m",
            "bridge_pier_base_m",
            "bridge_pier_top_m",
            "bridge_pier_height_m",
            "bridge_shore_top_m",
        )

        for key in scalar_height_keys:
            if key in metadata:
                metadata[key] = (
                    coordinate_engine.height_to_stl_mm(
                        metadata[key]
                    )
                )

        if "bridge_deck_thickness_m" in metadata:
            metadata["bridge_deck_thickness_m"] = max(
                float(
                    metadata[
                        "bridge_deck_thickness_m"
                    ]
                ),
                AtlasLandmarkFoundationBuilder
                .MIN_PRINTABLE_BRIDGE_DECK_THICKNESS_MM,
            )

        if "bridge_pier_positions" in metadata:
            metadata["bridge_pier_positions"] = tuple(
                (
                    x * 1000.0 / coordinate_engine.xy_scale,
                    y * 1000.0 / coordinate_engine.xy_scale,
                )
                for x, y in metadata[
                    "bridge_pier_positions"
                ]
            )

        return metadata

    @classmethod
    def build_landmarks(
        cls,
        landmarks,
        coordinate_engine,
        terrain_mesh,
        road_meshes=(),
        debug=True,
    ):
        meshes = []
        skipped = 0

        for source in landmarks:
            mesh = cls._build_landmark_mesh(
                source=source,
                coordinate_engine=coordinate_engine,
                terrain_mesh=terrain_mesh,
                road_meshes=road_meshes,
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

    @staticmethod
    def _resolve_stl_footprint(
        *,
        source,
        coordinate_engine,
    ):
        geometry = tuple(source.get("geometry", ()))

        if len(geometry) >= 3:
            return tuple(
                coordinate_engine.geometry_to_stl_mm(geometry)
            )

        tags = source.get("tags", {}) or {}

        is_rock_cut_tomb_node = (
            source.get("geometry_type") == "node"
            and tags.get("historic") == "tomb"
            and tags.get("tomb") == "rock-cut"
        )

        if not is_rock_cut_tomb_node:
            return ()

        lat = float(source["lat"])
        lon = float(source["lon"])

        center = tuple(
            coordinate_engine.geometry_to_stl_mm(
                ((lat, lon),)
            )
        )[0]

        center_x, center_y = center
        half_width_mm = 4.0
        half_depth_mm = 1.0

        return (
            (
                center_x - half_width_mm,
                center_y - half_depth_mm,
            ),
            (
                center_x + half_width_mm,
                center_y - half_depth_mm,
            ),
            (
                center_x + half_width_mm,
                center_y + half_depth_mm,
            ),
            (
                center_x - half_width_mm,
                center_y + half_depth_mm,
            ),
        )

    @classmethod
    def _build_landmark_mesh(
        cls,
        source,
        coordinate_engine,
        terrain_mesh,
        road_meshes=(),
    ):
        geometry = tuple(source.get("geometry", ()))

        stl_footprint = cls._resolve_stl_footprint(
            source=source,
            coordinate_engine=coordinate_engine,
        )

        if len(stl_footprint) < 3:
            return None

        landmark = AtlasLandmarkProviderOsm.from_source(source)

        try:
            local_meter_geometry = tuple(
                coordinate_engine.latlon_to_local_meters(lat, lon)
                for lat, lon in geometry
            )

            metric_landmark = replace(
                landmark,
                geometry=local_meter_geometry,
            )

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

                profile = (
                    AtlasChurchLandmarkProfileResolver.resolve(
                        metric_landmark,
                        scale_ratio=coordinate_engine.xy_scale,
                    )
                )

                resolved_geometry = (
                    AtlasChurchLandmarkBuilder.build(
                        landmark=metric_landmark,
                        profile=profile,
                    )
                )

                scaled_height = (
                    coordinate_engine.height_to_stl_mm(
                        resolved_geometry.height_m
                    )
                )

                scaled_geometry = replace(
                    resolved_geometry,
                    footprint=stl_footprint,
                    height_m=scaled_height,
                )

                mesh = AtlasChurchLandmarkMesher.build(
                    scaled_geometry
                )
            elif landmark.landmark_type in {
                AtlasLandmarkType.MOSQUE,
                AtlasLandmarkType.SYNAGOGUE,
            }:
                metric_mesh = (
                    AtlasWorshipLandmarkFallbackMesher.build(
                        metric_landmark
                    )
                )

                scaled_height = (
                    coordinate_engine.height_to_stl_mm(
                        metric_mesh["height_m"]
                    )
                )

                bottom = tuple(
                    (
                        float(x),
                        float(y),
                        0.0,
                    )
                    for x, y in stl_footprint
                )
                top = tuple(
                    (
                        float(x),
                        float(y),
                        float(scaled_height),
                    )
                    for x, y in stl_footprint
                )

                scaled_landmark = replace(
                    landmark,
                    geometry=stl_footprint,
                )

                mesh = (
                    AtlasWorshipLandmarkFallbackMesher.build(
                        scaled_landmark
                    )
                )

                mesh["height_m"] = (
                    metric_mesh["height_m"]
                )
                mesh["height_mm"] = (
                    scaled_height
                )
                mesh["bottom"] = bottom
                mesh["top"] = top

                # Fallback mesher STL footprint üzerinde
                # çalıştığı için Z yüksekliğini yeniden ölçekle.
                rescaled_triangles = []

                for triangle in mesh["triangles"]:
                    rescaled_triangles.append(
                        tuple(
                            (
                                float(point[0]),
                                float(point[1]),
                                (
                                    float(point[2])
                                    * scaled_height
                                    / mesh["max_z"]
                                    if mesh["max_z"] > 0.0
                                    else 0.0
                                ),
                            )
                            for point in triangle
                        )
                    )

                mesh["triangles"] = (
                    rescaled_triangles
                )
                mesh["max_z"] = scaled_height
                mesh["top_z"] = scaled_height

                scaled_geometry = (
                    AtlasWorshipFallbackScaledGeometry(
                        footprint=tuple(stl_footprint),
                        height_m=scaled_height,
                    )
                )
                resolved_geometry = scaled_geometry
            else:
                builder = (
                    AtlasLandmarkMeshBuilder
                    ._BUILDERS.get(
                        landmark.landmark_type
                    )
                )

                if builder is None:
                    return None

                resolved_geometry = builder.build(
                    metric_landmark
                )

                scaled_height = (
                    coordinate_engine.height_to_stl_mm(
                        resolved_geometry.height_m
                    )
                )

                if isinstance(
                    resolved_geometry,
                    AtlasBridgeGeometry,
                ):
                    metadata = cls._scale_bridge_metadata(
                        metadata=resolved_geometry.metadata,
                        coordinate_engine=coordinate_engine,
                    )

                    scaled_geometry = replace(
                        resolved_geometry,
                        footprint=stl_footprint,
                        height_m=scaled_height,
                        metadata=metadata,
                    )
                else:
                    replace_arguments = {
                        "footprint": stl_footprint,
                        "height_m": scaled_height,
                    }

                    if hasattr(
                        resolved_geometry,
                        "roof_height_m",
                    ):
                        replace_arguments["roof_height_m"] = (
                            coordinate_engine.height_to_stl_mm(
                                resolved_geometry.roof_height_m
                            )
                        )

                    scaled_geometry = replace(
                        resolved_geometry,
                        **replace_arguments,
                    )

                mesh = AtlasLandmarkGeometryMesher.build(
                    scaled_geometry
                )

            foundation_z = (
                AtlasLandmarkMeshBuilder
                ._resolve_foundation_z(
                    terrain_mesh=terrain_mesh,
                    footprint=scaled_geometry.footprint,
                )
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

            if "deck_sections" in mesh:
                translated_sections = []

                for section in mesh["deck_sections"]:
                    translated = dict(section)

                    for key in ("bottom", "top"):
                        translated[key] = tuple(
                            (
                                x,
                                y,
                                z + foundation_z,
                            )
                            for x, y, z in section[key]
                        )

                    translated["walls"] = tuple(
                        tuple(
                            (
                                x,
                                y,
                                z + foundation_z,
                            )
                            for x, y, z in wall
                        )
                        for wall in section["walls"]
                    )

                    translated["triangles"] = tuple(
                        tuple(
                            (
                                x,
                                y,
                                z + foundation_z,
                            )
                            for x, y, z in triangle
                        )
                        for triangle in section[
                            "triangles"
                        ]
                    )

                    translated_sections.append(
                        translated
                    )

                mesh["deck_sections"] = tuple(
                    translated_sections
                )

            is_galata_bridge = (
                isinstance(
                    resolved_geometry,
                    AtlasBridgeGeometry,
                )
                and landmark.tags.get("wikidata")
                == "Q81523"
            )

            if (
                is_galata_bridge
                and mesh.get("bottom")
            ):
                frame = (
                    AtlasGalataBridgeSupportResolver
                    ._resolve_frame(
                        scaled_geometry.footprint
                    )
                )

                supports = (
                    AtlasGalataBridgeSupportResolver
                    .resolve(
                        footprint=(
                            scaled_geometry.footprint
                        )
                    )
                )

                deck_bottom_z = min(
                    point[2]
                    for point in mesh["bottom"]
                )

                profile = AtlasBridgeLongitudinalProfile(
                    shore_top_m=float(
                        metadata["bridge_shore_top_m"]
                    ),
                    center_top_m=float(
                        scaled_geometry.height_m
                    ),
                    approach_ratio=float(
                        metadata.get(
                            "bridge_approach_ratio",
                            0.20,
                        )
                    ),
                    deck_thickness_m=float(
                        metadata[
                            "bridge_deck_thickness_m"
                        ]
                    ),
                    full_span_convex=bool(
                        metadata.get(
                            "bridge_full_span_convex",
                            False,
                        )
                    ),
                )

                support_meshes = []

                for support in supports:
                    local_bottom_z = (
                        foundation_z
                        + profile.bottom_z_at(
                            support[
                                "longitudinal_position"
                            ]
                        )
                    )

                    support_meshes.extend(
                        AtlasGalataBridgeSupportMesher
                        .build(
                            supports=(support,),
                            axis=(
                                frame["axis_x"],
                                frame["axis_y"],
                            ),
                            base_z=foundation_z,
                            top_z=(
                                local_bottom_z
                                + cls.GALATA_SUPPORT_DECK_EMBED_MM
                            ),
                        )
                    )

                support_meshes = tuple(
                    support_meshes
                )

                mesh["supports"] = support_meshes

                mesh["triangles"].extend(
                    triangle
                    for support in support_meshes
                    for triangle in support[
                        "triangles"
                    ]
                )

                parapets = (
                    AtlasGalataBridgeParapetMesher
                    .build(
                        deck_top=mesh["top"],
                    )
                )

                mesh["parapets"] = parapets

                mesh["triangles"].extend(
                    triangle
                    for parapet in parapets
                    for triangle in parapet[
                        "triangles"
                    ]
                )

                road_approaches = []

                if road_meshes:
                    approach_specs = (
                        AtlasBridgeRoadApproachResolver
                        .resolve(
                            mesh["top"]
                        )
                    )

                    for approach_spec in approach_specs:
                        approach_target = (
                            AtlasBridgeRoadApproachTargetResolver
                            .resolve(
                                start_edge=approach_spec[
                                    "start_edge"
                                ],
                                outward_axis=approach_spec[
                                    "outward_axis"
                                ],
                                road_meshes=road_meshes,
                            )
                        )

                        approach_profile = (
                            AtlasBridgeRoadApproachProfile(
                                bridge_top_z=(
                                    approach_spec[
                                        "bridge_top_z"
                                    ]
                                ),
                                road_top_z=(
                                    approach_target[
                                        "road_top_z"
                                    ]
                                ),
                                length_mm=(
                                    approach_target[
                                        "length_mm"
                                    ]
                                ),
                                deck_thickness_mm=(
                                    cls
                                    .MIN_PRINTABLE_BRIDGE_DECK_THICKNESS_MM
                                ),
                            )
                        )

                        approach_mesh = (
                            AtlasBridgeRoadApproachMesher
                            .build(
                                start_edge=(
                                    approach_spec[
                                        "start_edge"
                                    ]
                                ),
                                outward_axis=(
                                    approach_spec[
                                        "outward_axis"
                                    ]
                                ),
                                target_edge=(
                                    approach_target[
                                        "target_edge"
                                    ]
                                ),
                                profile=approach_profile,
                            )
                        )

                        approach_mesh[
                            "start_edge"
                        ] = approach_spec[
                            "start_edge"
                        ]
                        approach_mesh[
                            "target_edge"
                        ] = approach_target[
                            "target_edge"
                        ]
                        approach_mesh[
                            "end_point_count"
                        ] = approach_spec[
                            "end_point_count"
                        ]
                        approach_mesh[
                            "source_distance_mm"
                        ] = approach_target[
                            "source_distance_mm"
                        ]
                        approach_mesh[
                            "road_mesh_index"
                        ] = approach_target[
                            "road_mesh_index"
                        ]

                        road_approaches.append(
                            approach_mesh
                        )

                road_approaches = tuple(
                    road_approaches
                )

                mesh["road_approaches"] = (
                    road_approaches
                )

                mesh["triangles"].extend(
                    triangle
                    for approach in road_approaches
                    for triangle in approach[
                        "triangles"
                    ]
                )

            mesh["foundation_z"] = foundation_z
        except (TypeError, ValueError, AttributeError):
            return None

        mesh["landmark_id"] = landmark.id
        mesh["source"] = landmark.source
        mesh["tags"] = dict(landmark.tags)
        mesh["placement_mode"] = "foundation_first"

        return mesh
