# ATLAS_ENGINE HANDOFF — 2026-08-30

## Authority

Primary continuity authority:

1. `Docs/START_HERE.md`
2. `Docs/STATUS/CURRENT_STATUS.md`
3. `Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-08-08.md`

Read the latest appended record:

`PHASE8_ITEM11_15_PHYSICAL_IDENTITY_RECOVERY_PLAN_2026_08_30`

This handoff supersedes the operational stopping point in
`ATLAS_ENGINE_HANDOFF_2026-08-28.md`.
The older handoff remains historical.

## Current state

Phase 8: `ACTIVE / HOLD-BLOCKED`

Main Checklist Item 11:
`PHYSICAL REPRESENTATION GATE — ACTIVE / HOLD-BLOCKED`

Active subitem:
`11.15 — PHYSICAL IDENTITY RECOVERY`

Phase 9:
`NOT AUTHORIZED / NOT STARTED`

Safe pushed checkpoint at handoff creation:

`791b98b5b5e02d5f4af22be9a4141db6677cacee`

## Exact-scope dirty work to preserve

- `CORE/atlas_canonical_head_region_aware_relief_depth_policy.py`
- `Test/test_canonical_head_region_aware_relief_depth_policy.py`
- `CORE/atlas_canonical_head_local_facial_feature_z_correction.py`
- `Test/test_canonical_head_local_facial_feature_z_correction.py`

Do not stage, restore, delete or overwrite these files without resolving the
active Item-11.15 recovery work.

All unrelated dirty work remains protected.

## Active recovery sequence

R0 Freeze and preserve current evidence
R1 Representation failure decomposition
R2 Canonical geometry sufficiency audit
R3 Projection architecture decision
R4 Semantic locality and ownership
R5 Multi-scale facial geometry preservation
R6 Physical-depth allocation
R7 Digital validation gate
R8 Controlled physical validation
R9 Item 11.15 closure decision

## Exact next step

Begin:

`R0 — Freeze and preserve current evidence`

Then:

`R1 — Representation failure decomposition`

Do not return to arbitrary threshold tuning.

## Locked terminal protocol

- one meaningful terminal command per turn;
- show active checklist;
- command output through `tee`;
- copy same output with `/usr/bin/pbcopy`;
- wait for pasted output;
- exact-scope Git only;
- never `git add .`;
- no Phase 9.

## Exact first instruction

> Continue ATLAS_ENGINE at Phase 8 Main Checklist Item 11.15 — Physical Identity Recovery. Verify Git state and the latest 2026-08-30 recovery-plan record first. Preserve the four exact-scope dirty Item-11.15 files and protected unrelated work. Begin only at R0, then R1. Do not resume heuristic threshold tuning. Phase 9 is not authorized.

## R1.9 — Earliest-loss causal decision — 2026-08-30

Status: `CLOSED — CAUSAL STAGE IDENTIFIED`

Real-candidate stage decomposition established:

- robust global 2.0 mm base transfer preserves source-depth ordering with very
  high correlation and is not the earliest demonstrated major distortion;
- the earliest demonstrated serious identity-bearing distortion occurs in the
  `region-aware local semantic Z allocation` stage;
- nose-base source/base correlation was `1.000000`, then source/local fell to
  `0.757943`;
- philtrum source/base correlation was `1.000000`, then source/local fell to
  `-0.684747`;
- fixed-point local nose ordering is a separate downstream distortion mechanism,
  not the earliest cause;
- ordering modified 971 active raster samples and increased relief-ceiling
  saturation from 92 to 138 samples, including 46 ordering-induced ceiling
  samples;
- ordering partially repaired nose-base and philtrum ordering while degrading
  upper-lip and lower-lip source correlation and propagating saturation.

Causal decision:

`EARLIEST_DEMONSTRATED_IDENTITY_DISTORTION_STAGE =
REGION_AWARE_LOCAL_SEMANTIC_Z_ALLOCATION`

Downstream finding:

`FIXED_POINT_ORDERING =
SECONDARY_CROSS_REGION_PROPAGATION_AND_CEILING_SATURATION_MECHANISM`

Epistemic boundary:

This does not establish that a 2.0 mm physical relief budget is ultimately
sufficient, does not establish physical likeness, and does not authorize
physical-validation closure or Phase 9. It establishes only the earliest
demonstrated serious distortion within the measured current real-candidate
representation pipeline.

R1 repair remains intentionally unstarted. The next recovery stage is
`R2 — Canonical geometry sufficiency audit`.

## PHASE8_ITEM11_15_RECOVERY_R2_CANONICAL_GEOMETRY_SUFFICIENCY_2026_08_30

