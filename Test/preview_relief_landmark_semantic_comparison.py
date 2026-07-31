from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from CORE.atlas_relief_face_anchor_enhancer import (
    AtlasReliefFaceAnchorEnhancer,
)
from CORE.atlas_relief_face_landmark_regions import (
    AtlasReliefFaceLandmarkRegions,
)
from CORE.atlas_relief_face_semantic_detail_weight_map import (
    AtlasReliefFaceSemanticDetailWeightMap,
)
from CORE.atlas_relief_face_structure_confidence_map import (
    AtlasReliefFaceStructureConfidenceMap,
)
from CORE.atlas_relief_mediapipe_landmark_adapter import (
    AtlasReliefMediaPipeLandmarkAdapter,
)
from CORE.atlas_relief_normal_gradient_limiter import (
    AtlasReliefNormalGradientLimiter,
)
from CORE.atlas_relief_normal_confidence_applier import (
    AtlasReliefNormalConfidenceApplier,
)
from CORE.atlas_relief_normal_structure_detail_decomposer import (
    AtlasReliefNormalStructureDetailDecomposer,
)
from CORE.atlas_relief_screened_normal_integrator import (
    AtlasReliefScreenedNormalIntegrator,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_DIR = (
    PROJECT_ROOT
    / "Data"
    / "RELIEF"
    / "real_portrait_01"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "OUTPUT"
    / "RELIEF"
    / "landmark_semantic_comparison"
)

PORTRAIT_PATH = INPUT_DIR / "portrait_crop_320x400.png"
SUBJECT_MASK_PATH = INPUT_DIR / "subject_mask_320x400.png"
AI_DEPTH_PATH = INPUT_DIR / "ai_depth_16bit.png"
DSINE_NORMAL_PATH = INPUT_DIR / "dsine_normal_map.npy"

LANDMARK_PATH = (
    INPUT_DIR
    / "landmarks"
    / "mediapipe_face_landmarks_2d.npz"
)

PANEL_PATH = (
    OUTPUT_DIR
    / "legacy_vs_landmark_screened_preview.png"
)


STRUCTURE_RADIUS = 5
DETAIL_PERCENTILE = 95.0
ANCHOR_FACE_STRENGTH = 0.20
ANCHOR_MOUTH_SUPPRESSION = 0.35
ANCHOR_BLUR_RADIUS = 5
SCREENING_STRENGTH = 1.0
STRUCTURE_MINIMUM_RETENTION = 0.65
GLASSES_CORE_MINIMUM_RETENTION = 0.20
NOSE_MOUTH_MINIMUM_RETENTION = 0.30


def _load_grayscale(path: Path) -> np.ndarray:
    if not path.exists():
        raise FileNotFoundError(path)

    values = np.asarray(
        Image.open(path),
        dtype=np.float64,
    )

    if values.ndim != 2:
        raise ValueError(
            f"Expected grayscale image: {path}"
        )

    return values


def _normalize(
    values: np.ndarray,
    *,
    mask: np.ndarray | None = None,
) -> np.ndarray:
    array = np.asarray(
        values,
        dtype=np.float64,
    )

    selection = np.isfinite(array)

    if mask is not None:
        selection &= (
            np.asarray(mask, dtype=np.float64)
            > 0.0
        )

    selected = array[selection]

    if selected.size == 0:
        raise ValueError(
            "No finite active values available for normalization."
        )

    lower = float(
        np.percentile(selected, 1.0)
    )
    upper = float(
        np.percentile(selected, 99.0)
    )

    if upper <= lower:
        return np.zeros_like(
            array,
            dtype=np.float64,
        )

    return np.asarray(
        np.clip(
            (array - lower) / (upper - lower),
            0.0,
            1.0,
        ),
        dtype=np.float64,
    )


def _orient_anchor(
    depth: np.ndarray,
    subject_mask: np.ndarray,
) -> tuple[np.ndarray, bool]:
    normalized = _normalize(
        depth,
        mask=subject_mask,
    )

    foreground = normalized[
        subject_mask > 0.50
    ]
    background = normalized[
        subject_mask < 0.05
    ]

    foreground_median = float(
        np.median(foreground)
    )

    if background.size:
        background_median = float(
            np.median(background)
        )
    else:
        background_median = 0.0

    inverted = (
        foreground_median
        < background_median
    )

    if inverted:
        normalized = 1.0 - normalized

    normalized *= np.clip(
        subject_mask,
        0.0,
        1.0,
    )

    return (
        np.asarray(
            normalized,
            dtype=np.float64,
        ),
        inverted,
    )


def _normals_to_gradients(
    normals: np.ndarray,
    *,
    minimum_nz: float = 0.05,
) -> tuple[np.ndarray, np.ndarray]:
    normal_array = np.asarray(
        normals,
        dtype=np.float64,
    )

    nz = np.maximum(
        normal_array[..., 2],
        minimum_nz,
    )

    gradient_x = (
        -normal_array[..., 0] / nz
    )
    gradient_y = (
        -normal_array[..., 1] / nz
    )

    return gradient_x, gradient_y


def _gradients_to_normals(
    gradient_x: np.ndarray,
    gradient_y: np.ndarray,
) -> np.ndarray:
    normals = np.stack(
        [
            -gradient_x,
            -gradient_y,
            np.ones_like(gradient_x),
        ],
        axis=2,
    )

    lengths = np.linalg.norm(
        normals,
        axis=2,
        keepdims=True,
    )

    return np.asarray(
        normals / np.maximum(lengths, 1.0e-12),
        dtype=np.float64,
    )


def _combine_structure_and_detail(
    structure_normals: np.ndarray,
    limited_detail_normals: np.ndarray,
) -> np.ndarray:
    structure_x, structure_y = (
        _normals_to_gradients(
            structure_normals
        )
    )

    detail_x, detail_y = (
        _normals_to_gradients(
            limited_detail_normals
        )
    )

    return _gradients_to_normals(
        structure_x + detail_x,
        structure_y + detail_y,
    )


def _shade(
    height_map: np.ndarray,
    *,
    mask: np.ndarray,
    slope_scale: float = 10.0,
    ambient: float = 0.24,
) -> Image.Image:
    height = _normalize(
        height_map,
        mask=mask,
    )

    gradient_y, gradient_x = np.gradient(
        height
    )

    normal_x = (
        -gradient_x * slope_scale
    )
    normal_y = (
        -gradient_y * slope_scale
    )
    normal_z = np.ones_like(height)

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

    diffuse = np.clip(
        normal_x * light[0]
        + normal_y * light[1]
        + normal_z * light[2],
        0.0,
        1.0,
    )

    intensity = np.clip(
        ambient
        + (1.0 - ambient) * diffuse,
        0.0,
        1.0,
    )

    base = np.asarray(
        (218.0, 214.0, 204.0),
        dtype=np.float64,
    )
    shadow = np.asarray(
        (72.0, 72.0, 70.0),
        dtype=np.float64,
    )

    rgb = (
        shadow[None, None, :]
        + intensity[..., None]
        * (
            base[None, None, :]
            - shadow[None, None, :]
        )
    )

    outside = (
        np.asarray(mask, dtype=np.float64)
        <= 0.0
    )
    rgb[outside] = 245.0

    return Image.fromarray(
        np.rint(
            np.clip(rgb, 0.0, 255.0)
        ).astype(np.uint8),
        mode="RGB",
    )


def _mask_image(
    values: np.ndarray,
) -> Image.Image:
    normalized = np.clip(
        np.asarray(values, dtype=np.float64),
        0.0,
        1.0,
    )

    pixels = np.rint(
        normalized * 255.0
    ).astype(np.uint8)

    return Image.fromarray(
        pixels,
        mode="L",
    ).convert("RGB")


def _fit(
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

    canvas.paste(
        fitted.convert("RGB"),
        (
            (size[0] - fitted.width) // 2,
            (size[1] - fitted.height) // 2,
        ),
    )

    return canvas


def _make_panel(
    items: list[tuple[str, Image.Image]],
) -> Image.Image:
    tile_size = (320, 400)
    label_height = 32
    gap = 12
    margin = 18
    columns = 4

    rows = (
        len(items) + columns - 1
    ) // columns

    width = (
        2 * margin
        + columns * tile_size[0]
        + (columns - 1) * gap
    )
    height = (
        2 * margin
        + rows * (
            tile_size[1]
            + label_height
        )
        + (rows - 1) * gap
    )

    panel = Image.new(
        "RGB",
        (width, height),
        "white",
    )

    draw = ImageDraw.Draw(panel)
    font = ImageFont.load_default()

    for index, (label, image) in enumerate(items):
        row = index // columns
        column = index % columns

        x = (
            margin
            + column * (
                tile_size[0] + gap
            )
        )
        y = (
            margin
            + row * (
                tile_size[1]
                + label_height
                + gap
            )
        )

        panel.paste(
            _fit(image, tile_size),
            (x, y),
        )

        draw.text(
            (x + 4, y + tile_size[1] + 7),
            label,
            fill="black",
            font=font,
        )

    return panel


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    portrait = Image.open(
        PORTRAIT_PATH
    ).convert("RGB")

    subject_mask = (
        _load_grayscale(
            SUBJECT_MASK_PATH
        )
        / 255.0
    )

    depth = _load_grayscale(
        AI_DEPTH_PATH
    )

    anchor, anchor_inverted = (
        _orient_anchor(
            depth,
            subject_mask,
        )
    )

    dsine_normals = np.asarray(
        np.load(DSINE_NORMAL_PATH),
        dtype=np.float64,
    )

    if dsine_normals.shape[:2] != subject_mask.shape:
        raise ValueError(
            "DSINE normal shape does not match subject mask: "
            f"{dsine_normals.shape[:2]} "
            f"vs {subject_mask.shape}"
        )

    with np.load(LANDMARK_PATH) as data:
        points_xy = np.asarray(
            data["points_xy"],
            dtype=np.float64,
        )
        landmark_shape = tuple(
            int(value)
            for value in data["image_shape"]
        )

    if landmark_shape != subject_mask.shape:
        raise ValueError(
            "Landmark shape does not match subject mask."
        )

    grouped = (
        AtlasReliefMediaPipeLandmarkAdapter
        .convert(
            points_xy=points_xy,
            image_shape=subject_mask.shape,
        )
    )

    regions = (
        AtlasReliefFaceLandmarkRegions
        .build(
            image_shape=subject_mask.shape,
            landmarks=grouped,
        )
    )

    face_oval = grouped["face_oval"]

    face_bounds = (
        max(
            0,
            int(np.floor(np.min(face_oval[:, 1]))),
        ),
        min(
            subject_mask.shape[0] - 1,
            int(np.ceil(np.max(face_oval[:, 1]))),
        ),
        max(
            0,
            int(np.floor(np.min(face_oval[:, 0]))),
        ),
        min(
            subject_mask.shape[1] - 1,
            int(np.ceil(np.max(face_oval[:, 0]))),
        ),
    )

    enhanced_anchor = (
        AtlasReliefFaceAnchorEnhancer
        .enhance(
            anchor,
            subject_mask,
            face_bounds=face_bounds,
            face_strength=ANCHOR_FACE_STRENGTH,
            mouth_suppression_strength=(
                ANCHOR_MOUTH_SUPPRESSION
            ),
            blur_radius=ANCHOR_BLUR_RADIUS,
        )
    )

    structure_normals, detail_normals = (
        AtlasReliefNormalStructureDetailDecomposer
        .decompose(
            dsine_normals,
            mask=subject_mask,
            structure_radius=STRUCTURE_RADIUS,
        )
    )

    flat_normals = np.zeros_like(
        dsine_normals,
        dtype=np.float64,
    )
    flat_normals[..., 2] = 1.0

    legacy_confidence = (
        AtlasReliefFaceSemanticDetailWeightMap
        .build(
            subject_mask,
            face_bounds=face_bounds,
        )
    )

    landmark_confidence = (
        AtlasReliefFaceSemanticDetailWeightMap
        .build(
            subject_mask,
            face_bounds=face_bounds,
            landmark_regions=regions.masks,
        )
    )

    legacy_limited_detail = (
        AtlasReliefNormalGradientLimiter
        .limit(
            detail_normals,
            mask=subject_mask,
            confidence_map=legacy_confidence,
            magnitude_percentile=DETAIL_PERCENTILE,
        )
    )

    landmark_limited_detail = (
        AtlasReliefNormalGradientLimiter
        .limit(
            detail_normals,
            mask=subject_mask,
            confidence_map=landmark_confidence,
            magnitude_percentile=DETAIL_PERCENTILE,
        )
    )

    structure_confidence = (
        AtlasReliefFaceStructureConfidenceMap
        .build(
            subject_mask,
            landmark_regions=regions.masks,
        )
    )

    controlled_structure_normals = (
        AtlasReliefNormalConfidenceApplier
        .apply(
            structure_normals,
            confidence_map=structure_confidence,
            mask=subject_mask,
        )
    )

    glasses_core = np.power(
        regions.masks["eye_glasses"],
        3.0,
    )

    glasses_retention_map = (
        STRUCTURE_MINIMUM_RETENTION
        - glasses_core
        * (
            STRUCTURE_MINIMUM_RETENTION
            - GLASSES_CORE_MINIMUM_RETENTION
        )
    )

    nose_mouth_region = np.maximum.reduce(
        [
            regions.masks["nose_base"],
            0.90 * regions.masks["philtrum"],
            0.75 * regions.masks["upper_lip"],
            0.60 * regions.masks["lower_lip"],
        ]
    )

    nose_mouth_retention_map = (
        STRUCTURE_MINIMUM_RETENTION
        - nose_mouth_region
        * (
            STRUCTURE_MINIMUM_RETENTION
            - NOSE_MOUTH_MINIMUM_RETENTION
        )
    )

    structure_retention_map = np.minimum(
        glasses_retention_map,
        nose_mouth_retention_map,
    )

    structure_retention_map = np.clip(
        structure_retention_map,
        GLASSES_CORE_MINIMUM_RETENTION,
        STRUCTURE_MINIMUM_RETENTION,
    )

    retained_structure_normals = (
        AtlasReliefNormalConfidenceApplier
        .apply(
            structure_normals,
            confidence_map=structure_confidence,
            mask=subject_mask,
            minimum_retention=STRUCTURE_MINIMUM_RETENTION,
            minimum_retention_map=structure_retention_map,
        )
    )

    legacy_combined_normals = (
        _combine_structure_and_detail(
            structure_normals,
            legacy_limited_detail,
        )
    )

    landmark_combined_normals = (
        _combine_structure_and_detail(
            structure_normals,
            landmark_limited_detail,
        )
    )

    structure_controlled_combined_normals = (
        _combine_structure_and_detail(
            controlled_structure_normals,
            landmark_limited_detail,
        )
    )

    retained_structure_combined_normals = (
        _combine_structure_and_detail(
            retained_structure_normals,
            landmark_limited_detail,
        )
    )

    anchor_only_height = (
        AtlasReliefScreenedNormalIntegrator
        .integrate(
            flat_normals,
            enhanced_anchor,
            mask=subject_mask,
            screening_strength=SCREENING_STRENGTH,
        )
    )

    legacy_height = (
        AtlasReliefScreenedNormalIntegrator
        .integrate(
            legacy_combined_normals,
            enhanced_anchor,
            mask=subject_mask,
            screening_strength=SCREENING_STRENGTH,
        )
    )

    landmark_height = (
        AtlasReliefScreenedNormalIntegrator
        .integrate(
            landmark_combined_normals,
            enhanced_anchor,
            mask=subject_mask,
            screening_strength=SCREENING_STRENGTH,
        )
    )

    structure_controlled_height = (
        AtlasReliefScreenedNormalIntegrator
        .integrate(
            structure_controlled_combined_normals,
            enhanced_anchor,
            mask=subject_mask,
            screening_strength=SCREENING_STRENGTH,
        )
    )

    retained_structure_height = (
        AtlasReliefScreenedNormalIntegrator
        .integrate(
            retained_structure_combined_normals,
            enhanced_anchor,
            mask=subject_mask,
            screening_strength=SCREENING_STRENGTH,
        )
    )

    anchor_only_shaded = _shade(
        anchor_only_height,
        mask=subject_mask,
    )

    legacy_shaded = _shade(
        legacy_height,
        mask=subject_mask,
    )
    landmark_shaded = _shade(
        landmark_height,
        mask=subject_mask,
    )

    structure_controlled_shaded = _shade(
        structure_controlled_height,
        mask=subject_mask,
    )

    retained_structure_shaded = _shade(
        retained_structure_height,
        mask=subject_mask,
    )

    anchor_only_shaded.save(
        OUTPUT_DIR / "anchor_only_screened_shaded.png"
    )

    legacy_shaded.save(
        OUTPUT_DIR / "legacy_screened_shaded.png"
    )
    landmark_shaded.save(
        OUTPUT_DIR / "landmark_screened_shaded.png"
    )

    structure_controlled_shaded.save(
        OUTPUT_DIR
        / "landmark_structure_controlled_shaded.png"
    )

    retained_structure_shaded.save(
        OUTPUT_DIR
        / "landmark_structure_retained_065_shaded.png"
    )

    _mask_image(
        legacy_confidence
    ).save(
        OUTPUT_DIR / "legacy_semantic_confidence.png"
    )

    _mask_image(
        landmark_confidence
    ).save(
        OUTPUT_DIR / "landmark_semantic_confidence.png"
    )

    _mask_image(
        structure_confidence
    ).save(
        OUTPUT_DIR / "structure_confidence.png"
    )

    _mask_image(
        structure_retention_map
    ).save(
        OUTPUT_DIR / "structure_retention_map.png"
    )

    Image.fromarray(
        np.rint(
            _normalize(
                legacy_height,
                mask=subject_mask,
            )
            * 255.0
        ).astype(np.uint8),
        mode="L",
    ).save(
        OUTPUT_DIR / "legacy_screened_height.png"
    )

    Image.fromarray(
        np.rint(
            _normalize(
                landmark_height,
                mask=subject_mask,
            )
            * 255.0
        ).astype(np.uint8),
        mode="L",
    ).save(
        OUTPUT_DIR / "landmark_screened_height.png"
    )

    Image.fromarray(
        np.rint(
            _normalize(
                structure_controlled_height,
                mask=subject_mask,
            )
            * 255.0
        ).astype(np.uint8),
        mode="L",
    ).save(
        OUTPUT_DIR
        / "landmark_structure_controlled_height.png"
    )

    Image.fromarray(
        np.rint(
            _normalize(
                retained_structure_height,
                mask=subject_mask,
            )
            * 255.0
        ).astype(np.uint8),
        mode="L",
    ).save(
        OUTPUT_DIR
        / "landmark_structure_retained_065_height.png"
    )

    difference = (
        landmark_height
        - legacy_height
    )

    difference_scale = float(
        np.percentile(
            np.abs(
                difference[
                    subject_mask > 0.0
                ]
            ),
            99.0,
        )
    )

    if difference_scale <= 1.0e-12:
        difference_scale = 1.0

    signed = np.zeros(
        (
            subject_mask.shape[0],
            subject_mask.shape[1],
            3,
        ),
        dtype=np.uint8,
    )

    signed[..., 0] = np.rint(
        np.clip(
            -difference / difference_scale,
            0.0,
            1.0,
        )
        * 255.0
    ).astype(np.uint8)

    signed[..., 1] = np.rint(
        np.clip(
            difference / difference_scale,
            0.0,
            1.0,
        )
        * 255.0
    ).astype(np.uint8)

    difference_image = Image.fromarray(
        signed,
        mode="RGB",
    )

    difference_image.save(
        OUTPUT_DIR / "height_difference.png"
    )

    panel = _make_panel(
        [
            ("SOURCE", portrait),
            (
                "ENHANCED AI-DEPTH ANCHOR",
                _mask_image(enhanced_anchor),
            ),
            (
                "LEGACY SEMANTIC CONFIDENCE",
                _mask_image(legacy_confidence),
            ),
            (
                "LANDMARK SEMANTIC CONFIDENCE",
                _mask_image(landmark_confidence),
            ),
            (
                "ANCHOR ONLY — FLAT NORMALS",
                anchor_only_shaded,
            ),
            (
                "LEGACY SCREENED SHADED",
                legacy_shaded,
            ),
            (
                "LANDMARK SCREENED SHADED",
                landmark_shaded,
            ),
            (
                "STRUCTURE CONFIDENCE",
                _mask_image(structure_confidence),
            ),
            (
                "LOCAL RETENTION MAP",
                _mask_image(structure_retention_map),
            ),
            (
                "LANDMARK + STRUCTURE CONTROL 0.00",
                structure_controlled_shaded,
            ),
            (
                "LANDMARK + LOCAL GLASSES RETENTION",
                retained_structure_shaded,
            ),
            (
                "HEIGHT DIFFERENCE",
                difference_image,
            ),
        ]
    )

    panel.save(PANEL_PATH)

    active = subject_mask > 0.0

    print("image_shape:", subject_mask.shape)
    print("face_bounds:", face_bounds)
    print("anchor_inverted:", anchor_inverted)
    print("structure_radius:", STRUCTURE_RADIUS)
    print("detail_percentile:", DETAIL_PERCENTILE)
    print("screening_strength:", SCREENING_STRENGTH)
    print(
        "legacy_height_range:",
        (
            float(np.min(legacy_height[active])),
            float(np.max(legacy_height[active])),
        ),
    )
    print(
        "landmark_height_range:",
        (
            float(np.min(landmark_height[active])),
            float(np.max(landmark_height[active])),
        ),
    )
    print(
        "height_mean_absolute_difference:",
        f"{float(np.mean(np.abs(difference[active]))):.8f}",
    )
    controlled_difference = (
        structure_controlled_height
        - landmark_height
    )

    retained_difference = (
        retained_structure_height
        - landmark_height
    )

    print(
        "height_p99_absolute_difference:",
        f"{float(np.percentile(np.abs(difference[active]), 99.0)):.8f}",
    )
    print(
        "structure_control_mean_absolute_difference:",
        f"{float(np.mean(np.abs(controlled_difference[active]))):.8f}",
    )
    print(
        "structure_control_p99_absolute_difference:",
        f"{float(np.percentile(np.abs(controlled_difference[active]), 99.0)):.8f}",
    )
    print(
        "structure_retention:",
        STRUCTURE_MINIMUM_RETENTION,
    )
    print(
        "glasses_core_minimum_retention:",
        GLASSES_CORE_MINIMUM_RETENTION,
    )
    print(
        "nose_mouth_minimum_retention:",
        NOSE_MOUTH_MINIMUM_RETENTION,
    )
    print(
        "retention_map_range:",
        (
            float(np.min(structure_retention_map[active])),
            float(np.max(structure_retention_map[active])),
        ),
    )
    print(
        "structure_retained_mean_absolute_difference:",
        f"{float(np.mean(np.abs(retained_difference[active]))):.8f}",
    )
    print(
        "structure_retained_p99_absolute_difference:",
        f"{float(np.percentile(np.abs(retained_difference[active]), 99.0)):.8f}",
    )
    print("panel_path:", PANEL_PATH)


if __name__ == "__main__":
    main()
