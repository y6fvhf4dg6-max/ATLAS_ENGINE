# ATLAS — Personalized 3D Figurine Business Plan V1

**Authority date:** `2026-09-06`

**Program:** `ATLAS_PERSONALIZED_3D_FIGURINE_PRODUCT_FAMILY_V1`

**Status:** `ACTIVE_PRIMARY_ROADMAP`

**Commercial objective:** Convert customer photographs into recognizable,
desirable and physically manufacturable personalized 3D figurines.

---

# 0. AUTHORITY AND SUPERSESSION

This document is the active primary roadmap for the ATLAS personalized
figurine product family.

It supersedes the following SPC V1 files as active execution authority:

1. `Docs/Roadmap/SPC_V1_PART_1_STRATEGY_AND_IDENTITY.md`
2. `Docs/Roadmap/SPC_V1_PART_2_3D_ATLAS_AND_PRODUCT.md`
3. `Docs/Roadmap/SPC_V1_PART_3_BUSINESS_PILOT_AND_GOVERNANCE.md`

Those files remain preserved as historical strategy and evidence. Their valid
technical, commercial and physical findings are not deleted or rewritten.

This supersession does not:

- erase previous SPC evidence;
- turn an experiment into a production capability;
- claim generalization from one subject;
- authorize the old Phase 9;
- declare any product family production-ready.

`LEGACY_SPC_V1_STATUS = SUPERSEDED_AS_ACTIVE_AUTHORITY / HISTORICAL_PRESERVED`

`PHASE9_STATUS = NOT_AUTHORIZED / NOT_STARTED`

---

# 1. PRODUCT MISSION

ATLAS shall become a repeatable photo-to-physical-product system for
personalized 3D figurines.

Required customer-facing capability:

`CUSTOMER PHOTO(S)`
->
`INPUT AND RIGHTS GATE`
->
`PERSONAL IDENTITY PACKAGE`
->
`PRODUCT STYLE SELECTION`
->
`3D GENERATION`
->
`HUMAN IDENTITY APPROVAL`
->
`ATLAS GEOMETRY CONTROL`
->
`PHYSICAL PRODUCTIZATION`
->
`CUSTOMER APPROVAL`
->
`MANUFACTURE AND QA`

The target is not one successful demonstration. The target is a controlled
system capable of producing multiple product types from the same approved
personal identity.

Core principle:

`IDENTITY_BEFORE_STYLE`

An attractive figurine that does not recognizably represent the customer is a
failure.

---

# 2. AUTHORITY MODEL

## 2.1 AI

`AI = GENERATE`

AI may generate:

- stylized identity proposals;
- head and hair geometry;
- bodies and clothing;
- poses and accessories;
- textures and color proposals;
- candidate 3D meshes.

AI output is not production-ready merely because it looks attractive.

## 2.2 ATLAS

`ATLAS = CONTROL`

ATLAS owns:

- provenance;
- geometry inspection;
- coordinate and scale normalization;
- adaptive head/body integration;
- topology and manifold control;
- identity-preserving repair;
- fragile-feature analysis;
- color and part segmentation;
- base integration;
- STL and production export;
- production evidence.

## 2.3 Human

`HUMAN = JUDGE / CORRECT EXCEPTIONS`

Humans own:

- identity judgment;
- aesthetic judgment;
- source-suitability exceptions;
- approval of meaningful changes;
- bounded correction when automation is insufficient.

Human intervention shall be categorized and timed. It shall not be hidden.

## 2.4 Production

`PRODUCTION = MANUFACTURE / VERIFY`

Production owns slicing, printer/material selection, support strategy,
manufacture, finishing, packing and physical QA.

---

# 3. FIVE PRODUCT FAMILIES

All five product families are in scope. They share one identity and
production-control foundation.

## PF-1 — Premium Realistic Full-Body Figurine

- natural or near-natural human proportions;
- low facial stylization;
- detailed clothing, pose and accessories;
- premium collectible positioning;
- strongest identity and surface-detail requirement.

## PF-2 — Modern Chibi Figurine

- recognizably enlarged head;
- compact small body;
- premium rather than generic toy appearance;
- low-to-moderate facial stylization;
- integrated stable base;
- current first physical full-body pilot.

## PF-3 — Couple / Family Figurine

- two or more approved personal identities;
- relationship-specific pose and interaction;
- coordinated scale and composition;
- wedding, anniversary, family and memorial use cases;
- increased correction and production-complexity risk.

