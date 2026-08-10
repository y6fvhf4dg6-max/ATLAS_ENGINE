from pathlib import Path


SOURCE = Path(
    "CORE/atlas_foundation_first_engine.py"
).read_text()


def test_foundation_first_uses_context_resolver_with_profiles():
    assert (
        "AtlasBuildingHeightProductContextResolver"
        in SOURCE
    )
    assert ".resolve_with_profiles(" in SOURCE


def test_foundation_first_extracts_context_and_block_profiles():
    assert '"context_by_source_id"' in SOURCE
    assert '"block_profiles"' in SOURCE


def test_foundation_first_passes_real_block_profiles_to_morphology_evidence():
    assert "block_profiles=()" not in SOURCE

    assert (
        "block_profiles=block_profiles"
        in SOURCE
        or "block_profiles=(" in SOURCE
    )
