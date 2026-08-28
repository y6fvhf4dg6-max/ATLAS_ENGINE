# ATLAS_ENGINE HANDOFF — 2026-08-28

## 1. Purpose

This file is the current continuity / disaster-recovery handoff for ATLAS_ENGINE.

It records:

- working discipline;
- current verified repository state;
- current Main Checklist state;
- exact Phase 8 stopping point;
- Item 10 progress;
- test status;
- Phase 9 authorization boundary;
- protected unrelated dirty work;
- exact next step for a new session.

This handoff is subordinate to:

1. current verified Git state;
2. current authority documents;
3. explicit current user instruction;
4. verified persistent evidence.

Primary authority documents:

- `Docs/START_HERE.md`
- `Docs/STATUS/CURRENT_STATUS.md`
- `Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-08-08.md`

---

## 2. Working Discipline — LOCKED

Environment:

- macOS Apple Silicon
- repository: `/Users/Kubi/ATLAS_ENGINE`
- Python venv: `.venv`
- tests: `pytest`

Terminal protocol:

- exactly one meaningful terminal step per assistant turn;
- every terminal step must show output;
- output must be persisted with `tee`;
- the same output must be copied with `pbcopy`;
- wait for user-pasted output before issuing the next command.

Development sequence:

`read -> verify -> apply approved plan -> test -> persist -> commit -> push -> verify`

Checklist discipline:

- show the active checklist before every meaningful step;
- only one subitem may be active `[~]`;
- no silent scope expansion;
- no unrelated refactors;
- no new files/contracts without explicit approval where architecture/scope changes;
- no phase transition without explicit authorization.

Test discipline:

- RED-first where implementation is required;
- focused tests;
- related regression;
- full regression when CORE changes;
- Closure Challenge before closure;
- corrective RED / minimal fix if Closure Challenge fails.

Git safety:

- never use `git add .`;
- never broad reset/restore/clean;
- never force push;
- stage exact target paths only;
- inspect staged diff;
- run `git diff --cached --check`;
- commit known scope only;
- push `origin main`;
- verify `HEAD == origin/main`.

Epistemic boundaries:

- do not invent thresholds;
- do not invent support scores;
- do not invent acceptance criteria;
- do not infer metric units;
- repeatability / precision / trueness / accuracy remain separate concepts;
- no metric anatomical claim without verified metric ground truth;
- no Phase 9 until explicit Phase 8 GO + LOCK.

---

## 3. Main Checklist — LOCKED ORDER

1. Canonical Identity Representation
2. Canonical Correspondence Semantics
3. Hybrid Bounded-Detail Bridge
4. Six-View Quantitative Evidence
5. FLAME / PRNet Evidence Closure
6. Silhouette / Profile Closure
7. Identity Preservation
8. Pose / Expression Separation
9. Facial Region Geometry Quality
10. Metric Ground-Truth Layer
11. Physical Representation Gate
12. Runtime / Reproducibility
13. Commercial / Legal / Privacy
14. Three-Class Architecture Comparison
15. Phase 8 Final Decision / Phase 9 Gate

Current main item:

- Item 10 — `ACTIVE`

Official Phase 9:

- `NOT AUTHORIZED`
- `NOT STARTED`

---

## 4. Item 10 — Metric Ground-Truth Layer

Locked sequence:

- [x] 10.1 Ground-Truth Source Qualification
- [x] 10.2 Unit Certainty
- [x] 10.3 Scale Calibration
- [x] 10.4 Coordinate-System Contract
- [x] 10.5 Rigid Alignment
- [x] 10.6 Alignment Landmark Independence
- [x] 10.7 Surface Correspondence
- [x] 10.8 Global Metric Error
- [x] 10.9 Region-Wise Metric Error
- [x] 10.10 Measurement Uncertainty
- [x] 10.11 Repeat Capture / Repeatability
- [x] 10.12 Trueness vs Precision
- [ ] 10.13 Ground-Truth Leakage
- [ ] 10.14 Dataset Coverage
- [ ] 10.15 Closure

Exact next item:

`10.13 — Ground-Truth Leakage`

---

## 5. Item 10.12 — Final Closure

Status:

`BOUNDED_PASS`

Commit:

`98cd4043feee5455a1ef3402e22a4a0fa6eeac18`

Commit message:

`Add trueness precision metric contract`

Verified:

`HEAD == origin/main == 98cd4043feee5455a1ef3402e22a4a0fa6eeac18`

Implemented:

- `CORE/atlas_canonical_head_metric_trueness_precision.py`
- `Test/test_canonical_head_metric_trueness_precision.py`

Locked concepts:

- `TRUENESS` = closeness to reference truth
- `PRECISION` = consistency among repeated measurements

Locked evidence bases:

- `TRUENESS` -> `REFERENCE_TRUTH_COMPARISON`
- `PRECISION` -> `REPEATED_MEASUREMENT_CONSISTENCY`

