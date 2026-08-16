import pytest

from CORE.atlas_geometry_source_adapter import (
    AtlasGeometrySourceAdapter,
)
from CORE.atlas_geometry_source_result import (
    AtlasGeometrySourceResult,
)


class FixtureGeometrySourceAdapter(
    AtlasGeometrySourceAdapter,
):
    def adapt(
        self,
        source,
    ) -> AtlasGeometrySourceResult:
        return AtlasGeometrySourceResult(
            normalized_geometry={
                "source_snapshot": tuple(source),
            },
            local_bounds=(
                (0, 0, 0),
                (1, 1, 1),
            ),
            anchors={
                "origin": (0, 0, 0),
            },
            confidence=1.0,
            provenance="fixture adapter",
            supported_projection_modes=(
                "flat_plane",
                "cylindrical_surface",
            ),
        )


def test_geometry_source_adapter_base_is_abstract():
    with pytest.raises(TypeError):
        AtlasGeometrySourceAdapter()


def test_geometry_source_adapter_adapt_returns_canonical_result():
    adapter = FixtureGeometrySourceAdapter()

    result = adapter.adapt(
        source=[
            "provider",
            "payload",
        ],
    )

    assert isinstance(
        result,
        AtlasGeometrySourceResult,
    )
    assert result.normalized_geometry == {
        "source_snapshot": (
            "provider",
            "payload",
        ),
    }


def test_geometry_source_adapter_validates_canonical_result():
    adapter = FixtureGeometrySourceAdapter()

    result = adapter.adapt(
        source=["fixture"],
    )

    assert adapter.validate_result(result) is result


def test_geometry_source_adapter_rejects_noncanonical_result():
    adapter = FixtureGeometrySourceAdapter()

    with pytest.raises(
        TypeError,
        match="AtlasGeometrySourceResult",
    ):
        adapter.validate_result(
            {
                "geometry": "provider-specific",
            }
        )


def test_geometry_source_adapter_validates_requested_projection_mode():
    adapter = FixtureGeometrySourceAdapter()

    result = adapter.adapt(
        source=["fixture"],
    )

    assert adapter.validate_projection_mode(
        result,
        " Flat Plane ",
    ) == "flat_plane"

    with pytest.raises(
        ValueError,
        match="unsupported projection mode",
    ):
        adapter.validate_projection_mode(
            result,
            "dome_surface",
        )


def test_projection_validation_requires_canonical_result():
    adapter = FixtureGeometrySourceAdapter()

    with pytest.raises(
        TypeError,
        match="AtlasGeometrySourceResult",
    ):
        adapter.validate_projection_mode(
            {"geometry": "invalid"},
            "flat_plane",
        )
