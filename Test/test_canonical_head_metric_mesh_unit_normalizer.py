import numpy as np
import pytest

from CORE.atlas_canonical_head_metric_mesh_unit_normalizer import (
    AtlasCanonicalHeadMetricMeshUnitNormalizer,
)


def test_converts_metre_vertices_to_millimetres():
    source = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [0.125, -0.050, 1.712],
        ],
        dtype=np.float64,
    )

    result = AtlasCanonicalHeadMetricMeshUnitNormalizer.normalize(
        vertices=source,
        source_units="m",
    )

    assert result.source_units == "m"
    assert result.target_units == "mm"
    assert result.scale_factor == pytest.approx(1000.0)
    np.testing.assert_allclose(
        result.vertices_mm,
        np.asarray(
            [
                [0.0, 0.0, 0.0],
                [125.0, -50.0, 1712.0],
            ],
            dtype=np.float64,
        ),
    )


@pytest.mark.parametrize(
    ("source_units", "expected_scale"),
    (
        ("mm", 1.0),
        ("cm", 10.0),
        ("m", 1000.0),
    ),
)
def test_supports_explicit_metric_source_units(
    source_units,
    expected_scale,
):
    result = AtlasCanonicalHeadMetricMeshUnitNormalizer.normalize(
        vertices=np.asarray([[1.0, 2.0, 3.0]]),
        source_units=source_units,
    )

    assert result.scale_factor == pytest.approx(expected_scale)


def test_does_not_mutate_source_vertices():
    source = np.asarray([[1.0, 2.0, 3.0]])
    before = source.copy()

    AtlasCanonicalHeadMetricMeshUnitNormalizer.normalize(
        vertices=source,
        source_units="cm",
    )

    assert np.array_equal(source, before)


def test_rejects_unsupported_source_units():
    with pytest.raises(ValueError, match="source_units"):
        AtlasCanonicalHeadMetricMeshUnitNormalizer.normalize(
            vertices=np.asarray([[1.0, 2.0, 3.0]]),
            source_units="px",
        )


def test_rejects_nonfinite_vertices():
    with pytest.raises(ValueError, match="vertices"):
        AtlasCanonicalHeadMetricMeshUnitNormalizer.normalize(
            vertices=np.asarray([[1.0, np.nan, 3.0]]),
            source_units="m",
        )
