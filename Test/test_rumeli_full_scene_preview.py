from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)
from CORE.atlas_mesh_repair import (
    AtlasMeshRepair,
)
from EXPORT.atlas_stl_writer import (
    AtlasSTLWriter,
)


PBF_PATH = (
    PROJECT_ROOT
    / "Data/OSM/rumeli-hisari-test.osm.pbf"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "OUTPUT/STL/rumeli_hisari_full_scene_preview.stl"
)

LAYER_OUTPUT_PATHS = {
    "terrain": (
        PROJECT_ROOT
        / "OUTPUT/STL/rumeli_hisari_full_terrain.stl"
    ),
    "buildings": (
        PROJECT_ROOT
        / "OUTPUT/STL/rumeli_hisari_full_buildings.stl"
    ),
    "roads": (
        PROJECT_ROOT
        / "OUTPUT/STL/rumeli_hisari_full_roads.stl"
    ),
    "parks": (
        PROJECT_ROOT
        / "OUTPUT/STL/rumeli_hisari_full_parks.stl"
    ),
    "waters": (
        PROJECT_ROOT
        / "OUTPUT/STL/rumeli_hisari_full_water.stl"
    ),
    "castle_shells": (
        PROJECT_ROOT
        / "OUTPUT/STL/rumeli_hisari_full_castle_shell.stl"
    ),
    "castle_tower_caps": (
        PROJECT_ROOT
        / "OUTPUT/STL/rumeli_hisari_full_castle_towers.stl"
    ),
}

BBOX = (
    41.08050,
    29.04850,
    41.08850,
    29.05950,
)


