# CORE/atlas_artwork_foundation_builder.py

import math

from CORE.atlas_foundation_sampler import AtlasFoundationSampler
from CORE.atlas_mesh_validator import AtlasMeshValidator


class AtlasArtworkFoundationBuilder:
    """
    ATLAS Artwork Foundation Builder v0.2

    Görev:
    - OSM artwork node'larını terrain üzerine yerleştirmek.
    - Küçük fakat yazdırılabilir kapalı hacimler üretmek.
    - Bina alan filtresinden bağımsız çalışmak.
    - Hayvan heykellerini en yakın aynı profilli komşu eksenine yöneltmek.
    """

    PROFILE_DIMENSIONS_MM = {
        "animal_statue": {
            "width_mm": 0.90,
            "depth_mm": 1.40,
            "height_mm": 1.00,
        },
        "generic_statue": {
            "width_mm": 0.90,
            "depth_mm": 0.90,
            "height_mm": 1.40,
        },
    }

    @staticmethod
    def build_artworks(
        artworks,
        coordinate_engine,
        terrain_mesh,
        debug=True,
    ):
        prepared = (
            AtlasArtworkFoundationBuilder
            ._prepare_artworks(
                artworks=artworks,
                coordinate_engine=coordinate_engine,
            )
        )

        meshes = []
        accepted = 0
        skipped = 0

        for item in prepared:
            mesh = (
                AtlasArtworkFoundationBuilder
                ._build_artwork_mesh(
                    prepared=item,
                    terrain_mesh=terrain_mesh,
                )
            )

            if mesh is None:
                skipped += 1
                continue

            meshes.append(mesh)
            accepted += 1

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS ARTWORK FOUNDATION BUILDER REPORT")
            print("=" * 60)
            print(f"Input artworks   : {len(artworks)}")
            print(f"Accepted         : {accepted}")
            print(f"Skipped          : {skipped}")
            print(f"Artwork meshes   : {len(meshes)}")
            print(
                "Triangles        : "
                f"{AtlasArtworkFoundationBuilder._count_triangles(meshes)}"
            )
            print("=" * 60)
            print("")

        return meshes

    @staticmethod
    def _prepare_artworks(
        artworks,
        coordinate_engine,
    ):
        prepared = []

        for artwork in artworks:
            lat = artwork.get("lat")
            lon = artwork.get("lon")

            if lat is None or lon is None:
                continue

            try:
                x, y = coordinate_engine.point_to_stl_mm(
                    lat,
                    lon,
                )
            except AttributeError:
                x, y = coordinate_engine.geometry_to_stl_mm(
                    [(lat, lon)]
                )[0]

            profile = (
                AtlasArtworkFoundationBuilder
                ._classify_profile(artwork)
            )

            prepared.append(
                {
                    "source": artwork,
                    "source_id": artwork.get("id"),
                    "profile": profile,
                    "x": float(x),
                    "y": float(y),
                    "orientation_degrees": 0.0,
                }
            )

        for item in prepared:
            if item["profile"] != "animal_statue":
                continue

            candidates = [
                candidate
                for candidate in prepared
                if (
                    candidate is not item
                    and candidate["profile"] == item["profile"]
                )
            ]

            if not candidates:
                continue

            nearest = min(
                candidates,
                key=lambda candidate: (
                    (candidate["x"] - item["x"]) ** 2
                    + (candidate["y"] - item["y"]) ** 2
                ),
            )

            delta_x = nearest["x"] - item["x"]
            delta_y = nearest["y"] - item["y"]

            orientation_degrees = math.degrees(
                math.atan2(
                    delta_y,
                    delta_x,
                )
            )

            item["orientation_degrees"] = (
                AtlasArtworkFoundationBuilder
                ._normalize_axis_angle(
                    orientation_degrees
                )
            )

        return prepared

    @staticmethod
    def _build_artwork_mesh(
        prepared,
        terrain_mesh,
    ):
        x = prepared["x"]
        y = prepared["y"]
        profile = prepared["profile"]
        orientation_degrees = prepared[
            "orientation_degrees"
        ]

        dimensions = (
            AtlasArtworkFoundationBuilder
            .PROFILE_DIMENSIONS_MM[profile]
        )

        width_mm = dimensions["width_mm"]
        depth_mm = dimensions["depth_mm"]
        height_mm = dimensions["height_mm"]

        bottom_z = AtlasFoundationSampler.terrain_z_at_xy(
            terrain_mesh=terrain_mesh,
            x=x,
            y=y,
        )

        top_z = bottom_z + height_mm

        footprint = (
            AtlasArtworkFoundationBuilder
            ._rotated_rectangle(
                center_x=x,
                center_y=y,
                width_mm=width_mm,
                depth_mm=depth_mm,
                orientation_degrees=orientation_degrees,
            )
        )

        bottom = [
            (
                point_x,
                point_y,
                bottom_z,
            )
            for point_x, point_y in footprint
        ]

        top = [
            (
                point_x,
                point_y,
                top_z,
            )
            for point_x, point_y in footprint
        ]

        triangles = [
            (bottom[2], bottom[1], bottom[0]),
            (bottom[3], bottom[2], bottom[0]),
            (top[0], top[1], top[2]),
            (top[0], top[2], top[3]),
            (bottom[0], bottom[1], top[1]),
            (bottom[0], top[1], top[0]),
            (bottom[1], bottom[2], top[2]),
            (bottom[1], top[2], top[1]),
            (bottom[2], bottom[3], top[3]),
            (bottom[2], top[3], top[2]),
            (bottom[3], bottom[0], top[0]),
            (bottom[3], top[0], top[3]),
        ]

        walls = [
            (bottom[0], bottom[1], top[1], top[0]),
            (bottom[1], bottom[2], top[2], top[1]),
            (bottom[2], bottom[3], top[3], top[2]),
            (bottom[3], bottom[0], top[0], top[3]),
        ]

        mesh = {
            "type": "artwork_foundation",
            "source_id": prepared["source_id"],
            "profile": profile,
            "orientation_degrees": orientation_degrees,
            "width_mm": width_mm,
            "depth_mm": depth_mm,
            "height_mm": height_mm,
            "bottom_z": bottom_z,
            "top_z": top_z,
            "bottom": bottom,
            "top": top,
            "walls": walls,
            "triangles": triangles,
            "placement_mode": "foundation_first",
        }

        report = AtlasMeshValidator.report(mesh)

        if not report["valid"]:
            return None

        return mesh

    @staticmethod
    def _rotated_rectangle(
        center_x,
        center_y,
        width_mm,
        depth_mm,
        orientation_degrees,
    ):
        angle_radians = math.radians(
            orientation_degrees
        )

        forward_x = math.cos(angle_radians)
        forward_y = math.sin(angle_radians)

        side_x = -forward_y
        side_y = forward_x

        half_depth = depth_mm * 0.5
        half_width = width_mm * 0.5

        return [
            (
                center_x
                - forward_x * half_depth
                - side_x * half_width,
                center_y
                - forward_y * half_depth
                - side_y * half_width,
            ),
            (
                center_x
                + forward_x * half_depth
                - side_x * half_width,
                center_y
                + forward_y * half_depth
                - side_y * half_width,
            ),
            (
                center_x
                + forward_x * half_depth
                + side_x * half_width,
                center_y
                + forward_y * half_depth
                + side_y * half_width,
            ),
            (
                center_x
                - forward_x * half_depth
                + side_x * half_width,
                center_y
                - forward_y * half_depth
                + side_y * half_width,
            ),
        ]

    @staticmethod
    def _normalize_axis_angle(angle_degrees):
        while angle_degrees >= 90.0:
            angle_degrees -= 180.0

        while angle_degrees < -90.0:
            angle_degrees += 180.0

        return angle_degrees

    @staticmethod
    def _classify_profile(artwork):
        if artwork.get("statue_type") == "animal":
            return "animal_statue"

        return "generic_statue"

    @staticmethod
    def _count_triangles(meshes):
        return sum(
            len(mesh.get("triangles", []))
            for mesh in meshes
            if isinstance(mesh, dict)
        )
