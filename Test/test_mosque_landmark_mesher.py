from collections import Counter

import pytest

from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_mosque_landmark_builder import (
    AtlasMosqueLandmarkBuilder,
)
from CORE.atlas_mosque_landmark_mesher import (
    AtlasMosqueLandmarkMesher,
)
from CORE.atlas_mosque_landmark_profile import (
    AtlasMosqueLandmarkProfile,
)


def _geometry():
    landmark = AtlasLandmark(
        id=1201,
        landmark_type=AtlasLandmarkType.MOSQUE,
        geometry=(
            (0.0, 0.0),
            (24.0, 0.0),
            (24.0, 36.0),
            (0.0, 36.0),
        ),
        tags={
            "building": "mosque",
            "religion": "muslim",
            "height": "27",
            "atlas:worship_grammar": (
                "single_dome_single_minaret"
            ),
        },
        source="OSM",
    )

    return AtlasMosqueLandmarkBuilder.build(
        landmark=landmark,
        profile=AtlasMosqueLandmarkProfile(
            scale_ratio=3000.0,
            nozzle_diameter_mm=0.4,
        ),
    )


def _topology(triangles):
    counts = Counter()

    def point_key(point):
        return tuple(
            round(float(value), 8)
            for value in point
        )

    for first, second, third in triangles:
        for point_a, point_b in (
            (first, second),
            (second, third),
            (third, first),
        ):
            edge = tuple(
                sorted(
                    (
                        point_key(point_a),
                        point_key(point_b),
                    )
                )
            )
            counts[edge] += 1

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


def test_mesher_builds_premium_single_dome_single_minaret():
    mesh = AtlasMosqueLandmarkMesher.build(
        _geometry()
    )

    assert mesh["type"] == "mosque_landmark"
    assert mesh["worship_profile"] == "mosque"
    assert mesh["worship_grammar"] == (
        "single_dome_single_minaret"
    )
    assert mesh["special_architecture_applied"] is True
    assert mesh["uses_real_footprint"] is True

    assert len(mesh["prayer_hall_meshes"]) == 1
    assert len(mesh["dome_drum_meshes"]) == 1
    assert len(mesh["dome_meshes"]) == 1
    assert len(mesh["minaret_meshes"]) == 1
    assert len(mesh["minaret_balcony_meshes"]) == 1
    assert len(mesh["minaret_cap_meshes"]) == 1

    assert len(mesh["triangles"]) > 0


def test_prayer_hall_preserves_real_footprint():
    geometry = _geometry()

    mesh = AtlasMosqueLandmarkMesher.build(
        geometry
    )

    prayer_hall = mesh["prayer_hall_meshes"][0]

    assert prayer_hall["uses_real_footprint"] is True
    assert prayer_hall["footprint"] == geometry.footprint


def test_dome_is_centered_over_prayer_hall():
    mesh = AtlasMosqueLandmarkMesher.build(
        _geometry()
    )

    dome = mesh["dome_meshes"][0]
    drum = mesh["dome_drum_meshes"][0]

    assert dome["center_x"] == pytest.approx(
        12.0
    )
    assert dome["center_y"] == pytest.approx(
        18.0
    )
    assert drum["center_x"] == pytest.approx(
        dome["center_x"]
    )
    assert drum["center_y"] == pytest.approx(
        dome["center_y"]
    )


def test_minaret_is_offset_from_main_dome():
    mesh = AtlasMosqueLandmarkMesher.build(
        _geometry()
    )

    dome = mesh["dome_meshes"][0]
    minaret = mesh["minaret_meshes"][0]

    assert (
        minaret["center_x"],
        minaret["center_y"],
    ) != (
        dome["center_x"],
        dome["center_y"],
    )

    assert minaret["top_z"] > (
        mesh["prayer_hall_meshes"][0]["top_z"]
    )


def test_each_component_shell_is_closed_and_manifold():
    mesh = AtlasMosqueLandmarkMesher.build(
        _geometry()
    )

    component_groups = (
        mesh["prayer_hall_meshes"],
        mesh["dome_drum_meshes"],
        mesh["dome_meshes"],
        mesh["minaret_meshes"],
        mesh["minaret_balcony_meshes"],
        mesh["minaret_cap_meshes"],
    )

    for component_group in component_groups:
        for component in component_group:
            topology = _topology(
                component["triangles"]
            )

            assert topology["open_edges"] == 0
            assert topology["non_manifold_edges"] == 0


def test_mesher_rejects_wrong_geometry_type():
    with pytest.raises(
        TypeError,
        match="AtlasMosqueLandmarkGeometry",
    ):
        AtlasMosqueLandmarkMesher.build(
            object()
        )
