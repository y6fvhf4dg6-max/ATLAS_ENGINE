import pytest

from CORE.atlas_semantic_surface_texture_applier import (
    AtlasSemanticSurfaceTextureApplier,
)


def _closed_surface_mesh():
    bottom = [
        (0.0, 0.0, 1.0),
        (1.35, 0.0, 1.0),
        (1.35, 1.35, 1.0),
        (0.0, 1.35, 1.0),
    ]

    top = [
        (0.0, 0.0, 1.30),
        (1.35, 0.0, 1.30),
        (1.35, 1.35, 1.30),
        (0.0, 1.35, 1.30),
    ]

    walls = [
        (bottom[0], bottom[1], top[1], top[0]),
        (bottom[1], bottom[2], top[2], top[1]),
        (bottom[2], bottom[3], top[3], top[2]),
        (bottom[3], bottom[0], top[0], top[3]),
    ]

    triangles = [
        (top[0], top[1], top[2]),
        (top[0], top[2], top[3]),
        (bottom[2], bottom[1], bottom[0]),
        (bottom[3], bottom[2], bottom[0]),
        (bottom[0], bottom[1], top[1]),
        (bottom[0], top[1], top[0]),
        (bottom[1], bottom[2], top[2]),
        (bottom[1], top[2], top[1]),
        (bottom[2], bottom[3], top[3]),
        (bottom[2], top[3], top[2]),
        (bottom[3], bottom[0], top[0]),
        (bottom[3], top[0], top[3]),
    ]

    return {
        "type": "park_foundation",
        "surface_id": 123,
        "source": "osm",
        "bottom": bottom,
        "top": top,
        "walls": walls,
        "triangles": triangles,
    }


def test_applier_textures_only_top_contract():
    mesh = _closed_surface_mesh()

    result = AtlasSemanticSurfaceTextureApplier.apply(
        mesh=mesh,
        surface_role="plaza_ground",
    )

    assert result is not mesh
    assert result["bottom"] == mesh["bottom"]
    assert result["top"] != mesh["top"]

    original_top_z = [
        point[2]
        for point in mesh["top"]
    ]

    textured_top_z = [
        point[2]
        for point in result["top"]
    ]

    assert min(textured_top_z) >= min(original_top_z) - 0.14 - 1e-9
    assert max(textured_top_z) <= max(original_top_z) + 0.14 + 1e-9


def test_applier_keeps_wall_top_vertices_synchronized():
    mesh = _closed_surface_mesh()

    result = AtlasSemanticSurfaceTextureApplier.apply(
        mesh=mesh,
        surface_role="plaza_ground",
    )

    textured_top = set(result["top"])

    for wall in result["walls"]:
        assert wall[2] in textured_top
        assert wall[3] in textured_top


def test_applier_preserves_bottom_triangle_vertices():
    mesh = _closed_surface_mesh()

    result = AtlasSemanticSurfaceTextureApplier.apply(
        mesh=mesh,
        surface_role="plaza_ground",
    )

    original_bottom = set(mesh["bottom"])
    textured_vertices = {
        point
        for triangle in result["triangles"]
        for point in triangle
    }

    assert original_bottom.issubset(textured_vertices)


def test_applier_preserves_non_geometry_metadata():
    mesh = _closed_surface_mesh()

    result = AtlasSemanticSurfaceTextureApplier.apply(
        mesh=mesh,
        surface_role="plaza_ground",
    )

    assert result["type"] == "park_foundation"
    assert result["surface_id"] == 123
    assert result["source"] == "osm"


def test_applier_returns_copy_for_unsupported_role():
    mesh = _closed_surface_mesh()

    result = AtlasSemanticSurfaceTextureApplier.apply(
        mesh=mesh,
        surface_role="unknown_ground",
    )

    assert result == mesh
    assert result is not mesh


from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)
from CORE.atlas_park_foundation_builder import (
    AtlasParkFoundationBuilder,
)


class _TextureCoordinateEngine:
    @staticmethod
    def geometry_to_stl_mm(geometry):
        return list(geometry)


def _flat_texture_terrain(z=2.0):
    return {
        "top_points": [
            [
                (0.0, 0.0, z),
                (200.0, 0.0, z),
            ],
            [
                (0.0, 200.0, z),
                (200.0, 200.0, z),
            ],
        ],
        "metadata": {
            "size_x_mm": 200.0,
            "size_y_mm": 200.0,
            "size_mm": 200.0,
        },
        "triangles": [
            (
                (0.0, 0.0, z),
                (200.0, 0.0, z),
                (0.0, 200.0, z),
            ),
            (
                (200.0, 0.0, z),
                (200.0, 200.0, z),
                (0.0, 200.0, z),
            ),
        ],
    }


def test_real_park_foundation_remains_closed_and_manifold_after_paving_texture():
    park = {
        "id": 900,
        "geometry": [
            (20.0, 20.0),
            (21.35, 20.0),
            (21.35, 21.35),
            (20.0, 21.35),
        ],
        "park_type": "place:square",
    }

    mesh = AtlasParkFoundationBuilder._build_park_mesh(
        park=park,
        coordinate_engine=_TextureCoordinateEngine(),
        terrain_mesh=_flat_texture_terrain(),
    )

    textured = AtlasSemanticSurfaceTextureApplier.apply(
        mesh=mesh,
        surface_role="plaza_ground",
    )

    report = AtlasMeshValidator.report(textured)

    assert report["valid"] is True
    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_applier_never_reduces_existing_surface_thickness():
    mesh = _closed_surface_mesh()

    textured = AtlasSemanticSurfaceTextureApplier.apply(
        mesh=mesh,
        surface_role="plaza_ground",
    )

    for original_bottom, original_top, new_bottom, new_top in zip(
        mesh["bottom"],
        mesh["top"],
        textured["bottom"],
        textured["top"],
    ):
        original_thickness = (
            original_top[2] - original_bottom[2]
        )
        textured_thickness = (
            new_top[2] - new_bottom[2]
        )

        assert textured_thickness >= original_thickness - 1e-9


from CORE.atlas_lod_level_catalog import (
    LOD_0,
    LOD_1,
)


def test_applier_skips_semantic_texture_below_profile_lod():
    mesh = _closed_surface_mesh()

    result = AtlasSemanticSurfaceTextureApplier.apply(
        mesh=mesh,
        surface_role="plaza_ground",
        lod_level=LOD_0,
    )

    assert result == mesh
    assert "semantic_surface_texture" not in result


def test_applier_enables_semantic_texture_at_profile_lod():
    mesh = _closed_surface_mesh()

    result = AtlasSemanticSurfaceTextureApplier.apply(
        mesh=mesh,
        surface_role="plaza_ground",
        lod_level=LOD_1,
    )

    assert result["top"] != mesh["top"]
    assert (
        result["semantic_surface_texture"]["lod_min_level"]
        == 1
    )
    assert (
        result["semantic_surface_texture"]["applied_lod_level"]
        == 1
    )


def test_applier_rejects_invalid_lod_level():
    with pytest.raises(
        TypeError,
        match="lod_level",
    ):
        AtlasSemanticSurfaceTextureApplier.apply(
            mesh=_closed_surface_mesh(),
            surface_role="plaza_ground",
            lod_level=1,
        )
