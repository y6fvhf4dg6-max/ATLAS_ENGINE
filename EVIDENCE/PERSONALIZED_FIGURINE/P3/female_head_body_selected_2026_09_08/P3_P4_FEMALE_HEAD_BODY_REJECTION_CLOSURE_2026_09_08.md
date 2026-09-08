# P-3/P-4 Female Head–Body Pairing — Rejection Closure

Date: 2026-09-08

## Final decision

- `FINAL_HUMAN_VISUAL_GATE=FAIL`
- `HEAD_BODY_PAIRING=REJECTED`
- `ATTEMPT_BUDGET=EXHAUSTED`
- `NEW_GEOMETRY_ALLOWED=NO`
- `PRODUCTION_GEOMETRY_AUTHORIZATION=NO`
- `PHASE9_AUTHORIZATION=NO`

The previously selected female assembly in this directory remains a historical technical checkpoint only. It is superseded by this closure and must not be treated as a production-selected female geometry.

## Locked source that remained unchanged

Accepted dry-fit baseline:

- File: `atlas_p3_p4_female_head_plus_ratio5p30_neck_shortened_head_forward_centered_dryfit_v1.glb`
- SHA256: `710ae6dfcbf04dc5f3fa52968771290b0322748623058c84065e1961c923e4c9`
- Body vertices: 9,287
- Body faces: 18,476
- Visible head identity was locked.
- Arm, shoulder and torso exclusion was enforced throughout controlled trials.

Zero-deformation extracted inputs:

- Head SHA256: `749974cd50423411cd9ae5e703d101bb3a6caee7d169469ca29a5ecff6bbd22f`
- Body SHA256: `9740ba5308bbd5dfaa065967119fed3b4bd753aed8e697e66eda1478d7c848de`

## Decisive incompatibility measurement

The head underside and body neck were structurally incompatible:

- Head boundary: 302 vertices
- Head X width: 1.027721405029
- Body original boundary: 96 vertices
- Body first-inner boundary: 48 vertices
- Body-inner X width: 0.538854360580
- Body/head X-width ratio: 0.524319487697
- Head-to-body nearest XZ P95: 0.247769213281
- Head-to-body nearest XZ maximum: 0.261169899355

Only 5 of 302 head-boundary vertices lay inside the exact body-neck envelope. No closed natural neck loop was present.

## Rejected routes and lessons

### 1. Deep-support body correction

Rejected because it moved 1,253 fixed-domain vertices and violated strict Ring-2 preservation.

### 2. Ring-2 bounded harmonic body correction

Full amplitude created 17 reversed faces. The numerical safe limit was approximately:

- Maximum safe alpha: 0.152629002346539
- Minimum area ratio: 0.822481570595667

At that safe amplitude the residual neck mismatch remained too large to be useful. Route rejected.

### 3. Zero-deformation 302→48 strip + seam-aware DP

Topology passed, but the human visual gate failed with a floating head, black separation and shelf-like bridge.

Rejected output SHA256:

`a11a02ddbba96c024fba7f3492170c023dc733d0e808a90b2eb9c8d79b9baf2a`

Lesson: watertight topology does not establish anatomical continuity.

### 4. Horizontal head-underside section search

No usable natural section was found. The best scanned section at Y=5.165 still had a body-relative width ratio of 1.576081770392. Route rejected.

### 5. Direct 142→96 annular underside retopology

A strict invisible head domain was found:

- Head Ring 0: 302 vertices
- Ring 1: 154 vertices
- Ring 2: 171 vertices
- Removed head faces: 810
- Retained head frontier: 142 vertices
- Ring 3 and above: exactly preserved

The direct 142→96 annulus was watertight and numerically valid, but visually retained the floating-head separation and created a thin shelf.

Rejected output SHA256:

`5a6e99462152285f4c5a2576f38d074ea6b5aeb63536dda8a3b53c0220a4e7b8`

### 6. Vertical collar at Y=5.280 plus direct upper annulus

Y=5.280 was the first clean single-loop collar level:

- Collar height: 0.131822376251
- Above head frontier maximum: 0.014958648682
- Lower body loop: 96 unchanged vertices
- New upper loop: 96 vertices
- Collar faces: 192
- Upper annulus faces: 238

Topology and preservation passed. However, all 96 upper collar-to-annulus seam edges exceeded 90 degrees:

- Mean: 141.388117 degrees
- Maximum: 170.757359 degrees

The visual gate confirmed a jagged outward shelf and wing-like projections.

Rejected output SHA256:

`74df51ab416e0559cd32b473ebf42ef27fac7c76fea231f6eb5c4ceb1315f594`

### 7. Final five-ring 142→46 reconstruction

The final bounded body domain was selected at Rings 0–3:

- Domain vertices: 238
- Removed body faces: 334
- Fixed body frontier: 46 vertices
- Ring 4 and below: exactly fixed
- New matched rings: 5 × 142 vertices
- New faces: 1,608

The numerical gate passed:

- Vertices: 29,939
- Faces: 58,516
- Boundary edges: 0
- Nonmanifold edges: 0
- Degenerate faces: 0
- Watertight: true
- Winding consistent: true

The human visual gate failed decisively. The gradual surface formed an accordion/collar structure with vertical fins and sharp projections in front, profile, three-quarter and rear views.

Rejected output SHA256:

`aea417e6352c15d42fb060c1d7c8070ea5b95c08685399a5d7908bfe07382c0c`

## Final engineering conclusion

This Rodin female head and MakeHuman ratio-5.30 female body are not a viable production pairing under the locked identity and bounded neck-domain requirements. Repeated bridge, annulus and collar variants merely relocate the fundamental interface mismatch.

Do not resume this pairing by adding more rings, stronger smoothing, wider body deformation or another DP weight sweep.

A future female assembly must begin with one of these materially different inputs:

1. a body whose native neck envelope is compatible with the head underside; or
2. a head source generated with a real, narrow anatomical neck interface intended for full-body attachment.

## Preservation and promotion policy

- Original sources remain unchanged.
- Rejected temporary GLB candidates are not promoted into repository evidence.
- Logs, scripts, contracts and visual evidence are retained for reproducibility and to prevent repeating rejected routes.
- No production geometry is authorized.
- Phase 9 remains unauthorized.