def main():
    if not PBF_PATH.exists():
        raise FileNotFoundError(
            f"PBF bulunamadı: {PBF_PATH}"
        )

    result = (
        AtlasFoundationFirstEngine
        .generate_city_stl(
            pbf_path=str(PBF_PATH),
            bbox=BBOX,
            output_path=str(OUTPUT_PATH),
            target_size_mm=200,
            bed_width_mm=256,
            bed_depth_mm=256,
            margin_mm=15,
            max_buildings=None,
            min_points=3,
            max_points=500,
            z_scale=5500,
            terrain_provider_name="srtm",
            terrain_smoothing_passes=1,
            strict_input_quality=True,
            nature_provider_names=(),
            castle_only=False,
            castle_focus=True,
            castle_focus_padding_m=70.0,
            debug=True,
        )
    )

    expected_focus_bbox = (
        41.08317068,
        29.05452733,
        41.08665972,
        29.05766147,
    )

    assert result["castle_focus"] is True

    assert tuple(
        round(value, 8)
        for value in result["working_bbox"]
    ) == expected_focus_bbox

    print("")
    print("=" * 88)
    print("ATLAS RUMELI HISARI FULL SCENE REPORT")
    print("=" * 88)

    print(
        f"Reader buildings              : "
        f"{result.get('reader_buildings', 0)}"
    )

    print(
        f"Reader roads                  : "
        f"{result.get('reader_roads', 0)}"
    )

    print(
        f"Reader pedestrian paths       : "
        f"{result.get('reader_pedestrian_paths', 0)}"
    )

    print(
        f"Reader parks                  : "
        f"{result.get('reader_parks', 0)}"
    )

    print(
        f"Reader trees                  : "
        f"{result.get('reader_trees', 0)}"
    )

    print(
        f"Reader coastlines             : "
        f"{result.get('reader_coastlines', 0)}"
    )

    print(
        f"Reader castles                : "
        f"{result.get('reader_castles', 0)}"
    )

    print(
        f"Reader castle walls           : "
        f"{result.get('reader_castle_walls', 0)}"
    )

    print(
        f"Building meshes               : "
        f"{result.get('buildings', 0)}"
    )

    print(
        f"Water meshes                  : "
        f"{result.get('water_meshes', 0)}"
    )

    print(
        f"Castle wall meshes            : "
        f"{result.get('castle_wall_meshes', 0)}"
    )

    print(
        f"Castle shell meshes           : "
        f"{result.get('castle_shell_meshes', 0)}"
    )

    print(
        f"Castle tower cap meshes       : "
        f"{result.get('castle_tower_cap_meshes', 0)}"
    )

    print(
        f"Total meshes                  : "
        f"{result.get('meshes', 0)}"
    )

    print(
        f"Total triangles               : "
        f"{result.get('triangles', 0)}"
    )

    print(
        f"Terrain min height            : "
        f"{result.get('terrain_min_height_m')}"
    )

    print(
        f"Terrain max height            : "
        f"{result.get('terrain_max_height_m')}"
    )

    print(
        f"Terrain height delta          : "
        f"{result.get('terrain_delta_height_m')}"
    )

    print(
        f"Terrain smoothing passes      : "
        f"{result.get('terrain_smoothing_passes', 0)}"
    )

    input_quality_report = result.get(
        "input_quality_report",
        {},
    )

    geometry_quality = input_quality_report.get(
        "geometry",
        {},
    )

    semantic_quality = input_quality_report.get(
        "semantics",
        {},
    )

    terrain_quality = input_quality_report.get(
        "terrain",
        {},
    )

    quality_policy = input_quality_report.get(
        "policy",
        {},
    )

    automatic_corrections = input_quality_report.get(
        "automatic_corrections",
        {},
    )

    print(
        f"Input geometry valid percent  : "
        f"{geometry_quality.get('valid_percent')}"
    )

    print(
        f"Input invalid geometries      : "
        f"{geometry_quality.get('invalid_count')}"
    )

    geometry_issues = geometry_quality.get(
        "issue_counts",
        {},
    )

    print(
        f"Geometry not enough points    : "
        f"{geometry_issues.get('not_enough_points', 0)}"
    )

    print(
        f"Geometry duplicate points     : "
        f"{geometry_issues.get('duplicate_points', 0)}"
    )

    print(
        f"Geometry self intersections   : "
        f"{geometry_issues.get('self_intersection', 0)}"
    )

    print(
        f"Geometry zero area            : "
        f"{geometry_issues.get('zero_area', 0)}"
    )

    print(
        f"Height coverage percent       : "
        f"{semantic_quality.get('height_coverage_percent')}"
    )

    print(
        f"Roof coverage percent         : "
        f"{semantic_quality.get('roof_coverage_percent')}"
    )

    semantic_issues = semantic_quality.get(
        "issue_counts",
        {},
    )

    print(
        f"Invalid building heights      : "
        f"{semantic_issues.get('invalid_height', 0)}"
    )

    print(
        f"Non-positive building heights : "
        f"{semantic_issues.get('non_positive_height', 0)}"
    )

    print(
        f"Invalid building levels       : "
        f"{semantic_issues.get('invalid_levels', 0)}"
    )

    print(
        f"Non-positive building levels  : "
        f"{semantic_issues.get('non_positive_levels', 0)}"
    )

    print(
        f"Unknown roof shapes           : "
        f"{semantic_issues.get('unknown_roof_shape', 0)}"
    )

    print(
        f"Conflicting height values     : "
        f"{semantic_issues.get('conflicting_height_values', 0)}"
    )

    print(
        f"Conflicting roof shapes       : "
        f"{semantic_issues.get('conflicting_roof_shapes', 0)}"
    )

    print(
        f"Castle relations missing outer: "
        f"{semantic_issues.get('relation_missing_outer_geometry', 0)}"
    )

    print(
        f"Castle ways with inner rings  : "
        f"{semantic_issues.get('way_has_inner_geometry', 0)}"
    )

    print(
        f"Unsupported castle geometries : "
        f"{semantic_issues.get('unsupported_castle_geometry_type', 0)}"
    )

    print(
        f"Castle records missing tag    : "
        f"{semantic_issues.get('missing_castle_tag', 0)}"
    )

    print(
        f"Unknown castle records        : "
        f"{semantic_quality.get('unknown_castle_count')}"
    )

    print(
        f"Terrain coverage percent      : "
        f"{terrain_quality.get('coverage_percent')}"
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
        f"{quality_policy.get('reasons')}"
    )

    print(
        f"Terrain samples auto-filled   : "
        f"{automatic_corrections.get('terrain_missing_samples_filled', 0)}"
    )

    print(
        f"Inferred perimeter walls      : "
        f"{automatic_corrections.get('inferred_perimeter_walls', 0)}"
    )

    print(
        f"Castle focus fallback used    : "
        f"{automatic_corrections.get('castle_focus_fallback_used', False)}"
    )

    print(
        f"Castle relation roles corrected: "
        f"{automatic_corrections.get('castle_relation_roles_corrected', 0)}"
    )

    print(
        f"Automatic corrections total  : "
        f"{automatic_corrections.get('total_count', 0)}"
    )

    print(
        f"Output                        : "
        f"{OUTPUT_PATH}"
    )

    print("=" * 88)

    mesh_groups = result.get(
        "mesh_groups",
        {},
    )

    for group_name, output_path in (
        LAYER_OUTPUT_PATHS.items()
    ):
        group_meshes = mesh_groups.get(
            group_name,
            [],
        )

        if not group_meshes:
            continue

        AtlasSTLWriter.write(
            meshes=group_meshes,
            output_path=str(output_path),
            solid_name=(
                "ATLAS_RUMELI_FULL_"
                f"{group_name.upper()}"
            ),
        )

    total_open_edges = 0
    total_non_manifold_edges = 0

    for group_name, group_meshes in mesh_groups.items():
        group_open_edges = 0
        group_non_manifold_edges = 0

        for mesh in group_meshes:
            report = AtlasMeshValidator.report(
                mesh
            )

            open_edge_count = report.get(
                "open_edge_count",
                0,
            )

            non_manifold_edge_count = report.get(
                "non_manifold_edge_count",
                0,
            )

            group_open_edges += open_edge_count
            group_non_manifold_edges += (
                non_manifold_edge_count
            )

            total_open_edges += open_edge_count
            total_non_manifold_edges += (
                non_manifold_edge_count
            )

        print(
            f"{group_name:<30}: "
            f"open={group_open_edges}, "
            f"non_manifold={group_non_manifold_edges}"
        )

    print("")
    print("ROAD VALIDATOR STRUCTURE REPORT")
    print("-" * 88)

    invalid_reason_counts = {}

    for mesh_index, mesh in enumerate(
        mesh_groups.get(
            "roads",
            [],
        )
    ):
        report = AtlasMeshValidator.report(
            mesh
        )

        if report.get(
            "structure_valid",
            False,
        ):
            continue

        reason = report.get(
            "reason",
            "unknown",
        )

        invalid_reason_counts[reason] = (
            invalid_reason_counts.get(
                reason,
                0,
            )
            + 1
        )

    print(
        "invalid_reason_counts:",
        invalid_reason_counts,
    )

    for mesh_index, mesh in enumerate(
        mesh_groups.get(
            "roads",
            [],
        )
    ):
        report = AtlasMeshValidator.report(
            mesh
        )

        if report.get(
            "reason"
        ) != "wall_count_mismatch":
            continue

        print(
            f"wall_count_mismatch roads[{mesh_index}] "
            f"bottom={len(mesh.get('bottom', []))} "
            f"top={len(mesh.get('top', []))} "
            f"walls={len(mesh.get('walls', []))} "
            f"triangles={len(mesh.get('triangles', []))} "
            f"road_type={mesh.get('road_type')}"
        )

    print("")
    print("ROAD REPAIR COMPARISON")
    print("-" * 88)

    for mesh_index, mesh in enumerate(
        mesh_groups.get(
            "roads",
            [],
        )
    ):
        before_report = AtlasMeshValidator.report(
            mesh
        )

        repaired_mesh = AtlasMeshRepair.repair(
            mesh
        )

        after_report = AtlasMeshValidator.report(
            repaired_mesh
        )

        before_triangles = before_report.get(
            "triangles",
            0,
        )

        after_triangles = after_report.get(
            "triangles",
            0,
        )

        before_open = before_report.get(
            "open_edge_count",
            0,
        )

        after_open = after_report.get(
            "open_edge_count",
            0,
        )

        before_non_manifold = before_report.get(
            "non_manifold_edge_count",
            0,
        )

        after_non_manifold = after_report.get(
            "non_manifold_edge_count",
            0,
        )

        if (
            before_triangles != after_triangles
            or before_open != after_open
            or before_non_manifold
            != after_non_manifold
        ):
            print(
                f"roads[{mesh_index}] "
                f"triangles={before_triangles}->{after_triangles} "
                f"open={before_open}->{after_open} "
                f"non_manifold="
                f"{before_non_manifold}->{after_non_manifold}"
            )

    print("")
    print("PROBLEMATIC ROAD MESHES")
    print("-" * 88)

    for mesh_index, mesh in enumerate(
        mesh_groups.get(
            "roads",
            [],
        )
    ):
        report = AtlasMeshValidator.report(
            mesh
        )

        non_manifold_count = report.get(
            "non_manifold_edge_count",
            0,
        )

        if non_manifold_count <= 0:
            continue

        print(
            f"roads[{mesh_index}] "
            f"source_id={mesh.get('source_id')} "
            f"name={mesh.get('name')} "
            f"road_type={mesh.get('road_type')} "
            f"triangles={report.get('triangles', 0)} "
            f"non_manifold={non_manifold_count}"
        )

        print(
            "  sample_non_manifold_edges="
            f"{report.get('sample_non_manifold_edges', [])}"
        )

        print(
            "  mesh_keys="
            f"{sorted(mesh.keys())}"
        )

        for key in sorted(mesh.keys()):
            if key == "triangles":
                continue

            print(
                f"  {key}="
                f"{mesh.get(key)}"
            )

    print(
        f"Total open edges              : "
        f"{total_open_edges}"
    )

    print(
        f"Total non-manifold edges      : "
        f"{total_non_manifold_edges}"
    )

    print("=" * 88)


if __name__ == "__main__":
    main()
