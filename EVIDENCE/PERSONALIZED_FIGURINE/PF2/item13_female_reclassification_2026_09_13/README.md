# PF-2 Item13 — Female Self-Intersection Reclassification

STATUS = PASS_BY_CLASSIFICATION

This evidence supersedes the former female zero-defect repair as the accepted Item13 female decision.
The former repair remains preserved as rejected historical diagnostic evidence.

[PF2_ITEM13_FEMALE_RECLASSIFICATION_SUPERSESSION_2026_09_13]

## Scope

This block supersedes the FEMALE decision fields of:
- [PF2_ITEM13_GEOMETRIC_VALIDATION_TECHNICAL_PASS_2026_09_13]
- [PF2_ITEM13_GEOMETRIC_VALIDATION_CLOSED_2026_09_13]

Historical artifacts and measurements remain retained as evidence.

## Correct female source of truth

- FEMALE_GEOMETRY_SOURCE =
  `/Users/Kubi/ATLAS_PF2_PERSISTENT_GEOMETRY/item11_150mm_normalization_2026_09_11/atlas_pf2_item11_female_normalized_150mm_v1.glb`
- SHA256 =
  `4562d5be9ccc9e899b9af4ffd7397ba75b0ef8981808c2d3f2e9c777f727b14d`
- FEMALE_GEOMETRY_MUTATION = NO

## Former Item13 female repair

The former head-locked zero-defect candidate:

`/Users/Kubi/ATLAS_PF2_PERSISTENT_GEOMETRY/item13_female_head_locked_zero_defect_2026_09_13/atlas_pf2_item13_female_head_locked_zero_defect_v1.glb`

is retained only as historical diagnostic evidence.

Decision:
- FORMER_HEAD_LOCKED_ZERO_DEFECT_REPAIR = REJECTED
- ITEM13_REPAIR_VISUAL_ASSESSMENT = FAIL
- FINAL_GEOMETRY_SOURCE = NO
- DOWNSTREAM_ACCEPTED_SOURCE = NO
- GLOBAL_HEAD_MORPH_DISABLE_ROUTE = REJECT / STOP
- GLOBAL_MORPH_STRENGTH_ROUTE = REJECT / STOP

Reason:

The rejected repair did not perform a local correction on the accepted Item11
geometry. It rebuilt the assembly from older prepared-head + Dreamloft inputs
and reintroduced previously rejected head/neck/facial-form regressions.

## Raw crossing evidence on accepted Item11 geometry

- RAW_SELF_INTERSECTION_PAIRS = 1525

### Accepted neck/interface region

- ACCEPTED_NECK_INTERFACE_REGION_RAW_CROSSINGS = 1520
- Spatial contract:
  - pair maximum Z <= 105 mm
- Domain ownership:
  - BODY__HEAD = 706
  - HEAD__HEAD = 626
  - HEAD__TRANSITION = 188
- Measured positive crossing lengths:
  - MIN = 0.000007419 mm
  - P50 = 0.035198687 mm
  - P95 = 0.133029419 mm
  - P99 = 0.234910810 mm
  - MAX = 2.341523817 mm

These 1520 raw crossings occur inside the accepted
EMBEDDED_NECK_ROOT_PLUS_LOCAL_TRAPEZIUS_SURFACE neck/interface region.
Raw predicate hits in this region are not, by themselves, proof of an
unintended production defect.

### High-Z raw crossings

- HIGH_Z_RAW_CROSSINGS = 5

1. Inherited closed detail shell:
   - RAW_CROSSINGS = 1
   - COMPONENT_FACES = 638
   - crossing length = 0.073241743 mm
   - source-detail shell provenance is inherited from the accepted female
     identity source.

2. Main-head local topological neighborhood:
   - RAW_CROSSINGS = 4
   - crossing-length range =
     0.005961601 mm to 0.019498134 mm
   - face graph distance = 1 or 2
   - distance-2 pairs have 6-7 common intermediate faces
   - no separate-surface ownership witness was found.

## Corrected classification

- PROVEN_UNINTENDED_SEPARATE_SURFACE_PENETRATION_PAIRS = 0
- FEMALE_SELF_INTERSECTION_CLASSIFICATION = PASS
- FEMALE_GEOMETRIC_VALIDATION = PASS_BY_CLASSIFICATION
- FEMALE_GEOMETRY_MUTATION = NO

The raw self-intersection predicate count remains recorded as 1525.
This supersession does NOT rewrite the raw count to zero.
It changes the interpretation from raw predicate hits to classified geometric
evidence.

## Thickness / physical-survivability contract

Unchanged:

- PF-2 has no authority-defined numeric minimum-thickness threshold.
- No numeric threshold is invented in Item13.
- Real minimum-feature and local-wall survivability remain downstream gates:
  - Item15 Physical Print
  - Item16 Slicer / Support Inspection
- This classification does NOT claim physical-print survivability PASS.

## Current execution state

- PF2_ITEM13_FEMALE = PASS_BY_CLASSIFICATION
- ITEM14_HUMAN_VISUAL_GATE = ACTIVE / NOT PASS
- ITEM15_PHYSICAL_PRINT = NOT STARTED
- ITEM16_SLICER_SUPPORT_INSPECTION = NOT STARTED
- ITEM17_FINAL_CHIBI_PRODUCT_CANDIDATE_LOCK = NOT STARTED
- PHASE9 = NOT AUTHORIZED / NOT STARTED

[PF2_ITEM13_FEMALE_RECLASSIFICATION_SUPERSESSION_2026_09_13:END]
