from pathlib import Path
import hashlib
import numpy as np
import trimesh

ROOT = Path("/private/tmp/atlas_makehuman_source/makehuman")
BASE = ROOT / "data/3dobjs/base.obj"
TARGET_ROOT = ROOT / "data/targets"
OUTPUT = Path("/private/tmp/atlas_p3_p4_makehuman_generic_male_compact_body_v1.glb")

TARGETS = [
    ("macrodetails/african-male-young.target", 1.0 / 3.0, "MALE_ETHNIC_BLEND"),
    ("macrodetails/asian-male-young.target", 1.0 / 3.0, "MALE_ETHNIC_BLEND"),
    ("macrodetails/caucasian-male-young.target", 1.0 / 3.0, "MALE_ETHNIC_BLEND"),
    ("armslegs/upperlegs-height-decr.target", 0.60, "COMPACT_PROPORTION"),
    ("armslegs/lowerlegs-height-decr.target", 0.60, "COMPACT_PROPORTION"),
    ("measure/measure-shoulder-dist-decr.target", 0.35, "COMPACT_PROPORTION"),
    ("measure/measure-napetowaist-dist-decr.target", 0.35, "COMPACT_PROPORTION"),
    ("measure/measure-waisttohip-dist-decr.target", 0.25, "COMPACT_PROPORTION"),
]

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def load_base_obj(path):
    vertices = []
    body_faces = []
    active_group = None

    with path.open("r", encoding="utf-8", errors="strict") as handle:
        for line in handle:
            if line.startswith("v "):
                fields = line.split()
                vertices.append([float(fields[1]), float(fields[2]), float(fields[3])])
            elif line.startswith("g "):
                active_group = line.split(maxsplit=1)[1].strip()
            elif line.startswith("f ") and active_group == "body":
                polygon = []
                for token in line.split()[1:]:
                    polygon.append(int(token.split("/")[0]) - 1)
                for index in range(1, len(polygon) - 1):
                    body_faces.append([polygon[0], polygon[index], polygon[index + 1]])

    return np.asarray(vertices, dtype=np.float64), np.asarray(body_faces, dtype=np.int64)

def apply_target(vertices, target_path, weight):
    rows = 0
    maximum_index = -1

    with target_path.open("r", encoding="utf-8", errors="strict") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            fields = stripped.split()
            vertex_index = int(fields[0])
            delta = np.asarray(
                [float(fields[1]), float(fields[2]), float(fields[3])],
                dtype=np.float64,
            )
            if vertex_index >= len(vertices):
                raise RuntimeError(
                    f"TARGET_INDEX_OUT_OF_RANGE={vertex_index}|VERTICES={len(vertices)}"
                )
            vertices[vertex_index] += weight * delta
            rows += 1
            maximum_index = max(maximum_index, vertex_index)

    return rows, maximum_index

print("=== LOCKED SOURCES ===")
print(f"BASE={BASE}")
print(f"BASE_SHA256={sha256(BASE)}")

raw_vertices, body_faces = load_base_obj(BASE)
if len(raw_vertices) != 19158:
    raise RuntimeError(f"UNEXPECTED_RAW_VERTEX_COUNT={len(raw_vertices)}")
if len(body_faces) != 26756:
    raise RuntimeError(f"UNEXPECTED_BODY_TRIANGLE_COUNT={len(body_faces)}")

print(f"RAW_VERTICES={len(raw_vertices)}")
print(f"BODY_TRIANGLES={len(body_faces)}")
print(f"BODY_FACE_INDEX_MIN={int(body_faces.min())}")
print(f"BODY_FACE_INDEX_MAX={int(body_faces.max())}")

deformed = raw_vertices.copy()
male_stage = raw_vertices.copy()

print("\n=== APPLIED TARGET STACK ===")
for relative_path, weight, target_class in TARGETS:
    target_path = TARGET_ROOT / relative_path
    if not target_path.is_file():
        raise RuntimeError(f"MISSING_TARGET={target_path}")
    rows, maximum_index = apply_target(deformed, target_path, weight)
    if target_class == "MALE_ETHNIC_BLEND":
        apply_target(male_stage, target_path, weight)
    print(
        f"TARGET={relative_path}|CLASS={target_class}|WEIGHT={weight:.12f}"
        f"|ROWS={rows}|MAX_INDEX={maximum_index}|SHA256={sha256(target_path)}"
    )

male_displacement = np.linalg.norm(male_stage - raw_vertices, axis=1)
final_displacement = np.linalg.norm(deformed - raw_vertices, axis=1)

maximum_body_index = int(body_faces.max())
body_vertices = deformed[: maximum_body_index + 1].copy()

mesh = trimesh.Trimesh(
    vertices=body_vertices,
    faces=body_faces,
    process=False,
    validate=False,
)

if len(mesh.vertices) != 13380:
    raise RuntimeError(f"UNEXPECTED_BODY_VERTEX_COUNT={len(mesh.vertices)}")
if len(mesh.faces) != 26756:
    raise RuntimeError(f"UNEXPECTED_OUTPUT_FACE_COUNT={len(mesh.faces)}")

mesh.export(OUTPUT)

print("\n=== GENERIC MALE BODY OUTPUT ===")
print(f"OUTPUT={OUTPUT}")
print(f"VERTICES={len(mesh.vertices)}")
print(f"FACES={len(mesh.faces)}")
print(f"BOUNDS_MIN={mesh.bounds[0].tolist()}")
print(f"BOUNDS_MAX={mesh.bounds[1].tolist()}")
print(f"EXTENTS={mesh.extents.tolist()}")
print(f"CONNECTED_COMPONENTS={len(mesh.split(only_watertight=False))}")
print(f"BOUNDARY_EDGES_EXPECTED=0")
print(f"IS_WATERTIGHT={mesh.is_watertight}")
print(f"IS_WINDING_CONSISTENT={mesh.is_winding_consistent}")
print(f"MALE_BLEND_DISPLACEMENT_P95={float(np.percentile(male_displacement, 95)):.12f}")
print(f"MALE_BLEND_DISPLACEMENT_MAX={float(male_displacement.max()):.12f}")
print(f"FINAL_DISPLACEMENT_P95={float(np.percentile(final_displacement, 95)):.12f}")
print(f"FINAL_DISPLACEMENT_MAX={float(final_displacement.max()):.12f}")
print(f"SIZE_BYTES={OUTPUT.stat().st_size}")
print(f"SHA256={sha256(OUTPUT)}")

if not mesh.is_watertight or not mesh.is_winding_consistent:
    raise RuntimeError("MALE_BODY_TOPOLOGY_GATE=FAIL")

print("STATUS=PASS")
print("RODIN_MALE_ATTACHED=NO")
print("NEXT=GENERATE_INDEPENDENT_MALE_BODY_VISUAL")