## PF-4 — Natural Keepsake Figurine

- proportions between realistic and Chibi;
- soft stylization;
- recognition through face, hair, clothing and posture;
- desk, gift and commemorative positioning.

## PF-5 — Bobblehead / Character Figurine

- strongly enlarged personalized head;
- simplified or template-assisted body;
- fixed-head version validated first;
- mechanical bobble version only after fixed-head success;
- character and profession variants allowed.

No product family is cancelled because another family is developed first.

---

# 4. COMMON PERSONAL IDENTITY FOUNDATION

ATLAS shall create one reusable `PERSONAL_IDENTITY_PACKAGE` per approved
subject.

The package shall contain, where available:

- verified source photographs;
- source rights and consent;
- input-quality result;
- approved facial identity;
- approved head/skull character;
- approved hair and hairline;
- ears and relevant accessories;
- facial hair and characteristic marks;
- color references;
- approved neutral reference renders;
- safe head/body attachment region;
- known uncertainty and missing evidence;
- revision history.

The same identity package shall be usable across all five product families.

A successful result for one subject is:

`SUBJECT_SPECIFIC_PROOF`

It is not automatically:

`GENERAL_PIPELINE_PROOF`

---

# 5. CUSTOMER INPUT CONTRACT

## 5.1 Preferred capture

- clear frontal face photograph;
- left and right three-quarter or side photographs;
- full-body or desired-pose photograph;
- clothing reference;
- optional hair, ear and accessory detail photographs.

## 5.2 Quality gate

Check:

- resolution and focus;
- lighting;
- occlusion and filters;
- facial expression;
- head and hair visibility;
- clothing and body visibility;
- cross-photo identity consistency.

Missing evidence may reduce available options or require recapture. It shall
not be silently invented as observed truth.

## 5.3 Privacy and commercial use

Real customer photographs shall not be uploaded to an external provider unless
the provider-specific commercial, privacy and data-processing route is
approved.

`REAL_CUSTOMER_EXTERNAL_UPLOAD = BLOCKED_PENDING_APPROVED_VENDOR_ROUTE`

Local/private processing is preferred where practical.

---

# 6. COMMON TECHNICAL ARCHITECTURE

## 6.1 Identity generation

For every generator ATLAS shall record:

- provider and model/version;
- inputs;
- prompts/settings;
- generation date;
- licensing status;
- output hashes;
- human identity decision.

## 6.2 Product style profiles

Each product family shall explicitly control:

- head-to-body ratio;
- facial stylization;
- body proportions;
- hand and foot scale;
- surface detail;
- clothing simplification;
- accessory policy;
- base type;
- target physical size;
- material and color strategy.

The identity package is shared. The style profile changes the product.

## 6.3 Adaptive head/body integration

ATLAS shall not depend on one fixed crop loop, neck coordinate or
subject-specific harmonic patch.

For every candidate head/body pair the system shall:

1. preserve approved face, hair and head identity;
2. identify a safe lower-head attachment region;
3. estimate natural neck center, direction and scale;
4. inspect the body's neck interface;
5. align the body to the approved head where possible;
6. create only a short local transition;
7. avoid modifying visible identity geometry;
8. reject shelf, fan, funnel and stretched-triangle artifacts;
9. validate topology and visual continuity;
10. preserve rollback to the approved source head.

Global remeshing, voxelization, boolean repair or smoothing may not be applied
to an approved identity head without an identity-preservation gate.

## 6.4 Body and pose library

The system shall support:

- reusable base bodies;
- body-shape adaptation;
- compact standing and seated poses;
- profession and hobby poses;
- couple/family compositions;
- clothing modules;
- props and pets;
- product bases.

Ready-made assets may be used only with established provenance and commercial
rights.

## 6.5 Production normalization

ATLAS shall verify:

- units and orientation;
- total size;
- component count;
- watertightness and winding;
- self-intersection risk;
- minimum feature thickness;
- fragile appendages;
- support burden;
- center of mass and stability;
- base attachment;
- color/part separation;
- slicer compatibility;
- STL export integrity.

---

# 7. DEVELOPMENT WORK PROGRAM

## P-0 — Authority Migration and Capability Inventory

Goals:

- activate this roadmap;
- preserve legacy evidence;
- audit current ATLAS modules and checkpoints;
- classify every claimed capability as implemented, tested, physically proven,
  subject-specific, manual, external-provider-dependent or missing.

