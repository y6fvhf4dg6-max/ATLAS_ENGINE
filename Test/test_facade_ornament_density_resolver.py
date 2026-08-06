from CORE.atlas_facade_ornament_density_resolver import (
    AtlasFacadeOrnamentCandidate,
    AtlasFacadeOrnamentDensityResolver,
)


def _candidate(
    source_index,
    priority,
    real_size_m=1.0,
):
    return AtlasFacadeOrnamentCandidate(
        source_index=source_index,
        ornament_kind="rosette",
        priority=priority,
        real_size_m=real_size_m,
    )


def test_density_levels_apply_deterministic_detail_budgets():
    candidates = tuple(
        _candidate(index, priority=10 - index)
        for index in range(10)
    )

    low = AtlasFacadeOrnamentDensityResolver.resolve(
        candidates=candidates,
        density_level="low",
        scale_ratio=1000.0,
        nozzle_diameter_mm=0.4,
    )
    medium = AtlasFacadeOrnamentDensityResolver.resolve(
        candidates=candidates,
        density_level="medium",
        scale_ratio=1000.0,
        nozzle_diameter_mm=0.4,
    )
    high = AtlasFacadeOrnamentDensityResolver.resolve(
        candidates=candidates,
        density_level="high",
        scale_ratio=1000.0,
        nozzle_diameter_mm=0.4,
    )

    assert low.selected_count == 3
    assert medium.selected_count == 6
    assert high.selected_count == 10

    assert tuple(
        item.source_index
        for item in low.selected
    ) == (0, 1, 2)


def test_physically_omitted_candidates_never_consume_budget():
    result = AtlasFacadeOrnamentDensityResolver.resolve(
        candidates=(
            _candidate(0, priority=10, real_size_m=0.01),
            _candidate(1, priority=9, real_size_m=1.0),
            _candidate(2, priority=8, real_size_m=1.0),
            _candidate(3, priority=7, real_size_m=1.0),
        ),
        density_level="low",
        scale_ratio=1000.0,
        nozzle_diameter_mm=0.4,
    )

    assert result.selected_count == 3
    assert tuple(
        item.source_index
        for item in result.selected
    ) == (1, 2, 3)

    assert tuple(
        item.source_index
        for item in result.omitted
    ) == (0,)


def test_priority_order_is_stable_for_equal_priorities():
    result = AtlasFacadeOrnamentDensityResolver.resolve(
        candidates=(
            _candidate(4, priority=5),
            _candidate(2, priority=5),
            _candidate(7, priority=8),
            _candidate(1, priority=5),
        ),
        density_level="low",
        scale_ratio=1000.0,
        nozzle_diameter_mm=0.4,
    )

    assert tuple(
        item.source_index
        for item in result.selected
    ) == (7, 4, 2)


def test_physical_detail_decision_metadata_is_preserved():
    result = AtlasFacadeOrnamentDensityResolver.resolve(
        candidates=(
            _candidate(
                0,
                priority=10,
                real_size_m=0.2,
            ),
        ),
        density_level="high",
        scale_ratio=1000.0,
        nozzle_diameter_mm=0.4,
    )

    item = result.selected[0]

    assert item.action == "enlarge"
    assert item.scaled_size_mm == 0.2
    assert item.minimum_printable_mm == 0.4
    assert item.resolved_size_mm == 0.4
    assert item.scale_factor == 2.0
