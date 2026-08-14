import pytest

from CORE.atlas_tree_row_resolver import (
    AtlasTreeRowResolver,
)
from CORE.atlas_tree_foundation_builder import (
    AtlasTreeFoundationBuilder,
)


def test_resolver_builds_profile_from_source_tree_row_geometry():
    source = {
        "id": 123,
        "tree_type": "tree_row",
        "geometry": [
            (50.0000, 7.0000),
            (50.0001, 7.0000),
            (50.0002, 7.0000),
        ],
        "tags": {
            "natural": "tree_row",
        },
    }

    result = AtlasTreeRowResolver.resolve(source)

    assert result["source_id"] == 123
    assert result["semantic_role"] == "tree_row"
    assert result["representation_mode"] == "ordered_row"

    assert result["source_geometry"] == (
        (50.0000, 7.0000),
        (50.0001, 7.0000),
        (50.0002, 7.0000),
    )

    assert result["segment_count"] == 2
    assert result["length_m"] == pytest.approx(
        22.264,
        rel=0.02,
    )

    assert result["direction"]["north_m"] > 0.0
    assert abs(result["direction"]["east_m"]) < 0.05


def test_resolver_rejects_non_tree_row_source():
    with pytest.raises(
        ValueError,
        match="source tree_type must be tree_row",
    ):
        AtlasTreeRowResolver.resolve(
            {
                "id": 1,
                "tree_type": "tree",
                "geometry": [
                    (50.0, 7.0),
                    (50.1, 7.1),
                ],
            }
        )


def test_resolver_rejects_degenerate_geometry():
    with pytest.raises(
        ValueError,
        match="tree_row geometry must contain at least two points",
    ):
        AtlasTreeRowResolver.resolve(
            {
                "id": 1,
                "tree_type": "tree_row",
                "geometry": [
                    (50.0, 7.0),
                ],
            }
        )


def test_resolver_does_not_mutate_source():
    source = {
        "id": 5,
        "tree_type": "tree_row",
        "geometry": [
            (50.0, 7.0),
            (50.0001, 7.0001),
        ],
        "tags": {
            "natural": "tree_row",
        },
    }

    before = {
        "id": 5,
        "tree_type": "tree_row",
        "geometry": [
            (50.0, 7.0),
            (50.0001, 7.0001),
        ],
        "tags": {
            "natural": "tree_row",
        },
    }

    AtlasTreeRowResolver.resolve(source)

    assert source == before


def test_resolver_reports_segment_spacing_statistics():
    source = {
        "id": 123,
        "tree_type": "tree_row",
        "geometry": [
            (50.0000, 7.0000),
            (50.0001, 7.0000),
            (50.0002, 7.0000),
            (50.0003, 7.0000),
        ],
    }

    result = AtlasTreeRowResolver.resolve(source)

    spacing = result["source_segment_spacing"]

    assert spacing["count"] == 3
    assert spacing["minimum_m"] == pytest.approx(
        11.132,
        rel=0.02,
    )
    assert spacing["maximum_m"] == pytest.approx(
        11.132,
        rel=0.02,
    )
    assert spacing["mean_m"] == pytest.approx(
        11.132,
        rel=0.02,
    )
    assert spacing["regularity_ratio"] == pytest.approx(
        1.0,
        abs=1e-6,
    )


def test_resolver_marks_regular_straight_row_as_strong_evidence():
    source = {
        "id": 200,
        "tree_type": "tree_row",
        "geometry": [
            (50.0000, 7.0000),
            (50.0001, 7.0000),
            (50.0002, 7.0000),
            (50.0003, 7.0000),
        ],
    }

    result = AtlasTreeRowResolver.resolve(source)

    assert result["evidence_quality"] == "strong"
    assert result["direction_consistency_ratio"] == pytest.approx(
        1.0,
        abs=1e-6,
    )


def test_resolver_marks_reversing_row_as_weak_evidence():
    source = {
        "id": 201,
        "tree_type": "tree_row",
        "geometry": [
            (50.0000, 7.0000),
            (50.0001, 7.0000),
            (50.0002, 7.0000),
            (50.0001, 7.0000),
        ],
    }

    result = AtlasTreeRowResolver.resolve(source)

    assert result["evidence_quality"] == "weak"
    assert result["direction_consistency_ratio"] < 0.90


def test_resolver_marks_reversing_row_as_weak_evidence():
    source = {
        "id": 201,
        "tree_type": "tree_row",
        "geometry": [
            (50.0000, 7.0000),
            (50.0001, 7.0000),
            (50.0002, 7.0000),
            (50.0001, 7.0000),
        ],
    }

    result = AtlasTreeRowResolver.resolve(source)

    assert result["evidence_quality"] == "weak"
    assert result["direction_consistency_ratio"] < 0.90


