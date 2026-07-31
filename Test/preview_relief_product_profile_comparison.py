from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from CORE.atlas_relief_pipeline import AtlasReliefPipeline
from CORE.atlas_relief_product_profile import AtlasReliefProductProfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_DIRECTORY = (
    PROJECT_ROOT
    / "Data"
    / "RELIEF"
    / "real_portrait_01"
)

SOURCE_IMAGE_PATH = (
    INPUT_DIRECTORY
    / "portrait_crop.png"
)

SUBJECT_MASK_PATH = (
    INPUT_DIRECTORY
    / "subject_mask.png"
)

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "OUTPUT"
    / "RELIEF"
    / "real_portrait_shaded_preview"
)

PANEL_OUTPUT_PATH = (
    OUTPUT_DIRECTORY
    / "real_portrait_shaded_comparison.png"
)


PROFILES = (
    AtlasReliefProductProfile(
        name="memorial-soft",
        form_sigma=4.0,
        detail_sigma=1.2,
        form_weight=1.0,
        detail_weight=0.20,
        micro_detail_weight=0.02,
        micro_detail_limit=0.02,
        depth_lower_percentile=2.0,
        depth_upper_percentile=98.0,
        depth_gamma=1.10,
        background_depth_range=(0.0, 0.35),
        foreground_depth_range=(0.65, 1.0),
        relief_height_mm=1.60,
        smoothing_sigma=0.60,
        smoothing_radius=2,
    ),
    AtlasReliefProductProfile(
        name="caricature",
        form_sigma=2.5,
        detail_sigma=0.8,
        form_weight=1.15,
        detail_weight=0.45,
        micro_detail_weight=0.08,
        micro_detail_limit=0.04,
        depth_lower_percentile=1.0,
        depth_upper_percentile=99.0,
        depth_gamma=0.90,
        background_depth_range=(0.0, 0.30),
        foreground_depth_range=(0.65, 1.0),
        relief_height_mm=2.40,
        smoothing_sigma=0.25,
        smoothing_radius=1,
    ),
    AtlasReliefProductProfile(
        name="portrait-premium",
        form_sigma=3.0,
        detail_sigma=1.0,
        form_weight=1.0,
        detail_weight=0.35,
        micro_detail_weight=0.06,
        micro_detail_limit=0.03,
        depth_lower_percentile=1.0,
        depth_upper_percentile=99.0,
        depth_gamma=1.0,
        background_depth_range=(0.0, 0.40),
        foreground_depth_range=(0.60, 1.0),
        relief_height_mm=2.0,
        smoothing_sigma=0.35,
        smoothing_radius=1,
    ),
)


def _normalize_height_map(
    height_map: np.ndarray,
) -> np.ndarray:
    values = np.asarray(
        height_map,
        dtype=np.float64,
    )

    finite_mask = np.isfinite(values)

    if not np.any(finite_mask):
        raise ValueError(
            "Height map contains no finite values."
        )

    minimum = float(
        np.min(values[finite_mask])
    )
    maximum = float(
        np.max(values[finite_mask])
    )

    if maximum <= minimum:
        return np.zeros_like(
            values,
            dtype=np.float64,
        )

    normalized = (
        values - minimum
    ) / (
        maximum - minimum
    )

    return np.clip(
        normalized,
        0.0,
        1.0,
    )


def _save_height_map(
    height_map: np.ndarray,
    output_path: Path,
) -> Image.Image:
    normalized = _normalize_height_map(
        height_map
    )

    pixels = np.rint(
        normalized * 255.0
    ).astype(np.uint8)

    image = Image.fromarray(
        pixels,
        mode="L",
    )

    image.save(output_path)

    return image


