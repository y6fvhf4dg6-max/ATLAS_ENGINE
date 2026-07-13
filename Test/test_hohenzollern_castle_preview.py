from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)

PBF_PATH = PROJECT_ROOT / "Data/OSM/hohenzollern-test.osm.pbf"

OUTPUT_PATH = PROJECT_ROOT / "OUTPUT/STL/hohenzollern_castle_focus.stl"

BBOX = (
    48.3205,
    8.9635,
    48.3265,
    8.9720,
)


def main():
    if not PBF_PATH.exists():
        raise FileNotFoundError(f"PBF bulunamadı: {PBF_PATH}")

    result = AtlasFoundationFirstEngine.generate_city_stl(
        pbf_path=str(PBF_PATH),
        bbox=BBOX,
        output_path=str(OUTPUT_PATH),
        target_size_mm=180,
        bed_width_mm=256,
        bed_depth_mm=256,
        margin_mm=10,
        max_buildings=None,
        min_points=3,
        max_points=500,
        z_scale=5500,
        terrain_provider_name="srtm",
        nature_provider_names=(),
        strict_input_quality=True,
        castle_only=False,
        castle_focus=True,
        castle_focus_padding_m=70.0,
        debug=True,
    )

    print("")
    print("=" * 88)
    print("ATLAS HOHENZOLLERN FULL SCENE REPORT")
    print("=" * 88)

    print(f"Reader buildings              : " f"{result.get('reader_buildings', 0)}")

    print(f"Reader trees                  : " f"{result.get('reader_trees', 0)}")

    print(f"Reader roads                  : " f"{result.get('reader_roads', 0)}")

    print(
        f"Reader pedestrian paths       : "
        f"{result.get('reader_pedestrian_paths', 0)}"
    )

    print(f"Reader parks                  : " f"{result.get('reader_parks', 0)}")

    print(f"Reader castles                : " f"{result.get('reader_castles', 0)}")

    print(f"Reader castle walls           : " f"{result.get('reader_castle_walls', 0)}")

    print(f"Building meshes               : " f"{result.get('buildings', 0)}")

    print(f"Castle wall meshes            : " f"{result.get('castle_wall_meshes', 0)}")

    print(f"Castle shell meshes           : " f"{result.get('castle_shell_meshes', 0)}")

    print(
        f"Castle tower cap meshes       : "
        f"{result.get('castle_tower_cap_meshes', 0)}"
    )

    print(f"Total meshes                  : " f"{result.get('meshes', 0)}")

    print(f"Total triangles               : " f"{result.get('triangles', 0)}")

    input_quality = result.get(
        "input_quality_report",
        {},
    )

    quality_policy = input_quality.get(
        "policy",
        {},
    )

    semantic_quality = input_quality.get(
        "semantics",
        {},
    )

    semantic_issues = semantic_quality.get(
        "issue_counts",
        {},
    )

    semantic_issue_records = semantic_quality.get(
        "issue_records",
        {},
    )

    semantic_severity_counts = semantic_quality.get(
        "severity_counts",
        {},
    )

    semantic_severity_issues = semantic_quality.get(
        "severity_issues",
        {},
    )

    print("")
    print("INPUT QUALITY")
    print("-" * 88)

    print(
        f"Geometry valid percent        : "
        f"{input_quality.get('geometry', {}).get('valid_percent')}"
    )

    print(
        f"Terrain coverage percent      : "
        f"{input_quality.get('terrain', {}).get('coverage_percent')}"
    )

    print(
        f"Height coverage percent       : "
        f"{semantic_quality.get('height_coverage_percent')}"
    )

    print(
        f"Roof coverage percent         : "
        f"{semantic_quality.get('roof_coverage_percent')}"
    )

    print(
        f"Semantic issue total          : "
        f"{sum(int(value or 0) for value in semantic_issues.values())}"
    )

    nonzero_semantic_issues = {
        issue_name: int(issue_count or 0)
        for issue_name, issue_count
        in semantic_issues.items()
        if int(issue_count or 0) > 0
    }

    print(
        f"Nonzero semantic issues       : "
        f"{nonzero_semantic_issues}"
    )

    unknown_castles = input_quality.get(
        "castle_geometry",
        {},
    ).get(
        "unknown_castles",
        [],
    )

    nonempty_semantic_records = {
        issue_name: records
        for issue_name, records
        in semantic_issue_records.items()
        if records
    }

    print(
        f"Semantic severity counts      : "
        f"{semantic_severity_counts}"
    )

    print(
        f"Semantic severity issues      : "
        f"{semantic_severity_issues}"
    )

    print(
        f"Semantic issue record groups  : "
        f"{len(nonempty_semantic_records)}"
    )

    for issue_name, records in (
        nonempty_semantic_records.items()
    ):
        print(
            f"  {issue_name} ({len(records)})"
        )

        for record in records:
            print(
                f"    type={record.get('record_type')} "
                f"id={record.get('id')} "
                f"field={record.get('field')} "
                f"value={record.get('value')}"
            )

    print(
        f"Unknown castle count          : "
        f"{semantic_quality.get('unknown_castle_count', 0)}"
    )

    print(
        f"Unknown castle records        : "
        f"{unknown_castles}"
    )

    print(
        f"Input quality risk            : "
        f"{quality_policy.get('risk_level')}"
    )

    print(
        f"Input quality action          : "
        f"{quality_policy.get('action')}"
    )

    print(
        f"Input quality reasons         : "
        f"{quality_policy.get('reasons', [])}"
    )

    print(f"Output                        : " f"{OUTPUT_PATH}")

    print("=" * 88)


if __name__ == "__main__":
    main()