def test_resolver_uses_explicit_tree_spacing_evidence_for_product_spacing():
    source = {
        "id": 300,
        "tree_type": "tree_row",
        "geometry": [
            (50.0000, 7.0000),
            (50.0001, 7.0000),
            (50.0002, 7.0000),
        ],
        "tree_spacing_m": 5.0,
    }

    result = AtlasTreeRowResolver.resolve(
        source,
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    spacing = result["product_spacing"]

    assert spacing["evidence_source"] == "explicit_tree_spacing"
    assert spacing["source_spacing_m"] == pytest.approx(5.0)
    assert spacing["action"] == "enlarge"
    canonical = (
        AtlasTreeFoundationBuilder
        ._canonical_tree_dimensions()
    )

    assert spacing["resolved_spacing_mm"] == pytest.approx(
        canonical["crown_diameter_mm"] + 0.40
    )


def test_resolver_does_not_infer_tree_spacing_from_geometry_vertices():
    source = {
        "id": 301,
        "tree_type": "tree_row",
        "geometry": [
            (50.0000, 7.0000),
            (50.0001, 7.0000),
            (50.0002, 7.0000),
        ],
    }

    result = AtlasTreeRowResolver.resolve(
        source,
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    spacing = result["product_spacing"]

    assert spacing["evidence_source"] == "product_readability"
    assert spacing["action"] == "fallback"
    canonical = (
        AtlasTreeFoundationBuilder
        ._canonical_tree_dimensions()
    )

    assert spacing["resolved_spacing_mm"] == pytest.approx(
        canonical["crown_diameter_mm"] + 0.40
    )
    assert "source_spacing_m" not in spacing


@pytest.mark.parametrize(
    "tree_spacing_m",
    (
        0.0,
        -1.0,
        "invalid",
    ),
)
def test_resolver_rejects_invalid_explicit_tree_spacing(
    tree_spacing_m,
):
    source = {
        "id": 302,
        "tree_type": "tree_row",
        "geometry": [
            (50.0000, 7.0000),
            (50.0001, 7.0000),
            (50.0002, 7.0000),
        ],
        "tree_spacing_m": tree_spacing_m,
    }

    with pytest.raises(
        (TypeError, ValueError),
    ):
        AtlasTreeRowResolver.resolve(
            source,
            scale_ratio=5500.0,
            nozzle_diameter_mm=0.4,
        )


def test_explicit_osm_tree_row_remains_strong_with_irregular_way_vertices():
    source = {
        "id": 400,
        "tree_type": "tree_row",
        "geometry": [
            (50.00000, 7.00000),
            (50.00002, 7.00000),
            (50.00018, 7.00000),
            (50.00030, 7.00000),
        ],
        "tags": {
            "natural": "tree_row",
        },
    }

    result = AtlasTreeRowResolver.resolve(source)

    assert (
        result["source_segment_spacing"]["regularity_ratio"]
        < 0.75
    )
    assert result["direction_consistency_ratio"] == pytest.approx(
        1.0,
        abs=1e-6,
    )
    assert result["evidence_quality"] == "strong"


def test_resolver_uses_product_readability_fallback_when_spacing_is_missing():
    source = {
        "id": 401,
        "tree_type": "tree_row",
        "geometry": [
            (50.0000, 7.0000),
            (50.0001, 7.0000),
            (50.0002, 7.0000),
        ],
        "tags": {
            "natural": "tree_row",
        },
    }

    result = AtlasTreeRowResolver.resolve(
        source,
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    spacing = result["product_spacing"]

    assert spacing["action"] == "fallback"
    assert spacing["evidence_source"] == "product_readability"
    canonical = (
        AtlasTreeFoundationBuilder
        ._canonical_tree_dimensions()
    )

    assert spacing["resolved_spacing_mm"] == pytest.approx(
        canonical["crown_diameter_mm"] + 0.40
    )


def test_explicit_two_point_osm_tree_row_is_strong_evidence():
    source = {
        "id": 500,
        "tree_type": "tree_row",
        "geometry": [
            (50.0000, 7.0000),
            (50.0003, 7.0000),
        ],
        "tags": {
            "natural": "tree_row",
        },
    }

    result = AtlasTreeRowResolver.resolve(
        source,
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    assert result["segment_count"] == 1
    assert result["direction_consistency_ratio"] == pytest.approx(
        1.0,
        abs=1e-6,
    )
    assert result["evidence_quality"] == "strong"
    assert result["product_spacing"]["action"] == "fallback"


def test_resolver_reports_large_source_geometry_gaps():
    source = {
        "id": 600,
        "tree_type": "tree_row",
        "geometry": [
            (50.00000, 7.00000),
            (50.00005, 7.00000),
            (50.00010, 7.00000),
            (50.00040, 7.00000),
            (50.00045, 7.00000),
        ],
        "tags": {
            "natural": "tree_row",
        },
    }

    result = AtlasTreeRowResolver.resolve(source)

    gaps = result["source_gaps"]

    assert gaps["count"] == 1
    assert gaps["segment_indexes"] == (2,)
    assert gaps["maximum_gap_m"] > 20.0
