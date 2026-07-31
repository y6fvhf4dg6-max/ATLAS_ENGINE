from __future__ import annotations

import pytest

from CORE.atlas_physical_detail_resolver import (
    AtlasPhysicalDetailResolver,
)


def test_preserves_detail_already_above_printable_minimum():
    decision = AtlasPhysicalDetailResolver.resolve(
        real_size_m=3.0,
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
        detail_type="window",
    )

    assert decision.action == "preserve"
    assert decision.scaled_size_mm == pytest.approx(
        3.0 * 1000.0 / 5500.0
    )
    assert decision.minimum_printable_mm == pytest.approx(0.4)
    assert decision.resolved_size_mm == pytest.approx(
        decision.scaled_size_mm
    )
    assert decision.scale_factor == pytest.approx(1.0)


def test_enlarges_detail_below_printable_minimum():
    decision = AtlasPhysicalDetailResolver.resolve(
        real_size_m=1.0,
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
        detail_type="buttress",
    )

    assert decision.action == "enlarge"
    assert decision.scaled_size_mm == pytest.approx(
        1.0 * 1000.0 / 5500.0
    )
    assert decision.minimum_printable_mm == pytest.approx(0.4)
    assert decision.resolved_size_mm == pytest.approx(0.4)
    assert decision.scale_factor > 1.0


def test_omits_extremely_small_generic_detail():
    decision = AtlasPhysicalDetailResolver.resolve(
        real_size_m=0.10,
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
        detail_type="generic",
    )

    assert decision.action == "omit"
    assert decision.resolved_size_mm == pytest.approx(0.0)


@pytest.mark.parametrize(
    ("real_size_m", "scale_ratio", "nozzle_diameter_mm"),
    [
        (0.0, 5500.0, 0.4),
        (-1.0, 5500.0, 0.4),
        (1.0, 0.0, 0.4),
        (1.0, -5500.0, 0.4),
        (1.0, 5500.0, 0.0),
        (1.0, 5500.0, -0.4),
    ],
)
def test_rejects_non_positive_inputs(
    real_size_m,
    scale_ratio,
    nozzle_diameter_mm,
):
    with pytest.raises(ValueError):
        AtlasPhysicalDetailResolver.resolve(
            real_size_m=real_size_m,
            scale_ratio=scale_ratio,
            nozzle_diameter_mm=nozzle_diameter_mm,
            detail_type="generic",
        )