Gate:

`GATE-P0 = VERIFIED_CAPABILITY_MATRIX`

## P-1 — Five Product and Style Contracts

Goals:

- define one style profile for PF-1 through PF-5;
- define customer-selectable and protected parameters;
- define preview and approval views;
- define product-specific physical requirements.

Gate:

`GATE-P1 = FIVE_PRODUCT_CONTRACTS_APPROVED`

## P-2 — Customer Capture and Identity Package

Goals:

- input-quality validation;
- source provenance;
- identity anchors and uncertainty;
- reusable approved identity package.

Gate:

`GATE-P2 = REUSABLE_IDENTITY_PACKAGE_APPROVED`

## P-3 — Generation Benchmark

Goals:

- benchmark commercially admissible routes;
- compare identity, geometry, cost, latency and revision burden;
- select primary and fallback routes;
- reject attractive but unrecognizable output.

Gate:

`GATE-P3 = GENERATION_ROUTE_SELECTED`

## P-4 — Adaptive Head/Body Assembly

Goals:

- replace subject-specific coordinates and patches;
- analyze attachment regions;
- align approved heads with body candidates;
- build a bounded local connector;
- prove approved identity geometry remains unchanged.

Gate:

`GATE-P4 = ADAPTIVE_ASSEMBLY_PROVEN`

## P-5 — First Full-Body Chibi Pilot

Goals:

- reuse the approved Meshy V7 pilot identity;
- produce a 150 mm premium Chibi full-body candidate;
- use a compact body and stable integrated base;
- pass identity, geometry and slicer gates;
- manufacture and inspect the physical result.

Gate:

`GATE-P5 = PHYSICAL_CHIBI_PILOT_PASS`

The existing bust remains an intermediate proof. It does not close P-5.

## P-6 — Product-Family Expansion

After the common foundation and adaptive assembly are proven, validate:

1. PF-4 Natural Keepsake;
2. PF-1 Premium Realistic Full Body;
3. PF-3 Couple / Family;
4. PF-5 Fixed-Head Bobblehead;
5. optional mechanical Bobblehead.

The order may change through evidence, but all five remain targets.

Gate:

`GATE-P6 = FIVE_PRODUCT_FAMILY_FEASIBILITY_CLASSIFIED`

## P-7 — Manufacturing System

Goals:

- FDM and resin/SLA comparison where needed;
- print profiles;
- part and color strategy;
- support and cleanup limits;
- packaging and durability;
- repeatable QA.

Gate:

`GATE-P7 = REPEATABLE_PHYSICAL_PRODUCTION`

## P-8 — Economics and Operations

Measure per order:

- AI cost;
- operator and specialist time;
- regeneration count;
- print time;
- material and purge waste;
- failures and reprints;
- finishing;
- packaging and shipping;
- revisions;
- gross margin.

Gate:

`GATE-P8 = ECONOMIC_FEASIBILITY`

## P-9 — Controlled Customer Pilot

Goals:

- approved test customers;
- end-to-end order records;
- identity acceptance;
- willingness to pay;
- delivery/revision experience;
- rejection/refund analysis;
- product-family demand comparison.

Gate:

`GATE-P9 = CONTROLLED_COMMERCIAL_PILOT`

## P-10 — Commercial Lock

Commercial launch requires:

- repeatable identity acceptance;
- bounded human correction;
- reliable physical production;
- viable unit economics;
- approved privacy/vendor routes;
- customer evidence.

Gate:

`GATE-P10 = PRODUCT_FAMILY_COMMERCIAL_LOCK`

---

# 8. CURRENT VERIFIED EVIDENCE

As of `2026-09-06`:

- a Meshy V7 pilot head/identity was selected by human judgment;
- the identity was preserved through a bust production route;
- local cleanup and 150 mm normalization were demonstrated;
- STL export and Bambu Studio slicing were demonstrated;
- a physical bust was printed successfully;
- the bust is an intermediate proof, not the final product;
- a full-body personalized figurine has not passed;
- multi-subject generalization has not been demonstrated;
- all five product families have not been produced;
- the fixed-coordinate harmonic head/body attachment produced a visible
  shelf/fan artifact and is rejected as the general solution.

Current classification:

`PHOTO_TO_APPROVED_HEAD = SUBJECT_SPECIFIC_PROOF`