- Status: `CLOSED — CAUSAL SUFFICIENCY DECISION`
- Decision: `CANONICAL_NOT_EXONERATED_BUT_NOT_PRIMARY_CAUSE`
- Exact personal canonical mesh evidence: 5023 vertices.
- Canonical identity change is measurable: bbox-normalized RMS `0.010425098`, P95 `0.020443063`, max `0.035519139`.
- No canonical absolute-likeness acceptance threshold was applied.
- Metric 3D ground truth was not proven by this evidence.
- Therefore absolute canonical likeness sufficiency remains unproven.
- Canonical geometry is not proven to be the primary cause of the current physical-representation failure.
- R1 remains causal authority for the earliest measured severe loss: `REGION_AWARE_LOCAL_SEMANTIC_Z_ALLOCATION`.
- Secondary damage mechanism remains: `ORDERING_PROPAGATION_AND_CEILING_SATURATION`.
- No repair was performed during R2.
- Next: `R3 — Projection Architecture Decision`.
- Phase 9 remains `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_ITEM11_15_RECOVERY_R3_PROJECTION_ARCHITECTURE_2026_08_30

- Status: `CLOSED — ARCHITECTURE DECISION`
- Selected architecture: `C_VISIBILITY_AWARE_NORMAL_GRADIENT_DOMAIN`
- Required new boundary: `VISIBLE_CANONICAL_SURFACE_TO_RASTER_NORMAL_CORRESPONDENCE`
- Canonical correspondence: preserve through visible-surface rasterization.
- Primary geometric signal: canonical surface normals / derived gradients.
- Semantic masks: `CONSTRAINT_WEIGHT_AUDIT_NOT_DIRECT_Z_GENERATOR`.
- Depth reconstruction: `BOUNDED_NORMAL_GRADIENT_INTEGRATION`.
- Current scalar-depth path: `CONTROL_BASELINE_ONLY`.
- R1 primary failure remains: `REGION_AWARE_LOCAL_SEMANTIC_Z_ALLOCATION`.
- R1 secondary damage remains: `ORDERING_PROPAGATION_AND_CEILING_SATURATION`.
- R2 decision remains: `CANONICAL_NOT_EXONERATED_BUT_NOT_PRIMARY_CAUSE`.
- Implementation authorized by R3 decision alone: `NO`.
- Next recovery stage: `R4 — Semantic Locality / Ownership`.
- Phase 9: `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_ITEM11_15_RECOVERY_R4_SEMANTIC_LOCALITY_OWNERSHIP_2026_08_30

- Status: `CLOSED — SEMANTIC ROLE DECISION`.
- Semantic role: `CONSTRAINT_WEIGHT_AUDIT_NOT_DIRECT_GEOMETRY_GENERATOR`.
- Geometry owner: `CANONICAL_VISIBLE_SURFACE_NORMAL_GRADIENT_SIGNAL`.
- Region masks remain available for weighting, explicit local constraints, and regional audit.
- Region masks may not generate direct signed anatomical Z.
- Fixed anatomical Z offsets: `NOT RETAINED`.
- Nose-base residual Z generator: `NOT RETAINED`.
- Ordering propagation as geometry generator: `NOT RETAINED`.
- Ordering may return only as an audit or explicit constraint if later independently justified.
- Global physical depth bounds: `RETAINED`.
- Source canonical geometry remains the primary geometric signal.
- Implementation authorized by R4 decision alone: `NO`.
- Next recovery stage: `R5 — Multi-scale Facial Geometry`.
- Phase 9: `NOT AUTHORIZED / NOT STARTED`.

## PHASE8_ITEM11_15_RECOVERY_R5_MULTISCALE_FACIAL_GEOMETRY_2026_08_30

- Status: `CLOSED — MULTI-SCALE OWNERSHIP DECISION`.
- Identity owner: `CANONICAL_GEOMETRY`.
- Multi-scale signal owner: `CANONICAL_VISIBLE_SURFACE_NORMAL_GRADIENT`.
- External residual detail role: `BOUNDED_REFINEMENT_NOT_SECOND_IDENTITY_MODEL`.
- Semantic masks do not own facial frequency content.
- Scale parameterization: `PHYSICAL_MM_FIRST_RASTER_SAMPLES_DERIVED`.
- Raster radii must be derived from physical scale and sample pitch.
- Current `structure_radius=5` is only a baseline at `0.25 mm/sample`; it is not a universal physical constant.
- At the current pitch, radius 5 corresponds to `1.25 mm` radius and an `11 x 11` / `2.75 mm` kernel footprint.
- Broad structure bypasses high-frequency detail limiting by default.
- Fine/detail geometry may use bounded gradient limiting.
- Exact production facial frequency-band thresholds in mm are `NOT YET SELECTED`.
- Implementation authorized by R5 decision alone: `NO`.
- Next recovery stage: `R6 — Physical-depth Allocation`.
- Phase 9: `NOT AUTHORIZED / NOT STARTED`.
