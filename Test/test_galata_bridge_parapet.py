import pytest

from CORE.atlas_landmark_foundation_builder import (
    AtlasLandmarkFoundationBuilder,
)


class FakeCoordinateEngine:
    def geometry_to_stl_mm(self, geometry):
        return [
            (
                (lon - 8.0) * 1000.0,
                (lat - 50.0) * 1000.0,
            )
            for lat, lon in geometry
        ]

    def latlon_to_local_meters(self, lat, lon):
        return (
            (lon - 8.0) * 100_000.0,
            (lat - 50.0) * 100_000.0,
        )

    def height_to_stl_mm(self, height_m):
        return float(height_m) / 5.0


class FakeTerrain:
    def sample_height(self, x, y):
        return 2.5


def _galata_bridge_landmark():
    return {
        "id": 280961352,
        "geometry_type": "way",
        "geometry": (
            (50.000, 8.000),
            (50.000, 8.080),
            (50.010, 8.080),
            (50.010, 8.000),
        ),
        "tags": {
            "man_made": "bridge",
            "name": "Galata Köprüsü",
            "wikidata": "Q81523",
        },
    }


def _build_bridge():
    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[_galata_bridge_landmark()],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=FakeTerrain(),
        debug=False,
    )

    assert len(meshes) == 1
    return meshes[0]


def test_galata_bridge_adds_two_side_parapets():
    bridge = _build_bridge()

    assert "parapets" in bridge
    assert len(bridge["parapets"]) == 2

    for parapet in bridge["parapets"]:
        assert len(parapet["bottom"]) >= 2
        assert len(parapet["top"]) == len(parapet["bottom"])
        assert len(parapet["triangles"]) > 0


def test_galata_parapets_rise_above_deck_edges():
    bridge = _build_bridge()

    deck_top_max = max(
        point[2]
        for point in bridge["top"]
    )

    for parapet in bridge["parapets"]:
        bottom_levels = [
            point[2]
            for point in parapet["bottom"]
        ]
        top_levels = [
            point[2]
            for point in parapet["top"]
        ]

        assert min(bottom_levels) >= (
            min(
                point[2]
                for point in bridge["top"]
            )
            - parapet["deck_embed_mm"]
            - 1e-12
        )
        assert min(top_levels) > min(bottom_levels)
        assert max(top_levels) > max(bottom_levels)
        assert max(top_levels) > deck_top_max


def test_galata_parapets_follow_convex_bridge_profile():
    bridge = _build_bridge()

    for parapet in bridge["parapets"]:
        top_levels = {
            round(point[2], 6)
            for point in parapet["top"]
        }

        assert len(top_levels) >= 5



def _edge_counts(triangles):
    from collections import Counter

    def vertex_key(point):
        return tuple(round(float(value), 8) for value in point)

    def edge_key(first, second):
        return tuple(sorted((vertex_key(first), vertex_key(second))))

    counts = Counter()

    for first, second, third in triangles:
        counts[edge_key(first, second)] += 1
        counts[edge_key(second, third)] += 1
        counts[edge_key(third, first)] += 1

    return counts


def test_galata_parapets_are_closed_manifold_strips():
    bridge = _build_bridge()

    for parapet in bridge["parapets"]:
        counts = _edge_counts(parapet["triangles"])

        assert all(
            count == 2
            for count in counts.values()
        )



def test_galata_parapets_do_not_cross_bridge_ends():
    bridge = _build_bridge()
    parapets = bridge["parapets"]

    assert len(parapets) == 2

    first_outer = parapets[0]["outer_bottom"]
    second_outer = parapets[1]["outer_bottom"]

    assert first_outer[0] != second_outer[0]
    assert first_outer[-1] != second_outer[-1]


def test_galata_parapets_remove_all_densified_end_segments():
    from CORE.atlas_galata_bridge_parapet_mesher import (
        AtlasGalataBridgeParapetMesher,
    )

    deck_top = (
        (0.0, 0.0, 3.7),
        (2.0, 0.0, 3.7),
        (4.0, 0.0, 3.7),
        (6.0, 0.0, 3.7),
        (8.0, 0.0, 3.7),
        (10.0, 0.0, 3.7),
        (10.0, 5.0, 3.7),
        (10.0, 10.0, 3.7),
        (8.0, 10.0, 3.7),
        (6.0, 10.0, 3.7),
        (4.0, 10.0, 3.7),
        (2.0, 10.0, 3.7),
        (0.0, 10.0, 3.7),
        (0.0, 5.0, 3.7),
    )

    frame, expected_paths = (
        AtlasGalataBridgeParapetMesher
        ._resolve_side_paths(deck_top)
    )

    parapets = AtlasGalataBridgeParapetMesher.build(
        deck_top
    )

    assert len(parapets) == 2

    for parapet, expected_path in zip(
        parapets,
        expected_paths,
    ):
        path = parapet["outer_bottom"]

        assert len(path) == len(expected_path)

        for generated, source in zip(
            path,
            expected_path,
        ):
            generated_longitudinal = (
                AtlasGalataBridgeParapetMesher
                ._longitudinal(
                    generated,
                    frame,
                )
            )
            source_longitudinal = (
                AtlasGalataBridgeParapetMesher
                ._longitudinal(
                    source,
                    frame,
                )
            )

            assert abs(
                generated_longitudinal
                - source_longitudinal
            ) < 1e-9
            assert abs(
                generated[2]
                - (
                    source[2]
                    - parapet["deck_embed_mm"]
                )
            ) < 1e-9

        for first, second in zip(path, path[1:]):
            delta_x = second[0] - first[0]
            delta_y = second[1] - first[1]

            longitudinal = abs(
                delta_x * frame["axis_x"]
                + delta_y * frame["axis_y"]
            )
            lateral = abs(
                delta_x * frame["normal_x"]
                + delta_y * frame["normal_y"]
            )

            assert longitudinal >= lateral


def test_galata_parapets_are_inset_and_embedded_into_deck():
    from CORE.atlas_galata_bridge_parapet_mesher import (
        AtlasGalataBridgeParapetMesher,
    )

    deck_top = (
        (0.0, 0.0, 3.7),
        (20.0, 0.0, 3.7),
        (20.0, 6.0, 3.7),
        (0.0, 6.0, 3.7),
    )

    frame, side_paths = (
        AtlasGalataBridgeParapetMesher
        ._resolve_side_paths(deck_top)
    )

    parapets = AtlasGalataBridgeParapetMesher.build(
        deck_top
    )

    assert len(parapets) == 2

    for parapet, source_path in zip(
        parapets,
        side_paths,
    ):
        outer_bottom = parapet["outer_bottom"]

        assert outer_bottom != source_path

        for generated, source in zip(
            outer_bottom,
            source_path,
        ):
            generated_lateral = (
                AtlasGalataBridgeParapetMesher
                ._lateral(
                    generated,
                    frame,
                )
            )
            source_lateral = (
                AtlasGalataBridgeParapetMesher
                ._lateral(
                    source,
                    frame,
                )
            )

            assert (
                abs(generated_lateral)
                < abs(source_lateral)
            )
            assert generated[2] < source[2]

        assert parapet["edge_inset_mm"] > 0.0
        assert parapet["deck_embed_mm"] > 0.0
