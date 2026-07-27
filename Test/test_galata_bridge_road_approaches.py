from collections import Counter

from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)
from Test.preview_galata_bridge_scene import (
    BBOX,
    PBF_PATH,
    PRODUCT_SIZE_MM,
    SCALE_RATIO,
)


def _topology(triangles):
    def vertex_key(point):
        return tuple(
            round(float(value), 6)
            for value in point
        )

    def edge_key(first, second):
        return tuple(
            sorted(
                (
                    vertex_key(first),
                    vertex_key(second),
                )
            )
        )

    counts = Counter()

    for first, second, third in triangles:
        counts[edge_key(first, second)] += 1
        counts[edge_key(second, third)] += 1
        counts[edge_key(third, first)] += 1

    return {
        "open_edges": sum(
            count == 1
            for count in counts.values()
        ),
        "non_manifold_edges": sum(
            count > 2
            for count in counts.values()
        ),
    }


def test_real_galata_bridge_adds_two_manifold_road_approaches():
    result = AtlasFoundationFirstEngine.generate_city_stl(
        pbf_path=PBF_PATH,
        bbox=BBOX,
        output_path="/tmp/galata_road_approach_test.stl",
        target_size_mm=PRODUCT_SIZE_MM,
        bed_width_mm=256,
        bed_depth_mm=256,
        margin_mm=15,
        max_buildings=0,
        min_points=4,
        max_points=300,
        z_scale=SCALE_RATIO,
        terrain_provider_name="srtm",
        terrain_smoothing_passes=0,
        strict_input_quality=False,
        nature_provider_names=(),
        fixed_xy_scale=SCALE_RATIO,
        use_fixed_xy_scale=True,
        debug=False,
    )

    bridge = next(
        mesh
        for mesh in result["mesh_groups"]["landmarks"]
        if mesh.get("landmark_id") == 280961352
    )

    approaches = bridge["road_approaches"]

    assert len(approaches) == 2

    for approach in approaches:
        topology = _topology(
            approach["triangles"]
        )

        assert topology["open_edges"] == 0
        assert topology["non_manifold_edges"] == 0

        assert 0.25 < approach["length_mm"] < 2.50
        assert approach["source_distance_mm"] < 2.50
        assert approach["road_mesh_index"] >= 0

        start_first, start_second = (
            approach["start_edge"]
        )
        target_first, target_second = (
            approach["target_edge"]
        )

        start_width = (
            (
                start_second[0]
                - start_first[0]
            ) ** 2
            + (
                start_second[1]
                - start_first[1]
            ) ** 2
        ) ** 0.5

        target_width = (
            (
                target_second[0]
                - target_first[0]
            ) ** 2
            + (
                target_second[1]
                - target_first[1]
            ) ** 2
        ) ** 0.5

        assert abs(
            target_width - start_width
        ) < 1e-9
