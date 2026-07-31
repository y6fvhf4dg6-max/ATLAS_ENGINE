from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Sequence, Tuple

import numpy as np


_REQUIRED_LANDMARK_GROUPS: Tuple[str, ...] = (
    "face_oval",
    "left_eye",
    "right_eye",
    "nose_bridge",
    "nose_body",
    "nose_base",
    "upper_lip",
    "lower_lip",
    "chin",
)


@dataclass(frozen=True)
class AtlasReliefFaceLandmarkRegions:
    """
    Landmark-derived semantic region masks for the 2.5D portrait-relief line.

    Every mask:

    - matches the source image shape,
    - uses float64,
    - stays in the closed range 0..1,
    - is clipped to the landmark-derived face support.

    Landmark coordinates use the order ``[x, y]`` in image pixels.
    """

    masks: Dict[str, np.ndarray]

    @classmethod
    def build(
        cls,
        *,
        image_shape: Sequence[int],
        landmarks: Mapping[str, np.ndarray],
    ) -> "AtlasReliefFaceLandmarkRegions":
        height, width = _validate_image_shape(image_shape)
        validated = _validate_landmarks(
            landmarks=landmarks,
            height=height,
            width=width,
        )

        yy, xx = np.mgrid[
            0:height,
            0:width,
        ]
        xx = xx.astype(np.float64)
        yy = yy.astype(np.float64)

        face_oval = validated["face_oval"]
        face_interior = _polygon_mask(
            points=face_oval,
            xx=xx,
            yy=yy,
        )

        left_eye = validated["left_eye"]
        right_eye = validated["right_eye"]
        nose_bridge = validated["nose_bridge"]
        nose_body = validated["nose_body"]
        nose_base = validated["nose_base"]
        upper_lip = validated["upper_lip"]
        lower_lip = validated["lower_lip"]
        chin = validated["chin"]

        left_eye_center = np.mean(left_eye, axis=0)
        right_eye_center = np.mean(right_eye, axis=0)

        eye_span = max(
            float(
                np.linalg.norm(
                    right_eye_center - left_eye_center
                )
            ),
            1.0,
        )

        eye_glasses = np.maximum(
            _landmark_gaussian(
                points=left_eye,
                xx=xx,
                yy=yy,
                scale_x=1.35,
                scale_y=2.15,
                minimum_sigma_x=8.0,
                minimum_sigma_y=7.0,
            ),
            _landmark_gaussian(
                points=right_eye,
                xx=xx,
                yy=yy,
                scale_x=1.35,
                scale_y=2.15,
                minimum_sigma_x=8.0,
                minimum_sigma_y=7.0,
            ),
        )

        glasses_bridge_center = (
            left_eye_center + right_eye_center
        ) * 0.5

        glasses_bridge = _gaussian(
            xx=xx,
            yy=yy,
            center_x=float(glasses_bridge_center[0]),
            center_y=float(glasses_bridge_center[1]),
            sigma_x=max(eye_span * 0.16, 8.0),
            sigma_y=max(eye_span * 0.10, 5.0),
        )

        eye_glasses = np.maximum(
            eye_glasses,
            glasses_bridge,
        )

        nose_bridge_mask = _landmark_gaussian(
            points=nose_bridge,
            xx=xx,
            yy=yy,
            scale_x=2.0,
            scale_y=1.45,
            minimum_sigma_x=7.0,
            minimum_sigma_y=18.0,
        )

        nose_body_mask = _landmark_gaussian(
            points=nose_body,
            xx=xx,
            yy=yy,
            scale_x=1.30,
            scale_y=1.25,
            minimum_sigma_x=14.0,
            minimum_sigma_y=18.0,
        )

        nose_base_mask = _landmark_gaussian(
            points=nose_base,
            xx=xx,
            yy=yy,
            scale_x=1.20,
            scale_y=1.80,
            minimum_sigma_x=13.0,
            minimum_sigma_y=6.0,
        )

        upper_lip_mask = _landmark_gaussian(
            points=upper_lip,
            xx=xx,
            yy=yy,
            scale_x=1.10,
            scale_y=1.55,
            minimum_sigma_x=17.0,
            minimum_sigma_y=5.0,
        )

        lower_lip_mask = _landmark_gaussian(
            points=lower_lip,
            xx=xx,
            yy=yy,
            scale_x=1.10,
            scale_y=1.35,
            minimum_sigma_x=17.0,
            minimum_sigma_y=6.0,
        )

        nose_base_center = np.mean(nose_base, axis=0)
        upper_lip_center = np.mean(upper_lip, axis=0)

        philtrum_center = np.asarray(
            [
                (
                    nose_base_center[0]
                    + upper_lip_center[0]
                )
                * 0.5,
                (
                    nose_base_center[1]
                    + upper_lip_center[1]
                )
                * 0.5,
            ],
            dtype=np.float64,
        )

        philtrum_vertical_gap = max(
            float(
                upper_lip_center[1]
                - nose_base_center[1]
            ),
            2.0,
        )

        philtrum_mask = _gaussian(
            xx=xx,
            yy=yy,
            center_x=float(philtrum_center[0]),
            center_y=float(philtrum_center[1]),
            sigma_x=max(eye_span * 0.075, 5.0),
            sigma_y=max(
                philtrum_vertical_gap * 0.38,
                3.0,
            ),
        )

        left_cheek_mask, right_cheek_mask = (
            _build_cheek_masks(
                xx=xx,
                yy=yy,
                left_eye_center=left_eye_center,
                right_eye_center=right_eye_center,
                nose_base_center=nose_base_center,
                upper_lip_center=upper_lip_center,
                eye_span=eye_span,
                eye_glasses=eye_glasses,
                upper_lip=upper_lip_mask,
                lower_lip=lower_lip_mask,
            )
        )

        chin_mask = _landmark_gaussian(
            points=chin,
            xx=xx,
            yy=yy,
            scale_x=1.20,
            scale_y=1.25,
            minimum_sigma_x=18.0,
            minimum_sigma_y=12.0,
        )

        face_boundary_falloff = _face_boundary_ring(
            face_oval=face_oval,
            face_interior=face_interior,
            xx=xx,
            yy=yy,
        )

        masks = {
            "eye_glasses": eye_glasses,
            "nose_bridge": nose_bridge_mask,
            "nose_body": nose_body_mask,
            "nose_base": nose_base_mask,
            "philtrum": philtrum_mask,
            "upper_lip": upper_lip_mask,
            "lower_lip": lower_lip_mask,
            "left_cheek": left_cheek_mask,
            "right_cheek": right_cheek_mask,
            "chin": chin_mask,
            "face_interior": face_interior,
            "face_boundary_falloff": face_boundary_falloff,
        }

        clipped_masks = {
            name: _clip_mask(
                mask=mask,
                support=face_interior,
            )
            for name, mask in masks.items()
        }

        return cls(masks=clipped_masks)


