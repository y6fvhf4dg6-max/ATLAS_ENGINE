from pathlib import Path


ENGINE_PATH = Path(
    "CORE/atlas_foundation_first_engine.py"
)


def _engine_source():
    return ENGINE_PATH.read_text()


def test_generate_city_imports_urban_fabric_quality_report():
    source = _engine_source()

    assert (
        "from CORE.atlas_urban_fabric_quality_report import ("
        in source
    )

    assert (
        "AtlasUrbanFabricQualityReport"
        in source
    )


def test_generate_city_builds_urban_fabric_quality_report_from_final_result():
    source = _engine_source()

    assert (
        "AtlasUrbanFabricQualityReport.build("
        in source
    )

    assert (
        "scene_result=result"
        in source
    )


def test_generate_city_returns_urban_fabric_quality_report():
    source = _engine_source()

    assert (
        'result["urban_fabric_quality_report"]'
        in source
    )


def test_quality_report_wiring_occurs_after_water_and_bridge_composition_metadata():
    source = _engine_source()

    report_position = source.find(
        'result["urban_fabric_quality_report"]'
    )

    water_position = source.find(
        "attach_water_shoreline_composition"
    )

    bridge_position = source.find(
        "attach_bridge_urban_integration"
    )

    assert bridge_position >= 0
    assert water_position >= 0
    assert report_position >= 0

    assert report_position > bridge_position
    assert report_position > water_position
