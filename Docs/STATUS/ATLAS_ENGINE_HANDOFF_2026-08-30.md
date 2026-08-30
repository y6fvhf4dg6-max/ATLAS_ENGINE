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
