from collections import Counter

from CORE.atlas_church_footprint_resolver import (
    AtlasChurchFootprintResolver,
)
from CORE.atlas_church_roof_mesher import (
    AtlasChurchRoofMesher,
)
from CORE.atlas_church_roof_profile_system import (
    AtlasChurchRoofProfileSystem,
)


def _frame():
    return AtlasChurchFootprintResolver.resolve(
        (
            (0.0, 0.0),
            (30.0, 0.0),
            (30.0, 60.0),
            (0.0, 60.0),
        )
    )


def _profile():
    return AtlasChurchRoofProfileSystem.resolve(
        longitudinal_span=60.0,
        lateral_span=30.0,
        wall_height=20.0,
    )


def _topology(triangles):
    counts = Counter()

    def key(point):
        return tuple(
            round(float(value), 8)
            for value in point
        )

    for first, second, third in triangles:
        for a, b in (
            (first, second),
            (second, third),
            (third, first),
        ):
            edge = tuple(
                sorted(
                    (
                        key(a),
                        key(b),
                    )
                )
            )
            counts[edge] += 1

    return {
        "open_edges": sum(
            count == 1
            for count in counts.values()
        ),
        "non_manifold_edges": sum(
            count > 2
            for count in counts.values()
        ),
    }


def test_roof_mesher_builds_all_architectural_sections():
    mesh = AtlasChurchRoofMesher.build(
        frame=_frame(),
        profile=_profile(),
    )

    assert mesh["type"] == "church_roof_system"

    assert tuple(
        section["section_type"]
        for section in mesh["sections"]
    ) == (
        "outer_aisle_left",
        "outer_aisle_right",
        "main_nave",
        "transept",
        "apse",
    )


def test_main_nave_roof_has_real_sloped_faces_and_ridge():
    mesh = AtlasChurchRoofMesher.build(
        frame=_frame(),
        profile=_profile(),
    )

    main_nave = next(
        section
        for section in mesh["sections"]
        if section["section_type"] == "main_nave"
    )

    assert main_nave["roof_shape"] == "gable"
    assert len(main_nave["ridge"]) == 2
    assert len(main_nave["triangles"]) == 8

    ridge_z_values = {
        point[2]
        for point in main_nave["ridge"]
    }

    assert ridge_z_values == {
        main_nave["ridge_z"]
    }
    assert main_nave["ridge_z"] > main_nave["eave_z"]


def test_outer_aisle_roofs_are_lower_and_separate():
    mesh = AtlasChurchRoofMesher.build(
        frame=_frame(),
        profile=_profile(),
    )

    left = next(
        section
        for section in mesh["sections"]
        if section["section_type"]
        == "outer_aisle_left"
    )
    right = next(
        section
        for section in mesh["sections"]
        if section["section_type"]
        == "outer_aisle_right"
    )
    main = next(
        section
        for section in mesh["sections"]
        if section["section_type"] == "main_nave"
    )

    assert left["ridge_z"] < main["eave_z"]
    assert right["ridge_z"] < main["eave_z"]

    assert left["center_lateral"] < 0.0
    assert right["center_lateral"] > 0.0


def test_transept_ridge_is_perpendicular_to_main_nave_ridge():
    mesh = AtlasChurchRoofMesher.build(
        frame=_frame(),
        profile=_profile(),
    )

    main = next(
        section
        for section in mesh["sections"]
        if section["section_type"] == "main_nave"
    )
    transept = next(
        section
        for section in mesh["sections"]
        if section["section_type"] == "transept"
    )

    main_start, main_end = main["ridge"]
    transept_start, transept_end = transept["ridge"]

    main_vector = (
        main_end[0] - main_start[0],
        main_end[1] - main_start[1],
    )
    transept_vector = (
        transept_end[0] - transept_start[0],
        transept_end[1] - transept_start[1],
    )

    dot_product = (
        main_vector[0] * transept_vector[0]
        + main_vector[1] * transept_vector[1]
    )

    assert abs(dot_product) <= 1e-8


def test_apse_roof_is_closed_polygon_pyramid():
    mesh = AtlasChurchRoofMesher.build(
        frame=_frame(),
        profile=_profile(),
    )

    apse = next(
        section
        for section in mesh["sections"]
        if section["section_type"] == "apse"
    )

    assert apse["roof_shape"] == "polygon_pyramid"
    assert len(apse["base_ring"]) == 8
    assert len(apse["triangles"]) == 14

    topology = _topology(
        apse["triangles"]
    )

    assert topology["open_edges"] == 0
    assert topology["non_manifold_edges"] == 0


def test_each_roof_section_is_closed_and_manifold():
    mesh = AtlasChurchRoofMesher.build(
        frame=_frame(),
        profile=_profile(),
    )

    for section in mesh["sections"]:
        topology = _topology(
            section["triangles"]
        )

        assert topology["open_edges"] == 0
        assert topology["non_manifold_edges"] == 0
