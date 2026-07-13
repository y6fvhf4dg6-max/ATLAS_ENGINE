from pathlib import Path

from CORE.atlas_castle_geometry_classifier import (
    AtlasCastleGeometryClassifier,
)
from CORE.atlas_input_quality_report import (
    AtlasInputQualityReport,
)
from CORE.atlas_local_osm_reader import (
    AtlasLocalOSMReader,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BURGHAUSEN_PBF = (
    PROJECT_ROOT
    / "Data/OSM/burghausen-test.osm.pbf"
)

HOHENZOLLERN_PBF = (
    PROJECT_ROOT
    / "Data/OSM/hohenzollern-test.osm.pbf"
)

BURGHAUSEN_BBOX = (
    48.1500,
    12.8240,
    48.1628,
    12.8345,
)

HOHENZOLLERN_BBOX = (
    48.3205,
    8.9635,
    48.3265,
    8.9720,
)


def build_quality_report(
    pbf_path,
    bbox,
):
    if not pbf_path.exists():
        raise FileNotFoundError(
            f"Fixture PBF bulunamadı: {pbf_path}"
        )

    data = AtlasLocalOSMReader.read(
        pbf_path=str(pbf_path),
        bbox=bbox,
    )

    castles = data.get(
        "castles",
        [],
    )

    castle_geometry = (
        AtlasCastleGeometryClassifier.classify(
            castles=castles,
            castle_walls=data.get(
                "castle_walls",
                [],
            ),
            debug=False,
        )
    )

    report = AtlasInputQualityReport.build(
        buildings=data.get(
            "buildings",
            [],
        ),
        castles=castles,
        castle_geometry=castle_geometry,
        terrain_grid={
            "sample_count": 1,
            "missing_sample_count": 0,
        },
    )

    report["policy"] = (
        AtlasInputQualityReport.evaluate_policy(
            report
        )
    )

    return report


def test_burghausen_real_fixture_input_quality():
    report = build_quality_report(
        pbf_path=BURGHAUSEN_PBF,
        bbox=BURGHAUSEN_BBOX,
    )

    geometry = report["geometry"]
    semantics = report["semantics"]
    issues = semantics["issue_counts"]
    policy = report["policy"]

    assert geometry["valid_percent"] == 100.0

    assert semantics["unknown_castle_count"] == 0

    assert issues["unknown_roof_shape"] == 0
    assert issues["complex_roof_shape"] == 5

    complex_roof_records = (
        semantics["issue_records"]
        ["complex_roof_shape"]
    )

    assert [
        record["id"]
        for record in complex_roof_records
    ] == [
        122098764,
        122098773,
        122155613,
        122507266,
        123098479,
    ]

    assert all(
        record["record_type"] == "building"
        and record["field"] == "roof:shape"
        and record["value"] == "many"
        for record in complex_roof_records
    )

    assert semantics["building_count"] == 505
    assert semantics["height_count"] == 227
    assert semantics["roof_count"] == 113

    assert policy["risk_level"] == "LOW"
    assert policy["action"] == "CONTINUE"
    assert policy["reasons"] == []


def test_hohenzollern_real_fixture_input_quality():
    report = build_quality_report(
        pbf_path=HOHENZOLLERN_PBF,
        bbox=HOHENZOLLERN_BBOX,
    )

    geometry = report["geometry"]
    semantics = report["semantics"]
    issues = semantics["issue_counts"]
    policy = report["policy"]

    assert geometry["valid_percent"] == 100.0

    assert semantics["unknown_castle_count"] == 0

    assert sum(
        int(value or 0)
        for value in issues.values()
    ) == 0

    assert policy["risk_level"] == "MEDIUM"
    assert policy["action"] == "WARN"

    assert policy["reasons"] == [
        "building_height_coverage_below_25",
        "building_roof_coverage_below_10",
    ]
