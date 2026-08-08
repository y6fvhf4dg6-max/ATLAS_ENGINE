from CORE.atlas_tree_row_layout_resolver import (
    AtlasTreeRowLayoutResolver,
)


def test_layout_resolver_builds_deterministic_plan_for_strong_row():
    row_profile = {
        "source_id": 123,
        "semantic_role": "tree_row",
        "representation_mode": "ordered_row",
        "source_geometry": (
            (50.0000, 7.0000),
            (50.0001, 7.0000),
            (50.0002, 7.0000),
            (50.0003, 7.0000),
        ),
        "length_m": 33.396,
        "evidence_quality": "strong",
        "product_spacing": {
            "action": "preserve",
            "source_spacing_m": 5.0,
            "scaled_spacing_mm": 0.909090909,
            "minimum_printable_mm": 0.4,
            "resolved_spacing_mm": 0.909090909,
            "scale_factor": 1.0,
            "evidence_source": "explicit_tree_spacing",
        },
    }

    result = AtlasTreeRowLayoutResolver.resolve(
        row_profile=row_profile,
        scale_ratio=5500.0,
    )

    assert result["source_id"] == 123
    assert result["status"] == "resolved"
    assert result["tree_count"] >= 2
    assert result["resolved_spacing_mm"] > 0.0
    assert result["source_geometry"] == row_profile["source_geometry"]


def test_layout_resolver_skips_weak_row():
    result = AtlasTreeRowLayoutResolver.resolve(
        row_profile={
            "source_id": 124,
            "semantic_role": "tree_row",
            "representation_mode": "ordered_row",
            "source_geometry": (
                (50.0000, 7.0000),
                (50.0001, 7.0000),
            ),
            "length_m": 11.132,
            "evidence_quality": "weak",
            "product_spacing": None,
        },
        scale_ratio=5500.0,
    )

    assert result["status"] == "skipped"
    assert result["reason"] == "weak_evidence"
    assert result["tree_count"] == 0


def test_layout_resolver_places_points_along_source_polyline():
    row_profile = {
        "source_id": 500,
        "semantic_role": "tree_row",
        "representation_mode": "ordered_row",
        "source_geometry": (
            (50.0000, 7.0000),
            (50.0001, 7.0000),
            (50.0002, 7.0000),
            (50.0003, 7.0000),
        ),
        "length_m": 33.396,
        "evidence_quality": "strong",
        "product_spacing": {
            "action": "preserve",
            "source_spacing_m": 5.0,
            "scaled_spacing_mm": 0.909090909,
            "minimum_printable_mm": 0.4,
            "resolved_spacing_mm": 0.909090909,
            "scale_factor": 1.0,
            "evidence_source": "explicit_tree_spacing",
        },
    }

    result = AtlasTreeRowLayoutResolver.resolve(
        row_profile=row_profile,
        scale_ratio=5500.0,
    )

    points = result["placement_points"]

    assert len(points) == result["tree_count"]
    assert points[0] == row_profile["source_geometry"][0]
    assert points[-1] == row_profile["source_geometry"][-1]

    assert all(
        points[index][0] <= points[index + 1][0]
        for index in range(len(points) - 1)
    )


def test_layout_resolver_is_deterministic():
    row_profile = {
        "source_id": 501,
        "semantic_role": "tree_row",
        "representation_mode": "ordered_row",
        "source_geometry": (
            (50.0000, 7.0000),
            (50.0001, 7.0001),
            (50.0002, 7.0002),
        ),
        "length_m": 26.436,
        "evidence_quality": "strong",
        "product_spacing": {
            "action": "preserve",
            "source_spacing_m": 5.0,
            "scaled_spacing_mm": 0.909090909,
            "minimum_printable_mm": 0.4,
            "resolved_spacing_mm": 0.909090909,
            "scale_factor": 1.0,
            "evidence_source": "explicit_tree_spacing",
        },
    }

    first = AtlasTreeRowLayoutResolver.resolve(
        row_profile=row_profile,
        scale_ratio=5500.0,
    )
    second = AtlasTreeRowLayoutResolver.resolve(
        row_profile=row_profile,
        scale_ratio=5500.0,
    )

    assert first["placement_points"] == second["placement_points"]


def test_layout_points_follow_bent_source_polyline():
    row_profile = {
        "source_id": 600,
        "semantic_role": "tree_row",
        "representation_mode": "ordered_row",
        "source_geometry": (
            (50.0000, 7.0000),
            (50.0001, 7.0000),
            (50.0001, 7.0001),
        ),
        "length_m": 18.0,
        "evidence_quality": "strong",
        "product_spacing": {
            "action": "preserve",
            "source_spacing_m": 4.0,
            "scaled_spacing_mm": 0.727272727,
            "minimum_printable_mm": 0.4,
            "resolved_spacing_mm": 0.727272727,
            "scale_factor": 1.0,
            "evidence_source": "explicit_tree_spacing",
        },
    }

    result = AtlasTreeRowLayoutResolver.resolve(
        row_profile=row_profile,
        scale_ratio=5500.0,
    )

    points = result["placement_points"]

    assert points[0] == row_profile["source_geometry"][0]
    assert points[-1] == row_profile["source_geometry"][-1]

    for lat, lon in points:
        on_first_segment = (
            abs(lon - 7.0000) < 1e-12
            and 50.0000 <= lat <= 50.0001
        )
        on_second_segment = (
            abs(lat - 50.0001) < 1e-12
            and 7.0000 <= lon <= 7.0001
        )

        assert on_first_segment or on_second_segment


def test_layout_interpolation_handles_zero_length_segments():
    points = AtlasTreeRowLayoutResolver._interpolate_polyline(
        (
            (50.0000, 7.0000),
            (50.0000, 7.0000),
            (50.0002, 7.0000),
        ),
        4,
    )

    assert len(points) == 4
    assert points[0] == (50.0000, 7.0000)
    assert points[-1] == (50.0002, 7.0000)


def test_layout_preserves_large_source_gap_without_filling_it():
    row_profile = {
        "source_id": 600,
        "semantic_role": "tree_row",
        "representation_mode": "ordered_row",
        "source_geometry": (
            (50.00000, 7.00000),
            (50.00005, 7.00000),
            (50.00010, 7.00000),
            (50.00040, 7.00000),
            (50.00045, 7.00000),
        ),
        "length_m": 50.0,
        "evidence_quality": "strong",
        "product_spacing": {
            "action": "fallback",
            "resolved_spacing_mm": 1.5,
        },
        "source_gaps": {
            "count": 1,
            "segment_indexes": (2,),
            "maximum_gap_m": 33.396,
        },
    }

    result = AtlasTreeRowLayoutResolver.resolve(
        row_profile=row_profile,
        scale_ratio=5500.0,
    )

    assert result["preserved_gap_segment_indexes"] == (2,)

    member_sources = result["member_source_segments"]

    assert 2 not in member_sources
