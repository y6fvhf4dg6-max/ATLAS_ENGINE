from pathlib import Path

import numpy as np
from PIL import Image

from CORE.atlas_relief_pipeline import (
    AtlasReliefPipeline,
)
from EXPORT.atlas_stl_writer import (
    AtlasSTLWriter,
)
from Test.fixtures.relief.relief_synthetic_portrait_fixture import (
    write_synthetic_portrait_fixture,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PREVIEW_DIRECTORY = (
    PROJECT_ROOT
    / "OUTPUT"
    / "RELIEF"
    / "synthetic_portrait"
)

STL_OUTPUT_PATH = (
    PROJECT_ROOT
    / "OUTPUT"
    / "STL"
    / "relief_synthetic_portrait_preview.stl"
)

IMAGE_OUTPUT_PATH = (
    PREVIEW_DIRECTORY
    / "synthetic_portrait_input.png"
)

MASK_OUTPUT_PATH = (
    PREVIEW_DIRECTORY
    / "synthetic_portrait_mask.png"
)

HEIGHT_MAP_OUTPUT_PATH = (
    PREVIEW_DIRECTORY
    / "synthetic_portrait_height_map.png"
)


def _save_height_map_preview(
    height_map: np.ndarray,
) -> None:
    normalized = np.clip(
        np.asarray(
            height_map,
            dtype=np.float64,
        ),
        0.0,
        1.0,
    )

    preview = np.rint(
        normalized * 255.0
    ).astype(np.uint8)

    Image.fromarray(
        preview,
        mode="L",
    ).save(HEIGHT_MAP_OUTPUT_PATH)


def main() -> None:
    write_synthetic_portrait_fixture(
        PREVIEW_DIRECTORY,
        image_filename=(
            IMAGE_OUTPUT_PATH.name
        ),
        mask_filename=(
            MASK_OUTPUT_PATH.name
        ),
    )

    STL_OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result = AtlasReliefPipeline.build_from_image(
        IMAGE_OUTPUT_PATH,
        width_mm=80.0,
        depth_mm=96.0,
        form_sigma=3.0,
        detail_sigma=1.0,
        detail_weight=0.30,
        micro_detail_weight=0.05,
        mask_path=MASK_OUTPUT_PATH,
        mask_threshold=0.20,
        mask_feather_sigma=1.0,
        mask_morphology_operation="close",
        mask_morphology_radius=1,
    )

    relief_result = result["relief_result"]
    mesh = relief_result["mesh"]
    quality_report = relief_result[
        "quality_report"
    ]

    _save_height_map_preview(
        relief_result[
            "processed_height_map"
        ]
    )

    AtlasSTLWriter.write(
        meshes=[mesh],
        output_path=str(STL_OUTPUT_PATH),
        solid_name=(
            "ATLAS_RELIEF_"
            "SYNTHETIC_PORTRAIT"
        ),
    )

    print("")
    print("=" * 64)
    print(
        "ATLAS RELIEF IMAGE PIPELINE "
        "PREVIEW"
    )
    print("=" * 64)
    print(
        f"Image size       : "
        f"{mesh['column_count']} x "
        f"{mesh['row_count']}"
    )
    print(
        f"Physical size    : "
        f"{mesh['width_mm']:.3f} x "
        f"{mesh['depth_mm']:.3f} mm"
    )
    print(
        f"Base thickness   : "
        f"{mesh['base_thickness_mm']:.3f} mm"
    )
    print(
        f"Relief height    : "
        f"{mesh['relief_height_mm']:.3f} mm"
    )
    print(
        f"Minimum Z        : "
        f"{mesh['minimum_z']:.3f} mm"
    )
    print(
        f"Maximum Z        : "
        f"{mesh['maximum_z']:.3f} mm"
    )
    print(
        f"Triangles        : "
        f"{len(mesh['triangles'])}"
    )
    print(
        f"Open edges       : "
        f"{quality_report['open_edge_count']}"
    )
    print(
        f"Non-manifold     : "
        f"{quality_report['non_manifold_edge_count']}"
    )
    print(
        f"Maximum slope    : "
        f"{quality_report['maximum_slope_degrees']:.3f}°"
    )
    print(
        f"Print risk       : "
        f"{quality_report['print_risk_status']}"
    )
    print(
        f"Input image      : "
        f"{IMAGE_OUTPUT_PATH}"
    )
    print(
        f"Subject mask     : "
        f"{MASK_OUTPUT_PATH}"
    )
    print(
        f"Height map       : "
        f"{HEIGHT_MAP_OUTPUT_PATH}"
    )
    print(
        f"STL output       : "
        f"{STL_OUTPUT_PATH}"
    )
    print("=" * 64)
    print("")


if __name__ == "__main__":
    main()