def _validate_image_shape(
    image_shape: Sequence[int],
) -> Tuple[int, int]:
    if isinstance(image_shape, (str, bytes)):
        raise TypeError(
            "image_shape must contain exactly two integers"
        )

    try:
        values = tuple(image_shape)
    except TypeError as exc:
        raise TypeError(
            "image_shape must contain exactly two integers"
        ) from exc

    if len(values) != 2:
        raise ValueError(
            "image_shape must contain exactly two values"
        )

    height, width = values

    if (
        isinstance(height, bool)
        or isinstance(width, bool)
        or not isinstance(height, (int, np.integer))
        or not isinstance(width, (int, np.integer))
    ):
        raise TypeError(
            "image_shape values must be integers"
        )

    height = int(height)
    width = int(width)

    if height <= 0 or width <= 0:
        raise ValueError(
            "image_shape values must be positive"
        )

    return height, width


def _validate_landmarks(
    *,
    landmarks: Mapping[str, np.ndarray],
    height: int,
    width: int,
) -> Dict[str, np.ndarray]:
    if not isinstance(landmarks, Mapping):
        raise TypeError(
            "landmarks must be a mapping of named groups"
        )

    validated: Dict[str, np.ndarray] = {}

    for group_name in _REQUIRED_LANDMARK_GROUPS:
        if group_name not in landmarks:
            raise ValueError(
                f"missing required landmark group: "
                f"{group_name}"
            )

        points = np.asarray(
            landmarks[group_name],
            dtype=np.float64,
        )

        if (
            points.ndim != 2
            or points.shape[1] != 2
            or points.shape[0] < 2
        ):
            raise ValueError(
                f"landmark group {group_name!r} must "
                f"have shape (N, 2)"
            )

        if group_name == "face_oval" and points.shape[0] < 3:
            raise ValueError(
                "face_oval must contain at least "
                "three points"
            )

        if not np.all(np.isfinite(points)):
            raise ValueError(
                f"landmark group {group_name!r} contains "
                f"non-finite coordinates"
            )

        x = points[:, 0]
        y = points[:, 1]

        if (
            np.any(x < 0.0)
            or np.any(x > float(width - 1))
            or np.any(y < 0.0)
            or np.any(y > float(height - 1))
        ):
            raise ValueError(
                f"landmark group {group_name!r} contains "
                f"coordinates outside the image"
            )

        validated[group_name] = points.copy()

    return validated


