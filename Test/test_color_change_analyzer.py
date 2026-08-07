import dataclasses

import pytest

from CORE.atlas_color_change_analyzer import (
    AtlasColorChangeAnalysis,
    AtlasColorChangeAnalyzer,
)


def test_analysis_is_immutable():
    result = AtlasColorChangeAnalyzer.analyze(
        color_change_count=12,
        maximum_color_changes=20,
    )

    assert isinstance(result, AtlasColorChangeAnalysis)

    with pytest.raises(dataclasses.FrozenInstanceError):
        result.color_change_count = 15


def test_analysis_accepts_zero_color_changes():
    result = AtlasColorChangeAnalyzer.analyze(
        color_change_count=0,
        maximum_color_changes=20,
    )

    assert result.color_change_count == 0
    assert result.maximum_color_changes == 20
    assert result.excess_color_changes == 0
    assert result.is_excessive is False


def test_analysis_marks_count_below_threshold_as_safe():
    result = AtlasColorChangeAnalyzer.analyze(
        color_change_count=19,
        maximum_color_changes=20,
    )

    assert result.excess_color_changes == 0
    assert result.is_excessive is False


def test_analysis_marks_count_equal_to_threshold_as_safe():
    result = AtlasColorChangeAnalyzer.analyze(
        color_change_count=20,
        maximum_color_changes=20,
    )

    assert result.excess_color_changes == 0
    assert result.is_excessive is False


def test_analysis_reports_changes_above_threshold():
    result = AtlasColorChangeAnalyzer.analyze(
        color_change_count=60,
        maximum_color_changes=40,
    )

    assert result.color_change_count == 60
    assert result.maximum_color_changes == 40
    assert result.excess_color_changes == 20
    assert result.is_excessive is True


def test_analysis_accepts_zero_maximum_threshold():
    safe = AtlasColorChangeAnalyzer.analyze(
        color_change_count=0,
        maximum_color_changes=0,
    )
    excessive = AtlasColorChangeAnalyzer.analyze(
        color_change_count=1,
        maximum_color_changes=0,
    )

    assert safe.is_excessive is False
    assert excessive.is_excessive is True
    assert excessive.excess_color_changes == 1


@pytest.mark.parametrize(
    "color_change_count",
    [
        -1,
        1.0,
        1.5,
        "1",
        None,
        True,
        False,
    ],
)
def test_analysis_rejects_invalid_color_change_count(
    color_change_count,
):
    with pytest.raises((TypeError, ValueError)):
        AtlasColorChangeAnalyzer.analyze(
            color_change_count=color_change_count,
            maximum_color_changes=20,
        )


@pytest.mark.parametrize(
    "maximum_color_changes",
    [
        -1,
        20.0,
        20.5,
        "20",
        None,
        True,
        False,
    ],
)
def test_analysis_rejects_invalid_maximum_color_changes(
    maximum_color_changes,
):
    with pytest.raises((TypeError, ValueError)):
        AtlasColorChangeAnalyzer.analyze(
            color_change_count=10,
            maximum_color_changes=maximum_color_changes,
        )