Key semantics:

- accuracy is not accepted as an alias;
- repeatability is not accepted as an alias;
- quantified observations require finite non-negative `value_mm`;
- quantified observations require provenance;
- quantified observations require explicit evidence basis;
- evidence basis is not inferred when omitted;
- wrong concept/basis pairing is rejected;
- unresolved observations cannot carry fabricated numeric values;
- duplicate concepts are rejected;
- constructor-bypassed observations are revalidated;
- partial coverage is `INCOMPLETE`;
- complete coverage requires both trueness and precision.

Validation history:

- initial RED: `11 failed`
- initial focused: `11 passed`
- initial related: `203 passed`
- initial full: `5455 passed, 11 warnings`
- Closure Challenge V1: `FAIL`
- corrective RED V1: `3 failed, 11 passed`
- corrective focused V1: `14 passed`
- corrective related V1: `206 passed`
- corrective full V1: `5458 passed, 11 warnings`
- Closure Challenge V2: `FAIL`
- corrective RED V2: `2 failed, 14 passed`
- final focused: `16 passed`
- final related: `208 passed`
- final full: `5460 passed, 11 warnings`
- Closure Challenge V3: `PASS`

Closure marker:

`PHASE8_ITEM10_12_TRUENESS_VS_PRECISION_FINAL_CLOSURE_2026_08_28`

---

## 6. Item 10.11 — Previous Safe Checkpoint

Commit before 10.12:

`e2e202767aa878f93b4e5fa47726d34438f31def`

Commit message:

`Add metric repeatability contract`

Item 10.11 status:

`BOUNDED_PASS`

Key rule retained:

Repeatability MUST NOT be relabelled as accuracy or trueness.

---

## 7. Current Full Regression Baseline

Latest verified full regression after Item 10.12:

`5460 passed, 11 warnings in 134.79s`

Warnings are existing NumPy / FLAME deprecation warnings in the real FLAME surface correspondence path.

No test failures were present.

---

## 8. Protected Unrelated Dirty Work

The repository contains unrelated modified and untracked work.

Do not stage, reset, restore, clean, delete, rename, or overwrite unrelated dirty files unless explicitly authorized.

Known protected modified files include product, label, gift-box, preview, wall-collection and Strasbourg-related work.

Known protected untracked work includes label meshers, gift-box calibration files, portrait/relief data, OSM data, previews and experimental files.

Rule:

`Do not use git add .`

Always stage exact target paths only.

---

## 9. Phase 8 Boundary

Current Phase 8 status:

- Phase 8 / Phase 8.10 remains active in the broader program context.
- Phase 8 final decision has NOT been made.
- Phase 8 GO + LOCK has NOT been established.

Therefore:

`Phase 9 is NOT AUTHORIZED / NOT STARTED.`

Do not begin portrait-relief Phase 9 work.

---

## 10. Exact Next Step

Resume at:

`Main Checklist Item 10.13 — Ground-Truth Leakage`

First operation must be read-only.

Audit:

1. authority text for Item 10.13;
2. existing CORE/Test semantics for leakage;
3. existing ownership boundaries;
4. determine whether a separate executable contract is required.

Expected authority scope includes:

- fitting leakage;
- tuning leakage;
- model-selection leakage;
- subject / training overlap;
- validation overlap;
- registration leakage;
- correspondence leakage;
- evaluation-region leakage;
- post-hoc region selection;
- repeated benchmark adaptation where applicable.

Do not create a new 10.13 file until the audit is complete and file/contract creation has been explicitly approved if required.

---

## 11. Exact First Instruction For A New ChatGPT Session

Use this instruction:

> Continue ATLAS_ENGINE from `Docs/STATUS/ATLAS_ENGINE_HANDOFF_2026-08-28.md`. First verify current Git state and the three authority documents. Do not modify anything until verification is complete. Preserve the locked checklist-first, one-terminal-command-at-a-time, tee+pbcopy workflow. Resume only at Main Checklist Item 10.13 — Ground-Truth Leakage. Phase 9 is not authorized.

---

## 12. Continuity Files

Primary authority:

- `Docs/START_HERE.md`
- `Docs/STATUS/CURRENT_STATUS.md`
- `Docs/STATUS/ATLAS_ENGINE_DEVIR_2026-08-08.md`

Current handoff:

- `Docs/STATUS/ATLAS_ENGINE_HANDOFF_2026-08-28.md`

Older handoffs remain historical only and must not override current verified Git / authority state.

---

## 13. Current Safe Checkpoint

Repository:

`/Users/Kubi/ATLAS_ENGINE`

Branch:

`main`

Safe pushed commit:

`98cd4043feee5455a1ef3402e22a4a0fa6eeac18`

Commit:

`Add trueness precision metric contract`

Remote:

`origin/main`

Verified equality:

`HEAD == origin/main`

Next item:

`10.13 — Ground-Truth Leakage`
