from pathlib import Path
import hashlib
import json
import numpy as np
import trimesh

BASELINE = Path("/private/tmp/atlas_p3_p4_female_head_plus_ratio5p30_neck_shortened_head_forward_centered_dryfit_v1.glb")
REFERENCE = Path("/private/tmp/atlas_p3_p4_female_locked_baseline_male_v2_upper_neck_corrected_v1.glb")
CONTRACT_JSON = Path("/private/tmp/atlas_p3_p4_female_neck_ring2_preservation_contract_v1.json")
CONTRACT_NPZ = Path("/private/tmp/atlas_p3_p4_female_neck_ring2_preservation_contract_v1.npz")
OUTPUT = Path("/private/tmp/atlas_p3_p4_female_ring2_bounded_harmonic_neck_correction_dryfit_v1.glb")

EXPECTED_BASELINE_SHA = "710ae6dfcbf04dc5f3fa52968771290b0322748623058c84065e1961c923e4c9"
MOVE_TOL = 1.0e-12
GEOM_TOL = 1.0e-11

def file_sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def array_sha256(array, dtype):
    canonical = np.ascontiguousarray(np.asarray(array, dtype=dtype))
    return hashlib.sha256(canonical.tobytes()).hexdigest()

def load_scene_parts(path):
    scene = trimesh.load(path, force="scene", process=False)
    head = None
    body = None
    for node_name in scene.graph.nodes_geometry:
        transform, geometry_name = scene.graph[node_name]
        mesh = scene.geometry[geometry_name].copy()
        mesh.apply_transform(transform)
        if len(mesh.vertices) == 19942 and len(mesh.faces) == 39612:
            head = mesh
        elif len(mesh.vertices) == 9287 and len(mesh.faces) == 18476:
            body = mesh
    return head, body

def load_body(path):
    scene = trimesh.load(path, force="scene", process=False)
    candidates = []
    for node_name in scene.graph.nodes_geometry:
        transform, geometry_name = scene.graph[node_name]
        mesh = scene.geometry[geometry_name].copy()
        mesh.apply_transform(transform)
        if len(mesh.vertices) == 9287:
            candidates.append(mesh)
    if len(candidates) != 1:
        raise RuntimeError(f"BODY_RESOLUTION_FAIL={path}|COUNT={len(candidates)}")
    return candidates[0]

for required in (BASELINE, REFERENCE, CONTRACT_JSON, CONTRACT_NPZ):
    if not required.is_file():
        raise SystemExit(f"REQUIRED_FILE_MISSING={required}")

baseline_sha_before = file_sha256(BASELINE)
if baseline_sha_before != EXPECTED_BASELINE_SHA:
    raise SystemExit(
        f"BASELINE_HASH_GATE_FAIL={baseline_sha_before}|EXPECTED={EXPECTED_BASELINE_SHA}"
    )

contract = json.loads(CONTRACT_JSON.read_text(encoding="utf-8"))
with np.load(CONTRACT_NPZ) as data:
    ring0 = data["ring0_ids"].astype(np.int64)
    ring1 = data["ring1_ids"].astype(np.int64)
    ring2 = data["ring2_ids"].astype(np.int64)
    ring3 = data["ring3_ids"].astype(np.int64)
    movable_ids = data["movable_ids"].astype(np.int64)
    fixed_ids = data["fixed_ids"].astype(np.int64)

head, body = load_scene_parts(BASELINE)
reference_body = load_body(REFERENCE)
if head is None or body is None:
    raise SystemExit("BASELINE_HEAD_OR_BODY_RESOLUTION_FAIL")

head_vertices = np.asarray(head.vertices, dtype=np.float64)
head_faces = np.asarray(head.faces, dtype=np.int64)
body_vertices = np.asarray(body.vertices, dtype=np.float64)
body_faces = np.asarray(body.faces, dtype=np.int64)
reference_vertices = np.asarray(reference_body.vertices, dtype=np.float64)
reference_faces = np.asarray(reference_body.faces, dtype=np.int64)

if not np.array_equal(reference_faces, body_faces):
    raise SystemExit("REFERENCE_BODY_FACE_ORDER_GATE_FAIL")
if reference_vertices.shape != body_vertices.shape:
    raise SystemExit("REFERENCE_BODY_VERTEX_ORDER_GATE_FAIL")

expected_hashes = contract["hashes"]
baseline_hash_checks = {
    "head_vertices_sha256": array_sha256(head_vertices, np.float64),
    "head_faces_sha256": array_sha256(head_faces, np.int64),
    "body_vertices_sha256": array_sha256(body_vertices, np.float64),
    "body_faces_sha256": array_sha256(body_faces, np.int64),
    "fixed_vertices_sha256": array_sha256(body_vertices[fixed_ids], np.float64),
    "ring3_vertices_sha256": array_sha256(body_vertices[ring3], np.float64),
}
for key, actual in baseline_hash_checks.items():
    expected = expected_hashes[key]
    if actual != expected:
        raise SystemExit(
            f"PRESERVATION_CONTRACT_INPUT_GATE_FAIL={key}|"
            f"ACTUAL={actual}|EXPECTED={expected}"
        )

