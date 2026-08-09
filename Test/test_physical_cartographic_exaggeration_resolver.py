import pytest

from CORE.atlas_lod_level_catalog import (
    AtlasLoDLevelCatalog,
)
from CORE.atlas_physical_cartographic_exaggeration_resolver import (
    AtlasPhysicalCartographicExaggerationResolver,
)


def test_preserves_strict_scale_when_feature_is_already_printable():
    result = AtlasPhysicalCartographicExaggerationResolver.resolve(
        semantic_class="major_road",
        source_width_m=8.0,
        scale_ratio=3000.0,
        product_size_mm=150.0,
        nozzle_diameter_mm=0.4,
        minimum_printable_width_mm=0.8,
        semantic_priority=0.90,
        lod_level=AtlasLoDLevelCatalog.resolve(2),
    )

    assert result.source_width_m == pytest.approx(8.0)
    assert result.strict_scale_width_mm == pytest.approx(
        8.0 * 1000.0 / 3000.0
    )
    assert result.physical_width_mm == pytest.approx(
        result.strict_scale_width_mm
    )
    assert result.exaggerated is False
    assert result.reason == "strict_scale_readable"


def test_raises_unreadable_feature_to_physical_minimum():
    result = AtlasPhysicalCartographicExaggerationResolver.resolve(
        semantic_class="pedestrian_path",
        source_width_m=1.0,
        scale_ratio=5500.0,
        product_size_mm=150.0,
        nozzle_diameter_mm=0.4,
        minimum_printable_width_mm=0.8,
        semantic_priority=0.30,
        lod_level=AtlasLoDLevelCatalog.resolve(2),
    )

    assert result.strict_scale_width_mm == pytest.approx(
        1.0 * 1000.0 / 5500.0
    )
    assert result.physical_width_mm == pytest.approx(0.8)
    assert result.exaggerated is True
    assert result.reason == "physical_minimum"


@pytest.mark.parametrize(
    "semantic_class",
    (
        "major_road",
        "local_road",
        "service_road",
        "pedestrian_path",
        "cycleway",
        "railway",
        "light_rail",
        "tram",
        "narrow_waterway",
        "shoreline_edge",
        "vegetation_element",
    ),
)
def test_supports_required_cartographic_feature_classes(
    semantic_class,
):
    result = AtlasPhysicalCartographicExaggerationResolver.resolve(
        semantic_class=semantic_class,
        source_width_m=1.0,
        scale_ratio=5500.0,
        product_size_mm=150.0,
        nozzle_diameter_mm=0.4,
        minimum_printable_width_mm=0.8,
        semantic_priority=0.5,
        lod_level=AtlasLoDLevelCatalog.resolve(2),
    )

    assert result.semantic_class == semantic_class
    assert result.physical_width_mm >= 0.8


def test_source_truth_is_preserved_separately_from_product_geometry():
    result = AtlasPhysicalCartographicExaggerationResolver.resolve(
        semantic_class="cycleway",
        source_width_m=1.2,
        scale_ratio=5500.0,
        product_size_mm=150.0,
        nozzle_diameter_mm=0.4,
        minimum_printable_width_mm=0.8,
        semantic_priority=0.50,
        lod_level=AtlasLoDLevelCatalog.resolve(2),
    )

    assert result.source_width_m == pytest.approx(1.2)
    assert result.strict_scale_width_mm == pytest.approx(
        1.2 * 1000.0 / 5500.0
    )
    assert result.physical_width_mm == pytest.approx(0.8)
    assert result.source_width_m == pytest.approx(1.2)