`APPROVED_HEAD_TO_PHYSICAL_BUST = SUBJECT_SPECIFIC_PHYSICAL_PROOF`

`ADAPTIVE_HEAD_BODY_ASSEMBLY = NOT_YET_PROVEN`

`FULL_BODY_CHIBI = NOT_YET_PROVEN`

`FIVE_PRODUCT_FAMILY_PIPELINE = NOT_YET_PROVEN`

---

# 9. STOP AND REJECTION RULES

Stop or redesign when:

- identity is lost during stylization;
- repair changes the approved face/head;
- one subject coordinate is treated as a universal neck contract;
- a wide crop boundary is forced into a small neck aperture;
- manifold status excuses a visibly wrong surface;
- repeated patches fail the same visual gate;
- human correction is commercially excessive;
- licensing or customer-data processing is unresolved;
- printability improvement destroys recognizability;
- a successful render is presented as a physical-product success.

No blind parameter or weight sweep may replace diagnosis.

---

# 10. RESEARCH PROGRAM

## R-1 — Market and Product Benchmark

Research all five product families for:

- real delivered-product evidence;
- pricing and sizes;
- materials;
- revision policies;
- production times;
- customer complaints;
- EU and Turkey relevance.

## R-2 — Photo-to-3D Generation Routes

Compare:

- identity retention;
- full-body capability;
- multi-view support;
- commercial licensing;
- privacy/data handling;
- API or local deployment;
- cost, latency and mesh quality.

## R-3 — Adaptive Assembly

Research:

- head/neck attachment detection;
- body alignment;
- local bridging;
- identity-preserving topology processing;
- printable anatomy;
- automated rejection.

## R-4 — Bodies, Clothing and Assets

Research:

- licensed body libraries;
- pose systems;
- clothing assets;
- accessories;
- procedural alternatives;
- build-versus-buy decisions.

## R-5 — Manufacturing

Research:

- FDM versus resin/SLA;
- multicolor versus hand finishing;
- part-based assembly;
- durability;
- support and cleanup;
- packaging.

External technology remains a benchmark candidate until licensing, privacy and
production evidence are verified.

---

# 11. SUCCESS MEASURES

## Identity

- human recognition;
- cross-view consistency;
- cross-product consistency;
- preservation after repair;
- revision count.

## Product

- premium visual judgment;
- style-profile compliance;
- pose/accessory correctness;
- stability;
- detail readability.

## Geometry

- manifold and winding status;
- component count;
- self-intersection risk;
- feature thickness;
- fragile features;
- slicer acceptance.

## Operations

- operator minutes;
- specialist minutes;
- generation attempts;
- print failures;
- delivery time.

## Economics

- variable cost;
- labor;
- packaging and shipping;
- refund/revision cost;
- selling price;
- gross margin.

No invented likeness score replaces human identity judgment.

---

# 12. IMMEDIATE EXECUTION POINT

The former mainline:

`FIX_CURRENT_SUBJECT_SPECIFIC_HARMONIC_SHELF`

is stopped.

Its evidence remains a rejected technical experiment.

The exact next task is:

`P-0 / BUILD_VERIFIED_ATLAS_CAPABILITY_MATRIX`

The audit shall determine:

- what ATLAS implements;
- what has tests;
- what has real-subject evidence;
- what has physical proof;
- what remains manual;
- what depends on external AI;
- what is subject-specific;
- what is reusable across the five products;
- what is missing.

No new production geometry shall be implemented before review of the P-0
capability matrix.

---

# 13. CURRENT PROGRAM STATE

`ACTIVE_ROADMAP = PERSONALIZED_3D_FIGURINE_BUSINESS_PLAN_V1`

`PROGRAM_STATUS = FOUNDATION_AND_CAPABILITY_AUDIT_ACTIVE`

`CURRENT_WORK_PROGRAM = P-0`

`CURRENT_GATE = GATE-P0`

`CURRENT_FIRST_PHYSICAL_FULL_BODY_TARGET = PF-2_MODERN_CHIBI`

`ALL_FIVE_PRODUCT_FAMILIES_IN_SCOPE = YES`

`LEGACY_SPC_V1 = HISTORICAL_PRESERVED`

`OLD_EXACT_IDENTITY_RESEARCH = PARKED / NON_BLOCKING`

`PHASE9 = NOT_AUTHORIZED / NOT_STARTED`

---

