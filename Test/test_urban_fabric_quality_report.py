from CORE.atlas_urban_fabric_quality_report import (
    AtlasUrbanFabricQualityReport,
)


def _scene_result():
    return {
        "scene_morphology_evidence": {
            "building_density": 0.62,
            "road_density": 0.55,
            "block_compactness": 0.70,
            "vegetation_coverage": 0.28,
            "forest_coverage": 0.08,
            "water_coverage": 0.12,
            "railway_presence": True,
            "terrain_relief": 0.18,
            "landmark_density": 0.06,
        },
        "effective_scene_morphology": "historic_core",
        "morphology_composition_policy": {
            "terrain_emphasis": 0.40,
            "road_emphasis": 0.90,
            "urban_block_emphasis": 0.90,
            "vegetation_emphasis": 0.45,
            "water_emphasis": 0.55,
            "infrastructure_emphasis": 0.85,
            "landmark_emphasis": 1.00,
        },
        "city_composition_lod": {
            "decisions": {
                "road_1": {
                    "semantic_class": "major_road",
                    "retain": True,
                    "simplify": False,
                },
                "building_1": {
                    "semantic_class": "generic_building",
                    "retain": True,
                    "simplify": True,
                },
                "landmark_1": {
                    "semantic_class": "landmark",
                    "retain": True,
                    "simplify": False,
                },
                "path_1": {
                    "semantic_class": "minor_path",
                    "retain": False,
                    "simplify": False,
                },
            },
        },
        "mesh_groups": {
            "roads": [{"type": "road"}],
            "buildings": [{"type": "building"}],
            "parks": [{"type": "park"}],
            "trees": [{"type": "tree"}],
            "forest_canopies": [],
            "waters": [{"type": "water"}],
            "landmarks": [{"type": "landmark"}],
            "railways": [{"type": "railway"}],
        },
    }


def test_quality_report_builds_deterministic_read_only_metrics():
    scene = _scene_result()

    original = repr(scene)

    first = AtlasUrbanFabricQualityReport.build(
        scene_result=scene,
    )
    second = AtlasUrbanFabricQualityReport.build(
        scene_result=scene,
    )

    assert first == second
    assert repr(scene) == original

    assert first["type"] == (
        "urban_fabric_quality_report"
    )

    metrics = first["metrics"]

    assert metrics["building_density"] == 0.62
    assert metrics["road_density"] == 0.55
    assert metrics["block_compactness"] == 0.70
    assert metrics["vegetation_coverage"] == 0.28
    assert metrics["forest_coverage"] == 0.08
    assert metrics["water_coverage"] == 0.12
    assert metrics["railway_presence"] is True
    assert metrics["terrain_relief"] == 0.18
    assert metrics["landmark_density"] == 0.06


def test_quality_report_contains_composition_lod_statistics():
    report = AtlasUrbanFabricQualityReport.build(
        scene_result=_scene_result(),
    )

    stats = report[
        "composition_lod_statistics"
    ]

    assert stats["decision_count"] == 4
    assert stats["retained_count"] == 3
    assert stats["suppressed_count"] == 1
    assert stats["simplified_count"] == 1

    assert stats["retained_ratio"] == 0.75
    assert stats["suppressed_ratio"] == 0.25
    assert stats["simplified_ratio"] == 0.25


def test_quality_report_identifies_missing_semantic_content():
    scene = _scene_result()

    scene["mesh_groups"]["parks"] = []
    scene["mesh_groups"]["waters"] = []
    scene["mesh_groups"]["railways"] = []

    report = AtlasUrbanFabricQualityReport.build(
        scene_result=scene,
    )

    codes = {
        issue["code"]
        for issue in report["issues"]
    }

    assert "missing_park_content" in codes
    assert "missing_water_content" in codes
    assert "missing_railway_content" in codes


def test_quality_report_identifies_visually_weak_present_content():
    scene = _scene_result()

    scene["scene_morphology_evidence"][
        "road_density"
    ] = 0.01

    scene["scene_morphology_evidence"][
        "vegetation_coverage"
    ] = 0.01

    report = AtlasUrbanFabricQualityReport.build(
        scene_result=scene,
    )

    codes = {
        issue["code"]
        for issue in report["issues"]
    }

    assert "weak_road_presence" in codes
    assert "weak_vegetation_presence" in codes