def _build_shaded_preview(
    height_map: np.ndarray,
    *,
    horizontal_scale: float = 9.0,
    vertical_scale: float = 9.0,
    ambient: float = 0.24,
) -> Image.Image:
    height = _normalize_height_map(
        height_map
    )

    gradient_y, gradient_x = np.gradient(
        height
    )

    normal_x = (
        -gradient_x * horizontal_scale
    )
    normal_y = (
        -gradient_y * vertical_scale
    )
    normal_z = np.ones_like(
        height
    )

    normal_length = np.sqrt(
        normal_x * normal_x
        + normal_y * normal_y
        + normal_z * normal_z
    )

    normal_x /= normal_length
    normal_y /= normal_length
    normal_z /= normal_length

    light = np.asarray(
        (-0.50, -0.42, 0.76),
        dtype=np.float64,
    )

    light /= np.linalg.norm(light)

    diffuse = (
        normal_x * light[0]
        + normal_y * light[1]
        + normal_z * light[2]
    )

    diffuse = np.clip(
        diffuse,
        0.0,
        1.0,
    )

    intensity = np.clip(
        ambient
        + (1.0 - ambient) * diffuse,
        0.0,
        1.0,
    )

    base_stone = np.asarray(
        (218.0, 214.0, 204.0),
        dtype=np.float64,
    )

    shadow_stone = np.asarray(
        (72.0, 72.0, 70.0),
        dtype=np.float64,
    )

    rgb = (
        shadow_stone[None, None, :]
        + intensity[:, :, None]
        * (
            base_stone[None, None, :]
            - shadow_stone[None, None, :]
        )
    )

    rgb = np.rint(
        np.clip(
            rgb,
            0.0,
            255.0,
        )
    ).astype(np.uint8)

    return Image.fromarray(
        rgb,
        mode="RGB",
    )


def _fit_image(
    image: Image.Image,
    size: tuple[int, int],
) -> Image.Image:
    fitted = image.copy()
    fitted.thumbnail(
        size,
        Image.Resampling.LANCZOS,
    )

    canvas = Image.new(
        "RGB",
        size,
        (245, 245, 245),
    )

    x = (
        size[0] - fitted.width
    ) // 2

    y = (
        size[1] - fitted.height
    ) // 2

    if fitted.mode != "RGB":
        fitted = fitted.convert("RGB")

    canvas.paste(
        fitted,
        (x, y),
    )

    return canvas


def _make_panel(
    source_image: Image.Image,
    mask_image: Image.Image,
    profile_results: list[dict],
) -> Image.Image:
    tile_width = 360
    tile_height = 460
    label_height = 44
    gap = 18
    margin = 24

    columns = 2 + len(profile_results)

    panel_width = (
        margin * 2
        + columns * tile_width
        + (columns - 1) * gap
    )

    panel_height = (
        margin * 2
        + label_height
        + tile_height
    )

    panel = Image.new(
        "RGB",
        (
            panel_width,
            panel_height,
        ),
        (255, 255, 255),
    )

    draw = ImageDraw.Draw(panel)
    font = ImageFont.load_default()

    items = [
        (
            "SOURCE PHOTO",
            source_image,
        ),
        (
            "SUBJECT MASK",
            mask_image.convert("RGB"),
        ),
    ]

    for result in profile_results:
        items.append(
            (
                result["profile"].name.upper(),
                result["shaded_image"],
            )
        )

    for index, (label, image) in enumerate(items):
        x = (
            margin
            + index * (
                tile_width + gap
            )
        )

        draw.text(
            (
                x,
                margin,
            ),
            label,
            fill=(20, 20, 20),
            font=font,
        )

        fitted = _fit_image(
            image,
            (
                tile_width,
                tile_height,
            ),
        )

        panel.paste(
            fitted,
            (
                x,
                margin + label_height,
            ),
        )

    return panel