def test_relative_visual_hierarchy_is_not_inverted_by_exaggeration():
    major = AtlasPhysicalCartographicExaggerationResolver.resolve(
        semantic_class="major_road",
        source_width_m=8.0,
        scale_ratio=5500.0,
        product_size_mm=150.0,
        nozzle_diameter_mm=0.4,
        minimum_printable_width_mm=0.8,
        semantic_priority=0.90,
        lod_level=AtlasLoDLevelCatalog.resolve(2),
    )

    local = AtlasPhysicalCartographicExaggerationResolver.resolve(
        semantic_class="local_road",
        source_width_m=5.0,
        scale_ratio=5500.0,
        product_size_mm=150.0,
        nozzle_diameter_mm=0.4,
        minimum_printable_width_mm=0.8,
        semantic_priority=0.70,
        lod_level=AtlasLoDLevelCatalog.resolve(2),
    )

    pedestrian = (
        AtlasPhysicalCartographicExaggerationResolver.resolve(
            semantic_class="pedestrian_path",
            source_width_m=1.0,
            scale_ratio=5500.0,
            product_size_mm=150.0,
            nozzle_diameter_mm=0.4,
            minimum_printable_width_mm=0.8,
            semantic_priority=0.30,
            lod_level=AtlasLoDLevelCatalog.resolve(2),
        )
    )

    AtlasPhysicalCartographicExaggerationResolver.validate_relative_hierarchy(
        (major, local, pedestrian)
    )

    assert major.physical_width_mm > local.physical_width_mm
    assert local.physical_width_mm >= pedestrian.physical_width_mm


def test_higher_semantic_priority_may_receive_more_readable_width():
    low = AtlasPhysicalCartographicExaggerationResolver.resolve(
        semantic_class="narrow_waterway",
        source_width_m=0.8,
        scale_ratio=5500.0,
        product_size_mm=150.0,
        nozzle_diameter_mm=0.4,
        minimum_printable_width_mm=0.8,
        semantic_priority=0.30,
        lod_level=AtlasLoDLevelCatalog.resolve(2),
    )

    high = AtlasPhysicalCartographicExaggerationResolver.resolve(
        semantic_class="narrow_waterway",
        source_width_m=0.8,
        scale_ratio=5500.0,
        product_size_mm=150.0,
        nozzle_diameter_mm=0.4,
        minimum_printable_width_mm=0.8,
        semantic_priority=0.90,
        lod_level=AtlasLoDLevelCatalog.resolve(2),
    )

    assert (
        high.physical_width_mm
        >= low.physical_width_mm
    )


def test_nozzle_diameter_contributes_to_physical_minimum():
    result = AtlasPhysicalCartographicExaggerationResolver.resolve(
        semantic_class="shoreline_edge",
        source_width_m=0.5,
        scale_ratio=5500.0,
        product_size_mm=150.0,
        nozzle_diameter_mm=0.6,
        minimum_printable_width_mm=0.4,
        semantic_priority=0.60,
        lod_level=AtlasLoDLevelCatalog.resolve(2),
    )

    assert result.effective_minimum_width_mm >= 0.6
    assert (
        result.physical_width_mm
        >= result.effective_minimum_width_mm
    )


def test_lod_context_is_recorded_without_replacing_lod_system():
    lod = AtlasLoDLevelCatalog.resolve(1)

    result = AtlasPhysicalCartographicExaggerationResolver.resolve(
        semantic_class="railway",
        source_width_m=1.435,
        scale_ratio=5500.0,
        product_size_mm=150.0,
        nozzle_diameter_mm=0.4,
        minimum_printable_width_mm=0.8,
        semantic_priority=0.90,
        lod_level=lod,
    )

    assert result.lod_level is lod
    assert result.lod_level.level == 1


@pytest.mark.parametrize(
    "kwargs",
    (
        {"source_width_m": 0.0},
        {"source_width_m": -1.0},
        {"scale_ratio": 0.0},
        {"product_size_mm": 0.0},
        {"nozzle_diameter_mm": 0.0},
        {"minimum_printable_width_mm": 0.0},
        {"semantic_priority": -0.1},
        {"semantic_priority": 1.1},
    ),
)
def test_rejects_invalid_physical_exaggeration_inputs(
    kwargs,
):
    arguments = {
        "semantic_class": "local_road",
        "source_width_m": 5.0,
        "scale_ratio": 5500.0,
        "product_size_mm": 150.0,
        "nozzle_diameter_mm": 0.4,
        "minimum_printable_width_mm": 0.8,
        "semantic_priority": 0.70,
        "lod_level": AtlasLoDLevelCatalog.resolve(2),
    }
    arguments.update(kwargs)

    with pytest.raises((TypeError, ValueError)):
        AtlasPhysicalCartographicExaggerationResolver.resolve(
            **arguments
        )
