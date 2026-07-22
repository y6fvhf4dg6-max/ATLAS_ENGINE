from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

from CORE.providers.portrait.atlas_mediapipe_portrait_landmark_json_exporter import (
    AtlasMediaPipePortraitLandmarkJsonExporter,
)


class AtlasMediaPipePortraitLandmarkCli:
    """
    Runs MediaPipe Face Landmarker inference and exports deterministic JSON.

    The mediapipe dependency is imported lazily so this module remains
    importable in the main ATLAS_ENGINE Python environment.
    """

    @classmethod
    def build_parser(
        cls,
    ) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description=(
                "Export MediaPipe portrait face landmarks "
                "to deterministic ATLAS JSON."
            ),
        )

        parser.add_argument(
            "--image",
            required=True,
            type=Path,
            help="Input portrait image path.",
        )
        parser.add_argument(
            "--model",
            required=True,
            type=Path,
            help="MediaPipe face_landmarker.task path.",
        )
        parser.add_argument(
            "--output",
            required=True,
            type=Path,
            help="Output JSON path.",
        )
        parser.add_argument(
            "--view-type",
            default="front",
            help="Portrait view classification metadata.",
        )

        return parser

    @staticmethod
    def sha256_file(
        path: Path,
    ) -> str:
        digest = hashlib.sha256()

        with path.open(
            "rb",
        ) as stream:
            for block in iter(
                lambda: stream.read(
                    1024 * 1024
                ),
                b"",
            ):
                digest.update(
                    block
                )

        return digest.hexdigest()

    @staticmethod
    def convert_landmarks(
        landmarks: Any,
    ) -> list[dict[str, float | int]]:
        try:
            source_landmarks = tuple(
                landmarks
            )
        except TypeError as exc:
            raise TypeError(
                "landmarks must be iterable."
            ) from exc

        expected_count = (
            AtlasMediaPipePortraitLandmarkJsonExporter
            .EXPECTED_LANDMARK_COUNT
        )

        if len(
            source_landmarks
        ) != expected_count:
            raise ValueError(
                "MediaPipe result must contain exactly "
                f"{expected_count} landmarks."
            )

        return [
            {
                "id": landmark_id,
                "x": float(
                    landmark.x
                ),
                "y": float(
                    landmark.y
                ),
                "z": float(
                    landmark.z
                ),
            }
            for landmark_id, landmark in enumerate(
                source_landmarks
            )
        ]

    @classmethod
    def export(
        cls,
        *,
        image_path: Path,
        model_path: Path,
        output_path: Path,
        view_type: str,
        mediapipe_module: Any | None = None,
    ) -> Path:
        image_path = Path(
            image_path
        )
        model_path = Path(
            model_path
        )
        output_path = Path(
            output_path
        )

        if not image_path.is_file():
            raise FileNotFoundError(
                f"image file does not exist: {image_path}"
            )

        if not model_path.is_file():
            raise FileNotFoundError(
                f"model file does not exist: {model_path}"
            )

        if mediapipe_module is None:
            try:
                import mediapipe as mediapipe_module
            except ModuleNotFoundError as exc:
                raise RuntimeError(
                    "mediapipe is required for runtime export. "
                    "Run this module with the dedicated "
                    "Python 3.12 MediaPipe environment."
                ) from exc

        mp = mediapipe_module

        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = (
            mp.tasks.vision.FaceLandmarker
        )
        FaceLandmarkerOptions = (
            mp.tasks.vision.FaceLandmarkerOptions
        )
        RunningMode = (
            mp.tasks.vision.RunningMode
        )

        options = FaceLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path=str(
                    model_path.resolve()
                ),
            ),
            running_mode=RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.50,
            min_face_presence_confidence=0.50,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )

        image = mp.Image.create_from_file(
            str(
                image_path.resolve()
            )
        )

        with FaceLandmarker.create_from_options(
            options
        ) as landmarker:
            result = landmarker.detect(
                image
            )

        face_landmarks = tuple(
            result.face_landmarks
        )

        if len(
            face_landmarks
        ) != 1:
            raise ValueError(
                "MediaPipe must detect exactly one face."
            )

        landmark_records = cls.convert_landmarks(
            face_landmarks[
                0
            ]
        )

        payload = (
            AtlasMediaPipePortraitLandmarkJsonExporter
            .build_payload(
                image_width=image.width,
                image_height=image.height,
                confidence=1.0,
                landmarks=landmark_records,
                mediapipe_version=str(
                    mp.__version__
                ),
                model_asset=model_path.name,
                source_image_sha256=cls.sha256_file(
                    image_path
                ),
                view_type=view_type,
            )
        )

        return (
            AtlasMediaPipePortraitLandmarkJsonExporter
            .write(
                output_path,
                payload,
            )
        )

    @classmethod
    def main(
        cls,
        argv: list[str] | None = None,
    ) -> int:
        arguments = cls.build_parser().parse_args(
            argv
        )

        output_path = cls.export(
            image_path=arguments.image,
            model_path=arguments.model,
            output_path=arguments.output,
            view_type=arguments.view_type,
        )

        print(
            f"Exported MediaPipe portrait landmarks: "
            f"{output_path}"
        )

        return 0


if __name__ == "__main__":
    raise SystemExit(
        AtlasMediaPipePortraitLandmarkCli.main()
    )
