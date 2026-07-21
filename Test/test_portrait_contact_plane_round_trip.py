import numpy as np
import pytest

from CORE.atlas_neutral_parametric_face_surface_builder import (
    AtlasNeutralParametricFaceSurfaceBuilder,
)
from CORE.atlas_parametric_face_depth_deformer import (
    AtlasParametricFaceDepthDeformer,
)
from CORE.atlas_parametric_face_depth_profile import (
    AtlasParametricFaceDepthProfile,
)
from CORE.atlas_parametric_face_shaded_preview_renderer import (
    AtlasParametricFaceShadedPreviewRenderer,
)
from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)
from CORE.atlas_parametric_face_surface_validity_analyzer import (
    AtlasParametricFaceSurfaceValidityAnalyzer,
)
from CORE.atlas_portrait_contact_distance_relief_mapper import (
    AtlasPortraitContactDistanceReliefMapper,
)
from CORE.atlas_portrait_contact_plane_projector import (
    AtlasPortraitContactPlaneProjector,
)


def _simple_surface():
    return AtlasParametricFaceSurface(
        x_coordinates=[
            [-1.0, 0.0, 1.0],
            [-1.0, 0.0, 1.0],
        ],
        y_coordinates=[
            [-0.5, -0.5, -0.5],
            [0.5, 0.5, 0.5],
        ],
        z_coordinates=[
            [0.0, 0.4, 0.0],
            [0.1, 0.8, 0.1],
        ],
    )


def _production_baseline_surface():
    neutral_surface = (
        AtlasNeutralParametricFaceSurfaceBuilder.build(
            row_count=101,
            column_count=101,
        )
    )

    depth_profile = AtlasParametricFaceDepthProfile(
        name="contact-plane-round-trip",
        brow_projection=0.026,
        eye_socket_depth=0.035,
        cheek_projection=0.028,
        nose_bridge_projection=0.0,
        nose_tip_projection=0.0,
        nose_wing_projection=0.0,
        upper_lip_projection=0.0,
        lower_lip_projection=0.0,
        philtrum_depth=0.0,
        labiomental_fold_depth=0.0,
        chin_projection=0.0,
    )

    return AtlasParametricFaceDepthDeformer.deform(
        neutral_surface,
        depth_profile=depth_profile,
    )


def _round_trip(surface):
    projection = (
        AtlasPortraitContactPlaneProjector.project(
            surface,
        )
    )

    mapping = (
        AtlasPortraitContactDistanceReliefMapper.map(
            projection,
        )
    )

    reconstructed_surface = AtlasParametricFaceSurface(
        x_coordinates=surface.x_coordinates,
        y_coordinates=surface.y_coordinates,
        z_coordinates=mapping["relief_height"],
    )

    return (
        projection,
        mapping,
        reconstructed_surface,
    )


def test_round_trip_recovers_simple_surface_z_coordinates():
    surface = _simple_surface()

    (
        projection,
        mapping,
        reconstructed_surface,
    ) = _round_trip(
        surface,
    )

    assert projection.contact_plane_z == pytest.approx(
        surface.maximum_z,
    )

    assert mapping["relief_height"] == pytest.approx(
        surface.z_coordinates,
        abs=1.0e-15,
    )

    assert reconstructed_surface.z_coordinates == pytest.approx(
        surface.z_coordinates,
        abs=1.0e-15,
    )


def test_round_trip_recovers_production_baseline_z_coordinates():
    surface = _production_baseline_surface()

    (
        _projection,
        mapping,
        reconstructed_surface,
    ) = _round_trip(
        surface,
    )

    assert mapping["relief_height"] == pytest.approx(
        surface.z_coordinates,
        abs=1.0e-15,
    )

    assert reconstructed_surface.z_coordinates == pytest.approx(
        surface.z_coordinates,
        abs=1.0e-15,
    )


def test_round_trip_preserves_contact_point_as_surface_maximum():
    surface = _production_baseline_surface()

    (
        projection,
        mapping,
        reconstructed_surface,
    ) = _round_trip(
        surface,
    )

    assert mapping["relief_height"][
        projection.contact_index
    ] == pytest.approx(
        surface.maximum_z,
        abs=1.0e-15,
    )

    assert reconstructed_surface.maximum_z == pytest.approx(
        surface.maximum_z,
        abs=1.0e-15,
    )


def test_round_trip_preserves_surface_validity():
    surface = _production_baseline_surface()

    (
        _projection,
        _mapping,
        reconstructed_surface,
    ) = _round_trip(
        surface,
    )

    source_validity = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            surface,
        )
    )

    reconstructed_validity = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            reconstructed_surface,
        )
    )

    assert source_validity.is_safe
    assert reconstructed_validity.is_safe

    assert (
        reconstructed_validity.folded_cell_count
        == source_validity.folded_cell_count
    )
    assert (
        reconstructed_validity.inverted_normal_count
        == source_validity.inverted_normal_count
    )
    assert (
        reconstructed_validity.minimum_signed_cell_area
        == pytest.approx(
            source_validity.minimum_signed_cell_area,
            abs=1.0e-18,
        )
    )
    assert (
        reconstructed_validity.minimum_normal_z
        == pytest.approx(
            source_validity.minimum_normal_z,
            abs=1.0e-15,
        )
    )


def test_round_trip_preserves_shaded_preview():
    surface = _production_baseline_surface()

    (
        _projection,
        _mapping,
        reconstructed_surface,
    ) = _round_trip(
        surface,
    )

    source_preview = (
        AtlasParametricFaceShadedPreviewRenderer.render(
            surface,
        )
    )

    reconstructed_preview = (
        AtlasParametricFaceShadedPreviewRenderer.render(
            reconstructed_surface,
        )
    )

    assert np.array_equal(
        reconstructed_preview.preview,
        source_preview.preview,
    )

    assert reconstructed_preview.shading == pytest.approx(
        source_preview.shading,
        abs=5.0e-15,
    )


def test_round_trip_is_deterministic():
    surface = _production_baseline_surface()

    first = _round_trip(
        surface,
    )
    second = _round_trip(
        surface,
    )

    first_projection = first[0]
    second_projection = second[0]

    first_mapping = first[1]
    second_mapping = second[1]

    assert (
        first_projection.contact_index
        == second_projection.contact_index
    )

    assert first_projection.distance_to_plane == pytest.approx(
        second_projection.distance_to_plane,
        abs=1.0e-15,
    )

    assert first_mapping["relief_height"] == pytest.approx(
        second_mapping["relief_height"],
        abs=1.0e-15,
    )
