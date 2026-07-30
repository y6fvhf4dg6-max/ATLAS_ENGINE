from pathlib import Path
import sys

import numpy as np
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from CORE.atlas_relief_pipeline import AtlasReliefPipeline
from CORE.atlas_rock_relief_production_preset import (
    DALYAN_ROCK_TOMBS_PRODUCTION_PRESET,
)
from CORE.atlas_relief_product_profile import (
    AtlasReliefProductProfile,
)


SOURCE_PATH = (
    PROJECT_ROOT
    / "Data"
    / "RELIEF"
    / "dalyan_rock_tombs"
    / "rock_tombs_relief_working_240px.png"
)

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "OUTPUT"
    / "RELIEF"
    / "dalyan_rock_tombs"
)

HEIGHT_MAP_PATH = (
    OUTPUT_DIRECTORY
    / "rock_carved_landmark_height_map.png"
)

SHADED_PREVIEW_PATH = (
    OUTPUT_DIRECTORY
    / "rock_carved_landmark_shaded.png"
)


def normalize(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)

    minimum = float(np.min(array))
    maximum = float(np.max(array))

    if maximum <= minimum:
        return np.zeros_like(array)

    return (array - minimum) / (maximum - minimum)


def save_height_map(
    height_map: np.ndarray,
    output_path: Path,
) -> None:
    normalized = normalize(height_map)

    image = Image.fromarray(
        np.round(normalized * 255.0).astype(np.uint8),
        mode="L",
    )

    image.save(output_path)


def save_shaded_preview(
    height_map: np.ndarray,
    output_path: Path,
) -> None:
    normalized = normalize(height_map)

    gradient_y, gradient_x = np.gradient(normalized)

    normal_x = -gradient_x * 5.0
    normal_y = -gradient_y * 5.0
    normal_z = np.ones_like(normalized)

    length = np.sqrt(
        normal_x * normal_x
        + normal_y * normal_y
        + normal_z * normal_z
    )

    normal_x /= length
    normal_y /= length
    normal_z /= length

    light = np.array(
        [-0.45, -0.55, 0.70],
        dtype=np.float64,
    )
    light /= np.linalg.norm(light)

    shading = (
        normal_x * light[0]
        + normal_y * light[1]
        + normal_z * light[2]
    )

    shading = np.clip(
        0.20 + 0.80 * shading,
        0.0,
        1.0,
    )

    image = Image.fromarray(
        np.round(shading * 255.0).astype(np.uint8),
        mode="L",
    )

    image.save(output_path)


def main() -> None:
    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    source_image = Image.open(
        SOURCE_PATH
    ).convert(
        "L"
    )

    source_values = (
        np.asarray(
            source_image,
            dtype=np.float64,
        )
        / 255.0
    )

    normalized_values = (
        DALYAN_ROCK_TOMBS_PRODUCTION_PRESET
        .preprocessors[0](
            source_values
        )
    )

    normalized_source_path = (
        OUTPUT_DIRECTORY
        / "rock_tombs_illumination_normalized.png"
    )

    Image.fromarray(
        np.round(
            normalized_values * 255.0
        ).astype(
            np.uint8
        ),
        mode="L",
    ).save(
        normalized_source_path
    )

    profiles = (
        DALYAN_ROCK_TOMBS_PRODUCTION_PRESET.product_profile,
        AtlasReliefProductProfile(
            name="rock-carved-landmark-detail",
            form_sigma=2.4,
            detail_sigma=0.65,
            form_weight=0.85,
            detail_weight=0.55,
            micro_detail_weight=0.01,
            micro_detail_limit=0.015,
            depth_lower_percentile=3.0,
            depth_upper_percentile=97.0,
            depth_gamma=1.05,
            relief_height_mm=1.8,
            smoothing_sigma=0.22,
            smoothing_radius=1,
        ),
    )

    preprocessors = (
        (
            "original",
            (),
        ),
        (
            "illumination-normalized",
            DALYAN_ROCK_TOMBS_PRODUCTION_PRESET.preprocessors,
        ),
    )

    for source_name, source_preprocessors in preprocessors:
        for profile in profiles:
            if (
                profile
                is DALYAN_ROCK_TOMBS_PRODUCTION_PRESET.product_profile
                and source_preprocessors
                == DALYAN_ROCK_TOMBS_PRODUCTION_PRESET.preprocessors
            ):
                result = (
                    DALYAN_ROCK_TOMBS_PRODUCTION_PRESET
                    .build_from_image(
                        SOURCE_PATH,
                        width_mm=80.0,
                        depth_mm=50.0,
                    )
                )
            else:
                result = AtlasReliefPipeline.build_from_image(
                    SOURCE_PATH,
                    width_mm=80.0,
                    depth_mm=50.0,
                    product_profile=profile,
                    preprocessors=source_preprocessors,
                )

            height_map = result[
                "relief_result"
            ][
                "processed_height_map"
            ]

            stem = (
                f"{source_name}_{profile.name}"
            )

            height_path = (
                OUTPUT_DIRECTORY
                / f"{stem}_height_map.png"
            )
            shaded_path = (
                OUTPUT_DIRECTORY
                / f"{stem}_shaded.png"
            )

            save_height_map(
                height_map,
                height_path,
            )
            save_shaded_preview(
                height_map,
                shaded_path,
            )

            print(
                source_name,
                profile.name,
                height_map.shape,
                float(np.min(height_map)),
                float(np.max(height_map)),
            )
            print(height_path)
            print(shaded_path)

    print(
        "Normalized source:",
        normalized_source_path,
    )


if __name__ == "__main__":
    main()
