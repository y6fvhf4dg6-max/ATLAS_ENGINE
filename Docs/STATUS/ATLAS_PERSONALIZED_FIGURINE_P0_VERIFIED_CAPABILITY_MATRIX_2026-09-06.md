# ATLAS — Personalized 3D Figurine P-0 Verified Capability Matrix

**Decision date:** `2026-09-06`

**User decision:** `APPROVED`

**Gate:** `GATE-P0 = PASS / CAPABILITY_BOUNDARIES_LOCKED`

**Active roadmap:** `Docs/Roadmap/PERSONALIZED_3D_FIGURINE_BUSINESS_PLAN_V1.md`

This record preserves the user-reviewed capability boundary at the close of P-0. It does not authorize product launch or claim that any full-body product family is production-ready.

---

STATUS LEGEND:
PROVEN_REUSABLE       = implementation + focused tests; reusable contract exists
PARTIAL_REUSABLE      = useful implementation exists but figurine production coverage is incomplete
SUBJECT_SPECIFIC      = demonstrated only for the current Meshy V7 pilot
MANUAL_ONLY           = performed by human/operator; no reusable ATLAS owner
EXTERNAL_DEPENDENT    = production result depends on an external generator/source
MISSING               = no genuine figurine implementation owner found

| # | Capability | Current classification | Production owner / evidence | Tests | Real-subject evidence | Physical evidence | Automation / human / external boundary | Reuse and families | Missing work |
|---|---|---|---|---|---|---|---|---|---|
| 01 | Customer input and quality control | PARTIAL_REUSABLE | atlas_portrait_input_evidence; evidence_set; quality_observation; usability_gate | Focused tracked tests exist | Portrait inputs exercised; commercial multi-customer coverage absent | None required | Automated observations plus human capture judgment | Reusable foundation; PF-1–PF-5 | Figurine capture UI, multi-person/pet rules, rejection reasons, consent record |
| 02 | Identity generation | EXTERNAL_DEPENDENT + SUBJECT_SPECIFIC | Local FLAME recovery research; selected Meshy V7 pilot output | Local identity modules tested; commercial likeness not passed | One Meshy V7 identity selected by human judgment | Printed bust for that one identity | External AI generates; ATLAS local exact-identity route parked; human selects | Current subject only; potentially PF-1–PF-5 | Approved provider route, multi-subject benchmark, repeatability and failure rate |
| 03 | Identity approval | MANUAL_ONLY | Human visual judgment; likeness-risk and inspection contracts are supporting evidence only | Supporting contracts tested | Meshy V7 selected/rejected candidates reviewed | Bust judged by user | Human is final authority; no customer approval system | Principle reusable; system missing for PF-1–PF-5 | Standard views, approval UI, revision states, signed acceptance, audit trail |
| 04 | Source and model provenance | PROVEN_REUSABLE | Portrait evidence/provenance contracts; hashes; manifests; SPC-G4 evidence tree | Broad focused tests exist | Meshy V7 and pilot checkpoints hashed | Physical claim recorded separately from digital evidence | Largely automated record generation; operator preserves artifacts | Reusable; PF-1–PF-5 | Vendor job IDs, consent version, deletion receipt, license snapshot |
| 05 | Head and hair preparation | PARTIAL_REUSABLE + SUBJECT_SPECIFIC | Canonical-head mesh/physical adapters and family builder; Meshy V7 extracted head | Strong tracked head tests; hair-shell work untracked/not accepted | Meshy V7 head extraction and preservation | Bust printed | Head tooling partly automated; hair and identity selection require human/external AI | Head carrier reusable; accepted identity is subject-specific | Production hair contract, ear/glasses/beard rules, multiple subjects |
| 06 | Body generation and library | MISSING + EXTERNAL_DEPENDENT | Body-pose-prop adapter is semantic_reference_only; Dreamloft body is pilot source | Adapter tests explicitly prove it does not generate body geometry | One locked Dreamloft body checkpoint | No full-body physical pass | External/ready-made body source plus manual selection | No proven reusable human-body library; needed by PF-1–PF-5 | Licensed body catalog, proportions, sex/age/body types, semantic anchors |
| 07 | Pose | PARTIAL_REUSABLE + EXTERNAL_DEPENDENT | Canonical-head pose normalization exists; body adapter stores metadata only | Head-pose and adapter tests exist | One externally sourced standing pose | No full-body print proof | Head normalization automated; body rig/pose creation absent | Partial foundation; PF-1–PF-5 | Rig contract, joint limits, pose catalog, stability and collision validation |
| 08 | Clothing and accessories | MISSING | No genuine garment/accessory geometry owner found | No figurine clothing tests | Pilot body clothing comes only from external asset | None | External asset or artist work required | Not reusable yet; PF-1–PF-5 | Licensed catalog, fit/transfer, glasses/props, thickness and color parts |
| 09 | Adaptive head/body assembly | MISSING | No semantic owner; fixed-ratio head carrier is not body assembly; harmonic shelf route rejected | Carrier tests exist but no adaptive assembly tests | Meshy V7 + Dreamloft experiments only | No accepted full-body print | Current process manual/experimental | Not reusable; mandatory for PF-1–PF-5 | Detect neck interfaces, align scale/direction, controlled transition, preserve identity |
| 10 | Topology cleanup | PROVEN_REUSABLE + SUBJECT_SPECIFIC_PHYSICAL | atlas_mesh_repair; canonical-head topology contracts; production cleanup evidence | Tracked focused tests exist | Meshy/Tripo pilot mesh cleanup and debris removal | Cleaned/normalized route led to printed bust | Core checks/repair partly automated; operator confirmation | General mesh foundation reusable; figurine breadth unproven | Batch policy, self-intersection measurement, identity-safe repair thresholds |
| 11 | Coordinate and orientation normalization | PROVEN_REUSABLE | atlas_coordinate_engine; canonical-head pose normalization; checkpoint bounds | Tracked tests exist | Pilot world-space bounds/orientation measured | Bust production orientation used | Automated measurements plus operator selection | Reusable foundation; PF-1–PF-5 | Unified figurine axis contract and automatic source adapter |
| 12 | Scale normalization | PROVEN_REUSABLE + SUBJECT_SPECIFIC_PHYSICAL | atlas_scale_engine; metric unit normalizer; SPC-G4 150 mm artifact | Tracked tests exist | Uniform 150 mm pilot normalization | 150 mm bust printed | Automated normalization; target selected by product contract | Reusable foundation; current physical proof one subject | Per-family scale rules, head/body ratio rules, dimensional tolerance QA |
| 13 | Manifold and winding control | PROVEN_REUSABLE + SUBJECT_SPECIFIC_PHYSICAL | atlas_mesh_validator; topology manufacturability contract; normalized GLB evidence | Tracked validator tests exist | Pilot main geometry watertight/winding consistent | Resulting pilot printed | Automated validation; some cleanup/operator review | Reusable mesh foundation; PF-1–PF-5 | Figurine assembly regression and independent self-intersection owner |
| 14 | Fragile features and printability | PARTIAL_REUSABLE | fragile_connection, minimum_thickness, overhang analyzers; canonical-head slicer gate | Focused tracked tests exist | Applied production reasoning to pilot | Bust printed successfully, not five families | Automated analyzers plus manual slicer judgment | Reusable primitives; figurine thresholds incomplete | Hair/fingers/props/spring/ankles thresholds; resin versus FDM profiles |
| 15 | Color and part segmentation | PARTIAL_REUSABLE | Product color preview, material hierarchy, multicolor STL exporter | Tracked tests exist | No accepted personalized figurine color segmentation proof | Bust was one-color | Geographic automation exists; figurine semantics/manual painting unresolved | Platform reusable in part; PF-1–PF-5 unproven | Skin/hair/eye/clothing regions, AMS limits, full-color vendor route |
| 16 | Base integration | PARTIAL_REUSABLE | atlas_base_plate_builder/cutter; no figurine-specific integrated-base owner | General base tests exist | Chibi base not built/accepted | No full-body base print | Generic geometry automation; product design human-led | Generic base reusable; figurine base missing | Stability polygon, foot attachment, nameplate, couple/family arrangement |
| 17 | STL and export | PROVEN_REUSABLE + SUBJECT_SPECIFIC_PHYSICAL | Relief/wall/premium-box exporters plus successful figurine pilot export workflow | Multiple tracked exporter tests | Meshy V7 pilot exported for production | Bust manufactured from exported production route | Mostly automated with operator path management | Reusable export foundation; PF-1–PF-5 | Dedicated figurine package exporter, parts manifest, color assembly |
| 18 | Slicing and printer validation | PARTIAL_REUSABLE + MANUAL_PHYSICAL | atlas_bambu_3mf_production_validator and slicer gate; actual Bambu Studio workflow | Validator tests exist | Pilot manually opened/sliced | Bust printed successfully | Validator does not run Bambu Studio; production remains operator-driven | Supporting foundation reusable; one-subject proof | Automated slicer invocation, profile locking, screenshots, failure ingestion |
| 19 | Physical QA | PARTIAL_REUSABLE + SUBJECT_SPECIFIC | Physical representation/feature contracts and human inspection; persisted bust record | Supporting tracked tests exist | One pilot identity inspected | One successful physical bust reported and persisted | Human inspection dominates | QA concepts reusable; no repeatable figurine protocol | Measurement sheet, likeness photos, durability/drop/shipping, pass authority |
| 20 | Human time and economics | MISSING | No figurine-specific time/cost owner found | No relevant implementation tests | No multi-order dataset | No unit-economics proof | Entirely unmeasured | Required across PF-1–PF-5 | Time per stage, vendor/API cost, revisions, print labor, failure and margin |

