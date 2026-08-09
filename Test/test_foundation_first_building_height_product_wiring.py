from pathlib import Path


def test_generate_city_resolves_building_height_product_context():
    source = Path(
        "CORE/atlas_foundation_first_engine.py"
    ).read_text()

    assert (
        "_resolve_building_height_product_context("
        in source
    )

    assert (
        "building_height_product_context"
        in source
    )


def test_generate_city_passes_height_context_into_scene_builder():
    source = Path(
        "CORE/atlas_foundation_first_engine.py"
    ).read_text()

    assert (
        "building_height_context_by_source_id=("
        in source
    )

    assert (
        "building_height_product_context"
        in source
    )


def test_generate_city_exposes_building_minimum_readable_height():
    source = Path(
        "CORE/atlas_foundation_first_engine.py"
    ).read_text()

    assert (
        "building_minimum_readable_height_mm="
        in source
    )

    assert (
        "building_minimum_readable_height_mm=("
        in source
    )
