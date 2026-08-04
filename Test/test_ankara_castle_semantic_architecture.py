from pathlib import Path

from CORE.atlas_castle_geometry_classifier import (
    AtlasCastleGeometryClassifier,
)
from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)
from CORE.atlas_local_osm_reader import (
    AtlasLocalOSMReader,
)
from CORE.atlas_semantic_architecture_model import (
    AtlasSemanticArchitectureModel,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PBF_PATH = (
    PROJECT_ROOT
    / "Data/OSM/ankara-kalesi-test.osm.pbf"
)

BBOX = (
    39.9351328,
    32.8582838,
    39.9521044,
    32.8780862,
)


def _ankara_castle_classification():
    data = AtlasLocalOSMReader.read(
        pbf_path=str(PBF_PATH),
        bbox=BBOX,
    )

    return AtlasCastleGeometryClassifier.classify(
        castles=data.get("castles", []),
        castle_walls=data.get(
            "castle_walls",
            [],
        ),
        debug=False,
    )


def test_foundation_engine_resolves_ankara_castle_semantic_architecture():
    model = (
        AtlasFoundationFirstEngine
        .resolve_castle_semantic_architecture(
            _ankara_castle_classification()
        )
    )

    assert isinstance(
        model,
        AtlasSemanticArchitectureModel,
    )
    assert model.landmark_family == "castle"
    assert model.grammar_name == (
        "perimeter_fortification"
    )

    assert len(
        model.components_for_role(
            "perimeter_wall"
        )
    ) == 7

    unknown_sites = model.components_for_role(
        "unknown_site"
    )

    assert len(unknown_sites) == 1
    assert unknown_sites[0].flags == (
        "unresolved",
    )


def test_foundation_engine_keeps_castle_semantics_opt_in():
    result = {
        "mode": "foundation_first",
    }

    enriched = (
        AtlasFoundationFirstEngine
        .attach_castle_semantic_architecture(
            result=result,
            castle_geometry=(
                _ankara_castle_classification()
            ),
            include=False,
        )
    )

    assert enriched is result
    assert (
        "castle_semantic_architecture"
        not in enriched
    )


def test_foundation_engine_can_attach_ankara_castle_semantics():
    result = {
        "mode": "foundation_first",
    }

    enriched = (
        AtlasFoundationFirstEngine
        .attach_castle_semantic_architecture(
            result=result,
            castle_geometry=(
                _ankara_castle_classification()
            ),
            include=True,
        )
    )

    model = enriched[
        "castle_semantic_architecture"
    ]

    assert isinstance(
        model,
        AtlasSemanticArchitectureModel,
    )
    assert model.landmark_family == "castle"
    assert model.grammar_name == (
        "perimeter_fortification"
    )
    assert len(
        model.components_for_role(
            "perimeter_wall"
        )
    ) == 7
