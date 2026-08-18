from CORE.atlas_facade_arch_band_mesher import (
    AtlasFacadeArchBandMesher,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


def test_builds_closed_manifold_arch_band_with_open_center():
    result = AtlasFacadeArchBandMesher.build(
        center_x_mm=20.0,
        bottom_z_mm=5.0,
        outer_width_mm=20.0,
        outer_height_mm=30.0,
        band_width_mm=2.0,
        depth_mm=0.8,
        front_y_mm=0.0,
        arch_segments=16,
        arch_height_ratio=0.55,
    )

    assert result["component_type"] == "facade_arch_band"

    report = AtlasMeshValidator._topology_report(
        result
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0

    triangles = result["triangles"]
    assert triangles

    # The center of the opening must remain empty:
    # no front/back triangle may cover the opening center point.
    center = (
        20.0,
        20.0,
    )

    def point_in_triangle_2d(point, triangle):
        px, pz = point
        a, b, c = triangle

        ax, az = a[0], a[2]
        bx, bz = b[0], b[2]
        cx, cz = c[0], c[2]

        denominator = (
            (bz - cz) * (ax - cx)
            + (cx - bx) * (az - cz)
        )

        if abs(denominator) <= 1e-12:
            return False

        w0 = (
            (bz - cz) * (px - cx)
            + (cx - bx) * (pz - cz)
        ) / denominator

        w1 = (
            (cz - az) * (px - cx)
            + (ax - cx) * (pz - cz)
        ) / denominator

        w2 = 1.0 - w0 - w1

        return (
            w0 >= -1e-9
            and w1 >= -1e-9
            and w2 >= -1e-9
        )

    front_back_triangles = [
        triangle
        for triangle in triangles
        if (
            abs(triangle[0][1] - triangle[1][1]) <= 1e-9
            and abs(triangle[1][1] - triangle[2][1]) <= 1e-9
        )
    ]

    assert not any(
        point_in_triangle_2d(
            center,
            triangle,
        )
        for triangle in front_back_triangles
    )
