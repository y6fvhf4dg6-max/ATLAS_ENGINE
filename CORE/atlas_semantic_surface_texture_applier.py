from copy import deepcopy

from CORE.atlas_lod_level_catalog import (
    AtlasLoDLevel,
)
from CORE.atlas_semantic_surface_texture_pattern import (
    AtlasSemanticSurfaceTexturePattern,
)
from CORE.atlas_semantic_surface_texture_resolver import (
    AtlasSemanticSurfaceTextureResolver,
)


class AtlasSemanticSurfaceTextureApplier:
    @classmethod
    def apply(
        cls,
        *,
        mesh,
        surface_role,
        lod_level=None,
    ):
        result = deepcopy(mesh)

        if (
            lod_level is not None
            and not isinstance(
                lod_level,
                AtlasLoDLevel,
            )
        ):
            raise TypeError(
                "lod_level must be an AtlasLoDLevel"
            )

        profile = (
            AtlasSemanticSurfaceTextureResolver.resolve(
                surface_role=surface_role,
            )
        )

        if profile is None:
            return result

        if (
            lod_level is not None
            and lod_level.level
            < profile["lod_min_level"]
        ):
            return result

        texture_language = profile[
            "texture_language"
        ]

        if (
            texture_language
            not in
            AtlasSemanticSurfaceTexturePattern
            .SUPPORTED_TEXTURE_LANGUAGES
        ):
            return result

        pattern = AtlasSemanticSurfaceTexturePattern(
            texture_language=texture_language,
            relief_depth_mm=profile[
                "relief_depth_mm"
            ],
            feature_pitch_mm=profile[
                "feature_pitch_mm"
            ],
        )

        original_top = tuple(
            tuple(point)
            for point in mesh.get("top", ())
        )

        if not original_top:
            return result

        textured_top = tuple(
            (
                float(x),
                float(y),
                float(z)
                + pattern.offset_at(x, y),
            )
            for x, y, z in original_top
        )

        top_mapping = {
            original: textured
            for original, textured in zip(
                original_top,
                textured_top,
            )
        }

        result["top"] = list(textured_top)

        result["walls"] = [
            tuple(
                top_mapping.get(
                    tuple(point),
                    tuple(point),
                )
                for point in wall
            )
            for wall in mesh.get("walls", ())
        ]

        result["triangles"] = [
            tuple(
                top_mapping.get(
                    tuple(point),
                    tuple(point),
                )
                for point in triangle
            )
            for triangle in mesh.get("triangles", ())
        ]

        result["semantic_surface_texture"] = {
            "surface_role": surface_role,
            "texture_language": texture_language,
            "relief_depth_mm": profile[
                "relief_depth_mm"
            ],
            "feature_pitch_mm": profile[
                "feature_pitch_mm"
            ],
            "lod_min_level": profile[
                "lod_min_level"
            ],
            "applied_lod_level": (
                None
                if lod_level is None
                else lod_level.level
            ),
        }

        return result
