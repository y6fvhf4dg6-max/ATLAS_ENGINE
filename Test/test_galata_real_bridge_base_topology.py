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


def _edge_key(first, second):
    def vertex_key(point):
        return tuple(
            round(float(value), 6)
            for value in point
        )

    return tuple(
        sorted(
            (
                vertex_key(first),
                vertex_key(second),
            )
        )
    )


def _topology(triangles):
    counts = Counter()

    for first, second, third in triangles:
        counts[_edge_key(first, second)] += 1
        counts[_edge_key(second, third)] += 1
        counts[_edge_key(third, first)] += 1

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


def test_real_galata_base_deck_is_closed_and_manifold():
    result = AtlasFoundationFirstEngine.generate_city_stl(
        pbf_path=PBF_PATH,
        bbox=BBOX,
        output_path="/tmp/galata_real_base_topology_test.stl",
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

    support_triangle_count = sum(
        len(support["triangles"])
        for support in bridge.get("supports", ())
    )
    parapet_triangle_count = sum(
        len(parapet["triangles"])
        for parapet in bridge.get("parapets", ())
    )

    component_triangle_count = (
        support_triangle_count
        + parapet_triangle_count
    )

    assert component_triangle_count > 0

    base_triangles = bridge["triangles"][
        :-component_triangle_count
    ]

    topology = _topology(base_triangles)

    assert topology["open_edges"] == 0
    assert topology["non_manifold_edges"] == 0