all_edges = np.sort(np.asarray(body.edges, dtype=np.int64), axis=1)
unique_edges = np.unique(all_edges, axis=0)
adjacency = [set() for _ in range(len(body_vertices))]
for a, b in unique_edges:
    a, b = int(a), int(b)
    adjacency[a].add(b)
    adjacency[b].add(a)

reference_delta = reference_vertices - body_vertices
if np.abs(reference_delta[:, 1]).max() > GEOM_TOL:
    raise SystemExit("REFERENCE_CONTAINS_Y_DISPLACEMENT")

new_delta = np.zeros_like(body_vertices)
new_delta[np.ix_(ring0, [0, 2])] = reference_delta[np.ix_(ring0, [0, 2])]
new_delta[np.ix_(ring1, [0, 2])] = reference_delta[np.ix_(ring1, [0, 2])]

ring1_set = set(int(v) for v in ring1)
ring2_set = set(int(v) for v in ring2)
ring2_lookup = {int(v): i for i, v in enumerate(ring2)}

A = np.zeros((len(ring2), len(ring2)), dtype=np.float64)
B = np.zeros((len(ring2), 2), dtype=np.float64)

for row, vertex_id in enumerate(ring2):
    neighbors = adjacency[int(vertex_id)]
    if not neighbors:
        raise SystemExit(f"RING2_ISOLATED_VERTEX={int(vertex_id)}")
    A[row, row] = float(len(neighbors))
    for neighbor in neighbors:
        if neighbor in ring2_set:
            A[row, ring2_lookup[neighbor]] -= 1.0
        elif neighbor in ring1_set:
            B[row] += reference_delta[neighbor, [0, 2]]
        else:
            # Ring 3 and all deeper geometry are fixed at zero displacement.
            pass

if np.linalg.matrix_rank(A) != len(ring2):
    raise SystemExit("RING2_HARMONIC_SYSTEM_SINGULAR")

ring2_solution = np.linalg.solve(A, B)
new_delta[ring2, 0] = ring2_solution[:, 0]
new_delta[ring2, 2] = ring2_solution[:, 1]

corrected_vertices = body_vertices + new_delta
corrected_body = trimesh.Trimesh(
    vertices=corrected_vertices,
    faces=body_faces.copy(),
    process=False,
    validate=False,
)

displacement = np.linalg.norm(new_delta, axis=1)
fixed_moved = fixed_ids[displacement[fixed_ids] > MOVE_TOL]
ring3_moved = ring3[displacement[ring3] > MOVE_TOL]
y_displacement_max = float(np.abs(new_delta[:, 1]).max())

if len(fixed_moved) != 0:
    raise SystemExit(f"FIXED_DOMAIN_MOVEMENT_GATE_FAIL={len(fixed_moved)}")
if len(ring3_moved) != 0:
    raise SystemExit(f"RING3_MOVEMENT_GATE_FAIL={len(ring3_moved)}")
if y_displacement_max > MOVE_TOL:
    raise SystemExit(f"BODY_Y_MOVEMENT_GATE_FAIL={y_displacement_max}")
if not np.array_equal(corrected_body.faces, body_faces):
    raise SystemExit("BODY_FACE_PRESERVATION_GATE_FAIL")
if array_sha256(corrected_vertices[fixed_ids], np.float64) != expected_hashes["fixed_vertices_sha256"]:
    raise SystemExit("FIXED_VERTEX_HASH_GATE_FAIL")
if array_sha256(head_vertices, np.float64) != expected_hashes["head_vertices_sha256"]:
    raise SystemExit("HEAD_VERTEX_HASH_GATE_FAIL")
if array_sha256(head_faces, np.int64) != expected_hashes["head_faces_sha256"]:
    raise SystemExit("HEAD_FACE_HASH_GATE_FAIL")

tri_before = body_vertices[body_faces]
tri_after = corrected_vertices[body_faces]
normal_before = np.cross(
    tri_before[:, 1] - tri_before[:, 0],
    tri_before[:, 2] - tri_before[:, 0],
)
normal_after = np.cross(
    tri_after[:, 1] - tri_after[:, 0],
    tri_after[:, 2] - tri_after[:, 0],
)
area_before = np.linalg.norm(normal_before, axis=1) * 0.5
area_after = np.linalg.norm(normal_after, axis=1) * 0.5
valid_before = area_before > 1.0e-14
reversed_faces = np.flatnonzero(
    valid_before
    & ((normal_before * normal_after).sum(axis=1) <= 0.0)
)
degenerate_after = np.flatnonzero(area_after <= 1.0e-14)
area_ratio = area_after[valid_before] / area_before[valid_before]


from collections import Counter

unit_delta = new_delta.copy()
ring_class = np.full(len(body_vertices), 4, dtype=np.int64)
ring_class[ring0] = 0
ring_class[ring1] = 1
ring_class[ring2] = 2
ring_class[ring3] = 3