def _polygon_mask(
    *,
    points: np.ndarray,
    xx: np.ndarray,
    yy: np.ndarray,
) -> np.ndarray:
    inside = np.zeros(xx.shape, dtype=bool)

    x_points = points[:, 0]
    y_points = points[:, 1]
    point_count = int(points.shape[0])

    previous_index = point_count - 1

    for current_index in range(point_count):
        x_current = x_points[current_index]
        y_current = y_points[current_index]
        x_previous = x_points[previous_index]
        y_previous = y_points[previous_index]

        crosses_scanline = (
            (y_current > yy)
            != (y_previous > yy)
        )

        denominator = y_previous - y_current

        if abs(float(denominator)) < 1.0e-12:
            denominator = (
                1.0e-12
                if denominator >= 0.0
                else -1.0e-12
            )

        crossing_x = (
            (x_previous - x_current)
            * (yy - y_current)
            / denominator
            + x_current
        )

        inside ^= crosses_scanline & (xx < crossing_x)
        previous_index = current_index

    return inside.astype(np.float64)


def _landmark_gaussian(
    *,
    points: np.ndarray,
    xx: np.ndarray,
    yy: np.ndarray,
    scale_x: float,
    scale_y: float,
    minimum_sigma_x: float,
    minimum_sigma_y: float,
) -> np.ndarray:
    center = np.mean(points, axis=0)

    x_extent = float(
        np.max(points[:, 0])
        - np.min(points[:, 0])
    )
    y_extent = float(
        np.max(points[:, 1])
        - np.min(points[:, 1])
    )

    sigma_x = max(
        x_extent * 0.5 * scale_x,
        minimum_sigma_x,
    )
    sigma_y = max(
        y_extent * 0.5 * scale_y,
        minimum_sigma_y,
    )

    return _gaussian(
        xx=xx,
        yy=yy,
        center_x=float(center[0]),
        center_y=float(center[1]),
        sigma_x=sigma_x,
        sigma_y=sigma_y,
    )


def _gaussian(
    *,
    xx: np.ndarray,
    yy: np.ndarray,
    center_x: float,
    center_y: float,
    sigma_x: float,
    sigma_y: float,
) -> np.ndarray:
    sigma_x = max(float(sigma_x), 1.0e-6)
    sigma_y = max(float(sigma_y), 1.0e-6)

    normalized_x = (
        (xx - center_x) / sigma_x
    )
    normalized_y = (
        (yy - center_y) / sigma_y
    )

    mask = np.exp(
        -0.5
        * (
            normalized_x * normalized_x
            + normalized_y * normalized_y
        )
    )

    return np.asarray(mask, dtype=np.float64)


