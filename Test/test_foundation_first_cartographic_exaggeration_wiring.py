from pathlib import Path


def _source():
    return Path(
        "CORE/atlas_foundation_first_engine.py"
    ).read_text()


def test_generate_city_exposes_cartographic_exaggeration_context():
    source = _source()

    assert (
        "cartographic_nozzle_diameter_mm="
        in source
    )

    assert (
        "cartographic_lod_level="
        in source
    )


def test_generate_city_passes_cartographic_context_to_roads():
    source = _source()

    assert (
        "cartographic_product_size_mm=("
        in source
    )

    assert (
        "cartographic_nozzle_diameter_mm=("
        in source
    )

    assert (
        "cartographic_lod_level=("
        in source
    )


def test_generate_city_builds_narrow_waterway_meshes():
    source = _source()

    assert (
        "build_narrow_waterway_meshes("
        in source
    )

    assert (
        "narrow_waterway_meshes"
        in source
    )


def test_generate_city_includes_narrow_waterways_in_water_meshes():
    source = _source()

    assert (
        "*narrow_waterway_meshes"
        in source
    )


def test_generate_city_passes_cartographic_context_to_vegetation():
    source = _source()

    assert (
        "cartographic_product_size_mm=("
        in source
    )

    assert (
        "cartographic_lod_level=("
        in source
    )
