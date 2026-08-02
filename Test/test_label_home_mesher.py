from CORE.atlas_label_home_mesher import AtlasLabelHomeMesher


def test_home_symbol_builds_printable_closed_geometry():
    mesh = AtlasLabelHomeMesher.build(
        width_mm=7.0,
        height_mm=6.0,
        depth_mm=0.6,
    )

    assert mesh["type"] == "label_home"
    assert mesh["width_mm"] == 7.0
    assert mesh["height_mm"] == 6.0
    assert mesh["depth_mm"] == 0.6
    assert mesh["triangles"]


def test_home_symbol_rejects_non_positive_dimensions():
    for field_name in (
        "width_mm",
        "height_mm",
        "depth_mm",
    ):
        values = {
            "width_mm": 7.0,
            "height_mm": 6.0,
            "depth_mm": 0.6,
        }
        values[field_name] = 0.0

        try:
            AtlasLabelHomeMesher.build(**values)
        except ValueError:
            pass
        else:
            raise AssertionError(
                f"{field_name} should reject zero"
            )
