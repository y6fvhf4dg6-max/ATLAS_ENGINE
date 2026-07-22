from __future__ import annotations

import pickle
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import numpy as np

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.providers.portrait.atlas_portrait_flame_canonical_model_adapter import (
    AtlasPortraitFlameCanonicalModelAdapter,
)


class AtlasPortraitFlameCanonicalModelLoader:
    """
    Loads FLAME canonical model assets from NPZ or pickle files.

    Supported extensions:

    - .npz
    - .pkl
    - .pickle

    The loader only owns file decoding and delegates all FLAME field
    normalization and canonical-model construction to
    AtlasPortraitFlameCanonicalModelAdapter.

    Pickle files must come from a trusted local source.
    """

    _NPZ_SUFFIX = ".npz"
    _PICKLE_SUFFIXES = (
        ".pkl",
        ".pickle",
    )

    @classmethod
    def load(
        cls,
        path: Any,
        *,
        identity_parameter_count: Any,
        expression_parameter_count: Any,
        model_version: Any,
    ) -> AtlasPortraitFlameCanonicalModel:
        model_path = cls._normalize_path(
            path,
        )

        if not model_path.is_file():
            raise FileNotFoundError(
                f"FLAME model file does not exist: "
                f"{model_path}"
            )

        suffix = model_path.suffix.lower()

        if suffix == cls._NPZ_SUFFIX:
            source = cls._load_npz(
                model_path,
            )
            source_format = "npz"
        elif suffix in cls._PICKLE_SUFFIXES:
            source = cls._load_pickle(
                model_path,
            )
            source_format = "pickle"
        else:
            raise ValueError(
                "Unsupported FLAME model file extension: "
                f"{suffix or '<none>'}. Expected .npz, "
                ".pkl, or .pickle."
            )

        if not isinstance(
            source,
            Mapping,
        ):
            raise TypeError(
                "Decoded FLAME model must be a mapping."
            )

        return (
            AtlasPortraitFlameCanonicalModelAdapter
            .adapt(
                source=source,
                identity_parameter_count=(
                    identity_parameter_count
                ),
                expression_parameter_count=(
                    expression_parameter_count
                ),
                model_version=model_version,
                source_format=source_format,
            )
        )

    @staticmethod
    def _normalize_path(
        value: Any,
    ) -> Path:
        if isinstance(
            value,
            Path,
        ):
            return value

        if isinstance(
            value,
            str,
        ):
            normalized = value.strip()

            if not normalized:
                raise ValueError(
                    "path must not be blank."
                )

            return Path(
                normalized,
            )

        raise TypeError(
            "path must be a string or pathlib.Path."
        )

    @staticmethod
    def _load_npz(
        path: Path,
    ) -> dict[str, Any]:
        try:
            with np.load(
                path,
                allow_pickle=False,
            ) as archive:
                return {
                    key: np.array(
                        archive[
                            key
                        ],
                        copy=True,
                    )
                    for key in archive.files
                }
        except (
            OSError,
            ValueError,
            EOFError,
        ) as exc:
            raise ValueError(
                "Unable to decode FLAME NPZ model file."
            ) from exc

    @staticmethod
    def _load_pickle(
        path: Path,
    ) -> Mapping[str, Any]:
        try:
            with path.open(
                "rb",
            ) as stream:
                payload = pickle.load(
                    stream,
                )
        except (
            OSError,
            pickle.PickleError,
            EOFError,
            AttributeError,
            ImportError,
            IndexError,
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "Unable to decode FLAME pickle model file."
            ) from exc

        if not isinstance(
            payload,
            Mapping,
        ):
            raise TypeError(
                "Decoded FLAME pickle payload must be a mapping."
            )

        return payload