=== CROSS-CUTTING VERIFIED DECISIONS ===

1. ATLAS is strongest after an acceptable 3D identity has already been generated:
   provenance, normalization, topology, validation, export and physical-production control.

2. ATLAS does not currently possess a commercially proven internal photo-to-person identity generator.

3. The current successful identity route is:
   EXTERNAL_AI_GENERATION -> HUMAN_IDENTITY_SELECTION -> ATLAS_PRODUCTION_CONTROL.

4. The market benchmark confirms that human artist review and customer proofing are normal production stages, not exceptional failures.

5. The current largest technical product blocker is:
   ADAPTIVE_HEAD_BODY_ASSEMBLY.

6. The current largest operational blockers are:
   CUSTOMER_APPROVAL_SYSTEM;
   BODY/CLOTHING/POSE LIBRARY;
   HUMAN_TIME_AND_UNIT_ECONOMICS.

7. Physical proof is limited to one subject-specific bust.
   It does not prove a full-body product or all five product families.

8. Real customer photographs remain blocked from external upload until an approved provider route and customer consent record exist.

# GATE-P0 FINAL DECISION

GATE_P0=PASS
CAPABILITY_BOUNDARIES=LOCKED
USER_REVIEW=APPROVED
PRODUCT_LAUNCH_AUTHORIZATION=NO
FIRST_DOWNSTREAM_PRODUCT=PF-2_MODERN_CHIBI
NEXT_WORK_PROGRAM=P-1_FIVE_PRODUCT_AND_STYLE_CONTRACTS
PRODUCTION_GEOMETRY_AUTHORIZATION=NOT_CREATED_BY_GATE_P0