def test_quality_report_contains_vegetation_composition_metrics():
    scene = _scene_result()

    scene["vegetation_composition"] = {
        "isolated_trees": (
            {"id": 1},
            {"id": 2},
            {"id": 3},
        ),
        "tree_rows": (
            {"id": "row_a"},
            {"id": "row_b"},
        ),
        "forest_canopies": (
            {"id": "canopy_a"},
        ),
        "tree_row_member_count": 8,
    }

    report = AtlasUrbanFabricQualityReport.build(
        scene_result=scene,
    )

    vegetation = report[
        "vegetation_composition_metrics"
    ]

    assert vegetation == {
        "isolated_tree_count": 3,
        "tree_row_count": 2,
        "forest_canopy_count": 1,
        "tree_row_member_count": 8,
        "vegetation_mode_distribution": {
            "isolated_tree": 0.50,
            "tree_row": 2 / 6,
            "forest_canopy": 1 / 6,
        },
        "isolated_tree_clutter_ratio": 0.50,
    }


def test_quality_report_counts_building_height_outliers():
    scene = _scene_result()

    scene["building_height_resolutions"] = (
        {
            "building_id": 1,
            "is_statistical_outlier": False,
        },
        {
            "building_id": 2,
            "is_statistical_outlier": True,
        },
        {
            "building_id": 3,
            "is_statistical_outlier": True,
        },
    )

    report = AtlasUrbanFabricQualityReport.build(
        scene_result=scene,
    )

    assert (
        report["building_height_metrics"][
            "building_height_outlier_count"
        ]
        == 2
    )


def test_quality_report_calculates_terrain_prominence_from_existing_policy():
    scene = _scene_result()

    report = AtlasUrbanFabricQualityReport.build(
        scene_result=scene,
    )

    assert (
        report["terrain_metrics"][
            "terrain_prominence_ratio"
        ]
        == 0.40
    )


def test_quality_report_calculates_landmark_to_background_prominence_ratio():
    scene = _scene_result()

    scene["city_composition_lod"]["decisions"] = {
        "landmark_1": {
            "semantic_class": "landmark",
            "retain": True,
            "simplify": False,
            "narrative_priority": 1.00,
        },
        "building_1": {
            "semantic_class": "generic_building",
            "retain": True,
            "simplify": False,
            "narrative_priority": 0.40,
        },
        "building_2": {
            "semantic_class": "urban_block",
            "retain": True,
            "simplify": False,
            "narrative_priority": 0.60,
        },
    }

    report = AtlasUrbanFabricQualityReport.build(
        scene_result=scene,
    )

    prominence = report[
        "landmark_prominence_metrics"
    ]

    assert (
        prominence[
            "landmark_narrative_priority"
        ]
        == 1.00
    )

    assert (
        prominence[
            "background_narrative_priority"
        ]
        == 0.50
    )

    assert (
        prominence[
            "landmark_to_background_prominence_ratio"
        ]
        == 2.0
    )


def test_quality_report_measures_bridge_major_road_continuity():
    scene = _scene_result()

    scene["bridge_urban_integration"] = (
        {
            "bridge_element_id": "bridge_1",
            "approach_road_continuity": True,
            "approach_count": 2,
        },
        {
            "bridge_element_id": "bridge_2",
            "approach_road_continuity": False,
            "approach_count": 0,
        },
    )

    report = AtlasUrbanFabricQualityReport.build(
        scene_result=scene,
    )

    continuity = report[
        "road_continuity_metrics"
    ]

    assert continuity[
        "bridge_record_count"
    ] == 2

    assert continuity[
        "continuous_bridge_count"
    ] == 1

    assert continuity[
        "major_road_continuity_ratio"
    ] == 0.50


