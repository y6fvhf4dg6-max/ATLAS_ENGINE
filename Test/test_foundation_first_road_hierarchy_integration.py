import inspect

from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)


def test_foundation_first_engine_exposes_optional_road_print_minimum():
    signature = inspect.signature(
        AtlasFoundationFirstEngine.generate_city_stl
    )

    parameter = signature.parameters[
        "road_minimum_printable_width_mm"
    ]

    assert parameter.default is None