def evaluate_amplitude(alpha):
    candidate_vertices = body_vertices + unit_delta * float(alpha)
    triangles = candidate_vertices[body_faces]
    normals = np.cross(
        triangles[:, 1] - triangles[:, 0],
        triangles[:, 2] - triangles[:, 0],
    )
    areas = np.linalg.norm(normals, axis=1) * 0.5
    dots = (normal_before * normals).sum(axis=1)
    reversed_ids = np.flatnonzero(valid_before & (dots <= 0.0))
    degenerate_ids = np.flatnonzero(areas <= 1.0e-14)
    ratios = areas[valid_before] / area_before[valid_before]
    ring1_residual = np.linalg.norm(
        (unit_delta[ring1] * float(alpha)) - reference_delta[ring1],
        axis=1,
    )
    return {
        "alpha": float(alpha),
        "reversed": reversed_ids,
        "degenerate": degenerate_ids,
        "ratio_min": float(ratios.min()),
        "ratio_p01": float(np.percentile(ratios, 1)),
        "ratio_p05": float(np.percentile(ratios, 5)),
        "ring1_residual_mean": float(ring1_residual.mean()),
        "ring1_residual_max": float(ring1_residual.max()),
    }

full = evaluate_amplitude(1.0)
class_counts = Counter()
for face_id in full["reversed"]:
    classes = tuple(sorted(int(v) for v in ring_class[body_faces[face_id]]))
    class_counts[classes] += 1

print("=== FULL-AMPLITUDE REVERSAL LOCATION ===")
print(f"REVERSED_FACES={len(full['reversed'])}")
print(f"DEGENERATE_FACES={len(full['degenerate'])}")
for classes, face_count in sorted(class_counts.items()):
    print(
        f"FACE_RING_CLASSES={classes}|REVERSED_FACE_COUNT={face_count}"
    )

print()
print("=== COARSE AMPLITUDE SWEEP ===")
print(
    "FIELDS=ALPHA,REVERSED,DEGENERATE,AREA_RATIO_MIN,"
    "AREA_RATIO_P01,RING1_REFERENCE_RESIDUAL_MEAN,"
    "RING1_REFERENCE_RESIDUAL_MAX"
)
for alpha in np.linspace(0.0, 1.0, 21):
    result = evaluate_amplitude(alpha)
    print(
        f"ALPHA={result['alpha']:.3f}|"
        f"REVERSED={len(result['reversed'])}|"
        f"DEGENERATE={len(result['degenerate'])}|"
        f"AREA_RATIO_MIN={result['ratio_min']:.12f}|"
        f"AREA_RATIO_P01={result['ratio_p01']:.12f}|"
        f"RING1_REFERENCE_RESIDUAL_MEAN={result['ring1_residual_mean']:.12f}|"
        f"RING1_REFERENCE_RESIDUAL_MAX={result['ring1_residual_max']:.12f}"
    )

low = 0.0
high = 1.0
for _ in range(50):
    middle = (low + high) / 2.0
    result = evaluate_amplitude(middle)
    safe = (
        len(result["reversed"]) == 0
        and len(result["degenerate"]) == 0
        and result["ratio_min"] > 0.0
    )
    if safe:
        low = middle
    else:
        high = middle

safe_result = evaluate_amplitude(low)
unsafe_result = evaluate_amplitude(high)

print()
print("=== NUMERICAL SAFE LIMIT ===")
print(f"MAX_SAFE_ALPHA_APPROX={low:.15f}")
print(f"FIRST_UNSAFE_ALPHA_APPROX={high:.15f}")
print(f"SAFE_REVERSED_FACES={len(safe_result['reversed'])}")
print(f"SAFE_DEGENERATE_FACES={len(safe_result['degenerate'])}")
print(f"SAFE_AREA_RATIO_MIN={safe_result['ratio_min']:.15f}")
print(f"SAFE_RING1_REFERENCE_RESIDUAL_MEAN={safe_result['ring1_residual_mean']:.12f}")
print(f"SAFE_RING1_REFERENCE_RESIDUAL_MAX={safe_result['ring1_residual_max']:.12f}")
print(f"UNSAFE_REVERSED_FACES={len(unsafe_result['reversed'])}")
print()
print("AMPLITUDE_SELECTION_PERFORMED=NO")
print("CORRECTION_EXPORTED=NO")
print("DEFORMATION_PERSISTED=NO")
print(f"BASELINE_SHA256_AFTER={file_sha256(BASELINE)}")
print(f"BASELINE_UNCHANGED={file_sha256(BASELINE) == baseline_sha_before}")
print("RING3_AND_BELOW_CHANGED=NO")
print("HEAD_CHANGED=NO")
print("NEXT=DECIDE_IF_SAFE_AMPLITUDE_RETAINS_USEFUL_NECK_CORRECTION")
print("PRODUCTION_GEOMETRY_AUTHORIZATION=NO")