def test_quality_report_measures_water_surface_completeness():
    scene = _scene_result()

    scene["water_shoreline_composition"] = (
        {
            "semantic_class": "water",
            "supports_water_surface_continuity": True,
        },
        {
            "semantic_class": "coastline",
            "supports_water_surface_continuity": False,
        },
        {
            "semantic_class": "water",
            "supports_water_surface_continuity": True,
        },
    )

    report = AtlasUrbanFabricQualityReport.build(
        scene_result=scene,
    )

    water = report[
        "water_quality_metrics"
    ]

    assert water[
        "composition_record_count"
    ] == 3

    assert water[
        "continuous_surface_record_count"
    ] == 2

    assert water[
        "water_completeness_ratio"
    ] == (
        2 / 3
    )


def test_quality_report_flags_weak_continuity_when_present():
    scene = _scene_result()

    scene["bridge_urban_integration"] = (
        {
            "bridge_element_id": "bridge_1",
            "approach_road_continuity": False,
            "approach_count": 0,
        },
    )

    scene["water_shoreline_composition"] = (
        {
            "semantic_class": "water",
            "supports_water_surface_continuity": False,
        },
    )

    report = AtlasUrbanFabricQualityReport.build(
        scene_result=scene,
    )

    codes = {
        issue["code"]
        for issue in report["issues"]
    }

    assert "weak_major_road_continuity" in codes
    assert "weak_water_surface_continuity" in codes


def test_quality_report_measures_road_hierarchy_coverage_from_city_scene():
    from CORE.atlas_urban_fabric_scene_contract import (
        AtlasUrbanFabricElement,
        AtlasUrbanFabricScene,
    )

    scene = _scene_result()

    scene["city_composition_scene"] = AtlasUrbanFabricScene(
        elements=(
            AtlasUrbanFabricElement(
                element_id="road_1",
                semantic_class="major_road",
            ),
            AtlasUrbanFabricElement(
                element_id="road_2",
                semantic_class="local_road",
            ),
            AtlasUrbanFabricElement(
                element_id="road_3",
                semantic_class="service_road",
            ),
            AtlasUrbanFabricElement(
                element_id="road_4",
                semantic_class="pedestrian_path",
            ),
            AtlasUrbanFabricElement(
                element_id="building_1",
                semantic_class="generic_building",
            ),
        ),
    )

    report = AtlasUrbanFabricQualityReport.build(
        scene_result=scene,
    )

    road = report[
        "road_hierarchy_metrics"
    ]

    assert road["road_element_count"] == 4
    assert road["major_road_count"] == 1
    assert road["local_road_count"] == 1
    assert road["service_road_count"] == 1
    assert road["pedestrian_path_count"] == 1

    assert road["road_hierarchy_class_count"] == 4
    assert road["road_hierarchy_coverage_ratio"] == 1.0


def test_quality_report_measures_semantic_surface_coverage():
    scene = _scene_result()

    scene["mesh_groups"]["parks"] = (
        {
            "type": "park_foundation",
            "semantic_surface_texture": {
                "surface_role": "formal_park",
            },
        },
        {
            "type": "park_foundation",
        },
        {
            "type": "park_foundation",
            "semantic_surface_texture": {
                "surface_role": "plaza",
            },
        },
    )

    report = AtlasUrbanFabricQualityReport.build(
        scene_result=scene,
    )

    surfaces = report[
        "semantic_surface_metrics"
    ]

    assert surfaces[
        "eligible_surface_count"
    ] == 3

    assert surfaces[
        "textured_surface_count"
    ] == 2

    assert surfaces[
        "semantic_surface_coverage_ratio"
    ] == 2 / 3


def test_quality_report_measures_forest_canopy_presence():
    scene = _scene_result()

    scene["mesh_groups"]["forest_canopies"] = (
        {
            "type": "forest_canopy_foundation",
        },
        {
            "type": "forest_canopy_foundation",
        },
    )

    report = AtlasUrbanFabricQualityReport.build(
        scene_result=scene,
    )

    forest = report[
        "forest_continuity_metrics"
    ]

    assert forest[
        "forest_canopy_mesh_count"
    ] == 2

    assert forest[
        "forest_canopy_present"
    ] is True
