from __future__ import annotations

from pathlib import Path


class AtlasDalyanReliefSemanticMasks:
    SHAPE = (99, 240)
    DEFAULT_MATERIAL = "rock"

    @classmethod
    def build(
        cls,
        *,
        project_root: Path,
    ) -> dict:
        root = Path(project_root)
        mask_directory = (
            root
            / "Data"
            / "RELIEF"
            / "dalyan_rock_tombs"
            / "MASKS"
        )

        return {
            "type": "dalyan_relief_semantic_masks",
            "shape": cls.SHAPE,
            "default_material": cls.DEFAULT_MATERIAL,
            "mask_paths": {
                "vegetation": (
                    mask_directory
                    / "vegetation_240x99.png"
                ),
                "tomb_facade": (
                    mask_directory
                    / "tomb_facade_240x99.png"
                ),
            },
        }