def _build_cheek_masks(
    *,
    xx: np.ndarray,
    yy: np.ndarray,
    left_eye_center: np.ndarray,
    right_eye_center: np.ndarray,
    nose_base_center: np.ndarray,
    upper_lip_center: np.ndarray,
    eye_span: float,
    eye_glasses: np.ndarray,
    upper_lip: np.ndarray,
    lower_lip: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    cheek_center_y = (
        0.68 * float(nose_base_center[1])
        + 0.32 * float(upper_lip_center[1])
    )

    cheek_sigma_x = max(
        eye_span * 0.30,
        22.0,
    )
    cheek_sigma_y = max(
        eye_span * 0.30,
        24.0,
    )

    left_cheek = _gaussian(
        xx=xx,
        yy=yy,
        center_x=float(left_eye_center[0]),
        center_y=cheek_center_y,
        sigma_x=cheek_sigma_x,
        sigma_y=cheek_sigma_y,
    )

    right_cheek = _gaussian(
        xx=xx,
        yy=yy,
        center_x=float(right_eye_center[0]),
        center_y=cheek_center_y,
        sigma_x=cheek_sigma_x,
        sigma_y=cheek_sigma_y,
    )

    mouth_core = np.maximum(
        upper_lip,
        lower_lip,
    )

    # Suppress only the strong glasses core. A linear subtraction would
    # let the broad Gaussian tail erase useful cheek structure on compact
    # real faces.
    eye_suppression = (
        0.90
        * np.power(
            np.clip(eye_glasses, 0.0, 1.0),
            4.0,
        )
    )

    # Mouth detail must remain more strongly excluded because lip-line
    # gradients should not leak into the cheek-preservation regions.
    mouth_suppression = (
        0.95
        * np.power(
            np.clip(mouth_core, 0.0, 1.0),
            2.0,
        )
    )

    exclusion_factor = (
        np.clip(
            1.0 - eye_suppression,
            0.0,
            1.0,
        )
        * np.clip(
            1.0 - mouth_suppression,
            0.0,
            1.0,
        )
    )

    left_cheek *= exclusion_factor
    right_cheek *= exclusion_factor

    mouth_center_x = float(
        upper_lip_center[0]
    )
    transition_width = max(
        eye_span * 0.10,
        8.0,
    )

    horizontal_offset = np.clip(
        (xx - mouth_center_x)
        / transition_width,
        -60.0,
        60.0,
    )

    image_left_weight = (
        1.0
        / (
            1.0
            + np.exp(horizontal_offset)
        )
    )
    image_right_weight = (
        1.0
        - image_left_weight
    )

    # Select the spatial side from the actual landmark center rather
    # than from the semantic name. MediaPipe eye names are anatomical:
    # the person's left eye normally appears on the image-right side.
    left_cheek_side_weight = (
        image_left_weight
        if float(left_eye_center[0]) < mouth_center_x
        else image_right_weight
    )
    right_cheek_side_weight = (
        image_left_weight
        if float(right_eye_center[0]) < mouth_center_x
        else image_right_weight
    )

    left_cheek *= (
        0.15
        + 0.85 * left_cheek_side_weight
    )
    right_cheek *= (
        0.15
        + 0.85 * right_cheek_side_weight
    )

    return left_cheek, right_cheek


def _face_boundary_ring(
    *,
    face_oval: np.ndarray,
    face_interior: np.ndarray,
    xx: np.ndarray,
    yy: np.ndarray,
) -> np.ndarray:
    center = np.mean(face_oval, axis=0)

    radius_x = max(
        float(
            np.max(
                np.abs(
                    face_oval[:, 0] - center[0]
                )
            )
        ),
        1.0,
    )
    radius_y = max(
        float(
            np.max(
                np.abs(
                    face_oval[:, 1] - center[1]
                )
            )
        ),
        1.0,
    )

    radial_distance = np.sqrt(
        (
            (xx - float(center[0]))
            / radius_x
        )
        ** 2
        + (
            (yy - float(center[1]))
            / radius_y
        )
        ** 2
    )

    transition = np.clip(
        (radial_distance - 0.62) / 0.30,
        0.0,
        1.0,
    )

    smooth_transition = (
        transition
        * transition
        * (3.0 - 2.0 * transition)
    )

    return (
        face_interior
        * smooth_transition
    ).astype(np.float64)


def _clip_mask(
    *,
    mask: np.ndarray,
    support: np.ndarray,
) -> np.ndarray:
    clipped = np.asarray(
        mask,
        dtype=np.float64,
    )

    clipped = np.nan_to_num(
        clipped,
        nan=0.0,
        posinf=1.0,
        neginf=0.0,
    )

    clipped = np.clip(
        clipped,
        0.0,
        1.0,
    )

    clipped *= support

    return np.ascontiguousarray(
        clipped,
        dtype=np.float64,
    )
