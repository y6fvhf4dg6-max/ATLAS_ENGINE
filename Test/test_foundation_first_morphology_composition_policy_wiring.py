from pathlib import Path


def _source():
    return Path(
        "CORE/atlas_foundation_first_engine.py"
    ).read_text()


def test_generate_city_imports_morphology_composition_policy():
    source = _source()

    assert (
        "AtlasMorphologyCompositionPolicy"
        in source
    )


def test_generate_city_resolves_morphology_composition_policy():
    source = _source()

    assert (
        "morphology_composition_policy"
        in source
    )

    assert (
        "AtlasMorphologyCompositionPolicy.resolve"
        in source
    )


def test_generate_city_uses_effective_scene_morphology_for_policy():
    source = _source()

    assert (
        "morphology=effective_scene_morphology"
        in source
    )


def test_generate_city_passes_scene_evidence_to_policy():
    source = _source()

    assert (
        "scene_evidence=scene_morphology_evidence"
        in source
    )


def test_generate_city_returns_morphology_composition_policy():
    source = _source()

    assert (
        '"morphology_composition_policy"'
        in source
    )


def test_generate_city_passes_morphology_policy_to_city_composition_lod():
    source = _source()

    assert (
        "composition_policy=("
        in source
    )

    resolver_index = source.index(
        "AtlasCityCompositionLoDResolver"
    )

    assert (
        "morphology_composition_policy"
        in source[resolver_index:]
    )
