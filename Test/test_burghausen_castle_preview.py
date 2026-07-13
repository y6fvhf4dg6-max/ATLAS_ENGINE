from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)
from CORE.atlas_mesh_validator import AtlasMeshValidator

PBF_PATH = PROJECT_ROOT / "Data/OSM/burghausen-test.osm.pbf"

OUTPUT_PATH = PROJECT_ROOT / "OUTPUT/STL/burghausen_castle_focus.stl"

BBOX = (
    48.1500,
    12.8240,
    48.1628,
    12.8345,
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
        castle_only=True,
        debug=True,
    )

    print("")
    print("=" * 88)
    print("ATLAS BURGHAUSEN MESH TOPOLOGY DIAGNOSTIC")
    print("=" * 88)

    mesh_groups = result.get("mesh_groups", {})

    total_open_edges = 0
    total_non_manifold_edges = 0

    for group_name, group_meshes in mesh_groups.items():
        print("")
        print(f"[GROUP] {group_name}")
        print("-" * 88)

        for mesh_index, mesh in enumerate(group_meshes):
            report = AtlasMeshValidator.report(mesh)

            open_edge_count = report.get("open_edge_count", 0)
            non_manifold_count = report.get(
                "non_manifold_edge_count",
                0,
            )

            total_open_edges += open_edge_count
            total_non_manifold_edges += non_manifold_count

            print(
                f"{group_name}[{mesh_index}] "
                f"source_id={mesh.get('source_id')} "
                f"name={mesh.get('name')} "
                f"profile={mesh.get('castle_profile')} "
                f"height_mm={mesh.get('top_z', 0.0) - mesh.get('bottom_z', 0.0):.3f} "
                f"wall_height_mm={mesh.get('wall_height_mm')} "
                f"roof_profile={mesh.get('castle_roof_profile')} "
                f"tower_roof={mesh.get('castle_roof_applied', False)} "
                f"gable_roof={mesh.get('castle_gable_roof_applied', False)} "
                f"multi_gable={mesh.get('castle_multi_gable_roof_applied', False)} "
                f"triangles={report.get('triangles', 0)} "
                f"open_edges={open_edge_count} "
                f"non_manifold={non_manifold_count} "
                f"valid={report.get('valid', False)}"
            )

            if open_edge_count > 0:
                print("  sample_open_edges=" f"{report.get('sample_open_edges', [])}")

            if non_manifold_count > 0:
                print(
                    "  sample_non_manifold_edges="
                    f"{report.get('sample_non_manifold_edges', [])}"
                )

    print("")
    print("-" * 88)
    print(f"Total diagnostic open edges      : {total_open_edges}")
    print("Total diagnostic non-manifold   : " f"{total_non_manifold_edges}")
    print("=" * 88)
    print("ATLAS BURGHAUSEN FULL SCENE REPORT")
    focus_meshes = []

    for group_name in (
        "buildings",
        "castle_walls",
        "castle_shells",
        "castle_tower_caps",
    ):
        focus_meshes.extend(mesh_groups.get(group_name, []))

    focus_points = []

    for mesh in focus_meshes:
        for triangle in mesh.get("triangles", []):
            focus_points.extend(triangle)

    if focus_points:
        min_x = min(point[0] for point in focus_points)
        max_x = max(point[0] for point in focus_points)
        min_y = min(point[1] for point in focus_points)
        max_y = max(point[1] for point in focus_points)

        focus_width_mm = max_x - min_x
        focus_depth_mm = max_y - min_y

        print("")
        print("=" * 88)
        print("ATLAS BURGHAUSEN CASTLE-FOCUS BOUNDS")
        print("=" * 88)
        print(f"Minimum X                     : {min_x:.3f} mm")
        print(f"Maximum X                     : {max_x:.3f} mm")
        print(f"Minimum Y                     : {min_y:.3f} mm")
        print(f"Maximum Y                     : {max_y:.3f} mm")
        print(f"Castle-focus width            : {focus_width_mm:.3f} mm")
        print(f"Castle-focus depth            : {focus_depth_mm:.3f} mm")
        print(
            f"Largest occupied dimension    : "
            f"{max(focus_width_mm, focus_depth_mm):.3f} mm"
        )
        print(
            f"Current 180 mm utilization    : "
            f"{max(focus_width_mm, focus_depth_mm) / 180.0 * 100.0:.2f}%"
        )
        print("=" * 88)
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