[PERSONALIZED_FIGURINE_P0_GATE_CLOSED_2026_09_06:BEGIN]

# Personalized 3D Figurine P-0 — Verified Capability Matrix Closure

**Decision date:** `2026-09-06`

**User decision:** `APPROVED`

`GATE_P0 = PASS`

`CAPABILITY_BOUNDARIES = LOCKED`

Persistent matrix:

`Docs/STATUS/ATLAS_PERSONALIZED_FIGURINE_P0_VERIFIED_CAPABILITY_MATRIX_2026-09-06.md`

The closure establishes:

- ATLAS has reusable provenance, normalization, topology, validation, export
  and production-control foundations;
- commercially accepted photo-to-person identity generation remains dependent
  on an approved external route plus human identity judgment;
- current physical proof is limited to one subject-specific Meshy V7 bust;
- adaptive head/body assembly is not implemented and remains the largest
  technical product blocker;
- reusable body, pose, clothing and accessory coverage is missing or partial;
- customer approval/revision workflow and human-time economics remain missing;
- competitor evidence supports an AI/initial-model plus artist review plus
  customer proofing production model.

This closure does not authorize commercial launch, claim multi-subject
generalization, or claim that any full-body product family is production-ready.

Customer photographs may be externally processed only after:

1. explicit and recorded customer consent;
2. confirmation that the customer has authority for every depicted person;
3. selection of an approved commercial provider route;
4. documented privacy, retention/deletion and output-license conditions.

`PRODUCT_LAUNCH_AUTHORIZATION = NO`

`CURRENT_WORK_PROGRAM = P-1`

`CURRENT_GATE = GATE-P1`

`EXACT_NEXT = DEFINE_FIVE_PRODUCT_AND_STYLE_CONTRACTS`

The first downstream physical full-body target remains:

`PF-2 — MODERN CHIBI`

No production geometry is authorized merely by this P-0 closure.

Old Phase 9 remains:

`NOT_AUTHORIZED / NOT_STARTED`

[PERSONALIZED_FIGURINE_P0_GATE_CLOSED_2026_09_06:END]

---

[PERSONALIZED_FIGURINE_P1_GATE_CLOSED_2026_09_06:BEGIN]

# Personalized 3D Figurine P-1 — Five Product Contracts Closure

**Decision date:** `2026-09-06`

**User decision:** `APPROVED`

`GATE_P1 = PASS / FIVE_PRODUCT_CONTRACTS_LOCKED`

Persistent product contract:

`Docs/Roadmap/PERSONALIZED_3D_FIGURINE_FIVE_PRODUCT_CONTRACTS_V1.md`

The approved contract covers:

1. `PF-1 — PREMIUM REALISTIC FULL-BODY FIGURINE`
2. `PF-2 — MODERN CHIBI FIGURINE`
3. `PF-3 — COUPLE / FAMILY FIGURINE`
4. `PF-4 — NATURAL KEEPSAKE FIGURINE`
5. `PF-5 — BOBBLEHEAD / CHARACTER FIGURINE`

Protected shared rule:

`IDENTITY_BEFORE_STYLE`

Locked decisions include:

- PF-1 initially uses premium one-color resin with optional hand finish;
- PF-3 uses one shared technical family with separate Couple and Family
  commercial offers allowed;
- PF-4 defaults to 150 mm;
- PF-5 V0 is fixed-head only;
- base inscription is optional across all five families;
- one consolidated customer preference revision is included;
- ATLAS/artist-caused mismatch correction is treated separately;
- PF-2 remains 150 mm nominal and the first full-body physical target;
- customer approval of the production-intent model is required before printing.

This closure does not authorize commercial launch or production geometry.

`PRODUCT_LAUNCH_AUTHORIZATION = NO`

`PRODUCTION_GEOMETRY_AUTHORIZATION = NO`

`CURRENT_WORK_PROGRAM = P-2`

`CURRENT_GATE = GATE-P2`

`EXACT_NEXT = DEFINE_CUSTOMER_CAPTURE_AND_REUSABLE_IDENTITY_PACKAGE`

P-2 shall define the input-quality, consent, provenance, identity-anchor,
uncertainty and reusable `PERSONAL_IDENTITY_PACKAGE` contract.

Old Phase 9 remains:

`NOT_AUTHORIZED / NOT_STARTED`

[PERSONALIZED_FIGURINE_P1_GATE_CLOSED_2026_09_06:END]
