from pathlib import Path

from CORE.atlas_dalyan_relief_semantic_masks import (
    AtlasDalyanReliefSemanticMasks,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_defines_dalyan_mask_contract() -> None:
    result = AtlasDalyanReliefSemanticMasks.build(
        project_root=PROJECT_ROOT
    )

    assert result["type"] == "dalyan_relief_semantic_masks"
    assert result["shape"] == (99, 240)
    assert result["default_material"] == "rock"
    assert result["mask_paths"] == {
        "vegetation": (
            PROJECT_ROOT
            / "Data"
            / "RELIEF"
            / "dalyan_rock_tombs"
            / "MASKS"
            / "vegetation_240x99.png"
        ),
        "tomb_facade": (
            PROJECT_ROOT
            / "Data"
            / "RELIEF"
            / "dalyan_rock_tombs"
            / "MASKS"
            / "tomb_facade_240x99.png"
        ),
    }
