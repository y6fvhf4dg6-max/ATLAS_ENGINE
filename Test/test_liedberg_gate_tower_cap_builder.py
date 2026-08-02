from CORE.atlas_liedberg_gate_tower_cap_builder import (
    AtlasLiedbergGateTowerCapBuilder,
)


def make_gate_tower_mesh():
    return {
        "type": "liedberg_gate_tower",
        "source_id": 143975871,
        "architectural_role": "gate_tower_body",
        "top_z": 18.994895128498246,
        "top": [
            (99.20, 81.20, 18.994895128498246),
            (101.70, 82.30, 18.994895128498246),
            (101.00, 84.50, 18.994895128498246),
            (98.50, 83.40, 18.994895128498246),
        ],
    }


def test_liedberg_gate_tower_receives_polygonal_transition_cap():
    tower_mesh = make_gate_tower_mesh()

    result = AtlasLiedbergGateTowerCapBuilder.build(
        gate_tower_mesh=tower_mesh,
    )

    assert result is not None
    assert result["type"] == "liedberg_gate_tower_cap"
    assert result["source_id"] == 143975871
    assert result["architectural_role"] == "gate_tower_transition_cap"
    assert result["base_z"] == tower_mesh["top_z"]
    assert result["top_z"] > result["base_z"]
    assert result["top_width_ratio"] < 1.0
    assert len(result["bottom"]) == 4
    assert len(result["top"]) == 4
    assert len(result["triangles"]) == 12


def test_unrelated_tower_does_not_receive_liedberg_cap():
    tower_mesh = make_gate_tower_mesh()
    tower_mesh["source_id"] = 999

    result = AtlasLiedbergGateTowerCapBuilder.build(
        gate_tower_mesh=tower_mesh,
    )

    assert result is None
