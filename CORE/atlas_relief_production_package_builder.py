import json
import shutil
from pathlib import Path
from typing import Any


class AtlasReliefProductionPackageBuilder:
    @classmethod
    def build(
        cls,
        *,
        package_directory: Path,
        product_id: str,
        display_name: str,
        width_mm: float,
        depth_mm: float,
        stl_path: Path,
        preview_path: Path,
        source_path: Path,
        profile_name: str,
        production_variant: str,
        quality_report: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        package_directory = Path(package_directory)
        stl_path = cls._require_file(
            "stl_path",
            stl_path,
        )
        preview_path = cls._require_file(
            "preview_path",
            preview_path,
        )
        source_path = cls._require_file(
            "source_path",
            source_path,
        )

        stl_directory = package_directory / "STL"
        preview_directory = package_directory / "PREVIEW"
        source_directory = package_directory / "SOURCE"
        reports_directory = package_directory / "REPORTS"

        for directory in (
            stl_directory,
            preview_directory,
            source_directory,
            reports_directory,
        ):
            directory.mkdir(
                parents=True,
                exist_ok=True,
            )

        final_stl_name = (
            f"{product_id.replace('_80x50mm', '')}"
            "_relief_80x50mm_FINAL.stl"
        )
        final_preview_name = (
            f"{product_id.replace('_80x50mm', '')}"
            "_FINAL_shaded.png"
        )

        final_stl_path = (
            stl_directory
            / final_stl_name
        )
        final_preview_path = (
            preview_directory
            / final_preview_name
        )
        final_source_name = (
            "rock_tombs_illumination_normalized.png"
        )
        final_source_path = (
            source_directory
            / final_source_name
        )

        shutil.copy2(
            stl_path,
            final_stl_path,
        )
        shutil.copy2(
            preview_path,
            final_preview_path,
        )
        shutil.copy2(
            source_path,
            final_source_path,
        )

        quality_report_path = (
            reports_directory
            / "print_quality_report.json"
        )

        if quality_report is not None:
            quality_report_path.write_text(
                json.dumps(
                    quality_report,
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

        final_3mf_name = (
            f"{product_id}_FINAL.3mf"
        )

        manifest = {
            "product_id": product_id,
            "display_name": display_name,
            "product_type": "relief",
            "dimensions_mm": {
                "width": float(width_mm),
                "depth": float(depth_mm),
            },
            "profile_name": profile_name,
            "production_variant": production_variant,
            "files": {
                "final_stl": (
                    f"STL/{final_stl_name}"
                ),
                "final_preview": (
                    f"PREVIEW/{final_preview_name}"
                ),
                "normalized_source": (
                    f"SOURCE/{final_source_name}"
                ),
                "quality_report": (
                    "REPORTS/print_quality_report.json"
                ),
                "final_3mf": final_3mf_name,
            },
            "status": {
                "stl_ready": True,
                "quality_report_ready": (
                    quality_report is not None
                ),
                "bambu_3mf_ready": False,
            },
        }

        manifest_path = (
            package_directory
            / "production_manifest.json"
        )

        manifest_path.write_text(
            json.dumps(
                manifest,
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

        return {
            "package_directory": package_directory,
            "manifest_path": manifest_path,
            "final_stl_path": final_stl_path,
            "final_preview_path": final_preview_path,
            "final_source_path": final_source_path,
            "quality_report_path": (
                quality_report_path
                if quality_report is not None
                else None
            ),
        }

    @staticmethod
    def _require_file(
        field_name: str,
        path: Path,
    ) -> Path:
        resolved_path = Path(path)

        if not resolved_path.is_file():
            raise FileNotFoundError(
                f"{field_name} does not exist: "
                f"{resolved_path}"
            )

        return resolved_path
