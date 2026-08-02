from CORE.atlas_liedberg_gate_tower_builder import (
    AtlasLiedbergGateTowerBuilder,
)


def make_schloss_mesh():
    return {
        "source_id": 143975871,
        "body_top_z": 15.994895128498246,
        "roof_top_z": 17.794895128498247,
        "multi_gable_roof_records": [
            {
                "piece_index": 0,
                "ridge_start": (
                    97.39241823486934,
                    81.35224967460525,
                    17.794895128498247,
                ),
                "ridge_end": (
                    99.02986254528227,
                    78.32242953333795,
                    17.794895128498247,
                ),
                "long_side_mm": 3.443985185527459,
                "short_side_mm": 2.7950733675117063,
            },
            {
                "piece_index": 1,
                "ridge_start": (
                    96.43524976781501,
                    83.55738761110682,
                    17.794895128498247,
                ),
                "ridge_end": (
                    99.03465201519285,
                    84.59845292616572,
                    17.794895128498247,
                ),
                "long_side_mm": 2.8001266103330598,
                "short_side_mm": 2.2937135318136415,
            },
            {
                "piece_index": 2,
                "ridge_start": (
                    101.92381673660742,
                    83.32143953179101,
                    17.794895128498247,
                ),
                "ridge_end": (
                    99.1578323979253,
                    82.09989042224464,
                    17.794895128498247,
                ),
                "long_side_mm": 3.023714865669102,
                "short_side_mm": 1.9610123713037977,
            },
        ],
    }


def test_liedberg_schloss_receives_elevated_gate_tower_body():
    mesh = make_schloss_mesh()

    result = AtlasLiedbergGateTowerBuilder.build(
        castle_mesh=mesh,
    )

    assert result is not None
    assert result["type"] == "liedberg_gate_tower"
    assert result["source_id"] == 143975871
    assert result["architectural_role"] == "gate_tower_body"
    assert result["base_z"] == mesh["body_top_z"]
    assert result["top_z"] > mesh["roof_top_z"]
    assert result["height_mm"] >= 3.0
    assert result["height_mm"] < 4.0
    assert result["width_mm"] >= 2.10
    assert result["depth_mm"] >= 2.30
    assert len(result["triangles"]) == 12
    assert len(result["bottom"]) == 4
    assert len(result["top"]) == 4


def test_other_castles_do_not_receive_liedberg_gate_tower():
    mesh = make_schloss_mesh()
    mesh["source_id"] = 999

    result = AtlasLiedbergGateTowerBuilder.build(
        castle_mesh=mesh,
    )

    assert result is None
