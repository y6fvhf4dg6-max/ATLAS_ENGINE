from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from CORE.atlas_parametric_face_geometry import (
    AtlasParametricFaceGeometry,
)
from CORE.providers.portrait.atlas_portrait_reconstruction_adapter import (
    AtlasPortraitReconstructionAdapter,
)
from Test.fixtures.portrait.parametric_face_geometry_fixture import (
    load_parametric_face_geometry_fixture,
)


class FixtureReconstructionAdapter(
    AtlasPortraitReconstructionAdapter,
):
    ADAPTER_ID = "fixture-flame-adapter"
    PROVIDER_ID = "fixture-flame-provider"
    MODEL_FAMILY = "flame"
    MODEL_VERSION = "2023-open"
    SUPPORTED_INPUT_VIEWS = (
        "single_image",
        "multi_view",
    )

    def adapt(
        self,
        provider_payload,
        *,
        input_view="single_image",
    ) -> AtlasParametricFaceGeometry:
        self.validate_input_view(
            input_view,
        )

        if not isinstance(
            provider_payload,
            dict,
        ):
            raise TypeError(
                "provider_payload must be a mapping."
            )

        source = load_parametric_face_geometry_fixture()

        geometry = AtlasParametricFaceGeometry(
            vertices=provider_payload.get(
                "vertices",
                source.vertices,
            ),
            triangle_faces=provider_payload.get(
                "triangle_faces",
                source.triangle_faces,
            ),
            surface_normals=provider_payload.get(
                "surface_normals",
                source.surface_normals,
            ),
            uv_coordinates=provider_payload.get(
                "uv_coordinates",
                source.uv_coordinates,
            ),
            semantic_vertex_regions=provider_payload.get(
                "semantic_vertex_regions",
                source.semantic_vertex_regions,
            ),
            landmark_vertex_map=provider_payload.get(
                "landmark_vertex_map",
                source.landmark_vertex_map,
            ),
            identity_parameters=provider_payload.get(
                "identity_parameters",
                source.identity_parameters,
            ),
            expression_parameters=provider_payload.get(
                "expression_parameters",
                source.expression_parameters,
            ),
            pose_parameters=provider_payload.get(
                "pose_parameters",
                source.pose_parameters,
            ),
            confidence=provider_payload.get(
                "confidence",
                source.confidence,
            ),
            visibility=provider_payload.get(
                "visibility",
                source.visibility,
            ),
            metadata={
                "adapter_id": self.adapter_id,
                "input_view": input_view,
                "model_family": self.model_family,
                "model_version": self.model_version,
                "provider_id": self.provider_id,
                "synthetic": True,
            },
        )

        return self.validate_geometry(
            geometry,
        )


def _adapter():
    return FixtureReconstructionAdapter()


def test_adapter_base_is_abstract():
    with pytest.raises(
        TypeError,
    ):
        AtlasPortraitReconstructionAdapter()


def test_adapter_exposes_normalized_identity():
    adapter = _adapter()

    assert adapter.adapter_id == "fixture-flame-adapter"
    assert adapter.provider_id == "fixture-flame-provider"
    assert adapter.model_family == "flame"
    assert adapter.model_version == "2023-open"


def test_adapter_identity_is_read_only():
    adapter = _adapter()

    with pytest.raises(
        AttributeError,
    ):
        adapter.adapter_id = "changed"


def test_adapter_reports_supported_input_views():
    adapter = _adapter()

    assert adapter.supported_input_views == (
        "multi_view",
        "single_image",
    )


@pytest.mark.parametrize(
    "input_view",
    [
        "single_image",
        "multi_view",
    ],
)
def test_adapter_accepts_supported_input_view(
    input_view,
):
    adapter = _adapter()

    assert adapter.validate_input_view(
        input_view,
    ) == input_view


@pytest.mark.parametrize(
    "input_view",
    [
        "",
        " ",
        "video",
        None,
        123,
    ],
)
def test_adapter_rejects_invalid_input_view(
    input_view,
):
    adapter = _adapter()

    with pytest.raises(
        ValueError,
        match="input_view",
    ):
        adapter.validate_input_view(
            input_view,
        )


def test_adapter_converts_payload_to_canonical_geometry():
    adapter = _adapter()

    geometry = adapter.adapt(
        {},
        input_view="single_image",
    )

    assert isinstance(
        geometry,
        AtlasParametricFaceGeometry,
    )

    assert geometry.vertex_count == 25
    assert geometry.triangle_count == 32


