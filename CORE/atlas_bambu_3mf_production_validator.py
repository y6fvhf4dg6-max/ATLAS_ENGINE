from __future__ import annotations

import json
import math
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree


_REQUIRED_MEMBERS = (
    "Metadata/model_settings.config",
    "Metadata/project_settings.config",
    "Metadata/plate_1.json",
)

_REPAIR_FIELDS = (
    "edges_fixed",
    "degenerate_facets",
    "facets_removed",
    "facets_reversed",
    "backwards_edges",
)


def _parse_positive_float(value, *, name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc

    if not math.isfinite(result) or result <= 0:
        raise ValueError(f"{name} must be positive and finite")

    return result


@dataclass(frozen=True)
class AtlasBambu3MFProductionValidation:
    object_face_count: int
    part_face_count: int
    part_count: int
    face_counts_match: bool
    mesh_repair_count: int
    has_mesh_repairs: bool
    printer_model: str
    nozzle_diameter_mm: float
    layer_height_mm: float
    support_enabled: bool
    bed_type: str
    is_structurally_valid: bool


class AtlasBambu3MFProductionValidator:
    @classmethod
    def validate(
        cls,
        path: str | Path,
    ) -> AtlasBambu3MFProductionValidation:
        archive_path = Path(path)

        if not archive_path.is_file():
            raise FileNotFoundError(archive_path)

        try:
            with zipfile.ZipFile(archive_path, "r") as archive:
                names = set(archive.namelist())

                missing = [
                    name
                    for name in _REQUIRED_MEMBERS
                    if name not in names
                ]
                if missing:
                    raise ValueError(
                        "missing required metadata: "
                        + ", ".join(missing)
                    )

                model_settings = archive.read(
                    "Metadata/model_settings.config"
                )
                project_settings = json.loads(
                    archive.read(
                        "Metadata/project_settings.config"
                    )
                )
                plate_settings = json.loads(
                    archive.read(
                        "Metadata/plate_1.json"
                    )
                )
        except zipfile.BadZipFile as exc:
            raise ValueError(
                "path must reference a valid 3MF archive"
            ) from exc

        try:
            root = ElementTree.fromstring(model_settings)
        except ElementTree.ParseError as exc:
            raise ValueError(
                "model settings metadata must be valid XML"
            ) from exc

        object_face_nodes = root.findall(
            ".//object/metadata[@face_count]"
        )
        if len(object_face_nodes) != 1:
            raise ValueError(
                "model settings must contain exactly one "
                "object face count"
            )

        object_face_count = int(
            object_face_nodes[0].attrib["face_count"]
        )

        mesh_stats = root.findall(".//object/part/mesh_stat")
        if not mesh_stats:
            raise ValueError(
                "model settings must contain part mesh statistics"
            )

        part_face_counts = [
            int(node.attrib["face_count"])
            for node in mesh_stats
        ]
        part_face_count = sum(part_face_counts)

        mesh_repair_count = 0
        for node in mesh_stats:
            for field in _REPAIR_FIELDS:
                mesh_repair_count += int(
                    node.attrib.get(field, "0")
                )

        printer_model = str(
            project_settings.get("printer_model", "")
        ).strip()
        if not printer_model:
            raise ValueError(
                "project settings must contain printer_model"
            )

        nozzle_diameter_mm = _parse_positive_float(
            plate_settings.get("nozzle_diameter"),
            name="nozzle_diameter",
        )

        layer_height_mm = _parse_positive_float(
            project_settings.get("layer_height"),
            name="layer_height",
        )

        enable_support = str(
            project_settings.get("enable_support", "")
        ).strip()
        if enable_support not in {"0", "1"}:
            raise ValueError(
                "enable_support must be '0' or '1'"
            )

        bed_type = str(
            plate_settings.get("bed_type", "")
        ).strip()
        if not bed_type:
            raise ValueError(
                "plate settings must contain bed_type"
            )

        face_counts_match = (
            object_face_count == part_face_count
        )
        has_mesh_repairs = mesh_repair_count > 0

        return AtlasBambu3MFProductionValidation(
            object_face_count=object_face_count,
            part_face_count=part_face_count,
            part_count=len(mesh_stats),
            face_counts_match=face_counts_match,
            mesh_repair_count=mesh_repair_count,
            has_mesh_repairs=has_mesh_repairs,
            printer_model=printer_model,
            nozzle_diameter_mm=nozzle_diameter_mm,
            layer_height_mm=layer_height_mm,
            support_enabled=(enable_support == "1"),
            bed_type=bed_type,
            is_structurally_valid=(
                face_counts_match
                and not has_mesh_repairs
            ),
        )
