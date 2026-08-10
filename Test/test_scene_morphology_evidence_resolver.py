import pytest

from CORE.atlas_scene_morphology_evidence_resolver import (
    AtlasSceneMorphologyEvidenceResolver,
)
from CORE.atlas_urban_block_resolver import (
    AtlasUrbanBlockProfile,
)


def test_scene_morphology_evidence_resolver_builds_normalized_evidence():
    result = AtlasSceneMorphologyEvidenceResolver.resolve(
        product_area_mm2=19600.0,
        building_footprint_area_mm2=7840.0,
        road_surface_area_mm2=3920.0,
        vegetation_area_mm2=4900.0,
        forest_area_mm2=1960.0,
        water_area_mm2=980.0,
        railway_count=2,
        terrain_relief_mm=12.0,
        terrain_reference_height_mm=60.0,
        landmark_count=4,
        building_count=40,
        block_profiles=(
            AtlasUrbanBlockProfile(
                block_id="block_1",
                member_element_ids=("building_1",),
                density_ratio=0.80,
            ),
            AtlasUrbanBlockProfile(
                block_id="block_2",
                member_element_ids=("building_2",),
                density_ratio=0.60,
            ),
        ),
    )

    assert result["building_density"] == pytest.approx(0.40)
    assert result["road_density"] == pytest.approx(0.20)
    assert result["vegetation_coverage"] == pytest.approx(0.25)
    assert result["forest_coverage"] == pytest.approx(0.10)
    assert result["water_coverage"] == pytest.approx(0.05)
    assert result["block_compactness"] == pytest.approx(0.70)
    assert result["railway_presence"] is True
    assert result["terrain_relief"] == pytest.approx(0.20)
    assert result["landmark_density"] == pytest.approx(0.10)


def test_scene_morphology_evidence_resolver_handles_empty_scene():
    result = AtlasSceneMorphologyEvidenceResolver.resolve(
        product_area_mm2=10000.0,
        building_footprint_area_mm2=0.0,
        road_surface_area_mm2=0.0,
        vegetation_area_mm2=0.0,
        forest_area_mm2=0.0,
        water_area_mm2=0.0,
        railway_count=0,
        terrain_relief_mm=0.0,
        terrain_reference_height_mm=1.0,
        landmark_count=0,
        building_count=0,
        block_profiles=(),
    )

    assert result == {
        "building_density": 0.0,
        "road_density": 0.0,
        "block_compactness": 0.0,
        "vegetation_coverage": 0.0,
        "forest_coverage": 0.0,
        "water_coverage": 0.0,
        "railway_presence": False,
        "terrain_relief": 0.0,
        "landmark_density": 0.0,
    }


def test_scene_morphology_evidence_resolver_rejects_invalid_product_area():
    with pytest.raises(
        ValueError,
        match="product_area_mm2",
    ):
        AtlasSceneMorphologyEvidenceResolver.resolve(
            product_area_mm2=0.0,
            building_footprint_area_mm2=0.0,
            road_surface_area_mm2=0.0,
            vegetation_area_mm2=0.0,
            forest_area_mm2=0.0,
            water_area_mm2=0.0,
            railway_count=0,
            terrain_relief_mm=0.0,
            terrain_reference_height_mm=1.0,
            landmark_count=0,
            building_count=0,
            block_profiles=(),
        )