def _build_profile(
    profile: AtlasReliefProductProfile,
) -> dict:
    result = (
        AtlasReliefPipeline
        .build_from_image(
            SOURCE_IMAGE_PATH,
            width_mm=80.0,
            depth_mm=80.0,
            product_profile=profile,
            mask_path=SUBJECT_MASK_PATH,
            mask_threshold=0.20,
            mask_feather_sigma=1.0,
            mask_morphology_operation="close",
            mask_morphology_radius=1,
        )
    )

    relief_result = result[
        "relief_result"
    ]

    height_map = relief_result[
        "processed_height_map"
    ]

    height_output_path = (
        OUTPUT_DIRECTORY
        / f"{profile.name}_height_map.png"
    )

    shaded_output_path = (
        OUTPUT_DIRECTORY
        / f"{profile.name}_shaded.png"
    )

    height_image = _save_height_map(
        height_map,
        height_output_path,
    )

    shaded_image = (
        _build_shaded_preview(
            height_map
        )
    )

    shaded_image.save(
        shaded_output_path
    )

    return {
        "profile": profile,
        "pipeline_result": result,
        "height_image": height_image,
        "shaded_image": shaded_image,
        "height_output_path": (
            height_output_path
        ),
        "shaded_output_path": (
            shaded_output_path
        ),
    }


def _print_profile_report(
    profile_result: dict,
) -> None:
    profile = profile_result[
        "profile"
    ]

    relief_result = profile_result[
        "pipeline_result"
    ]["relief_result"]

    mesh = relief_result[
        "mesh"
    ]

    quality_report = relief_result[
        "quality_report"
    ]

    print("")
    print("-" * 64)
    print(
        f"PROFILE           : {profile.name}"
    )
    print("-" * 64)
    print(
        f"Relief height     : "
        f"{mesh['relief_height_mm']:.3f} mm"
    )
    print(
        f"Grid              : "
        f"{mesh['column_count']} x "
        f"{mesh['row_count']}"
    )
    print(
        f"Triangles         : "
        f"{len(mesh['triangles'])}"
    )
    print(
        f"Open edges        : "
        f"{quality_report['open_edge_count']}"
    )
    print(
        f"Non-manifold      : "
        f"{quality_report['non_manifold_edge_count']}"
    )
    print(
        f"Maximum slope     : "
        f"{quality_report['maximum_slope_degrees']:.3f}°"
    )
    print(
        f"Print risk        : "
        f"{quality_report['print_risk_status']}"
    )
    print(
        f"Height map        : "
        f"{profile_result['height_output_path']}"
    )
    print(
        f"Shaded preview    : "
        f"{profile_result['shaded_output_path']}"
    )


def main() -> None:
    if not SOURCE_IMAGE_PATH.is_file():
        raise FileNotFoundError(
            f"Source image not found: "
            f"{SOURCE_IMAGE_PATH}"
        )

    if not SUBJECT_MASK_PATH.is_file():
        raise FileNotFoundError(
            f"Subject mask not found: "
            f"{SUBJECT_MASK_PATH}"
        )

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    source_image = Image.open(
        SOURCE_IMAGE_PATH
    ).convert("RGB")

    mask_image = Image.open(
        SUBJECT_MASK_PATH
    ).convert("L")

    profile_results = [
        _build_profile(profile)
        for profile in PROFILES
    ]

    panel = _make_panel(
        source_image,
        mask_image,
        profile_results,
    )

    panel.save(
        PANEL_OUTPUT_PATH
    )

    print("")
    print("=" * 64)
    print(
        "ATLAS REAL PORTRAIT "
        "SHADED RELIEF PREVIEW"
    )
    print("=" * 64)
    print(
        f"Source image      : "
        f"{SOURCE_IMAGE_PATH}"
    )
    print(
        f"Subject mask      : "
        f"{SUBJECT_MASK_PATH}"
    )

    for profile_result in profile_results:
        _print_profile_report(
            profile_result
        )

    print("")
    print("=" * 64)
    print(
        f"Comparison panel  : "
        f"{PANEL_OUTPUT_PATH}"
    )
    print(
        "STL generation    : DISABLED"
    )
    print("=" * 64)
    print("")


if __name__ == "__main__":
    main()
