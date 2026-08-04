from __future__ import annotations

import pytest

from CORE.atlas_bridge_builder import (
    AtlasBridgeBuilder,
)
from CORE.atlas_castle_geometry_classifier import (
    AtlasCastleGeometryClassifier,
)
from CORE.atlas_church_landmark_builder import (
    AtlasChurchLandmarkBuilder,
)
from CORE.atlas_church_landmark_profile import (
    AtlasChurchLandmarkProfile,
)
from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_mosque_landmark_builder import (
    AtlasMosqueLandmarkBuilder,
)
from CORE.atlas_mosque_landmark_profile import (
    AtlasMosqueLandmarkProfile,
)
from CORE.atlas_semantic_architecture_adapter_resolver import (
    AtlasSemanticArchitectureAdapterResolver,
)
from CORE.atlas_semantic_architecture_model import (
    AtlasSemanticArchitectureModel,
)


def _landmark(
    *,
    landmark_id,
    landmark_type,
    geometry,
    tags,
):
    return AtlasLandmark(
        id=landmark_id,
        landmark_type=landmark_type,
        geometry=geometry,
        tags=tags,
        source="OSM",
    )


def _church_geometry():
    landmark = _landmark(
        landmark_id=1801,
        landmark_type=AtlasLandmarkType.CHURCH,
        geometry=(
            (0.0, 0.0),
            (20.0, 0.0),
            (20.0, 40.0),
            (0.0, 40.0),
        ),
        tags={
            "building": "church",
        },
    )

    return AtlasChurchLandmarkBuilder.build(
        landmark=landmark,
        profile=AtlasChurchLandmarkProfile(),
    )


def _mosque_geometry():
    landmark = _landmark(
        landmark_id=1802,
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
        },
    )

    return AtlasMosqueLandmarkBuilder.build(
        landmark=landmark,
        profile=AtlasMosqueLandmarkProfile(),
    )


def _bridge_geometry():
    landmark = _landmark(
        landmark_id=1803,
        landmark_type=AtlasLandmarkType.BRIDGE,
        geometry=(
            (0.0, 0.0),
            (30.0, 0.0),
        ),
        tags={
            "bridge": "yes",
        },
    )

    return AtlasBridgeBuilder.build(
        landmark
    )


def _castle_classification():
    closed_geometry = [
        (48.0000, 12.0000),
        (48.0000, 12.0010),
        (48.0010, 12.0010),
        (48.0010, 12.0000),
        (48.0000, 12.0000),
    ]

    return AtlasCastleGeometryClassifier.classify(
        castles=[
            {
                "id": 1804,
                "geometry_type": "relation",
                "outer_geometries": [
                    closed_geometry,
                ],
                "tags": {
                    "historic": "castle",
                },
            },
        ],
        castle_walls=[],
        debug=False,
    )


@pytest.mark.parametrize(
    "source,expected_family",
    [
        (_church_geometry, "church"),
        (_mosque_geometry, "mosque"),
        (_bridge_geometry, "bridge"),
        (_castle_classification, "castle"),
    ],
)
def test_resolver_dispatches_supported_architecture_sources(
    source,
    expected_family,
):
    model = AtlasSemanticArchitectureAdapterResolver.resolve(
        source()
    )

    assert isinstance(
        model,
        AtlasSemanticArchitectureModel,
    )
    assert model.landmark_family == expected_family


def test_resolver_rejects_arbitrary_dict():
    with pytest.raises(
        TypeError,
        match="unsupported semantic architecture source",
    ):
        AtlasSemanticArchitectureAdapterResolver.resolve(
            {
                "unrelated": (),
            }
        )


def test_resolver_rejects_unsupported_object():
    with pytest.raises(
        TypeError,
        match="unsupported semantic architecture source",
    ):
        AtlasSemanticArchitectureAdapterResolver.resolve(
            object()
        )
