from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import pytest

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.providers.portrait.atlas_portrait_flame_canonical_model_loader import (
    AtlasPortraitFlameCanonicalModelLoader,
)


def _source_mapping() -> dict:
    vertex_count = 4

    shapedirs = np.zeros(
        (
            vertex_count,
            3,
            3,
        ),
        dtype=np.float64,
    )

    return {
        "v_template": np.array(
            [
                [-1.0, 1.0, 0.0],
                [1.0, 1.0, 0.0],
                [-1.0, -1.0, 0.0],
                [1.0, -1.0, 0.0],
            ],
            dtype=np.float64,
        ),
        "f": np.array(
            [
                [0, 2, 1],
                [1, 2, 3],
            ],
            dtype=np.int64,
        ),
        "shapedirs": shapedirs,
        "posedirs": np.zeros(
            (
                vertex_count * 3,
                3,
            ),
            dtype=np.float64,
        ),
        "J_regressor": np.array(
            [
                [0.25, 0.25, 0.25, 0.25],
                [0.50, 0.50, 0.00, 0.00],
            ],
            dtype=np.float64,
        ),
        "weights": np.array(
            [
                [1.0, 0.0],
                [1.0, 0.0],
                [0.5, 0.5],
                [0.5, 0.5],
            ],
            dtype=np.float64,
        ),
        "kintree_table": np.array(
            [
                [-1, 0],
                [0, 1],
            ],
            dtype=np.int64,
        ),
    }


def _load(
    path: Path,
):
    return (
        AtlasPortraitFlameCanonicalModelLoader
        .load(
            path,
            identity_parameter_count=2,
            expression_parameter_count=1,
            model_version="synthetic-file-v1",
        )
    )


def test_loader_reads_npz(
    tmp_path,
):
    path = (
        tmp_path
        / "model.npz"
    )

    np.savez(
        path,
        **_source_mapping(),
    )

    model = _load(
        path
    )

    assert isinstance(
        model,
        AtlasPortraitFlameCanonicalModel,
    )
    assert model.vertex_count == 4
    assert model.triangle_count == 2
    assert model.metadata[
        "source_format"
    ] == "npz"


def test_loader_reads_pickle(
    tmp_path,
):
    path = (
        tmp_path
        / "model.pkl"
    )

    with path.open(
        "wb",
    ) as stream:
        pickle.dump(
            _source_mapping(),
            stream,
        )

    model = _load(
        path
    )

    assert model.vertex_count == 4
    assert model.metadata[
        "source_format"
    ] == "pickle"


def test_loader_accepts_pickle_extension(
    tmp_path,
):
    path = (
        tmp_path
        / "model.pickle"
    )

    with path.open(
        "wb",
    ) as stream:
        pickle.dump(
            _source_mapping(),
            stream,
        )

    model = _load(
        path
    )

    assert model.joint_count == 2


def test_loader_accepts_string_path(
    tmp_path,
):
    path = (
        tmp_path
        / "model.npz"
    )

    np.savez(
        path,
        **_source_mapping(),
    )

    model = (
        AtlasPortraitFlameCanonicalModelLoader
        .load(
            str(
                path
            ),
            identity_parameter_count=2,
            expression_parameter_count=1,
            model_version="synthetic-file-v1",
        )
    )

    assert model.vertex_count == 4


def test_loader_rejects_missing_file(
    tmp_path,
):
    with pytest.raises(
        FileNotFoundError,
    ):
        _load(
            tmp_path
            / "missing.npz"
        )


@pytest.mark.parametrize(
    "suffix",
    [
        ".json",
        ".txt",
        ".bin",
    ],
)
def test_loader_rejects_unsupported_extension(
    tmp_path,
    suffix,
):
    path = (
        tmp_path
        / f"model{suffix}"
    )
    path.write_bytes(
        b"invalid"
    )

    with pytest.raises(
        ValueError,
        match="extension",
    ):
        _load(
            path
        )


def test_loader_rejects_invalid_npz(
    tmp_path,
):
    path = (
        tmp_path
        / "model.npz"
    )
    path.write_bytes(
        b"not-an-npz"
    )

    with pytest.raises(
        ValueError,
        match="NPZ",
    ):
        _load(
            path
        )


def test_loader_rejects_invalid_pickle(
    tmp_path,
):
    path = (
        tmp_path
        / "model.pkl"
    )
    path.write_bytes(
        b"not-a-pickle"
    )

    with pytest.raises(
        ValueError,
        match="pickle",
    ):
        _load(
            path
        )


def test_loader_rejects_non_mapping_pickle(
    tmp_path,
):
    path = (
        tmp_path
        / "model.pkl"
    )

    with path.open(
        "wb",
    ) as stream:
        pickle.dump(
            [
                "invalid",
            ],
            stream,
        )

    with pytest.raises(
        TypeError,
        match="mapping",
    ):
        _load(
            path
        )


def test_loader_preserves_model_version(
    tmp_path,
):
    path = (
        tmp_path
        / "model.npz"
    )

    np.savez(
        path,
        **_source_mapping(),
    )

    model = (
        AtlasPortraitFlameCanonicalModelLoader
        .load(
            path,
            identity_parameter_count=2,
            expression_parameter_count=1,
            model_version="flame-2023",
        )
    )

    assert model.metadata[
        "model_version"
    ] == "flame-2023"
