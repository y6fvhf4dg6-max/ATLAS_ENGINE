from CORE.atlas_foundation_first_engine import AtlasFoundationFirstEngine


def test_foundation_first_terrain_base_has_production_safe_minimum_thickness():
    assert AtlasFoundationFirstEngine.BASE_PLATE_HEIGHT_MM >= 1.60
