import dataclasses

import pytest

from CORE.atlas_triangle_file_count_analyzer import (
    AtlasTriangleFileCountAnalysis,
    AtlasTriangleFileCountAnalyzer,
)


def test_analysis_is_immutable():
    result = AtlasTriangleFileCountAnalyzer.analyze(
        triangle_count=100_000,
        maximum_triangle_count=200_000,
        file_count=4,
        maximum_file_count=5,
    )

    assert isinstance(result, AtlasTriangleFileCountAnalysis)

    with pytest.raises(dataclasses.FrozenInstanceError):
        result.triangle_count = 120_000


def test_zero_counts_are_valid():
    result = AtlasTriangleFileCountAnalyzer.analyze(
        triangle_count=0,
        maximum_triangle_count=0,
        file_count=0,
        maximum_file_count=0,
    )

    assert result.excess_triangle_count == 0
    assert result.excess_file_count == 0
    assert result.is_triangle_count_excessive is False
    assert result.is_file_count_excessive is False
    assert result.has_excessive_counts is False


def test_counts_below_thresholds_are_safe():
    result = AtlasTriangleFileCountAnalyzer.analyze(
        triangle_count=199_999,
        maximum_triangle_count=200_000,
        file_count=4,
        maximum_file_count=5,
    )

    assert result.excess_triangle_count == 0
    assert result.excess_file_count == 0
    assert result.has_excessive_counts is False


def test_counts_equal_to_thresholds_are_safe():
    result = AtlasTriangleFileCountAnalyzer.analyze(
        triangle_count=200_000,
        maximum_triangle_count=200_000,
        file_count=5,
        maximum_file_count=5,
    )

    assert result.is_triangle_count_excessive is False
    assert result.is_file_count_excessive is False
    assert result.has_excessive_counts is False


def test_triangle_count_above_threshold_is_reported_independently():
    result = AtlasTriangleFileCountAnalyzer.analyze(
        triangle_count=250_000,
        maximum_triangle_count=200_000,
        file_count=4,
        maximum_file_count=5,
    )

    assert result.excess_triangle_count == 50_000
    assert result.excess_file_count == 0
    assert result.is_triangle_count_excessive is True
    assert result.is_file_count_excessive is False
    assert result.has_excessive_counts is True


def test_file_count_above_threshold_is_reported_independently():
    result = AtlasTriangleFileCountAnalyzer.analyze(
        triangle_count=150_000,
        maximum_triangle_count=200_000,
        file_count=7,
        maximum_file_count=5,
    )

    assert result.excess_triangle_count == 0
    assert result.excess_file_count == 2
    assert result.is_triangle_count_excessive is False
    assert result.is_file_count_excessive is True
    assert result.has_excessive_counts is True


def test_both_excesses_are_reported():
    result = AtlasTriangleFileCountAnalyzer.analyze(
        triangle_count=260_000,
        maximum_triangle_count=200_000,
        file_count=8,
        maximum_file_count=5,
    )

    assert result.triangle_count == 260_000
    assert result.maximum_triangle_count == 200_000
    assert result.file_count == 8
    assert result.maximum_file_count == 5
    assert result.excess_triangle_count == 60_000
    assert result.excess_file_count == 3
    assert result.is_triangle_count_excessive is True
    assert result.is_file_count_excessive is True
    assert result.has_excessive_counts is True


@pytest.mark.parametrize(
    "field_name",
    (
        "triangle_count",
        "maximum_triangle_count",
        "file_count",
        "maximum_file_count",
    ),
)
@pytest.mark.parametrize(
    "invalid_value",
    (
        -1,
        1.0,
        "1",
        None,
        True,
        False,
    ),
)
def test_rejects_invalid_count_values(
    field_name,
    invalid_value,
):
    kwargs = {
        "triangle_count": 100_000,
        "maximum_triangle_count": 200_000,
        "file_count": 4,
        "maximum_file_count": 5,
    }
    kwargs[field_name] = invalid_value

    with pytest.raises((TypeError, ValueError)):
        AtlasTriangleFileCountAnalyzer.analyze(**kwargs)
