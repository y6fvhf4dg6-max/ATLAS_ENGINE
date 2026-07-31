from collections import Counter

from CORE.atlas_church_landmark_builder import (
    AtlasChurchLandmarkBuilder,
)
from CORE.atlas_church_landmark_mesher import (
    AtlasChurchLandmarkMesher,
)
from CORE.atlas_church_landmark_profile import (
    AtlasChurchLandmarkProfile,
)
from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_type import AtlasLandmarkType


def _landmark(
    *,
    landmark_type=AtlasLandmarkType.CHURCH,
):
    return AtlasLandmark(
        id=601,
        landmark_type=landmark_type,
        geometry=(
            (0.0, 0.0),
            (20.0, 0.0),
            (20.0, 40.0),
            (0.0, 40.0),
        ),
        tags={},
        source="OSM",
    )


def _topology(triangles):
    counts = Counter()

    def key(point):
        return tuple(round(float(value), 8) for value in point)

    for first, second, third in triangles:
        for a, b in (
            (first, second),
            (second, third),
            (third, first),
        ):
            counts[tuple(sorted((key(a), key(b))))] += 1

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


def test_mesher_builds_closed_church_mesh():
    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    assert mesh["type"] == "church_landmark"
    assert mesh["landmark_id"] == 601
    assert mesh["landmark_class"] == "church"
    assert len(mesh["triangles"]) > 0

    topology = _topology(
        mesh["triangles"]
    )

    assert topology["open_edges"] == 0
    assert topology["non_manifold_edges"] == 0


def test_cathedral_mesh_contains_twin_tower_components():
    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(
            landmark_type=AtlasLandmarkType.CATHEDRAL,
        ),
        profile=AtlasChurchLandmarkProfile(
            landmark_class="cathedral",
            tower_count=2,
        ),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    assert mesh["landmark_class"] == "cathedral"
    assert len(mesh["tower_meshes"]) == 2
    assert len(mesh["spire_meshes"]) == 2


def test_mesher_preserves_component_batches():
    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    assert len(mesh["nave_meshes"]) == 1
    assert len(mesh["transept_meshes"]) == 1
    assert len(mesh["apse_meshes"]) == 1
    assert len(mesh["tower_meshes"]) == 1
    assert len(mesh["spire_meshes"]) == 1
    assert len(mesh["roof_meshes"]) == 4


def test_mesher_rejects_wrong_geometry_type():
    try:
        AtlasChurchLandmarkMesher.build(
            object()
        )
    except TypeError as exc:
        assert "AtlasChurchLandmarkGeometry" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid geometry type to be rejected"
        )
