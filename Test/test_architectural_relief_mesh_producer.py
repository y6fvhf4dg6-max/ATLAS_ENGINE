import numpy as np
import pytest

from CORE.atlas_architectural_relief_mesh_producer import (
    AtlasArchitecturalReliefMeshProducer,
)
from CORE.atlas_architectural_relief_physical_profile import (
    AtlasArchitecturalReliefPhysicalProfile,
)


def _physical_profile():
    return AtlasArchitecturalReliefPhysicalProfile(
        name="architectural-premium-v1",
        base_thickness_mm=1.0,
        relief_height_mm=2.4,
        target_sample_spacing_mm=2.0,
    )


def test_builds_mesh_from_physical_profile():
    height_map = np.array(
        [
            [0.0, 0.5, 1.0],
            [0.25, 0.75, 0.5],
        ],
        dtype=np.float64,
    )

    result = (
        AtlasArchitecturalReliefMeshProducer
        .build(
            height_map=height_map,
            width_mm=8.0,
            depth_mm=4.0,
            physical_profile=(
                _physical_profile()
            ),
        )
    )

    assert result["type"] == (
        "architectural_relief_mesh_production"
    )
    assert result["source_height_map"].shape == (
        2,
        3,
    )
    assert result["resampled_height_map"].shape == (
        3,
        5,
    )

    mesh = result["mesh"]

    assert mesh["row_count"] == 3
    assert mesh["column_count"] == 5
    assert mesh["width_mm"] == pytest.approx(
        8.0
    )
    assert mesh["depth_mm"] == pytest.approx(
        4.0
    )
    assert mesh[
        "base_thickness_mm"
    ] == pytest.approx(1.0)
    assert mesh[
        "relief_height_mm"
    ] == pytest.approx(2.4)


def test_mesh_matches_physical_triangle_plan():
    result = (
        AtlasArchitecturalReliefMeshProducer
        .build(
            height_map=np.array(
                [
                    [0.0, 1.0],
                    [1.0, 0.0],
                ],
                dtype=np.float64,
            ),
            width_mm=8.0,
            depth_mm=4.0,
            physical_profile=(
                _physical_profile()
            ),
        )
    )

    assert result["triangle_count"] == (
        result["physical_plan"][
            "triangle_count"
        ]
    )
    assert result["triangle_count"] == len(
        result["mesh"]["triangles"]
    )


def test_mesh_is_closed_and_manifold():
    result = (
        AtlasArchitecturalReliefMeshProducer
        .build(
            height_map=np.array(
                [
                    [0.0, 0.4, 1.0],
                    [0.2, 0.8, 0.3],
                    [0.0, 0.5, 0.9],
                ],
                dtype=np.float64,
            ),
            width_mm=8.0,
            depth_mm=4.0,
            physical_profile=(
                _physical_profile()
            ),
        )
    )

    topology = result["topology_report"]

    assert topology["open_edge_count"] == 0
    assert (
        topology["non_manifold_edge_count"]
        == 0
    )
    assert result["is_printable_topology"] is True


def test_preserves_normalized_height_endpoints():
    result = (
        AtlasArchitecturalReliefMeshProducer
        .build(
            height_map=np.array(
                [
                    [0.0, 1.0],
                    [0.5, 0.25],
                ],
                dtype=np.float64,
            ),
            width_mm=4.0,
            depth_mm=4.0,
            physical_profile=(
                AtlasArchitecturalReliefPhysicalProfile(
                    name="architectural",
                    base_thickness_mm=1.0,
                    relief_height_mm=2.0,
                    target_sample_spacing_mm=2.0,
                )
            ),
        )
    )

    resampled = result[
        "resampled_height_map"
    ]

    assert resampled[0, 0] == pytest.approx(
        0.0
    )
    assert resampled[0, -1] == pytest.approx(
        1.0
    )
    assert result["mesh"][
        "maximum_z"
    ] == pytest.approx(3.0)


def test_same_target_shape_returns_isolated_copy():
    height_map = np.array(
        [
            [0.0, 0.5, 1.0],
            [0.2, 0.6, 0.8],
            [0.0, 0.4, 1.0],
        ],
        dtype=np.float64,
    )

    result = (
        AtlasArchitecturalReliefMeshProducer
        .build(
            height_map=height_map,
            width_mm=4.0,
            depth_mm=4.0,
            physical_profile=(
                AtlasArchitecturalReliefPhysicalProfile(
                    name="architectural",
                    base_thickness_mm=1.0,
                    relief_height_mm=2.0,
                    target_sample_spacing_mm=2.0,
                )
            ),
        )
    )

    resampled = result[
        "resampled_height_map"
    ]

    assert np.array_equal(
        resampled,
        height_map,
    )
    assert resampled is not height_map
    assert not np.shares_memory(
        resampled,
        height_map,
    )


@pytest.mark.parametrize(
    "height_map",
    [
        [0.0, 1.0],
        [[0.0]],
        np.zeros(
            (2, 2, 2),
            dtype=np.float64,
        ),
        [
            [0.0, float("nan")],
            [0.5, 1.0],
        ],
        [
            [-0.01, 0.0],
            [0.5, 1.0],
        ],
        [
            [0.0, 1.01],
            [0.5, 1.0],
        ],
    ],
)
def test_rejects_invalid_height_maps(
    height_map,
):
    with pytest.raises(
        ValueError,
        match="height_map",
    ):
        AtlasArchitecturalReliefMeshProducer.build(
            height_map=height_map,
            width_mm=4.0,
            depth_mm=4.0,
            physical_profile=(
                _physical_profile()
            ),
        )


def test_rejects_invalid_physical_profile_type():
    with pytest.raises(
        TypeError,
        match="physical_profile",
    ):
        AtlasArchitecturalReliefMeshProducer.build(
            height_map=np.zeros(
                (2, 2),
                dtype=np.float64,
            ),
            width_mm=4.0,
            depth_mm=4.0,
            physical_profile=object(),
        )


def test_does_not_mutate_input():
    height_map = np.array(
        [
            [0.0, 0.5],
            [1.0, 0.25],
        ],
        dtype=np.float64,
    )
    original = height_map.copy()

    AtlasArchitecturalReliefMeshProducer.build(
        height_map=height_map,
        width_mm=4.0,
        depth_mm=4.0,
        physical_profile=(
            _physical_profile()
        ),
    )

    np.testing.assert_array_equal(
        height_map,
        original,
    )
