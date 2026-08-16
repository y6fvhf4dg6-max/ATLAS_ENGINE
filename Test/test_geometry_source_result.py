from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_geometry_source_result import (
    AtlasGeometrySourceResult,
)


def test_geometry_source_result_is_provider_independent_immutable_and_normalized():
    anchors = {
        " Origin ": (0, 0, 0),
        "Top Center": (5, 2.5, 2),
    }
    geometry = (
        "synthetic_triangle_mesh",
        (
            (0.0, 0.0, 0.0),
            (10.0, 0.0, 0.0),
            (0.0, 5.0, 2.0),
        ),
    )

    result = AtlasGeometrySourceResult(
        normalized_geometry=geometry,
        local_bounds=(
            (0, 0, 0),
            (10, 5, 2),
        ),
        anchors=anchors,
        confidence=0.9,
        provenance=" Synthetic Fixture ",
        supported_projection_modes=(
            " Flat Plane ",
            "Cylindrical Surface",
        ),
    )

    assert result.normalized_geometry == geometry
    assert result.local_bounds == (
        (0.0, 0.0, 0.0),
        (10.0, 5.0, 2.0),
    )
    assert dict(result.anchors) == {
        "origin": (0.0, 0.0, 0.0),
        "top_center": (5.0, 2.5, 2.0),
    }
    assert result.confidence == 0.9
    assert result.provenance == "Synthetic Fixture"
    assert result.supported_projection_modes == (
        "flat_plane",
        "cylindrical_surface",
    )

    anchors[" Origin "] = (99, 99, 99)

    assert result.anchors["origin"] == (
        0.0,
        0.0,
        0.0,
    )

    with pytest.raises(FrozenInstanceError):
        result.confidence = 0.5


def test_geometry_source_result_isolated_from_mutable_geometry_input():
    geometry = {
        "vertices": [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        "faces": [[0, 1, 2]],
    }

    result = AtlasGeometrySourceResult(
        normalized_geometry=geometry,
        local_bounds=((0, 0, 0), (1, 1, 0)),
        anchors={"origin": (0, 0, 0)},
        confidence=1.0,
        provenance="fixture",
        supported_projection_modes=("flat_plane",),
    )

    geometry["vertices"][0][0] = 99.0
    geometry["faces"].append([2, 1, 0])

    assert result.normalized_geometry["vertices"][0][0] == 0.0
    assert result.normalized_geometry["faces"] == [[0, 1, 2]]


@pytest.mark.parametrize(
    "local_bounds",
    (
        ((1, 0, 0), (0, 1, 1)),
        ((0, 2, 0), (1, 1, 1)),
        ((0, 0, 3), (1, 1, 2)),
    ),
)
def test_geometry_source_result_rejects_reversed_local_bounds(
    local_bounds,
):
    with pytest.raises(ValueError, match="local_bounds"):
        AtlasGeometrySourceResult(
            normalized_geometry=("fixture",),
            local_bounds=local_bounds,
            anchors={"origin": (0, 0, 0)},
            confidence=1.0,
            provenance="fixture",
            supported_projection_modes=("flat_plane",),
        )


def test_geometry_source_result_requires_supported_projection_mode():
    result = AtlasGeometrySourceResult(
        normalized_geometry=("fixture",),
        local_bounds=((0, 0, 0), (1, 1, 1)),
        anchors={"origin": (0, 0, 0)},
        confidence=1.0,
        provenance="fixture",
        supported_projection_modes=(
            "flat_plane",
            "cylindrical_surface",
        ),
    )

    assert result.require_projection_mode(
        " Flat Plane "
    ) == "flat_plane"

    with pytest.raises(
        ValueError,
        match="unsupported projection mode",
    ):
        result.require_projection_mode(
            "dome_surface"
        )


@pytest.mark.parametrize(
    "local_bounds",
    (
        ((0, 0), (1, 1, 1)),
        ((0, 0, 0), (1, 1, float("nan"))),
        "invalid",
    ),
)
def test_geometry_source_result_rejects_invalid_local_bounds(
    local_bounds,
):
    with pytest.raises(ValueError, match="local_bounds"):
        AtlasGeometrySourceResult(
            normalized_geometry=("fixture",),
            local_bounds=local_bounds,
            anchors={"origin": (0, 0, 0)},
            confidence=1.0,
            provenance="fixture",
            supported_projection_modes=("flat_plane",),
        )


def test_geometry_source_result_rejects_duplicate_normalized_anchor_names():
    with pytest.raises(
        ValueError,
        match="anchor names must be unique",
    ):
        AtlasGeometrySourceResult(
            normalized_geometry=("fixture",),
            local_bounds=((0, 0, 0), (1, 1, 1)),
            anchors={
                "Top Center": (0, 0, 0),
                " top   center ": (1, 1, 1),
            },
            confidence=1.0,
            provenance="fixture",
            supported_projection_modes=("flat_plane",),
        )


@pytest.mark.parametrize(
    "confidence",
    (
        -0.01,
        1.01,
        float("nan"),
        float("inf"),
        True,
    ),
)
def test_geometry_source_result_rejects_invalid_confidence(
    confidence,
):
    with pytest.raises(ValueError, match="confidence"):
        AtlasGeometrySourceResult(
            normalized_geometry=("fixture",),
            local_bounds=((0, 0, 0), (1, 1, 1)),
            anchors={"origin": (0, 0, 0)},
            confidence=confidence,
            provenance="fixture",
            supported_projection_modes=("flat_plane",),
        )


@pytest.mark.parametrize(
    "provenance",
    (
        "",
        "   ",
        None,
    ),
)
def test_geometry_source_result_rejects_invalid_provenance(
    provenance,
):
    with pytest.raises(ValueError, match="provenance"):
        AtlasGeometrySourceResult(
            normalized_geometry=("fixture",),
            local_bounds=((0, 0, 0), (1, 1, 1)),
            anchors={"origin": (0, 0, 0)},
            confidence=1.0,
            provenance=provenance,
            supported_projection_modes=("flat_plane",),
        )


@pytest.mark.parametrize(
    "projection_modes",
    (
        (),
        "flat_plane",
        ("Flat Plane", " flat   plane "),
    ),
)
def test_geometry_source_result_rejects_invalid_projection_mode_sets(
    projection_modes,
):
    with pytest.raises(
        ValueError,
        match="supported_projection_modes",
    ):
        AtlasGeometrySourceResult(
            normalized_geometry=("fixture",),
            local_bounds=((0, 0, 0), (1, 1, 1)),
            anchors={"origin": (0, 0, 0)},
            confidence=1.0,
            provenance="fixture",
            supported_projection_modes=projection_modes,
        )