def test_adapter_preserves_provider_payload_arrays():
    adapter = _adapter()
    source = load_parametric_face_geometry_fixture()

    vertices = np.array(
        source.vertices,
        copy=True,
    )
    vertices[:, 2] *= 0.75

    geometry = adapter.adapt(
        {
            "vertices": vertices,
        }
    )

    assert np.allclose(
        geometry.vertices,
        vertices,
    )


def test_adapter_records_deterministic_metadata():
    adapter = _adapter()

    geometry = adapter.adapt(
        {},
        input_view="single_image",
    )

    assert geometry.metadata == {
        "adapter_id": "fixture-flame-adapter",
        "input_view": "single_image",
        "model_family": "flame",
        "model_version": "2023-open",
        "provider_id": "fixture-flame-provider",
        "synthetic": True,
    }


def test_adapter_validates_its_geometry():
    adapter = _adapter()

    geometry = adapter.adapt(
        {},
    )

    assert adapter.validate_geometry(
        geometry,
    ) is geometry


def test_adapter_rejects_non_geometry_output():
    adapter = _adapter()

    with pytest.raises(
        TypeError,
        match="AtlasParametricFaceGeometry",
    ):
        adapter.validate_geometry(
            {
                "vertices": [],
            }
        )


@pytest.mark.parametrize(
    (
        "metadata_key",
        "invalid_value",
    ),
    [
        (
            "adapter_id",
            "another-adapter",
        ),
        (
            "provider_id",
            "another-provider",
        ),
        (
            "model_family",
            "another-model",
        ),
        (
            "model_version",
            "another-version",
        ),
    ],
)
def test_adapter_rejects_foreign_geometry_metadata(
    metadata_key,
    invalid_value,
):
    adapter = _adapter()
    geometry = adapter.adapt(
        {},
    )

    metadata = dict(
        geometry.metadata,
    )
    metadata[
        metadata_key
    ] = invalid_value

    foreign_geometry = replace(
        geometry,
        metadata=metadata,
    )

    with pytest.raises(
        ValueError,
        match=metadata_key,
    ):
        adapter.validate_geometry(
            foreign_geometry,
        )


def test_adapter_rejects_missing_identity_metadata():
    adapter = _adapter()
    geometry = adapter.adapt(
        {},
    )

    metadata = dict(
        geometry.metadata,
    )
    del metadata[
        "provider_id"
    ]

    incomplete_geometry = replace(
        geometry,
        metadata=metadata,
    )

    with pytest.raises(
        ValueError,
        match="provider_id",
    ):
        adapter.validate_geometry(
            incomplete_geometry,
        )


def test_adapter_rejects_non_mapping_payload():
    adapter = _adapter()

    with pytest.raises(
        TypeError,
        match="provider_payload",
    ):
        adapter.adapt(
            [
                "invalid",
            ]
        )


def test_adapter_output_is_deterministic():
    adapter = _adapter()

    first = adapter.adapt(
        {},
    )
    second = adapter.adapt(
        {},
    )

    assert first.to_dict() == second.to_dict()


class MissingAdapterId(
    FixtureReconstructionAdapter,
):
    ADAPTER_ID = ""


class MissingProviderId(
    FixtureReconstructionAdapter,
):
    PROVIDER_ID = ""


class MissingModelFamily(
    FixtureReconstructionAdapter,
):
    MODEL_FAMILY = ""


class MissingModelVersion(
    FixtureReconstructionAdapter,
):
    MODEL_VERSION = ""


@pytest.mark.parametrize(
    "adapter_type",
    [
        MissingAdapterId,
        MissingProviderId,
        MissingModelFamily,
        MissingModelVersion,
    ],
)
def test_adapter_requires_complete_identity(
    adapter_type,
):
    with pytest.raises(
        ValueError,
    ):
        adapter_type()


class InvalidInputViews(
    FixtureReconstructionAdapter,
):
    SUPPORTED_INPUT_VIEWS = (
        "single_image",
        "",
    )


def test_adapter_rejects_invalid_supported_input_views():
    with pytest.raises(
        ValueError,
        match="SUPPORTED_INPUT_VIEWS",
    ):
        InvalidInputViews()
